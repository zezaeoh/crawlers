import scrapy
import re

from scrapy.loader.processors import MapCompose, Join, TakeFirst

filter_list = [
    'http',
    'https',
]
# flag_filter_list = [
#     '특정업체 거론 후기,반복적 업체노출 또는 광고성 후기,공동구매 유도글,판매글',
#     '홍보, 링크,',
#     '후기주의!'
# ]
# flag = False


def filter_strip(v):
    # global flag
    # if flag:
    #     return ''
    # for a in flag_filter_list:
    #     if a in v:
    #         flag = True
    #         return ''
    for a in filter_list:
        if a in v:
            return ''
    return v.strip()


def filter_pic(v):
    return None if not v else v


def filter_date(v):
    return [re.sub(r'(\d+)\.(\d+)\.(\d+)\. (\d+):(\d+)', r'\1-\2-\3 \4:\5', a)
            for a in re.findall(r'\d+\.\d+\.\d+\. \d+:\d+', v)]


class DachshundCrawlerItem(scrapy.Item):
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
    content = scrapy.Field(
        input_processor=MapCompose(filter_strip),
        output_processor=Join()
    )  # 내용
    date = scrapy.Field(
        input_processor=MapCompose(filter_date),
        output_processor=TakeFirst()
    )  # 날짜
    url = scrapy.Field(
        output_processor=Join()
    )  # 게시글 주소
    pic = scrapy.Field(
        input_processor=MapCompose(filter_pic)
    )  # 사진
    pass

