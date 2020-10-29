# coding='UTF-8'
import sys

sys.path.append('../')
from bs4 import BeautifulSoup
import threading, pymysql, time, requests, os, urllib3
from config import mysql_config

requests.packages.urllib3.disable_warnings()


class Spider():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36',
        'Referer': "https://www.mzitu.com"
    }
    page_url_list = []
    img_url_list = []
    rlock = threading.RLock()
    s = requests.session()
    s.keep_alive = False
    s.headers = headers
    dbhost = {
        "host": mysql_config['HOST'],
        "dbname": mysql_config['NAME'],
        "user": mysql_config['USER'],
        "password": mysql_config['PASSWORD']
    }

    def __init__(self, page_num=10, img_path='imgdir', thread_num=5, type="xinggan", type_id=1):
        self.spider_url = 'https://www.mzitu.com/'
        self.page_number = int(page_num)
        self.img_path = img_path
        self.thread_num = thread_num
        self.type = type
        self.type_id = type_id

    def get_url(self):
        for i in range(2, self.page_number + 1):
            if i ==1:
                page = self.s.get(self.spider_url +"/"+self.type ,verify=False).text
            page=self.s.get(self.spider_url +"/"+self.type+"/page/"+str(i),verify=False).text
            soup = BeautifulSoup(page, "html.parser")
            page_base_url = soup.find("div",class_="postlist").find_all("li")
            for page_url in page_base_url:
                url = page_url.find("a").get("href")
                self.page_url_list.append(url)
            i = i + 1

    def get_img_url(self):
        db = pymysql.connect(self.dbhost.get("host"), self.dbhost.get("user"), self.dbhost.get("password"),
                             self.dbhost.get("dbname"))
        cursor = db.cursor()
        for img_base_url in self.page_url_list:
            tagidlist = []
            img_soup = BeautifulSoup(self.s.get(img_base_url,verify=False).text, "html.parser")
            img_num = img_soup.find("div", class_="pagenavi").text.split("…")[-1][0:-5]
            img_url = img_soup.find("div", class_="main-image").find("img").get("src").split("/")[0:-1]
            img_surl = "/".join(img_url)
            title = img_soup.find("h2", class_="main-title").text
            isExists = cursor.execute("SELECT * FROM images_page WHERE title =" + "'" + title + "'" + " limit 1;")
            tag_list = img_soup.find("div", class_="main-tags").find_all("a")
            if isExists == 1:
                print("已采集：" + title)
            else:
                for tags in tag_list:
                    tag=tags.text
                    print(tag)
                    sqltag = "SELECT * FROM images_tag WHERE tag =" + "'" + tag + "'" + " limit 1;"
                    isExiststag = cursor.execute(sqltag)
                    if isExiststag != 1:
                        cursor.execute("INSERT INTO images_tag (tag) VALUES (%s)", tag)
                    cursor.execute("SELECT id FROM images_tag WHERE tag =" + "'" + tag + "'")
                    for id in cursor.fetchall():
                        tagidlist.append(id[0])
                p = (title, str(tagidlist), time.strftime('%Y-%m-%d', time.localtime(time.time())), self.type_id, "1")
                cursor.execute("INSERT INTO images_page (title,tagid,sendtime,typeid,firstimg) VALUES (%s,%s,%s,%s,%s)",
                               p)
                print("开始采集：" + title)
                pageid = cursor.lastrowid
                for i in range(1, int(img_num)):
                    temp_url = img_soup.find("div", class_="main-image").find("img").get("src").split("/")
                    path = temp_url[-1][0:3]
                    new_url = img_surl + "/" + path + str("%02d" % i) + ".jpg"
                    img_src = temp_url[-3] + "/" + temp_url[-2] + "/" + path + str("%02d" % i) + ".jpg"
                    imgp = pageid, self.img_path + img_src
                    cursor.execute("INSERT INTO images_image (pageid,imageurl) VALUES (%s,%s)", imgp)
                    if i == 1:
                        cursor.execute(
                            "UPDATE images_page SET firstimg = " + "'" + self.img_path + img_src + "'" + " WHERE title=" + "'" + title + "'")
                    self.img_url_list.append(new_url)
                    i = i + 1
        db.close()

    def down_img(self, imgsrc):
        path = imgsrc.split("/")[-3] + "/" + imgsrc.split("/")[-2]
        isdata = os.path.exists("../" + self.img_path + path)
        if isdata == False:
            os.makedirs("../" + self.img_path + path)
        isfile = os.path.exists("../" + self.img_path + path + "/" + imgsrc.split("/")[-1])
        if isfile == False:
            with open("../" + self.img_path + path + "/" + imgsrc.split("/")[-1], "wb")as f:
                print("下载图片：" + self.img_path + path + "/" + imgsrc.split("/")[-1])
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
        # 启动thread_num个来下载图片
        for img_th in range(self.thread_num):
            download_t = threading.Thread(target=self.down_url)
            download_t.start()


if __name__ == '__main__':
    for i in [{"page": 2, "type": "xinggan", "type_id": 1},]:
        spider = Spider(page_num=i.get("page"), img_path='/static/images/', thread_num=10, type_id=i.get("type_id"),
                        type=i.get("type"))
        spider.get_url()
        spider.get_img_url()
        spider.run()
