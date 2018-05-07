from scrapy_splash.request import SplashRequest
from scrapy import Request


class DSplashRequest(SplashRequest):

    def __init__(self, *args, **kwargs):
        splash_args = kwargs.setdefault('args', {})
        splash_args['wait'] = 0.5
        super(DSplashRequest, self).__init__(*args, **kwargs)


class PhantomjsRequest(Request):

    def __init__(self, url, callback=None, method='GET', meta={}, **kwargs):
        meta.setdefault('phantomjs', {})
        super(PhantomjsRequest, self).__init__(url, callback, method, meta=meta, **kwargs)
