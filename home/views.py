from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate,login
from home.models import UserInfo
from home.utils import util
from home.utils import query_mysql
from django.shortcuts import redirect
import os
import re
import time
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import json
from Get_QianFan import getQianFan

from .models import AirQuality
# Create your views here.

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        # 自动兼容 form-data 和 JSON 两种格式
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            else:
                username = request.POST.get('username')
                password = request.POST.get('password')
        except:
            username = request.POST.get('username')
            password = request.POST.get('password')

        user = authenticate(request,username = username,password = password)
        if user is not None:
            login(request,user)
            request.session['uid'] = user.id
            request.session['uname'] = user.username
            request.session['avatar'] = user.avatar

            return JsonResponse({"status":"200","msg":"登录成功"})
        else:
            return JsonResponse({"status":"500","msg":"用户名或密码错误"})
    else:
        return render(request,'login.html')


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        print(username, email, password, confirm_password)

        # 账号格式校验：6-10位，只能是数字或字母
        if not re.match(r'^[a-zA-Z0-9]{6,10}$', username):
            return JsonResponse({"status": "500", "msg": "账号必须是6-10位数字或字母"})

        # 密码格式校验：8-12位，只能是数字或字母
        if not re.match(r'^[a-zA-Z0-9]{8,12}$', password):
            return JsonResponse({"status": "500", "msg": "密码必须是8-12位数字或字母"})

        # 确认密码校验
        if password != confirm_password:
            return JsonResponse({"status": "500", "msg": "两次密码输入不一致"})

        if UserInfo.objects.filter(username=username).exists():
            return JsonResponse({"status": '500', "msg": "用户名已存在"})
        if UserInfo.objects.filter(email=email).exists():
            return JsonResponse({"status": '500', "msg": "邮箱已存在"})

        UserInfo.objects.create(username=username, email=email, password=make_password(password))

        return JsonResponse({"status": '200', "msg": "注册成功"})
    else:
        return render(request, 'register.html')


def index(request):
    yearList = util.getYearList()
    monthList = util.getMonthList()
    dayList = util.getDayList()
    cityList = util.getCityList()

    default_city = cityList[0] if cityList else None
    default_date = AirQuality.objects.latest('date').date if AirQuality.objects.exists() else None
    air_quality_data = None
    if default_city and default_date:
        air_quality_data = AirQuality.objects.filter(
            city=default_city,
            date=default_date
        ).first()

    sql = 'select * from part1'
    res = query_mysql.query(sql)
    name_list1 = [i[0] for i in res]
    value_list1 = [i[1] for i in res]

    sql2 = f"select * from part2 where city = '{default_city}'"
    city_analysis_data = query_mysql.query(sql2)
    if city_analysis_data:
        city_analysis_data = {
            'avg_PM': city_analysis_data[0][1],
            'avg_PM10': city_analysis_data[0][2],
            'avg_So2': city_analysis_data[0][3],
            'avg_No2': city_analysis_data[0][4],
            'avg_Co': city_analysis_data[0][5],
            'avg_03': city_analysis_data[0][6]
        }

    content = {
        'yearList' : yearList,
        'monthList' : monthList,
        'dayList' : dayList,
        'cityList' : cityList,
        'default_city' : default_city,
        'default_date' : default_date,
        'air_quality_data':air_quality_data,
        'name_list1':name_list1,
        'value_list1':value_list1,
        'city_analysis_data':city_analysis_data
    }
    return render(request,'index.html',content)

#查询空气信息
def get_air_quality(request):
    city = request.GET.get('city')
    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    print(city,year,month,day)

    try:
        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        air_quality = AirQuality.objects.filter(
            city=city,
            date=date_str
        ).first()
        if air_quality:
            data = {
                'status': '200',
                'data': {
                    'airQuality': air_quality.airQuality,
                    'AQI': air_quality.AQI,
                    'PM': air_quality.PM,
                    'PM10': air_quality.PM10,
                    'So2': air_quality.So2,
                    'No2': air_quality.No2,
                    'Co': air_quality.Co,
                    'O3': air_quality.O3,
                }
            }
        else:
            data = {'status': '500', 'msg': '未找到数据'}
    except Exception as e:
        data = {'status': '500', 'msg': str(e)}

    return JsonResponse(data)

