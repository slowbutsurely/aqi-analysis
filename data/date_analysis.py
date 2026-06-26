from calendar import month

import pandas as pd
from django.db.models.expressions import result
from sqlalchemy import create_engine
from config import Config

# 创建数据库连接
engine = create_engine(
    f'mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}'
)

# 关键修改：把 engine=engine 改成 con=engine
df = pd.read_sql_table(table_name='aqi_data', con=engine)
df['date'] = pd.to_datetime(df['date'])

def part1():
    """城市平均AQI"""
    result = df.groupby('city')['AQI'].mean().reset_index(name='avg_AQI')
    print(result)
    result = result.sort_values('avg_AQI',ascending=False)
    result.to_sql('part1',engine,if_exists='replace',index=False)


def part2():
    "污染物平均值"
    result = df.groupby('city').agg({
        'PM': 'mean',
        'PM10': 'mean',
        'So2': 'mean',
        'No2': 'mean',
        'Co': 'mean',
        'O3': 'mean',
    }).reset_index()
    print(result)

    result.columns = ['city', 'avg_PM', 'avg_PM10', 'avg_So2', 'avg_No2', 'avg_Co', 'avg_O3']
    result.to_sql('part2', engine, if_exists='replace', index=False)


def part3():
    "年度空气质量分析"
    result = df.groupby(['city','year','month'])['AQI'].agg(['max','min']).reset_index()
    print(result)
    result.columns = ['city','year','month','max_AQI','min_AQI']
    result.to_sql('part3',engine,if_exists='replace',index=False)

def part4():
    "每月PM2。5 PM10平均值"
    result = df.groupby(['city', 'year', 'month']).agg({
        'PM':'mean',
        'PM10': 'mean'
    }).reset_index()
    print(result)
    result.columns = ['city', 'year', 'month', 'avg_PM', 'avg_PM10']
    result.to_sql('part4', engine, if_exists='replace', index=False)

def part5():
    "优质天气"
    df['greatAir'] = df['AQI'] < 50
    result = df.groupby(['city','year','month'])['greatAir'].sum().reset_index(name='greatAirCount')
    print(result)
    result.to_sql('part5',engine,if_exists='replace',index=False)

def part6():
    "So2,No2最大值"
    result = df.groupby('city').agg({
        'So2':'max',
        'No2':'max'
    }).reset_index()
    print(result)
    result.columns = ['city','max_So2','max_No2']
    result.to_sql('part6',engine,if_exists='replace',index=False)

def part7():
    '''Co浓度'''
    bins = [0,0.25,0.5,0.75,1.0,float('inf')]
    labels = ['0-0.25','0.25-0.5','0.5-0.75','0.75-1','1以上']
    df['Co_category'] = pd.cut(df['Co'],bins = bins, labels=labels)
    result = df.groupby('Co_category').size().reset_index(name='Co_count')
    print(result)
    result.to_sql('part7', engine, if_exists='replace', index=False)

def part8():
    "O3浓度"
    bins = [0,25,50,75,100,float('inf')]
    labels = ['0-25','25-50','50-70','75-100','100以上']
    df['O3_category'] = pd.cut(df['O3'],bins=bins,labels=labels)
    result = df.groupby('O3_category').size().reset_index(name='O3_count')
    print(result)
    result.to_sql('part8', engine, if_exists='replace', index=False)

def part9():
    "月度平均AQI"

    result = df.groupby(['city','year','month'])['AQI'].mean().reset_index(name='month_AQI')
    print(result)
    result.to_sql('part9', engine, if_exists='replace', index=False)

def part10():
    "日度AQI"
    df['day'] = df['date'].dt.day
    print(df['day'])
    data = df[['city','year','month','day','AQI','rank']]
    data.to_sql('part10', engine, if_exists='replace', index=False)



if __name__ == "__main__":
    part1()
    part2()
    part3()
    part4()
    part5()
    part6()
    part7()
    part8()
    part9()
    part10()

