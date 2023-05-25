from django.contrib import admin
from .models import ChannelInfo, TrendList, PopularChannelInfo, Category

# Register your models here.
admin.site.register(ChannelInfo)
admin.site.register(TrendList)
admin.site.register(PopularChannelInfo)
admin.site.register(Category)