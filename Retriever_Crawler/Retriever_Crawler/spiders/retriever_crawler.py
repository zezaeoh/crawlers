import scrapy
import re
import os

from scrapy import signals
from scrapy.exceptions import CloseSpider
from scrapy.loader import ItemLoader
from Retriever_Crawler.items import RetrieverCrawlerItem
from datetime import datetime

'''
community
board_list = [
    '300148',  # 정치유머 게시판             1분 약 300건
    '300143',  # 유머 게시판                 7분 약 2000건
    '300147',  # 고민정보 게시판             2초 약 10건
    '300117',  # 음식 갤러리                 2초 약 10건
    '300100',  # 여행 갤러리                 0초 약 1건
    '102230',  # 던전앤파이터 게시판 전체글  24초 약 100건
    '101289',  # 디아블로 게시판 전체글      0초 약 1건
    '184032',  # 오버워치 PC 게시판 전체글   1초 약 7건
    '182656',  # 오버워치 콘솔 게시판 전체글 0초 약 1건
    '184404',  # 소녀전선 게시판 전체글      6초 약 30건
    '100159',  # WOW 게시판 전체글           11초 약  60건
]
'''


class RetrieverCrawlSpider(scrapy.Spider):
    name = 'retriever_crawler'
    custom_settings = {
        'ITEM_PIPELINES': {
            'Retriever_Crawler.pipelines.JsonPipeline': 400
        }
    }
    allowed_domains = ['m.ruliweb.com']

    @classmethod
    def from_crawler(cls, crawler, board_id='', **kwargs):
        spider = super(RetrieverCrawlSpider, cls).from_crawler(crawler, **kwargs)
        spider.board_id = board_id
        spider.started_on = datetime.now()
        spider.visited_links = set()
        spider.r = re.compile(r'(\d+)-(\d+)-(\d+) (\d+):(\d+):(\d+)')
        spider.p = re.compile(r'http://m\.ruliweb\.com/community/board/{}/read/.*'.format(board_id))
        spider.postPage = 'http://m.ruliweb.com/community/board/%s?page={}' % board_id
        spider.i = 1
        spider.url_list = []
        if os.path.isfile('/var/log/{}.log'.format(cls.name + '_' + spider.board_id)):
            with open('/var/log/{}.log'.format(cls.name + '_' + spider.board_id), mode='rt', encoding='utf-8') as f:
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
        with open('/var/log/{}.log'.format(self.name + '_' + self.board_id), mode='wt', encoding='utf-8') as f:
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

    def get_filtered_request(self, is_parse=False):
        if is_parse and not self.url_list:
            print('parsing page error!')
            raise CloseSpider('parsing page error!')
        while True:
            if not self.url_list:
                self.i += 1
                rq = scrapy.Request(self.postPage.format(self.i), callback=self.parse)
                return rq
            tmp = self.url_list.pop(0)
            if tmp['url'] not in self.visited_links:
                next_url = tmp['url']
                break
        rq = scrapy.Request(url=next_url, callback=self.parse_post,
                            meta={'item': tmp['item']})
        self.visited_links.add(next_url)
        return rq

    def parse(self, response):
        self.url_list.clear()
        for link in response.xpath('//table[@class="board_list_table"]/tbody//tr[@class="table_body"]'):
            url = link.xpath('./td[@class="subject"]/div[@class="title row"]/a[@class="subject_link deco"]/@href').extract_first()
            if self.p.search(url):
                if len(self.furl) <= 5:
                    furl = url[:url.find('?')]
                    self.furl.append(furl)
                item = {
                    'writer': link.xpath('./td[@class="subject"]/div[@class="info row"]/span[@class="writer text_over"]/text()').extract(),
                    'title': link.xpath('./td[@class="subject"]/div[@class="title row"]/a[@class="subject_link deco"]/text()').extract()
                }
                self.url_list.append({'url': url[:url.find('?')],
                                      'item': item})
        rq = self.get_filtered_request(is_parse=True)
        return rq

    def parse_post(self, response):
        print('parsing post..', response.url)
        i = ItemLoader(item=RetrieverCrawlerItem(), response=response)
        item = response.meta['item']
        i.add_value('title', item['title'])
        i.add_value('writer', item['writer'])
        i.add_value('category', self.board_id)
        i.add_xpath('content', '//*[@id="board_read"]//div[@class="view_content"]//text()')
        i.add_xpath('date', '//*[@id="board_read"]//span[@class="regdate"]//text()')
        i.add_xpath('pic', '//*[@id="board_read"]//div[@class="view_content"]//img/@src')
        i.add_value('url', response.url)
        re_i = i.load_item()
        match = self.r.search(re_i['date'])
        if match:
            if self.is_okay(response, match):
                rq = self.get_filtered_request()
                return re_i, rq
            else:
                print('termination condition met')
                raise CloseSpider('termination condition met')
