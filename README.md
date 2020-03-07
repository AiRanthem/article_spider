# Article Spider
根据慕课网的scrapy教程学习爬虫的编写

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
7. pipeline结构