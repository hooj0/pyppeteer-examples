#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog first pyppeteer example, crawling `quotes.toscrape.com` data


# ===============================================================================
# 标题：first pyppeteer example
# ===============================================================================
# 使用：利用 pyppeteer 框架爬取网页的动态数据
# -------------------------------------------------------------------------------
# 描述：第一个上手示例，利用框架爬取动态数据
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例
# 如果没有安装 pyquery 可以进行安装，pyquery是jquery的翻版
#       pip install pyquery
# -------------------------------------------------------------------------------
import asyncio
from pyppeteer import launch
from pyquery import PyQuery


async def main():

    # 启动浏览器
    browser = await launch()
    # 打开一个新页面
    page = await browser.newPage()
    # 地址栏跳转到当前网址
    await page.goto("http://quotes.toscrape.com/js/")

    # 获取网页内容，关键一步
    content = await page.content()

    # 解析转换数据，利用PyQeruy进行数据查找
    pq = PyQuery(content)
    print("quote：", pq(".quote").length)

    # 关闭浏览器
    await browser.close()

# 利用异步方式执行函数
asyncio.get_event_loop().run_until_complete(main())

