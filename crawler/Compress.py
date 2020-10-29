# -*- coding: utf-8 -*-
import sys

sys.path.append('../')
from  PIL import Image as Img
import os,threading,platform

class Compress():
    file_list=[]
    rlock = threading.RLock()
    def __init__(self,file_dir,new_dir=None,th_num=10):
        self.file_dir=file_dir
        self.new_dir=new_dir
        self.th_num=th_num

    sysstr = platform.system()
    if sysstr == "Windows":
        p="\\"
    else:
        p="/"

    def get_file_name(self):
        for files in os.walk(self.file_dir):
            for name in files[2]:
                file=files[0]+self.p+name
                size=int(os.path.getsize(file) / 1024)
                if size>400:
                    self.file_list.append(file)

    def pl_compress(self,file_path):
        path = file_path.split(self.p)
        name = path[-1]
        image = Img.open(file_path)
        image.save("/".join(path[0:-1])+self.p+name, quality=85)
        print("压缩完成：" + file_path)

    def pl_compress_new(self,file_path):
        path = file_path.split(self.p)
        name = path[-1]
        image = Img.open(file_path)
        new_name=self.new_dir+self.p+"/".join(path[-2:-1])+self.p
        is_ex=os.path.exists(new_name)
        if not is_ex:
            os.makedirs(new_name)
        image.save(new_name+name, quality=85)
        print("压缩完成：" + file_path)

    def do_work(self):
        while True:
            Compress.rlock.acquire()
            if len(Compress.file_list) == 0:
                Compress.rlock.release()
                break
            else:
                file_path = Compress.file_list.pop()
                Compress.rlock.release()
                try:
                    if new_dir == None:
                        self.pl_compress(file_path)
                    else:
                        self.pl_compress_new(file_path)
                except Exception as e:
                    pass


    def run(self):
        for i in range(self.th_num):
            download_t = threading.Thread(target=self.do_work)
            download_t.start()


if __name__ == "__main__":
    print("输入源图片所在路径")
    dir_name = input("")
    print("1.覆盖原图片，2.压缩到新路径")
    in_num=input("")
    new_dir=None
    if in_num=="2":
        print("输入保存路径")
        new_dir = input("")
    compress=Compress(dir_name,new_dir,10)
    compress.get_file_name()
    compress.run()