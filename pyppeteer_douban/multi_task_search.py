#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-25
# @copyright by hoojo @2020
# @changelog use pyppeteer many task search `douban` book


# ===============================================================================
# 标题：many task search `douban` book
# ===============================================================================
# 使用：利用 pyppeteer 框架进行豆瓣图书查询
# -------------------------------------------------------------------------------
# 描述：利用框架进行多个任务模式，搜索豆瓣图书
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 构建多个任务查询图书操作
# -------------------------------------------------------------------------------
import asyncio
import re
import queue
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


def extract(book_info):
    nick_name = re.findall(r"副标题:(.*?)\n", book_info)
    publish_org = re.findall(r"出版社:(.*?)\n", book_info)
    publish_date = re.findall(r"出版年:(.*?)\n", book_info)
    price = re.findall(r"定价:(.*?)\n", book_info)
    isbn = re.findall(r"ISBN:(.*?)\n", book_info)

    return {
        "nick_name": "".join(nick_name).strip(),
        "publish_org": "".join(publish_org).strip(),
        "publish_date": "".join(publish_date).strip(),
        "price": "".join(price).strip(),
        "isbn": "".join(isbn).strip()
    }


async def request_book(text, page):
    # 设置请求URL
    url = f"https://search.douban.com/book/subject_search?search_text={text}&cat=1001"
    # 地址栏跳转到当前网址
    response = await page.goto(url)
    print("request url: ", response.url)

    # 获取网页内容
    content = await page.content()
    print("search: %s, content: %s" % (await page.title(), len(content)))

    subject = await page.J("#wrapper div.item-root > a[href^='https://book.douban.com/subject/']")
    if subject:
        # html = await page.Jeval("#wrapper div.item-root > a[href^='https://book.douban.com/subject/']", "node => node.outerHTML")
        # print("subject html: ", html)

        # 等待新页面加载完成
        await asyncio.gather(
            page.waitForNavigation(),
            subject.click(),
        )

        title = await page.title()
        content = await page.content()
        print("title: %s, content: %s" % (title, len(content)))

        interest_sectl = await page.J("div#interest_sectl")
        if not interest_sectl:
            print("非图书，无法提取到相关记录：%s\n" % text)
            return None

        name = await page.Jeval("div#wrapper h1", "node => node.innerText")
        author = await page.Jeval("div#wrapper div#info a[href]", "node => node.innerText")

        score = await page.Jeval("div#interest_sectl strong.rating_num", "node => node.innerText")
        star = await page.Jeval("div#interest_sectl div.rating_right div.ll", "node => node.className.replace('ll bigstar', '')")
        num = await page.Jeval("div#interest_sectl div.rating_right a.rating_people", "node => node.innerText")

        tags = await page.Jeval("div#wrapper div#db-tags-section div.indent", "node => node.innerText")

        book_info_text = await page.Jeval("div#wrapper div#info", "node => node.textContent")
        book_info = extract(book_info_text)
        print("book info: ", book_info)

        book = {
            "name": name, "author": author,
            "score": score, "star": star, "num": num,
            "tags": tags.replace(" ", "").replace("\xa0", ", ")
        }

        print("book: ", book)
    else:
        print("没有搜索到相关记录：", text)


async def search():

    # 获取屏幕尺寸
    width, height = screen_size()
    # 启动浏览器
    # browser = await launch()
    browser = await launch(headless=False, dumpio=True, args=["--disable-infobars", "--start-maximized"])
    """
    if browser.pages() <= 5:
        #  创建新窗口
        page = await browser.newPage()
        
        pass
    else:
        # 等待已创建打开的窗口完成任务

        # 等待某个请求完成
        response = await page.waitForResponse(lambda res: res.url == 'http://example.com' and res.status == 200)
        if response.ok:
            pass
        pass
    """

    for i in range(3):
        # 打开一个新页面
        page = await browser.newPage()
        # 设置页面视图大小
        await page.setViewport(viewport={"width": width, "height": height})
        # 设置 user-agent 模拟浏览器操作
        await page.setUserAgent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36")

        # 等待队列清空
        while not queue.empty():
            text = queue.get_nowait()
            await request_book(text, page)

            print("\n")
            await asyncio.sleep(2)

    await asyncio.sleep(100)
    # 关闭浏览器
    await browser.close()


# 利用异步方式执行函数
text_list = ["传", "afafdafd", "人民", "小狗钱钱"]

queue = queue.Queue(10)
queue.put("传")
queue.put("afafdafd")
queue.put("传")
queue.put("人民")
queue.put("小狗钱钱")
queue.put("成功")
queue.put("战胜")

asyncio.get_event_loop().run_until_complete(search())