#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog request & response interception result


# ===============================================================================
# 标题：request & response intercept
# ===============================================================================
# 使用：利用 pyppeteer 框架对请求之前和之后的操作进行拦截处理
#
#     # 启用 request 拦截
#     await page.setRequestInterception(True)
#
#     page.on("request", request_handler)
#     page.on("response", response_handler)
# -------------------------------------------------------------------------------
# 描述：通过拦截请求可以在请求之前做一些固定的操作，通过在请求完成后做些固定操作
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例，利用框架拦截请求
# -------------------------------------------------------------------------------
import asyncio
import json
from jsonpath import jsonpath
from pyppeteer import launch
from pyppeteer.network_manager import Request, Response


# 请求开始之前触发
async def request_handler(req: Request):
    # print("request header: ", req.headers)
    await req.continue_()


# 请求完成之后触发
async def response_handler(resp: Response):
    # print("response url: ", resp.url)

    if "apub/json/prevent.new" in resp.url:
        print("请求结果拦截……")
        text = await resp.text()

        title = jsonpath(json.loads(text), "$..title")
        print("title: ", title)


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


async def main():

    w, h = screen_size()
    print(f'设置窗口为：width：{w} height：{h}')

    browser = await launch(headless=False, userDataDir="user-data", args=[
        "--disable-infobars", "--no-sandbox",
        "--start-maximized",     # 最大化窗口
        # f'--window-size={w},{h}' # 设置窗口大小
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
    ])

    page = await browser.newPage()

    # 设置内容页面大小
    await page.setViewport(viewport={"width": w, "height": h})
    # 启用JavaScript
    await page.setJavaScriptEnabled(True)
    # 启用 request 拦截
    await page.setRequestInterception(True)

    page.on("request", request_handler)
    page.on("response", response_handler)

    # await page.goto("https://news.qq.com/")

    # 修改 navigator.webdriver 检测
    js_script = """
    () =>{ 
        Object.defineProperties(navigator,{ webdriver:{ get: () => false } });
        window.navigator.chrome = { runtime: {},  };
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], });
     }
    """
    # 本页刷新后值不变，自动执行js
    await page.evaluateOnNewDocument(js_script)
    await page.goto("https://news.qq.com/")

    # 关闭网页
    await page.close()
    # 关闭浏览器
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())