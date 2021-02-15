import sys

sys.path.append('../')
import pymysql,os
from config import mysql_config

dbhost = {
    "host": mysql_config['HOST'],
    "dbname": mysql_config['NAME'],
    "user": mysql_config['USER'],
    "password": mysql_config['PASSWORD']
}

db = pymysql.connect(dbhost.get("host"), dbhost.get("user"), dbhost.get("password"), dbhost.get("dbname"))
cursor = db.cursor()

def del_page(id):
    cursor.execute("Delete FROM images_page WHERE id=" + "'" + id + "'")

def check_page_image():
    cursor.execute("SELECT id FROM images_page where id>3277")
    for row in cursor.fetchall():
        pageid = str(row[0])
        has_image = cursor.execute("select id from images_image where pageid='" + pageid + "' limit 1")
        if has_image == 0:
            print("page id: " + pageid + " has no image, delete")
            #del_page(pageid)


if __name__=="__main__":
    check_page_image()
