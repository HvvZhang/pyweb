# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
#from scrapy import Item

class PywebItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    pass

class JobboleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_time = scrapy.Field()
    url = scrapy.Field()
    #URL地址处理为MD5格式,为了安全,存储方便,不会因为编码方式的差异而出现存取时的乱码现象
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
