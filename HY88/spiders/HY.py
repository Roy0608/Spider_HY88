# -*- coding: utf-8 -*-
import scrapy


class HySpider(scrapy.Spider):
    name = 'HY'
    allowed_domains = ['huangye88.com']
    start_urls = ['http://huangye88.com/']

    def parse(self, response):
        pass
