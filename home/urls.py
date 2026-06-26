from django.urls import path
from home import views

app_name = 'home'

urlpatterns = [
    path('', views.user_login, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('index/', views.index, name='index'),
    path('get_air_quality/', views.get_air_quality, name='get_air_quality'),
    path('get_city_analysis/', views.get_city_analysis, name='get_city_analysis'),
    path('changeInfo/', views.changeInfo, name='changeInfo'),
    path('data_list/', views.data_list, name='data_list'),
    path('part1/', views.part1, name='part1'),
    path('part2/', views.part2, name='part2'),
    path('part3/', views.part3, name='part3'),
    path('part4/', views.part4, name='part4'),
    path('forecast/', views.forecast, name='forecast'),
    path('get_qianfan/', views.get_qianfan, name='get_qianfan'),
]