# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse  # 组合url
from pyweb.items import JobboleArticleItem, ArticleItenLoader
from pyweb.utils.common import get_md5
from scrapy.loader import ItemLoader  # 方便维护爬取规则

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        '''
        1. 文章列表页获取url并解析
        2. 跳到列表页下一页，执行1.
        '''
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            # 文章详情页解析，交给scrapy下载
            image_url = post_node.css("img::attr(src)").extract_first()
            post_url = post_node.css("::attr(href)").extract_first()
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)
        # 提取下一页
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_urls:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    def parse_detail(self, response):
        # 解析具体的页面
        article_item = JobboleArticleItem()

        # 通过Itemloader加载Item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader = ArticleItenLoader(item=JobboleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)  # 直接添加值
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_time", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content","div.entry")
        article_item = item_loader.load_item()

        yield article_item  # 传递到pipelines


        # item_loader.add_xpath()
        # xpath方式
        # 文章标题
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")
        # 封面,在标题页不在详情页，通过meta传到详情页，get获取字典没有为空不抛异常
        # 文章时间
        # create_time = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace(
        #     " ·", "")
        # 赞的数量
        # praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        # 收藏数量
        # fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # comment_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract()[0]
        # tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()

        '''
         urljoin使用方法：
         urljoin("http://www.google.com/1/aaa.html","bbbb.html")
        'http://www.google.com/1/bbbb.html'
         urljoin("http://www.google.com/1/aaa.html","2/bbbb.html")
        'http://www.google.com/1/2/bbbb.html'
         urljoin("http://www.google.com/1/aaa.html","/2/bbbb.html")
        'http://www.google.com/2/bbbb.html'
         urljoin("http://www.google.com/1/aaa.html","http://www.google.com/3/ccc.html")
        'http://www.google.com/3/ccc.html'
         urljoin("http://www.google.com/1/aaa.html","http://www.google.com/ccc.html")
        'http://www.google.com/ccc.html'
         urljoin("http://www.google.com/1/aaa.html","javascript:void(0)")
        'javascript:void(0)'
        
        '''