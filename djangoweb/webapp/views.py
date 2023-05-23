from django.shortcuts import render, redirect
from .models import ChannelInfo, PopularChannelInfo, TrendList

import os
import re
import pandas as pd
import json
from datetime import datetime, timedelta
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

Categoryid = {'1': "애니메이션", '2': "자동차", '10': "음악", '15': "동물", '17': "스포츠", '20': "게임",
              '22': "블로그", '23': "코미디", '24': "엔터테인먼트", '25': "뉴스_정치", '26': "스타일", '27': "교육", '28': "과학_기술", '30': "영화"}


def home(request):
    return render(request, 'cover/index.html')


def main(request):
    return render(request, 'jumbotron/index.html')


def dashboard(request):
    return render(request, 'dashboard/index.html')


# def searchchannel_old(request):
#     if request.method == 'POST':
#         chnl = ChannelInfo()
#         chnl.channel_name = request.POST['channel_name']

#         # YouTube API 클라이언트를 빌드
#         youtube = build('youtube', 'v3', developerKey=API_KEY2)

#         # search API 채널 이름으로 채널 id 가져오기
#         search_response = youtube.search().list(
#             q=chnl.channel_name,
#             type="channel",
#             part="id",
#         ).execute()
#         chnl.channelID = search_response['items'][0]['id']['channelId']

#         # 채널 통계를 가져옵니다.
#         channels_response = youtube.channels().list(
#             part='snippet,contentDetails,statistics',
#             id=chnl.channelID
#         ).execute()
#         chnl.channel_name = channels_response['items'][0]['snippet']['title']
#         chnl.views = int(
#             channels_response['items'][0]['statistics']['viewCount'])
#         chnl.subscribers = int(
#             channels_response['items'][0]['statistics']['subscriberCount'])
#         chnl.hidden_sub = int(
#             channels_response['items'][0]['statistics']['hiddenSubscriberCount'])
#         chnl.videos = int(
#             channels_response['items'][0]['statistics']['videoCount'])
#         chnl.channel_img = channels_response['items'][0]['snippet']['thumbnails']['high']['url']
#         cpm = 17  # 1000 뷰당 예상 수익 ($2)
#         chnl.revenue = round((chnl.views / 1000) * cpm)

#         # search API로 채널 비디오 리스트 가져오기
#         search_response = youtube.search().list(
#             channelId=chnl.channelID,
#             type="video",
#             part="id",
#             maxResults=50,  # 한 번에 최대 50개의 결과 가져오기
#             order="date"
#         ).execute()
#         # 검색 결과에서 동영상 ID 추출
#         video_ids = []
#         for item in search_response["items"]:
#             video_ids.append(item["id"]["videoId"])
#         # # 검색 결과가 50개 이상일 경우, 다음 페이지에 대한 요청을 보내어 결과를 가져옴
#         # while "nextPageToken" in search_response:
#         #     search_response = youtube.search().list(
#         #         channelId=chnl.channelID,
#         #         type="video",
#         #         part="id",
#         #         maxResults=50,
#         #         pageToken=search_response["nextPageToken"]
#         #     ).execute()
#         #     for item in search_response["items"]:
#         #         video_ids.append(item["id"]["videoId"])
#         # 비디오 정보 가져오기
#         video_title = []
#         video_url = []
#         video_category_id = []
#         video_views = []
#         video_likes = []
#         video_comments = []
#         video_date = []
#         video_embed = []
#         for video_id in video_ids:
#             video_response = youtube.videos().list(
#                 part='snippet, statistics, player', id=video_id).execute()
#             if video_response['items'] == []:
#                 video_category_id.append('-')
#                 video_views.append('-')
#                 video_likes.append('-')
#                 video_comments.append('-')
#                 video_date.append('-')
#             else:
#                 video_title.append(
#                     video_response['items'][0]['snippet']['title'])
#                 video_url.append(
#                     video_response['items'][0]['snippet']['thumbnails']['high']['url'])
#                 video_category_id.append(
#                     video_response['items'][0]['snippet']['categoryId'])
#                 video_views.append(
#                     video_response['items'][0]['statistics']['viewCount'])
#                 video_likes.append(
#                     video_response['items'][0]['statistics']['likeCount'])
#                 try:
#                     video_comments.append(video_response['items']
#                                           [0]['statistics']['commentCount'])
#                 except:
#                     video_comments.append('댓글중지')
#                 video_date.append(
#                     video_response['items'][0]['snippet']['publishedAt'])
#                 video_embed.append(
#                     video_response['items'][0]['player']['embedHtml'])
#         video_result = []
#         video_result.append(video_title)
#         video_result.append(video_url)
#         video_result.append(video_category_id)
#         video_result.append(video_views)
#         video_result.append(video_likes)
#         video_result.append(video_comments)
#         video_result.append(video_date)
#         # json 활용하여 textField 형태로 리스트들 저장
#         chnl.video_title = json.dumps(video_title)
#         chnl.video_url = json.dumps(video_url)
#         chnl.video_category_id = json.dumps(video_category_id)
#         chnl.video_views = json.dumps(video_views)
#         chnl.video_likes = json.dumps(video_likes)
#         chnl.video_comments = json.dumps(video_comments)
#         chnl.video_date = json.dumps(video_date)
#         # pandas dataframe 생성후 html로 변경, render context 인자로 넘겨줌
#         df = pd.DataFrame([video_title, video_url, video_category_id,
#                           video_views, video_likes, video_comments, video_date]).T
#         df.columns = ['video_title', 'video_url', 'video_category_id',
#                       'video_views', 'video_likes', 'video_comments', 'video_date']
#         # for url in video_url:
#         #     df.replace(url, '<img src='+url+'>', inplace=True)
#             # df.loc[url, video_url] = '<img src='+url+'>'
#         # df = df.sort_values(by=['조회 수','좋아요 수','댓글 수'], ascending=False)
#         df_html = df.to_html(decimal=',', justify='center',
#                              classes='table table-striped table-sm table-hover')
#         now = datetime.now()
#         chnl.LoadDate = now.strftime('%Y%m%d')
#         chnl.save()
#     return render(request, 'dashboard/index.html', context={'chnl': chnl, 'df_html': df_html, 'video_embed':video_embed ,'video_result':video_result, 'df':df})

