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
}

BASE_URL = "https://www.zhihu.com"
TOPIC_API = "/api/v4/topics/{topic_id}/feeds/timeline_activity"
QUESTION_API = "/question/{question_id}"


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


url = BASE_URL + TOPIC_API.format(topic_id=sys.argv[1])
urls = get_urls(url)
print(urls)
collect_info(urls, sys.argv[2])

# data_frame = pd.DataFrame(columns=['title', 'url', 'watch', 'answer'])
# get_question_info(sys.argv[1], data_frame)
# print(html.encode('gbk', 'ignore').decode('gbk'))
# get_urls(html)
