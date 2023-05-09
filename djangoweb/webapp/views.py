from django.shortcuts import render, redirect
from .models import ChannelInfo, PopularChannelInfo, TrendList

import os
import re
import pandas as pd
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Create your views here.

# API 키를 입력
API_KEY1 = 'AIzaSyCcis4wzheGUE8j9hRQ9xp43w7LREedD6M'
API_KEY2 = 'AIzaSyCybUkLvjkdaWFgdc7GtVdnn-vgal0g0mg'
API_KEY3 = 'AIzaSyD1mS8iqeHOniuebnom3cFT_yVG1VI1odA'
API_KEY4 = 'AIzaSyA2-DRryTN0JYnI3P-letj_bl-sj9wpVKw'
API_KEY5 = 'AIzaSyB5nnPCXwDu3BWpCQxcrpa8mdJYqBZANjQ'

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

        # YouTube API 클라이언트를 빌드
        youtube = build('youtube', 'v3', developerKey=API_KEY1)


        # search API 채널 이름으로 채널 id 가져오기
        search_response = youtube.search().list(
            q=chnl.channel_name,
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
        chnl.views = int(
            channels_response['items'][0]['statistics']['viewCount'])
        chnl.subscribers = int(
            channels_response['items'][0]['statistics']['subscriberCount'])
        chnl.hidden_sub = int(
            channels_response['items'][0]['statistics']['hiddenSubscriberCount'])
        chnl.videos = int(
            channels_response['items'][0]['statistics']['videoCount'])
        chnl.channel_img = channels_response['items'][0]['snippet']['thumbnails']['high']['url']
        cpm = 17  # 1000 뷰당 예상 수익 ($2)
        chnl.revenue = round((chnl.views / 1000) * cpm)

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
        # # 검색 결과가 50개 이상일 경우, 다음 페이지에 대한 요청을 보내어 결과를 가져옴
        # while "nextPageToken" in search_response:
        #     search_response = youtube.search().list(
        #         channelId=chnl.channelID,
        #         type="video",
        #         part="id",
        #         maxResults=50,
        #         pageToken=search_response["nextPageToken"]
        #     ).execute()
        #     for item in search_response["items"]:
        #         video_ids.append(item["id"]["videoId"])
        # 비디오 정보 가져오기
        video_title = []
        video_url = []
        video_category_id = []
        video_views = []
        video_likes = []
        video_comments = []
        video_date = []
        for video_id in video_ids:
            video_response = youtube.videos().list(
                part='snippet, statistics', id=video_id).execute()
            if video_response['items'] == []:
                video_category_id.append('-')
                video_views.append('-')
                video_likes.append('-')
                video_comments.append('-')
                video_date.append('-')
            else:
                video_title.append(
                    video_response['items'][0]['snippet']['title'])
                video_url.append(
                    video_response['items'][0]['snippet']['thumbnails']['high']['url'])
                video_category_id.append(
                    video_response['items'][0]['snippet']['categoryId'])
                video_views.append(
                    video_response['items'][0]['statistics']['viewCount'])
                video_likes.append(
                    video_response['items'][0]['statistics']['likeCount'])
                try:
                    video_comments.append(video_response['items']
                                      [0]['statistics']['commentCount'])
                except:
                    video_comments.append('댓글중지')
                video_date.append(
                    video_response['items'][0]['snippet']['publishedAt'])
        # json 활용하여 textField 형태로 리스트들 저장
        chnl.video_title = json.dumps(video_title)
        chnl.video_url = json.dumps(video_url)
        chnl.video_category_id = json.dumps(video_category_id)
        chnl.video_views = json.dumps(video_views)
        chnl.video_likes = json.dumps(video_likes)
        chnl.video_comments = json.dumps(video_comments)
        chnl.video_date = json.dumps(video_date)
        # pandas dataframe 생성후 html로 변경, render context 인자로 넘겨줌
        df = pd.DataFrame([video_title, video_url, video_category_id,
                          video_views, video_likes, video_comments, video_date]).T
        df.columns = ['비디오 명', '비디오 썸네일 URL', '카테고리 ID',
                      '조회 수', '좋아요 수', '댓글 수', '게시일']
        for url in video_url:
            df.replace(url, '<img src='+url+'>', inplace=True)
            # df.loc[url, video_url] = '<img src='+url+'>'
        # df = df.sort_values(by=['조회 수','좋아요 수','댓글 수'], ascending=False)
        df_html = df.to_html(decimal=',', justify='center',
                             classes='table table-striped table-sm table-hover')
        now = datetime.now()
        chnl.LoadDate = now.strftime('%Y%m%d')
        chnl.save()
    return render(request, 'dashboard/index.html', context={'chnl': chnl, 'df': df_html})

def youtube_social_login(request):
    return render(request, 'login/index.html')


def makeTrendList(request):
    #TrendList.objects.all().delete()
    # API 인증 정보를 설정합니다.

    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    # YouTube API 클라이언트를 빌드합니다.
    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION, developerKey=API_KEY2)

    # 실시간 급상승 동영상 정보를 가져오는 API 요청을 생성합니다.
    req = youtube.videos().list(
        part='snippet,statistics',
        chart='mostPopular',
        regionCode='KR',
        maxResults=50
    )

    # API 요청을 실행하고 응답을 받아옵니다.
    response = req.execute()
    now = datetime.now()
        
    for index, item in enumerate(response['items']):
        tl = TrendList()
        tl.title = item['snippet']['title']
        tl.channel_title = item['snippet']['channelTitle']
        tl.views = item['statistics']['viewCount']
        tl.video_id = item['id']
        tl.url = f'https://www.youtube.com/watch?v={tl.video_id}'
        tl.LoadDate = now.strftime('%Y%m%d')
        tl.save()

    return render(request, 'trendList/index.html')


