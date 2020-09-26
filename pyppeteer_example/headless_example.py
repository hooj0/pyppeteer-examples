#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog launch parameter headless show browser for Chromium


# ===============================================================================
# 标题：launch parameter headless
# ===============================================================================
# 使用：利用 pyppeteer 框架参数查看浏览器
#
#     # headless 参数设置为 False 运行后可以看到 浏览器 Chromium
#     browser = await launch(headless=False)
# -------------------------------------------------------------------------------
# 描述：设置不同的参数，查看浏览器
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例，利用框架参数查看浏览器
# -------------------------------------------------------------------------------
import asyncio
from pyppeteer import launch


async def main():

    """
    参数 headless，默认值 True
        如果我们将它设置为 True 或者默认不设置它，在启动的时候我们是看不到任何界面的，
        如果把它设置为 False，那么在启动的时候就可以看到界面，

        一般我们在调试的时候会把它设置为 False，在生产环境上就可以设置为 True
    """

    # headless 参数设置为 False 运行后可以看到 浏览器 Chromium
    browser = await launch(headless=False)
    await asyncio.sleep(100)
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())