def is_three_months_ago(time_str):
    # 현재 시간 가져오기
    current_time = datetime.now()

    # 주어진 시간 문자열을 datetime 객체로 변환
    time_format = "%Y-%m-%dT%H:%M:%S%fZ"
    given_time = datetime.strptime(time_str, time_format)

    # 현재 시간에서 3개월 전 시간 계산
    three_months_ago = current_time - timedelta(days=6*30)

    # 주어진 시간이 3개월 이전인지 판단
    if given_time > three_months_ago:
        return True
    else:
        return False


def time_to_seconds(time_str):
    # 'PT#M#S' 형식에서 분과 초를 추출하여 변환
    minutes = 0
    seconds = 0

    # 'M'과 'S' 사이에 있는 문자열 추출
    time_components = time_str.split('T')[1].split('S')[0]

    # 'M'을 기준으로 분 추출
    if 'M' in time_components:
        minutes = int(time_components.split('M')[0])

    # 'S'를 기준으로 초 추출
    if 'S' in time_components:
        seconds = int(time_components.split('S')[0])

    # 분을 초로 변환
    minutes_to_seconds = minutes * 60

    # 분과 초를 더하여 총 초로 반환
    total_seconds = minutes_to_seconds + seconds

    return total_seconds


def searchchannel(request):
    chnl = ChannelInfo()
    if request.method == 'POST':
        chnl.channel_name = request.POST['channel_name']

        # YouTube API 클라이언트를 빌드
        youtube = build('youtube', 'v3', developerKey=API_KEY5)

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
        maxResults=12,  # 한 번에 최대 12개의 결과 가져오기
        order="date"
    ).execute()
    # 검색 결과에서 동영상 ID 추출
    video_ids = []

    # 비디오 정보 가져오기
    video_result = []
    video_title = []
    video_views = []
    video_likes = []
    video_duration = []

    # 평점용 데이터 인덱스 뽑기
    # 평점 지표
    rating = [1, 1, 1, 1, 1]
    now = datetime.now()
    rated_video = []

    for item in search_response["items"]:
        video_ids.append(item["id"]["videoId"])
    button_clicked = request.POST.get('button_clicked', '')
    if button_clicked == 'LoadMore':
        # 검색 결과가 50개 이상일 경우, 다음 페이지에 대한 요청을 보내어 결과를 가져옴
        while "nextPageToken" in search_response:
            search_response = youtube.search().list(
                channelId=chnl.channelID,
                type="video",
                part="id",
                maxResults=9,
                pageToken=search_response["nextPageToken"]
            ).execute()
            for item in search_response["items"]:
                video_ids.append(item["id"]["videoId"])

    for video_id in video_ids:
        video_info = []
        video_response = youtube.videos().list(
            part='snippet, statistics, player, contentDetails', id=video_id).execute()
        video_info.append(
            video_response['items'][0]['snippet']['title'])  # 0 : title
        video_title.append(
            video_response['items'][0]['snippet']['title'])  # 0 : title

        video_info.append(
            video_response['items'][0]['snippet']['thumbnails']['high']['url'])  # 1: 썸네일

        video_info.append(
            Categoryid[video_response['items'][0]['snippet']['categoryId']])  # 2: 카테고리 번호

        video_info.append(
            video_response['items'][0]['statistics']['viewCount'])  # 3: 조회수
        video_views.append(
            video_response['items'][0]['statistics']['viewCount'])  # 3: 조회수

        video_info.append(
            video_response['items'][0]['statistics']['likeCount'])  # 4: 좋아요수
        video_likes.append(
            video_response['items'][0]['statistics']['likeCount'])  # 4: 좋아요수
        try:
            video_info.append(video_response['items']  # 5: 댓글 수
                              [0]['statistics']['commentCount'])
        except:
            video_info.append('댓글 중지 상태')
        video_info.append(  # 6: 게시일
            video_response['items'][0]['snippet']['publishedAt'])

        video_info.append(
            re.findall(r'www.youtube.com/embed/[\w\W\s\S]{11}', video_response['items'][0]['player']['embedHtml'])[0])

        video_duration.append(
            video_response['items'][0]['contentDetails']['duration']
        )
        # 시간연산
        publish_date_str = video_response['items'][0]['snippet']['publishedAt']
        if (is_three_months_ago(publish_date_str)):  # 조건 달것 3개월 이네
            rated_video.append(len(video_title)-1)
        video_result.append(video_info)

    # 채널 평점
    # 구독자 수 1번
    if (len(rated_video)):
        if (chnl.subscribers > 1000000):
            rating[0] = 5.0
        elif (chnl.subscribers > 100000):
            alpha = (chnl.subscribers-100000)/9900000
            rating[0] = 3*(1-alpha)+5*alpha
        else:
            alpha = (chnl.subscribers)/100000
            rating[0] = 1*(1-alpha)+3*alpha

        # 구독자 충성도 2번
        views_per_subs = 0
        like_per_subs = 0
        com_per_subs = 0
        vs_rate = 0
        ls_rate = 0
        cs_rate = 0
        for sample in rated_video:
            views_per_subs += int(video_views[sample])/chnl.subscribers
            like_per_subs += int(video_likes[sample])/chnl.subscribers
            # 100만 1700~ 5
            com_per_subs += int(video_likes[sample])/chnl.subscribers
            views_per_subs /= len(rated_video)
            like_per_subs /= len(rated_video)
            com_per_subs /= len(rated_video)

            # 구독자 대비 조회수
            if (views_per_subs > 1):
                vs_rate = 5
            else:
                alpha = views_per_subs
                vs_rate = 1*(1-alpha) + 5*(alpha)

            # 구독자 대비 좋아요  100만당 1만
            if (like_per_subs > 0.01):
                ls_rate = 5
            else:
                alpha = like_per_subs/0.01
                ls_rate = 1*(1-alpha) + 5*(alpha)

            # 구독자 대비 댓글 100만당 1700개
            if (com_per_subs > 0.0017):
                cs_rate = 5
            else:
                alpha = com_per_subs/0.0017
                cs_rate = 1*(1-alpha) + 5*(alpha)

            # 합산
            rating[1] = vs_rate * 0.6 + ls_rate*0.2 + cs_rate * 0.2

        # 영상 주기 3번
        # print("영상개수")
        # print(len(rated_video))
        # print("\n")
        if (len(rated_video) > 72):
            rating[3] = 5
        else:
            alpha = len(rated_video)/72
            rating[2] = 1*(1-alpha) + 5*alpha

        # 영상 평균 조회수 4번
        avg_view = 0
        for sample in rated_video:
            avg_view += int(video_views[sample])
        avg_view = avg_view/len(rated_video)
        if (avg_view > 500000):
            rating[4] = 5
        elif (avg_view >= 10000):
            alpha = avg_view/500000
            rating[3] = 1*(1-alpha) + 5*alpha
        else:
            rating[3] = 1

        # 영상 길이 5번
        avg_duration = 0
        for sample in rated_video:
            time_str = video_duration[sample]
            avg_duration += time_to_seconds(time_str)
        avg_duration /= len(rated_video)
        # print("평균 시간")
        # print(avg_duration)
        if (avg_duration > 1200):
            rating[4] = 5
        elif (avg_duration > 480):
            alpha = avg_duration/1200
            rating[4] = 1*(1-alpha) + 5*alpha
        else:
            rating[4] = 1
    # 채널평점 끝
    for i in range(5):
        rating[i] = round(rating[i], 2)
    print("<평점>\n", "구독자 수: ", rating[0], ", 구독자 충성도: ", rating[1],
          ", 영상 주기:", rating[2], ", 영상평균조회수: ", rating[3], ", 영상길이: ", rating[4])
    now = datetime.now()
    chnl.LoadDate = now.strftime('%Y%m%d')
    chnl.save()
    return render(request, 'dashboard/index.html', context={'chnl': chnl, 'video_result': video_result, 'rating': rating})


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

    for index in range((int(param)-1)*12, int(param)*12):
        tlList.append(all_videos[index])

    return render(request, 'trendList/showTrendList.html', context={'tl': tlList})


