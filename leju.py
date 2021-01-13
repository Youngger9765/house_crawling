#!/usr/bin/env python
# coding: utf-8

# In[111]:


import os
os.getcwd()


# In[112]:


from selenium import webdriver
import selenium
import random_user_agent

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType 

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from time import sleep
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import json


# In[124]:


class leju_crawler:
    def __init__(self):
#         software_names = [SoftwareName.CHROME.value]
#         operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
#         user_agent_rotator = UserAgent(
#             software_names = software_names,
#             operating_systems = operating_systems,
#             limit = 100
#         )

#         self.user_agent = user_agent_rotator.get_random_user_agent()
#         print(user_agent)

        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

        chrome_options = Options()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument(f'user-agent={user_agent}')
        # chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # chrome_options.add_argument("--disable-blink-features");
        # chrome_options.add_argument("--disable-blink-features=AutomationControlled");
        # driver = webdriver.Chrome(options=chrome_options)
        executable_path=os.getcwd()+'/chromedriver_6'
#         print(executable_path)

        self.browser = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
    
    def fetch_data(self, url):
        browser = self.browser
        browser.get(url)
        sleep(10)
        data_soup = BeautifulSoup(browser.page_source, 'html.parser')
        browser.quit()
        
        return data_soup
        
    def get_title(self, data):
        title = data.find('title').string
        
        return title
        
    def get_price_info(self, data):
        avg_price = data.find('div', class_='avg_house_price_val').text
        max_price = data.find('div', class_='max_house_price_val').text
        min_price = data.find('div', class_='min_house_price_val').text
        this_year_avg_price = data.find('div', class_='avg_date_house_price_val').text
        
        info = {
            'avg_price': avg_price,
            'max_price': max_price, 
            'min_price': min_price,
            'this_year_avg_price': this_year_avg_price
        }
        
        return info
    
    def get_basic_info(self, data):
        building_title = data.find('article', class_='building_title').text
        households = data.find('article', class_='households').text
        house_year = data.find('article', class_='house_year').text
        ttotal_floor = data.find('article', class_='ttotal_floor').text
        elementary = data.find('article', class_='elementary').text
        junior = data.find('article', class_='junior').text
        developer1 = data.find('article', class_='developer1').text
        
        basic_info = {
            'building_title': building_title,
            'households': households,
            'house_year': house_year,
            'ttotal_floor': ttotal_floor,
            'elementary': elementary,
            'junior': junior,
            'developer1': developer1,
        }
        
        return basic_info
        
        
    def get_sale_items(self, data):
        items = data.find_all('div', class_='sales-item-box')
        sale_items = []
        for item in items:
            floor = item.find('span').text
            title = item.find('a').text
            link = item.find('a')['href']
            price = item.find_all('li')[1].text
            area = item.find_all('li')[0].text
            
            data = {
                'floor': floor,
                'title': title,
                'link': link,
                'price': price,
                'area': area,
            }
            
            sale_items.append(data)
            
        return sale_items
            
        
            
        
    def get_data_json(self, data):
        title = self.get_title(data)
        price_info = self.get_price_info(data)
        basic_info =self.get_basic_info(data)
        sale_items = self.get_sale_items(data)
        
        data_json = {
            "title": title,
            'price_info': price_info,
            'basic_info': basic_info,
            'sale_items': sale_items
        }
        
        return data_json


def crawl(event, context):
    
    url_list = [
        "https://www.leju.com.tw/page_search_result?oid=L37611690f7027",
    ]
    
    body = {'profile':[]}
    num = 0
    for url in url_list:
        leju_crawler = leju_crawler()
        data = leju_crawler.fetch_data(url)
        data_json = leju_crawler.get_data_json(data)
#         data_json = json.loads(data_json)
        data_json = json.dumps(data_json, indent=4, sort_keys=True, ensure_ascii=False).encode('utf8')
        print(data_json.decode())
        body['profile'].append()

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }
    return response





