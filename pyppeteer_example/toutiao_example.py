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
    browser = await launch(headless=False, args=["--disable-infobars", "--start-maximized"])

    page = await browser.newPage()
    await page.setUserAgent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36")
    # 是否启用JS，enabled设为False，则无渲染效果
    await page.setJavaScriptEnabled(enabled=True)
    # 设置页面视图大小
    await page.setViewport(viewport={"width": 1480, "height": 800})

    # 修改 navigator.webdriver 检测
    js_script = """
    () =>{ 
        Object.defineProperties(navigator,{ webdriver:{ get: () => false } });
        window.navigator.chrome = { runtime: {},  };
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], });
     }
    """

    js1 = '''() =>{Object.defineProperties(navigator,{ webdriver:{ get: () => false}})}'''
    js2 = '''() => {alert(window.navigator.webdriver)}'''
    js3 = '''() => {window.navigator.chrome = {runtime: {}, }; }'''
    js4 = '''() =>{Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});}'''
    js5 = '''() =>{Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5,6],});}'''


    # 本页刷新后值不变，自动执行js
    await page.evaluateOnNewDocument(js_script)
    await page.goto("http://www.toutiao.com")

    # await page.goto("http://www.toutiao.com", options={'timeout': 50000})
    # await page.waitForXPath("//div[@class='title-box']")
    # await page.evaluate(js1)
    # await page.evaluate(js2)
    # 鼠标滚动到底
    # await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
    await asyncio.sleep(3)

    # 打印页面cookies
    print("cookie: ", await page.cookies())
    # 打印当前页标题
    print("title: ", await page.title())
    # 获取页面内容
    content = await page.content()
    # print("content: ", content)

    # 抓取新闻标题
    title_elements = await page.xpath("//div[@class='title-box']/a")
    print(title_elements)
    for item in title_elements:
        # 获取文本

        title_str = await (await item.getProperty("textContent")).jsonValue()
        print(await item.getProperty("textContent"))
        # 获取链接
        title_link = await (await item.getProperty("href")).jsonValue()
        print(title_str)
        print(title_link)

    await asyncio.sleep(100)
    # 关闭浏览器
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())