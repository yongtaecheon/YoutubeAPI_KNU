from django.db import models
from django.contrib.auth.models import User
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
    
class CredentialsModel(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    credentials = models.TextField()
    
class AnalyticsInfo(models.Model):
    channel_id = models.TextField(max_length=1000)
    date = models.DateTimeField(null = False)
    views = models.BigIntegerField(null=True,default=0)
    comments = models.BigIntegerField(null=True,default=0)
    likes = models.BigIntegerField(null=True,default=0)
    dislikes = models.BigIntegerField(null=True,default=0)
    shares = models.BigIntegerField(null=True,default=0)
    subscribersGained = models.BigIntegerField(null=True,default=0)
    subscribersLost = models.BigIntegerField(null=True,default=0)
    estimatedMinutesWatched =  models.BigIntegerField(null=True,default=0)
    audienceWatchRatio = models.FloatField(null=True,default=0)
    relativeRetentionPerformance = models.FloatField(null=True,default=0)
    