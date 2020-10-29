# encoding: utf-8
import sys

sys.path.append('../')
from bs4 import BeautifulSoup
import threading, pymysql, time, requests, os, urllib3, re
from config import mysql_config

requests.packages.urllib3.disable_warnings()
# 数据库连接信息
dbhost = {
    "host": mysql_config['HOST'],
    "dbname": mysql_config['NAME'],
    "user": mysql_config['USER'],
    "password": mysql_config['PASSWORD']
}


class Spider():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36',
        'Referer': "http://www.xgmmtk.com/"
    }
    page_url_list = []
    img_url_list = []
    rlock = threading.RLock()
    # s = requests.session()

    def __init__(self, img_path='imgdir', thread_number=5):
        self.spider_url = 'http://www.xgmmtk.com/'
        self.img_path = img_path
        self.thread_num = thread_number

    def get_url(self):
        page = requests.get("http://www.xgmmtk.com/")
        soup = BeautifulSoup(page.text, "html.parser")
        a_soup = soup.find_all("a")
        for a in a_soup:
            url = "http://www.xgmmtk.com/" + a.get("href")
            self.page_url_list.append(url)

    def get_img(self):
        db = pymysql.connect(dbhost.get("host"), dbhost.get("user"), dbhost.get("password"), dbhost.get("dbname"))
        cursor = db.cursor()
        while True:
            self.rlock.acquire()
            if len(self.page_url_list) == 0:
                self.rlock.release()
                break
            else:
                page_url = self.page_url_list.pop()
                self.rlock.release()
                page = requests.get(page_url)
                soup=BeautifulSoup(page.text,"html.parser")
                title=soup.title.string.replace("�","")
                isExists = cursor.execute(
                    "SELECT title FROM images_page WHERE title =" + "'" + title + "'" + " limit 1;")
                if isExists == 0:
                    print("添加采集：",title)
                    if "袜" in title or "丝" in title:
                        type_id = 3
                        tagidlist=[3679,3700,3719,3628]
                    elif "腿" in title:
                        type_id = 4
                        tagidlist=[3679,3700,3719,3628]
                    elif "青春" in title or "清纯" in title or "萝莉" in title:
                        tagidlist=[3694,3627,3635]
                        type_id = 2
                    elif "胸" in title:
                        type_id = 5
                        tagidlist=[3694,3627,3635]
                    else:
                        tagidlist=[3630,3623,3618,3642]
                        type_id = 1
                    p = (
                        title, str(tagidlist), time.strftime('%Y-%m-%d', time.localtime(time.time())), type_id,
                        "1",
                        page_url)
                    cursor.execute(
                        "INSERT INTO images_page (title,tagid,sendtime,typeid,firstimg,crawler) VALUES (%s,%s,%s,%s,%s,%s)",
                        p)
                    pageid = cursor.lastrowid
                    img = soup.find_all("img")
                    i=0
                    page_id=page_url[page_url.find("?id=")+4:-1]
                    img_path = self.img_path + time.strftime('%Y%m%d', time.localtime(
                        time.time())) + "/" +page_id + "/"
                    for imgurl in img:
                        imgsrc = "http://www.xgmmtk.com/" + imgurl.get("src")
                        self.img_url_list.append(
                            {"img_url": imgsrc, "Referer": page_url,
                             "id": page_id})
                        if i==0:
                            cursor.execute(
                                "UPDATE images_page SET firstimg = " + "'" + img_path+imgsrc.split("/")[-1] + "'" + " WHERE id=" + "'" + str(
                                    pageid) + "'")
                        i+=1
                else:
                    print("已采集")
                    pass
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
        isfile = os.path.exists("../" + path + page_id + "/" + imgsrc.split("/")[-1])
        if not isfile:
            with open("../" + path + page_id + "/" + imgsrc.split("/")[-1], "wb") as f:
                print("已保存：" ,imgsrc)
                f.write(requests.get(imgsrc, headers=headers,verify=False).content)



    def run_img(self):
        while True:
            Spider.rlock.acquire()
            if len(self.img_url_list) == 0 :
                Spider.rlock.release()
                continue
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

    def run(self):
        # 启动thread_num个来下载图片
        for img_th in range(self.thread_num):
            download_t = threading.Thread(target=self.run_img)
            download_t.start()

        for img_th in range(self.thread_num):
            run_t = threading.Thread(target=self.get_img)
            run_t.start()

if __name__ == "__main__":
    spider=Spider(img_path='/static/images/',thread_number=10)
    spider.get_url()
    spider.run()
