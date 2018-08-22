from scrapy import signals
from selenium import webdriver
from scrapy.http import HtmlResponse
from scrapy.exceptions import CloseSpider
from selenium.common.exceptions import TimeoutException

import time


class JavaScriptMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        s.driver = webdriver.PhantomJS()
        s.driver.set_page_load_timeout(10)
        s.retry = 0
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_request(self, request, spider):
        print("rendering...")
        try:
            self.driver.get(request.url)
        except TimeoutException:
            print('time out! rendering restart')
            return request
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
        rq = spider.get_filtered_request()
        return rq

    def spider_closed(self, spider):
        self.driver.quit()
        print("driver closed!")
