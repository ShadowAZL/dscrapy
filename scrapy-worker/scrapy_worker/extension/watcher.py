from scrapy import signals
from scrapy.exceptions import NotSupported
from scrapy_zookeeper.zoo_watcher import Register
from scrapy_webservice.webservice import WebService


class Watcher(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self.zw = None
        self.crawler.signals.connect(self.engine_started, signal=signals.engine_started)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def engine_started(self):
        self.zw = Register(self.crawler.settings.get('ZOOKEEPER_PATH'),
                           self._get_web_services(),
                           self.crawler.settings.get('ZOOKEEPER_HOSTS'))

    def _get_web_services(self):
        for ext in self.crawler.extensions.middlewares:
            if isinstance(ext, WebService):
                return "http://{host.host:s}:{host.port:d}".format(host=ext.port.getHost()).encode('utf-8')
        raise NotSupported('Web Not Supported Please Check!')
