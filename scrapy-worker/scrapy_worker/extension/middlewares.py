# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse

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
        return cls(crawler.settings.get('PROXIES'))

    def __init__(self, proxies=()):
        self.proxies = proxies

    def process_request(self, request, spider):
        request.meta['proxy'] = random.choice(self.proxies)
        return None
