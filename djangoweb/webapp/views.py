from django.shortcuts import render, redirect
from .models import ChannelInfo

import os
import datetime
import re
import pandas as pd
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

# Create your views here.
def home(request):
    return render(request, 'cover/index.html')

def jumbotron(request):
    return render(request, 'jumbotron/index.html')

def dashboard(request):
    return render(request, 'dashboard/index.html')

def login(request):
    return render(request, "login/index.html")

def get_authenticated_service(request):
    credentials = Credentials.from_authorized_user_info(
        request.session['google_auth_token'])
    youtube_analytics_service = build('youtubeAnalytics', 'v2', credentials=credentials)
    return youtube_analytics_service

def get_channel_views(request):
    try:
        youtube_analytics_service = get_authenticated_service(request)
        channel_response = youtube_analytics_service.reports().query(
            ids='channel==CHANNEL_ID',
            metrics='views',
            start_date='2022-01-01',
            end_date='2022-01-31',
            dimensions='day'
        ).execute()

        return channel_response

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None
    
def searchchannel(request):
    if request.method == 'POST':
        chnl = ChannelInfo()
        chnl.channel_name = request.POST['channel_name']
        # API 키를 입력
        API_KEY1 = 'AIzaSyCcis4wzheGUE8j9hRQ9xp43w7LREedD6M'
        API_KEY2 = 'AIzaSyCybUkLvjkdaWFgdc7GtVdnn-vgal0g0mg'
        API_KEY3 = 'AIzaSyD1mS8iqeHOniuebnom3cFT_yVG1VI1odA'

        # YouTube API 클라이언트를 빌드
        youtube = build('youtube', 'v3', developerKey=API_KEY2)

        # search API 채널 이름으로 채널 id 가져오기
        search_response = youtube.search().list(
            q = chnl.channel_name,
            type="channel",
            part="id",
        ).execute()
        chnl.channelID = search_response['items'][0]['id']['channelId']

        # 채널 통계를 가져옵니다.
        channels_response = youtube.channels().list(
            part='snippet,contentDetails,statistics',
            id=chnl.channelID
        ).execute()
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

        # search API로 채널 비디오 리스트 가져오기
        search_response = youtube.search().list(
            channelId=chnl.channelID,
            type="video",
            part="id",
            maxResults=50  # 한 번에 최대 50개의 결과 가져오기
        ).execute()
        # 검색 결과에서 동영상 ID 추출
        video_ids = []
        for item in search_response["items"]:
            video_ids.append(item["id"]["videoId"])
        # 검색 결과가 50개 이상일 경우, 다음 페이지에 대한 요청을 보내어 결과를 가져옴
        while "nextPageToken" in search_response:
            search_response = youtube.search().list(
                channelId=chnl.channelID,
                type="video",
                part="id",
                maxResults=50,
                pageToken=search_response["nextPageToken"]
            ).execute()
            for item in search_response["items"]:
                video_ids.append(item["id"]["videoId"])
        #비디오 정보 가져오기
        title = []
        category_id = []
        views = []
        likes = []
        comments = []
        date = []
        for video_id in video_ids:
            video_response = youtube.videos().list(
                part='snippet, statistics', id=video_id).execute()
            if video_response['items'] == []:
                category_id.append('-')
                views.append('-')
                likes.append('-')
                comments.append('-')
                date.append('-')
            else:
                title.append(video_response['items'][0]['snippet']['title'])
                category_id.append(
                    video_response['items'][0]['snippet']['categoryId'])
                views.append(video_response['items'][0]['statistics']['viewCount'])
                likes.append(video_response['items'][0]['statistics']['likeCount'])
                comments.append(video_response['items']
                                [0]['statistics']['commentCount'])
                date.append(video_response['items'][0]['snippet']['publishedAt'])
        #json 활용하여 textField 형태로 리스트들 저장
        chnl.video_title = json.dumps(title)
        chnl.video_category_id = json.dumps(category_id)
        chnl.video_views = json.dumps(views)
        chnl.video_likes = json.dumps(likes)
        chnl.video_comments = json.dumps(comments)
        chnl.video_date = json.dumps(date)
        #pandas dataframe 생성후 html로 변경, render context 인자로 넘겨줌
        df = pd.DataFrame([title, category_id, views, likes, comments, date]).T
        df.columns = ['비디오 명', '카테고리 ID', '조회 수','좋아요 수', '댓글 수', '게시일']
        # df = df.sort_values(by=['조회 수','좋아요 수','댓글 수'], ascending=False)
        df_html = df.to_html(decimal=',', justify ='center', classes='table table-striped table-sm')
        chnl.save()
    return render(request, 'dashboard/index.html', context={'chnl':chnl, 'df':df_html})

# def viewchannel(request):
#     if request.method =='GET':
#         return render(request, 'dashboard', {'channel'})



