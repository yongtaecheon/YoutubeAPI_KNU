from django.db import models
# Create your models here.

class ChannelInfo(models.Model):
    LoadDate = models.CharField(null=True, default='', max_length=100)
    channelID = models.CharField(max_length=100)
    channel_name = models.CharField(null=True,default='',max_length=100)
    views = models.BigIntegerField(null=True,default=0)
    hidden_sub = models.IntegerField(null=True,default=0)
    subscribers = models.IntegerField(null=True,default=0)
    videos = models.IntegerField(null=True,default=0)
    revenue = models.FloatField(null=True,default=0)
    channel_img = models.CharField(null=True,default='',max_length=100) #as url

    video_title = models.TextField(null=True,default='',max_length=1000)
    video_url = models.TextField(null=True,default='',max_length=1000)
    video_category_id = models.TextField(null=True,default='',max_length=1000)
    video_views = models.TextField(null=True,default='',max_length=1000)
    video_likes = models.TextField(null=True,default='',max_length=1000)
    video_comments = models.TextField(null=True,default='',max_length=1000)
    video_date = models.TextField(null=True,default='',max_length=1000)


class TrendList(models.Model):
    LoadDate = models.CharField(null=True, default='', max_length=100)
    title = models.CharField(max_length=100)
    channel_title = models.CharField(null=True, default='', max_length=100)
    views = models.BigIntegerField(null=True, default=0)
    video_id = models.CharField(max_length=100)
    category_name = models.CharField(null=True, default='', max_length=100)
    url = models.CharField(max_length=200)
    
class PopularChannelInfo(models.Model):
    LoadDate = models.CharField(null=True, default='', max_length=100)
    channel_category = models.CharField(default='',max_length=100)
    channelID = models.CharField(default='',max_length=100)
    channel_name = models.CharField(null=True,default='',max_length=100)
    channel_views = models.BigIntegerField(null=True,default=0)
    subscribers = models.IntegerField(null=True,default=0)
    channel_thumbnail = models.CharField(default='',max_length=100)

class Category(models.Model):
    category_id = models.IntegerField(null=True,default=0)
    category_name = models.CharField(null=True, default='',max_length=100)
    ranking_subscribers = models.IntegerField(null=True,default=0)
    ranking_viewcounters = models.IntegerField(null=True,default=0)
    
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
    subscribersViewsRatio = models.FloatField(null=True,default=0)
    # audienceWatchRatio = models.FloatField(null=True,default=0)
    # relativeRetentionPerformance = models.FloatField(null=True,default=0)
    
