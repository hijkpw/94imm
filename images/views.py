from django.shortcuts import render
from images.models import *
import random, json
from django.http import HttpResponse
from config import site_name, site_url, key_word, description, email,friendly_link



def index(request):
    if request.method == "GET":
        imgs = []
        page_list = Page.objects.all().order_by('?')[:50]
        typedict, typelist = type_list()
        for pid in page_list:
            id = pid.id
            title = pid.title
            firstimg = pid.firstimg
            sendtime = pid.sendtime
            hot = pid.hot
            type_id = pid.typeid
            imgs.append({"pid": id, "firstimg": firstimg, "title": title, "sendtime": sendtime, "hot": hot,
                         "type": typedict[type_id], "type_id": type_id})
        return render(request, 'index.html',
                      {"data": imgs, "typelist": typelist, "siteName": site_name, "keyWord": key_word,
                       "description": description, "siteUrl": site_url, "email": email})


def page(request, i_id):
    # try:
    page_arr = Page.objects.get(id=i_id)
    imgs = []
    tags = []
    typedict, typelist = type_list()
    page_hot = page_arr.hot
    page_arr.hot = page_hot + 1
    page_arr.save()
    time = page_arr.sendtime
    typeid = page_arr.typeid
    pagetype = Type.objects.get(id=typeid).type
    title = page_arr.title
    taglist = page_arr.tagid
    tag_arr = taglist.replace("[", "").replace("]", "").split(",")
    for t_id in tag_arr:
        tagid = t_id.strip(" ")
        tag = Tag.objects.get(id=tagid).tag
        tags.append({"tname": tag, "tid": tagid})
    imglist = Image.objects.filter(pageid=i_id)
    for img_arr in imglist:
        img = img_arr.imageurl
        imgs.append(img)
    if len(tags) > 4:
        tags = random.sample(tags, 4)
    typename = typedict[typeid]
    return render(request, 'page.html',
                  {"data": imgs, "tag": tags, "title": title, "type": pagetype, "typeid": str(typeid), "time": time,
                   "similar": page_similar(typeid), "typelist": typelist, "pageid": i_id, "siteName": site_name,
                   "keyWord": key_word, "description": description, "typeName": typename, "siteUrl": site_url,
                   "email": email,"friendly_link":friendly_link})


def tag(request, tid):
    if request.method == "GET":
        imgs = []
        page_list = Page.objects.all().order_by("-id")
        typedict, typelist = type_list()
        for pid in page_list:
            if tid in pid.tagid:
                id = pid.id
                title = pid.title
                firstimg = pid.firstimg
                type_id = pid.typeid
                sendtime = pid.sendtime
                hot = pid.hot
                imgs.append({"pid": id, "firstimg": firstimg, "title": title, "sendtime": sendtime, "hot": hot,
                             "type": typedict[type_id], "type_id": type_id})
        return render(request, 'index.html',
                      {"data": imgs, "typelist": typelist, "siteName": site_name, "keyWord": key_word,
                       "description": description, "siteUrl": site_url, "email": email,"friendly_link":friendly_link})


def type(request, typeid):
    if request.method == "GET":
        imgs = []
        typedict, typelist = type_list()
        page_list = Page.objects.filter(typeid=typeid).order_by("-id")
        for pid in page_list:
            title = pid.title
            firstimg = pid.firstimg
            id = pid.id
            hot = pid.hot
            type_id = pid.typeid
            sendtime = pid.sendtime
            imgs.append({"pid": id, "firstimg": firstimg, "title": title, "sendtime": sendtime, "hot": hot,
                         "type": typedict[type_id], "type_id": type_id})
        return render(request, 'category.html',
                      {"data": imgs, "typelist": typelist, "typeid": str(typeid), "siteName": site_name,
                       "keyWord": key_word, "description": description, "siteUrl": site_url, "email": email,"friendly_link":friendly_link})


def page_similar(id):
    similarlist = []
    sidlist = Page.objects.filter(typeid=id).order_by("?")
    type = Type.objects.get(id=id).type
    i = 0
    for s in sidlist:
        if i < 20:
            stitle = s.title
            pid = s.id
            tid = s.typeid
            firstimg = s.firstimg
            sendtime = s.sendtime
            hot = s.hot
            if pid != id:
                similarlist.append(
                    {"stitle": stitle, "tid": tid, "pid": pid, "firstimg": firstimg, "sendtime": sendtime, "hot": hot,
                     "type": type, "type_id": tid
                     })
                i += 1
    return similarlist


