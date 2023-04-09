from django.shortcuts import render, redirect
from .models import ChannelInfo

import os
import datetime
import re
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Create your views here.
def home(request):
    return render(request, 'cover/index.html')

def jumbotron(request):
    return render(request, 'jumbotron/index.html')

def dashboard(request):
    return render(request, 'dashboard/index.html')

def searchchannel(request):
    if request.method == 'POST':
        chnl = ChannelInfo()
        chnl.channel_name = request.POST['channel_name']
        # API 키를 입력하세요.
        API_KEY = 'AIzaSyCcis4wzheGUE8j9hRQ9xp43w7LREedD6M'

        # YouTube API 클라이언트를 빌드합니다.
        youtube = build('youtube', 'v3', developerKey=API_KEY)

        # search API 요청 보내기
        search_response = youtube.search().list(
            q = chnl.channel_name,
            type="channel",
            part="id",
            maxResults=50  # 한 번에 최대 50개의 결과 가져오기
        ).execute()

        chnl.channelID = search_response['items'][0]['id']['channelId']
        # search API 요청 보내기
        search_response = youtube.search().list(
            channelId=chnl.channelID,
            type="video",
            part="id",
            maxResults=50  # 한 번에 최대 50개의 결과 가져오기
        ).execute()
        
        # 채널 통계를 가져옵니다.
        channels_response = youtube.channels().list(
            part='snippet,contentDetails,statistics',
            id=chnl.channelID
        ).execute()
        # 채널 정보 가져오기
        chnl.channel_name = channels_response['items'][0]['snippet']['title']
        chnl.views = int(channels_response['items'][0]['statistics']['viewCount'])
        chnl.subscribers = int(
            channels_response['items'][0]['statistics']['subscriberCount'])
        chnl.hidden_sub = int(
            channels_response['items'][0]['statistics']['hiddenSubscriberCount'])
        chnl.videos = int(
            channels_response['items'][0]['statistics']['videoCount'])

        cpm = 17  # 1000 뷰당 예상 수익 ($2)
        chnl.revenue = (chnl.views / 1000) * cpm
        chnl.save()
    return render(request, 'dashboard/index.html', context={'chnl':chnl})

# def viewchannel(request):
#     if request.method =='GET':
#         return render(request, 'dashboard', {'channel'})



