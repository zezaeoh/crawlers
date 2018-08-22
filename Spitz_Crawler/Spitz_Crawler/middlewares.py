from scrapy import signals, Request
from selenium import webdriver
from scrapy.http import HtmlResponse
from scrapy.exceptions import CloseSpider

import time


class JavaScriptMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        s.driver = webdriver.PhantomJS()
        s.retry = 0
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_request(self, request, spider):
        print("rendering...")
        self.driver.get(request.url)
        time.sleep(1)
        body = self.driver.page_source.encode('utf-8')
        print("parsing... " + request.url)
        self.retry = 0
        return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        print("rendering error occurred!")
        print(str(exception))
        self.retry += 1
        if self.retry > 10:
            raise CloseSpider('max retries exceeded!')
        print("move to next url")
        if spider.url_list:
            tmp = spider.url_list.pop(0)
            next_url = tmp['url']
            rq = Request(url=next_url, callback=spider.parse_post,
                                meta={'item': tmp['item']})
            spider.visited_links.add(next_url)
            return rq
        else:
            spider.i += 1
            rq = Request(spider.postPage.format(spider.i), dont_filter=True, callback=spider.parse)
            return rq

    def spider_closed(self, spider):
        self.driver.quit()
        print("driver closed!")
