import os
import datetime
from datetime import date
from time import sleep

from selenium import webdriver
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

import json
import re
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# facebook_scraper
from facebook_scraper import get_posts
from facebook_scraper import get_group_info

# https://github.com/ScriptSmith/socialreaper
import socialreaper


class selenium_engine:
    def __init__(self):
        # user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--single-process')
        # chrome_options.add_argument(f'user-agent={user_agent}')
        # chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # chrome_options.add_argument("--disable-blink-features");
        # chrome_options.add_argument("--disable-blink-features=AutomationControlled");

        # is_AWS = os.environ['is_AWS']

        # ChromeDriverManager
        # chrome_options.binary_location = '/opt/headless-chromium'
        # self.browser = webdriver.Chrome('/opt/chromedriver',options=chrome_options)
        self.browser = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)


class crawler:
    def __init__(self):
        print("===crawler init ===")
        self.browser = None

    def get_browser(self):
        engine = selenium_engine()
        self.browser = engine.browser

    def wait_by_class_name(self, class_name):
        timeout = 10
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, class_name))
            WebDriverWait(self.browser, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
        finally:
            print("Page loaded")
        sleep(5)

    def scroll_down(self, count):
        for i in range(count):
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(5)


class lejuCrawler(crawler):
    def __init__(self):
        print("===lejuCrawler init ===")

    def fetch_data(self, url):
        self.get_browser()
        data_soup = self.fetch_url_data(url)

        return data_soup

    def fetch_url_data(self, url):
        print(f"===fetch:{url}===")
        browser = self.browser
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

class _591_Crawler(crawler):
    def __init__(self):
        print("===_591_Crawler init ===")

    def fetch_data(self, url):
        self.get_browser()
        data_soup = self.fetch_url_data(url)
        
        return data_soup

    def fetch_url_data(self, url):
        print(f"===fetch:{url}===")
        browser = self.browser
        browser.get(url)
        self.wait_by_class_name("vue-public-list-page")
        
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
            else:
                last_page = True

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

class fb_Crawler(crawler):
    def __init__(self):
        print("===fb_Crawler init ===")

    def fetch_data(self,url):
        self.get_browser()
        data_soup = self.fetch_url_data(url)
        # print(data_soup)
        return data_soup

    def fetch_url_data(self, url):
        print(f"===fetch:{url}===")
        browser = self.browser
        m_url = url.replace("www","m")
        browser.get(m_url)
        sleep(10)
        # self.wait_by_class_name(".du4w35lb.k4urcfbm.l9j0dhe7.sjgh65i0 .rq0escxv.rq0escxv.l9j0dhe7.du4w35lb.hybvsw6c.io0zqebd.m5lcvass.fbipl8qg.nwvqtn77.k4urcfbm.ni8dbmo4.stjgntxs.sbcfpzgs")
        self.scroll_down(2)
        data_soup = BeautifulSoup(browser.page_source, 'html.parser')
        browser.quit()
        print(f"===fetch:{url} done===")

        return data_soup

    def get_data_json(self, data_soup):
        # selector params for www.
        # posts_group_class_name = "h1 a"
        # posts_group_id_selector = 'meta[property="al:android:url"]'
        # post_class_name = ".du4w35lb.k4urcfbm.l9j0dhe7.sjgh65i0 .rq0escxv.rq0escxv.l9j0dhe7.du4w35lb.hybvsw6c.io0zqebd.m5lcvass.fbipl8qg.nwvqtn77.k4urcfbm.ni8dbmo4.stjgntxs.sbcfpzgs"
        # title_class_name = "h3"
        # sub_title_class_name = "h4"
        # content_class_name_1 = ".dati1w0a.ihqw7lf3.hv4rvrfc.ecm0bbzt"
        # content_class_name_2 = ".d2edcug0.hpfvmrgz.qv66sw1b.c1et5uql.oi732d6d.ik7dh3pa.ht8s03o8.a8c37x1j.fe6kdd0r.mau55g9w.c8b282yb.keod5gw0.nxhoafnm.aigsh9s9.d9wwppkn.iv3no6db.jq4qci2q.a3bd9o3v.b1v8xokw.oo9gr5id.hzawbc8m"
        # img_class_name = "img"
        # post_a_class_name = ".oajrlxb2.g5ia77u1.qu0x051f.esr5mh6w.e9989ue4.r7d6kgcz.rq0escxv.nhd2j8a9.nc684nl6.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.jb3vyjys.rz4wbd8a.qt6c0cv9.a8nywdso.i1ao9s8h.esuyzwwr.f1sip0of.lzcic4wl.gmql0nx0.gpro0wi8.b1v8xokw"

        # post_group_name = data_soup.select_one(posts_group_class_name).text
        # post_group_id = data_soup.select_one(posts_group_id_selector)["content"].replace("fb://group/","")
        # post_group_url = data_soup.select_one(posts_group_class_name)["href"][:-1]

        # selector params for m.
        group_name_selector = "head > title"
        post_group_name = data_soup.select_one(group_name_selector).text
        posts_group_id_selector = 'meta[property="al:android:url"]'
        post_group_id = data_soup.select_one(posts_group_id_selector)["content"].replace("fb://group/","")
        posts_group_class_name = 'meta[property="og:url"]'
        post_group_url = data_soup.select_one(posts_group_class_name)["content"][:-1]

        # posts
        post_class_name = "section > article"
        posts = data_soup.select(post_class_name)
        data_json = []
        for post in posts:
            try:
                # post
                post_id = json.loads(post["data-ft"])["top_level_post_id"]
                post_link = "https://www.facebook.com/" + post_id

                page_id = json.loads(post["data-ft"])["page_id"]
                publish_time = json.loads(post["data-ft"])["page_insights"][page_id]['post_context']['publish_time']
                post_time = datetime.datetime.fromtimestamp(publish_time).strftime("%Y-%m-%d")

                 # # title
                title = ""
                sub_title = ""

                # # content
                content = post.find('div',{'data-ft':'{"tn":"*s"}'}).text

                # # img
                try:
                    img_link = "www.facebook.com/" + json.loads(post["data-ft"])['photo_id']
                except:
                    img_link = ""

                data = {
                    "post_group_id": post_group_id,
                    "post_group_url": post_group_url,
                    "post_group_name": post_group_name,
                    "post_link": post_link,
                    "post_time": post_time,
                    "title": title,
                    "sub_title": sub_title,
                    "content": content,
                    "img_link": img_link,
                }
                data_json.append(data)

            except Exception as e:
                print(repr(e))

        return data_json

class fb_private_Crawler(fb_Crawler):
    def __init__(self):
        print("===fb_private_Crawler init ===")

    def fetch_data(self,url):
        print("=====fb_private_Crawler fetch_data======")
        self.get_browser()
        self.login_bowser()
        data_soup = self.fetch_url_data(url)

        return data_soup

    def login_bowser(self):
        url = "https://www.facebook.com"
        browser = self.browser
        browser.get(url)
        sleep(15)
        username = 'young.tsai.9765@gmail.com'
        password = 'babamama2022'
        WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="email"]')))
        elem = browser.find_element_by_id("email")
        elem.send_keys(username)
        sleep(3)
        elem = browser.find_element_by_id("pass")
        elem.send_keys(password)
        sleep(3)
        elem = browser.find_element_by_xpath('//button[@name="login"]')
        elem.click()
        sleep(10)

