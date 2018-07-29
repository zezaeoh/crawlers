from __future__ import unicode_literals
from scrapy.conf import settings
from scrapy import log
from datetime import datetime

import boto3
import uuid


# DynamoDB에 저장하는 클래스
class DynamoDBPipeline(object):
    def __init__(self):
        connection = boto3.resource('dynamodb')
        table = connection.Table('com_raw')
        self.comID = settings['DYNAMODB_COMID']
        self.table = table

    def process_item(self, item, spider):
        item['comID'] = self.comID
        item['postID'] = datetime.now().strftime('%Y%m%d%H%M%S%f') + uuid.uuid4().hex
        self.table.put_item(Item=dict((k, v) for k, v in item.items() if v))
        log.msg("Post added to DynamoDB database!",
                level=log.DEBUG, spider=spider)
        return item