def objectcreation():
    object = PopularChannelInfo()
    return object


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
    youtube = build('youtube', 'v3', developerKey=API_KEY4)
    all_ranking_channel(youtube)
    set = PopularChannelInfo.objects.all()
    return


def savedata(request, param):
    request.session['param'] = param
    return redirect('showrankingchannel')


def showrankingchannel(request, param):
    date = datetime.now().strftime('%Y%m%d')
    categorys = []
    if 'indexcount' not in request.session:
        indexcount = 12
        request.session['indexcount'] = indexcount
    if request.method == 'POST':
        if 'category' in request.POST:
            categorys = request.POST.getlist("category")
        request.session['categorys'] = categorys
    else:
        categorys = request.session.get('categorys')
        request.session['categorys'] = categorys
    all_chnls = PopularChannelInfo.objects.filter(LoadDate=date)
    if categorys and '없음' not in categorys:
        all_chnls = all_chnls.filter(channel_category__in=categorys)
    pop_subsort_chnlist = all_chnls.order_by('ranking_subscribers')
    pop_viewsort_chnlist = all_chnls.order_by('ranking_viewcounters')
    pop_chnllist = []
    if request.method == 'POST':
        button_clicked = request.POST.get('button_clicked', '')
        request.session['button_clicked'] = button_clicked
    else:
        button_clicked = request.session.get('button_clicked')
        request.session['button_clicked'] = button_clicked

    if button_clicked == 'Subscriber':
        if len(pop_subsort_chnlist) % 10 != 0:
            indexcount = int(len(pop_subsort_chnlist)/10) + 1
        elif len(pop_subsort_chnlist) % 10 == 0:
            indexcount = int(len(pop_subsort_chnlist)/10)
        request.session['indexcount'] = indexcount
        for index in range((int(param)-1)*10, int(param)*10):
            if index < len(pop_subsort_chnlist):
                pop_chnllist.append(pop_subsort_chnlist[index])
    elif button_clicked == 'ViewCount':
        if len(pop_viewsort_chnlist) % 10 != 0:
            indexcount = int(len(pop_viewsort_chnlist)/10) + 1
        elif len(pop_viewsort_chnlist) % 10 == 0:
            indexcount = int(len(pop_viewsort_chnlist)/10)
        request.session['indexcount'] = indexcount
        for index in range((int(param)-1)*10, int(param)*10):
            if index < len(pop_viewsort_chnlist):
                pop_chnllist.append(pop_viewsort_chnlist[index])
    else:
        if len(all_chnls) % 10 != 0:
            indexcount = int(len(all_chnls)/10) + 1
        elif len(all_chnls) % 10 == 0:
            indexcount = int (len(all_chnls) / 10)
        for index in range((int(param)-1) * 10, int(param) * 10):
            if index<len(all_chnls):
                pop_chnllist.append(all_chnls[index])
                request.session['indexcount']=indexcount

    print(indexcount, request.session['indexcount'])

    return render(request, 'category/index.html', context={
        'pop_chnllist': pop_chnllist, 'indexcount': indexcount})


def updateDB(request):
    makeTrendList()
    make_rankingchannel()
    return render(request, 'update/index.html')
