"""djangoweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import webapp.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', webapp.views.home),
    path('main/', webapp.views.main),
    path('dashboard/', webapp.views.dashboard),
    path('searchchannel/', webapp.views.searchchannel, name='searchchannel'),
    path('accounts/', include('allauth.urls')),
    path('updateDB/', webapp.views.updateDB, name='updateDB'),
    path('showTrendList/<int:param>/',webapp.views.showTrendList, name='showTrendList'),
    # path('showCategoryPopChannel/<int:param>/',webapp.views.showCategoryPopChannel, name='showCategoryPopChannel'),
    path('showTrendData/', webapp.views.showTrendData, name ='showTrendData'),
    path('showData/<int:param1>/<str:param2>/', webapp.views.showData, name="showData"),
    path('showrankingchannel/<int:param>/',
         webapp.views.showrankingchannel, name='showrankingchannel'),
    path('api_request/', webapp.views.api_request, name = 'api_request'),
    path('oauth2callback/', webapp.views.oauth2callback, name = 'oauth2callback'),
    path('authorize/', webapp.views.authorize, name = 'authorize'),
    path('revoke/', webapp.views.revoke, name = 'revoke'),
    path('clear_credentials/', webapp.views.clear_credentials, name = 'clear_credentials'),
    path('print_index_table/', webapp.views.print_index_table, name = 'print_index_table'),
    ]
