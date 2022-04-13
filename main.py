#!/usr/bin/env python
# coding: utf-8
from util.gsheet_worker import GsheetWorker
from util.crawler import lejuCrawler, _591_Crawler, fb_Crawler
from util.crawler import fb_GoupCrawlerByRequests
from util.crawler import fb_private_Crawler
from util.crawler import fb_Crawler_by_facebook_scraper
from util.crawler import yt_CrawlerBySelenium
from util.crawler import yt_CrawlerByfeeds
from util.crawler import yt_CrawlerByScriptbarrel
from util.notification import LineWorker
import json


# Params
def web_config(name):
    config = {
        "leju":{
            "url_list_tab": "bot-list",
            "to_crawl_link_col": 2,
            "crawler": lejuCrawler(),
            "result_tab":"bot",
            "result_link_col": 6
        },
        "591":{
            "url_list_tab": "591-list",
            "to_crawl_link_col": 2,
            "crawler": _591_Crawler(),
            "result_tab":"591-bot",
            "result_link_col": 2
        },
        "fb": {
            "url_list_tab": "FB-list",
            "to_crawl_link_col": 2,
            "crawler": fb_Crawler(),
            "result_tab": "FB-bot",
            "result_link_col": 4
        },
        "fb-private": {
            "url_list_tab": "FB-private-list",
            "to_crawl_link_col": 2,
            "crawler": fb_private_Crawler(),
            "result_tab": "FB-private-bot",
            "result_link_col": 4
        },
        "fb_Crawler_by_facebook_scraper": {
        	"url_list_tab": "FB-list",
            "to_crawl_link_col": 2,
        	"crawler": fb_Crawler_by_facebook_scraper(),
        	"result_tab": "FB-bot",
        	"result_link_col": 4
        },
        "fb_GoupCrawlerByRequests": {
        	"url_list_tab": "FB-list",
            "to_crawl_link_col": 2,
        	"crawler": fb_GoupCrawlerByRequests(),
        	"result_tab": "FB-bot",
        	"result_link_col": 4
        },
        "yt_CrawlerBySelenium": {
            "url_list_tab": "YT-list",
            "to_crawl_link_col": 2,
            "crawler": yt_CrawlerBySelenium(),
            "result_tab": "YT-bot",
            "result_link_col": 4
        },
        "yt_CrawlerByfeeds": {
            "url_list_tab": "YT-list",
            "to_crawl_link_col": 2,
            "crawler": yt_CrawlerByfeeds(),
            "result_tab": "YT-bot",
            "result_link_col": 4
        },
        "yt_CrawlerByScriptbarrel": {
            "url_list_tab": "YT-list",
            "to_crawl_link_col": 2,
            "crawler": yt_CrawlerByScriptbarrel(),
            "result_tab": "YT-bot",
            "result_link_col": 4
        },

    }
    config_data = config[name]
    return config_data

def customer_list():
    c_list = [
        {
            "name": "Young",
            "sheet_key": "15V1XD3p_mD8SSP_TQkY2PwYTM_FjOAXQXD1GuJcrpfI",
            "line_notify_token": "R7iIcVlcM4rBs0srfLtpea8bFrGhav3wBkX6V06of25"
        },
        # {
        # 	"name": "小黑",
        # 	"sheet_key": "11O1ujc-in6iI9kwdQtFzjQ5OkQ5oP4aDZwhoH6p9tgY",
        # 	"line_notify_token": "TABjG5hi1xyxu6MH9OU5rZULxPgYFlw5fb5QBkptK4z"
        # }
    ]

    return c_list

# Main function
def crawl(web_name):
    for customer in customer_list():
        customer_name = customer["name"]
        sheet_key = customer["sheet_key"]
        sht_worker = GsheetWorker(sheet_key).get_sheet_worker(web_name)
        line_notify_token = customer["line_notify_token"]
        line_worker = LineWorker(line_notify_token)
        try:
            # notify
            message = f"{customer_name} 開始今日爬蟲"
            line_worker.send_notification(message)
            # config
            config_data = web_config(web_name)
            tab_name = config_data['url_list_tab']
            to_crawl_link_col = config_data['to_crawl_link_col']
            crawler = config_data['crawler']
            # crawler
            to_crawl_url_list = get_to_crawl_url_list_by_sheet(sht_worker, tab_name, to_crawl_link_col)
            crawled_data_list = get_crawled_data_list(crawler, to_crawl_url_list)
            # sheet
            write_crawled_data_list_to_sheet(web_name, crawled_data_list, sht_worker)
            sht_worker.send_line_notify(line_notify_token)
            # notify
            message = f"{customer_name} 完成今日爬蟲"
            line_worker.send_notification(message)
        except Exception as error:
            print(repr(error))

def get_to_crawl_url_list_by_sheet(sht_worker, tab_name, to_crawl_link_col):
    to_crawl_url_list = sht_worker.get_col_all_value(tab_name, to_crawl_link_col)[1:]
    return to_crawl_url_list

def get_crawled_data_list(crawler, to_crawl_url_list):
    crawled_data_list = []
    for url in to_crawl_url_list:
        try:
            data = crawler.fetch_data(url)
            data_json = crawler.get_data_json(data)
            data_json = json.dumps(data_json, ensure_ascii=False).encode('utf8')
            crawled_data_list.append(data_json.decode())
        except Exception as error:
            print(f"fetch fail:{url}")
            print(repr(error))

    return crawled_data_list

def write_crawled_data_list_to_sheet(web_name, data_list, sht_worker):
    config_data = web_config(web_name)
    result_tab_name = config_data['result_tab']
    result_link_col = config_data['result_link_col']
    sheet_bot = sht_worker.get_sheet_bot(result_tab_name)
    link_list = sht_worker.get_col_all_value(result_tab_name, result_link_col)
    sht_worker.write_profile_to_sheet(data_list, sheet_bot, link_list)

def crawl_all(event,context):
    # crawl("leju")
    # crawl("591")
    # crawl("fb")
    # crawl("fb-private")
    # crawl("fb_Crawler_by_facebook_scraper")
    # crawl("fb_GoupCrawlerByRequests")
    # crawl("yt_CrawlerBySelenium")
    crawl("yt_CrawlerByfeeds")
    # crawl("yt_CrawlerByScriptbarrel")


if __name__ == "__main__":
    crawl_all("","")
    