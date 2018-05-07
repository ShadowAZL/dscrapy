import redis
import logging

from codecs import decode, encode

from scrapy.statscollectors import StatsCollector
from scrapy_redis.connection import from_settings as redis_from_settings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RedisStatsCollector(StatsCollector):
    def __init__(self, crawler):
        StatsCollector.__init__(self, crawler)

        self.redis = redis_from_settings(crawler.settings)
        self.crawler = crawler
        self.key = '%s:stats' % crawler.spidercls.name

        self.encoding = crawler.settings['REDIS_ENCODING']

    def get_value(self, key, default=None, spider=None):
        value = self.redis.hget(self.key, key)
        if value is None:
            return default
        else:
            try:
                return int(decode(value, self.encoding))
            except ValueError:
                return decode(value, self.encoding)

    def get_stats(self, spider=None):
        stats = self.redis.hgetall(self.key)
        return {decode(k, self.encoding): decode(v, self.encoding) for (k, v) in stats}

    def set_value(self, key, value, spider=None):
        StatsCollector.set_value(self, key, value)
        self.redis.hset(self.key, key, value)

    def inc_value(self, key, count=1, start=0, spider=None):
        StatsCollector.inc_value(self, key, count, start)

        pipe = self.redis.pipeline()
        pipe.hsetnx(self.key, key, start)
        pipe.hincrby(self.key, key, count)
        pipe.execute()

    def max_value(self, key, value, spider=None):
        StatsCollector.max_value(self, key, value)
        self.max_min_value(max, key, value)

    def min_value(self, key, value, spider=None):
        StatsCollector.min_value(self, key, value)
        self.max_min_value(min, key, value)

    def clear_stats(self, spider=None):
        StatsCollector.clear_stats(self)
        self.redis.delete(self.key)

    def max_min_value(self, max_or_min, key, value):
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(self.key)
                    pre_value = pipe.hget(self.key, key)
                    if pre_value:
                        new_value = max_or_min(int(pre_value), value)
                    else:
                        new_value = value
                    pipe.multi()
                    pipe.hset(self.key, key, new_value)
                    pipe.execute()
                    break
                except redis.WatchError as e:
                    logger.debug(e)
                    pass
