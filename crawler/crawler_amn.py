# coding='UTF-8'
import sys
sys.path.append('../')
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
import threading,pymysql,time,requests,os,urllib3,re,random
from config import mysql_config

requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 5
s = requests.session()
s.keep_alive = False
s.mount('http://', HTTPAdapter(max_retries=3))
# 数据库连接信息
dbhost = {
    "host": mysql_config['HOST'],
    "dbname": mysql_config['NAME'],
    "user": mysql_config['USER'],
    "password": mysql_config['PASSWORD']
}

base_url="https://www.2meinv.com/"
tag_url="https://www.2meinv.com/tags-{}-{}.html"
index_url="https://www.2meinv.com/index-1.html"
img_path='/static/images/'

class Spider():
    page_url_list = []
    img_url_list = []
    rlock = threading.RLock()
    proxy_dict = ""
    def __init__(self, start_page_num, end_page_num,img_path, thread_num, type="home",type_id=0):
        self.start_page_num = start_page_num
        self.end_page_num=end_page_num
        self.img_path = img_path
        self.thread_num = thread_num
        self.type = type
        self.type_id=type_id

    def get_url(self):
        for i in range(self.start_page_num, self.end_page_num):
            if self.type_id==0:
                page = s.get(index_url.format(str(i)), verify=False, timeout=10).text
            else:
                page = s.get(tag_url.format(self.type,str(i)), verify=False, timeout=10).text
            # page = s.get(base_url + self.type+"-"+str(i)+".html", verify=False).text
            soup = BeautifulSoup(page, "html.parser")
            page_base_url = soup.find("ul", class_="detail-list").find_all("li")
            for page_url in page_base_url:
                url = page_url.find("a",class_="dl-pic").get("href")
                self.page_url_list.append(url)

    def get_img(self,url):
        tagidlist=[]
        db = pymysql.connect(dbhost.get("host"), dbhost.get("user"), dbhost.get("password"), dbhost.get("dbname"))
        cursor = db.cursor()
        page = s.get(url,verify=False, timeout=10)
        soup = BeautifulSoup(page.text, "html.parser")
        title=soup.title.string.replace("_爱美女","")
        if self.type_id == 0:
            if "袜" in title or "丝" in title or "腿" in title:
                self.type_id = 2
            elif "青春" in title or "清纯" in title:
                self.type_id = 3
            elif "萝莉" in title:
                self.type_id = 4
            else:
                self.type_id = 1
        isExists = cursor.execute("SELECT title FROM images_page WHERE title =" + "'" + title + "'" + " limit 1;")
        if isExists != 0:
            print("已采集：" , title)
        else:
            print("正在采集：", title)
            tags=soup.find(attrs={"name":"Keywords"})['content'].split(",")
            for tag in tags:
                sqltag = "SELECT * FROM images_tag WHERE tag =" + "'" + tag + "'" + " limit 1;"
                isExiststag = cursor.execute(sqltag)
                if isExiststag == 0:
                    cursor.execute("INSERT INTO images_tag (tag) VALUES (%s)", tag)
                cursor.execute("SELECT id FROM images_tag WHERE tag =" + "'" + tag + "'")
                for id in cursor.fetchall():
                    tagidlist.append(id[0])
            p = (title, str(tagidlist), time.strftime('%Y-%m-%d', time.localtime(time.time())), self.type_id, "1",url)
            cursor.execute("INSERT INTO images_page (title,tagid,sendtime,typeid,firstimg,crawler) VALUES (%s,%s,%s,%s,%s,%s)", p)
            pageid = cursor.lastrowid
            img_soup=soup.find("div",class_="page-show").text
            img_nums=re.sub("\D", "", img_soup)
            if len(img_nums)==6:
                img_num=img_nums[-2:]
            elif len(img_nums)<6:
                img_num = img_nums[-1]
            elif len(img_nums)>6:
                img_num = img_nums[-3:]
            id=url.split("-")[-1].split(".")[0]
            for i in range(1,int(img_num)+1):
                img_page_url=base_url+"article-"+id+"-"+str(i)+".html"
                img_page=s.get(img_page_url)
                img_soup=BeautifulSoup(img_page.text, "html.parser")
                img_url=img_soup.find("div",class_="pp hh").find("img").get("src")
                img_name = img_url.split("/")[-1]
                img_loc_path = self.img_path + time.strftime('%Y%m%d', time.localtime(
                    time.time())) + "/" + id + "/" + img_name
                imgp = pageid, img_loc_path,img_url
                cursor.execute("INSERT INTO images_image (pageid,imageurl,originurl) VALUES (%s,%s,%s)", imgp)
                if i==1:
                    cursor.execute(
                        "UPDATE images_page SET firstimg = " + "'" + img_loc_path + "'" + " WHERE id=" + "'" + str(
                            pageid) + "'")
                self.img_url_list.append({"img_url":img_url,"Referer":url,"id":id})

    def down_img(self,imgsrc,Referer,id):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
            "Referer": Referer
        }
        path = img_path + time.strftime('%Y%m%d', time.localtime(time.time())) + "/"
        page_id = id
        isdata = os.path.exists("../" + path + page_id)
        if not isdata:
            os.makedirs("../" + path + page_id)
        with open("../" + path + page_id + "/" + imgsrc.split("/")[-1].split(".")[0] + ".jpg", "wb") as f:
            print("已保存：" + path + page_id + "/" + imgsrc.split("/")[-1].split(".")[0] + ".jpg")
            f.write(s.get(imgsrc, headers=headers,verify=False, timeout=10).content)

    def run_page(self):
        while True:
            Spider.rlock.acquire()
            if len(self.page_url_list) == 0:
                Spider.rlock.release()
                break
            else:
                page_url = self.page_url_list.pop()
                Spider.rlock.release()
                try:
                    self.get_img(page_url)
                except Exception as e:
                    print(e)
                    pass

    def run_img(self):
        while True:
            Spider.rlock.acquire()
            if len(self.img_url_list) == 0 :
                Spider.rlock.release()
                break
            else:
                urls = self.img_url_list.pop()
                url = urls.get("img_url")
                Referer = urls.get("Referer")
                id = urls.get("id")
                Spider.rlock.release()
                try:
                    self.down_img(url, Referer, id)
                except Exception as e:
                    print(e)
                    pass

    def run_1(self):
        # 启动thread_num个进程来爬去具体的img url 链接
        url_threa_list=[]
        for th in range(self.thread_num):
            add_pic_t = threading.Thread(target=self.run_page)
            url_threa_list.append(add_pic_t)

        for t in url_threa_list:
            t.setDaemon(True)
            t.start()

        for t in url_threa_list:
            t.join()

    def run_2(self):
        # 启动thread_num个来下载图片
        for img_th in range(self.thread_num):
            download_t = threading.Thread(target=self.run_img)
            download_t.start()

# start_page是采集开始也，end是采集结束页，type不用修改，自动分类，起始页为1
if __name__ == "__main__":
    cl_list=[{"start_page": 1,"end_page":2, "type": "Cosplay", "type_id":6},
             {"start_page": 1,"end_page":2, "type": "性感", "type_id":1},
             {"start_page": 1, "end_page": 2, "type": "丝袜", "type_id": 3},
             {"start_page": 1, "end_page": 2, "type": "美腿", "type_id": 4},
             {"start_page": 1, "end_page": 2, "type": "美胸", "type_id": 5},
             {"start_page": 1, "end_page": 2, "type": "制服诱惑", "type_id": 7}
             ]


    for i in cl_list:
        spider = Spider(start_page_num=i.get("start_page"),end_page_num=i.get("end_page"), img_path='/static/images/', thread_num=3,
                        type=i.get("type"),type_id=i.get("type_id"))
        spider.get_url()
        spider.run_1()
        spider.run_2()
