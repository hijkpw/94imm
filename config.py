mysql_config = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dbname',
        'USER': 'user',
        'PASSWORD': 'pass',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
# 数组形式，可以添加多个域名
allow_url=["www.imeizi.me","imeizi.me", "127.0.0.1"]
# 缓存超时时间，服务器性能好可缩短此时
cache_time=300
# 使用的模板（暂时开放一个）
templates="zde"
# 网站名
site_name="爱妹子"
# 一键脚本自动添加
site_url = "https://imeizi.me"
# 网站关键词
key_word = "爱妹子,美女写真,性感美女,美女图片,高清美女"
# 网站说明
description = "每日分享最新最全的美女图片和高清性感美女图片，性感妹子、日本妹子、台湾妹子、清纯妹子、妹子自拍以及街拍美女图片"
# 底部联系邮箱
email = "admin@imeizi.me"
# 网站调试模式
debug = False
# 友联
friendly_link = [{"name":"网络跳跃","link":"https://hijk.art"},{"name":"V2ray科技","link":"https://v2raytech.com"}]
