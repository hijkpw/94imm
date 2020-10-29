# coding='UTF-8'

import sys

sys.path.append('../')
from bs4 import BeautifulSoup
import threading, pymysql, time, requests, os, urllib3, re,random
from config import mysql_config

requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 5
s = requests.session()
s.keep_alive = False
# 数据库连接信息
dbhost = {
    "host": mysql_config['HOST'],
    "dbname": mysql_config['NAME'],
    "user": mysql_config['USER'],
    "password": mysql_config['PASSWORD']
}
base_url="https://mm131.pro"

class Spider():
    rlock = threading.RLock()
    page_url_list = []
    img_url_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
        "Referer": base_url
    }

    def __init__(self, page_num, img_path, thread_num, type_id=1, type="home",tagslist=["性感美女","诱惑美女","大胸美女","萌妹子"]):
        self.page_num = page_num
        self.img_path = img_path
        self.thread_num = thread_num
        self.type_id = type_id
        self.type = type
        self.tagslist= tagslist

    def get_url(self):
        for i in range(4,self.page_num):
            page = s.get(base_url+"/e/action/ListInfo/?classid="+str(self.type_id), headers=self.headers,verify=False)
            soup = BeautifulSoup(page.text, "html.parser")
            try:
                page_div = soup.find("dl", class_="list-left public-box").find_all("dd")
            except:
                print("采集错误，跳过本条")
                continue
            del page_div[-1]
            for dd in page_div:
                url = dd.find("a").get("href")
                self.page_url_list.append(base_url+url)

    def get_img(self,url):
        db = pymysql.connect(dbhost.get("host"), dbhost.get("user"), dbhost.get("password"), dbhost.get("dbname"))
        cursor = db.cursor()
        tagidlist = []
        page = s.get(url, headers=self.headers)
        page.encoding='UTF-8'
        soup = BeautifulSoup(page.text, "html.parser")
        # page_div = soup.find("div", class_="content-pic")
        title = soup.title.string.replace("_znns.com宅男钕神",'')
        title = title.replace("_znns.com",'')
        isExists = cursor.execute("SELECT title FROM images_page WHERE title =" + "'" + title + "'" + " limit 1;")
        if isExists != 0:
            print("isExists:" + title)
        else:
            tagslist = re.findall('<meta name="keywords" content="(.*?)" />', page.text)
            for tags in tagslist:
                for tag in tags.split(","):
                    sqltag = "SELECT * FROM images_tag WHERE tag =" + "'" + tag + "'" + " limit 1;"
                    isExiststag = cursor.execute(sqltag)
                    if isExiststag == 0:
                        cursor.execute("INSERT INTO images_tag (tag) VALUES (%s)", tag)
                    cursor.execute("SELECT id FROM images_tag WHERE tag =" + "'" + tag + "'")
                    for id in cursor.fetchall():
                        tagidlist.append(id[0])
            p = (
            title, str(tagidlist), time.strftime('%Y-%m-%d', time.localtime(time.time())), self.type_id, "1", url)
            cursor.execute(
                "INSERT INTO images_page (title,tagid,sendtime,typeid,firstimg,crawler) VALUES (%s,%s,%s,%s,%s,%s)", p)
            print("down：" + title)
            pageid = cursor.lastrowid
            img_num_soup = soup.find("div", class_="content-page").find("span").text
            img_num = "".join(re.findall(r"\d", img_num_soup))
            for i in range(1, int(img_num)):
                headers = self.headers.copy()
                headers.update({"Referer":url})
                id = url.split("/")[-1].split(".")[0]
                if i==1:
                    img_page_url=url
                else:
                    img_page_url = "/".join(url.split("/")[0:-1]) + "/" + id + "_" + str(i) + ".html"
                img_page=s.get(img_page_url,headers=headers,verify=False)
                # page.encoding = 'utf-8'
                img_soup=BeautifulSoup(img_page.text,"html.parser")
                img_url = img_soup.find("div",class_="content-pic").find("img").get("src")
                img_name =img_url.split("/")[-1]
                id=url.split("/")[-1].split(".")[0]
                img_loc_path = self.img_path + time.strftime('%Y%m%d', time.localtime(
                    time.time())) + "/" + id + "/" +img_name
                if i == 1:
                    cursor.execute(
                        "UPDATE images_page SET firstimg = " + "'" + img_loc_path + "'" + " WHERE id=" + "'" + str(
                            pageid) + "'")
                imgp = pageid, img_loc_path,img_url
                cursor.execute("INSERT INTO images_image (pageid,imageurl,originurl) VALUES (%s,%s,%s)", imgp)
                i += 1
                data={"img_url":img_url,"Referer":url,"id":id}
                if data in self.img_url_list:
                    continue
                else:
                    self.img_url_list.append(data)

    def down_img(self,imgsrc,Referer,id):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
            "Referer": Referer
        }
        path = self.img_path + time.strftime('%Y%m%d', time.localtime(time.time())) + "/"
        page_id = id
        isdata = os.path.exists("../" + path + page_id)
        if not isdata:
            os.makedirs("../" + path + page_id)
        isfile = os.path.exists("../" + path + page_id + "/" + imgsrc.split("/")[-1].split(".")[0] + ".jpg")
        if not isfile:
            with open("../" + path + page_id + "/" + imgsrc.split("/")[-1].split(".")[0] + ".jpg", "wb") as f:
                print("已保存：" + path + page_id + "/" + imgsrc.split("/")[-1].split(".")[0] + ".jpg")
                f.write(s.get(imgsrc, headers=headers,verify=False).content)

    def run_page(self):
        while True:
            Spider.rlock.acquire()
            if len(self.page_url_list) == 0:
                Spider.rlock.release()
                break
            else:
                try:
                    page_url = self.page_url_list.pop()
                except Exception as e:
                    print(e)
                    pass
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


# page是采集深度，从1开始，采集第一页即采集最新发布。type是源站分类，type_id是对应本站分类的id
if __name__ == "__main__":
    for i in [{"page": 20, "type": "xinggan", "type_id": 1},{"page":1,"type":"qingchun","type_id": 2}]:
        spider = Spider(page_num=i.get("page"), img_path='/static/images/', thread_num=10, type_id=i.get("type_id"),
                        type=i.get("type"),tagslist=["性感美女","诱惑美女","大胸美女","萌妹子"])
        spider.get_url()
        spider.run_1()
        spider.run_2()
