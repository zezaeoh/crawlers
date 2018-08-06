from __future__ import unicode_literals
from scrapy.conf import settings
from scrapy import log
from botocore.exceptions import ClientError

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

