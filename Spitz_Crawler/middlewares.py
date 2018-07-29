from scrapy import signals
from selenium import webdriver
from scrapy.http import HtmlResponse
import time


class JavaScriptMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        s.driver = webdriver.PhantomJS()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_closed)
        return s

    def process_request(self, request, spider):
        print("rendering...")
        self.driver.get(request.url)
        time.sleep(1)
        body = self.driver.page_source.encode('utf-8')
        print("parsing... " + request.url)
        return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_closed(self, spider):
        self.driver.close()
        print("driver closed!")
