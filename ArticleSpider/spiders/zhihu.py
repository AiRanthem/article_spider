# -*- coding: utf-8 -*-
import time

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pickle

from selenium.webdriver.support.wait import WebDriverWait

from ArticleSpider.captcha import ZhihuCnCaptcha, EN_CAP_XPATH, CN_CAP_XPATH, ZhihuEnCaptcha
from ArticleSpider.settings import COOKIES_STORE


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        chrome_option = Options()
        chrome_option.add_argument('--disable-extensions')
        chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browser = webdriver.Chrome(executable_path='driver/chromedriver.exe', options=chrome_option)

    def start_requests(self):
        # cookies = pickle.load(open(COOKIES_STORE+'/zhihu.cookie', 'rb'))
        # cookie_dict = {}
        # for cookie in cookies:
        #     cookie_dict[cookie['name']] = cookie['value']
        # browser = webdriver.Chrome()
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
        # todo take off the captcha
        # login
        time.sleep(1.1)
        self.browser.execute_script(
            "document.getElementsByClassName('Button SignFlow-submitButton Button--primary Button--blue')[0].click()")

        # catch the captcha
        cap_container = self.wait_an_element_by_xpath(
            xpath="//div[contains(@class,'Captcha SignFlow-captchaContainer')]", timeout=1.5)
        if cap_container:
            cap = None
            try:
                cap = ZhihuEnCaptcha(self.parse_captcha(EN_CAP_XPATH))
            except:
                try:
                    cap = ZhihuCnCaptcha(self.parse_captcha(CN_CAP_XPATH))
                except Exception as e:
                    print(e)
                    cap = None
            if cap:
                cap.process(browser=self.browser)




        # cookies = browser.get_cookies()
        #
        # pickle.dump(cookies, open(COOKIES_STORE+'/zhihu.cookie', 'wb'))
        #
        # cookie_dict = {}
        # for cookie in cookies:
        #     cookie_dict[cookie['name']] = cookie['value']

        return [scrapy.Request(url=self.start_urls[0], dont_filter=True)]

    def parse(self, response):
        pass

    def wait_an_element_by_xpath(self, xpath, timeout):
        try:
            element = WebDriverWait(self.browser, timeout).until(
                lambda driver: driver.find_element_by_xpath(xpath)
            )
            return element
        except Exception as e:
            return None

    def parse_captcha(self, xpath):
        while True:
            src = self.browser.find_element_by_xpath(xpath).get_attribute('src')
            if not src.endswith('null'):
                break
        return src