def get_city_analysis(request):
    city = request.GET.get('city')
    sql2 = f"select * from part2 where city = '{city}'"
    city_analysis_data = query_mysql.query(sql2)
    if city_analysis_data:
        data = {
            'status': '200',
            'data': {
                'avg_PM': city_analysis_data[0][1],
                'avg_PM10': city_analysis_data[0][2],
                'avg_So2': city_analysis_data[0][3],
                'avg_No2': city_analysis_data[0][4],
                'avg_Co': city_analysis_data[0][5],
                'avg_O3': city_analysis_data[0][6],
            }
        }
        return JsonResponse(data)
    else:
        data = {'status':'500','msg':'未获取数据'}
        return JsonResponse(data)

def changeInfo(request):
    if not request.session.get('uid'):
        return redirect('home:login')

    try:
        user = UserInfo.objects.get(id=request.session.get('uid'))
    except UserInfo.DoesNotExist:
        return redirect('home:login')
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)

        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']

            fs = FileSystemStorage()

            timestamp = int(time.time())
            file_name = f'avatar/user_{user.id}_{timestamp}'

            if user.avatar:
                old_path = os.path.join(settings.MEDIA_ROOT, user.avatar)
                if os.path.exists(old_path):
                    os.remove(old_path)

            saved_path = fs.save(file_name, avatar)
            user.avatar = saved_path
            request.session['avatar'] = saved_path

        user.save()
        messages.success(request,'个人信息更新成功')
        return redirect('home:index')
    content = {
        'user': user
    }

    return render(request,'changeInfo.html',content)


def data_list(request):
    # 获取搜索参数
    search_city = request.GET.get('city','')
    search_year = request.GET.get('year','')
    search_airQuality = request.GET.get('airQuality','')  # 修正：原来是拼写错误 irquality

    # 查询所有数据
    data = AirQuality.objects.all()

    # 按照条件进行过滤
    if search_city:
        data = data.filter(city__icontains=search_city)

    if search_year:
        data = data.filter(year=search_year)

    if search_airQuality:
        data = data.filter(airQuality__icontains=search_airQuality)

    # 分页处理
    paginator = Paginator(data, 10)  # 每页显示10条数据
    page_num = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_num)
    except PageNotAnInteger:
        # 如果page不是整数，默认第一页
        page_obj = paginator.get_page(1)
    except EmptyPage:
        # 如果page超出范围，返回最后一页
        page_obj = paginator.get_page(paginator.num_pages)

    # 构造上下文
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        # 保留搜索参数，用于分页时保留搜索条件
        'search_city': search_city,
        'search_year': search_year,
        'search_airQuality': search_airQuality,
    }

    return render(request, 'data_list.html', context)


def part1(request):
    cityList = util.getCityList()
    yearList = util.getYearList()

    default_city = cityList[0] if cityList else ''
    default_year = yearList[0] if yearList else ''
    select_city = request.POST.get('city', default_city)
    select_year = request.POST.get('year', default_year)

    def fetch_data(table, city, year):
        sql = f"select * from {table} where city='{city}' and year={year}"
        res = query_mysql.query(sql)
        return (
            [row[2] for row in res],
            [row[3] for row in res],
            [row[4] for row in res],
        )

    month_list1, max_aqi1, min_aqi1 = fetch_data('part3', select_city, select_year)
    month_list2, avg_PM, avg_PM10 = fetch_data('part4', select_city, select_year)

    context = {
        'cityList': cityList,
        'yearList': yearList,
        'month_list1': month_list1,
        'max_aqi1': max_aqi1,
        'min_aqi1': min_aqi1,
        'month_list2': month_list2,
        'avg_PM': avg_PM,
        'avg_PM10': avg_PM10,
        'select_city': select_city,
        'select_year': int(select_year,)
    }
    return render(request, 'part1.html', context)

