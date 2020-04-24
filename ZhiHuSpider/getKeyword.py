# -*- coding:UTF-8 -*-

import random
import re
import sys
import time

import requests
import pymysql
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
import pandas as pd

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
}

BASE_URL = "https://www.zhihu.com"
TOPIC_API = "/api/v4/topics/{topic_id}/feeds/timeline_activity"
QUESTION_API = "/question/{qid}"

ANSWER_API = "/api/v4/questions/{qid}/answers?include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action," \
             "annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings," \
             "comment_permission,created_time,updated_time,review_info,relevant_info,question.detail,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp," \
             "is_labeled,is_recognized;data[].mark_infos[].url;data[].author.follower_count,badge[].topics&limit=5&offset=0&platform=desktop&sort_by=default"
ANSWER_URL = "/answer/{aid}"


def get_html(i_url):
    try:
        response = requests.get(i_url, headers=headers)
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


def get_answer_info(qid, keyword):
    adf = pd.DataFrame({'content': [], 'url': []})
    aapi = BASE_URL + ANSWER_API.format(qid=qid)
    is_end = False
    next_url = aapi

    while not is_end:
        json = get_json(next_url)
        is_end = json['paging']['is_end']
        # print(next_url)
        answers = json['data']
        for answer in answers:
            content_html = answer['content']
            content = BeautifulSoup(content_html, 'html5lib').get_text()
            if keyword in content:
                aid = answer['id']
                aurl = BASE_URL + QUESTION_API.format(qid=qid) + ANSWER_URL.format(aid=aid)
                adf.loc[adf.shape[0]] = {'content': content, 'url': aurl}
                print(aurl)
        next_url = json['paging']['next']
    return adf


def get_qids(tid):
    qids = []
    t_url = BASE_URL + TOPIC_API.format(topic_id=tid)
    is_end = False
    next_url = t_url

    while not is_end:
        json = get_json(next_url)
        is_end = json['paging']['is_end']
        # print(next_url)
        questions = json['data']
        for question in questions:
            item = question['target']
            if 'question' in item:
                question_id = question['target']['question']['id']
                qids.append(question_id)
        next_url = json['paging']['next']
    return set(qids)


def collect_info(ids, word, outfile):
    df = pd.DataFrame({'content': [], 'url': []})
    for qid in ids:
        ainfo = get_answer_info(qid, word)
        df = pd.concat([df, ainfo], ignore_index=True)
    df.to_csv(outfile, index=False, encoding='utf_8_sig')
    return


question_ids = get_qids(sys.argv[1])
collect_info(question_ids, sys.argv[2], sys.argv[3])

