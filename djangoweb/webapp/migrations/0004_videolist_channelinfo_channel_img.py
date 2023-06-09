# Generated by Django 4.1.7 on 2023-04-09 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0003_remove_channelinfo_view_channelinfo_views'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_title', models.CharField(default='', max_length=1000, null=True)),
                ('video_category_id', models.IntegerField(default=0, null=True)),
                ('video_views', models.BigIntegerField(default=0, null=True)),
                ('video_likes', models.BigIntegerField(default=0, null=True)),
                ('video_comments', models.BigIntegerField(default=0, null=True)),
                ('video_date', models.CharField(default='', max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='channelinfo',
            name='channel_img',
            field=models.ImageField(default=0, null=True, upload_to=''),
        ),
    ]