def part2(request):
    cityList = util.getCityList()
    yearList = util.getYearList()
    monthList = util.getMonthList()

    default_city = cityList[0] if cityList else ''
    default_year = yearList[0] if yearList else ''
    default_month = monthList[0] if monthList else ''

    select_city = request.POST.get('city', default_city)
    select_year = request.POST.get('year', default_year)
    select_month = request.POST.get('month', default_month)

    sql1 = f"select * from part10 where city='{select_city}' and year={select_year} and month={select_month}"
    res = query_mysql.query(sql1)

    day_list = [i[3] for i in res]
    aqi_list = [i[4] for i in res]
    rank_list = [i[5] for i in res]

    sql2 = f"select * from part5 where city='{select_city}' and year={select_year} and month={select_month}"
    res2 = query_mysql.query(sql2)

    result = []
    for i in res2:
        result.append({'value': i[3], 'name': i[2]})

    context = {
        'cityList': cityList,
        'yearList': yearList,
        'monthList': monthList,
        'select_city': select_city,
        'select_year': int(select_year),
        'select_month': int(select_month),
        'day_list': day_list,
        'aqi_list': aqi_list,
        'rank_list': rank_list,
        'result': result,
    }
    return render(request, 'part2.html', context)

def part3(request):
    sql1 = 'select * from part6'
    res1 = query_mysql.query(sql1)

    name_list1 = [i[0] for i in res1]
    maxSo2_list1 = [i[1] for i in res1]
    maxNo2_list1 = [i[2] for i in res1]

    sql2 = 'select * from part7'
    res2 = query_mysql.query(sql2)
    result1 = [{"value": i[1], "name": i[0]} for i in res2]

    sql3 = 'select * from part8'
    res3 = query_mysql.query(sql3)
    result2 = [{"value": i[1], "name": i[0]} for i in res3]

    context = {
        'name_list1': name_list1,
        'maxSo2_list1': maxSo2_list1,
        'maxNo2_list1': maxNo2_list1,
        'result1': result1,
        'result2': result2,
    }
    return render(request, 'part3.html', context)

def part4(request):
    monthList = util.getMonthList()
    yearList = util.getYearList()

    default_month = monthList[0] if monthList else ''
    default_year = yearList[0] if yearList else ''

    select_month = request.POST.get('month', default_month)
    select_year = request.POST.get('year', default_year)

    sql = f'select * from part9 where year={select_year} and month={select_month}'
    res = query_mysql.query(sql)
    result = [{"name": i[0], "value": round(i[3], 0)} for i in res]

    context = {
        'select_month': int(select_month),
        'select_year': int(select_year),
        'monthList': monthList,
        'yearList': yearList,
        'result': result,
    }
    return render(request, 'part4.html', context)

from predict import predict

def forecast(request):
    if request.method == 'POST':
        pm25 = float(request.POST.get('pm25'))
        So2 = float(request.POST.get('So2'))
        No2 = float(request.POST.get('No2'))
        season = request.POST.get('season')
        PM10 = float(request.POST.get('PM10'))
        Co = float(request.POST.get('Co'))
        print(pm25, So2, No2, season, PM10, Co)
        result = predict(pm25, PM10, So2, No2, Co, season)

        return JsonResponse({'status': '200', 'result': result})
    else:
        return render(request, 'forecast.html')


from home.utils.web_spider import spider
from pypinyin import lazy_pinyin
from datetime import datetime


def get_qianfan(request):
    if request.method == 'POST':
        # 接收前端选择的城市
        city = request.POST.get('city')

        city_pinyin = ''.join(lazy_pinyin(city)).translate(str.maketrans('', '', '-'))
        # 获取当前年月
        today = datetime.today()
        year, month = today.year, today.month
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1

        try:
            # 调用爬虫获取空气质量数据
            air_quality_data = spider(city_pinyin, city, year, month)

            # 将数据转为JSON字符串，传给AI
            data_str = json.dumps(air_quality_data, ensure_ascii=False)

            # 调用千帆AI分析
            ai_response = getQianFan(data_str)

            # 返回页面，传递城市列表、AI结果、选中的城市
            return render(request, 'get_qianfan.html', {
                'cityList': util.getCityList(),
                'ai_response': ai_response['response'],
                'select_city': city
            })

        except Exception as e:
            # 爬虫或AI调用失败，只返回城市列表
            print(f"错误：{e}")
            return render(request, 'get_qianfan.html', {
                'cityList': util.getCityList()
            })

    else:
        # GET请求，只显示城市列表
        return render(request, 'get_qianfan.html', {
            'cityList': util.getCityList()
        })