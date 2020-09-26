#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog launch parameter devtools show browser and open dev mode


# ===============================================================================
# 标题：launch parameter devtools
# ===============================================================================
# 使用：利用 pyppeteer 框架参数查看浏览器,，并打开开发者调试工具
#
# browser = await launch(devtools=True, args=["--disable-infobars"])
# -------------------------------------------------------------------------------
# 描述：设置不同的参数，查看浏览器和打开开发者调试工具
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例，利用框架参数查看浏览器和打开开发者调试工具
# -------------------------------------------------------------------------------
import asyncio
from pyppeteer import launch


async def main():
    """
        将 devtools 参数设置为 True，这样每开启一个界面就会弹出一个调试窗口，非常方便调试操作
    """
    # devtools 参数设置 True，那么 headless 就会被关闭，界面始终会显现出来
    # browser = await launch(devtools=True)

    # 关掉提示："Chrome 正受到自动测试软件的控制"
    browser = await launch(devtools=True, args=["--disable-infobars"])
    page = await browser.newPage()
    # 设置请求头userAgent，用 手机的方式打开
    await page.setUserAgent("Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Mobile Safari/537.36")
    await page.goto("https://www.baidu.com")

    await asyncio.sleep(100)
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())