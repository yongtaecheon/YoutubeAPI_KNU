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
