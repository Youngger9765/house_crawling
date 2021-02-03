#!/usr/bin/env python
# coding: utf-8
from util.gsheet import gsheet_worker 
from util.crawler import lejuCrawler 
import json


def crawl(event, context):
    data = get_data()
    write_to_sheet(data)

def get_data():
    # crawl
    sht_worker = gsheet_worker()
    url_list = sht_worker.get_col_all_value("bot-list", 2)[1:]
    print(url_list)
    # url_list = [
    #     "https://www.leju.com.tw/page_search_result?oid=L37611690f7027", #麗軒珍寶
    #     "https://www.leju.com.tw/page_search_result?oid=L93811608b8266", #世紀公園B
    # ]
    body = {'profile':[]}
    for url in url_list:
        try:
            leju_crawler = lejuCrawler()
            data = leju_crawler.fetch_data(url)
            data_json = leju_crawler.get_data_json(data)
            data_json = json.dumps(data_json, ensure_ascii=False).encode('utf8')
            body['profile'].append(data_json.decode())
        except Exception as e:
            print(f"fetch fail:{url}")
            print(repr(e))
            


    print(body)
    return body


def write_to_sheet(data):
    sht_worker = gsheet_worker()
    sht_worker.write_profile_to_sheet(data)

if __name__ == "__main__":
    crawl("","")
