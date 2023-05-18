from django.shortcuts import render, redirect
from .models import ChannelInfo, PopularChannelInfo, TrendList

import os
import re
import pandas as pd
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.db.models import Q


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


def makeTrendList():
    # TrendList.objects.all().delete()
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
    return


def showTrendList(request, param):
    all_videos = TrendList.objects.all()

    tlList = []

    for index in range((int(param)-1)*10, int(param)*10-1):
        tlList.append(all_videos[index])

    return render(request, 'trendList/showTrendList.html', context={'tl': tlList})


def objectcreation():
    object = PopularChannelInfo()
    return object


Categoryid = {'1': "애니메이션", '2': "자동차", '10': "음악", '15': "동물", '17': "스포츠", '20': "게임",
              '22': "블로그", '23': "코미디", '24': "엔터테인먼트", '25': "뉴스_정치", '26': "스타일", '27': "교육", '28': "과학_기술", '30': "영화"}


def get_channelId_byplaylist(youtube, Categorylist):
    cid = []
    vid = []
    key = 0
    if Categorylist == str(10):
        id = "PL4fGSI1pDJn6jXS_Tv_N9B8Z0HTRVJE0m"
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=id,
        maxResults=50
    )
    response = request.execute()
    for item in response["items"]:
        videoid = item['snippet']['resourceId']["videoId"]
        if videoid not in vid:
            vid.append(videoid)

    while 'nextPageToken' in response and len(vid) < 100:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=id,
            maxResults=50,
            pageToken=response['nextPageToken']
        )
        response = request.execute()
        for item in response["items"]:
            videoid = item['snippet']['resourceId']["videoId"]
            if videoid not in vid:
                vid.append(videoid)
    for i in range(len(vid)):
        key = 0
        request = youtube.videos().list(
            part="snippet",
            id=vid[i]
        )
        response = request.execute()
        for j in range(len(cid)):
            if response['items'][0]['snippet']['channelId'] == cid[j]:
                key = 1
                break
        if key == 0:
            cid.append(response['items'][0]['snippet']['channelId'])
    return cid


def get_channelId_bynone(youtube):
    cid = []
    key = 0
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        maxResults=50,
        regionCode='KR'
    )
    response = request.execute()
    for item in response['items']:
        for cidcount in range(len(cid)):
            if cid[cidcount] == item['snippet']['channelId']:
                key = 1
                break
        if key == 0:
            cid.append(item['snippet']['channelId'])
        key = 0
    while 'nextPageToken' in response and len(cid) < 100:
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            maxResults=50,
            pageToken=response['nextPageToken'],
            regionCode='KR'
        )
        response = request.execute()
        key = 0
        for item in response['items']:
            for cidcount in range(len(cid)):
               if cid[cidcount] == item['snippet']['channelId']:
                   key = 1
                   break
            if key == 0:
                cid.append(item['snippet']['channelId'])
            if len(cid) >= 100:
                break
            key = 0
    return cid


def get_channelId_bycategory(youtube, Categoryid):
    cid = []
    key = 0
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        videoCategoryId=Categoryid,
        maxResults=50,
        regionCode='KR'
    )
    response = request.execute()
    for item in response['items']:
        for cidcount in range(len(cid)):
            if cid[cidcount] == item['snippet']['channelId']:
                key = 1
                break
        if key == 0:
            cid.append(item['snippet']['channelId'])
        key = 0
    while 'nextPageToken' in response and len(cid) < 100:
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            videoCategoryId=Categoryid,
            maxResults=50,
            pageToken=response['nextPageToken'],
            regionCode='KR'
        )
        response = request.execute()
        key = 0
        for item in response['items']:
            for cidcount in range(len(cid)):
               if cid[cidcount] == item['snippet']['channelId']:
                   key = 1
                   break
            if key == 0:
                cid.append(item['snippet']['channelId'])
            if len(cid) >= 100:
                break
            key = 0
    return cid


def get_channelinfo_bychannelId(youtube, cid, categoryid):
    popularchannel = []
    for ids in range(len(cid)):
        result = youtube.channels().list(
            part='snippet, statistics',
            id=cid[ids],
        ).execute()
        cname = result['items'][0]['snippet']['title']
        cthumbnail = result['items'][0]['snippet']['thumbnails']['high']['url']
        cviewCount = int(result['items'][0]['statistics']['viewCount'])
        if (~result['items'][0]['statistics']['hiddenSubscriberCount']):
            csubscriber = int(result['items'][0]
                              ['statistics']['subscriberCount'])
        else:
            csubscriber = int(result['items'][0]
                              ['statistics']['hiddenSubscriberCount'])
        category = Categoryid[categoryid]
        popularchannel.append(
            [category, cid[ids], cname, cviewCount, csubscriber, cthumbnail, -1, -1])
    return popularchannel


