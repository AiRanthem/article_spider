# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from scrapy.loader.processors import TakeFirst, Identity, MapCompose, Join
from scrapy.loader import ItemLoader


class CNBlogItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

def data_convert(value):
    time_match = re.match('.*?(\d+.*)', value)
    if time_match:
        return time_match.group(1)
    else:
        return "1970-07-01"
    

class CNBlogArticleItem(scrapy.Item):
    # id
    post_id = scrapy.Field()
    # title
    title = scrapy.Field()
    # time
    create_time = scrapy.Field(input_processor = MapCompose(data_convert))
    # content
    content = scrapy.Field()
    # tags
    tags = scrapy.Field(output_processor = Join(','))
    # extra
    commentCount = scrapy.Field()
    totalView = scrapy.Field()
    # front image
    front_image_url = scrapy.Field(output_processor = Identity())
    front_image_path = scrapy.Field()

class EasyZhihuJsonItem(scrapy.Item):
    data = scrapy.Field()

