# -*- coding: utf-8 -*-
from __future__ import absolute_import
import json
import re

from extension.spiders import DCrawlSpider
from scrapy.http import Request
from scrapy.spiders.crawl import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider
from scrapy_redis.spiders import RedisCrawlSpider


from scrapy_worker.items import BookItem


class QidianSpider(RedisCrawlSpider):
    name = 'qidian'
    allowed_domains = ['qidian.com']

    start_urls = ['https://www.qidian.com/all']
    rules = [
        Rule(LinkExtractor(restrict_css=('.all-img-list .book-img-box a',)), callback='parse_profile_page', follow=True),
        Rule(LinkExtractor(restrict_css=('.lbf-pagination-item-list .lbf-pagination-next ',)), follow=True),
    ]

    def parse_profile_page(self, response):
        # self.logger.debug('Parse Profile Page. URL :  %s' % response.url)
        book = BookItem()

        name = response.css('.book-information .book-info  h1 em::text').extract_first()
        url = response.url
        author = response.css('.book-information .book-info .writer::text').extract_first()

        tag = response.xpath('string(//div[contains(@class,"book-information")]/div[contains(@class,"book-info")]/p[@class="tag"])').extract_first()
        tag = re.sub('\s+', ' ', tag)

        words = response.css('.book-information .book-info p em::text').extract_first()
        chapters = response.css('.j_catalog_block a i span::text').extract_first()
        comments = response.css('.j_discussion_block a i span::text').extract_first()

        book['name'] = name
        book['url'] = url
        book['author'] = author
        book['tag'] = tag
        book['words'] = words
        book['chapters'] = chapters
        book['comments'] = comments

        yield book
