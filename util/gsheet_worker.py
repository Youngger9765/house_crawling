# !/usr/bin/python
# coding:utf-8
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import hashlib
import requests
from datetime import datetime as dt
from time import sleep

class GsheetWorker:
    def __init__(self, sheet_key):
        self.sheet_key = sheet_key
        self.sheet_worker = None
        self.message_list = []
        self.sheet_config = None
        self.url_list_tab = None
        self.to_crawl_link_col = None
        self.result_tab = None
        self.result_host_name_col = None
        self.result_content_col = None
        self.result_link_col = None
        self.result_message_col = None
        self.black_list = [
            "林森北路",
            "1房"
        ]

    def get_sheet_worker(self, web_name):
        if web_name == "leju":
            worker = LejuGsheetWorker(self.sheet_key)
        elif web_name == "591":
            worker = _591GsheetWorker(self.sheet_key)
        elif web_name in ["fb","fb-private","fb_Crawler_by_facebook_scraper", "fb_GoupCrawlerByRequests"]:
            worker = FbGsheetWorker(self.sheet_key)
        elif web_name in ["YtApiCrawler","YtCrawlerByfeeds","yt_CrawlerByScriptbarrel", "YtCrawlerInPlaylist"]:
            worker = YtGsheetWorker(self.sheet_key)

        return worker

    def get_sheet(self, sheet_key):
        scopes = ["https://spreadsheets.google.com/feeds"]
        current_path = os.getcwd()
        credentials = ServiceAccountCredentials.from_json_keyfile_name(current_path+"/cred.json", scopes)
        gss_client = gspread.authorize(credentials)
        spreadsheet_key_path = sheet_key
        sheet = gss_client.open_by_key(spreadsheet_key_path)
        return sheet

    def data_to_sheet_value_list(self, data):
        sheet_worker = self.sheet_worker
        sheet_value_list = sheet_worker.data_to_sheet_value_list(data)

        return sheet_value_list

    def get_col_all_value(self, tab_name, colunm_index):
        sheet = self.get_sheet(self.sheet_key)
        sheet_tab = sheet.worksheet(tab_name)
        col_all_value = sheet_tab.col_values(colunm_index)
        return col_all_value

    def get_to_crawl_url_list(self):
        tab_name = self.url_list_tab
        to_crawl_link_col = self.to_crawl_link_col
        to_crawl_url_list = self.get_col_all_value(tab_name, to_crawl_link_col)[1:]
        return to_crawl_url_list

    def get_result_sheet_tab(self,result_tab_name):
        sheet = self.get_sheet(self.sheet_key)
        result_sheet_tab = sheet.worksheet(result_tab_name)
        return result_sheet_tab

    def write_data_list_to_sheet(self, data_list):
        result_tab_name = self.result_tab
        result_sheet_tab = self.get_result_sheet_tab(result_tab_name)
        result_link_col = self.result_link_col
        exist_link_list = self.get_col_all_value(result_tab_name, result_link_col)
        for data in data_list:
            sheet_value = self.data_to_sheet_value(data)
            sheet_row_cnt = 2
            self.insert_sheet_value(result_sheet_tab, sheet_value, exist_link_list, sheet_row_cnt)

    def insert_sheet_value(self, result_sheet_tab, sheet_value, exist_link_list, sheet_row_cnt=2):
        """
            result_sheet_tab = tab
            sheet_value: inserted data value list
            exist_link_list: the list of link already saved in sheet
        """
        link = str(sheet_value[self.result_link_col-1])
        print("====link====")
        print(link)

        if link in exist_link_list:
            print("===exist!===")
            print(link)
            print("============")
        else:
            try:
                sleep(1.5)
                result_sheet_tab.insert_row(sheet_value, sheet_row_cnt)
                result_host_name = sheet_value[self.result_host_name_col-1]
                content = sheet_value[self.result_content_col-1]
                # message = f"【YT-{result_host_name}】 有新作品: {content}，詳情請點擊:{link}"
                message = sheet_value[self.result_message_col-1]
                print(message)
                self.message_list.append(message)
                sheet_row_cnt +=1
            except Exception as error:
                sleep(10)
                print("sheet insert fail!")
                print(repr(error))


