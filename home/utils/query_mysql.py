import pymysql
from config import Config

def conn():
    con = pymysql.connect(host=Config.DB_HOST,user=Config.DB_USER,port=Config.DB_PORT,
                          password=Config.DB_PASSWORD,db=Config.DB_NAME)

    cur = con.cursor()
    return con,cur

def close():
    con,cur = conn()
    cur.close()
    con.close()

def query(sql):
    con,cur = conn()
    cur.execute(sql)
    res = cur.fetchall()
    close()

    return res

def insert(sql):
    con,cur = conn()
    cur.execute(sql)
    con.commit()
    close()