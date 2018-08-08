import scrapy
import re
import os

from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.loader import ItemLoader
from Beagle_Crawler.items import BeagleCrawlerItem
from datetime import datetime


class BeagleCrawlSpiderBbs(scrapy.Spider):
    name = 'beagle_crawler_bbs'
    custom_settings = {
        'ITEM_PIPELINES': {
            'Beagle_Crawler.pipelines.DynamoDBPipeline': 400
        }
    }
    allowed_domains = ['m.ppomppu.co.kr']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BeagleCrawlSpiderBbs, cls).from_crawler(crawler, *args, **kwargs)
        spider.started_on = datetime.now()
        spider.r = re.compile(r'(\d+)-(\d+)-(\d+) (\d+):(\d+)')
        spider.p = re.compile(r'bbs_view\.php\?id=freeboard&no=.*')
        spider.prefix = 'http://m.ppomppu.co.kr/new/'
        spider.postPage = 'http://m.ppomppu.co.kr/new/bbs_list.php?id=freeboard&page={}'
        spider.i = 1
        if os.path.isfile('/var/log/{}.log'.format(cls.name)):
            with open('/var/log/{}.log'.format(cls.name), mode='rt', encoding='utf-8') as f:
                s = f.read()
                if s:
                    spider.mode = True
                    spider.url = s.split()
                    spider.furl = []
                else:
                    spider.mode = False
                    spider.url = []
                    spider.furl = []
        else:
            spider.mode = False
            spider.url = []
            spider.furl = []
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        with open('/var/log/{}.log'.format(self.name), mode='wt', encoding='utf-8') as f:
            f.write(' '.join(spider.furl))
        print('Work time:', datetime.now() - spider.started_on)

    def start_requests(self):
        url = self.postPage.format(self.i)
        rq = scrapy.Request(url, callback=self.parse)
        yield rq

    def is_okay(self, response, match):
        if self.mode:
            for t_url in self.url:
                if t_url in response.url:
                    return False
            return True
        else:
            hr = (self.started_on - datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)),
                                             int(match.group(4)), int(match.group(5))))
            if hr.days < 1:
                if (hr.seconds // 3600) > 6:
                    return False
                else:
                    return True
            else:
                return False

    def parse(self, response):
        self.url_list = []
        for link in response.xpath('//ul[@class="bbsList"]//a'):
            url = link.xpath('./@href').extract_first()
            if self.p.search(url):
                if len(self.furl) <= 5:
                    furl = self.prefix + url
                    furl = furl[:furl.find('&page')]
                    self.furl.append(furl)
                item = {'writer': link.xpath('./span[@class="ct"]/text()').extract(),
                        'title': link.xpath('./strong/text()').extract()}
                self.url_list.append({'url': self.prefix + url,
                                      'item': item})
        tmp = self.url_list.pop(0)
        next_url = tmp['url']
        rq = scrapy.Request(url=next_url, callback=self.parse_post,
                            meta={'item': tmp['item']})
        return rq

    def parse_post(self, response):
        print('parsing post..', response.url)
        i = ItemLoader(item=BeagleCrawlerItem(), response=response)
        item = response.meta['item']
        i.add_value('title', item['title'])
        i.add_value('writer', item['writer'])
        i.add_value('category', 'freeboard')
        i.add_xpath('content', '//*[@id="KH_Content"]//text()')
        i.add_xpath('date', '//*[@id="wrap"]/div[@class="ct"]/div/h4/div/span[@class="hi"]/text()')
        i.add_xpath('pic', '//*[@id="KH_Content"]//img/@src')
        i.add_value('url', response.url)
        re_i = i.load_item()
        match = self.r.search(re_i['date'])
        if match:
            if self.is_okay(response, match):
                if self.url_list:
                    tmp = self.url_list.pop(0)
                    next_url = tmp['url']
                    rq = scrapy.Request(url=next_url, callback=self.parse_post,
                                        meta={'item': tmp['item']})
                    return re_i, rq
                else:
                    self.i += 1
                    rq = scrapy.Request(self.postPage.format(self.i), callback=self.parse)
                    return re_i, rq
            else:
                raise CloseSpider('termination condition met')


class BeagleCrawlSpiderEtcInfo(scrapy.Spider):
    name = 'beagle_crawler_etc_info'
    custom_settings = {
        'ITEM_PIPELINES': {
            'Beagle_Crawler.pipelines.DynamoDBPipeline': 400
        }
    }
    allowed_domains = ['m.ppomppu.co.kr']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BeagleCrawlSpiderEtcInfo, cls).from_crawler(crawler, *args, **kwargs)
        spider.started_on = datetime.now()
        spider.r = re.compile(r'(\d+)-(\d+)-(\d+) (\d+):(\d+)')
        spider.p = re.compile(r'bbs_view\.php\?id=etc_info&no=.*')
        spider.prefix = 'http://m.ppomppu.co.kr/new/'
        spider.postPage = 'http://m.ppomppu.co.kr/new/bbs_list.php?id=etc_info&page={}'
        spider.i = 1
        if os.path.isfile('/var/log/{}.log'.format(cls.name)):
            with open('/var/log/{}.log'.format(cls.name), mode='rt', encoding='utf-8') as f:
                s = f.read()
                if s:
                    spider.mode = True
                    spider.url = s.split()
                    spider.furl = []
                else:
                    spider.mode = False
                    spider.url = []
                    spider.furl = []
        else:
            spider.mode = False
            spider.url = []
            spider.furl = []
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        with open('/var/log/{}.log'.format(self.name), mode='wt', encoding='utf-8') as f:
            f.write(' '.join(spider.furl))
        print('Work time:', datetime.now() - spider.started_on)

    def start_requests(self):
        url = self.postPage.format(self.i)
        rq = scrapy.Request(url, callback=self.parse)
        yield rq

    def is_okay(self, response, match):
        if self.mode:
            for t_url in self.url:
                if t_url in response.url:
                    return False
            return True
        else:
            hr = (self.started_on - datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)),
                                             int(match.group(4)), int(match.group(5))))
            if hr.days < 1:
                if (hr.seconds // 3600) > 6:
                    return False
                else:
                    return True
            else:
                return False

    def parse(self, response):
        self.url_list = []
        for link in response.xpath('//ul[@class="bbsList"]//a'):
            url = link.xpath('./@href').extract_first()
            if self.p.search(url):
                if len(self.furl) <= 5:
                    furl = self.prefix + url
                    furl = furl[:furl.find('&page')]
                    self.furl.append(furl)
                item = {'writer': link.xpath('./span[@class="ct"]/text()').extract(),
                        'title': link.xpath('./strong/text()').extract()}
                self.url_list.append({'url': self.prefix + url,
                                      'item': item})
        tmp = self.url_list.pop(0)
        next_url = tmp['url']
        rq = scrapy.Request(url=next_url, callback=self.parse_post,
                            meta={'item': tmp['item']})
        return rq

    def parse_post(self, response):
        print('parsing post..', response.url)
        i = ItemLoader(item=BeagleCrawlerItem(), response=response)
        item = response.meta['item']
        i.add_value('title', item['title'])
        i.add_value('writer', item['writer'])
        i.add_value('category', 'etc_info')
        i.add_xpath('content', '//*[@id="KH_Content"]//text()')
        i.add_xpath('date', '//*[@id="wrap"]/div[@class="ct"]/div/h4/div/span[@class="hi"]/text()')
        i.add_xpath('pic', '//*[@id="KH_Content"]//img/@src')
        i.add_value('url', response.url)
        re_i = i.load_item()
        match = self.r.search(re_i['date'])
        if match:
            if match:
                if self.is_okay(response, match):
                    if self.url_list:
                        tmp = self.url_list.pop(0)
                        next_url = tmp['url']
                        rq = scrapy.Request(url=next_url, callback=self.parse_post,
                                            meta={'item': tmp['item']})
                        return re_i, rq
                    else:
                        self.i += 1
                        rq = scrapy.Request(self.postPage.format(self.i), callback=self.parse)
                        return re_i, rq
                else:
                    raise CloseSpider('termination condition met')


class BeagleCrawlSpiderAppInfo(scrapy.Spider):
    name = 'beagle_crawler_app_info'
    custom_settings = {
        'ITEM_PIPELINES': {
            'Beagle_Crawler.pipelines.DynamoDBPipeline': 400
        }
    }
    allowed_domains = ['m.ppomppu.co.kr']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BeagleCrawlSpiderAppInfo, cls).from_crawler(crawler, *args, **kwargs)
        spider.started_on = datetime.now()
        spider.r = re.compile(r'(\d+)-(\d+)-(\d+) (\d+):(\d+)')
        spider.p = re.compile(r'bbs_view\.php\?id=ppomapp&no=.*')
        spider.prefix = 'http://m.ppomppu.co.kr/new/'
        spider.postPage = 'http://m.ppomppu.co.kr/new/bbs_list.php?id=ppomapp&page={}'
        spider.i = 1
        if os.path.isfile('/var/log/{}.log'.format(cls.name)):
            with open('/var/log/{}.log'.format(cls.name), mode='rt', encoding='utf-8') as f:
                s = f.read()
                if s:
                    spider.mode = True
                    spider.url = s.split()
                    spider.furl = []
                else:
                    spider.mode = False
                    spider.url = []
                    spider.furl = []
        else:
            spider.mode = False
            spider.url = []
            spider.furl = []
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        with open('/var/log/{}.log'.format(self.name), mode='wt', encoding='utf-8') as f:
            f.write(' '.join(spider.furl))
        print('Work time:', datetime.now() - spider.started_on)

    def start_requests(self):
        url = self.postPage.format(self.i)
        rq = scrapy.Request(url, callback=self.parse)
        yield rq

    def is_okay(self, response, match):
        if self.mode:
            for t_url in self.url:
                if t_url in response.url:
                    return False
            return True
        else:
            hr = (self.started_on - datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)),
                                             int(match.group(4)), int(match.group(5))))
            if hr.days < 1:
                if (hr.seconds // 3600) > 6:
                    return False
                else:
                    return True
            else:
                return False

    def parse(self, response):
        self.url_list = []
        for link in response.xpath('//ul[@class="bbsList"]//a'):
            url = link.xpath('./@href').extract_first()
            if self.p.search(url):
                if len(self.furl) <= 5:
                    furl = self.prefix + url
                    furl = furl[:furl.find('&page')]
                    self.furl.append(furl)
                item = {'writer': link.xpath('./span[@class="ct"]/text()').extract(),
                        'title': link.xpath('./strong/text()').extract()}
                self.url_list.append({'url': self.prefix + url,
                                      'item': item})
        tmp = self.url_list.pop(0)
        next_url = tmp['url']
        rq = scrapy.Request(url=next_url, callback=self.parse_post,
                            meta={'item': tmp['item']})
        return rq

    def parse_post(self, response):
        print('parsing post..', response.url)
        i = ItemLoader(item=BeagleCrawlerItem(), response=response)
        item = response.meta['item']
        i.add_value('title', item['title'])
        i.add_value('writer', item['writer'])
        i.add_value('category', 'app_info')
        i.add_xpath('content', '//*[@id="KH_Content"]//text()')
        i.add_xpath('date', '//*[@id="wrap"]/div[@class="ct"]/div/h4/div/span[@class="hi"]/text()')
        i.add_xpath('pic', '//*[@id="KH_Content"]//img/@src')
        i.add_value('url', response.url)
        re_i = i.load_item()
        match = self.r.search(re_i['date'])
        if match:
            if match:
                if self.is_okay(response, match):
                    if self.url_list:
                        tmp = self.url_list.pop(0)
                        next_url = tmp['url']
                        rq = scrapy.Request(url=next_url, callback=self.parse_post,
                                            meta={'item': tmp['item']})
                        return re_i, rq
                    else:
                        self.i += 1
                        rq = scrapy.Request(self.postPage.format(self.i), callback=self.parse)
                        return re_i, rq
                else:
                    raise CloseSpider('termination condition met')


class BeagleCrawlSpiderPpomppu(scrapy.Spider):
    name = 'beagle_crawler_ppomppu'
    custom_settings = {
        'ITEM_PIPELINES': {
            'Beagle_Crawler.pipelines.DynamoDBPipeline': 400
        }
    }
    allowed_domains = ['m.ppomppu.co.kr']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BeagleCrawlSpiderPpomppu, cls).from_crawler(crawler, *args, **kwargs)
        spider.started_on = datetime.now()
        spider.r = re.compile(r'(\d+)-(\d+)-(\d+) (\d+):(\d+)')
        spider.p = re.compile(r'bbs_view\.php\?id=ppomppu&no=.*')
        spider.prefix = 'http://m.ppomppu.co.kr/new/'
        spider.postPage = 'http://m.ppomppu.co.kr/new/bbs_list.php?id=ppomppu&page={}'
        spider.i = 1
        if os.path.isfile('/var/log/{}.log'.format(cls.name)):
            with open('/var/log/{}.log'.format(cls.name), mode='rt', encoding='utf-8') as f:
                s = f.read()
                if s:
                    spider.mode = True
                    spider.url = s.split()
                    spider.furl = []
                else:
                    spider.mode = False
                    spider.url = []
                    spider.furl = []
        else:
            spider.mode = False
            spider.url = []
            spider.furl = []
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        with open('/var/log/{}.log'.format(self.name), mode='wt', encoding='utf-8') as f:
            f.write(' '.join(spider.furl))
        print('Work time:', datetime.now() - spider.started_on)

    def start_requests(self):
        url = self.postPage.format(self.i)
        rq = scrapy.Request(url, callback=self.parse)
        yield rq

    def is_okay(self, response, match):
        if self.mode:
            for t_url in self.url:
                if t_url in response.url:
                    return False
            return True
        else:
            hr = (self.started_on - datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)),
                                             int(match.group(4)), int(match.group(5))))
            if hr.days < 1:
                if (hr.seconds // 3600) > 6:
                    return False
                else:
                    return True
            else:
                return False

    def parse(self, response):
        self.url_list = []
        for link in response.xpath('//ul[@class="bbsList"]//a'):
            url = link.xpath('./@href').extract_first()
            if self.p.search(url):
                if len(self.furl) <= 5:
                    furl = self.prefix + url
                    furl = furl[:furl.find('&page')]
                    self.furl.append(furl)
                item = {'writer': link.xpath('./p[1]/span[2]/text()').extract(),
                        'title': link.xpath('./span[@class="title"]//text()').extract()}
                self.url_list.append({'url': self.prefix + url,
                                      'item': item})
        tmp = self.url_list.pop(0)
        next_url = tmp['url']
        rq = scrapy.Request(url=next_url, callback=self.parse_post,
                            meta={'item': tmp['item']})
        return rq

    def parse_post(self, response):
        print('parsing post..', response.url)
        i = ItemLoader(item=BeagleCrawlerItem(), response=response)
        item = response.meta['item']
        i.add_value('title', item['title'])
        i.add_value('writer', item['writer'])
        i.add_value('category', 'ppomppu')
        i.add_xpath('content', '//*[@id="KH_Content"]//text()')
        i.add_xpath('date', '//*[@id="wrap"]/div[@class="ct"]/div/h4/div/span[@class="hi"]/text()')
        i.add_xpath('pic', '//*[@id="KH_Content"]//img/@src')
        i.add_value('url', response.url)
        re_i = i.load_item()
        match = self.r.search(re_i['date'])
        if match:
            if match:
                if self.is_okay(response, match):
                    if self.url_list:
                        tmp = self.url_list.pop(0)
                        next_url = tmp['url']
                        rq = scrapy.Request(url=next_url, callback=self.parse_post,
                                            meta={'item': tmp['item']})
                        return re_i, rq
                    else:
                        self.i += 1
                        rq = scrapy.Request(self.postPage.format(self.i), callback=self.parse)
                        return re_i, rq
                else:
                    raise CloseSpider('termination condition met')
