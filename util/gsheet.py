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

class gsheet_worker:
    def __init__(self, sheet_key, web_name=None, result_tab_name=None):
        self.sheet_key = sheet_key
        if web_name == "leju":
            self.sheet_worker = leju_gsheet_worker()
        elif web_name == "591":
            self.sheet_worker = _591_gsheet_worker()
        elif web_name in ["fb","fb-private","fb_Crawler_by_facebook_scraper", "fb_GoupCrawlerByRequests"]:
            self.sheet_worker = fb_gsheet_worker()
        elif web_name in ["yt_CrawlerByfeeds","yt_CrawlerByScriptbarrel"]:
            self.sheet_worker = yt_gsheet_worker()
        else:
            self.sheet_worker = None

        self.black_list = [
            "林森北路",
            "1房"
        ]
        
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
        sheet_bot_link = sheet.worksheet(tab_name)
        col_all_value = sheet_bot_link.col_values(colunm_index)
        return col_all_value
        
        
    def write_profile_to_sheet(self, data, result_tab_name, result_link_col):
        sheet = self.get_sheet(self.sheet_key)
        sheet_bot = sheet.worksheet(result_tab_name)

        link_list = self.get_col_all_value(result_tab_name, result_link_col)
        # print("====link_list====")
        # print(link_list)

        sheet_worker = self.sheet_worker
        sheet_worker.write_profile_to_sheet(data, sheet_bot, link_list)
        
    
    def send_line_notify(self, line_notify_token):
        sheet_worker = self.sheet_worker
        message_list = sheet_worker.get_message_list()
        for message in message_list:
            if any(word in message for word in self.black_list):
                print("====black_list====")
            else:
                url = "https://notify-api.line.me/api/notify"
                headers = {
                    'Authorization': f"Bearer {line_notify_token}",
                }
                data = {
                    "message": message,
                }
                # To send data form-encoded
                response = requests.post(url, headers=headers, data=data)
            
            
class leju_gsheet_worker:
    def __init__(self):
        self.message_list = []

    def data_to_sheet_value_list(self, data):
        profile = json.loads(data)
        title = profile['title']
        price_info = profile['price_info']
        basic_info = profile['basic_info']

        sale_items = profile['sale_items']
        sheet_value_list = []
        for sale_item in sale_items:
            floor = sale_item['floor']
            sub_title = sale_item['title']
            link = sale_item['link']
            price = sale_item['price']
            area = sale_item['area']
            now = dt.now().strftime("%Y/%m/%d")

            sheet_value = [
                str(title),
                str(price_info),
                str(basic_info),
                floor,
                sub_title,
                link,
                price,
                area,
                now
            ]
            sheet_value_list.append(sheet_value)
            
        return sheet_value_list

    def write_profile_to_sheet(self, data, sheet_bot, link_list):
        profile_list = data['profile']
        for profile in profile_list:
            sheet_value_list = self.data_to_sheet_value_list(profile)
            # print(sheet_value_list)
        
            sheet_row_cnt = 2
            for sheet_value in sheet_value_list:
                link = str(sheet_value[5])
                print("====link====")
                print(link)
                
                if link in link_list:
                    print("===exist!===")
                    print(link)
                    print("============")
                else:
                    sleep(1)
                    sheet_bot.insert_row(sheet_value, sheet_row_cnt) 
                    message = f"【樂居】{sheet_value[0]} 有新物件 {sheet_value[4]}，{sheet_value[6]} ，詳情請點擊: {sheet_value[5]}" 
                    print(message)
                    # self.send_line_notify(message) 
                    self.message_list.append(message)                 
                    sheet_row_cnt +=1

    def get_message_list(self):
        message_list = self.message_list
        return message_list
          

