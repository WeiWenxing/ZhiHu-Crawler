# -*- coding:UTF-8 -*-

import random
import re
import sys
import time

import requests
import pymysql
from pyquery import PyQuery as pq
import pandas as pd

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    'cookie': 'BIDUPSID=D59FA1BEB7DF1F297413B0AA4FDEF128; PSTM=1580788382; BAIDUID=D59FA1BEB7DF1F296EEBC79E1EA36A50:FG=1; BD_UPN=12314753; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BD_HOME=1; delPer=0; BD_CK_SAM=1; PSINO=2; COOKIE_SESSION=5_0_8_3_0_7_1_2_7_3_2_0_0_0_0_0_0_0_1588043061%7C9%230_0_1588043061%7C1; ZD_ENTRY=google; BDRCVFR[feWj1Vr5u3D]=mk3SLVN4HKm; BDUSS=JlS2VxMFY1MXo5RVFTSEtGS29kWXBtcm54RE9ZaTdCVzl0WWNpUGs1d29kODllRVFBQUFBJCQAAAAAAAAAAAEAAAAZhLMHcGVhcmxkb3RleQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACjqp14o6qdeMD; H_PS_PSSID=31355_1440_31326_21100_31421_31342_30901_30823_31163_31472_31195; H_PS_645EC=7248MK8nZgz7xrSF%2FuF5Sb2YNExiMC0FezUdY9c%2FMiWchKuInOjL9q2lD%2B0',
}

KEY_URL = "https://www.baidu.com/s?wd=site%3Awww.zhihu.com%20question%20{key}"


def get_html(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # print(response.text.encode('gbk', 'ignore').decode('gbk'))
            return response.text
        else:
            print('请求网页源代码错误, 错误状态码：', response.status_code)
    except Exception as e:
        print(e)
        return None


def get_json(i_url):
    try:
        response = requests.get(i_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print('请求网页json错误, 错误状态码：', response.status_code)
    except Exception as e:
        print(e)
        time.sleep(60 + float(random.randint(1, 4000)) / 100)
        return get_json(i_url)


def read_excel(file_path):
    df = pd.read_excel(file_path)
    return df


def get_keys(data_frame):
    keys = data_frame['关键词'].unique()
    return keys


def get_key_result(keyword, df):
    url = KEY_URL.format(key=keyword)
    html = get_html(url)
    # print(print(html.encode('gbk', 'ignore').decode('gbk')))
    doc = pq(html)
    baidu = doc('.nums .nums_text').text()
    count = baidu.replace('百度为您找到相关结果约', '').replace('个', '').replace(',', '')
    df.loc[df.shape[0]] = {'key': keyword, 'count': count}
    return


def get_all_count(infile, outfile):
    data_frame = pd.DataFrame(columns=['key', 'count'])
    df_excel = read_excel(infile)
    all_keys = get_keys(df_excel)
    for key in all_keys:
        get_key_result(key, data_frame)
    result = data_frame.sort_values('count', ascending=True)
    result.to_csv(outfile, index=False, encoding='utf_8_sig')
    return


get_all_count("shop.xlsx", "keyword.csv")
# print(doc('title'))

# print(doc('.NewGlobalWrite-topTitle').text())

