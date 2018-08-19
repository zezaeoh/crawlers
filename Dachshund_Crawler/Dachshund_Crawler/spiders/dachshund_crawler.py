import scrapy
import re
import os

from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.loader import ItemLoader
from Dachshund_Crawler.items import DachshundCrawlerItem
from datetime import datetime


class DachshundCrawlSpider(scrapy.Spider):
    name = 'dachshund_crawler'
    custom_settings = {
        'ITEM_PIPELINES': {
            'Dachshund_Crawler.pipelines.RQPipeline': 400
        }
    }
    allowed_domains = ['m.cafe.naver.com']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DachshundCrawlSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.started_on = datetime.now()
        spider.visited_links = set()
        spider.r = re.compile(r'(\d+)-(\d+)-(\d+) (\d+):(\d+)')
        spider.p = re.compile(r'/ArticleRead.nhn\?clubid=10298136.*articleid=(\d+).*')
        spider.clubid = 'clubid=10298136'
        spider.articleid = 'articleid='
        spider.article = '/ArticleRead.nhn?%s&articleid={}' % spider.clubid
        spider.prefix = 'https://m.cafe.naver.com'
        spider.postPage = 'https://m.cafe.naver.com/ArticleList.nhn?search.clubid=10298136&search.page={}'
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
        rq.meta['reconnect'] = False
        yield rq

    def is_okay(self, response, match):
        if self.mode:
            for t_url in self.url:
                if t_url in response.url and self.clubid in response.url:
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
        for link in response.xpath('//*[@id="articleListArea"]/ul//li'):
            url = link.xpath('./a[1]/@href').extract_first()
            match = self.p.search(url)
            if match:
                if len(self.furl) <= 10:
                    furl = self.articleid + match.group(1)
                    self.furl.append(furl)
                item = {'writer': link.xpath('./a[1]/div[@class="user_area"]/span[@class="nick"]//text()').extract(),
                        'title': link.xpath('./a[1]/strong[@class="tit"]/text()').extract()}
                self.url_list.append({'url': self.prefix + self.article.format(match.group(1)),
                                      'item': item})
        while True:
            if not self.url_list:
                return
            tmp = self.url_list.pop(0)
            if tmp['url'] not in self.visited_links:
                next_url = tmp['url']
                break
        rq = scrapy.Request(url=next_url, callback=self.parse_post,
                            meta={'item': tmp['item'], 'reconnect': False})
        self.visited_links.add(next_url)
        return rq

    def parse_post(self, response):
        print('parsing post..', response.url)
        i = ItemLoader(item=DachshundCrawlerItem(), response=response)
        item = response.meta['item']
        i.add_value('title', item['title'])
        i.add_value('writer', item['writer'])
        i.add_xpath('content', '//*[@id="postContent"]//text()')
        i.add_xpath('date', '//*[@id="ct"]//span[@class="date font_l"]/text()')
        i.add_xpath('date', '//*[@id="ct"]//span[@class="board_time"]//text()')
        i.add_xpath('date', '//*[@id="ct"]/div[@class="post "]/div[@class="post_info"]//text()')
        i.add_xpath('date', '//*[@id="ct"]/div[@class="post"]/div[@class="post_info"]//text()')
        i.add_xpath('pic', '//*[@id="postContent"]//img/@src')
        i.add_value('url', response.url)
        re_i = i.load_item()
        if 'date' not in re_i:
            tmp = response.xpath('//div[@class="error_content_body"]/h2//text()').extract()
            print('connection error')
            for a in tmp:
                if '카페 멤버만 볼 수 있습니다.' in a:
                    print('try reconnection')
                    rq = scrapy.Request(url=response.url, callback=self.parse_post, dont_filter=True,
                                        meta={'item': item, 'reconnect': True})
                    return rq
            print('move on to next url')
            if self.url_list:
                tmp = self.url_list.pop(0)
                next_url = tmp['url']
                rq = scrapy.Request(url=next_url, callback=self.parse_post,
                                    meta={'item': tmp['item'], 'reconnect': False})
                self.visited_links.add(next_url)
                return rq
            else:
                self.i += 1
                rq = scrapy.Request(self.postPage.format(self.i), dont_filter=True, callback=self.parse)
                rq.meta['reconnect'] = False
                return rq
        match = self.r.search(re_i['date'])
        if match:
            if self.is_okay(response, match):
                if self.url_list:
                    tmp = self.url_list.pop(0)
                    next_url = tmp['url']
                    rq = scrapy.Request(url=next_url, callback=self.parse_post,
                                        meta={'item': tmp['item'], 'reconnect': False})
                    self.visited_links.add(next_url)
                    return re_i, rq
                else:
                    self.i += 1
                    rq = scrapy.Request(self.postPage.format(self.i), dont_filter=True, callback=self.parse)
                    rq.meta['reconnect'] = False
                    return re_i, rq
            else:
                raise CloseSpider('termination condition met')
