import os
import datetime
from datetime import date
from time import sleep
from unittest import case
from random import randrange


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


class CrawlerWorker():
    def __int__(self):
        pass

    def get_crawler(self, web_name):
        switcher = {
            "leju": lejuCrawler,
            "591": _591_Crawler,
            "fb": fb_Crawler,
            "fb-private": fb_private_Crawler,
            "fb_Crawler_by_facebook_scraper": fb_Crawler_by_facebook_scraper,
            "fb_GoupCrawlerByRequests": fb_GoupCrawlerByRequests,
            "YtApiCrawler": YtApiCrawler,
            "YtCrawlerByfeeds": YtCrawlerByfeeds,
            "yt_CrawlerByScriptbarrel": yt_CrawlerByScriptbarrel,
            "YtCrawlerInPlaylist": YtCrawlerInPlaylist,
            "notion-youtube": YtCrawlerByfeeds,
            "notion-FB": fb_Crawler_by_facebook_scraper,
        }
        return switcher.get(web_name, lambda: "")()

    def get_crawled_data_list(self, web_name, to_crawl_url_list):
        crawler = self.get_crawler(web_name)
        crawled_data_list = []
        for url in to_crawl_url_list:
            try:
                data = crawler.fetch_data(url)
                data_list_json = crawler.get_data_json(data)
                data_list_json_encode = json.dumps(data_list_json, ensure_ascii=False).encode('utf8')
                data_list = json.loads(data_list_json_encode)
                crawled_data_list += data_list
                sleep(randrange(10))
            except Exception as error:
                print(f"fetch fail:{url}")
                print(repr(error))

        return crawled_data_list

class SeleniumEngine:
    def __init__(self):
        # user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument('--disable-dev-shm-usage')
        # chrome_options.add_argument('--single-process')
        # chrome_options.add_argument(f'user-agent={user_agent}')
        # chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        # chrome_options.add_argument("--disable-blink-features");
        # chrome_options.add_argument("--disable-blink-features=AutomationControlled");

        # is_AWS = os.environ['is_AWS']

        # ChromeDriverManager
        # chrome_options.binary_location = '/opt/headless-chromium'
        # self.browser = webdriver.Chrome('/opt/chromedriver',options=chrome_options)
        self.browser = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)


class SeleniumCrawler:
    def __init__(self):
        print("===crawler init ===")
        self.browser = None

    def get_browser(self):
        engine = SeleniumEngine()
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

    def login_to_FB(self, email,pwd):
        browser = self.browser
        browser.get("http://www.facebook.com")
        username = browser.find_element_by_id("email")
        password = browser.find_element_by_id("pass")
        submit = browser.find_element(by=By.CSS_SELECTOR, value='button[name="login"]')
        sleep(1)
        username.send_keys(email)
        sleep(1)
        password.send_keys(pwd)
        sleep(1)
        submit.click()
        sleep(10)

    def login_to_LearnMode(self, email, pwd):
        browser = self.browser
        browser.get("https://www.learnmode.net/login")
        sleep(3)
        user_selector = '.account-input-div input'
        user_element = browser.find_element(by=By.CSS_SELECTOR, value=user_selector)
        password_selector = '.password-input-div input'
        password_element = browser.find_element(by=By.CSS_SELECTOR, value=password_selector)
        submit_selector = '#loginModal .user-input-block .main-btn-div button'
        submit_element = browser.find_element(by=By.CSS_SELECTOR, value=submit_selector)
        sleep(1)
        user_element.send_keys(email)
        sleep(1)
        password_element.send_keys(pwd)
        sleep(1)
        submit_element.click()
        sleep(10)

    def save_cookies_to_json(self, file_name):
        browser = self.browser
        cookies = browser.get_cookies()
        json_object = json.dumps(cookies)
        file = open(file_name, "w")
        file.write(json_object)
        file.close()

    def quit_browser(self):
        browser = self.browser
        browser.quit()


