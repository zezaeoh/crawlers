from __future__ import unicode_literals
from scrapy.conf import settings
from scrapy import log
from botocore.exceptions import ClientError
from scrapy.exporters import JsonItemExporter

import boto3


# DynamoDB에 저장하는 클래스
class DynamoDBPipeline(object):
    def __init__(self):
        connection = boto3.resource('dynamodb')
        self.table_name = 'content'
        self.index_table = 'indexes'
        self.table = connection.Table(self.table_name)
        self.store = connection.Table(self.index_table)
        self.media = settings['DYNAMODB_COMID']
        self.index = 1
        try:
            tr = self.store.get_item(
                Key={
                    'table': self.table_name
                }
            )
        except ClientError as _e:
            print(_e.response['Error']['Message'])
        else:
            if 'Item' in tr:
                self.index = int(tr['Item']['index'])

    def process_item(self, item, spider):
        item['media'] = self.media
        item['r_id'] = self.index
        self.index += 1
        self.table.put_item(Item=dict((k, v) for k, v in item.items() if v))
        log.msg("Post added to DynamoDB database!",
                level=log.DEBUG, spider=spider)
        return item

    def close_spider(self, spider):
        self.store.put_item(
            Item={
                'table': self.table_name,
                'index': self.index
            }
        )
        print('indexing over')


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
