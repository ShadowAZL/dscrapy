import logging

from twisted.internet import task

from scrapy.exceptions import NotConfigured
from scrapy import signals

logger = logging.getLogger(__name__)


class SpeedStats(object):
    """Log basic scraping stats periodically"""

    def __init__(self, stats, interval=60.0):
        self.stats = stats
        self.interval = interval
        self.multiplier = 60.0 / self.interval
        self.task = None

    @classmethod
    def from_crawler(cls, crawler):
        interval = crawler.settings.getfloat('LOGSTATS_INTERVAL')
        if not interval:
            raise NotConfigured
        o = cls(crawler.stats, interval)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.pagesprev = 0
        self.itemsprev = 0
        self.rsp_bytes_prev = 0

        self.task = task.LoopingCall(self.log, spider)
        self.task.start(self.interval)

    def log(self, spider):
        items = self.stats.get_value('item_scraped_count', 0)
        pages = self.stats.get_value('response_received_count', 0)
        rsp_bytes = self.stats.get_value('response_bytes', 0)
        irate = (items - self.itemsprev) * self.multiplier
        prate = (pages - self.pagesprev) * self.multiplier
        rsp_rate = (rsp_bytes - self.rsp_bytes_prev) * self.multiplier
        self.pagesprev, self.itemsprev, self.rsp_bytes_prev = pages, items, rsp_bytes

        self.stats.set_value('item_scraped_speed', irate, spider)
        self.stats.set_value('response_received_speed', prate, spider)
        self.stats.set_value('response_download_speed', rsp_rate, spider)

    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()
