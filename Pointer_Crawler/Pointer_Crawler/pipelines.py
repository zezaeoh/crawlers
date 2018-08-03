from __future__ import unicode_literals
from scrapy.exporters import JsonItemExporter
from scrapy.conf import settings
from scrapy import log
from datetime import datetime

import boto3
import uuid


# JSON파일로 저장하는 클래스 (test)
class JsonPipeline(object):
    def __init__(self):
        self.file = open("pointer_test.json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# DynamoDB에 저장하는 클래스
class DynamoDBPipeline(object):
    def __init__(self):
        connection = boto3.resource('dynamodb')
        table = connection.Table('com_raw')
        self.comID = settings['DYNAMODB_COMID']
        self.table = table

    def process_item(self, item, spider):
        item['comID'] = self.comID
        item['postID'] = datetime.now().strftime('%Y%m%d%H%M%S%f')[:15] + uuid.uuid4().hex[:5]
        self.table.put_item(Item=dict((k, v) for k, v in item.items() if v))
        log.msg("Post added to DynamoDB database!",
                level=log.DEBUG, spider=spider)
        return item