class fb_Crawler_by_facebook_scraper():
    def __init__(self):
        print("===fb_Crawler_by_facebook_scraper init ===")

    def fetch_data(self,url):
        if "groups" in url:
            group_id = url.split("/")[-1]
            posts = get_posts(group=group_id, pages=1)
            group_info = get_group_info(group_id)
            post_group_id = group_info['id']
            post_group_url = "www.facebook.com/groups/" + group_id
            post_group_name = group_info['name']

        return [posts, post_group_id, post_group_url, post_group_name]

    def get_data_json(self, data):
        posts = data[0]
        post_group_id = data[1]
        post_group_url = data[2]
        post_group_name = data[3]
        cnt = 0
        cnt_limit = 10
        data_json = []
        for post in posts:
            content = post['post_text'][:100]
            post_time = str(post['time']).split()[0]
            post_link = "www.facebook.com/" + post['post_id']
            img_link = post['image']
            data = {
                'post_group_id': post_group_id,
                'post_group_url': post_group_url,
                'post_group_name': post_group_name,
                'post_link': post_link,
                'post_time': post_time,
                "title": "",
                "sub_title": "",
                'content': content,
                'img_link': img_link
            }
            data_json.append(data)
            print(data)

            cnt +=1
            if cnt >= cnt_limit:
                break

        return data_json

