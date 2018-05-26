# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from scrapy.utils.python import to_native_str
from twisted.internet import task

from scrapy_redis.connection import get_redis_from_settings

import random


class UserAgentMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('USER_AGENTS'))

    def __init__(self, user_agents=()):
        self.user_agents = user_agents

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        request.headers["User-Agent"] = user_agent
        return None


class ProxyMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        if settings.getbool('REDIS_IP_PROXY_ENABLED'):
            ipproxy_key = crawler.settings.get('REDIS_IP_PROXY_KEY')
            server = get_redis_from_settings(crawler.settings)
            return cls(server=server, key=ipproxy_key)
        return cls(crawler.settings.get('PROXIES'))

    def __init__(self, proxies=None, server=None, key=None, limit=10, freq=120):
        self.proxies = proxies
        self.limit = limit
        if server is not None and key is not None:
            self.server = server
            self.key = key
            self.proxies = [to_native_str(i) for i in self.server.srandmember(self.key, self.limit)]
            self.heartbeat = task.LoopingCall(self._update_ip)
            self.heartbeat.start(freq)

    def _update_ip(self):
        self.proxies = [to_native_str(i) for i in self.server.srandmember(self.key, self.limit)]

    def process_request(self, request, spider):
        request.meta['proxy'] = random.choice(self.proxies)
        return None
