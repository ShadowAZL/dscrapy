# -*- coding: utf-8 -*-
import scrapy
from w3lib.html import remove_tags

from scrapy.spiders import Spider


class IPPrxoySpider(Spider):
    name = 'ipproxy'
    start_urls = ['http://www.xicidaili.com/nn/',
                  'http://www.xicidaili.com/nt/',
                  'http://www.xicidaili.com/wn/',
                  'http://www.xicidaili.com/wt/']

    test_url = 'http://www.w3school.com.cn'
    test_code = '06004630'

    def parse(self, response):
        ip_list = response.css('#ip_list tr')
        for ip_item in ip_list:
            items = ip_item.css('td').extract()
            if items:
                ip = remove_tags(items[1])
                port = remove_tags(items[2])
                schema = remove_tags(items[5]).lower()
                yield scrapy.Request(self.test_url, callback=self.test_proxy,
                                     meta={'proxy': '%s://%s:%s' % (schema, ip, port), 'download_timeout': 1},
                                     dont_filter=True)
        pass

    def test_proxy(self, response):
        if self.test_code in response.text:
            print(response.request.meta['proxy'])
            self.crawler.stats.inc_value('porxy/count')
            yield {'Proxy': response.request.meta['proxy']}