class _591_gsheet_worker:
    def __init__(self):
        self.message_list = []

    def data_to_sheet_value_list(self, data):
        sheet_value_list = []
        listInfo_list = json.loads(data)
        for rent_info in listInfo_list:
            title = rent_info['title']
            link = rent_info['url']
            info = rent_info['info']
            address = rent_info['address']
            price = rent_info['price']
            now = dt.now().strftime("%Y/%m/%d")

            sheet_value = [
                str(title),
                str(link),
                str(info),
                str(address),
                str(price),
                now
            ]
            sheet_value_list.append(sheet_value)

        return sheet_value_list

    def write_profile_to_sheet(self, data, sheet_bot, link_list):
        profile_list = data['profile']
        for profile in profile_list:
            sheet_value_list = self.data_to_sheet_value_list(profile)
            # print(sheet_value_list)
        
            sheet_row_cnt = 2
            for sheet_value in sheet_value_list:
                link = str(sheet_value[1])
                print("====link====")
                print(link)
                
                if link in link_list:
                    print("===exist!===")
                    print(link)
                    print("============")
                else:
                    try:
                        sleep(3)
                        sheet_bot.insert_row(sheet_value, sheet_row_cnt) 
                        message = f"【591租屋】 有新物件 {sheet_value[0]}:{sheet_value[2]},address:{sheet_value[3]} price:{sheet_value[4]} ，詳情請點擊:{sheet_value[1]}" 
                        print(message)
                        self.message_list.append(message)                 
                        sheet_row_cnt +=1
                    except Exception as e:
                        print(f"sheet insert fail!")
                        print(repr(e))

    def get_message_list(self):
        message_list = self.message_list
        return message_list


class fb_gsheet_worker:
    def __init__(self):
        self.message_list = []

    def data_to_sheet_value_list(self, data):
        sheet_value_list = []
        post_list = json.loads(data)

        for post_info in post_list:
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
                now
            ]
            sheet_value_list.append(sheet_value)

        return sheet_value_list

    def write_profile_to_sheet(self, data, sheet_bot, link_list):
        profile_list = data['profile']
        for profile in profile_list:
            sheet_value_list = self.data_to_sheet_value_list(profile)        
            sheet_row_cnt = 2
            link_position = 3
            for sheet_value in sheet_value_list:
                link = str(sheet_value[link_position])
                print("====link====")
                print(link)
                
                if link in link_list:
                    print("===exist!===")
                    print(link)
                    print("============")
                else:
                    try:
                        sleep(3)
                        sheet_bot.insert_row(sheet_value, sheet_row_cnt) 
                        message = f"【FB-{sheet_value[2]}】 有新文章: {sheet_value[5]} {sheet_value[6]} {sheet_value[7]} ，詳情請點擊:{sheet_value[3]}"
                        print(message)
                        self.message_list.append(message)                 
                        sheet_row_cnt +=1
                    except Exception as e:
                        print(f"sheet insert fail!")
                        print(repr(e))

    def get_message_list(self):
        message_list = self.message_list
        return message_list


class yt_gsheet_worker:
    def __init__(self):
        self.message_list = []

    def data_to_sheet_value_list(self, data):
        sheet_value_list = []
        video_list = json.loads(data)

        for video in video_list:
            channel_id = video['channel_id']
            channel_url = video['channel_url']
            channel_name = video['channel_name']
            video_url = video['video_url']
            published = video['published']
            title = video['title']
            img_link = video['img_link']
            now = dt.now().strftime("%Y/%m/%d")

            data = {
                "channel_id": channel_id,
                "channel_url": channel_url,
                "channel_name": channel_name,
                "video_url": video_url,
                "published": published,
                "title": title,
                "img_link": img_link
            }


            sheet_value = [
                str(channel_id),
                str(channel_url),
                str(channel_name),
                str(video_url),
                str(published),
                str(title),
                str(img_link),
                now
            ]
            sheet_value_list.append(sheet_value)

        return sheet_value_list

    def write_profile_to_sheet(self, data, sheet_bot, link_list):
        profile_list = data['profile']
        for profile in profile_list:
            sheet_value_list = self.data_to_sheet_value_list(profile)        
            sheet_row_cnt = 2
            link_position = 3
            for sheet_value in sheet_value_list:
                link = str(sheet_value[link_position])
                print("====link====")
                print(link)
                
                if link in link_list:
                    print("===exist!===")
                    print(link)
                    print("============")
                else:
                    try:
                        sleep(3)
                        sheet_bot.insert_row(sheet_value, sheet_row_cnt) 
                        message = f"【FB-{sheet_value[2]}】 有新影片: {sheet_value[5]}，詳情請點擊:{link}"
                        print(message)
                        self.message_list.append(message)                 
                        sheet_row_cnt +=1
                    except Exception as e:
                        print(f"sheet insert fail!")
                        print(repr(e))

    def get_message_list(self):
        message_list = self.message_list
        return message_list
