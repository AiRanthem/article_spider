# -*- coding: utf-8 -*-
import pickle
import os

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver

from ArticleSpider.config import LAGOU_PASSWD,LAGOU_PHONE
from ArticleSpider.settings import COOKIES_STORE


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    _cookie_path = COOKIES_STORE + '/lagou.cookie'

    rules = (
        Rule(LinkExtractor(allow=(r"zhaopin/.*", r"gongsi/j\d+\.html")), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+\.html'), callback='parse_job', follow=True),
    )

    def parse_job(self, response):
        """
        解析拉勾网的职位数据
        """
        item = {}
        #item['domain_id'] = response.xpath('//input[@id="sid"]/@value').get()
        #item['name'] = response.xpath('//div[@id="name"]').get()
        #item['description'] = response.xpath('//div[@id="description"]').get()
        return item

    def start_requests(self):
        # take cookies from file 'lagou.cookie'
        cookies = {}
        if os.path.exists(self._cookie_path):
            cookies = pickle.load(open(self._cookie_path, 'rb'))

        browser = webdriver.Chrome(executable_path="driver/chromedriver.exe")
        browser.get("https://passport.lagou.com/login/login.html")
        browser.find_element_by_xpath("//div[@class='form_body']//input[@type='text']").send_keys(LAGOU_PHONE)
        browser.find_element_by_xpath("//div[@class='form_body']//input[@type='password']").send_keys(LAGOU_PASSWD)
        browser.find_element_by_xpath("//div[@class='form_body']//input[@type='submit']").click()

        cookies = browser.get_cookies()
        pickle.dump(cookies, open(self._cookie_path, 'wb'))




