#!/usr/bin/python3
import sys

sys.path.append('../')
from bs4 import BeautifulSoup
import threading,pymysql,time,requests,os,urllib3
from config import mysql_config
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 5

class Spider():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36',
        'Referer': "https://www.meitulu.com"
    }
    page_url_list = []
    img_url_list = []
    rlock = threading.RLock()
    s=requests.session()
    s.keep_alive = False
    dbhost = {
        "host": mysql_config['HOST'],
        "dbname": mysql_config['NAME'],
        "user": mysql_config['USER'],
        "password": mysql_config['PASSWORD']
    }

    def __init__(self,page_number=10,img_path='imgdir',thread_number=5,type='xinggan',type_id=1):
        self.spider_url = 'https://www.meitulu.com/t/'+type
        self.page_number = int(page_number)
        self.img_path = img_path
        self.thread_num = thread_number
        self.type_id = type_id

    def get_url(self):
        db = pymysql.connect(self.dbhost.get("host"), self.dbhost.get("user"), self.dbhost.get("password"),
                             self.dbhost.get("dbname"))
        cursor = db.cursor()
        for i in range(1, self.page_number+1):
            page_base_url = BeautifulSoup(requests.get(self.spider_url + "/" + str(i) + ".html").content.decode("utf-8"),
                                          "html.parser")
            if i == 1:
                page_base_url = BeautifulSoup(requests.get(self.spider_url).content.decode("utf-8"), "html.parser")
            img_ul = page_base_url.find("ul", class_="img").find_all("li")
            for img_li in img_ul:
                page_url = img_li.find("p", class_="p_title").find("a").get("href")
                self.page_url_list.append(page_url)
        db.close()

    def get_img_url(self):
        db = pymysql.connect(self.dbhost.get("host"), self.dbhost.get("user"), self.dbhost.get("password"), self.dbhost.get("dbname"))
        cursor = db.cursor()
        for page_url in reversed(self.page_url_list):
            tagidlist = []
            img_div_soup = BeautifulSoup(requests.get(page_url).content.decode("utf-8"), "html.parser")
            img_base_url = img_div_soup.find("img", class_="content_img").get("src").split("/")
            img_url = "/".join(img_base_url[0:-1])
            title = img_div_soup.find("div", class_="weizhi").find("h1").text.replace(" 萝莉丝袜写真套图","")
            isExists =cursor.execute("SELECT * FROM images_page WHERE title =" + "'" + title + "'" + " limit 1;")
            if isExists != 0:
                print ("已采集:"+title)
            else:
                tag_list = img_div_soup.find("div", class_="fenxiang_l").find_all("a")
                for tag in tag_list:
                    sqltag = "SELECT * FROM images_tag WHERE tag =" + "'" + tag.text + "'" + " limit 1;"
                    isExiststag = cursor.execute(sqltag)
                    if isExiststag == 0:
                        cursor.execute("INSERT INTO images_tag (tag) VALUES (%s)", tag.text)
                    cursor.execute("SELECT id FROM images_tag WHERE tag =" + "'" + tag.text + "'")
                    for id in cursor.fetchall():
                        tagidlist.append(id[0])
                p = (
                title, str(tagidlist), time.strftime('%Y-%m-%d', time.localtime(time.time())), self.type_id, "1", page_url)
                cursor.execute(
                    "INSERT INTO images_page (title,tagid,sendtime,typeid,firstimg,crawler) VALUES (%s,%s,%s,%s,%s,%s)",
                    p)
                pageid =cursor.lastrowid
                ima_num_tem = img_div_soup.find("div", id="pages").text
                img_num = ima_num_tem[-6:-4]
                i = 1
                for i in range(1, int(img_num)):
                    img_src = img_url + "/" + str(i) + "." + img_base_url[-1].split(".")[-1]
                    img_loc_path = self.img_path + img_base_url[-2]+"/"+ str(i) + "." + img_base_url[-1].split(".")[-1]
                    imgp = pageid, img_loc_path,img_src
                    if i == 1:
                        cursor.execute(
                            "UPDATE images_page SET firstimg = " + "'" + img_loc_path + "'" + " WHERE title=" + "'" + title + "'")
                    i = i + 1
                    cursor.execute("INSERT INTO images_image (pageid,imageurl,originurl) VALUES (%s,%s,%s)", imgp)
                    self.img_url_list.append(img_src)
                print("添加："+title)
        db.close()

    def down_img(self,imgsrc):
        path = imgsrc.split("/")[-2]
        isdata = os.path.exists("../" + self.img_path + path)
        if isdata == False:
            os.makedirs("../" + self.img_path + path)
        with open("../" + self.img_path + path + "/" + imgsrc.split("/")[-1], "wb")as f:
            f.write(requests.get(imgsrc, headers=self.headers, verify=False).content)

    def down_url(self):
        while True:
            Spider.rlock.acquire()
            if len(Spider.img_url_list) == 0:
                Spider.rlock.release()
                break
            else:
                img_url = Spider.img_url_list.pop()
                Spider.rlock.release()
                try:
                    self.down_img(img_url)
                except Exception as e:
                    pass


    def run(self):
        # print("开始下载")
        # 启动thread_num个进程来爬去具体的img url 链接
        for th in range(self.thread_num):
            add_pic_t = threading.Thread(target=self.get_img_url)
            add_pic_t.start()

        # 启动thread_num个来下载图片
        for img_th in range(self.thread_num):
            download_t = threading.Thread(target=self.down_url)
            download_t.start()


if __name__ == '__main__':
    for i in [{"page": 3, "type": "1290", "type_id": 4}]:
        spider = Spider(page_number=i.get("page"), img_path='/static/images/', thread_number=10,type=i.get("type"),type_id=i.get("type_id"))
        spider.get_url()
        spider.get_img_url()
        spider.run()