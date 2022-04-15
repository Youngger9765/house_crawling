#!/usr/bin/env python
# coding: utf-8
from util.gsheet_worker import GsheetWorker
from util.crawler import CrawlerSelection
from util.notification import LineWorker
import json


# Params
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
            crawler = CrawlerSelection().get_crawler(web_name)
            # crawler
            to_crawl_url_list = sht_worker.get_to_crawl_url_list()
            crawled_data_list = get_crawled_data_list(crawler, to_crawl_url_list)
            # sheet
            sht_worker.write_data_list_to_sheet(crawled_data_list)
            message_list = sht_worker.message_list
            for message in message_list:
                line_worker.send_notification(message)
            # notify
            message = f"{customer_name} 完成今日爬蟲"
            line_worker.send_notification(message)
        except Exception as error:
            print(repr(error))



def get_crawled_data_list(crawler, to_crawl_url_list):
    crawled_data_list = []
    for url in to_crawl_url_list:
        try:
            data = crawler.fetch_data(url)
            data_list_json = crawler.get_data_json(data)
            data_list_json_encode = json.dumps(data_list_json, ensure_ascii=False).encode('utf8')
            data_list = json.loads(data_list_json_encode)
            crawled_data_list += data_list
        except Exception as error:
            print(f"fetch fail:{url}")
            print(repr(error))

    return crawled_data_list


def crawl_all(event,context):
    # crawl("leju")
    # crawl("591")
    # crawl("fb")
    # crawl("fb-private")
    # crawl("fb_Crawler_by_facebook_scraper")
    # crawl("fb_GoupCrawlerByRequests")
    # crawl("yt_CrawlerBySelenium")
    crawl("YtCrawlerByfeeds")
    # crawl("yt_CrawlerByScriptbarrel")


if __name__ == "__main__":
    crawl_all("","")
    