def search(request):
    if "s" in request.GET:
        imgs = []
        typedict, typelist = type_list()
        context = request.GET['s']
        pagelist = Page.objects.filter(title__contains=context).order_by("-id")
        for pid in pagelist:
            title = pid.title
            firstimg = pid.firstimg
            id = pid.id
            hot = pid.hot
            type_id = pid.typeid
            sendtime = pid.sendtime
            imgs.append({"pid": id, "firstimg": firstimg, "title": title, "sendtime": sendtime, "hot": hot,
                         "type": typedict[type_id], "type_id": type_id})
        return render(request, 'index.html',
                      {"data": imgs, "typelist": typelist, "siteName": site_name, "keyWord": key_word,
                       "description": description, "siteUrl": site_url, "email": email,"friendly_link":friendly_link})


def HotTag(request):
    tag_sql = Tag.objects.all().order_by("?")
    tag_dict = {}
    tag_id_list = []
    page_sql = Page.objects.all()
    page_dict = {}
    return_list = []
    typedict, typelist = type_list()
    for alltag in tag_sql:
        tag_dict.update({str(alltag.id).strip(): alltag.tag})
    for page in page_sql:
        title = page.title
        pid = page.id
        tag_id = page.tagid.replace("[", "").replace("]", "").split(",")
        for t in tag_id:
            if str(t).strip() == '':
                pass
            else:
                if str(t).strip() not in tag_id_list:
                    page_dict.update({str(t).strip(): 1})
                    tag_id_list.append(str(t).strip())
                else:
                    view = page_dict[str(t).strip()]
                    page_dict.update({str(t).strip(): view + 1})

    page_dict_sort = sorted(page_dict.items(), key=lambda d: d[1], reverse=True)
    for i in page_dict_sort:
        if page_dict[str(i[0])] > 20:
            return_list.append(
                {"tid": i[0], "tag": tag_dict[str(i[0]).strip()], "viwe": page_dict[str(i[0].strip())]}
            )
    return render(request, 'tag.html',
                  {"data": return_list, "typelist": typelist, "keyword": return_list[0:10], "siteName": site_name,
                   "keyWord": key_word, "description": description, "siteUrl": site_url, "email": email,"friendly_link":friendly_link})


def SortBy(request, method):
    if request.method == "GET":
        if method == "new":
            page_list = Page.objects.all().order_by("-id")[:100]
        else:
            page_list = Page.objects.all().order_by("-hot")[:100]
        imgs = []
        type_dict, typelist = type_list()
        for pid in page_list:
            title = pid.title
            firstimg = pid.firstimg
            id = pid.id
            hot = pid.hot
            type_id = pid.typeid
            sendtime = pid.sendtime
            imgs.append({"pid": id, "firstimg": firstimg, "title": title, "sendtime": sendtime, "hot": hot,
                         "type": type_dict[type_id], "type_id": type_id})

        return render(request, 'sort.html',
                      {"data": imgs, "typelist": typelist, "method": method, "siteName": site_name, "keyWord": key_word,
                       "description": description, "siteUrl": site_url, "email": email,"friendly_link":friendly_link})


def getVideo(request):
    count = Video.objects.count()
    video_info = ''
    while True:
        vid = random.randint(1, count)
        try:
            video_info = Video.objects.get(id=vid)
            break
        except:
            continue
    url = video_info.url
    user_id = video_info.user_id
    source = video_info.source
    return HttpResponse(json.dumps({"url": url, "user_id": user_id, "source": source}))


def mVideo(request):
    if request.method == "GET":
        count = Video.objects.count()
        video_info = ''
        while True:
            vid = random.randint(1, count)
            try:
                video_info = Video.objects.get(id=vid)
                break
            except:
                continue
        url = "https:"+video_info.url
        return render(request, 'mVideo.html', {
            "url": url,
            "user_id": video_info.user_id,
            "date_time": video_info.date_time,
            "v_name": video_info.v_name,
            "source": video_info.source, "siteName": site_name, "keyWord": key_word, "description": description,
            "siteUrl": site_url, "email": email,"friendly_link":friendly_link})


def pVideo(request):
    if request.method == "GET":
        typedict, typelist = type_list()
        count = Video.objects.count()
        video_info = ''
        while True:
            try:
                vid = random.randint(1, count)
            except:
                break
            try:
                video_info = Video.objects.get(id=vid)
                break
            except:
                continue
        url="https:"+video_info.url
        return render(request, 'video.html', {
            "url": url,
            "user_id": video_info.user_id,
            "date_time": video_info.date_time,
            "v_name": video_info.v_name,
            "source": video_info.source,
            "typelist": typelist, "siteName": site_name, "keyWord": key_word, "description": description,
            "siteUrl": site_url, "email": email,"friendly_link":friendly_link})


def type_list():
    typelist = []
    type_list = Type.objects.all().order_by("id")
    type_dict = {}
    for type_arr in type_list:
        type = type_arr.type
        type_id = type_arr.id
        typelist.append({"type": type, "type_id": str(type_id)})
        type_dict.update({type_id: type})
    return type_dict, typelist