class LejuGsheetWorker(GsheetWorker):
    def __init__(self,sheet_key):
        super().__init__(sheet_key)
        self.url_list_tab = "leju-list"
        self.to_crawl_link_col = 2
        self.result_tab = "leju-bot"
        self.result_host_name_col = 1
        self.result_content_col = 5
        self.result_link_col = 6
        self.result_message_col = 12

    def data_to_sheet_value(self, data):
        sale_item = data
        title = sale_item['title']
        floor = sale_item['floor']
        name = sale_item['name']
        link = sale_item['link']
        price = sale_item['price']
        area = sale_item['area']
        now = dt.now().strftime("%Y/%m/%d")
        message = f"【樂居-{title}】 有新物件: {name} {price}萬，詳情請點擊:{link}"

        sheet_value = [
            str(title),
            str(""),
            str(""),
            floor,
            name,
            link,
            price,
            area,
            now,
            message
        ]
            
        return sheet_value


class _591GsheetWorker(GsheetWorker):
    def __init__(self,sheet_key):
        super().__init__(sheet_key)
        self.url_list_tab = "591-list"
        self.to_crawl_link_col = 2
        self.result_tab = "591-bot"
        self.result_host_name_col = 1
        self.result_content_col = 3
        self.result_link_col = 2
        self.result_message_col = 7

    def data_to_sheet_value(self, data):
        rent_info = data
        title = rent_info['title']
        link = rent_info['url']
        info = rent_info['info']
        address = rent_info['address']
        price = rent_info['price']
        now = dt.now().strftime("%Y/%m/%d")
        message = f"【591-{title}】 有新物件: {info} {address} {price}元，詳情請點擊:{link}"

        sheet_value = [
            str(title),
            str(link),
            str(info),
            str(address),
            str(price),
            now,
            message
        ]

        return sheet_value


class FbGsheetWorker(GsheetWorker):
    def __init__(self,sheet_key):
        super().__init__(sheet_key)
        self.url_list_tab = "FB-list"
        self.to_crawl_link_col = 2
        self.result_tab = "FB-bot"
        self.result_host_name_col = 3
        self.result_content_col = 8
        self.result_link_col = 4
        self.result_message_col = 11

    def data_to_sheet_value(self, data):
        post_info = data
        post_group_id = post_info['post_group_id'], # 這邊會變成 tuple 不知道為什麼？
        post_group_id = post_group_id[0]
        post_group_url = post_info['post_group_url']
        post_group_name = post_info['post_group_name']
        post_link = post_info['post_link']
        post_time = post_info['post_time']
        title = post_info['title']
        sub_title = post_info['sub_title']
        content = post_info['content']
        img_link = post_info['img_link']
        now = dt.now().strftime("%Y/%m/%d")
        message = f"【FB-{post_group_name}】 有新物件: {title} {sub_title} {content}，詳情請點擊:{post_link}"

        sheet_value = [
            str(post_group_id),
            str(post_group_url),
            str(post_group_name),
            str(post_link),
            str(post_time),
            str(title),
            str(sub_title),
            str(content),
            str(img_link),
            now,
            message
        ]

        return sheet_value


class YtGsheetWorker(GsheetWorker):
    def __init__(self,sheet_key):
        super().__init__(sheet_key)
        self.url_list_tab = "YT-list"
        self.to_crawl_link_col = 2
        self.result_tab = "YT-bot"
        self.result_host_name_col = 3
        self.result_content_col = 6
        self.result_link_col = 4
        self.result_message_col = 12

    def data_to_sheet_value(self, data):
        video = data
        channel_id = video['channel_id']
        channel_url = video['channel_url']
        channel_name = video['channel_name']
        video_id = video['video_id']
        video_url = video['video_url']
        published = video['published']
        title = video['title']
        img_link = video['img_link']
        description = video['description']
        tag_list = video['tag_list']
        now = dt.now().strftime("%Y/%m/%d")
        message = f"【YT-{channel_name}】 有新影片: {title}，詳情請點擊:{video_url}"
        playlist_id = video["playlist_id"]
        playlist_title = video["playlist_title"]
        playlist_position = video["playlist_position"]

        sheet_value = [
            str(channel_id),
            str(channel_url),
            str(channel_name),
            str(video_url),
            str(published),
            str(title),
            str(img_link),
            str(description),
            str(tag_list),
            str(video_id),
            now,
            message,
            playlist_id,
            playlist_title,
            playlist_position,
        ]

        return sheet_value

