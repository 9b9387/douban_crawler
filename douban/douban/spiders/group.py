# -*- coding: utf-8 -*-
import scrapy


class GroupSpider(scrapy.Spider):
    name = 'group'
    allowed_domains = ['group.douban.com']
    start_urls = ['https://www.douban.com/group/topic/132914779/']
    
    def parse(self, response):
        for comment in response.css('li.comment-item'):
            yield {
                'content': comment.css('div.content').css('p::text').get(),
            }
