#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-24
# @copyright by hoojo @2020
# @changelog use pyppeteer query `douban` book setter ebook-meta


# ===============================================================================
# 标题：query `douban` book setter ebook-meta
# ===============================================================================
# 使用：利用 pyppeteer 框架进行豆瓣图书查询，并设置电子书元数据
# terminal command:
#       python ebook_meta.py file
#       python ebook_meta.py dir
#       python ebook_meta.py -v dir
# -------------------------------------------------------------------------------
# 描述：利用 pyppeteer 框架进行豆瓣图书查询，并设置电子书元数据
# -------------------------------------------------------------------------------
import asyncio
import re
import os
import sys
import shutil
from pyppeteer import launch


# -------------------------------------------------------------------------------
# 构建单任务查询图书操作
# -------------------------------------------------------------------------------
def debug(message, *args):
    print("[DEBUG]" + message, *args)


def info(message, *args):
    print("[INFO]" + message, *args)


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
    info("[request] request url: %s" % response.url)
    # 获取网页内容
    content = await page.content()
    info("[request] search: %s, content: %s" % (await page.title(), len(content)))
    await asyncio.sleep(0.5)

    subject = await page.J("#wrapper div.item-root a[href^='https://book.douban.com/subject/']")
    if subject:

        # 等待新页面加载完成
        await asyncio.gather(
            page.waitForNavigation(),
            subject.click(),
        )

        title = await page.title()
        content = await page.content()
        info("[request] title: %s, content: %s" % (title, len(content)))
        await asyncio.sleep(0.5)

        interest_sectl = await page.J("div#interest_sectl")
        if not interest_sectl:
            info("[request] 非图书，无法提取到相关记录：%s\n" % text)
            return None

        name = await page.Jeval("div#wrapper h1", "node => node.innerText")
        author = await page.JJeval("div#wrapper div#info > span:nth-child(1) a[href]", """nodes => {
            var authors = [];
            nodes.forEach(function (item) {
                authors.push(item.innerText);
            });
            return authors.join(" ");
        }""")

        if not author:
            author = await page.Jeval("div#wrapper div#info a[href]", "node => node.innerText")

        score = await page.Jeval("div#interest_sectl strong.rating_num", "node => node.innerText")
        star = await page.Jeval("div#interest_sectl div.rating_right div.ll", "node => node.className.replace('ll bigstar', '')")
        num = await page.Jeval("div#interest_sectl div.rating_right", "node => node.innerText")

        comment = await page.Jeval("div.related_info div.intro", "node => node.innerText")

        tags = ""
        tags_el = await page.J("div#wrapper div#db-tags-section")
        if tags_el:
            tags = await tags_el.Jeval("div.indent", "node => node.innerText")

        book_info_text = await page.Jeval("div#wrapper div#info", "node => node.textContent")
        book_info = extract(book_info_text)
        # debug("[request] book info: %s" % book_info)

        book = {
            "name": name.replace('"', '”'), "author": author,
            "score": score, "star": star, "num": num, "comment": comment,
            "tags": tags.replace(" ", "").replace("\xa0", ", ")
        }

        # debug("[request] book: %s\n" % book)

        book.update(book_info)
        return book
    else:
        info("[request] 没有搜索到相关记录：%s\n" % text)
        return None


def rename_book(book_metadata):

    for book_file_name, book in book_metadata.items():
        if not book:
            continue

        src = book_file_name
        suffix = src.split(".")[-1]
        if book["nick_name"]:
            dst_file = "{author}-{name}：{nick_name}.{0}".format(suffix, **book)
        else:
            dst_file = "{author}-{name}.{0}".format(suffix, **book)

        dst = os.path.join(os.path.dirname(src), "rename", dst_file)
        debug("[rename] %s ===>>> %s" % (src, dst))

        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))

        try:
            os.rename(src, dst)
            # shutil.copy(src, dst)
        except FileNotFoundError as e:
            info("[rename] ", src, "文件不存在", e)


async def exec_command(*args):
    debug("[command] start run cmd")

    buffer = bytearray()
    cmd_process = asyncio.create_subprocess_exec("ebook-meta", *args, stdout=asyncio.subprocess.PIPE)
    proc = await cmd_process

    while True:
        line = await proc.stdout.readline()
        # debug("[command] r: ", line[0:-1].decode("gbk"))
        if not line:
            break

        buffer.extend(line)

    await proc.wait()

    return_code = proc.returncode
    debug("[command] return code: ", return_code)

    if not return_code:
        cmd_output = bytes(buffer).decode("gbk")
        print(cmd_output)

    return return_code


async def modify_meta(file, page):

    exception_files = []

    async def book_metadata(book_file, book_file_path):
        book_name = book_file.split(".")[0]

        book = await request_book(book_name, page)
        if not book:
            exception_files.append(book_file_path)
            return None
        debug("[modify meta] book: %s\n" % book)

        metadata = [
            "-t", book["name"], "-a", book["author"], "-c", book["comment"],
            "--identifier", "isbn:" + book["isbn"], "--isbn", book["isbn"], "--tags", book["tags"],
            "-p", book["publish_org"], "-d", book["publish_date"], "-r", str(int(book["star"]) * 0.1),
                            ]
        return_code = await exec_command(book_file_path, *metadata)
        debug("[modify meta] 返回码: ", return_code)

        if return_code != 0:
            exception_files.append(book_file_path)
        else:
            info("[modify meta] 编辑图书元数据成功: ", book_file_path)
            rename_book({book_file_path: book})

    if not os.path.exists(file):
        info("[modify meta] 文件或目录不存在：", file)
    else:
        if os.path.isfile(file):
            await book_metadata(os.path.basename(file), file)
        else:
            for root, dirs, files in os.walk(file):
                for item in files:
                    debug("[modify meta] 发现新文件: ", item)
                    file_path = os.path.join(root, item)
                    await book_metadata(item, file_path)
                    print("\n======================================================================================\n")

    info("[modify meta] 元数据修改异常书籍: ", exception_files)


async def run_browser(file):

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

    # 编辑元数据
    await modify_meta(file, page)

    # 关闭浏览器
    await browser.close()


# 获取事件循环
if os.name == 'nt':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
else:
    loop = asyncio.get_event_loop()

loop.run_until_complete(run_browser("book-files/"))
# loop.run_until_complete(run_browser("book-files/杨国荣-成己与成物.mobi"))
# loop.run_until_complete(exec_command("book-files/杨国荣-成己与成物.mobi", *["-c", " "]))