def sort_channel_byCount(channels, key):
    if key == 1:  # subscriber
        sorted_channels = sorted(channels, key=lambda x: -x[4])
        return sorted_channels
    elif key == 2:  # viewcounter
        sorted_channelv = sorted(channels, key=lambda x: -x[3])
        return sorted_channelv


def ranking_channel(categoryid, youtube):
    if categoryid == str(30):
        cid = get_channelId_bynone(youtube)
    else:
        cid = get_channelId_bycategory(youtube, categoryid)
    if categoryid == str(10):
        cid = cid + get_channelId_byplaylist(youtube, categoryid)
    channel = get_channelinfo_bychannelId(youtube, cid, categoryid)
    return channel


def print_channel(channel):
    date = datetime.now().strftime('%Y%m%d')
    for k in range(len(channel)):
        channelcategory = channel[k][0]
        channeliD = channel[k][1]
        channelname = channel[k][2]
        channelviews = channel[k][3]
        subscriber = channel[k][4]
        channelthumbnail = channel[k][5]
        rankingsubscribers = channel[k][6]
        rankingviewcounters = channel[k][7]
        PopularChannelInfo.objects.create(channel_category=channelcategory, channelID=channeliD, channel_name=channelname,
                                          channel_views=channelviews, subscribers=subscriber, channel_thumbnail=channelthumbnail,
                                          ranking_subscribers=rankingsubscribers, ranking_viewcounters=rankingviewcounters, LoadDate=date)


def not_multi(channel):
    multicheck = []
    mkey = 0
    for i in range(len(channel)):
        for j in range(len(multicheck)):
            if channel[i][1] == multicheck[j][1]:
                mkey = 1
                break
        if mkey == 0:
            multicheck.append(channel[i])
        mkey = 0
    return multicheck


def regenerate(channel):
    channel = sort_channel_byCount(channel, 1)
    channels = channel
    for i in range(len(channel)):
        channel[i][6] = i+1
    channel = sort_channel_byCount(channel, 2)
    channelv = channel
    for i in range(len(channel)):
        channel[i][7] = i+1
    # if len(channel)>100:
    #    for i in range(100,len(channels)):
    #        del channels[100]
    #    for i in range(100,len(channelv)):
    #        del channelv[100]
    channel = channels + channelv
    channel = not_multi(channel)
    return channel


def all_ranking_channel(youtube):
    allranking = []
    success_Category = [1, 2, 10, 15, 17, 20, 22, 23, 24, 25, 26, 28, 30]
    for i in range(len(success_Category)):
        allranking = allranking + \
            ranking_channel(str(success_Category[i]), youtube)
        allranking = not_multi(allranking)
    allranking = regenerate(allranking)
    print_channel(allranking)


def make_rankingchannel():
    youtube = build('youtube', 'v3', developerKey=API_KEY1)
    all_ranking_channel(youtube)
    set = PopularChannelInfo.objects.all()
    return


def showrankingchannel(request, param):
    date = datetime.now().strftime('%Y%m%d')
    categorys = []
    if request.method == 'POST':
        if 'category' in request.POST:
            categorys = request.POST.getlist("category")
            print(categorys)
    all_chnls = PopularChannelInfo.objects.filter(LoadDate=date)
    if categorys:
        all_chnls = all_chnls.filter(channel_category__in=categorys)
    pop_subsort_chnlist = all_chnls.order_by('ranking_subscribers')
    pop_viewsort_chnlist = all_chnls.order_by('ranking_viewcounters')
    pop_chnllist = []
    button_clicked = request.POST.get('button_clicked', '')
    if button_clicked == 'Subscriber':
        for index in range((int(param)-1)*10, int(param)*10-1):
            pop_chnllist.append(pop_subsort_chnlist[index])
    elif button_clicked == 'ViewCount':
        for index in range((int(param)-1)*10, int(param)*10-1):
            pop_chnllist.append(pop_viewsort_chnlist[index])
    else:
        for index in range((int(param)-1)*10, int(param)*10-1):
            pop_chnllist.append(all_chnls[index])
    return render(request, 'category/index.html', context={
        'pop_chnllist': pop_chnllist})


def updateDB(request):
    makeTrendList()
    make_rankingchannel()
    return render(request, 'update/index.html')