def showTrendList(request, param):
    all_videos = TrendList.objects.all()

    tlList = []

    for index in range((int(param)-1)*10, int(param)*10-1):
        tlList.append(all_videos[index])

    return render(request, 'trendList/showTrendList.html', context={'tl': tlList})


def objectcreation():
    object = PopularChannelInfo()
    return object


def categoryPopChannel(request):
    if request.method == 'POST':
        now = datetime.now()
        youtube = build('youtube', 'v3', developerKey=API_KEY3)
        pop_chnllist = []
        pop_chnl = PopularChannelInfo()

        categories = youtube.videoCategories().list(
            part='snippet', regionCode='KR').execute()
        for case in categories['items']:
            print("카테고리 : ", case['snippet']['title'])

        for category in categories['items']:

            category_id = category['id']
            category_name = category['snippet']['title']

            if (category['snippet']['assignable'] == False):
                continue
            try:
                search_response = youtube.videos().list(
                    chart='mostPopular',
                    part='snippet',
                    videoCategoryId=category_id,
                    maxResults=1,
                    regionCode='KR'
                ).execute()

            except HttpError as error:
                if (error.resp.status == 404):
                    continue
                else:
                    print("error occurred", error)

            print("카테고리", category_name)
            print(" ")
            for video in search_response['items']:
                channel_id = video['snippet']['channelId']
                channel_response = youtube.channels().list(
                    part='snippet,statistics',
                    id=channel_id
                ).execute()
                pop_chnllist.append(objectcreation())
                for channel in channel_response['items']:

                    channel_title = channel['snippet']['title']
                    channel_description = channel['snippet']['description']
                    channel_thumbnail = channel['snippet']['thumbnails']['high']['url']
                    channel_viewCount = channel['statistics']['viewCount']
                    if (~channel['statistics']['hiddenSubscriberCount']):
                        channel_subscribe = channel['statistics']['subscriberCount']
                        pop_chnllist[-1].subscribers = channel_subscribe
                    pop_chnllist[-1].channelID = channel_id
                    pop_chnllist[-1].channel_views = channel_viewCount
                    pop_chnllist[-1].channel_category = category_name
                    pop_chnllist[-1].channel_name = channel_title
                    pop_chnllist[-1].channel_thumbnail = channel_thumbnail
                    pop_chnllist[-1].LoadDate = now.strftime('%Y%m%d')
                    pop_chnllist[-1].save()

                    # pop_chnllist.append(pop_chnl)

                    print("     채널 이름:", pop_chnl.channel_name)
        # for pop_chnl_item in pop_chnllist:
        #    pop_chnl_item.save()

    return render(request, 'category/index.html', context={'pop_chnlist': pop_chnllist})

# def viewchannel(request):
#     if request.method =='GET':
#         return render(request, 'dashboard', {'channel'})
