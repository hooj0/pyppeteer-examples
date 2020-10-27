#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-24
# @copyright by hoojo @2020
# @changelog use pyppeteer search `douban` book category


# ===============================================================================
# 标题：search `douban` book category
# ===============================================================================
# 使用：利用 pyppeteer 框架进行豆瓣图书查询
# -------------------------------------------------------------------------------
# 描述：利用框架进行简单搜索豆瓣图书分类
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 构建查询图书操作
# -------------------------------------------------------------------------------
import asyncio
import os
from pyppeteer import launch


def screen_size():
    """
    使用tkinter获取屏幕大小
    """
    import tkinter
    tk = tkinter.Tk()

    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()

    tk.quit()

    return width, height


async def request(page, text):
    # 设置请求URL
    url = f"http://read.douban.com/category?kind={text}"
    # 地址栏跳转到当前网址
    response = await page.goto(url)
    print("request url: ", response.url)
    print("title: %s, ok: %s" % (await page.title(), response.ok))

    await page.click("a.select-control")

    panel = await page.J("div.selector-panel")
    if panel:
        select_list = await page.JJ("div.select-group ul.select-option-list")

        subject_el = await select_list[1].J("a.selected")
        subject = await (await subject_el.getProperty("textContent")).jsonValue()

        categories = await select_list[2].JJeval("a.select-option", """nodes => {
            var categories = [];
            nodes.forEach(function (item) {
                if (item.innerText != '全部') {
                    categories.push(item.innerText);
                }
            });
            return categories;
        }""")

        for category in categories:
            dst = os.path.join("ebook", subject, category)
            print("dst: ", dst)

            if not os.path.exists(dst):
                os.makedirs(dst)

        print("categories: ", categories)
    else:
        print("没有搜索到相关记录：", text)


async def spider():

    # 获取屏幕尺寸
    width, height = screen_size()
    # 启动浏览器
    # browser = await launch()
    browser = await launch(headless=False, dumpio=True, args=["--disable-infobars", "--start-maximized"])
    # 打开一个新页面
    page = await browser.newPage()
    # 设置页面视图大小
    await page.setViewport(viewport={"width": width, "height": height})
    # 设置 user-agent 模拟浏览器操作
    await page.setUserAgent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36")

    await request(page, 2)
    for i in range(100, 112):
        await asyncio.sleep(2)
        await request(page, i)

    # 关闭浏览器
    await browser.close()


asyncio.get_event_loop().run_until_complete(spider())