class lejuCrawler(SeleniumCrawler):
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
           
    def get_data_json(self, data):
        ext_url = data[1]
        data_soup = data[0]
        title = data_soup.find('title').string
        items = data_soup.select('#sale-objects-wrap .border-grey-3')
        sale_items = []
        for idx, item in enumerate(items):
            floor = item.select_one(".text-16px").text
            name = item.select_one(".title-width").text.replace("\n","").strip()
            link = ext_url[idx]
            price = item.select(".items-baseline")[0].select('span')[0].text.replace("\n","").strip()
            area = item.select(".items-baseline")[1].select('span')[0].text.replace("\n","").strip()
            
            item_data = {
                'title': title,
                'floor': floor,
                'name': name,
                'link': link,
                'price': price,
                'area': area,
            }
            sale_items.append(item_data)
 
        return sale_items

class _591_Crawler(SeleniumCrawler):
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

class fb_Crawler(SeleniumCrawler):
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
        # # selector params for www.
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

            except Exception as error:
                print(repr(error))

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
        current_path = current_path = os.getcwd()
        fb_secret_name = "fb_secret.json"
        data_path = current_path + "/" + fb_secret_name
        file = open(data_path)
        file_dict = json.load(file)
        email = file_dict["email"]
        pwd = file_dict["pwd"]
        selenium_crawler = SeleniumCrawler()
        selenium_crawler.get_browser()
        selenium_crawler.login_to_FB(email,pwd)
        cookies_file_name = "fb_cookies.json"
        selenium_crawler.save_cookies_to_json(cookies_file_name)
        selenium_crawler.quit_browser()

    def fetch_data(self,url):
        current_path = os.getcwd()
        cookie_path = current_path + "/fb_cookies.json"
        if "groups" in url:
            group_id = url.split("/")[-1]
            posts = get_posts(group=group_id, pages=1,cookies=cookie_path)
            group_info = get_group_info(group_id)
            post_group_id = group_info['id']
            post_group_url = "www.facebook.com/groups/" + group_id
            post_group_name = group_info['name']
        else:
            group_id = url.split("/")[-1]
            posts = get_posts(group_id, pages=1, cookies=cookie_path)
            post_group_id = group_id
            post_group_url = "www.facebook.com/" + group_id
            res= requests.get(url).text
            data_soup = BeautifulSoup(res, 'html.parser')
            post_group_name = data_soup.select_one("title").text

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
            title = post['text'][:50]
            content = post['text']
            
            if post['time']:
                post_time = str(post['time']).split()[0]
            else:
                post_time = date.today().strftime("%Y-%m-%d")

            tag_pattern = r'\#(.*?)[ |\n]|【(.*?)】|《(.*?)》|「(.*?)」'
            tag_tuple_list = re.findall(tag_pattern, post['text'] + " ")
            tag_list = []
            for tag_tuple in tag_tuple_list:
                tag_list += list(tag_tuple)
                tag_list = list(set(tag_list))
            if '' in tag_list:
                tag_list.remove('')

            post_link = "www.facebook.com/" + post['post_id']
            img_link = post['image']
            data = {
                'post_group_id': post_group_id,
                'post_group_url': post_group_url,
                'post_group_name': post_group_name,
                'post_link': post_link,
                'post_time': post_time,
                "title": title,
                "sub_title": "",
                'content': content,
                'img_link': img_link,
                'tag_list': tag_list
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
                        post_group_url = "https://www.facebook.com/groups/" + re.search(pattern, str(post)).group(1)
                        post_group_name = post.find('h3').text
                        post_id = json.loads(post["data-ft"])["mf_story_key"]
                        post_link = "https://www.facebook.com/" + post_id
                        publish_time = re.search(r'\"publish_time\":(.*?),', str(post)).group(1) # TIME
                        publish_time = int(publish_time)
                        post_time = datetime.datetime.fromtimestamp(publish_time).strftime("%Y-%m-%d")
                        content = post.find('div',{'data-ft':'{"tn":"*s"}'}).text # CONTENT
                        img_link = ""
                        # try:
                        #     photo_id = json.loads(post["data-ft"])["photo_id"]
                        #     img_link = "www.facebook.com/" + photo_id
                        # except Exception as error:
                        #     print(repr(error))
                        try:
                            pattern = r'href="\/photo\.php\?fbid=(.*?)&'
                            photo_id = re.search(pattern, str(post)).group(1)
                            img_link = "www.facebook.com/" + photo_id
                        except Exception as error:
                            print(repr(error))

                        data = {
                            "post_group_id": post_group_id,
                            "post_group_url": post_group_url,
                            "post_group_name": post_group_name,
                            "post_link": post_link,
                            "post_time": post_time,
                            "title": content[:50] + "...",
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


class YtApiUtil:
    def __init__(self):
        current_path = current_path = os.getcwd()
        youtube_key_name = "youtube_key.json"
        data_path = current_path + "/" + youtube_key_name
        file = open(data_path)
        file_dict = json.load(file)
        self.API_key = file_dict["API_key"]
        
    def get_all_playlists(self, channel_id, page_token=""):
        API_key = self.API_key
        url = f"https://youtube.googleapis.com/youtube/v3/playlists?part=contentDetails&part=snippet&part=id&channelId={channel_id}&maxResults=50&key={API_key}&pageToken={page_token}"
        resp = requests.get(url)
        
        return json.loads(resp.text)
    
    def get_all_playlist_items(self, playlist_id, page_token=""):
        API_key = self.API_key
        url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet&part=contentDetails&maxResults=50&playlistId={playlist_id}&key={API_key}&pageToken={page_token}"
        resp = requests.get(url)
        
        return json.loads(resp.text)
    
    def get_video_info(self, video_id):
        API_key = self.API_key
        url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&id={video_id}&key={API_key}"
        resp = requests.get(url)
        
        try:
            video_info = json.loads(resp.text)["items"][0]
        except:
            video_info = None
        
        return video_info
        
class YtApiCrawler(YtApiUtil):
    def __init__(self):
        print("===YtApiCrawler init ===")
        super().__init__()

    def fetch_data(self, url):
        print("===YtApiCrawler fetch_data ===")
        channel_id = url.replace("https://www.youtube.com/channel/","")
        playlists = []
        page_token = ""
        has_next_page = True
        while has_next_page:
            all_playlists = self.get_all_playlists(channel_id, page_token)
            playlists += all_playlists["items"]
            if "nextPageToken" in all_playlists:
                page_token = all_playlists["nextPageToken"]
            else:
                has_next_page = False

        playlist_list = []
        for item in playlists:
            channel_id = item["snippet"]["channelId"]
            channel_name = item["snippet"]["channelTitle"]
            channel_url = url
            playlist_id = item["id"]
            playlist_title = item["snippet"]["title"]

            data = {
                "channel_id": channel_id,
                "channel_name": channel_name,
                "channel_url": channel_url,
                "playlist_id": playlist_id,
                "playlist_title": playlist_title,
                "video_items": []
            }

            playlist_list.append(data)

        playlist_items_list = []
        for playlist_dict in playlist_list:
            playlist_id = playlist_dict["playlist_id"]
            page_token = ""
            has_next_page = True
            while has_next_page:
                playlist_items = self.get_all_playlist_items(playlist_id, page_token)
                playlist_dict["video_items"] += playlist_items["items"]
                if "nextPageToken" in playlist_items:
                    page_token = playlist_items["nextPageToken"]
                else:
                    has_next_page = False
            playlist_items_list.append(playlist_dict)

        return playlist_items_list

    def get_data_json(self, playlist_items_list):
        data_json = []
        for playlist_dict in playlist_items_list:
            for item in playlist_dict["video_items"]:
                video_id = item["snippet"]["resourceId"]["videoId"]
                video_info = self.get_video_info(video_id)
                if video_info:
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    published = item["snippet"]["publishedAt"].split("T")[0]
                    title = item["snippet"]["title"]
                    description = item["snippet"]["description"]
                    playlist_position = int(item["snippet"]["position"]) +1
                    
                    if "standard" in item["snippet"]["thumbnails"]:
                        img_link = item["snippet"]["thumbnails"]["standard"]["url"] 
                    else: 
                        img_link = ""

                    if "tags" in video_info["snippet"]:
                        tag_list = video_info["snippet"]["tags"]
                    else:
                        tag_list = []

                    channel_id = playlist_dict["channel_id"]
                    channel_url = playlist_dict["channel_url"]
                    channel_name = playlist_dict["channel_name"]
                    playlist_id = playlist_dict["playlist_id"]
                    playlist_title = playlist_dict["playlist_title"]
                    
                    data = {
                        "channel_id": channel_id,
                        "channel_url": channel_url,
                        "channel_name": channel_name,
                        "video_id": video_id,
                        "video_url": video_url,
                        "published": published,
                        "title": title,
                        "img_link": img_link,
                        "description": description,
                        "tag_list": tag_list,
                        "playlist_id": playlist_id,
                        "playlist_title": playlist_title,
                        "playlist_position": playlist_position
                    }
                    data_json.append(data)
                    print(data)
        
        return data_json

class YoutubeRequestsCrawler:
    def __init__(self):
        print("===crawler init ===")

    def get_yt_playlist_with_video(self, url, channel_name):
        resp = requests.get(url)
        data_soup = BeautifulSoup(resp.text, 'html.parser')
        video_title = data_soup.select_one('meta[name="title"]')["content"]
        query_url = f"https://www.youtube.com/results?sp=mAEB&search_query={video_title}+{channel_name}"
        resp = requests.get(query_url)
        data_soup = BeautifulSoup(resp.text, 'html.parser')
        data_soup_str = str(data_soup)
        
        try:
            playlist_pattern = r'{"playlistRenderer":{"playlistId":"(.*?)"'
            playlist_id = re.findall(playlist_pattern, data_soup_str)[0]
        except:
            playlist_id = ""
            
        if playlist_id:
            video_id = url.replace("https://www.youtube.com/watch?v=","")
            query_url = f"https://www.youtube.com/watch?v={video_id}&list={playlist_id}"
            resp = requests.get(query_url)
            data_soup = BeautifulSoup(resp.text, 'html.parser')
            data_soup_str = str(data_soup)
            index_pattern = f'{video_id}.*index=(.*?)\"'
            playlist_position = re.findall(index_pattern, data_soup_str)[0]
        else:
            playlist_position = ""

        data = {
            "playlist_id": playlist_id,
            "playlist_position": playlist_position
        }
        
        return data
    def get_yt_channel_info(self, channel_id):
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        resp = requests.get(url)
        data_soup = BeautifulSoup(resp.content, 'xml')
        channel_name = data_soup.select_one("feed > title").text
        channel_url = data_soup.select_one('feed > link[rel="alternate"]')["href"]
        channel_feeds_url = url
        channel_author_name = data_soup.select_one('author > name').text
        channel_published = data_soup.select_one('feed > published').text

        channel_data = {
            "channel_id": channel_id,
            "channel_name": channel_name,
            "channel_url": channel_url,
            "channel_author_name": channel_author_name,
            "channel_feeds_url": channel_feeds_url,
            "channel_published": channel_published
        }
        
        return channel_data

    def get_yt_playlist_info(self, playlist_id):
        url = f"https://www.youtube.com/watch?v=&list={playlist_id}"
        resp = requests.get(url)
        data_soup = BeautifulSoup(resp.text, 'html.parser')
        data_soup_str = str(data_soup)
        playlist_title_pattern = r'"titleText":{"runs":\[{"text":"(.*?)"'
        playlist_title = re.findall(playlist_title_pattern, data_soup_str)[0]
        
        playlist_data = {
            "playlist_id": playlist_id,
            "playlist_title": playlist_title
        }
        
        return playlist_data

class YtCrawlerByfeeds():
    def __init__(self):
        print("===YtCrawlerByfeeds init ===")
        # https://www.youtube.com/feeds/videos.xml?channel_id=UCo4ie5g9_uat5pjWt2DgCKA

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
            video_id = video.find("yt:videoId").text
            title = video.select_one("title").text
            channel_name = video.select_one("author name").text
            channel_url = video.select_one("author uri").text
            channel_id = video.find("yt:channelId").text
            published = video.select_one("published").text.split("T")[0]
            img_link = video.find("media:thumbnail")["url"]
            description = video.find("media:description").text
            tag_pattern = r'\#(.*?) '
            tag_list = re.findall(tag_pattern, title + " " + description)

            try:
                req_crawler = YoutubeRequestsCrawler()
                data = req_crawler.get_yt_playlist_with_video(video_url,channel_name)
                playlist_id = data["playlist_id"]
                playlist_position = data["playlist_position"]
                playlist_title = req_crawler.get_yt_playlist_info(playlist_id)["playlist_title"]
            except:
                playlist_id = ""
                playlist_title = ""

            data = {
                "channel_id": channel_id,
                "channel_url": channel_url,
                "channel_name": channel_name,
                "video_id": video_id,
                "video_url": video_url,
                "published": published,
                "title": title,
                "img_link": img_link,
                "description": description,
                "tag_list": tag_list,
                "playlist_id": playlist_id,
                "playlist_title": playlist_title,
                "playlist_position": playlist_position
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
        data_soup_str = data_soup_str.replace("\n</div>\n","<hr/>")
        video_link_pattern = r'<a href="(.*?)"'
        video_links = re.findall(video_link_pattern, data_soup_str)
        title_pattern = r'<b>Title:<\/b> (.*?)<br\/>'
        titles = re.findall(title_pattern, data_soup_str)
        img_pattern = r'<img src="(.*?)"'
        img_links = re.findall(img_pattern, data_soup_str)
        date_pattern = r'<b>Date:<\/b> (.*?)<br\/>'
        video_dates = re.findall(date_pattern, data_soup_str)
        description_pattern = r'<b>Description:<\/b> (.*?)(<hr\/>|\\n</div>)'
        descriptions = re.findall(description_pattern, data_soup_str)
        data_json = []
        cnt_limit = 200

        for i, v in enumerate(video_links):
            video_url = v.replace("http://","https://www.")
            video_id_pattern = r'.*\?v\=(.*)'
            video_id = re.findall(video_id_pattern, v)[0]
            title = titles[i]
            img_link = img_links[i]
            published = video_dates[i]
            description = ''.join(descriptions[i]).replace("<br/>","\n")
            tag_pattern = r'\#(.*?) '
            tag_list = re.findall(tag_pattern,''.join(title) + " " + description)

            try:
                req_crawler = YoutubeRequestsCrawler()
                data = req_crawler.get_yt_playlist_with_video(video_url,channel_name)
                playlist_id = data["playlist_id"]
                playlist_position = data["playlist_position"]
                playlist_title = req_crawler.get_yt_playlist_info(playlist_id)
            except:
                playlist_id = ""
                playlist_title = ""

            data = {
                "channel_name":channel_name,
                "channel_url": channel_url,
                "channel_id": channel_id,
                "video_id": video_id,
                "video_url": video_url,
                "published": published,
                "title": title,
                "img_link": img_link,
                "description": description,
                "tag_list": tag_list,
                "playlist_id": playlist_id,
                "playlist_title": playlist_title,
                "playlist_position": playlist_position
            }
            data_json.append(data)

            if i >= cnt_limit:
                break

        return data_json

class YtCrawlerInPlaylist():
    # TODO: 善用 API
    def __init__(self):
        print("===YtCrawlerInPlaylist init ===")

    def fetch_data(self, url):
        print("===YtCrawlerInPlaylist fetch_data ===")

        playlists_url = f"{url}/playlists"
        resp = requests.get(playlists_url)
        data_soup = BeautifulSoup(resp.text, 'html.parser')
        channel_url = url
        channel_name = data_soup.select_one('link[itemprop="name"]')["content"]
        channel_id = url.replace("https://www.youtube.com/channel/","")
        playlistId_pattern = r'playlistId":"(.*?)",'
        playlistId_list = re.findall(playlistId_pattern, resp.text)
        playlistId_list = list(set(playlistId_list))
        data_dict_list = []

        for playlist_id in playlistId_list:
            yt_list_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            resp = requests.get(yt_list_url)
            data_soup = BeautifulSoup(resp.text, 'html.parser')
            playlist_title = data_soup.select_one('meta[property="og:title"]')["content"]
            videoId_pattern = r'"videoId":"(.*?)",'
            videoId_list = re.findall(videoId_pattern, resp.text)
            video_id_list = list(set(videoId_list))
            print(video_id_list)

            for video_id in video_id_list:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                print(video_url)
                resp = requests.get(video_url)
                data_soup = BeautifulSoup(resp.text, 'html.parser')
                data_dict = {
                    "channel_name": channel_name,
                    "channel_url": channel_url,
                    "channel_id": channel_id,
                    "playlist_id": playlist_id,
                    "playlist_title": playlist_title,
                    "data_soup": data_soup
                }
                data_dict_list.append(data_dict)

        return data_dict_list
        
    def get_data_json(self, data_dict_list):
        data_json = []

        for data_dict in data_dict_list:
            channel_name = data_dict["channel_name"]
            channel_url = data_dict["channel_url"]
            channel_id = data_dict["channel_id"]
            playlist_id = data_dict['playlist_id']
            data_soup = data_dict["data_soup"]
            video_id = data_soup.select_one('meta[itemprop="videoId"]')["content"]
            video_url = data_soup.select_one('[name="twitter:url"]')["content"]
            published = data_soup.select_one('meta[itemprop="uploadDate"]')["content"]
            title = data_soup.select_one('meta[itemprop="name"]')["content"]
            img_link = data_soup.select_one('link[itemprop="thumbnailUrl"]')["href"]
            description = data_soup.select_one('meta[itemprop="description"]')["content"]
            playlist_id = data_dict["playlist_id"]
            playlist_title = data_dict["playlist_title"]
            
            try:
                tag_pattern = r'"shortDescription":"(#.*?)\\n'
                data_soup_str = str(data_soup)
                tag_list = re.findall(tag_pattern, data_soup_str)[0]
                tag_list = tag_list.split("#")
                tag_list.remove("")
            except:
                tag_list = []

            data = {
                "channel_name":channel_name,
                "channel_url": channel_url,
                "channel_id": channel_id,
                "video_id": video_id,
                "video_url": video_url,
                "published": published,
                "title": title,
                "img_link": img_link,
                "description": description,
                "tag_list": tag_list,
                "playlist_id": playlist_id,
                "playlist_title": playlist_title,
                "playlist_position": ""
            }
            data_json.append(data)
            print(data)

        return data_json

class LearnModeCrawler(SeleniumCrawler):    
    def __init__(self):
        print("===LearnModeCrawler init ===")

    def fetch_data(self, url):
        self.get_browser()
        email = "purpleice9765@msn.com"
        pw = "learnmode9765"
        self.login_to_LearnMode(email, pw)
        data_soup = self.fetch_url_data(url)
        self.quit_browser()

        return data_soup

    def fetch_url_data(self, url):
        print(f"===fetch:{url}===")
        browser = self.browser
        browser.get(url)
        sleep(5)

        chapter_items = browser.find_elements(by=By.CSS_SELECTOR, value=".chapter-item")
        del chapter_items[0]

        for chap in chapter_items:
            chap.click()
            sleep(1)

        chapter_name_list = []
        names = browser.find_elements(by=By.CSS_SELECTOR, value=".chapter-name")
        for n in names:
            chapter_name_list.append(n.text)
        del chapter_name_list[0]


        resources = browser.find_elements(by=By.CSS_SELECTOR, value='.resource-list')
        content_link_list = []
        for resource in resources:
            link_list = []
            links = resource.find_elements(by=By.CSS_SELECTOR, value="a")
            for link_ele in links:
                link = link_ele.get_attribute("href")
                link_list.append(link)
            content_link_list.append(link_list)
        del content_link_list[0]

        content_data_soup_list = []
        for urls in content_link_list:
            content_link_data_soup = []
            for _url in urls:
                print(_url)
                browser.get(_url)
                sleep(5)
                data_soup = BeautifulSoup(browser.page_source, 'html.parser')
                content_link_data_soup.append(data_soup)

            content_data_soup_list.append(content_link_data_soup)
        print(f"===fetch:{url} done===")
        
        return [chapter_name_list, content_data_soup_list]
    
    def get_attachment_data(self, url):
        self.get_browser()
        email = "purpleice9765@msn.com"
        pw = "learnmode9765"
        self.login_to_LearnMode(email, pw)
        browser = self.browser
        browser.get(url)
        sleep(5)
        file_items = browser.find_elements(by=By.CSS_SELECTOR, value=".file-item")
        file_items_num = len(file_items)
        attachment_list = []
        for i in range(file_items_num):
            file_items = browser.find_elements(by=By.CSS_SELECTOR, value=".file-item")
            print(i)
            file_name = file_items[i].text
            print(file_name)
            file_items[i].click()
            sleep(1)
            img_modal = browser.find_elements(by=By.CSS_SELECTOR, value=".modal.show")
            is_img = len(img_modal) > 0 
            if is_img:
                link_selector = browser.find_elements(by=By.CSS_SELECTOR, value=".modal.show img")[0]
                file_link = link_selector.get_attribute('src')
                browser.refresh();
                sleep(3)
            else:
                network = browser.execute_script("var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;")
                file_link = network[-1]["name"]

            attachment_data = {
                "file_name": file_name,
                "file_link": file_link
            }
            attachment_list.append(attachment_data)

        self.quit_browser()
        return attachment_list

    def get_data_json(self, data):
        chapter_name_list = data[0]
        content_data_soup_list = data[1]
        data_json = []

        for i, data_soups in enumerate(content_data_soup_list):
            chapter_data = {}
            chapter_data["chapter_name"] = chapter_name_list[i]
            chapter_data["chapter_index"] = i
            chapter_data["chapter_content"] = []
            
            for data_soup in data_soups:                
                try:
                    title_selector = ".title-wrapper .title-text"
                    title = data_soup.select_one(title_selector).text
                except:
                    title_selector = ".title-lg"
                    title = data_soup.select_one(title_selector).text

                try:
                    link_selector = ".resource-item.active"
                    link = data_soup.select_one(link_selector)['href']
                except:
                    link_selector = ".nav-item-section.selected a"
                    link = data_soup.select_one(link_selector)['href']

                pattern = r'\/course\/.*?\/.*?\/(.*?)\/'
                link_type = re.findall(pattern, link)[0]

                content_link = ""
                attachment = []
                if link_type == "video":
                    iframe_src = data_soup.select_one("iframe")['src']
                    pattern = r"embed\/(.*?)\?"
                    youtube_id = re.findall(pattern, iframe_src)[0]
                    content_link = f"https://www.youtube.com/watch?v={youtube_id}"
                elif link_type == "hyperlink":
                    content_link_selector = ".hyperlink .content a"
                    content_link = data_soup.select_one(content_link_selector)['href']
                elif link_type == "book":
                    content_link_selector = "iframe.pdf-reader"
                    content_link = data_soup.select_one(content_link_selector)['src']
                elif link_type == "homework":
                    url = "https://www.learnmode.net" + link
                    attachment = self.get_attachment_data(url)

                content_data = {
                    "title": title,
                    "link": link,
                    "link_type": link_type,
                    "content_link": content_link,
                    "attachment": attachment
                }
                
                chapter_data["chapter_content"].append(content_data)

            data_json.append(chapter_data)
        print(data_json)
                                
        return data_json

    def save_file(self, data_json):
        json_string =json.dumps(data_json)
        current_path = current_path = os.getcwd()
        data_path = current_path + "/learmode_data.json"
        # Directly from dictionary
        with open(data_path, 'w') as outfile:
            json.dump(json_string, outfile)
        
        # Using a JSON string
        with open(data_path, 'w') as outfile:
            outfile.write(json_string)