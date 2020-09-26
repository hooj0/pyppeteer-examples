#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog pyppeteer async multitaskging execute result


# ===============================================================================
# 标题：async multitaskging execute
# ===============================================================================
# 使用：利用 pyppeteer 框架同时执行多个任务并返回结果
#
#     task_urls = [
#         "https://www.baidu.com",
#         "https://www.qq.com",
#     ]
#
#     tasks = (html(task_url, 300) for task_url in task_urls)
#
#     loop = asyncio.get_event_loop()
#     results = loop.run_until_complete(asyncio.gather(*tasks))
#
#     for result in results:
#         print("{} result: {}".format(result["title"], result))
# -------------------------------------------------------------------------------
# 描述：尝试利用异步方式同时执行多个爬虫，并返回正常的结果
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例，多任务执行
# -------------------------------------------------------------------------------
import asyncio
from pyppeteer import launch


async def html(url, timeout=30):
    """
    # timeout 设置浏览器超时限制
    browser = await launch(headless=True, dumpio=True, timeout=(1000 * timeout), args=[
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
    ])
    """
    browser = await launch(headless=True, dumpio=True)

    page = await browser.newPage()
    # 使用默认超时限制
    # response = await page.goto(url)
    # 设置请求超时限制
    response = await page.goto(url, {timeout: (timeout * 1000)})
    # timeout 设置为0 关闭默认超时限制
    # response = await page.goto(url, {"timeout": 0})

    title = await page.title()
    content = await page.content()
    cookie = await page.cookies()
    header = response.headers
    status = response.status

    # 关闭网页
    await page.close()
    # 关闭浏览器
    await browser.close()

    return {
        "title": title,
        "content": len(content),
        "cookie": len(cookie),
        "header": header,
        "status": status
    }


if __name__ == "__main__":

    task_urls = [
        "https://www.baidu.com",
        "https://www.qq.com",
        "https://www.douban.com",
        "https://www.163.com",
    ]

    tasks = (html(task_url, 300) for task_url in task_urls)

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(*tasks))

    for result in results:
        print("{} result: {}".format(result["title"], result))