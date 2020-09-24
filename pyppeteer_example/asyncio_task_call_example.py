#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog asyncio task callback function, crawling `quotes.toscrape.com` data


# ===============================================================================
# 标题：asyncio task callback function
# ===============================================================================
# 使用：利用 pyppeteer 框架结合协程完成异步回调
# -------------------------------------------------------------------------------
# 描述：利用Python协程实现异步回调
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例，利用Python协程实现异步回调
# -------------------------------------------------------------------------------
import asyncio
from pyppeteer import launch
from pyquery import PyQuery


async def page_content():

    # 启动浏览器
    browser = await launch()
    # 打开一个新页面
    page = await browser.newPage()
    # 地址栏跳转到当前网址
    await page.goto("http://quotes.toscrape.com/js/")

    # 获取网页内容，关键一步
    content = await page.content()
    return content


def parser(task):
    print(task)
    content = task.result()
    # 解析转换数据，利用PyQeruy进行数据查找
    pq = PyQuery(content)
    print("quote：", pq(".quote").length)


tasks = []
task1 = asyncio.ensure_future(page_content())
task1.add_done_callback(parser)
tasks.append(task1)

task2 = asyncio.ensure_future(page_content())
task2.add_done_callback(parser)
tasks.append(task2)

# 利用异步方式执行函数
asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))

