import os
from selenium import webdriver
import selenium
# import random_user_agent

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType 
from webdriver_manager.chrome import ChromeDriverManager

# from random_user_agent.user_agent import UserAgent
# from random_user_agent.params import SoftwareName, OperatingSystem

from time import sleep
from bs4 import BeautifulSoup
import json
import re

class selenium_engine:
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

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument(f'user-agent={user_agent}')
        # chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # chrome_options.add_argument("--disable-blink-features");
        # chrome_options.add_argument("--disable-blink-features=AutomationControlled");
 
        # ChromeDriverManager
        self.browser = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
        # self.browser = webdriver.Chrome(options=chrome_options)
        
        # local
        # executable_path=os.getcwd()+'/chromedriver_6'
        # self.browser = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
    
    # def fetch_data(self, url):
    #     # print(f"===fetch:{url}===")
    #     browser = self.browser
    #     browser.get(url)
    #     sleep(10)
    #     data_soup = BeautifulSoup(browser.page_source, 'html.parser')
    #     browser.quit()
    #     # print(f"===fetch:{url} done===")
        
    #     return data_soup



class lejuCrawler:
    def __init__(self):
        pass

    def fetch_data(self, url):
        print(f"===fetch:{url}===")
        engine = selenium_engine()
        browser = engine.browser
        browser.get(url)
        sleep(10)
        data_soup = BeautifulSoup(browser.page_source, 'html.parser')
        browser.quit()
        print(f"===fetch:{url} done===")
        # print(data_soup)
        
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
        # building_title = data.find('article', class_='building_title').text
        # households = data.find('article', class_='households').text
        # house_year = data.find('article', class_='house_year').text
        # ttotal_floor = data.find('article', class_='ttotal_floor').text
        # elementary = data.find('article', class_='elementary').text
        # junior = data.find('article', class_='junior').text
        # developer1 = data.find('article', class_='developer1').text
        
        # basic_info = {
        #     'building_title': building_title,
        #     'households': households,
        #     'house_year': house_year,
        #     'ttotal_floor': ttotal_floor,
        #     'elementary': elementary,
        #     'junior': junior,
        #     'developer1': developer1,
        # }

        basic_info = {}
        
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

class _591_Crawler:
    def __init__(self):
        pass

    def fetch_data(self, url):
        print(f"===fetch:{url}===")

        pattern = r".*&region=(\d).*"
        region = re.match(pattern, url).group(1)

        engine = selenium_engine()
        browser = engine.browser
        browser.get(url)

        # PopUp 選縣市 -> 目前取消
        # timeout = 3
        # try:
        #     element_present = EC.presence_of_element_located((By.ID, "area-box-close"))
        #     WebDriverWait(browser, timeout).until(element_present)
        #     browser.find_element_by_css_selector(f'[data-id="{region}"]').click()
        # except TimeoutException:
        #     print("Timed out waiting for page to load")
        # finally:
        #     print("Page loaded")
        
        timeout = 10
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, "vue-public-list-page"))
            WebDriverWait(browser, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        finally:
            print("Page loaded")    

        sleep(5)    

        data_soup_list = []
        last_page = False
        while last_page is False:
            data_soup = BeautifulSoup(browser.page_source, 'html.parser')
            data_soup_list.append(data_soup)
            
            try:
                browser.find_element_by_css_selector(".pageNext.last")
                last_page = True
                print("last page")
            except:
                print("not the last page")
                browser.find_element_by_css_selector(".pageNext").click()
                sleep(5)


        browser.quit()
        print(f"===fetch:{url} done===")
        # print(len(data_soup_list))
        
        return data_soup_list
        
    def get_data_json(self, data_soup_list):
        data_json = []

        for data_soup in data_soup_list:
            listInfo_list = data_soup.select(".vue-list-rent-item")
            
            for listInfo in listInfo_list:

                title = listInfo.select_one(".vue-list-rent-item .rent-item-right .item-title").text.replace("\n", "").strip()
                title

                url = listInfo.select_one(".vue-list-rent-item > a").get('href').strip()
                url

                info = []
                info_ele_list = listInfo.select(".vue-list-rent-item .item-style li")
                for info_ele in info_ele_list:
                  text = info_ele.text.replace("\n", "").replace(" ", "")
                  info.append(text)

                address = listInfo.select_one(".vue-list-rent-item .item-area span").text
                address

                price = listInfo.select_one(".vue-list-rent-item .item-price-text span").text.replace("\n","").replace(" ","")
                price
                
                data = {
                    "title": title,
                    "url": url,
                    "info": info,
                    "address": address,
                    "price": price
                }

                # print(data)
                data_json.append(data)
        
        return data_json
