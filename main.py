#!/usr/bin/env python
# coding: utf-8
from util.gsheet import gsheet_worker
from util.crawler import lejuCrawler, _591_Crawler, fb_Crawler, fb_private_Crawler
# from util.crawler import fb_Crawler_by_facebook_scraper
import json
import requests

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
		},
		"fb": {
			"url_list_tab": "FB-list",
			"crawler": fb_Crawler(),
			"result_tab": "FB-bot",
			"result_link_col": 2
		},
		"fb-private": {
			"url_list_tab": "FB-private-list",
			"crawler": fb_private_Crawler(),
			"result_tab": "FB-private-bot",
			"result_link_col": 2
		},
		# "fb_Crawler_by_facebook_scraper": {
		# 	"url_list_tab": "FB-list",
		# 	"crawler": fb_Crawler_by_facebook_scraper(),
		# 	"result_tab": "FB-bot",
		# 	"result_link_col": 2
		# }

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
		line_notify_token = customer["line_notify_token"]
		try:
			message = f"{customer_name} 開始今日爬蟲"
			send_line_notification(line_notify_token, message)
			data = get_data(web_name, sheet_key)
			write_to_sheet(data, web_name, sheet_key, line_notify_token)
			message = f"{customer_name} 完成今日爬蟲"
			send_line_notification(line_notify_token, message)
		except Exception as e:
			print(repr(e))

def get_data(web_name, sheet_key):
	# config
	config_data = web_config(web_name)
	tab_name = config_data['url_list_tab']

	# get by sheet
	sht_worker = gsheet_worker(sheet_key)
	url_list = sht_worker.get_col_all_value(tab_name, 2)[1:]
	# print(url_list)
	
	# url_list = [
		# "https://www.leju.com.tw/page_search_result?oid=Lff61014736365e",
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
	# print(body)
	return body

def write_to_sheet(data, web_name, sheet_key, line_notify_token):
	config_data = web_config(web_name)
	result_tab_name = config_data['result_tab']
	result_link_col = config_data['result_link_col']
	sht_worker = gsheet_worker(sheet_key, web_name)
	sht_worker.write_profile_to_sheet(data,result_tab_name,result_link_col)
	sht_worker.send_line_notify(line_notify_token)

def send_line_notification(line_notify_token, message):
	print(message)
	url = "https://notify-api.line.me/api/notify"
	headers = {
		'Authorization': f"Bearer {line_notify_token}",
	}
	data = {
		"message": message,
	}
	requests.post(url, headers=headers, data=data)
			

def crawl_all(event,context):
	# crawl("leju")
	# crawl("591")
	crawl("fb")
	crawl("fb-private")
	# crawl("fb_Crawler_by_facebook_scraper")
		

if __name__ == "__main__":
	crawl("leju")
	# crawl("591")
	crawl("fb")
	# crawl("fb-private")
	# crawl("fb_Crawler_by_facebook_scraper")
