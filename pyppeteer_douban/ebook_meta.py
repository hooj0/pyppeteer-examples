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
#       python ebook_meta.py -l info dir
# -------------------------------------------------------------------------------
# 描述：利用 pyppeteer 框架进行豆瓣图书查询，并设置电子书元数据
# -------------------------------------------------------------------------------
from pyppeteer import launch
import asyncio
import re
import os
import getopt
import sys
import term


# -------------------------------------------------------------------------------
# 构建单任务查询图书操作
# -------------------------------------------------------------------------------
log_mode = "info"


def debug(message, *args):
    if log_mode.lower() == "debug":
        print("[DEBUG]" + message, *args)


def info(message, *args):
    if log_mode.lower() == "info" or log_mode.lower() == "debug":
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
    subtitle = re.findall(r"副标题:(.*?)\n", book_info)
    publish_org = re.findall(r"出版社:(.*?)\n", book_info)
    publish_date = re.findall(r"出版年:(.*?)\n", book_info)
    price = re.findall(r"定价:(.*?)\n", book_info)
    isbn = re.findall(r"ISBN:(.*?)\n", book_info)
    series = re.findall(r"丛书:(.*?)\n", book_info)

    return {
        "subtitle": "".join(subtitle).strip(),
        "publisher": "".join(publish_org).strip(),
        "date": "".join(publish_date).strip(),
        "price": "".join(price).strip(),
        "isbn": "".join(isbn).strip(),
        "series": "".join(series).strip(),
    }


async def request_book_detail(text, link, page):
    response = await page.goto(link, {"timeout": 0})
    info("[detail] request url: %s" % response.url)

    title = await page.title()
    info("[detail] title: %s, ok: %s" % (title, response.ok))

    await page.waitFor("div#content", timeout=0)
    # response = await page.waitForResponse(response.url)
    # response.ok

    interest_sectl = await page.J("div#interest_sectl")
    if not interest_sectl:
        info("[detail] 非图书，无法提取到相关记录：%s\n" % text)
        return None

    name = await page.Jeval("div#wrapper h1", "node => node.innerText")
    authors = await page.JJeval("div#wrapper div#info > span:nth-child(1) a[href]", """nodes => {
            var authors = [];
            nodes.forEach(function (item) {
                authors.push(item.innerText);
            });
            return authors.join(" ");
        }""")

    if not authors:
        authors = await page.Jeval("div#wrapper div#info a[href]", "node => node.innerText")

    rating = await page.Jeval("div#interest_sectl strong.rating_num", "node => node.innerText")
    star = await page.Jeval("div#interest_sectl div.rating_right div.ll", "node => node.className.replace('ll bigstar', '')")
    num = await page.Jeval("div#interest_sectl div.rating_right", "node => node.innerText")

    comments, content_el = "", await page.J("div.related_info div.intro")
    if content_el:
        comments = await page.Jeval("div.related_info div.intro", "node => node.innerText")

    tags, tags_el = "", await page.J("div#wrapper div#db-tags-section")
    if tags_el:
        tags = await tags_el.Jeval("div.indent", "node => node.innerText")

    book_info_text = await page.Jeval("div#wrapper div#info", "node => node.textContent")
    book_info = extract(book_info_text)

    book = {
        "title": name.replace('"', '”'), "authors": authors,
        "rating": rating, "star": star, "num": num, "comments": comments,
        "tags": tags.replace(" ", "").replace("\xa0", ", ")
    }

    book.update(book_info)

    debug("[detail] book: %s\n" % book)
    return book


async def request_book(text, page):
    # 设置请求URL
    url = f"https://search.douban.com/book/subject_search?search_text={text}&cat=1001"
    # 地址栏跳转到当前网址
    response = await page.goto(url, {"timeout": 0})
    info("[request] request url: %s" % response.url)
    info("[request] search: %s, ok: %s\n" % (await page.title(), response.ok))

    subjects = await page.JJ("#wrapper div.item-root div.detail a[href^='https://book.douban.com/subject/']")
    if subjects:
        links = []
        for subject in subjects:
            links.append(await (await subject.getProperty("href")).jsonValue())

        books = []
        for link in links[0:5]:
            book = await request_book_detail(text, link, page)
            if book:
                books.append(book)
            await asyncio.sleep(1.5)

        return books
    else:
        info("[request] 没有搜索到相关记录：%s\n" % text)
        return None


def rename_book(book_metadata):

    for book_file_name, book in book_metadata.items():
        if not book:
            continue

        src, suffix = book_file_name, book_file_name.split(".")[-1]
        if book["subtitle"]:
            dst_file = "{authors}-{title}：{subtitle}.{0}".format(suffix, **book)
        else:
            dst_file = "{authors}-{title}.{0}".format(suffix, **book)

        # dst = os.path.join(os.path.dirname(src), "rename", dst_file)
        dst = os.path.join(os.path.dirname(src), dst_file)
        debug("[rename] %s ===>>> %s" % (src, dst))

        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))

        try:
            os.rename(src, dst)
        except FileNotFoundError as e:
            info("[rename] ", src, "文件不存在", e)


