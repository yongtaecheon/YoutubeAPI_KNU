from django.db import models
# Create your models here.

class ChannelInfo(models.Model):
    channelID = models.CharField(max_length=100)
    channel_name = models.CharField(null=True,default='',max_length=100)
    views = models.BigIntegerField(null=True,default=0)
    hidden_sub = models.IntegerField(null=True,default=0)
    subscribers = models.IntegerField(null=True,default=0)
    videos = models.IntegerField(null=True,default=0)
    revenue = models.FloatField(null=True,default=0)
    channel_img = models.ImageField(null=True,default=0)

    video_title = models.TextField(null=True,default='',max_length=1000)
    video_category_id = models.TextField(null=True,default='',max_length=1000)
    video_views = models.TextField(null=True,default='',max_length=1000)
    video_likes = models.TextField(null=True,default='',max_length=1000)
    video_comments = models.TextField(null=True,default='',max_length=1000)
    video_date = models.TextField(null=True,default='',max_length=1000)