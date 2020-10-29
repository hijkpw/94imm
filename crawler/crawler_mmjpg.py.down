#coding='UTF-8'

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

class Spider():
    rlock = threading.RLock()
    page_url_list=[]
    img_url_list=[]
    proxy_dict = ""
    base_url="http://www.mmmjpg.com/"
    def __init__(self,start_page_num,end_page_num,img_path,thread_num,type):
        self.start_page_num=start_page_num
        self.end_page_num=end_page_num
        self.img_path=img_path
        self.thread_num=thread_num
        self.type=type

    def get_url(self):
        for i in range(self.start_page_num,self.end_page_num+1):
            if i==0:
                page=s.get(self.base_url)
            else:
                page=s.get(self.base_url+self.type+"/"+str(i))
            soup=BeautifulSoup(page.text, "html.parser")
            url_soup=soup.find("div",class_="pic").find("ul").find_all("li")
            for li in url_soup:
                url=li.find("a").get("href")
                self.page_url_list.append(url)

    def get_img(self,url):
        db = pymysql.connect(dbhost.get("host"), dbhost.get("user"), dbhost.get("password"),dbhost.get("dbname"))
        cursor = db.cursor()
        tagidlist=[]
        page_id = url.split("/")[-1]
        page_url=self.base_url+"mm/"+page_id
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
            "Referer": page_url
        }
        info_page = s.get(self.base_url+"mm/" + page_id,headers=headers)
        info_page.encoding="utf-8"
        info_soup = BeautifulSoup(info_page.text,"html.parser")
        title=info_soup.find("div",class_="article").find("h1").text
        if "袜" in title or "丝" in title or "腿" in title:
            type_id = 2
        elif "青春" in title or "清纯" in title:
            type_id = 3
        elif "萝莉" in title:
            type_id = 4
        else:
            type_id = 1
        isExists = cursor.execute("SELECT title FROM images_page WHERE title =" + "'" + title + "'" + " limit 1;")
        img_m_src=info_soup.find("div",class_="content").find("a").find("img").get("src").split("/")[-3]
        if isExists != 0:
            print("已采集：" + title)
        else:
            tags=info_soup.find("div",class_="tags").find_all("a")
            for tag_soup in tags:
                tag=tag_soup.text
                sqltag = "SELECT * FROM images_tag WHERE tag =" + "'" + tag + "'" + " limit 1;"
                isExiststag = cursor.execute(sqltag)
                if isExiststag == 0:
                    cursor.execute("INSERT INTO images_tag (tag) VALUES (%s)", tag)
                cursor.execute("SELECT id FROM images_tag WHERE tag =" + "'" + tag + "'")
                for id in cursor.fetchall():
                    tagidlist.append(id[0])
            p = (title, str(tagidlist), time.strftime('%Y-%m-%d', time.localtime(time.time())), self.type_id, "1",page_url)
            cursor.execute("INSERT INTO images_page (title,tagid,sendtime,typeid,firstimg,crawler) VALUES (%s,%s,%s,%s,%s,%s)", p)
            print("开始采集："+title)
            pageid = cursor.lastrowid
            page=s.get(page_url,headers=headers)
            soup=BeautifulSoup(page.text,"html.parser")
            img_base=soup.find("div",class_="content").find("img").get("src").split("/")
            img_base_url="http://"+img_base[2]+"/"
            img_num=soup.find("div",class_="page").text.replace("全部图片下一页","").split("...")[-1]
            img_path = self.img_path + time.strftime('%Y%m%d', time.localtime(
                time.time())) + "/" + img_base[-2] +"/"
            for i in range(1,int(img_num)):
                img_loc_path=img_path+str(i)+".jpg"
                imgp = pageid, img_loc_path, img_base_url+img_base[-2]+"/"+str(i)+".jpg"
                cursor.execute("INSERT INTO images_image (pageid,imageurl,originurl) VALUES (%s,%s,%s)", imgp)
                if i == 1:
                    cursor.execute(
                        "UPDATE images_page SET firstimg = " + "'" + img_loc_path + "'" + " WHERE id=" + "'" + str(
                            pageid) + "'")
                self.img_url_list.append({"img_url": img_base_url+img_base[-2]+"/"+str(i)+".jpg", "Referer": url, "id": img_base[-2]})
                # print({"img_url": img_base_url+img_path+str(i)+".jpg", "Referer": img_base_url+img_base[-2], "id": img_base[-2]})



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
                page_url = self.page_url_list.pop()
                Spider.rlock.release()
                try:
                    self.get_img(page_url)
                except Exception as e:
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

# start_page是采集开始也，end是采集结束页，type不用修改，自动分类
if __name__ == "__main__":
    for i in [{"start_page": 1,"end_page":1, "type": "home"}]:
        spider=Spider(start_page_num=i.get("start_page"),end_page_num=i.get("end_page"),img_path='/static/images/',thread_num=10,type=i.get("type"))
        spider.get_url()
        spider.run_1()
        spider.run_2()