from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse

from extension.requests import PhantomjsRequest

from selenium import webdriver
import random


class PhantomjsMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        if crawler.spidercls.requestFactory != PhantomjsRequest:
            raise NotConfigured
        s = cls(crawler.settings.get('DRIVER_EXECUTABLE_PATH'))
        crawler.signals.connect(s.close_driver, signal=signals.spider_closed)
        return s

    def __init__(self, executable_path):
        self.executable_path = executable_path
        self.driver = webdriver.PhantomJS(executable_path=self.executable_path)

    def process_request(self, request, spider):
        if 'phantomjs' not in request.meta:
            return

        self.driver.get(request.url)
        return HtmlResponse(request.url, body=self.driver.page_source, request=request, encoding='utf-8')

    def close_driver(self):
        self.driver.close()