class fb_GoupCrawlerByRequests():
    def __init__(self):
        print("===fb_CrawlerByRequests init ===")

    def fetch_data(self, url):
        print("===fb_CrawlerByRequests fetch_data ===")

        # init parameters
        rs = requests.Session()
        bac = ''
        max_date =  datetime.datetime.now().strftime('%Y-%m-%d')
        headers = {'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43',
                'x-fb-lsd': 'GoogleBot'}
        data = {'lsd': 'GoogleBot',
                '__a': 'GoogleBot'}

        # redirect to m.facebook
        groupurl = re.sub('www','m', url)
        today = date.today()
        until_date=today.strftime("%Y-%m-%d")
        print(until_date)
        print(max_date)

        # request data and break loop until reach the goal
        data_soup_list = []
        while max_date >= until_date:

            # request params
            params = {
                'bac': bac,
                'multi_permalinks': '',
                'refid': '18'
                }
            resp = rs.post(groupurl, headers=headers, params=params, data=data)
            # print(resp.status_code)
            # print(resp.text)

            resp = re.sub(r'for \(;;\);', '', resp.text)
            try:
                resp = json.loads(resp)
            except:
                print('Error at josn.load stage.')
                return resp

            data_soup = BeautifulSoup(resp['payload']['actions'][0]['html'], "lxml")
            data_soup_list.append(data_soup)
            reactions = re.findall('\(new \(require\("ServerJS"\)\)\(\)\).handle\((.*?)\);', resp['payload']['actions'][2]['code'])[0]
            max_date = max([re.findall('"publish_time":(.*?),', str(time['data-ft']))[0] for time in data_soup.select('section > article')])
            max_date = datetime.datetime.fromtimestamp(int(max_date)).strftime('%Y-%m-%d')
            print(f'TimeStamp: {max_date}.')
            try:
                bac = re.findall('bac=(.*?)%3D', data_soup.select('div > a.primary')[0]['href'])[0]
            except:
                bac = re.findall('bac=(.*?)&', data_soup.select('div > a.primary')[0]['href'])[0]

        return data_soup_list

    def get_data_json(self, data_soup_list):
        break_times = 0
        data_json = []
        for data_soup in data_soup_list:
            try:
                # Parse content
                for post in data_soup.select('section > article'):
                    try:
                        post_group_id = json.loads(post["data-ft"])["page_id"]
                        pattern = r'.*href=\"https:\/\/m.facebook.com\/groups\/(.*?)\/permalink\/.*'
                        post_group_url = "www.facebook.com/groups/" + re.search(pattern, str(post)).group(1)
                        post_group_name = post.find('h3').text
                        post_id = json.loads(post["data-ft"])["mf_story_key"]
                        post_link = "www.facebook.com/" + post_id
                        publish_time = re.search(r'\"publish_time\":(.*?),', str(post)).group(1), # TIME
                        publish_time = int(list(publish_time)[0])
                        post_time = datetime.datetime.fromtimestamp(publish_time).strftime("%Y-%m-%d")
                        content = post.find('div',{'data-ft':'{"tn":"*s"}'}).text # CONTENT
                        img_link = ""
                        try:
                            photo_id = json.loads(post["data-ft"])["photo_id"]
                            img_link = "www.facebook.com/" + photo_id
                        except Exception as error:
                            print(repr(error))

                        data = {
                            "post_group_id": post_group_id,
                            "post_group_url": post_group_url,
                            "post_group_name": post_group_name,
                            "post_link": post_link,
                            "post_time": post_time,
                            "title": "",
                            "sub_title": "",
                            "content": content,
                            "img_link": img_link,
                        }
                        data_json.append(data)
                    except Exception as error:
                        print(repr(error))              
                break_times = 0 # reset break times to zero
            except Exception as error:
                print(repr(error))
                break_times += 1
                print('break_times:', break_times)
                if break_times > 5:
                    return data_soup.select('div > a.primary')[0]['href']
                    # return print('ERROR: Please send the following URL to the author. \n', rs.url)

        return data_json


