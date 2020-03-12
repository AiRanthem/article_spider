# 爬取知乎数据

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

   

4. 