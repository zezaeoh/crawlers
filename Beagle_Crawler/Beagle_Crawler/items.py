import scrapy
import re

from scrapy.loader.processors import MapCompose, Join, TakeFirst


def filter_strip(v):
    if 'adsbygoogle' in v:
        return ''
    return v.strip()


def filter_pic(v):
    return None if not v else v


def filter_date(v):
    return re.findall(r'\d+-\d+-\d+ \d+:\d+', v)


class BeagleCrawlerItem(scrapy.Item):
    r_id = scrapy.Field()
    media = scrapy.Field()
    title = scrapy.Field(
        input_processor=MapCompose(filter_strip),
        output_processor=TakeFirst()
    )  # 제목
    writer = scrapy.Field(
        input_processor=MapCompose(filter_strip),
        output_processor=Join()
    )  # 작성자
    category = scrapy.Field(
        output_processor=Join()
    )  # 게시판 분류
    content = scrapy.Field(
        input_processor=MapCompose(filter_strip),
        output_processor=Join()
    )  # 내용
    date = scrapy.Field(
        input_processor=MapCompose(filter_date),
        output_processor=Join()
    )  # 날짜
    url = scrapy.Field(
        output_processor=Join()
    )  # 게시글 주소
    pic = scrapy.Field(
        input_processor=MapCompose(filter_pic)
    )  # 사진
    pass
