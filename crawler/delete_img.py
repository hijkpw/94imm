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
    cursor.execute("SELECT imageurl FROM images_image WHERE pageid =" + "'" + id + "'")
    for img in cursor.fetchall():
        try:
            os.remove(img[0])
        except FileNotFoundError:
            print("***************")
            print("图片不存在或未下载")
            pass
        except Exception as e:
            print("***************")
            print("图片删除失败，错误信息：",e)
    cursor.execute("Delete FROM images_image WHERE pageid=" + "'" + id + "'")
    print("***************")
    print("图片删除成功")
    print("***************")
    print("采集数据删除成功")
    try:
        ls = os.listdir('../cache')
        for i in ls:
            os.remove("../cache/"+i)
        os.system("sh ../restart.sh")
        print("***************")
        print("缓存更新成功")
    except Exception as e:
        print("***************")
        print("缓存更新失败，错误信息：",e)

if __name__=="__main__":
    print("请输入要删除的图集ID")
    id=input()
    del_page(id)