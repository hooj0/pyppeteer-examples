#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-12
# @copyright by hoojo @2020
# @changelog scrapy book spider core class


# ===============================================================================
# 标题：scrapy book core code
# ===============================================================================
# 使用：利用 scrapy 框架为书籍重命名
# -------------------------------------------------------------------------------
# 描述：读取指定目录下的文件，对文件进行豆瓣搜索重命名
# -------------------------------------------------------------------------------
import os
import logging
import scrapy
import scrapy.exceptions
from urllib.request import quote
from scrapy.cmdline import execute
from scrapy_book.items import RenameBookItem


# -------------------------------------------------------------------------------
# 构建 scrapy 框架生成爬虫书籍实体对象
# -------------------------------------------------------------------------------
class RenameBookSpider(scrapy.Spider):

    name = "rename"
    allowed_domains = ["douban.com"]
    start_urls = ["https://search.douban.com/book/subject_search"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
    }

    logger = logging.getLogger(__name__)
    
    file_dir = "books"
    search_url = "https://search.douban.com/book/subject_search?search_text=%s&cat=1001"

    def parse(self, response):
        if len(self.file_dir) == 0:
            self.logger.critical("file dir is None!")
            raise scrapy.exceptions.NotConfigured("<<<<<<<file dir configuration is None!>>>>>>>>")

        for root, dirs, files in os.walk(self.file_dir):
            for file in files:
                #self.logger.debug("find file: %s", file)
                print("find file: %s" % file)

                file_path = os.path.join(root, file)
                book_name = file.split(".")[0]

                if book_name is not None:
                    url = self.search_url % quote(book_name)
                    print("search url: ", url)

                    request = scrapy.Request(url, headers=self.headers, callback=self.parse_book_list)
                    request.cb_kwargs["book"] = {"book_name": book_name, "filename": file, "file_path": file_path}

                    yield request

    def parse_book_list(self, response, book):

        book_item = response.css("div.item-root:nth-child(0)").get()
        print("book item: ", book_item)

        if book_item is not None:
            book["url"] = book_item.css("a::attr(href)").get()

            request = scrapy.Request(book["url"], headers=self.headers, callback=self.parse_book_detail)
            request.cb_kwargs["book"] = book

            yield request

    def parse_book_detail(self, response, book):

        item = RenameBookItem()

        item["url"] = book["url"]
        item["filename"] = book["filename"]
        item["book_name"] = book["book_name"]
        item["author"] = response.css("div#info > span::text").get().replace("/", "&")\
                                .replace("作者:", "").replace("(", "[").replace(")", "]")
        item["real_name"] = "%s-%s" % (item["author"], item["filename"])

        src = book["file_path"]
        dst = os.path.join(os.path.dirname(src), "rename", item["real_name"])
        print("%s ===>>> %s" % (src, dst))

        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))

        os.rename(src, dst)

        yield item