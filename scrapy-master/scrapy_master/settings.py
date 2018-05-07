# specify the spider name running
SPIDER_NAME = 'qidian'

# Specify the spider start_urls and key in redis. This will be push redis when statr
# START_URLS must be list.
START_URLS = ['https://www.qidian.com/all']
START_URLS_KEY = '%s:start_urls' % SPIDER_NAME

# stats collector key in redis
STATS_KEY = '%s:stats' % SPIDER_NAME

# Specify the host and port to use when connecting to Redis (optional).
REDIS_HOST = '192.168.31.218'
REDIS_PORT = 6379
# Use other encoding than utf-8 for redis.
REDIS_ENCODING = 'utf-8'

# zookeeper hosts
ZOOKEEPER_HOSTS = '127.0.0.1:2181'

# watch node path in zookeeper
ZOOKEEPER_PATH = '/scrapy_worker'

# scrapyd master addresss
SCRAPYD_MASTER = '127.0.0.1:5000'


