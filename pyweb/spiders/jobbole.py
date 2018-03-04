# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse  # 组合url
from pyweb.items import JobboleArticleItem
from pyweb.utils.common import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        '''
        1. 文章列表页获取url并解析
        2. 跳到列表页下一页，执行1.

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
        article_item = JobboleArticleItem()

        # 封面,在标题页不在详情页，通过meta传到详情页，get获取字典没有为空不抛异常
        front_image_url = response.meta.get("front_image_url", "")
        # 文章标题
        title = response.css('.entry-header h1::text').extract_first()
        # 文章时间
        create_time = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace(
            " ·", "")
        # 赞的数量
        praise_nums = response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        # 收藏数量
        fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        match_re = re.match(".*(\d+).*", fav_nums)
        if match_re:  # 如果匹配成功，取第一个（）内
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0
        # 评论数量
        comment_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        match_re = re.match(".*(\d+).*", comment_nums)
        print(match_re)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0


        # 内容html格式，待进一步分析
        content = response.xpath('//div[@class="entry"]').extract()[0]

        tag_list = response.xpath(
            '//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()  # ['其他', ' 18 评论 ', '招聘', '程序员', '职场']

        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]  # ['其他', '招聘', '程序员', '职场']

        tags = ','.join(tag_list)  # '其他,招聘,程序员,职场'
        article_item["url_object_id"] = get_md5(response.url)
        article_item["title"] = title
        article_item["url"] = response.url  # 从哪个url获取的
        try:
            create_time = datetime.datetime.strptime(create_time,"%y/%m/%d").date()
        except Exception as e:
            create_time = datetime.datetime.now().date()
        article_item["create_time"] = create_time
        article_item["front_image_url"] = [front_image_url]
        article_item["praise_nums"] = praise_nums
        article_item["comment_nums"] = comment_nums
        article_item["fav_nums"] = fav_nums
        article_item["tags"] = tags
        article_item["content"] = content

        yield article_item  # 传递到pipelines
