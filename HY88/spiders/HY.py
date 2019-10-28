# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy


class HySpider(scrapy.Spider):
    name = 'HY'  # 爬虫名
    allowed_domains = ['huangye88.com']  # 域名
    start_urls = ['http://b2b.huangye88.com/region/']  #起始地址

    def parse(self, response):
        city_urls = response.xpath('//dl[@id="clist"]/dd/a/@href').extract()  # 城市url
        for city in city_urls:
            print(city)
            yield scrapy.Request(
                city,
                callback=self.parse_reg_urls  # 市所属的区县
            )

    def parse_reg_urls(self, response):
        reg_urls = response.xpath('//div[@id="subarealist"]/div[2]/a/@href').extract() # 区县url
        for reg in reg_urls:
            print(reg)
            yield scrapy.Request(
                reg,
                callback=self.parse_ind_urls  # 不同行业和所属省市区
            )

    def parse_ind_urls(self, response):
        item = {}
        # 省
        item['pro'] = response.xpath('//div[@class="subNav"]/a[2]/text()').extract()[0][:-4]
        # 市
        item['city'] = response.xpath('//div[@class="subNav"]/a[3]/text()').extract()[0][:-4]
        # 区
        item['reg'] = response.xpath('//div[@class="subNav"]/text()')\
                                            .extract()[2].replace(' » ','').replace('\r\n','')

        ind_urls = response.xpath('//div[@class="tag_tx"]/ul/li/a/@href').extract() # 行业url
        for ind in ind_urls:
            print(ind)
            print(item)
            # yield scrapy.Request(
            #     ind,
            #     callback=self.parse_ind_cont,  # 企业信息
            #     meta={'item': deepcopy(item)},
            #     dont_filter=True
            # )

