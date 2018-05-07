from scrapy_redis.spiders import RedisSpider, RedisCrawlSpider
from scrapy.http import Request, TextResponse


class DSpiderMixin(object):
    """The purpose of this Spider is to merge Splash and Redis, and extend to PhantomJS

    Attributes
    ----------
    requestFactory :  <class : scrapy.http.Request> subclass
        we use this factory to create new request.If you want to use splash to render html,
        you should replace it with SplashRequest.
    """
    requestFactory = Request

    def make_requests_from_url(self, url):
        return self.requestFactory(url, dont_filter=True)

    def _build_request(self, rule, link):
        r = self.requestFactory(url=link.url, callback=self._response_downloaded)
        r.meta.update(rule=rule, link_text=link.text)
        return r

    def _requests_to_follow(self, response):
        if not isinstance(response, TextResponse):
            return
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                yield rule.process_request(r)


class DSpider(DSpiderMixin, RedisSpider):
    pass


class DCrawlSpider(DSpiderMixin, RedisCrawlSpider):
    pass
