from django.shortcuts import render, redirect
from .models import ChannelInfo
from django.contrib.auth.decorators import login_required
from oauth2_provider.models import AccessToken, Application
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.client import OAuth2Credentials
from django.contrib.auth.models import User
from .models import CredentialsModel
from django.http import JsonResponse
from django.urls import reverse


import os
import datetime
import re
import requests
import pandas as pd
import json
import google.oauth2.credentials
import googleapiclient.discovery
import google_auth_oauthlib.flow

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CLIENT_SECRETS_FILE = "C:/Users/dnjsr/OneDrive/Desktop/project/YoutubeAPI_KNU/djangoweb/webapp/client_secret_2.json"
SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly']
API_SERVICE_NAME = 'youtubeAnalytics'
API_VERSION = 'v2'

def api_request(request):
  if 'credentials' not in request.session:
    return redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **request.session['credentials'])

  youtube = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  report = youtube.reports().query(ids='channel==MINE', startDate='2020-05-01', endDate='2020-06-30', metrics='views').execute()

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  request.session['credentials'] = credentials_to_dict(credentials)

  return JsonResponse(report)

def authorize(request):
      # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  request.session['state'] = state

  return redirect(authorization_url)


def oauth2callback(request):
      # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = request.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = request.build_absolute_uri()
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  request.session['credentials'] = credentials_to_dict(credentials)

  return redirect(reverse('api_request'))

def revoke(request):
  if 'credentials' not in request.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **request.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())

def clear_credentials(request):
  if 'credentials' in request.session:
    del request.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table(request):
      return render(request, "test/index.html")

# Create your views here.
def home(request):
    return render(request, 'cover/index.html')

def jumbotron(request):
    return render(request, 'jumbotron/index.html')

def dashboard(request):
    return render(request, 'dashboard/index.html')

def login(request):
    return render(request, "login/index.html")
    
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



