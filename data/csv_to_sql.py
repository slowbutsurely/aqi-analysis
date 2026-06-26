import pandas as pd
import pymysql
from config import Config

class AirData:
    def __init__(self):
        # 数据库连接
        self.conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        # 读取CSV（无表头，匹配数据顺序）
        self.df = pd.read_csv('data.csv', header=None,
                              names=['date','AQI','airQuality','rank','PM','PM10','So2','No2','Co','O3','city'])
        self._preprocess_data()

    def _preprocess_data(self):
        '''数据预处理：去重、转换日期类型、清理缺失值'''
        self.df.drop_duplicates(inplace=True)
        # 关键：把date列强制转换为datetime类型（解决strftime报错）
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        self.df['year'] = self.df['date'].dt.year
        self.df['month'] = self.df['date'].dt.month
        # 清理转换失败的缺失值
        self.df.dropna(inplace=True)

    def save_to_mysql(self, table_name):
        with self.conn.cursor() as cursor:
            for index, row in self.df.iterrows():
                #
                insert_sql = f"""
                INSERT INTO {table_name}(city, date, airQuality, AQI, `rank`, PM, PM10, So2, No2, Co, O3, `year`, `month`)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                #
                params = (
                    row['city'],
                    row['date'].strftime('%Y-%m-%d'),  #
                    row['airQuality'],
                    row['AQI'],
                    row['rank'],
                    row['PM'],
                    row['PM10'],
                    row['So2'],
                    row['No2'],
                    row['Co'],
                    row['O3'],
                    row['year'],
                    row['month'],
                )
                cursor.execute(insert_sql, params)
        self.conn.commit()

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    air = AirData()
    air.save_to_mysql('aqi_data')
    air.close()