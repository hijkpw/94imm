import sys

sys.path.append('../')
import threading, pymysql,os,requests
from config import mysql_config


url_list=[]
origin_list=[]


rlock = threading.RLock()
dbhost = {
    "host": mysql_config['HOST'],
    "dbname": mysql_config['NAME'],
    "user": mysql_config['USER'],
    "password": mysql_config['PASSWORD']
}
db = pymysql.connect(dbhost.get("host"), dbhost.get("user"), dbhost.get("password"), dbhost.get("dbname"))
cursor = db.cursor()

def del_page():
    cursor.execute("Delete FROM images_page WHERE firstimg='1'")

def img_url():
    cursor.execute("SELECT * FROM images_image")
    for img_url in cursor.fetchall():
        isExiststag=os.path.exists(".."+img_url[2])
        host_sql = "SELECT crawler FROM images_page WHERE id =" + "'" + str(img_url[1]) + "'"
        cursor.execute(host_sql)
        if not isExiststag:
            print("添加图片：" + img_url[-1])
            url_list.append({"img_path": img_url[-2], "origin_url": img_url[-1], "host": cursor.fetchone()[0]})
        elif os.path.getsize(".."+img_url[2])==0:
            os.remove(".."+img_url[2])
            print("添加图片：" + img_url[-1])
            url_list.append({"img_path": img_url[-2], "origin_url": img_url[-1], "host": cursor.fetchone()[0]})
        elif "http://www.nvshenge.com" in img_url[-1]:
            image_path=img_url[-2].split("/")[-1][0:8]
            origin_url="http://nvshenge.com/uploads/image/"+image_path+"/"+img_url[-2].split("/")[-1]
            print("添加图片：" + origin_url)
            url_list.append({"img_path": img_url[-2], "origin_url": origin_url, "host": cursor.fetchone()[0]})
        else:
            continue


def down_img():
    while True:
        rlock.acquire()
        if len(url_list) == 0:
            rlock.release()
            break
        else:
            img_url = url_list.pop()
            rlock.release()
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
                    "Referer": img_url.get("host")
                }
                img_path=img_url.get("img_path")
                path = "/".join(img_path.split("/")[1:-1])
                is_path=os.path.exists("../"+path)
                if "http://nvshenge.com" == img_url.get("origin_url")[0:19]:
                    continue
                if not is_path:
                    os.makedirs("../" + path)
                origin_url=img_url.get("origin_url")
                with open (".."+img_path,"wb") as w:
                    w.write(requests.get(origin_url, headers=headers,verify=False,timeout=5).content)
                print("下载完成："+origin_url)
            except Exception as e:
                # url_list.append({"img_path":img_url.get("img_path"),"origin_url":img_url.get("origin_url"),"host":img_url.get("host")})
                # print("下载失败，重新添加到列表中")
                pass

if __name__ == "__main__":
    del_page()
    try:
        img_url()
    except Exception as e:
        print(e)
    for i in range(10):
        t2 = threading.Thread(target=down_img)
        t2.start()
