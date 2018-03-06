# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re
#from scrapy import Item
from scrapy.loader.processors import MapCompose, TakeFirst, Join   #传递任意多的函数
from scrapy.loader import ItemLoader # 重载它

class PywebItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    pass


def add_jobbole(value):
    return  value+".jobbole"


def time_convert(value):
    try:
        create_time = datetime.datetime.strptime(value, "%y/%m/%d").date()
    except Exception as e:
        create_time = datetime.datetime.now().date()
    return create_time

# 点赞收藏评论共用
def get_nums(value):
    match_re = re.match(".*(\d+).*", value)
    if match_re:  # 如果匹配成功，取第一个（）内
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    # 去除tags中的评论
    if "评论" in value:
        return ""
    else:
        return value

def return_value(value):
    return value

class ArticleItenLoader(ItemLoader):
    #只取itemloader形成的list的第一个
    default_output_processor = TakeFirst()

class JobboleArticleItem(scrapy.Item):

    title = scrapy.Field(
        input_processor = MapCompose(lambda x:x+"-jobbole", add_jobbole)

    )
    create_time = scrapy.Field(
        input_processor = MapCompose(time_convert),
    )

    url = scrapy.Field()
    #URL地址处理为MD5格式,为了安全,存储方便,不会因为编码方式的差异而出现存取时的乱码现象
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    # tags本身已经是list
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    content = scrapy.Field()
