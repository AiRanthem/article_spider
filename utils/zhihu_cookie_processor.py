import json
import pickle

from ArticleSpider.settings import COOKIES_STORE

with open(r'C:\Code\python\article_spider\utils\zhihu_cookie.json', 'r') as f:
    cookieJson = json.load(f)
pickle.dump(cookieJson, open(COOKIES_STORE+'/zhihu.cookie', 'wb'))
print('cookie dumped to' + COOKIES_STORE + '/zhihu.cookie')
