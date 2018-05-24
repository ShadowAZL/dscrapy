from scrapy.utils.reqser import request_to_dict, request_from_dict
from scrapy import signals
from twisted.internet import threads
from . import picklecompat


class Base(object):
    """Per-spider base queue class"""

    def __init__(self, server, spider, key, serializer=None):
        """Initialize per-spider redis queue.

        Parameters
        ----------
        server : StrictRedis
            Redis client instance.
        spider : Spider
            Scrapy spider instance.
        key: str
            Redis key where to put and get messages.
        serializer : object
            Serializer object with ``loads`` and ``dumps`` methods.

        """
        if serializer is None:
            serializer = picklecompat
        if not hasattr(serializer, 'loads'):
            raise TypeError("serializer does not implement 'loads' function: %r"
                            % serializer)
        if not hasattr(serializer, 'dumps'):
            raise TypeError("serializer '%s' does not implement 'dumps' function: %r"
                            % serializer)

        self.server = server
        self.spider = spider
        self.key = key % {'spider': spider.name}
        self.serializer = serializer

    def _encode_request(self, request):
        """Encode a request object"""
        obj = request_to_dict(request, self.spider)
        return self.serializer.dumps(obj)

    def _decode_request(self, encoded_request):
        """Decode an request previously encoded"""
        obj = self.serializer.loads(encoded_request)
        return request_from_dict(obj, self.spider)

    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError

    def push(self, request):
        """Push a request"""
        raise NotImplementedError

    def pop(self, timeout=0):
        """Pop a request"""
        raise NotImplementedError

    def clear(self):
        """Clear queue/stack"""
        self.server.delete(self.key)


class CacheQueue(Base):
    def __init__(self, cache_limit=10, *args, **kwargs):
        super(CacheQueue, self).__init__(*args, **kwargs)
        self.cache = None
        self.cache_limit = cache_limit
        self.defered = None

    def __len__(self):
        """Return the length of the queue"""
        return self.defered is not None or self.server.zcard(self.key)

    def push(self, request):
        """Push a request"""
        data = self._encode_request(request)
        score = -request.priority
        self.server.execute_command('ZADD', self.key, score, data)

    def pop(self, timeout=0):
        """
        Pop a request
        """
        if not self.cache and not self.defered:
            def _ret(requests):
                self.cache = requests
                return requests
            def _cb(_):
                self.defered = None
                return _
            self.defered = threads.deferToThread(self._fetch)
            self.defered.addCallback(_ret)
            self.defered.addBoth(_cb)
        if self.cache:
            return self._decode_request(self.cache.pop())

    def _fetch(self):
        # use atomic range/remove using multi/exec
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, self.cache_limit, desc=True).zremrangebyrank(self.key, 0, self.cache_limit)
        results, count = pipe.execute()
        return results


class PriorityCacheQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""
    def __init__(self, *args, **kwargs):
        self.cache_size = kwargs.pop('cache_size', 10)
        self.enqueue_cache = []
        self.dequeue_cache = []
        self.defered = None
        super(PriorityCacheQueue, self).__init__(*args, **kwargs)

        self.spider.crawler.signals.connect(self.flush, signal=signals.spider_idle)

    def __len__(self):
        """Return the length of the queue"""
        return self.defered is not None or self.server.zcard(self.key)

    def push(self, request):
        """Push a request"""

        data = self._encode_request(request)
        score = -request.priority
        self.enqueue_cache.append((score, data))

        if len(self.enqueue_cache) > self.cache_size or len(self.dequeue_cache) == 0:
            self.flush()

    def pop(self, timeout=0):
        """
        Pop a request
        timeout not support in this queue class
        """
        if not self.dequeue_cache and not self.defered:
            self.fetch()

        if self.dequeue_cache:
            return self._decode_request(self.dequeue_cache.pop())

    def flush(self):
        if not self.enqueue_cache:
            return
        requests = self.enqueue_cache[:]
        self.enqueue_cache.clear()
        threads.deferToThread(self._flush, requests)

    def _flush(self, requests):
        pipe = self.server.pipeline(transaction=False)
        for score, data in requests:
            pipe.execute_command('ZADD', self.key, score, data)
        pipe.execute()

    def fetch(self):
        # use atomic range/remove using multi/exec
        self.defered = threads.deferToThread(self._fetch)

        def _cb(results):
            if results:
                self.dequeue_cache = results
            if len(self.enqueue_cache) > self.cache_size or len(self.dequeue_cache) == 0:
                self.flush()

        def _clear(_):
            self.defered = None
            return _
        self.defered.addCallback(_cb)
        self.defered.addBoth(_clear)

    def _fetch(self):
        # use atomic range/remove using multi/exec
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, self.cache_size, desc=True).zremrangebyrank(self.key, 0, self.cache_size)
        results, count = pipe.execute()
        return results
