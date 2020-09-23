#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog use web browser user cookie cache


# ===============================================================================
# 标题：use web browser user cookie cache
# ===============================================================================
# 使用：利用 pyppeteer 框架参数设置浏览器缓存，免去频繁登录操作
# -------------------------------------------------------------------------------
# 描述：设置参数，免去频繁登录操作
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例，设置参数免去频繁登录操作
# -------------------------------------------------------------------------------
import asyncio
from pyppeteer import launch


async def main():

    # userDataDir 缓存用户数据
    browser = await launch(headless=False, userDataDir="user-data", args=['--disable-infobars'])
    page = await browser.newPage()

    # 设置内容页面大小
    await page.setViewport(viewport={"width": 1280, "height": 800})
    # 首次登录后，下一次可以“手动”跳过登录
    await page.goto("https://www.taobao.com")

    # 利用浏览器执行特定脚本，绕过 webdriver 检测
    await page.evaluate("""() => {
        Object.defineProperties(navigator, {
            webdriver: {
                    get: () => false
                }
            })
    }""")

    await asyncio.sleep(100)
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())