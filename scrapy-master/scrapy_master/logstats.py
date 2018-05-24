from threading import Thread
from redis import StrictRedis
from datetime import datetime
import logging
import time
logger = logging.getLogger(__name__)


class LogStats(Thread):
    def __init__(self, settings, interval=60):
        super(LogStats, self).__init__()
        self.settings = settings
        self.stats_key = self.settings['STATS_KEY']
        self.redis_cli = StrictRedis(host=settings['REDIS_HOST'], port=settings['REDIS_PORT'])
        self.interval = interval / 60.0
        self.pre_item = 0
        self.pre_page = 0
        self.irate = 0
        self.prate = 0
        self.avg_irate = 0
        self.avg_prate = 0
        self.start_time = datetime.now()

    def get_stats(self, name):
        return self.redis_cli.hget(self.settings['STATS_KEY'], name)

    def run(self):
        while True:
            item = int(self.get_stats('item_scraped_count') or 0)
            page = int(self.get_stats('response_received_count') or 0)
            self.irate = (item - self.pre_item) / self.interval
            self.prate = (page - self.pre_page) / self.interval

            delta = (datetime.now() - self.start_time).seconds or 1
            self.avg_irate = int(item / delta / 60)
            self.avg_prate = int(item / delta / 60)

            msg = ("Crawled %(pages)d pages (at %(pagerate)d pages/min. Avg Speed %(avg_prate).2f pages/min), "
                   "scraped %(items)d items (at %(itemrate)d items/min. Avg Speed %(avg_irate).2f items/min))")
            log_args = {'pages': page, 'pagerate': self.prate, 'avg_prate': self.avg_prate,
                        'items': item, 'itemrate': self.irate, 'avg_irate': self.avg_irate}
            logger.info(msg, log_args)

            time.sleep(self.interval * 60.0)



