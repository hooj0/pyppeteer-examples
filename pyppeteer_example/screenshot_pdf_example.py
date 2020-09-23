#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog second pyppeteer example, crawling page data and screenshot pdf file


# ===============================================================================
# 标题：second pyppeteer example
# ===============================================================================
# 使用：利用 pyppeteer 框架爬取网页的动态数据，并且进行截图生成PDF文件，执行特定的JS代码
# -------------------------------------------------------------------------------
# 描述：利用框架截屏生成PDF文档
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例，利用框架截屏生成PDF文档
# -------------------------------------------------------------------------------
import asyncio
from pyppeteer import launch


async def main():

    browser = await launch()
    page = await browser.newPage()

    resp = await page.goto(url="http://quotes.toscrape.com/js/", options={'timeout': 30000})
    print("响应头: ", resp.headers)
    print("响应状态: ", resp.status)

    # screenshot 方法可以传入保存的图片路径，
    # 还可以指定保存格式 type、清晰度 quality、是否全屏 fullPage、裁切 clip 等各个参数实现截图
    await page.screenshot(path="tmp/example.png")
    # 可以指定放缩大小 scale、页码范围 pageRanges、宽高 width 和 height、方向 landscape
    await page.pdf(path="tmp/example.pdf")

    # 执行特定的JavaScript代码
    result = await page.evaluate("""() => {
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight,
            deviceScaleFactor: window.devicePixelRatio
        }
    }""")

    print("result: ", result)
    # result:  {"width': 800, 'height': 600, 'deviceScaleFactor': 1}

    # 获取网页body文本内容，force_expr=True，强制Pyppeteer作为表达式处理
    text_content = await page.evaluate("document.body.textContent", force_expr=True)
    print("text content: ", text_content)

    element = await page.querySelector("h1")
    # 获取 h1 标签的文本内容
    title = await page.evaluate("(element) => element.textContent", element)
    print("title: ", title)

    # 滚动到页面底部
    await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")

    await browser.close()

asyncio.get_event_loop().run_until_complete(main())