class yt_CrawlerBySelenium(crawler):
    def __init__(self):
        print("===yt_CrawlerBySelenium init ===")

    # def fetch_data(self,url):
    #     self.get_browser()
    #     data_soup = self.fetch_url_data(url)
    #     # print(data_soup)
    #     return data_soup

    # def get_data_json(self, data_soup):
    #     videos = data_soup.select("#meta #video-title")
    #     for video in videos:
    #         title = video['title']
    #         href = video['href']
            
    #         print(title)
    #         print(href)



class yt_CrawlerByfeeds():
    def __init__(self):
        print("===yt_CrawlerByfeeds init ===")
        # https://www.youtube.com/feeds/videos.xml?channel_id=UCT3uWFvKLVpRnEealmRwvrw

    def fetch_data(self,url):
        channel_id = url.replace("https://www.youtube.com/channel/","")
        feeds_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        response = requests.get(feeds_url)
        data_soup = BeautifulSoup(response.content, 'xml')

        return data_soup

    def get_data_json(self, data_soup):
        data_json = []
        videos = data_soup.select("entry")
        for video in videos:
            video_url = video.find("link")["href"]
            title = video.select_one("title").text
            channel_name = video.select_one("author name").text
            channel_url = video.select_one("author uri").text
            channel_id = video.find("yt:channelId").text
            published = video.select_one("published").text
            img_link = video.find("media:thumbnail")["url"]
            data = {
                "channel_id": channel_id,
                "channel_url": channel_url,
                "channel_name": channel_name,
                "video_url": video_url,
                "published": published,
                "title": title,
                "img_link": img_link
            }
            data_json.append(data)
            print(data)

        return data_json


class yt_CrawlerByScriptbarrel():
    def __init__(self):
        print("===yt_CrawlerByScriptbarrel init ===")
        #  https://www.scriptbarrel.com/xml.cgi?channel_id=UCKPflKAE2Y1tm8VSi32iboQ&name=老孫聊遊戲

    def fetch_data(self,url):
        channel_id = url.replace("https://www.youtube.com/channel/","")
        feeds_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        response = requests.get(feeds_url)
        data_soup = BeautifulSoup(response.content, 'xml')
        video = data_soup.select("entry")[0]
        channel_name = video.select_one("author name").text
        channel_url = video.select_one("author uri").text
        channel_id = video.find("yt:channelId").text
        scriptbarrel_url = f"https://www.scriptbarrel.com/getvids?goods=https%3A%2F%2Fwww.youtube.com%2Fchannel%2F{channel_id}"
        response = requests.get(scriptbarrel_url)
        data_soup = BeautifulSoup(response.content, 'html.parser')

        return [data_soup, channel_name, channel_url, channel_id]

    def get_data_json(self, data):
        data_soup = data[0]
        channel_name = data[1]
        channel_url = data[2]
        channel_id = data[3]

        data_soup_str = str(data_soup)
        video_link_pattern = r'<a href="(.*?)"'
        video_links = re.findall(video_link_pattern, data_soup_str)
        title_pattern = r'<b>Title:<\/b> (.*?)<br\/>'
        titles = re.findall(title_pattern, data_soup_str)
        img_pattern = r'<img src="(.*?)"'
        img_links = re.findall(img_pattern, data_soup_str)
        date_pattern = r'<b>Date:<\/b> (.*?)<br\/>'
        video_dates = re.findall(date_pattern, data_soup_str)

        data_json = []
        cnt_limit = 200
        for i,v in enumerate(video_links):
            video_url = v.replace("http://","https://www.")
            title = titles[i]
            img_link = img_links[i]
            published = video_dates[i]

            data = {
                "channel_name":channel_name,
                "channel_url": channel_url,
                "channel_id": channel_id,
                "video_url": video_url,
                "published": published,
                "title": title,
                "img_link": img_link,
            }
            data_json.append(data)

            if i >= cnt_limit:
                break

        return data_json



