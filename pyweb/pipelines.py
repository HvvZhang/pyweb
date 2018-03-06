# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi  # 将mysqldb一些操作变成异步化操作

import MySQLdb  # mycqlclient
import MySQLdb.cursors


# 再进入这个pipeline,保存到数据库或文件
class PywebPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):
    # 同步机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'mysql123456', 'jobbole', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article(title, create_time, url, url_object_id, comment_nums, fav_nums, praise_nums, tags, content)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql, (
            item["title"], item["create_time"], item["url"], item["url_object_id"], item["comment_nums"],
            item["fav_nums"], item["praise_nums"], item["tags"], item["content"]))
        self.conn.commit()

# 支持关系数据库异步，适用于爬取速度大于插入数据库速度
class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        # 可变化参数
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # 处理异常

    def handle_error(self, failure):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
                    insert into article(title, create_time, url, url_object_id, comment_nums, fav_nums, praise_nums, tags, content)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """
        cursor.execute(insert_sql, (item["title"], item["create_time"], item["url"], item["url_object_id"], item["comment_nums"],
            item["fav_nums"], item["praise_nums"], item["tags"], item["content"]))


# 保存到json文件
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open("article.json", "w", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(lines)
        return item  # 下一个pipeline可能用到

    def spider_closed(self, spider):
        self.file.close()


# 先进入这个pipeline，自己处理一些数据的赋值完善item
class ArticleImagePipeline(ImagesPipeline):
    # 重载item_completed,得到实际下载地址
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        return item
