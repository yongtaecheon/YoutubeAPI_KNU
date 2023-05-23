from django.contrib import admin
from .models import ChannelInfo, CredentialsModel, AnalyticsInfo

# Register your models here.
admin.site.register(ChannelInfo)
admin.site.register(CredentialsModel)
admin.site.register(AnalyticsInfo)
