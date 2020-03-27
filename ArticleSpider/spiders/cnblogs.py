# -*- coding: utf-8 -*-
from urllib import parse
import re
import json

import scrapy
from ArticleSpider.items import CNBlogArticleItem


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']

    def parse(self, response):
        # 出口
        page = response.meta.get("page_no", None)
        if not page:
            page = 1
        if page > 3:
            return
        ### 获得封面和文章url
        content_blocks = response.xpath("//div[@class='content']")

        for block in content_blocks:
            detail_url = block.xpath("h2/a/@href").extract_first()
            image_url = block.xpath("div[@class='entry_summary']/a/img/@src").extract_first()
            if image_url and image_url.startswith('/'):
                image_url = 'https:' + image_url
            yield scrapy.Request(
                url=parse.urljoin(response.url, detail_url),
                callback=self.parse_detail,
                meta={"front_image_url": image_url}
            )

        next_path = response.xpath("//a[contains(text(), 'Next >')]/@href").extract_first()
        yield scrapy.Request(url=parse.urljoin(response.url, next_path), callback=self.parse,
                             meta={'page_no': page + 1})

    def parse_detail(self, response):
        """对新闻详情页面进行信息解析"""
        match_re = re.match(".*?(\d+)", response.url)
        if match_re:
            # id
            post_id = match_re.group(1)
            '''
            使用ItemLoader
            '''
            item_loader = CNBlogItemLoader(item=CNBlogArticleItem(), response=response)
            item_loader.add_value("post_id", post_id)
            item_loader.add_xpath("title", "//div[@id='news_title']/a/text()")
            item_loader.add_xpath("create_time", "//span[@class='time']/text()")
            item_loader.add_xpath("content", "//div[@id='news_body']")
            item_loader.add_xpath("tags", "//div[@class='news_tags']/a/text()")
            if response.meta.get("front_image_url", ""):
                item_loader.add_value(
                    "front_image_url", response.meta.get("front_image_url", ""))
            # extra
            yield scrapy.FormRequest(
                url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo"),
                callback=self.parse_extra_info,
                meta={
                    'post_id': post_id,
                    "item_loader": item_loader
                },
                formdata={'contentId': post_id},
                method='GET'
            )
            pass

    def parse_extra_info(self, response):
        """对新闻详情页面的ajax数据进行解析"""
        item_loader = response.meta.get("item_loader", None)
        if item_loader:
            extraDict = json.loads(response.text)
            item_loader.add_value("commentCount", extraDict['CommentCount'])
            item_loader.add_value("totalView", extraDict['TotalView'])

        item = item_loader.load_item()

        # commentCount = extraDict['CommentCount']
        # item["commentCount"] = commentCount
        # totalView = extraDict['TotalView']
        # item["totalView"] = totalView

        yield item
