# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyWorkerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class BookItem(scrapy.Item):
    # this class is for qidian book info
    name = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    tag = scrapy.Field()
    words = scrapy.Field()
    chapters = scrapy.Field()
    comments = scrapy.Field()

