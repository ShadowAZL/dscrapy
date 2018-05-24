"""
用来收集爬虫运行信息，有些爬虫信息并需要收集，因此掠过
"""

import redis
import logging

from codecs import decode, encode

from scrapy.statscollectors import StatsCollector
from scrapy_redis.connection import from_settings as redis_from_settings
from twisted.internet import threads

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RedisStatsCollector(StatsCollector):
    redis_field = ['item_scraped_count', 'response_received_count']

    def __init__(self, crawler):
        StatsCollector.__init__(self, crawler)

        self.redis = redis_from_settings(crawler.settings)
        self.crawler = crawler
        self.key = '%s:stats' % crawler.spidercls.name

        self.encoding = crawler.settings['REDIS_ENCODING']

    def get_value(self, key, default=None, spider=None):
        if key not in self.redis_field:
            return super(RedisStatsCollector, self).get_value(key, default, spider)

        value = self.redis.hget(self.key, key)
        if value is None:
            return default
        else:
            try:
                return int(decode(value, self.encoding))
            except ValueError:
                return decode(value, self.encoding)

    def set_value(self, key, value, spider=None):
        if key not in self.redis_field:
            return super(RedisStatsCollector, self).set_value(key, value, spider)

        super(RedisStatsCollector, self).set_value(key, value, spider)
        threads.deferToThread(self._set_value, key, value)

    def _set_value(self, key, value):
        self.redis.hset(self.key, key, value)

    def inc_value(self, key, count=1, start=0, spider=None):
        super(RedisStatsCollector, self).inc_value(key, count, start)

        if key not in self.redis_field:
            return
        threads.deferToThread(self._inc_value, key, count, start)

    def _inc_value(self, key, count=1, start=0):
        pipe = self.redis.pipeline()
        pipe.hsetnx(self.key, key, start)
        pipe.hincrby(self.key, key, count)
        pipe.execute()

    def clear_stats(self, spider=None):
        super(RedisStatsCollector, self).clear_stats(spider)
        self.redis.delete(self.key)

    def _max_value(self, key, value, spider=None):
        StatsCollector.max_value(self, key, value)
        self.max_min_value(max, key, value)

    def _min_value(self, key, value, spider=None):
        StatsCollector.min_value(self, key, value)
        self.max_min_value(min, key, value)

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