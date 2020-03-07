# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class CNBlogArticleItem(scrapy.Item):
    # id
    post_id = scrapy.Field()
    # title
    title = scrapy.Field()
    # time
    create_time = scrapy.Field()
    # content
    content = scrapy.Field()
    # tags
    tags = scrapy.Field()
    # extra
    commentCount = scrapy.Field()
    totalView = scrapy.Field()
    # front image
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()