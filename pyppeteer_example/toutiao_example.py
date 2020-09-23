#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog pyppeteer spider toutiao.com data


# ===============================================================================
# 标题：pyppeteer spider toutiao.com data
# ===============================================================================
# 使用：利用 pyppeteer 框架爬取头条数据
# -------------------------------------------------------------------------------
# 描述：测试利用 pyppeteer 框架爬取头条数据
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例，测试利用 pyppeteer 框架爬取头条数据
# -------------------------------------------------------------------------------
import asyncio
from pyppeteer import launch


async def main():
    # headless参数设为False，则变成有头模式
    browser = await launch(
        # headless=False
    )

    page = await browser.newPage()

    # 设置页面视图大小
    await page.setViewport(viewport={"width":1280, "height":800})

    # 是否启用JS，enabled设为False，则无渲染效果
    await page.setJavaScriptEnabled(enabled=True)

    await page.goto("https://www.toutiao.com/")

    # 打印页面cookies
    print(await page.cookies())
    # 打印当前页标题
    print(await page.title())
    # 获取页面内容
    content = await page.content()

    # 抓取新闻标题
    title_elements = await page.xpath("//div[@class='title-box']/a")
    for item in title_elements:
        # 获取文本
        title_str = await (await item.getProperty("textContent")).jsonValue()
        print(await item.getProperty("textContent"))
        # 获取链接
        title_link = await (await item.getProperty("href")).jsonValue()
        print(title_str)
        print(title_link)

    # 关闭浏览器
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())