#!/usr/bin/env python
# coding: utf-8
from util.gsheet_worker import GsheetWorker
from util.notion_worker import NotionCrawlerHandler
from util.notion_worker import NotionDataTransfer
from util.crawler import CrawlerWorker
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
            # crawler by config
            to_crawl_url_list = sht_worker.get_to_crawl_url_list()
            cawler_worker = CrawlerWorker()            
            crawled_data_list = cawler_worker.get_crawled_data_list(web_name, to_crawl_url_list)
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


def crawl_by_notion(web_name):
    # channel_url_list
    notion_crawler_handler = NotionCrawlerHandler()
    channel_list = notion_crawler_handler.get_channel_list()
    kind = web_name.replace("notion-","")
    to_crawl_url_list =  [channel["url"] for channel in channel_list if channel["kind"]==kind]
    to_crawl_url_list = list(set(to_crawl_url_list))

    print(to_crawl_url_list)
    print("=========!!!!")
    # crawler
    cawler_worker = CrawlerWorker()
    crawled_data_list = cawler_worker.get_crawled_data_list(web_name, to_crawl_url_list)

    # send to notion
    notion_data_transfer = NotionDataTransfer()
    content_data_list = notion_data_transfer.crawled_data_to_content_data_list(web_name, crawled_data_list)
    notion_crawler_handler.write_content_data_list_to_db(content_data_list)

def crawl_all(event,context):
    # crawl("leju")
    # crawl("591")
    # crawl("fb")
    # crawl("fb-private")
    # crawl("fb_Crawler_by_facebook_scraper")
    # crawl("fb_GoupCrawlerByRequests")
    # crawl("YtCrawlerByfeeds")
    # crawl("yt_CrawlerByScriptbarrel")

    # crawl_by_notion("notion-youtube")
    crawl_by_notion("notion-FB")


if __name__ == "__main__":
    crawl_all("","")
    