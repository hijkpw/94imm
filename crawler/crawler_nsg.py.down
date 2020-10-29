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

# dbhost = {
#     "host": "192.168.1.67",
#     "dbname": "silumz",
#     "user": "silumz",
#     "password": "fendou2009"
# }

base_url="http://www.nvshenge.com/mntp/"
img_path='/static/images/'

class Spider():
    page_url_list = []
    img_url_list = []
    rlock = threading.RLock()
    proxy_dict = ""
    def __init__(self, start_page_num, end_page_num,img_path, thread_num, type="home"):
        self.start_page_num = start_page_num
        self.end_page_num=end_page_num
        self.img_path = img_path
        self.thread_num = thread_num
        self.type = type

    def get_url(self):
        for i in range(self.start_page_num -1, self.end_page_num -1):
            if i==0:
                page=s.get(base_url, verify=False).text
            else:
                page = s.get(base_url + "list_"+str(i)+".html", verify=False).text
            soup = BeautifulSoup(page, "html.parser")
            all_list = soup.find_all("a", class_="PicTxt")
            i = 0
            for info_soup in all_list:
                url=info_soup.get("href")
                title=info_soup.text
                self.page_url_list.append({"url":url,"title":title})
                i += 1


    def get_img(self):
        db = pymysql.connect(dbhost.get("host"), dbhost.get("user"), dbhost.get("password"),
                             dbhost.get("dbname"))
        cursor = db.cursor()
        while True:
            self.rlock.acquire()
            if len(self.page_url_list) == 0:
                self.rlock.release()
                break
            else:
                page_info= self.page_url_list.pop()
                page_url = page_info.get("url")
                title = page_info.get("title")
                if "袜" in title or "丝" in title or "腿" in title:
                    type_id = 2
                elif "青春" in title or "清纯" in title:
                    type_id = 3
                elif "萝莉" in title:
                    type_id = 4
                else:
                    type_id = 1
                self.rlock.release()
                try:
                    tagidlist = []
                    page = s.get(page_url, verify=False).text
                    soup = BeautifulSoup(page, "html.parser")
                    img_num_soup = soup.find("div", class_="articleTop yh").find("h1").text
                    img_num = int(img_num_soup[img_num_soup.find("(1/") + 3:img_num_soup.find("）")])
                    isExists = cursor.execute(
                        "SELECT title FROM images_page WHERE title =" + "'" + title + "'" + " limit 1;")
                    if isExists != 0:
                        print("已采集：" + title)
                    else:
                        taglist = soup.find("div",class_="articleTag l").find_all("dd")
                        for tag_soup in taglist:
                            tag=tag_soup.text
                            sqltag = "SELECT * FROM images_tag WHERE tag =" + "'" + tag + "'" + " limit 1;"
                            isExiststag = cursor.execute(sqltag)
                            if isExiststag == 0:
                                cursor.execute("INSERT INTO images_tag (tag) VALUES (%s)", tag)
                            cursor.execute("SELECT id FROM images_tag WHERE tag =" + "'" + tag + "'")
                            for id in cursor.fetchall():
                                tagidlist.append(id[0])
                        p = (
                        title, str(tagidlist), time.strftime('%Y-%m-%d', time.localtime(time.time())), type_id,
                        "1", page_url)
                        cursor.execute(
                            "INSERT INTO images_page (title,tagid,sendtime,typeid,firstimg,crawler) VALUES (%s,%s,%s,%s,%s,%s)",
                            p)
                        print("开始采集：" + title)
                        pageid = cursor.lastrowid
                        for i in range(0, int(img_num)):
                            img_id = page_url.split("/")[-1].split(".")[0]
                            if i==0:
                                url=page_url
                            else:
                                url = "/".join(page_url.split("/")[0:-1])+"/"+img_id+"_"+str(i)+".html"
                            img_page=s.get(url, verify=False).text
                            img_soup= BeautifulSoup(img_page, "html.parser")
                            img_src=img_soup.find("div",id="ArticlePicBox1").find("img").get("src")
                            img_loc_path = self.img_path + time.strftime('%Y%m%d', time.localtime(
                                time.time())) + "/"+img_id+"/"+img_src.split("/")[-1]
                            if i == 0:
                                cursor.execute(
                                    "UPDATE images_page SET firstimg = " + "'" + img_loc_path + "'" + " WHERE title=" + "'" + title + "'")
                            imgp = pageid, img_loc_path, img_src
                            cursor.execute("INSERT INTO images_image (pageid,imageurl,originurl) VALUES (%s,%s,%s)",
                                           imgp)
                            self.img_url_list.append({"url": img_src, "path": img_loc_path, "referer": page_url})
                except Exception as e:
                    cursor.execute("Delete FROM images_page WHERE title=" + "'" + title + "'")
                    print("采集失败(已删除)：",title)
                    print("连接地址：", page_url)
                    print("错误信息：", e)
        db.close()

    def down_img(self, imgsrc, imgpath, referer):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
            "Referer": referer
        }
        isdata = os.path.exists(".." +"/".join(imgpath.split("/")[0:-1]))
        if not isdata:
            os.makedirs(".."+"/".join(imgpath.split("/")[0:-1]))
        with open(".."+ imgpath, "wb")as f:
            f.write(requests.get(imgsrc, headers=headers, verify=False).content)
            print("下载图片：" + imgpath)

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
                    url = img_url.get("url")
                    path = img_url.get("path")
                    referer = img_url.get("referer")
                    self.down_img(url, path, referer)
                except Exception as e:
                    print(e)
                    self.img_url_list.append(
                        {"url": img_url.get("url"), "path": img_url.get("path"), "referer": img_url.get("referer")})
                    pass

    def run_1(self):
        # 启动thread_num个进程来爬去具体的img url 链接
        url_threa_list = []
        for th in range(self.thread_num):
            add_pic_t = threading.Thread(target=self.get_img)
            url_threa_list.append(add_pic_t)

        for t in url_threa_list:
            t.setDaemon(True)
            t.start()

        for t in url_threa_list:
            t.join()

    def run_2(self):
        # 启动thread_num个来下载图片
        for img_th in range(self.thread_num):
            download_t = threading.Thread(target=self.down_url)
            download_t.start()


# start_page是采集开始也，end是采集结束页，type不用修改，自动分类，起始页为1
if __name__ == "__main__":
    for i in [{"start_page": 1,"end_page":2, "type": "index"}]:
        spider = Spider(start_page_num=i.get("start_page"),end_page_num=i.get("end_page"), img_path='/static/images/', thread_num=10,
                        type=i.get("type"))
        spider.get_url()
        spider.run_1()
        spider.run_2()