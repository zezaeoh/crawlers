from __future__ import unicode_literals
from scrapy.conf import settings
from scrapy import log
from rq import Queue
from redis import Redis


# RQ로 보내는 클래스
class RQPipeline(object):
    def __init__(self):
        self.q = Queue(connection=Redis(host=settings['RQ_HOST'], port=settings['RQ_PORT']))
        self.table_name = 'content'

    def process_item(self, item, spider):
        self.q.enqueue('workFunctions.process_main', self.table_name, item['cycle'], item['is_first'],
                       result_ttl=0, timeout=7200)
        print('cycle:', item['cycle'])
        print('is_first:', item['is_first'])
        print("Process request sending to RQ cache!")
        return item

    def close_spider(self, spider):
        print('rq connection over')