#!/usr/bin/env python
# coding: utf-8
from util.gsheet import gsheet_worker, leju_gsheet_worker
from util.crawler import lejuCrawler, _591_Crawler
import json

# Params
def web_config(name):
    config = {
        "leju":{
            "url_list_tab": "bot-list",
            "crawler": lejuCrawler(),
            "result_tab":"bot",
            "result_link_col": 6
        },
        "591":{
            "url_list_tab": "591-list",
            "crawler": _591_Crawler(),
            "result_tab":"591-bot",
            "result_link_col": 2
        }
    }
    config_data = config[name]

    return config_data


# Main function
def crawl(web_name):
    data = get_data(web_name)
    write_to_sheet(data,web_name)

def get_data(web_name):
    # config
    config_data = web_config(web_name)
    tab_name = config_data['url_list_tab']

    # get by sheet
    sht_worker = gsheet_worker()
    url_list = sht_worker.get_col_all_value(tab_name, 2)[1:]
    # print(url_list)
    
    # url_list = [
        # "https://www.leju.com.tw/page_search_result?oid=L37611690f7027", #麗軒珍寶
        # "https://www.leju.com.tw/page_search_result?oid=L93811608b8266", #世紀公園B
        # "https://www.leju.com.tw/page_search_result?oid=L08243922184a6", #公園大鎮
        # "https://www.leju.com.tw/page_search_result?oid=L5ab18401ccd6c",
        # "https://www.leju.com.tw/page_search_result?oid=L225192883ca30"
    # ]
    
    # to json file
    body = {'profile':[]}
    for url in url_list:
        try:
            crawler = config_data['crawler']
            data = crawler.fetch_data(url)
            data_json = crawler.get_data_json(data)
            data_json = json.dumps(data_json, ensure_ascii=False).encode('utf8')
            body['profile'].append(data_json.decode())
        except Exception as e:
            print(f"fetch fail:{url}")
            print(repr(e))

    print(body)
    return body


def write_to_sheet(data, web_name):
    config_data = web_config(web_name)
    result_tab_name = config_data['result_tab']
    result_link_col = config_data['result_link_col']
    sht_worker = gsheet_worker(web_name)
    sht_worker.write_profile_to_sheet(data,result_tab_name,result_link_col)

if __name__ == "__main__":
    crawl("leju")
    crawl("591")