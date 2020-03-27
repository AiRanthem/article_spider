# 爬取知乎数据

## 日记

2020/3/12 完成selenium登录，cookies登录

2020/3/17 完成知乎爬虫。

## 笔记

1. selenium基本使用

   ```python
   from selenium import webdriver
   
   browser = webdriver.Chrome(executable_path='/usr/bin/chromedriver')
   
   browser.get('https://www.zhihu.com/signin')
   
   browser.find_element_by_xpath("//div[@class='SignFlow-tab']").click()
   browser.find_element_by_xpath("//input[@name='username']").send_keys('18965150181')
   browser.find_element_by_xpath("//button[@class='Button SignFlow-submitButton Button--primary Button--blue']") \
       .click()
   ```

2. 爬取知乎，需要手动启动chrome，否则driver会被识别。启动之前确保所有chrome实例已经被关闭

   ```zsh
   google-chrome-stable --remote-debugging-port=9222
   ```

   在`start_request`方法中，代码如下：

   ```python
   from selenium.webdriver.chrome.options import Options
   
       def start_requests(self):
           chrome_option = Options()
           chrome_option.add_argument('--disable-extensions')
           chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
           
           browser = webdriver.Chrome(options=chrome_option)
           browser.get('https://www.zhihu.com/signin')
   ```

3. 使用cookie

   ```python
   # settings.py
   USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36' # find with F12 in any Request Header
   DOWNLOADER_MIDDLEWARES = {
       'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 2 # user agent 自动变换
   }
   COOKIES_ENABLED = True
   COOKIES_DEBUG = True
   
   # in start_requests(self) of ArticleSpider.zhihu
   # arter you've logged in once
   browser.get('https://www.zhihu.com')
   cookies = browser.get_cookies()
   pickle.dump(cookies, open(COOKIES_STORE+'/zhihu.cookie', 'wb')) # not necessary
   cookie_dict = {}
   for cookie in cookies:
   	cookie_dict[cookie['name']] = cookie['value']
   ```

   

4. 通过`者也`识别倒立文字，注意修改sklearn中的引用：

   ```python
   from scipy.misc import comb
   # change to
   from scipy.special import comb
   ```

   

5. scrapy shell通过-s USER_AGENT='...'来实现配置的添加：

   `scrapy shell -s USER_AGENT='MOZILA.....' https://www.zhihu.com`

6. 对url的批量处理：这里需要对获取首页所有的问题url

   ```python
   all_urls = response.xpath('//a/@href').extract()
   all_urls = [parse.urljoin(response.url, url) for url in all_urls]
   # with filter
   all_urls = filter(lambda x: True if x.startswith('https') else Flase, all_urls)
   # with generator
   
   ```

   

7. 通过开发者工具找数据API，可以减少很多工作

8. 通过一个pipeline处理不同的Item：将sql语句包装在items中屏蔽变化

   ```python
   # class xxItem
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
       
   # class xxPipeline
       def do_insert(self, cursor, item):
           insert_sql, params = item.get_sql()
           cursor.execute(insert_sql, tuple(params))
   
   ```

   

9. 