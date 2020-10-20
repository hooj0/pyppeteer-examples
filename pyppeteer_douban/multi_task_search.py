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
import asyncio
import re
import os
import shutil
import random
from pyppeteer import launch


# -------------------------------------------------------------------------------
# 构建多个任务查询图书操作
# -------------------------------------------------------------------------------
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
        "nick_name": "".join(nick_name).replace('"', '”').strip(),
        "publish_org": "".join(publish_org).strip(),
        "publish_date": "".join(publish_date).strip(),
        "price": "".join(price).strip(),
        "isbn": "".join(isbn).strip(),
    }


async def request(n, text, page):
    # 设置请求URL
    url = f"https://search.douban.com/book/subject_search?search_text={text}&cat=1001"
    # 地址栏跳转到当前网址
    response = await page.goto(url)
    print("[book consumer-%s] request url: %s" % (n, response.url))

    # 获取网页内容
    content = await page.content()
    print("[book consumer-%s] search: %s, content: %s" % (n, await page.title(), len(content)))

    subject = await page.J("#wrapper div.item-root > a[href^='https://book.douban.com/subject/']")
    if subject:
        # html = await page.Jeval("#wrapper div.item-root > a[href^='https://book.douban.com/subject/']", "node => node.outerHTML")
        # print("subject html: ", html)

        # 休眠1秒
        await asyncio.sleep(1)

        # 等待新页面加载完成
        await asyncio.gather(
            page.waitForNavigation(),
            subject.click(),
        )

        title = await page.title()
        content = await page.content()
        print("[book consumer-%s] title: %s, content: %s" % (n, title, len(content)))

        interest_sectl = await page.J("div#interest_sectl")
        if not interest_sectl:
            print("[book consumer-%s] 非图书，无法提取到相关记录：%s\n" % (n, text))
            return None

        name = await page.Jeval("div#wrapper h1", "node => node.innerText")
        author = await page.JJeval("div#wrapper div#info > span:nth-child(1) a[href]", """nodes => {
            var authors = [];
            nodes.forEach(function (item) {
                authors.push(item.innerText);
            });
            return authors.join(" & ");
        }""")

        if not author:
            author = await page.Jeval("div#wrapper div#info a[href]", "node => node.innerText")

        score = await page.Jeval("div#interest_sectl strong.rating_num", "node => node.innerText")
        star = await page.Jeval("div#interest_sectl div.rating_right div.ll", "node => node.className.replace('ll bigstar', '')")
        # num = await page.Jeval("div#interest_sectl div.rating_right a.rating_people span", "node => node.innerText")
        num = await page.Jeval("div#interest_sectl div.rating_right", "node => node.innerText")

        tags = ""
        tags_el = await page.J("div#wrapper div#db-tags-section")
        if tags_el:
            tags = await tags_el.Jeval("div.indent", "node => node.innerText")

        book_info_text = await page.Jeval("div#wrapper div#info", "node => node.textContent")
        book_info = extract(book_info_text)
        # print("[book consumer-%s] book info: %s" % (n, book_info))

        book = {
            "name": name.replace('"', '”'), "author": author,
            "score": score, "star": star, "num": num,
            "tags": tags.replace(" ", "").replace("\xa0", ", ")
        }

        # print("[book consumer-%s] book: %s\n" % (n, book))

        book.update(book_info)
        return book
    else:
        print("[book consumer-%s] 没有搜索到相关记录：%s\n" % (n, text))
        return None


async def search(book_names):

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

    for book in book_names:
        await request(book, page)

    await asyncio.sleep(100)
    # 关闭浏览器
    await browser.close()


# -------------------------------------------------------------------------------
# 队列写入，读取操作
# -------------------------------------------------------------------------------
async def book_consumer(n, queue):
    """
        电子书订阅者，获取图书信息队列中的书籍信息，去豆瓣图书中提取图书的详细信息
    """

    print("[book consumer-%s] start " % n)

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

    # 创建一个集合存储书籍信息
    book_metadata = {}
    while True:
        print("[book consumer-%s] waiting" % n)

        book = await queue.get()
        print("[book consumer-%s] get queue data: %s" % (n, book))

        if book is None:
            queue.task_done()
            break
        else:
            await asyncio.sleep(random.randint(2, 6))
            print("[book consumer-%s] sleep" % n)

            book_data = await request(n, book["book_name"], page)
            print("[book consumer-%s] return book data: %s" % (n, book_data))

            book_metadata[book["file_path"]] = book_data

            queue.task_done()

    # print("[book consumer-%s] book metadata: %s" % (n, book_metadata))
    print("[book consumer-%s] finished " % n)

    # await asyncio.sleep(20)
    # 关闭浏览器
    await browser.close()

    return book_metadata


async def book_producer(size, queue, file_dir):
    """
        电子书信息生产者，扫描指定目录下的图书文件，将图书名称保存到队列中
    """

    print("[book producer] start")

    if not file_dir:
        print("[book producer] file dir is None!")
        return

    for root, dirs, files in os.walk(file_dir):
        for file in files:
            # print("[book producer] find file: %s" % file)

            file_path = os.path.join(root, file)
            book_name = file.split(".")[0]

            if book_name is not None:
                book = {"book_name": book_name, "filename": file, "file_path": file_path}

                await queue.put(book)
                print("[book producer] queue put: ", book)

    print("[book producer] queue put None stopped")
    for _ in range(size):
        await queue.put(None)

    print("[book producer] queue join clear")
    await queue.join()
    print("[book producer] finished")


async def book_spider(file_dir, consumer_num=1, queue_size=5):
    """
        :param file_dir: 查询的文件目录，目录中存放已有的书籍信息
        :param consumer_num: 消费者数量，数量越多并发越多
        :param queue_size: 队列大小
    """
    print("[book spider] run...")

    # 创建一个队列，最大的长度是 size
    queue = asyncio.Queue(maxsize=queue_size)
    # 创建消费者
    consumers = [loop.create_task(book_consumer(i, queue)) for i in range(1, consumer_num + 1)]
    # 创建一个生产者的任务
    producers = loop.create_task(book_producer(consumer_num, queue, file_dir))

    print("[book spider] wait consumers/producers run")
    # 等待consumers, producers 所有的函数执行完成
    done, pending = await asyncio.wait(consumers + [producers])
    # 获取返回值，包装成集合
    book_metadata = {}
    for task in done:
        if task.result():
            book_metadata.update(task.result())

    print("[book spider] run finished")
    return book_metadata


def book_rename(book_metadata):

    for book_file_name, book in book_metadata.items():
        # print("key: %s, value: %s" % (book_file_name, book))
        if not book:
            continue

        src = book_file_name
        suffix = book_file_name.split(".")[-1]
        if book["nick_name"]:
            dst_file = "{author}-{name}：{nick_name}.{0}".format(suffix, **book)
        else:
            dst_file = "{author}-{name}.{0}".format(suffix, **book)

        dst = os.path.join(os.path.dirname(src), "rename", dst_file)
        print("%s ===>>> %s" % (src, dst))

        dst = os.path.join("rename-book-files", dst_file)
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))

        # os.rename(src, dst)
        shutil.move(src, dst)
        # shutil.copy(src, dst)


loop = asyncio.get_event_loop()

try:
    print("going event loop")
    result = loop.run_until_complete(book_spider("f:/book-files", queue_size=20, consumer_num=1))
    print("result: ", result)

    book_rename(result)
finally:
    print("close event loop")
    loop.close()

# 利用异步方式执行函数
# text_list = ["传", "afafdafd", "人民", "小狗钱钱"]
# asyncio.get_event_loop().run_until_complete(search(text_list))