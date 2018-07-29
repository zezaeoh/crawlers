import scrapy
import re
import os
from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.loader import ItemLoader
from Spitz_Crawler.items import SpitzCrawlerItem
from datetime import datetime


class SpitzCrawlSpider(scrapy.Spider):
    name = 'spitz_crawler'
    custom_settings = {
        'ITEM_PIPELINES': {
            'Spitz_Crawler.pipelines.DynamoDBPipeline': 400
        }
    }
    allowed_domains = ['m.todayhumor.co.kr']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SpitzCrawlSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.started_on = datetime.now()
        print(spider.started_on)
        spider.r = re.compile(r'(\d+)/(\d+)/(\d+) (\d+):(\d+)')
        spider.p = re.compile(r'view.php\?table=.*')
        spider.prefix = 'http://m.todayhumor.co.kr/'
        spider.postPage = 'http://m.todayhumor.co.kr/list.php?table=total&page={}'
        spider.i = 1
        if os.path.isfile('/var/log/spitz_crawler.log'):
            with open('/var/log/spitz_crawler.log', mode='rt', encoding='utf-8') as f:
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
        with open('/var/log/spitz_crawler.log', mode='wt', encoding='utf-8') as f:
            f.write(' '.join(spider.furl))
        print('Work time:', datetime.now() - spider.started_on)

    def start_requests(self):
        url = self.postPage.format(self.i)
        rq = scrapy.Request(url, callback=self.parse)
        yield rq

    def parse(self, response):
        for link in response.xpath('/html/body//a'):
            url = link.xpath('./@href').extract_first()
            if self.p.search(url):
                if len(self.furl) <= 5:
                    furl = self.prefix + url
                    furl = furl[:furl.find('&page')]
                    self.furl.append(furl)
                item = {}
                item['date'] = link.xpath('./div/div[2]/span[2]/text()').extract_first()
                match = self.r.search(item['date'])
                if match:
                    if self.mode:
                        for t_url in self.url:
                            if t_url in (self.prefix + url):
                                raise CloseSpider('termination condition met')
                    else:
                        hr = (self.started_on - datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)),
                                                         int(match.group(4)), int(match.group(5))))
                        if hr.days < 1:
                            if (hr.seconds // 3600) > 6:
                                raise CloseSpider('termination condition met')
                        else:
                            raise CloseSpider('termination condition met')
                item['writer'] = link.xpath('./div/div[2]/span[3]/text()').extract()
                item['title'] = link.xpath('./div/div[3]/h2/text()').extract()
                rq = scrapy.Request(self.prefix + url, callback=self.parse_post)
                rq.meta['item'] = item
                yield rq
        self.i += 1
        rq = scrapy.Request(self.postPage.format(self.i), callback=self.parse)
        yield rq

    def parse_post(self, response):
        print('paring post..', response.url)
        i = ItemLoader(item=SpitzCrawlerItem(), response=response)
        item = response.meta['item']
        i.add_value('title', item['title'])
        i.add_value('writer', item['writer'])
        i.add_xpath('content', '/html/body//div[@class="viewContent"]/text()')
        i.add_xpath('content', '/html/body//div[@class="viewContent"]//*[not(self::script)]/text()')
        i.add_xpath('content', '/html/body//div[@class="viewContent"]//*[not(self::script)]//*[not(self::script)]/text()')
        i.add_value('date', item['date'])
        i.add_xpath('pic', '/html/body//div[@class="viewContent"]//img/@src')
        i.add_value('url', response.url)
        return i.load_item()
