# -*- coding: utf-8 -*-
import time

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pickle

from ArticleSpider.settings import COOKIES_STORE

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    def start_requests(self):
        cookies = pickle.load(open(COOKIES_STORE+'/zhihu.cookie', 'rb'))
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        browser = webdriver.Chrome()
        # chrome_option = Options()
        # chrome_option.add_argument('--disable-extensions')
        # chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        # browser = webdriver.Chrome(options=chrome_option)
        # open the page
        browser.get('https://www.zhihu.com')
        # # login with password
        # browser.execute_script("document.getElementsByClassName('SignFlow-tab')[1].click()")
        # # enter username and password
        # browser.find_element_by_xpath("//input[@name='username']").send_keys(Keys.CONTROL + 'a')
        # browser.find_element_by_xpath("//input[@name='username']").send_keys('18965150181')
        # browser.find_element_by_xpath("//input[@name='password']").send_keys(Keys.CONTROL + 'a')
        # browser.find_element_by_xpath("//input[@name='password']").send_keys('pachong101')
        # # todo take off the captcha
        # # login
        # browser.execute_script(
        #     "document.getElementsByClassName('Button SignFlow-submitButton Button--primary Button--blue')[0].click()")

        # cookies = browser.get_cookies()
        #
        # pickle.dump(cookies, open(COOKIES_STORE+'/zhihu.cookie', 'wb'))
        #
        # cookie_dict = {}
        # for cookie in cookies:
        #     cookie_dict[cookie['name']] = cookie['value']

        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]

    def parse(self, response):
        pass
