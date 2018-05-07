from scrapy import signals
from .queue import Base


class PriorityCacheQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""
    def __init__(self, *args, **kwargs):
        self.cache_size = kwargs.pop('cache_size', 10)
        self.enqueue_cache = []
        self.dequeue_cache = []
        super(PriorityCacheQueue, self).__init__(*args, **kwargs)

        self.spider.crawler.signals.connect(self.flush, signal=signals.spider_idle)

    def __len__(self):
        """Return the length of the queue"""
        return self.server.zcard(self.key)

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
        if not self.dequeue_cache:
            self.fetch()

        if self.dequeue_cache:
            return self._decode_request(self.dequeue_cache.pop())

    def flush(self):
        if not self.enqueue_cache:
            return
        pipe = self.server.pipeline(transaction=False)
        for score, data in self.enqueue_cache:
            pipe.execute_command('ZADD', self.key, score, data)
        pipe.execute()
        self.enqueue_cache.clear()

    def fetch(self):
        # use atomic range/remove using multi/exec
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, self.cache_size, desc=True).zremrangebyrank(self.key, 0, self.cache_size)
        results, count = pipe.execute()
        if results:
            self.dequeue_cache = results

        if len(self.enqueue_cache) > self.cache_size or len(self.dequeue_cache) == 0:
            self.flush()
