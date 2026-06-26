import os
import django
from home.utils.query_mysql import query

os.environ.setdefault('DJANGO_SETTINGS_MODULE','aqi_analysis.settings')
django.setup()

from django.db.models.functions import ExtractYear,ExtractMonth,ExtractDay

from home.models import AirQuality

def getYearList():
    "从date字段中提取年份列表"

    return list(AirQuality.objects
                .annotate(extracted_year=ExtractYear('date'))
                .values_list('extracted_year',flat=True)
                .distinct()
                .order_by('-extracted_year')
                )

def getMonthList():
    "从date字段中提取月份列表"

    return list(AirQuality.objects
                .annotate(extracted_month=ExtractMonth('date'))
                .values_list('extracted_month',flat=True)
                .distinct()
                .order_by('-extracted_month')
                )

def getDayList():
    "从date字段中提取日列表"

    return list(AirQuality.objects
                .annotate(extracted_day=ExtractDay('date'))
                .values_list('extracted_day',flat=True)
                .distinct()
                .order_by('-extracted_day')
                )

def getCityList():
    "获取城市列表"
    return list(set(AirQuality.objects
                .values_list('city',flat=True)
                ))

def getAirData():
    sql = 'select * from aqi_data'
    res =query(sql)

    return res


if __name__=="__main__":
   # print(getYearList())
    #print(getMonthlist())
    print(getAirData())