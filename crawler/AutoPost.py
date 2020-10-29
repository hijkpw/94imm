# -*- coding: utf-8 -*-
import sys

sys.path.append('../')
import pymysql,time,os,random,shutil,platform
from config import mysql_config

dbhost = {
    "host": mysql_config['HOST'],
    "dbname": mysql_config['NAME'],
    "user": mysql_config['USER'],
    "password": mysql_config['PASSWORD']
}

def do_post(file_dir,sleep_time="0"):
    db = pymysql.connect(dbhost.get("host"),dbhost.get("user"), dbhost.get("password"),dbhost.get("dbname"))
    cursor = db.cursor()
    for files in os.walk(file_dir):
        tagidlist = []
        sysstr = platform.system()
        if sysstr == "Windows":
            title=files[0].split("\\")[-1]
            os_path=file_dir.split("\\")[-1]
        elif sysstr == "Linux":
            title = files[0].split("/")[-1]
            os_path = file_dir.split("/")[-1]
        if title != os_path:
            tags=['cosplay','萝莉','美腿','丝袜','少女']
            isExists = cursor.execute("SELECT * FROM images_page WHERE title =" + "'" + title + "'" + " limit 1;")
            if isExists != 0:
                print("已存在：" + title)
            else:
                for tag in tags:
                    sqltag = "SELECT * FROM images_tag WHERE tag =" + "'" + tag + "'" + " limit 1;"
                    isExiststag = cursor.execute(sqltag)
                    if isExiststag != 1:
                        cursor.execute("INSERT INTO images_tag (tag) VALUES (%s)", tag)
                    cursor.execute("SELECT id FROM images_tag WHERE tag =" + "'" + tag + "'")
                    for id in cursor.fetchall():
                        tagidlist.append(id[0])
                p = (title, str(tagidlist), time.strftime('%Y-%m-%d', time.localtime(time.time())), "1", "1")
                cursor.execute("INSERT INTO images_page (title,tagid,sendtime,typeid,firstimg) VALUES (%s,%s,%s,%s,%s)",
                                   p)
                pageid = cursor.lastrowid
                rpath = "".join(random.sample('abcdefghijklmnopqrstuvwxyz', 7))
                count = 1
                for name in files[2]:
                    path=files[0]+"/"+name
                    rename=str(count)+"."+name.split(".")[-1]
                    path_isExists=os.path.exists("../static/images/"+rpath)
                    if not path_isExists:
                        os.makedirs("../static/images/"+rpath)
                    try:
                        shutil.move(path, "../static/images/"+rpath+"/"+rename)
                        imgp = "/static/images/" + rpath+"/"+rename
                        if count==1:
                            cursor.execute(
                                "UPDATE images_page SET firstimg = %s WHERE id=%s",(imgp,pageid))
                        cursor.execute("INSERT INTO images_image (pageid,imageurl) VALUES (%s,%s)", (pageid,imgp))

                    except Exception as e:
                        print(e)
                        break
                    count+=1
                try:
                    os.removedirs(files[0])
                except:
                    print("目录不为空，无法删除")
            print("发布完成：" + title)
        time.sleep(int(sleep_time))

# do_post("输入图片所在目录","发布间隔时间，默认0，单位秒")
if __name__ == "__main__":
    print("图片所在目录：")
    path=input("")
    print("自动发布间隔，0为全部发布，单位秒")
    send_time=input("")
    do_post(path,send_time)

