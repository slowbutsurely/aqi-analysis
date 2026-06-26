import random
import time

import requests
from bs4 import BeautifulSoup
import csv

class Spider:
    def __init__(self,cityName,realName):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Referer': 'https://www.tianqihoubao.com/',

        }
        self.cityName = cityName
        self.realName = realName

        self.f = open('data.csv','a',encoding='utf-8',newline='')
        self.writer = csv.DictWriter(self.f,fieldnames=[
            'Date',
            'AQI',
            'level',
            'rank',
            'pm25',
            'pm10',
            'No2',
            'So2',
            'Co',
            'O3',
            'city'
        ])

        # 用来存储要返回给 Django 的数据
        self.result_data = []


    def send_request(self,year,month):
        url = f'https://www.tianqihoubao.com/aqi/{self.cityName}-{year}{month:02d}.html'
        print(url)
        time.sleep(random.randint(1,5))
        resp = requests.get(url, headers=self.headers, timeout=10)
        print(resp.status_code)
        self.parse_resp(resp.text)

        # 关键：返回数据给 Django
        return self.result_data


    def parse_resp(self,resp):
        # 每次解析前清空
        self.result_data = []

        soup = BeautifulSoup(resp,'html.parser')
        tr = soup.find_all('tr')
        for d in tr[1:]:
            td = d.find_all('td')
            Date = td[0].get_text().strip()
            AQI = td[1].get_text().strip()
            level = td[2].get_text().strip()
            rank = td[3].get_text().strip()
            pm25 = td[4].get_text().strip()
            pm10 = td[5].get_text().strip()
            No2 = td[6].get_text().strip()
            So2 = td[7].get_text().strip()
            Co = td[8].get_text().strip()
            O3 = td[9].get_text().strip()
            print(Date, AQI, level, rank, pm25, pm10, No2, So2, Co, O3)
            data_dict = {
                'Date': Date,
                'AQI': AQI,
                'level': level,
                'rank': rank,
                'pm25': pm25,
                'pm10': pm10,
                'No2': No2,
                'So2': So2,
                'Co': Co,
                'O3': O3,
                'city': self.realName
            }
            self.save_data(data_dict)

            # 把数据加入列表，返回给 Django
            self.result_data.append(data_dict)

    def save_data(self,data_dict):
        #存储数据
        self.writer.writerow(data_dict)


    def run(self):
        #运行
        for year in range(2022,2027):
            for month in range(1,13):
                self.send_request(year,month)

if __name__ == "__main__":
    cityDict = {
        'beijing': '北京',
        'shanghai': '上海',
        'guangzhou': '广州',
        'shenzhen': '深圳',
        'hangzhou': '杭州',
        'nanjing': '南京',
        'chengdu': '成都',
        'wuhan': '武汉',
        'xian': '西安',
        'chongqing': '重庆'
    }
    for k,v in cityDict.items():
      spider = Spider(k,v)
      spider.run()

def spider(city_pinyin, real_name, year, month):
    s = Spider(city_pinyin, real_name)
    return s.send_request(year, month)