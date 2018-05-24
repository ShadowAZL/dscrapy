from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from twisted.internet import threads, defer

from extension.requests import PhantomjsRequest
import queue
from selenium import webdriver
import random


class PhantomjsMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('PHANTOMJS_ENABLED'):
            raise NotConfigured
        if crawler.spidercls.requestFactory != PhantomjsRequest:
            raise NotConfigured
        s = cls(crawler.settings.get('DRIVER_EXECUTABLE_PATH'), crawler.settings.get('PHANTOMJS_MAX_CON', 5))
        crawler.signals.connect(s.close_driver, signal=signals.spider_closed)
        return s

    def __init__(self, executable_path, max_con):
        self.executable_path = executable_path
        self.sem = defer.DeferredSemaphore(max_con)
        self.queue = queue.LifoQueue(max_con)

    def process_request(self, request, spider):
        if 'phantomjs' not in request.meta:
            return
        return self.sem.run(self._get, request, spider)

    def _get(self, request, spider):
        try:
            driver = self.queue.get_nowait()
        except queue.Empty:
            driver = webdriver.PhantomJS(executable_path=self.executable_path)

        dfd = threads.deferToThread(self._process_request, request, driver)
        dfd.addCallback(self._responsed, driver)
        return dfd

    def _process_request(self, request, driver):
        driver.get(request.url)
        return HtmlResponse(request.url, body=driver.page_source, request=request, encoding='utf-8')

    def _responsed(self, _, driver):
        self.queue.put(driver)
        return _

    def close_driver(self):
        while not self.queue.empty():
            driver = self.queue.get_nowait()
            driver.close()

