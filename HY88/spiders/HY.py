# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from HY88.items import Hy88Item


class HySpider(scrapy.Spider):
    name = 'HY'  # 爬虫名
    allowed_domains = ['huangye88.com']  # 域名
    start_urls = ['http://b2b.huangye88.com/region/']  #起始地址

    def parse(self, response):
        city_urls = response.xpath('//dl[@id="clist"]/dd/a/@href').extract()  # A-Z城市url
        for city_url in city_urls:
            #print(city_url)
            yield scrapy.Request(
                city_url,
                callback=self.parse_reg_urls  # 市所属的区县
            )

    def parse_reg_urls(self, response):
        reg_urls = response.xpath('//div[@id="subarealist"]/div[2]/a/@href').extract() # 区县url
        for reg_url in reg_urls:
            #print(reg_url)
            yield scrapy.Request(
                reg_url,
                callback=self.parse_ind_urls  # 不同行业和所属省市区
            )

    def parse_ind_urls(self, response):
        # item = Hy88Item()
        item = {}
        # 省
        item['pro'] = response.xpath('//div[@class="subNav"]/a[2]/text()').extract()[0][:-4]
        # 市
        item['city'] = response.xpath('//div[@class="subNav"]/a[3]/text()').extract()[0][:-4]
        # 区县
        item['reg'] = response.xpath('//div[@class="subNav"]/text()').extract()[2].replace(
            ' » ','').replace('\r\n','').split('市',1)[1].split('企')[0]
        # 行业url
        ind_urls = response.xpath('//div[@class="tag_tx"]/ul/li/a/@href').extract()
        for ind_url in ind_urls:
            #print(ind)
            #print(item)
            yield scrapy.Request(
                ind_url,
                callback=self.parse_ind_det,  # 企业信息
                meta={'item1': deepcopy(item)},
                dont_filter=True
            )

    def parse_ind_det(self, response):
        item = response.meta['item1']
        # 公司url
        det_urls = response.xpath(
            '//form[@id="jubao"]/dl[@itemtype="http://data-vocabulary.org/Organization"]/dt/h4/a/@href').extract()
        # item['com_name'] = response.xpath(
            # '//form[@id="jubao"]/dl[@itemtype="http://data-vocabulary.org/Organization"]/dt/h4/a/text()').extract()
        # print(item)
        if det_urls is not None:
            for det_url in det_urls:
                det_url = det_url + 'company_detail.html'  # 公司详情的url
                #print(det_url)
                yield scrapy.Request(
                    det_url,
                    callback=self.parse_com_det,  # 详细信息
                    meta={'item2': deepcopy(item)},
                    dont_filter=True
                )
        # 列表页翻页
        next_url = response.xpath(
            '//div[@class="page_tag Baidu_paging_indicator"]/a[contains(text(), "下一页")]/@href').extract_first()
        if next_url is not None:
            #print('------下一页------')
            yield scrapy.Request(
                next_url,
                callback=self.parse_ind_det,
                meta={'item': deepcopy(item)},
                dont_filter=True
            )

    def parse_com_det(self, response):
        item = response.meta['item2']
        # 1.公司资料
        item['com_name'] = response.xpath('//div[@class="data"]/p/text()').extract_first() # 公司名
        info = response.xpath('//div[@class="data"]/ul[@class="con-txt"]/li')
        com_info = []
        for i in info:
            com_info.append("".join(i.xpath('.//text()').extract()))
        # 把列表转换成字符串并用逗号把每个信息隔开
        item['com_info'] = ",".join(com_info) # 公司资料信息
        # 2.公司介绍
        item['com_intro'] = "".join(
            response.xpath('//div[@class="r-content"]/p[@class="txt"]//text()').extract()) # 公司介绍信息
        # 3.详细资料（表格）
        info2 = response.xpath('//p[@class="txt"]/following-sibling::table[1]/tr')
        det_info = []
        for j in info2:
            det_info.append("：".join(j.xpath('./td//text()').extract()))
        # 把列表转换成字符串并用逗号把每个信息隔开
        item['det_info'] = ",".join(det_info) # 公司详细资料信息
        cont_url = response.xpath('//div[@class="nav"]/ul/a/li[contains(text(), "联系我们")]/../@href').extract_first()
        #yield item
        yield scrapy.Request(
            cont_url,
            callback=self.parse_cont_det,
            meta={'item3': deepcopy(item)},
            dont_filter=True
        )

    def parse_cont_det(self, response):
        item = response.meta['item3']
        info2 = response.xpath('//div[@class="site"]/ul[@class="con-txt"]/li')
        cont_info = []
        for i in info2:
            cont_info.append("".join(i.xpath('.//text()').extract()))
        # 把列表转换成字符串并用逗号把每个信息隔开
        item['cont_info'] = ",".join(cont_info)  # 公司资料信息
        yield item





