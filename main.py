import sys

from scrapy.cmdline import execute
from ArticleSpider.settings import PROJECT_PATH

sys.path.append(PROJECT_PATH)

execute(["scrapy","crawl","cnblogs"])
