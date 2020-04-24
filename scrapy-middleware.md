> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 https://zhuanlan.zhihu.com/p/42498126

> **作者：Zarten**  
> **知乎专栏：[Python 爬虫深入详解](https://zhuanlan.zhihu.com/zarten)**  
> **知乎 ID： [Zarten](https://www.zhihu.com/people/zarten/posts)**  
> **简介： 互联网一线工作者，尊重原创并欢迎评论留言指出不足之处，也希望多些关注和点赞是给作者最好的鼓励 ！**

**概述**
------

![](https://pic2.zhimg.com/v2-4a19d3a77fce2fb0ee79792b6ff8a7b1_b.jpg)
![](https://pic2.zhimg.com/v2-4a19d3a77fce2fb0ee79792b6ff8a7b1_r.jpg)

整体的详细流程如下，来源 scrapy 的官网，地址点[这里](https://link.zhihu.com/?target=https%3A//github.com/scrapy/scrapy/blob/master/docs/topics/architecture.rst)

![](https://pic1.zhimg.com/v2-69fbf7d1bcc656f5c945650fa7f40ab8_b.jpg) ![](https://pic1.zhimg.com/v2-69fbf7d1bcc656f5c945650fa7f40ab8_r.jpg)

**下载器中间件（Downloader Middleware）**
---------------------------------

如上图标号 4、5 处所示，下载器中间件用于处理 scrapy 的 request 和 response 的钩子框架，可以全局的修改一些参数，如代理 ip，header 等

使用下载器中间件时必须激活这个中间件，方法是在 settings.py 文件中设置 DOWNLOADER_MIDDLEWARES 这个字典，格式类似如下：

```
DOWNLOADERMIDDLEWARES = {
    'myproject.middlewares.Custom_A_DownloaderMiddleware': 543,
    'myproject.middlewares.Custom_B_DownloaderMiddleware': 643,
    'myproject.middlewares.Custom_B_DownloaderMiddleware': None,
}
```

数字越小，越靠近引擎，数字越大越靠近下载器，所以数字越小的，processrequest() 优先处理；数字越大的，process_response() 优先处理；若需要关闭某个中间件直接设为 None 即可

**自定义下载器中间件**
-------------

有时我们需要编写自己的一些下载器中间件，如使用代理，更换 user-agent 等，对于请求的中间件实现 `process_request`(_request_, _spider_)；对于处理回复中间件实现`process_response`(_request_, _response_, _spider_)；以及异常处理实现 `process_exception`(_request_, _exception_, _spider_)

*   **`process_request`(_request_, _spider_)**

每当 scrapy 进行一个 request 请求时，这个方法被调用。通常它可以返回 1.None 2.Response 对象 3.Request 对象 4. 抛出 IgnoreRequest 对象

通常返回 None 较常见，它会继续执行爬虫下去。其他返回情况参考[这里](https://link.zhihu.com/?target=https%3A//doc.scrapy.org/en/latest/topics/downloader-middleware.html%23scrapy.downloadermiddlewares.DownloaderMiddleware)

例如下面 2 个例子是更换 user-agent 和代理 ip 的下载中间件

**user-agent 中间件**

```
from faker import Faker

class UserAgent_Middleware():

    def process_request(self, request, spider):
        f = Faker()
        agent = f.firefox()
        request.headers['User-Agent'] = agent
```

**代理 ip 中间件**

```
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    # 'Connection': 'close'
}

class Proxy_Middleware():

    def __init__(self):
        self.s = requests.session()

    def process_request(self, request, spider):

        try:
            xdaili_url = spider.settings.get('XDAILI_URL')

            r = self.s.get(xdaili_url, headers= headers)
            proxy_ip_port = r.text
            request.meta['proxy'] = 'http://' + proxy_ip_port
        except requests.exceptions.RequestException:
            print('***get xdaili fail!')
            spider.logger.error('***get xdaili fail!')

    def process_response(self, request, response, spider):
        if response.status != 200:
            try:
                xdaili_url = spider.settings.get('XDAILI_URL')

                r = self.s.get(xdaili_url, headers= headers)
                proxy_ip_port = r.text
                request.meta['proxy'] = 'http://' + proxy_ip_port
            except requests.exceptions.RequestException:
                print('***get xdaili fail!')
                spider.logger.error('***get xdaili fail!')

            return request
        return response

    def process_exception(self, request, exception, spider):

        try:
            xdaili_url = spider.settings.get('XDAILI_URL')

            r = self.s.get(xdaili_url, headers= headers)
            proxy_ip_port = r.text
            request.meta['proxy'] = 'http://' + proxy_ip_port
        except requests.exceptions.RequestException:
            print('***get xdaili fail!')
            spider.logger.error('***get xdaili fail!')

        return request
```

**遇到验证码的处理方法**

同样有时我们会遇到输入验证码的页面，除了自动识别验证码之外，还可以重新请求（前提是使用了代理 ip），只需在 spider 中禁止过滤

```
def parse(self, response):
  
        result = response.text

        if re.search(r'make sure you\'re not a robot', result):
            self.logger.error('check时ip被限制！ asin为: {0}'.format(origin_asin))
            print('check时ip被限制！ asin为: {0}'.format(origin_asin))

            response.request.meta['dont_filter'] = True

            return response.request
```

**重试中间件**

有时使用代理会被远程拒绝或超时等错误，这时我们需要换代理 ip 重试，重写 scrapy.downloadermiddlewares.retry.RetryMiddleware

```
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

class My_RetryMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response

        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            try:
                xdaili_url = spider.settings.get('XDAILI_URL')

                r = requests.get(xdaili_url)
                proxy_ip_port = r.text
                request.meta['proxy'] = 'https://' + proxy_ip_port
            except requests.exceptions.RequestException:
                print('获取讯代理ip失败！')
                spider.logger.error('获取讯代理ip失败！')

            return self._retry(request, reason, spider) or response
        return response


    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get('dont_retry', False):
            try:
                xdaili_url = spider.settings.get('XDAILI_URL')

                r = requests.get(xdaili_url)
                proxy_ip_port = r.text
                request.meta['proxy'] = 'https://' + proxy_ip_port
            except requests.exceptions.RequestException:
                print('获取讯代理ip失败！')
                spider.logger.error('获取讯代理ip失败！')

            return self._retry(request, exception, spider)
```

**scrapy 中对接 selenium**

```
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from gp.configs import *


class ChromeDownloaderMiddleware(object):

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 设置无界面
        if CHROME_PATH:
            options.binary_location = CHROME_PATH
        if CHROME_DRIVER_PATH:
            self.driver = webdriver.Chrome(chrome_options=options, executable_path=CHROME_DRIVER_PATH)  # 初始化Chrome驱动
        else:
            self.driver = webdriver.Chrome(chrome_options=options)  # 初始化Chrome驱动

    def __del__(self):
        self.driver.close()

    def process_request(self, request, spider):
        try:
            print('Chrome driver begin...')
            self.driver.get(request.url)  # 获取网页链接内容
            return HtmlResponse(url=request.url, body=self.driver.page_source, request=request, encoding='utf-8',
                                status=200)  # 返回HTML数据
        except TimeoutException:
            return HtmlResponse(url=request.url, request=request, encoding='utf-8', status=500)
        finally:
            print('Chrome driver end...')
```

*   **`process_response`(_request_, _response_, _spider_)**

当请求发出去返回时这个方法会被调用，它会返回 1.Response 对象 2.Request 对象 3. 抛出 IgnoreRequest 对象

1. 若返回 Response 对象，它会被下个中间件中的 process_response() 处理

2. 若返回 Request 对象，中间链停止，然后返回的 Request 会被重新调度下载

3. 抛出 IgnoreRequest，回调函数 Request.errback 将会被调用处理，若没处理，将会忽略

*   **`process_exception`(_request_, _exception_, _spider_)**

当下载处理模块或 process_request() 抛出一个异常（包括 IgnoreRequest 异常）时，该方法被调用

通常返回 None, 它会一直处理异常

*   **`from_crawler`(_cls_, _crawler_)**

这个类方法通常是访问 settings 和 signals 的入口函数

```
@classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_host = crawler.settings.get('MYSQL_HOST'),
            mysql_db = crawler.settings.get('MYSQL_DB'),
            mysql_user = crawler.settings.get('MYSQL_USER'),
            mysql_pw = crawler.settings.get('MYSQL_PW')
        )
```

**scrapy 自带下载器中间件**
-------------------

以下中间件是 scrapy 默认的下载器中间件

```
{
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 100,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': 560,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 900,
}
```

scrapy 自带中间件请参考[这里](https://link.zhihu.com/?target=https%3A//doc.scrapy.org/en/latest/topics/downloader-middleware.html%23built-in-downloader-middleware-reference)

**Spider 中间件（Spider Middleware）**
---------------------------------

如文章第一张图所示，spider 中间件用于处理 response 及 spider 生成的 item 和 Request

_**注意：从上图看到第 1 步是没经过 spider Middleware 的**_

启动 spider 中间件必须先开启 settings 中的设置

```
SPIDER_MIDDLEWARES = {
    'myproject.middlewares.CustomSpiderMiddleware': 543,
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,
}
```

数字越小越靠近引擎，process_spider_input() 优先处理，数字越大越靠近 spider，process_spider_output() 优先处理, 关闭用 None

**编写自定义 spider 中间件**
--------------------

*   **`process_spider_input`(_response_, _spider_)**

当 response 通过 spider 中间件时，这个方法被调用，返回 None

*   **`process_spider_output`(_response_, _result_, _spider_)**

当 spider 处理 response 后返回 result 时，这个方法被调用，必须返回 Request 或 Item 对象的可迭代对象，一般返回 result

*   **`process_spider_exception`(_response_, _exception_, _spider_)**

当 spider 中间件抛出异常时，这个方法被调用，返回 None 或可迭代对象的 Request、dict、Item

写下你的评论...  

当你在中间件中 return request 时，scrapy 会不会过滤掉这次请求

不会的

能说明下 scrapy 中 middleware 是如何实现的吗

重试中间件那里没看太明白，既然重试不是应该返回一个 request 对象么？怎么返回了一个 response