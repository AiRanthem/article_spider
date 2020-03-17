# -*- coding: utf-8 -*-
import time
import re
import json
import pickle

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from ArticleSpider.captcha import ZhihuCnCaptcha, EN_CAP_XPATH, CN_CAP_XPATH, ZhihuEnCaptcha
from ArticleSpider.settings import COOKIES_STORE, ZHIHU_QUESTION_API_TEMPLATE


def drop_argument_from_cookie(args, cookies):
    for cookie in cookies:
        for arg in args:
            if arg in cookie:
                del cookie[arg]
    return cookies


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    invalid_cookie_args = ['sameSite', 'expiry']

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        chrome_option = Options()
        chrome_option.add_argument('--disable-extensions')
        chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browser = webdriver.Chrome(executable_path='driver/chromedriver.exe', options=chrome_option)

    def start_requests(self):
        try:
            cookies = pickle.load(open(COOKIES_STORE + '/zhihu.cookie', 'rb'))
            cookie_dict = {}
            drop_argument_from_cookie(self.invalid_cookie_args, cookies)
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']
                self.browser.add_cookie(cookie)
            self.browser.get(self.start_urls[0])
            if not self.logged_in():
                raise Exception('login failed')
            print("Cookies load succeed.")
            pickle.dump(self.browser.get_cookies(), open(COOKIES_STORE + '/zhihu.cookie', 'wb'))
        except Exception as e:
            print(e)
            cookies = self.login()
            pickle.dump(cookies, open(COOKIES_STORE + '/zhihu.cookie', 'wb'))

        cookie_dict = {}
        drop_argument_from_cookie(self.invalid_cookie_args, cookies)
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]

    def logged_in(self):
        try:
            self.wait_an_element_by_xpath("//a[@title='回答'", 1)
            return True
        except Exception as e:
            print(e)
            return False

    def login(self):
        self.browser.get('https://www.zhihu.com/signin')
        """
        return the cookies after login
        """
        try:
            self.browser.maximize_window()
        except:
            pass
        # open the page
        self.browser.get('https://www.zhihu.com')
        # login with password
        self.browser.execute_script("document.getElementsByClassName('SignFlow-tab')[1].click()")
        # enter username and password
        self.browser.find_element_by_xpath("//input[@name='username']").send_keys(Keys.CONTROL + 'a')
        self.browser.find_element_by_xpath("//input[@name='username']").send_keys('18965150181')
        self.browser.find_element_by_xpath("//input[@name='password']").send_keys(Keys.CONTROL + 'a')
        self.browser.find_element_by_xpath("//input[@name='password']").send_keys('pachong101')
        # login
        time.sleep(0.44)
        self.browser.execute_script(
            "document.getElementsByClassName('Button SignFlow-submitButton Button--primary Button--blue')[0].click()")

        # catch the captcha
        cap_container = self.wait_an_element_by_xpath(
            xpath="//div[contains(@class,'Captcha SignFlow-captchaContainer')]", timeout=1.5)
        if cap_container:
            cap = None
            try:
                cap = ZhihuEnCaptcha(self.parse_captcha(EN_CAP_XPATH))
            except Exception as e:
                print(e)
                try:
                    cap = ZhihuCnCaptcha(self.parse_captcha(CN_CAP_XPATH))
                except Exception as e:
                    print(e)
                    cap = None
            if cap:
                cap.process(browser=self.browser)

        # return self.browser.get_cookies()
        input('after logged in, press Enter')
        return self.browser.get_cookies()

    def wait_an_element_by_xpath(self, xpath, timeout):
        try:
            element = WebDriverWait(self.browser, timeout).until(
                lambda driver: driver.find_element_by_xpath(xpath)
            )
            return element
        except Exception as e:
            print(e)
            return None

    def parse_captcha(self, xpath):
        while True:
            src = self.browser.find_element_by_xpath(xpath).get_attribute('src')
            if not src.endswith('null'):
                break
        return src

    def parse(self, response):
        urls = response.xpath("//a/@href").extract()
        urls = [url for url in urls if url.startswith('/question')]

        for url in urls:
            match = re.match('/question/(\d+).*', url)
            if match:
                qid = match.group(1)
                yield scrapy.Request(
                    url=ZHIHU_QUESTION_API_TEMPLATE.format(qid),
                    callback=self.parse_question,
                    meta={'question': qid}
                )

    def parse_question(self, response):
        data = json.loads(response.text)
        qid = response.meta.get('question')
        match = re.match('.*offset=(\d+)&.*', response.url)
        offset = 'UNKNOWN'
        if match:
            offset = match.group(1)

        d = data['data']

        with open('zhihu_json_data/{}_{}.json'.format(qid, offset), 'w', encoding='utf-8') as f:
            json.dump(data['data'], f, ensure_ascii=False)

        if not data['paging']['is_end'] and int(offset) < 51:
            yield scrapy.Request(
                url=data['paging']['next'],
                callback=self.parse_question,
                meta={'question': qid}
            )
