BOT_NAME = 'webcorpus'

SPIDER_MODULES = ['webcorpus.crawlers.news']
NEWSPIDER_MODULE = 'webcorpus.crawlers.news'

COOKIES_ENABLED = False

DOWNLOAD_DELAY = 0.05

LOG_ENABLED = True
CONCURRENT_REQUESTS = 512
AUTOTHROTTLE_ENABLED = True
CONCURRENT_REQUESTS_PER_DOMAIN = 512
CONCURRENT_ITEMS = 1000
DOWNLOAD_TIMEOUT = 60

RETRY_ENABLED = True
RETRY_TIMES = 2     # + initial request


LOG_LEVEL = 'DEBUG'

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36'\
             '(KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'

DEPTH_PRIORITY = 1
CHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'
