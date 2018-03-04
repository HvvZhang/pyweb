# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from scrapy.pipelines.images import ImagesPipeline

# 再进入这个pipeline,保存到数据库或文件
class PywebPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open("article.json", "w", encoding="utf-8")
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False)+'\n'
        self.file.write(lines)
        return item  # 下一个pipeline可能用到
    def spider_closed(self, spider):
        self.file.close()

# 先进入这个piipeline，自己处理一些数据的赋值完善item
class ArticleImagePipeline(ImagesPipeline):
    # 重载item_completed,得到实际下载地址
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value["path"]
        item["front_image_path"] = image_file_path
        return item