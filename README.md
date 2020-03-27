# Article Spider
scrapy框架入门

## 第一阶段：初步使用scrapy爬取CNblog（已完成）

## [第二阶段: 爬取知乎数据（学习selenium）](zhihu_note.md)（已完成）

## [第三阶段：爬取拉勾网数据（学习Crawl）](lagou_note.md)



## 结构
1. parse:用来解析
2. Request/FormRequest:通过yield发起请求
3. Item:用来数据传递

## 细碎笔记
1. 新建项目: `scrapy startproject <name>`
2. 建立爬虫: `cd <name>; scrapy genspider <spider_name> <domain>`
3. 在parse方法中写抓取策略，其他地方进行解析
4. 通过urllib.parse.urljoin进行url处理。注意：url拼接时，子url如果以'/'开头，则会被拼接到绝对路径（域名）下，否则是相对路径，即当前完整url
5. 在parse中异步下载。
    ```python
    yield Request(
        url, #要访问的url
        callback, #解析使用的回调函数
        meta #传递的信息，在下一个函数中可以使用 response.meta属性调用。是一个字典。
    )
    ```
    注意：需要参数时，使用`FormRequest`。默认post，可以指定方法
6. Items:数据传递
    + 使用 name = Field()来定义域
    + Field参数：
        ```python
        from scrapy.loader.processors import MapCompose, TakeFirst # 用来连接方法和取首位
        # 处理器可以从上面的模块选择导入
        scrapy.Field(
            input_processor = MapCompose(fun1, fun2, ..), # 输入值会被传入的参数串联处理
            output_processor = TakeFirst() # 这里保存第一个
        )
        ```
    
7. 图片下载的pipeline：`scrapy.pipelines.images.ImagesPipeline`
    ```python
    #配置
    IMAGES_URLS_FIELD = 'front_image_url'
    IMAGES_STORE = '/home/airan/learn_python/article_spider/images'
    ```
8. pipeline的结构（方法）：
    ```python
    process_item(self, item, spider)
    item_completed(self, results, item, info)
    spider_closed(self, spider)
    ```
9. 使用Exporter简化导出。只需要三步就可以使用exporter：
    1. 在init中调用`start_exporting()`
    2. 需要导出时，使用`export_item(item)`
    3. 最后调用`finish_exporting()`
    ```python
    # example
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
    ```
10. 数据入库: 
    1. 通过MySQLdb模块直接进行数据库操作：
        ```python
        class MysqlPipeline(object):
            def __init__(self):
                super().__init__()
                self.conn = MySQLdb.connect(
                    MYSQL_HOST,
                    MYSQL_USER,
                    MYSQL_PASSWORD,
                    MYSQL_DB,
                    charset = MYSQL_CHARSET,
                    use_unicode = True
                )
                self.cursor = self.conn.cursor()

            def process_item(self, item, spider):
                insert_sql = '''
                    insert into article values(%s)
                '''
                params = [param1]
                self.cursor.execute(insert_sql, params)
                self.conn.commit()
        ```
    2. 异步处理，代码框架如下：
        ```python
        from twisted.enterprise import adbapi
        from MySQLdb.cursors import DictCursor
        class MysqlTwistedPipeline(object):
            @classmethod
            def from_settings(cls, settings):
                dbparams = dict(
                    host = settings['MYSQL_HOST'], 
                    _other_params = settings['OTHER_PARAMS'],
                    cursorclass = DictCursor,
                    use_unicode = True
                )
                dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)
                return cls(dbpool)
            
            def __init__(self, dbpool):
                self.dbpool = dbpool

            def process_item(self, item, spider):
                query = self.dbpool.runInteraction(self.do_insert, item) # runInteraction(function, **params),自动注入cursor
                query.addErrback(self.handle_error) # 自动注入failure

            def handle_error(self, failure):
                print(failure)

            def do_insert(self, cursor, item):
                insert_sql = '''
                    insert into article values(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                '''
                params = []
                params.append(_something_in_your_item)
                cursor.execute(insert_sql, tuple(params))
        ```
11. 使用ItemLoader
    ```python
    ''' 使用ItemLoader '''
    from scrapy.loader import ItemLoader

    # ...

    item_loader = ItemLoader(item=YourItem(), response=response)
    item_loader.add_xpath("field_name", "xpath")
    item_loader.add_value("field_name", value)
    # ...
    item = item_loader.load_item()

    ''' 定制ItemLoader '''
    # 通过继承ItemLoader类并修改下面四个属性，可以简单定制ItemLoader
    class ItemLoader(object):
        default_item_class = Item
        default_input_processor = Identity()
        default_output_processor = Identity()
        default_selector_class = Selector
    # 默认的processor会被Item中Field设置的processor覆盖
    ```
