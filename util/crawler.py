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
        
        try:
            browser.find_element_by_css_selector(".cookies-button.know").click()
        except:
            pass

        link_btns = browser.find_elements_by_css_selector('#sale-objects-wrap .border-grey-3 .icon-link-ext')
        ext_url_list = []

        for link in link_btns:
            browser.execute_script("arguments[0].click();", link)
            browser.switch_to.window(browser.window_handles[1])
            url = browser.current_url
            print(url)
            ext_url_list.append(url)
            browser.close()
            browser.switch_to.window(browser.window_handles[0])

        browser.quit()
        print(f"===fetch:{url} done===")
        # print(data_soup)
        
        return [data_soup, ext_url_list]
    
    def get_title(self, data):
        title = data.find('title').string

        return title
        
    def get_price_info(self, data):
        # avg_price = data.find('div', class_='avg_house_price_val').text
        # max_price = data.find('div', class_='max_house_price_val').text
        # min_price = data.find('div', class_='min_house_price_val').text
        # this_year_avg_price = data.find('div', class_='avg_date_house_price_val').text
        
        # info = {
            # 'avg_price': avg_price,
            # 'max_price': max_price, 
            # 'min_price': min_price,
        #     'this_year_avg_price': this_year_avg_price
        # }
        
        info = {}
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
        ext_url = data[1]
        data_soup = data[0]
        items = data_soup.select('#sale-objects-wrap .border-grey-3')
        sale_items = []
        for idx, item in enumerate(items):
            floor = item.select_one(".text-16px").text
            title = item.select_one(".title-width").text.replace("\n","").strip()
            link = ext_url[idx]
            price = item.select(".items-baseline")[0].select('span')[0].text.replace("\n","").strip()
            area = item.select(".items-baseline")[1].select('span')[0].text.replace("\n","").strip()
            
            item_data = {
                'floor': floor,
                'title': title,
                'link': link,
                'price': price,
                'area': area,
            }
            sale_items.append(item_data)
 
        return sale_items
        
    def get_data_json(self, data):
        title = self.get_title(data[0])
        sale_items = self.get_sale_items(data)
        
        data_json = {
            "title": title,
            'price_info': "",
            'basic_info': "",
            'sale_items': sale_items
        }
        
        return data_json

class _591_Crawler:
    def __init__(self):
        pass

    def fetch_data(self, url):
        print(f"===fetch:{url}===")

        # pattern = r".*&region=(\d).*"
        # region = re.match(pattern, url).group(1)

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
            
            if len(browser.find_elements(By.CLASS_NAME, 'pageNext')) > 0:
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
                url = listInfo.select_one(".vue-list-rent-item > a").get('href').strip()
                info = []
                info_ele_list = listInfo.select(".vue-list-rent-item .item-style li")
                for info_ele in info_ele_list:
                  text = info_ele.text.replace("\n", "").replace(" ", "")
                  info.append(text)

                address = listInfo.select_one(".vue-list-rent-item .item-area span").text
                price = listInfo.select_one(".vue-list-rent-item .item-price-text span").text.replace("\n","").replace(" ","")                
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


class fb_Crawler:
    def __init__(self):
        pass

    def fetch_data(self, url):
        print(f"===fetch:{url}===")
        engine = selenium_engine()
        browser = engine.browser
        browser.get(url)

        timeout = 10
        try:
            element_present_class_name = ".du4w35lb.k4urcfbm.l9j0dhe7.sjgh65i0 .rq0escxv.rq0escxv.l9j0dhe7.du4w35lb.hybvsw6c.io0zqebd.m5lcvass.fbipl8qg.nwvqtn77.k4urcfbm.ni8dbmo4.stjgntxs.sbcfpzgs"
            element_present = EC.presence_of_element_located((By.CLASS_NAME, element_present_class_name))
            WebDriverWait(browser, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        finally:
            print("Page loaded")  

        sleep(10)

        # scroll down
        for i in range(1):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(5)

        data_soup = BeautifulSoup(browser.page_source, 'html.parser')
        print(f"===fetch:{url} done===")

        return data_soup


    def get_data_json(self, data_soup):
        # selector params
        posts_group_class_name = "h1 a"
        post_class_name = ".du4w35lb.k4urcfbm.l9j0dhe7.sjgh65i0 .rq0escxv.rq0escxv.l9j0dhe7.du4w35lb.hybvsw6c.io0zqebd.m5lcvass.fbipl8qg.nwvqtn77.k4urcfbm.ni8dbmo4.stjgntxs.sbcfpzgs"
        title_class_name = "h3"
        sub_title_class_name = "h4"
        content_class_name = ".dati1w0a.ihqw7lf3.hv4rvrfc.ecm0bbzt"
        img_class_name = "img"
        post_a_class_name = ".oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gmql0nx0.gpro0wi8.b1v8xokw"

        post_group_name = data_soup.select_one(posts_group_class_name).text
        # posts
        posts = data_soup.select(post_class_name)
        data_json = []
        for post in posts:
            # post
            post_link = post.select_one(post_a_class_name).get("href").split('/?')[0]
            post_time = post.select_one(post_a_class_name).get("aria-label")

            # title
            title = ""
            sub_title = ""

            try:
                title = post.select_one(title_class_name).text
                sub_title = post.select_one(sub_title_class_name).text
            except:
                print("no title")

            # content
            content_list = post.select(content_class_name)
            content = ""
            for c in content_list:
                content = content + " " + c.text

            # img
            img_link = post.select_one(img_class_name).get("src")

            data = {
                "post_group_name": post_group_name,
                "post_link": post_link,
                "post_time": post_time,
                "title": title,
                "sub_title": sub_title,
                "content": content,
                "img_link": img_link,
            }
            data_json.append(data)

        return data_json
