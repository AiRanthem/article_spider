# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
import MySQLdb
from MySQLdb.cursors import DictCursor
from twisted.enterprise import adbapi

from ArticleSpider.config import MYSQL_HOST, MYSQL_PASSWORD, MYSQL_USER, MYSQL_DB, MYSQL_CHARSET

class ArticleImagesPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            image_file_path = ''
            for ok, value in results:
                image_file_path = value['path']
            item['front_image_path'] = image_file_path
        return item

class JsonWithEncodingPipeline(object):
    def __init__(self):
        super().__init__()
        self.file = codecs.open('article.json', 'a', 'utf-8')
    
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()

class JsonExporterPipeline(object):
    def __init__(self):
        super().__init__()
        self.file = open('articleExporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

class MysqlTwistedPipeline(object):
    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host = settings['MYSQL_HOST'], 
            passwd = settings['MYSQL_PASSWORD'], 
            user = settings['MYSQL_USER'], 
            db = settings['MYSQL_DB'], 
            charset = settings['MYSQL_CHARSET'], 
            cursorclass = DictCursor,
            use_unicode = True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)
        return cls(dbpool)
    
    def __init__(self, dbpool):
        super().__init__()
        self.dbpool = dbpool

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item) # runInteraction(function, **params),自动注入cursor
        query.addErrback(self.handle_error) # 自动注入failure

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = '''
            insert into article (post_id, title, create_time, content, tags, comment_count, total_view, front_image_url, front_image_path)
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE key update content=VALUES(content), title=VALUES(title);
        '''
        params = []
        params.append(item.get('post_id'))
        params.append(item.get('title', ''))
        params.append(item.get('create_time', '1970-1-1'))
        params.append(item.get('content', ''))
        params.append(item.get('tags', ''))
        params.append(item.get('commentCount', 0))
        params.append(item.get('totalView', 0))
        params.append(item.get('front_image_url', ''))
        params.append(item.get('front_image_path', ''))

        cursor.execute(insert_sql, tuple(params))

