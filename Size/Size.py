"""
爬取并分析全国女性Size
时间：2020/3/26
"""

import requests
import re
import json
import pymysql


#爬取商品id
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'}
def get_id(key_word,wq):
    #jd_url='https://search.jd.com/Search?keyword=%E5%A5%B3%E6%80%A7%E5%86%85%E8%A1%A3&enc=utf-8&wq=%E5%A5%B3%E6%80%A7nei%27yi&pvid=fafd7af082734ae1a4a6cb674f98b2e4'
    jd_url = 'https://search.jd.com/Search'
    product_ids = []
    # 爬前3页的商品
    j = 51;
    for i in range(17,25,2):
        param = {'keyword': key_word, 'enc': 'utf-8', 'qrst':'1', 'rt':1, 'stop':1, 'vt':2, 'wq':wq, 'page':i, 's':j, 'click':0}
        response = requests.get(jd_url,params = param,headers=headers)
        # 商品id
        ids = re.findall('data-pid="(.*?)"', response.text,re.S)
        product_ids += ids
        if i!= 3:
            j = j+50+i-4;
        else:
            j+=50
    return product_ids

#爬取评价
def getSizes(ids):
    Sizes = []
    for id in ids:
        for i in range(0,8):
            url = 'https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId='+id+'&score=0&sortType=5&page='+str(i)+'&pageSize=10&isShadowSku=0&fold=1'
            response = requests.get(url)
            size = re.findall('"productSize":"(.*?)"',response.text)
            Sizes+=size
    return Sizes

#数据清洗（统一尺码）
def unified(str):
    if 'E' in str:
        return 'E'
    if 'D' in str:
        return 'D'
    if 'C' in str:
        return 'C'
    if 'B' in str:
        return 'B'
    if 'A' in str:
        return 'A'
    if 'XXL' in str:
        return 'E'
    if 'XL' in str:
        return 'D'
    if 'L' in str:
        return 'C'
    if 'M' in str:
        return 'B'
    if 'S' in str:
        return 'A'
    if '均码' in str:
        return 'B'
    if '大' in str:
        return 'C'
    if '小' in str:
        return 'A'

#运行
conn = pymysql.connect(host='localhost',user='root',password='123',database='size',port=3306)
cursor = conn.cursor()
ids = get_id("胸罩","xiong'zhao")
Sizes = getSizes(ids)
Sizes_flush = []
for size in Sizes:
    if unified(size) is not None:
        Sizes_flush+=unified(size)
        sql = "INSERT INTO jd_size(size) values('" + unified(size) + "');"
        cursor.execute(sql)
        conn.commit()
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root:123@127.0.0.2:3306/size?charset=utf8')
sizes = pd.read_sql('jd_size',con=engine)
data_gb = sizes[['size']].groupby(by='size')
#绘制饼图
import matplotlib.pyplot as plt
plt.figure(figsize=(6,6))
plt.pie(data_gb.size(),labels=['A','B','C','D','E'],explode=[0,0.05,0,0,0],autopct='%.2f %%')
plt.title("中国地区女性Size", fontproperties="SimHei")
plt.legend()
plt.show()
#绘制直方图
plt.bar(['A','B','C','D','E'], height=data_gb.size(), color="b", width=0.5)
conn.close()


#id url分析
#https://search.jd.com/Search?keyword=%E8%83%B8%E7%BD%A9&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=xiong%27zhao&page=3&s=51&click=0
#https://search.jd.com/Search?keyword=%E8%83%B8%E7%BD%A9&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=xiong%27zhao&page=5&s=101&click=0
#https://search.jd.com/Search?keyword=%E8%83%B8%E7%BD%A9&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=xiong%27zhao&page=7&s=153&click=0
#https://search.jd.com/Search?keyword=%E8%83%B8%E7%BD%A9&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=xiong%27zhao&page=9&s=205&click=0

#评价url分析
#https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=44814461608&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1
#https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=1766164741&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1

