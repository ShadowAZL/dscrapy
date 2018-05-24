import logging
import time

from scrapy.dupefilters import RFPDupeFilter

from extension.dupefilter import request_fingerprint

from . import defaults
from .connection import get_redis_from_settings
from .bloomfilter import BloomFilter

logger = logging.getLogger(__name__)


class RedisDupeFilter(RFPDupeFilter):
    """Redis-based request duplicates filter.

    This class can also be used with default Scrapy's scheduler.

    """

    logger = logger

    def __init__(self, server, key, debug=False):
        """Initialize the duplicates filter.

        Parameters
        ----------
        server : redis.StrictRedis
            The redis server instance.
        key : str
            Redis key Where to store fingerprints.
        debug : bool, optional
            Whether to log filtered requests.

        """
        self.server = server
        self.key = key
        self.debug = debug
        self.logdupes = True

    @classmethod
    def from_settings(cls, settings):
        """Returns an instance from given settings.

        This uses by default the key ``dupefilter:<timestamp>``. When using the
        ``scrapy_redis.scheduler.Scheduler`` class, this method is not used as
        it needs to pass the spider name in the key.

        """
        if not settings.getbool('SCRAPY_REDIS_ENABLED'):
            return RFPDupeFilter.from_settings(settings)

        server = get_redis_from_settings(settings)

        key = defaults.DUPEFILTER_KEY % {'timestamp': int(time.time())}
        debug = settings.getbool('DUPEFILTER_DEBUG')

        instance = cls(server, key=key, debug=debug)
        if settings.getbool('BLOOMFILTER_ENABLED'):
            instance.bloomfilter = BloomFilter(server, key)
            instance.request_seen = instance.bloom_request_seen
        return instance

    @classmethod
    def from_crawler(cls, crawler):
        """Returns instance from crawler.

        Parameters
        ----------
        crawler : scrapy.crawler.Crawler

        Returns
        -------
        RFPDupeFilter
            Instance of RFPDupeFilter.

        """
        return cls.from_settings(crawler.settings)

    def request_seen(self, request):
        """Returns True if request was already seen.

        Parameters
        ----------
        request : scrapy.http.Request

        Returns
        -------
        bool

        """
        fp = self.request_fingerprint(request)
        # This returns the number of values added, zero if already exists.
        added = self.server.sadd(self.key, fp)
        return added == 0

    def bloom_request_seen(self, request):
        fp = self.request_fingerprint(request)
        exists = self.bloomfilter.exists(fp)
        if exists:
            return True
        else:
            self.bloomfilter.insert(fp)
            return False

    def request_fingerprint(self, request):
        """Returns a fingerprint for a given request.

        Parameters
        ----------
        request : scrapy.http.Request

        Returns
        -------
        str

        """
        return request_fingerprint(request)

    @classmethod
    def from_spider(cls, spider):
        settings = spider.settings
        server = get_redis_from_settings(settings)
        dupefilter_key = settings.get("SCHEDULER_DUPEFILTER_KEY", defaults.SCHEDULER_DUPEFILTER_KEY)
        key = dupefilter_key % {'spider': spider.name}
        debug = settings.getbool('DUPEFILTER_DEBUG')

        instance = cls(server, key=key, debug=debug)
        if settings.getbool('BLOOMFILTER_ENABLED'):
            instance.bloomfilter = BloomFilter(server, key)
            instance.request_seen = instance.bloom_request_seen
        return instance

    def close(self, reason=''):
        """Delete data on close. Called by Scrapy's scheduler.

        Parameters
        ----------
        reason : str, optional

        """
        self.clear()

    def clear(self):
        """Clears fingerprints data."""
        self.server.delete(self.key)

