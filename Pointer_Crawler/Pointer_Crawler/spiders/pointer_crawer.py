import scrapy
import re
import os

from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.loader import ItemLoader
from Pointer_Crawler.items import PointerCrawlerItem
from datetime import datetime


class PointerCrawlSpider(scrapy.Spider):
    name = 'pointer_crawler'
    custom_settings = {
        'ITEM_PIPELINES': {
            'Pointer_Crawler.pipelines.JsonPipeline': 400
        }
    }
    allowed_domains = ['m.clien.net']

    @classmethod
    def from_crawler(cls, crawler, **kwargs):
        spider = super(PointerCrawlSpider, cls).from_crawler(crawler, **kwargs)
        spider.started_on = datetime.now()
        spider.visited_links = set()
        spider.r = re.compile(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)')
        spider.p = re.compile(r'/service/board/.*/\d+\?.*')
        spider.prefix = 'https://m.clien.net'
        spider.postPage = 'https://m.clien.net/service/group/clien_all?&od=T31&po={}'
        spider.i = 0
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
        flag = False
        for link in response.xpath('/html/body/div[@class="nav_container"]/div[@class="content_list"]//div[@class="list_item symph-row"]'):
            url = link.xpath('./div[@class="list_title"]/a[@class="list_subject"]/@href').extract_first()
            if self.p.search(url):
                if len(self.furl) <= 5:
                    furl = self.prefix + url
                    furl = furl[:furl.find('?')]
                    self.furl.append(furl)
                item = {
                    'title': link.xpath('./div[@class="list_title"]/a[@class="list_subject"]/span[1]/text()').extract()
                }
                self.url_list.append({'url': self.prefix + url[:url.find('?')],
                                      'item': item})
        while True:
            if not self.url_list:
                if flag:
                    self.i += 1
                    rq = scrapy.Request(self.postPage.format(self.i), dont_filter=True, callback=self.parse)
                    return rq
                else:
                    print('page parsing error!!')
                    return
            tmp = self.url_list.pop(0)
            if tmp['url'] not in self.visited_links:
                next_url = tmp['url']
                break
            flag = True
        rq = scrapy.Request(url=next_url, callback=self.parse_post,
                            meta={'item': tmp['item']})
        self.visited_links.add(next_url)
        return rq

    def parse_post(self, response):
        print('parsing post..', response.url)
        i = ItemLoader(item=PointerCrawlerItem(), response=response)
        item = response.meta['item']
        i.add_value('title', item['title'])
        i.add_xpath('writer', '//div[@class="post_contact"]/span[@class="contact_name"]/span/img/@alt')
        i.add_xpath('writer', '//div[@class="post_contact"]/span[@class="contact_name"]/span/text()')
        i.add_xpath('content', '//div[@class="post_content"]/article//text()')
        i.add_xpath('date', '//div[@class="post_time"]/span[1]//text()')
        i.add_xpath('pic', '//div[@class="post_content"]/article//img/@src')
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
                    self.visited_links.add(next_url)
                    return re_i, rq
                else:
                    self.i += 1
                    rq = scrapy.Request(self.postPage.format(self.i), callback=self.parse)
                    return re_i, rq
            else:
                raise CloseSpider('termination condition met')
