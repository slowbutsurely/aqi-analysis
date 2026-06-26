from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class AirQuality(models.Model):
    city = models.CharField('城市',max_length=50)
    date = models.DateField('日期')
    airQuality = models.CharField('空气质量等级',max_length=50)
    AQI = models.IntegerField('AQI指数')
    rank = models.CharField('排名',max_length=50)
    PM = models.IntegerField('PM2.5')
    PM10 = models.IntegerField('PM10')
    So2 = models.IntegerField('So2')
    No2 = models.IntegerField('No2')
    Co = models.FloatField('Co')
    O3 = models.IntegerField('O3')
    year = models.IntegerField('年份')
    month = models.IntegerField('月份')

    class Meta:
      db_table = 'aqi_data'
      verbose_name = '空气质量数据'
      verbose_name_plural = '空气质量管理'
      ordering = ['-date']


class UserInfo(AbstractUser):
    avatar = models.CharField('头像URL', max_length=255, blank=True, default='', help_text='用户头像URL地址')

    created_at = models.DateTimeField('创建时间',auto_now_add=True)
    update_at = models.DateTimeField('更新时间',auto_now=True)

    class Meta:
        db_table = 'userinfo'
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        ordering = ['-created_at']