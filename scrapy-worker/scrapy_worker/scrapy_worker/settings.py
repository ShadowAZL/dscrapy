# -*- coding: utf-8 -*-

# Scrapy settings for scrapy_worker project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'scrapy_worker'

SPIDER_MODULES = ['scrapy_worker.spiders']
NEWSPIDER_MODULE = 'scrapy_worker.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre"
USER_AGENTS = [
    "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
    "Avant Browser/1.2.789rel1 (http://www.avantbrowser.com)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre",
    "Mozilla/5.0 (Windows; U; Windows XP) Gecko MultiZilla/1.6.1.0a",
]

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 64

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 5
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'extension.middlewares.UserAgentMiddleware': 200,
    'scrapy_phantomjs.middlewares.PhantomjsMiddleware': 600,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy_webservice.webservice.WebService': 1,
    'extension.watcher.Watcher': 2,
}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapy_mongodb.pipelines.MongoDBPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 3.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
#HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'


# Whether to flush requests on start. Default is False.
SCHEDULER_FLUSH_ON_START = True

# log all duplicate requests.
DUPEFILTER_DEBUG = True

# see the cookies being sent and received from Scrapy
COOKIES_DEBUG = True

HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

SPLASH_URL = 'http://192.168.170.131:8050'
# Enables scheduling storing requests queue in redis.
SCHEDULER = 'scrapy_redis.scheduler.Scheduler'

# Enables stats collector in redis.
STATS_CLASS = 'extension.statscollectors.RedisStatsCollector'

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RedisDupeFilter'

# Use other encoding than utf-8 for redis.
REDIS_ENCODING = 'utf-8'

# Specify the host and port to use when connecting to Redis (optional).
REDIS_HOST = '192.168.31.218'
REDIS_PORT = '6379'

# Specify the uri to use when connecting to mongodb (optional).
MONGODB_URI = 'mongodb://192.168.31.218:27017'

# enable web services
WEBSERVICE_ENABLED = True

# zookeeper hosts
ZOOKEEPER_HOSTS = '127.0.0.1:2181'

# watch node path in zookeeper
ZOOKEEPER_PATH = '/scrapy_worker/child'
