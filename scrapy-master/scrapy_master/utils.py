from redis import StrictRedis
from datetime import datetime


class RedisAgent(object):
    def __init__(self, settings):
        self.settings = settings
        self.redis_cli = StrictRedis(host=config['REDIS_HOST'], port=config['REDIS_PORT'])

    def send_start_urls(self, start_urls=None):
        start_urls = start_urls or self.settings['START_URLS']
        key = self.settings['START_URLS_KEY']
        self.redis_cli.lpush(key, *start_urls)
        return True

    def get_all_stats(self):
        return self.redis_cli.hgetall(self.settings['STATS_KEY'])

    def get_stats(self, name):
        return self.redis_cli.hget(self.settings['STATS_KEY'], name)

    def _get_time(self, key):
        t = self.get_stats(key)
        if not t:
            return datetime.utcnow()
        else:
            return datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f')

    def get_elapsed_time(self):
        start_time = self._get_time('start_time')
        end_time = self._get_time('finish_time')
        return (end_time - start_time).seconds

    def get_crawl_speed(self):
        delta = self.get_elapsed_time()
        response_speed = int(self.get_stats('downloader/response_bytes') or 0) / (delta or 1)
        return '%.2f kb/s' % response_speed


