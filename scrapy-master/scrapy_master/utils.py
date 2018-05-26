import logging
import requests
from six.moves.urllib_parse import urljoin
from redis import StrictRedis
from datetime import datetime


logger = logging.getLogger(__name__)


class RedisAgent(object):
    def __init__(self, settings):
        self.settings = settings
        self.redis_cli = StrictRedis(host=settings['REDIS_HOST'], port=settings['REDIS_PORT'])

    def send_start_urls(self, start_urls=None):
        start_urls = start_urls or self.settings['START_URLS']
        key = self.settings['START_URLS_KEY']
        request_key = self.settings['REQUEST_KEY']
        if self.redis_cli.zcard(request_key):
            logger.info("Resuming crawl")
            return False
        self.redis_cli.delete(key)
        self.redis_cli.lpush(key, *start_urls)
        logger.info('Send Start URL')
        return True

    def get_all_stats(self):
        return self.redis_cli.hgetall(self.settings['STATS_KEY'])

    def get_stats(self, name):
        return self.redis_cli.hget(self.settings['STATS_KEY'], name)


def json_parse(method, url, param=None, files=None):
    try:
        if method == 'POST':
            r = requests.post(url, data=param, files=files)
        else:
            r = requests.get(url, params=param)
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

    try:
        return r.json()
    except Exception as e:
        logger.exception(e)
        return {'status': 'error', 'message': str(e)}


def schedule(host, **param):
    """ Schedule a spider run (also known as a job), returning the job id.
        Supported Request Methods: POST
        Parameters:
            project (string, required) - the project name
            spider (string, required) - the spider name
            setting (string, optional) - a Scrapy setting to use when running the spider
            jobid (string, optional) - a job id used to identify the job, overrides the default generated UUID
            _version (string, optional) - the version of the project to use
            any other parameter is passed as spider argument
    """
    url = urljoin(host, 'schedule.json')
    return json_parse('POST', url, param)


def cancel(host, **param):
    """ Cancel a spider run (aka. job). If the job is pending, it will be removed. If the job is running, it will be terminated.
        Supported Request Methods: POST
        Parameters:
            project (string, required) - the project name
            job (string, required) - the job id
    """
    url = urljoin(host, 'cancel.json')
    return json_parse('POST', url, param)
