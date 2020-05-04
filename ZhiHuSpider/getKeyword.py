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
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
}

BASE_URL = "http://www.zhihu.com"
TOPIC_API = "/api/v4/topics/{topic_id}/feeds/timeline_activity"
QUESTION_API = "/question/{qid}"

ANSWER_API = "/api/v4/questions/{qid}/answers?include=data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action," \
             "annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings," \
             "comment_permission,created_time,updated_time,review_info,relevant_info,question.detail,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp," \
             "is_labeled,is_recognized;data[].mark_infos[].url;data[].author.follower_count,badge[].topics&limit=5&offset=0&platform=desktop&sort_by=default"
ANSWER_URL = "/answer/{aid}"
COMMENT_API = '/api/v4/answers/{aid}/comments?include=data%5B*%5D.author%2Ccollapsed' \
          '%2Creply_to_author%2Cdisliked%2Ccontent%2Cvoting%2Cvote_count%2Cis_parent_author%2Cis_author' \
          '%2Calgorithm_right&order=normal&limit=20&offset=0&status=open'


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
        print(response.status_code)
        if response.status_code == 200:
            return response.json()
        else:
            print('request json error, code:', response.status_code)
    except Exception as e:
        print(e)
        time.sleep(60 + float(random.randint(1, 4000)) / 100)
        return get_json(i_url)


def is_in(words, content):
    for word in words:
        if word in content:
            return True
    return False


def get_comment(qid, aid, keyword):
    cdf = pd.DataFrame({'content': [], 'url': [], 'q_url': []})
    capi = BASE_URL + COMMENT_API.format(aid=aid)
    is_end = False
    next_url = capi

    while not is_end:
        json = get_json(next_url)
        if not 'paging' in json:
            break
        if not 'is_end' in json['paging']:
            break
        is_end = json['paging']['is_end']
        # print(next_url)
        comments = json['data']
        i = 0
        for comment in comments:
            content_html = comment['content']
            content = BeautifulSoup(content_html, 'html5lib').get_text()
            if is_in(keyword, content):
                aurl = BASE_URL + QUESTION_API.format(qid=qid) + ANSWER_URL.format(aid=aid)
                qurl = re.search('&offset=\d+', next_url).group() + '&i=' + str(i)
                cdf.loc[cdf.shape[0]] = {'content': content, 'url': aurl, 'q_url': qurl}
                # print(aurl)
                print(aurl)
                print(qurl)
            i=i+1
            if i > 10:
                break
        next_url = json['paging']['next']
    return cdf


def get_answer(qid, keyword):
    adf = pd.DataFrame({'content': [], 'url': [], 'q_url': []})
    aapi = BASE_URL + ANSWER_API.format(qid=qid)
    is_end = False
    next_url = aapi

    while not is_end:
        json = get_json(next_url)
        is_end = json['paging']['is_end']
        # print(next_url)
        answers = json['data']
        for answer in answers:
            aid = answer['id']
            cdf = get_comment(qid, aid, keyword)
            cdf.to_csv(outfile, mode='a', header=False, index=False, encoding='utf_8_sig')
            adf = pd.concat([adf, cdf], ignore_index=True)
        next_url = json['paging']['next']
    return adf


def get_qids(tid):
    qids = []
    t_url = BASE_URL + TOPIC_API.format(topic_id=tid)
    is_end = False
    next_url = t_url

    while not is_end:
        print(next_url)
        json = get_json(next_url)

        is_end = json['paging']['is_end']
        questions = json['data']
        for question in questions:
            item = question['target']
            if 'question' in item:
                question_id = question['target']['question']['id']
                qids.append(question_id)
        next_url = json['paging']['next']
    return set(qids)


def collect_info(ids, outfile, word):
    df = pd.DataFrame({'content': [], 'url': [], 'q_url': []})
    df.to_csv(outfile, index=False, encoding='utf_8_sig')
    for qid in ids:
        ainfo = get_answer(qid, word)
        df = pd.concat([df, ainfo], ignore_index=True)
    # df.to_csv(outfile, index=False, encoding='utf_8_sig')
    return

outfile =  sys.argv[2]
question_ids = get_qids(sys.argv[1])
collect_info(question_ids, sys.argv[2], sys.argv[3:])

