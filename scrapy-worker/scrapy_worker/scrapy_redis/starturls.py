from twisted.internet import defer
from scrapy.exceptions import NotConfigured


class StatrURLMiddleware(object):

    @classmethod
    def from_settings(cls, settings):
        if not settings.getbool('SCRAPY_REDIS_ENABLED'):
            raise NotConfigured
        return cls()

    def process_start_requests(self, start_requests, spider):
        return next(start_requests)

