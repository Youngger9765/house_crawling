import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import hashlib
import requests

class gsheet_worker:
    def __init__(self):
        self.sheet_key = '15V1XD3p_mD8SSP_TQkY2PwYTM_FjOAXQXD1GuJcrpfI'

    def get_hash_str(self,data):
        hash_str = int(hashlib.sha1(data.encode("utf-8")).hexdigest(), 16) % (10 ** 8)
        return hash_str
        
    def get_sheet(self, sheet_key):
        scopes = ["https://spreadsheets.google.com/feeds"]
        current_path = os.getcwd()
        credentials = ServiceAccountCredentials.from_json_keyfile_name(current_path+"/cred.json", scopes)
        gss_client = gspread.authorize(credentials)
        spreadsheet_key_path = sheet_key
        sheet = gss_client.open_by_key(spreadsheet_key_path)
        return sheet
    
    def data_to_sheet_value_list(self, data):
        profile = json.loads(data)
        title = profile['title']
        price_info = profile['price_info']
        basic_info = profile['basic_info']

        sale_items = profile['sale_items']
        sheet_value_list = []
        sheet_value_str_list = []
        for sale_item in sale_items:
            floor = sale_item['floor']
            sub_title = sale_item['title']
            link = sale_item['link']
            price = sale_item['price']
            area = sale_item['area']

            sheet_value = [
                str(title),
                str(price_info),
                str(basic_info),
                floor,
                sub_title,
                link,
                price,
                area
            ]

            sheet_value_str = "".join(sheet_value)
            sheet_value_str_list.append(sheet_value_str)
            # sheet_value.append(sheet_value_str)

            hash_str = self.get_hash_str(sheet_value_str)
            sheet_value.append(hash_str)
            sheet_value_list.append(sheet_value)
            
        return sheet_value_list

    def get_col_all_value(self, tab_name, colunm_index):
        sheet = self.get_sheet(self.sheet_key)
        sheet_bot_link = sheet.worksheet(tab_name)
        col_all_value = sheet_bot_link.col_values(colunm_index)
        return col_all_value
        
        
    def write_profile_to_sheet(self, data):
        sheet = self.get_sheet(self.sheet_key)
        sheet_bot = sheet.worksheet('bot')

        link_list = self.get_col_all_value("bot", 5)
        profile_list = data['profile']
        for profile in profile_list:
            sheet_value_list = self.data_to_sheet_value_list(profile)
            # print(sheet_value_list)
        
            sheet_row_cnt = 2
            for sheet_value in sheet_value_list:
                link = str(sheet_value[5])
                
                if link in link_list:
                    print("===exist!===")
                    print(link)
                    print("============")
                else:
                    sheet_bot.insert_row(sheet_value, sheet_row_cnt) 
                    message = f"{sheet_value[0]} 有新物件 {sheet_value[4]}，{sheet_value[6]} ，詳情請點擊公告" 
                    self.send_line_notify(message)                  
                    sheet_row_cnt +=1

    def send_line_notify(self, message):
        line_notify_token = "R7iIcVlcM4rBs0srfLtpea8bFrGhav3wBkX6V06of25"
        url = "https://notify-api.line.me/api/notify"

        headers = {
            'Authorization': f"Bearer {line_notify_token}",
        }
        data = {
            "message": message,
        }
        # To send data form-encoded
        response = requests.post(url, headers=headers, data=data)
            
            
            
        