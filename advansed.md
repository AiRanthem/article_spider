# 进阶技巧
## 设置selenium的chrome driver不加载图片
```python
from selenium import webdriver
chrome_opt = webdriver.ChromeOptions()
prefs={"profile.managed_default_content_settings.images":2}
chrome_opt.add_experimental_option("prefs",prefs)
browser=webdriver.Chrome(executable_path="///",chrome_options=chrome_opt)
```

## scrapy中间件
![](https://pic2.zhimg.com/80/v2-4a19d3a77fce2fb0ee79792b6ff8a7b1_720w.jpg)

### 启用中间件
以下载器中间件为例：
```python
# settings.py
DOWNLOADERMIDDLEWARES = {
    'myproject.middlewares.Custom_A_DownloaderMiddleware': 543,
    'myproject.middlewares.Custom_B_DownloaderMiddleware': 643,
    'myproject.middlewares.Custom_C_DownloaderMiddleware': None,
}
```
数字越小，越靠近引擎，数字越大越靠近下载器，所以数字越小的，processrequest()优先处理；数字越大的，process_response()优先处理；若需要关闭某个中间件直接设为None即可

### 中间件中的方法

对于请求的中间件实现 `process_request(request, spider)`；

对于处理回复中间件实现`process_response(request, response, spider)`；

对于异常处理实现 `process_exception(request, exception, spider)`

### 中间件示例
[example](scrapy-middleware.md)
## selenium集成到scrapy中
```python
# middlewares.py
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

