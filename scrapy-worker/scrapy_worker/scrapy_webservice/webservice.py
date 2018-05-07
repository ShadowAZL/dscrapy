import logging
import traceback
from twisted.web import server, resource
from twisted.python import log
from twisted.web import resource

from scrapy.exceptions import NotConfigured
from scrapy import signals
from scrapy.utils.reactor import listen_tcp
from scrapy.utils.python import to_native_str
from scrapy.utils.serialize import ScrapyJSONDecoder

from scrapyd.utils import native_stringify_dict

from scrapy_webservice.serialize import ScrapyJSONEncoder
from scrapy_webservice.server import server_call
from scrapy_zookeeper.zoo_watcher import ZooWatcher, Register

logger = logging.getLogger(__name__)


class JsonResource(resource.Resource):

    def __init__(self, crawler, target=None):
        super(JsonResource, self).__init__()
        self.crawler = crawler
        self.json_encoder = ScrapyJSONEncoder()

    def render(self, txrequest):
        try:
            r = resource.Resource.render(self, txrequest)
            return self.render_object(r, txrequest).encode('utf-8')
        except Exception as e:
            log.err()
            r = {"status": "error", "message": str(e)}
            return self.render_object(r, txrequest).encode('utf-8')

    def render_object(self, obj, txrequest):
        r = self.json_encoder.encode(obj) + "\n"
        txrequest.setHeader('Content-Type', 'application/json')
        txrequest.setHeader('Access-Control-Allow-Origin', '*')
        txrequest.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, PUT, DELETE')
        txrequest.setHeader('Access-Control-Allow-Headers',' X-Requested-With')
        txrequest.setHeader('Content-Length', len(r))
        return r


class ControlResource(JsonResource):

    def __init__(self, crawler, target=None):
        JsonResource.__init__(self, crawler, target)
        self.json_decoder = ScrapyJSONDecoder()
        self.crawler = crawler
        self._target = target

    def render_GET(self, txrequest):
        return self.get_target()

    def render_POST(self, txrequest):
        reqstr = to_native_str(txrequest.content.getvalue())
        target = self.get_target()
        return server_call(target, reqstr, self.json_decoder)

    def getChild(self, name, txrequest):
        target = self.get_target()
        try:
            newtarget = getattr(target, to_native_str(name))
            return ControlResource(self.crawler, newtarget)
        except AttributeError:
            return resource.ErrorPage(404, "No Such Resource", "No such child resource.")

    def get_target(self):
        return self._target


class CrawlerResource(ControlResource):

    ws_name = 'crawler'

    def __init__(self, crawler):
        super(CrawlerResource, self).__init__(crawler, crawler)


class RootResource(JsonResource):

    def render_GET(self, txrequest):
        return {'resources': [to_native_str(k) for k in self.children.keys()]}

    def getChild(self, name, txrequest):
        if name == b'':
            return self
        return JsonResource.getChild(self, name, txrequest)


class WebService(server.Site):

    def __init__(self, crawler):
        if not crawler.settings.getbool('WEBSERVICE_ENABLED'):
            raise NotConfigured
        self.crawler = crawler
        logfile = crawler.settings['WEBSERVICE_LOGFILE']
        self.portrange = [int(x) for x in crawler.settings.getlist('WEBSERVICE_PORT', [6023, 6073])]
        self.host = crawler.settings.get('WEBSERVICE_HOST', '127.0.0.1')
        root = RootResource(crawler)
        root.putChild(b'crawler', CrawlerResource(self.crawler))
        server.Site.__init__(self, root, logPath=logfile)
        self.noisy = False
        crawler.signals.connect(self.start_listening, signals.engine_started)
        crawler.signals.connect(self.stop_listening, signals.engine_stopped)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def start_listening(self):
        self.port = listen_tcp(self.portrange, self.host, self)
        logger.debug(
            'Web service listening on {host.host:s}:{host.port:d}'.format(
                host=self.port.getHost()))

    def stop_listening(self):
        self.port.stopListening()


