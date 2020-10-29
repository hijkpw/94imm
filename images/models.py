from django.db import models

# Create your models here.
class Page(models.Model):
    typeid = models.IntegerField()
    sendtime=models.DateField()
    title=models.CharField(max_length=200)
    firstimg=models.CharField(max_length=200)
    tagid=models.CharField(max_length=200)
    hot=models.IntegerField()

class Image(models.Model):
    pageid=models.IntegerField()
    imageurl=models.URLField()

class Type(models.Model):
    type=models.CharField(max_length=200)

class Tag(models.Model):
    tag = models.CharField(max_length=200)


class Video(models.Model):
    url = models.CharField(max_length=1024)
    user_id = models.CharField(max_length=15)
    date_time = models.CharField(max_length=30)
    v_name = models.CharField(max_length=1024)
    v_path = models.CharField(max_length=50)
    source = models.CharField(max_length=10)
