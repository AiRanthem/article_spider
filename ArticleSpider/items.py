# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from scrapy.loader.processors import TakeFirst, Identity, MapCompose, Join
from scrapy.loader import ItemLoader


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

    def get_sql(self):
        insert_sql = '''
            insert into article (post_id, title, create_time, content, tags, comment_count, total_view, front_image_url, front_image_path)
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE key update content=VALUES(content), title=VALUES(title);
        '''
        params = []
        params.append(self.get('post_id'))
        params.append(self.get('title', ''))
        params.append(self.get('create_time', '1970-1-1'))
        params.append(self.get('content', ''))
        params.append(self.get('tags', ''))
        params.append(self.get('commentCount', 0))
        params.append(self.get('totalView', 0))
        params.append(self.get('front_image_url', ''))
        params.append(self.get('front_image_path', ''))

        return insert_sql, params

