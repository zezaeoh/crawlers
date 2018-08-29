import scrapy


class ProcessingSpider(scrapy.Spider):
    name = 'processing_start'
    custom_settings = {
        'ITEM_PIPELINES': {
            'Processing_Scheduler.pipelines.RQPipeline': 400
        }
    }

    @classmethod
    def from_crawler(cls, crawler, cycle=0, is_first=False, **kwargs):
        spider = super(ProcessingSpider, cls).from_crawler(crawler, **kwargs)
        spider.cycle = int(cycle)
        spider.is_first = bool(is_first)
        return spider

    def start_requests(self):
        yield scrapy.Request('https://google.com', callback=self.parse)

    def parse(self, response):
        item = {'cycle': self.cycle, 'is_first': self.is_first}
        return item
