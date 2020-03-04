# -*- coding: utf-8 -*-
from urllib import parse
import re
import json

import scrapy
import requests

from ArticleSpider.items import CNBlogArticleItem
class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']

    def parse(self, response):
        ### 获得封面和文章url
        content_blocks = response.xpath("//div[@class='content']")
        # todo 修改迭代次数，去掉注释
        for block in content_blocks[:1]:
            detail_url = block.xpath("h2/a/@href").extract_first()
            image_url = block.xpath("div[@class='entry_summary']/a/img/@src").extract_first()
            yield scrapy.Request(
                url=parse.urljoin(response.url,detail_url), 
                callback=self.parse_detail, 
                meta={"front_image_url":image_url}
            )
        
        # next_path = response.xpath("//a[contains(text(), 'Next >')]/@href").extract_first()
        # yield scrapy.Request(url=parse.urljoin(response.url, next_path), callback=self.parse)

    def parse_detail(self, response):
        '''对新闻详情页面进行信息解析'''
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            # create an item
            item = CNBlogArticleItem()

            # id
            post_id = match_re.group(1)
            item["post_id"] = post_id
            # title
            title = response.xpath("//div[@id='news_title']/a/text()").extract_first()
            item["title"] = title
            # time
            time_match = re.match('.*?(\d+.*)', response.xpath("//span[@class='time']/text()").extract_first())
            if time_match:
                create_time = time_match.group(1)
            else:
                create_time = ''
            item["create_time"] = create_time
            # content
            content = response.xpath("//div[@id='news_body']").extract_first()
            item["content"] = content
            # tags
            tags = ",".join(response.xpath("//div[@class='news_tags']/a/text()").extract())
            item["tags"] = tags

            item["front_image_url"] = response.meta.get("front_image_url","")
            # extra
            yield scrapy.FormRequest(
                url = parse.urljoin(response.url,"/NewsAjax/GetAjaxNewsInfo"),
                callback = self.parse_extra_info, 
                meta = {
                    'post_id' : post_id,
                    "item" : item
                },
                formdata={'contentId':post_id},
                method='GET'
            )
            pass
        
    def parse_extra_info(self, response):
        '''对新闻详情页面的ajax数据进行解析'''
        item = response.meta.get("item","")
        extraDict = json.loads(response.text)
        commentCount = extraDict['CommentCount']
        totalView = extraDict['TotalView']
        pass