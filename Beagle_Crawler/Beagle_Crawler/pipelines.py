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
        self.media = settings['DYNAMODB_COMID']

    def process_item(self, item, spider):
        item['media'] = self.media
        item = dict((k, v) for k, v in item.items() if v)
        self.q.enqueue('workFunctions.dynamo_pipe_line', item, self.table_name, result_ttl=0)
        log.msg("Post sending to RQ cache!",
                level=log.DEBUG, spider=spider)
        return item

    def close_spider(self, spider):
	    self.q.enqueue('workFunctions.process_main', self.table_name, result_ttl=0)
        print('rq connection over')