async def exec_command(*args):
    debug("[command] start run cmd")

    buffer = bytearray()
    debug("[command] ebook-meta ", *args)

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
        term.writeLine("\n书籍元数据信息如下：", term.green, term.bold)
        print("====" * 30)
        term.write(cmd_output, term.bgwhite, term.bold, term.black)
        print("====" * 30)

    return return_code


async def choose_book(books, book_file_path):

    def print_book(i, book):
        text = term.format("图书序号：", term.cyan, term.bold) \
               + term.format(i, term.red, term.bold) \
               + term.format(", 书名：%s" % book["title"], term.yellow, term.bold)
        print("====" * 10 + "<<<" * 3, text, ">>>" * 3 + "====" * 10)
        term.writeLine("||  title: %s" % book["title"], term.red)
        term.writeLine("||  subtitle: %s" % book["subtitle"], term.red)
        term.writeLine("||  authors: %s" % book["authors"], term.red)
        term.writeLine("||  tags: %s" % book["tags"], term.red)
        term.writeLine("||  rating: %s" % book["rating"], term.magenta)
        term.writeLine("||  star: %s" % book["star"], term.magenta)
        term.writeLine("||  num: %s" % book["num"], term.magenta)
        term.writeLine("||  price: %s" % book["price"], term.blue)
        term.writeLine("||  isbn: %s" % book["isbn"], term.blue)
        term.writeLine("||  publisher: %s" % book["publisher"], term.yellow)
        term.writeLine("||  date: %s" % book["date"], term.yellow)
        term.writeLine("||  series: %s" % book["series"], term.yellow)
        term.writeLine("||  comments: %s" % book["comments"], term.white)
        print("\n")

    # 打印书籍信息
    for i in range(len(books)):
        print_book(i, books[i])

    # 显示元数据信息
    return_code = await exec_command(book_file_path)
    debug("[choose book] 返回码: ", return_code)

    if return_code != 0:
        return None

    # 选择图书信息
    index = 0
    if len(books) > 0:
        text = term.format("\n\n请选择书籍元数据", term.red, term.bold) \
               + term.format("[0-%s]" % len(books), term.yellow, term.bold) \
               + term.format("之间的数字: ", term.red, term.bold)
        term.writeLine(text)
        index = int(input())
    book = books[index]

    term.writeLine("你选择了书籍：%s" % book["title"], term.blue, term.bold)
    print_book(index, book)

    return book


async def modify_meta(file, page):

    exception_files = []

    async def book_metadata(book_file, book_file_path):
        book_name = book_file.split(".")[0]

        books = await request_book(book_name, page)
        if not books:
            exception_files.append(book_file_path)
            return None

        book = await choose_book(books, book_file_path)
        debug("[modify meta] book: %s\n" % book)

        metadata = [
            "-t", book["title"], "-a", book["authors"], "-c", book["comments"], "-s", book["series"],
            "--identifier", "isbn:" + book["isbn"], "--isbn", book["isbn"], "--tags", book["tags"],
            "-p", book["publisher"], "-d", book["date"], "-r", str(int(book["star"]) * 0.1),
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
                    term.writeLine("发现新文件: %s" % item, term.yellow, term.underscore)
                    file_path = os.path.join(root, item)
                    await book_metadata(item, file_path)
                    term.writeLine("\n\n\n" + "####" * 30, term.cyan)

    if exception_files:
        info("[modify meta] 元数据修改无效的图书: ", exception_files)


async def run_browser(file):

    # 获取屏幕尺寸
    width, height = screen_size()
    # 启动浏览器
    browser = await launch()
    # browser = await launch(headless=False, dumpio=True, args=["--disable-infobars", "--start-maximized"])
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


def run(file):
    # 获取事件循环
    if os.name == 'nt':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    loop.run_until_complete(run_browser(file))


def main(argv):
    # print('argv: %s' % argv)

    help_usage = '''
    USAGE: python ebook_meta.py [OPTIONS] -h --log debug [COMMAND] command [FILE] file
    
    OPTIONS: 
      -h,--help                  use the help manual.
      -l,--log debug,info,none   print ebook metadata debug log, print ebook metadata info log. default: info
      
    COMMANDS:
      help        use the help manual
        
    EXAMPLES: 
      python ebook_meta.py -h
      python ebook_meta.py help
    
      python ebook_meta.py /home/ebook/hello.epub
      python ebook_meta.py /home/ebook/
      
      python ebook_meta.py -l debug /home/ebook/hello.epub
      python ebook_meta.py -l info /home/ebook/hello.epub
      
      python ebook_meta.py --log debug /home/ebook/
    '''

    # default run current path
    if len(argv) < 1:
        run(".")
        sys.exit()

    try:
        long_opts = ["help", "log="]
        opts, args = getopt.getopt(argv, "hl:", long_opts)
        # print('opts: %s, args: %s' % (opts, args))
    except getopt.GetoptError:
        print(help_usage)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help_usage)
            sys.exit()
        elif opt in ("-l", "--log"):
            global log_mode
            log_mode = arg

    for arg in args:
        if arg == 'help':
            print(help_usage)
            sys.exit()
        else:
            run(arg)

    if len(args) < 0:
        print(help_usage)
        sys.exit()


if __name__ == "__main__":
    main(sys.argv[1:])