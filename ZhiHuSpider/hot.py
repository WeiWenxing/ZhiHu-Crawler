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
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    'cookie': 'zap=8d63121a-2726-499b-aa8e-3652e8f7adb4; d_c0="AHBZDWynwxCPTs3bjgVtOfRs9NWF55QxltM=|1580788024"; _ga=GA1.2.406319380.1583230363; z_c0=Mi4xejM1RERRQUFBQUFBY0ZrTmJLZkRFQmNBQUFCaEFsVk4zeGhuWHdEUlNIdkppYnZ4ZVZ2YWF5RW9UcFFPQnF6QmlB|1585040095|05c5f8862297393441c64d56699bfaa40fc1655a; q_c1=09f97b88991c48c693600c776dc1e549|1585554103000|1585554103000; tst=h; _xsrf=8vKBom6CLiKMnsK5mDzHHpQKPVQwGrgH; __utmv=51854390.100--|2=registration_date=20181123=1^3=entry_date=20181123=1; tshl=; __utma=51854390.406319380.1583230363.1587364424.1587535850.2; __utmz=51854390.1587535850.2.2.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/topic/19776749/hot; _gid=GA1.2.1681207338.1587693534; SESSIONID=GTuzd3yoQDrtyyJlgSU5YPc37Yv2MuDTSsi77ajPjxH; osd=U1kRAk9H2xwXtf1XWkeOTLiyBnhOAIpsaNTOKzATn2tmyYEdM-hsvkmw-FdaO1PvOUnfVu2BhqdNBDTebixWgkw=; JOID=UVAWC05F0hsetP9eXU6PTrG1D3lMCY1ladbHLDkSnWJhwIAfOu9lv0u5_15bOVroMEjdX-qIh6VEAz3fbCVRi00=; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1587706458,1587725111,1587726723,1587726884; KLBRSID=3d7feb8a094c905a519e532f6843365f|1587730535|1587720791; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1587730534'
}

BASE_URL = "https://www.zhihu.com"
TOPIC_API = "/api/v4/topics/{topic_id}/feeds/timeline_activity"
QUESTION_API = "/question/{question_id}"
KEYS = ['zvideo', 'science', 'digital', 'sport', 'fashion', 'focus', 'car', 'school', 'film', 'depth']


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


def get_question_info(q_url, df):
    html = get_html(q_url)
    doc = pq(html)
    # div = doc('.NumberBoard-itemInner:last strong').attr('title')
    question_url = q_url
    question_title = doc('.QuestionPage meta[itemprop=name]').attr('content')
    watch_count = doc('.NumberBoard-itemInner:last strong').attr('title')
    answer_count = doc('.QuestionPage meta[itemprop=answerCount]').attr('content')
    good = ''
    rate = 0
    if int(answer_count) != 0:
        rate = int(watch_count) // int(answer_count)
    if rate > 5000:
        good = str(rate)
    # print(str(question_title).encode('gbk', 'ignore').decode('gbk'))

    df.loc[df.shape[0]] = {'title': question_title, 'url': question_url, 'watch': watch_count, 'answer': answer_count, 'good': good}
    return


def get_urls(init_url):
    url_list = []
    is_end = False
    next_url = init_url

    while not is_end:
        # print(next_url)
        json = get_json(next_url)
        is_end = json['paging']['is_end']
        # print(is_end)
        print(next_url)
        questions = json['data']
        # print(str(questions).encode('gbk', 'ignore').decode('gbk'))
        for question in questions:
            item = question['target']
            if 'question' in item:
                question_id = question['target']['question']['id']
                ques_url = BASE_URL + QUESTION_API.format(question_id=question_id)
                url_list.append(ques_url)
                print(question_id)
        next_url = json['paging']['next']
    return set(url_list)


def collect_info(url_list, outfile):
    data_frame = pd.DataFrame(columns=['title', 'url', 'watch', 'answer', 'good'])
    for q_url in url_list:
        get_question_info(q_url, data_frame)
    result = data_frame.sort_values('good', ascending=False)
    result.to_csv(outfile, index=False, encoding='utf_8_sig')
    return


def hot_urls():
    keys = ['zvideo', 'science', 'digital', 'sport', 'fashion', 'focus', 'car', 'school', 'film', 'depth']
    hots = []
    for key in KEYS:
        hots.append(BASE_URL + "/hot?list=" + key)
    return keys


hot_url = BASE_URL + "/hot"
doc = pq(get_html(hot_url))
# print(doc('title'))

print(str(get_html(hot_url)).encode('gbk', 'ignore').decode('gbk'))
# print(doc('.NewGlobalWrite-topTitle').text())

