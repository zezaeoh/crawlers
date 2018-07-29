import scrapy
from scrapy.loader.processors import MapCompose, Join, TakeFirst

filter_list = [
    'http',
    'https',
    'adsbygoogle'
]


def filter_strip(v):
    for a in filter_list:
        if a in v:
            return ''
    return v.strip()


class SpitzCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    comID = scrapy.Field()
    postID = scrapy.Field()
    title = scrapy.Field(
        input_processor=MapCompose(filter_strip),
        output_processor=TakeFirst()
    )  # 제목
    writer = scrapy.Field(
        input_processor=MapCompose(filter_strip),
        output_processor=Join()
    )  # 작성자
    content = scrapy.Field(
        input_processor=MapCompose(filter_strip),
        output_processor=Join()
    )  # 내용
    date = scrapy.Field(
        input_processor=MapCompose(filter_strip),
        output_processor=Join()
    )  # 날짜
    url = scrapy.Field(
        output_processor=Join()
    )  # 게시글 주소
    pic = scrapy.Field()  # 사진
    pass
