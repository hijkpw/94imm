# 安装说明：
参数配置
> 配置文件为根目录下的config.py
```python
# 数据库信息，一键脚本自动添加
mysql_config = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '94imm',
        'USER': '94imm',
        'PASSWORD': '94imm',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
# 数组形式，可以添加多个域名
allow_url=["www.94imm.com","94imm.com"]
# 缓存超时时间，服务器性能好可缩短此时
cache_time=300
# 使用的模板（暂时开放一个）
templates="zde"
# 网站名
site_name="94iMM"
# 一键脚本自动添加
site_url = "https://www.94imm.com"
# 网站关键词
key_word = "关键词1,关键词2,关键词3"
# 网站说明
description = "这是一个高质量的自动爬虫"
# 底部联系邮箱
email = "admin@94imm.com"
# 网站调试模式
debug = False
# 页面底部友情链接
friendly_link = [{"name":"94imm","link":"https://www.94imm.com"},{"name":"获取源码","link":"https://github.com/Turnright-git/94imm.git"}]

```

使用说明
> 进入项目根目录
```shell
启动网站
./run.sh s
关闭网站
./run.sh stop
重启网站
./run.sh r
清空网站缓存（使所做的修改立即生效）
./run.sh c
```
> 项目模板目录templates，base.html中可直接添加统计代码

手动安装说明
> 项目依赖python3.6 mysql5.6

```
git clone https://github.com/hijkpw/94imm.git
cd 94imm
vi config.py  #参照配置说明修改
vi uwsgi.ini  #修改uwsgi配置
```
如需使用反向代理，在nginx.conf中添加如下server段
```
server {
    listen       80;
    server_name  localhost; # 网站域名

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
    location /static {
        root /var/www/94imm;
        expires max;
    }

    location /favicon.ico {
        root /var/www/94imm;
    }
}
```
