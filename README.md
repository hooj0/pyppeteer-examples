# pyppeteer book
Use python `ppeteer` lib spider book `douban.com` data.

## 介绍

利用 `Pyppeteer`库爬取豆瓣书籍信息，`Pyppeteer`和`Selenium`差不多都是一个自动化测试的工具，它们都可以用于网络爬虫中来应对 `JavaScript` 渲染的页面的抓取。也就是说正常爬虫爬取的页面是请求地址返回后的结果，但有些页面的数据通过JavaScript进行异步请求，导致不能正常爬取到数据。这个时候如果使用`Pyppeteer`自动化这类工具，就能很轻松的获取`JavaScript`二次请求的结果数据。

> 这里不介绍 `Selenium` 的具体使用，只对 `Pyppeteer` 的用法做实际的操作演示。

## 准备

- `python3.5.2+`
- `pyppeteer`

## 开始

如果没有安装`Pyppeteer`，需要先安装框架

### 安装环境

```shell
# 利用pip安装pyppeteer
pip install pyppeteer
```

如果没有错误安装成功后，即可开始下面的工作。

### 快速上手

```shell
cd worksapce
D:\worksapce>scrapy startproject scrapy_book

# 首次运行，程序会自动下载Chromium 
[W:pyppeteer.chromium_downloader] start chromium download.
Download may take a few minutes.
 81%|████████  | 110622720/136913619 [03:09<00:40, 649705.84it/s]
```

### 生成代码

`scrapy` 可以自动生成 `spider` 的代码，使用如下命令会在 `spider` 目录生成代码模板。

```shell
D:\work_private>cd scrapy_book
D:\work_private\scrapy_book>scrapy genspider book bloogle.top
```

## 使用

使用命令启动运行项目

```shell
# 使用命令行的方式分析网页，可以进行表达式测试
scrapy shell https://bloogle.top/

# 运行爬虫
scrapy crawl book

# 运行爬虫，存储抓取的数据
scrapy crawl book -o book.json

# 运行爬虫，存储抓取的数据，不分行存储
scrapy crawl book -o book.jl

# 处理存储中文编码
scrapy crawl book -o book.jl -s FEED_EXPORT_ENCODING=utf-8
```

## 清单

在执行爬虫下载图片文件时出现错误代码，如下：

```shell
    from PIL import Image
ModuleNotFoundError: No module named 'PIL'
```

解决办法安装 `pillow`

```shell
pip install pillow

# 已经安装过了，这时可以先卸载，获取最新的pillow
# 运行卸载命令:
pip uninstall pillow
```



## 参考

`scrapy` 官方文档 https://docs.scrapy.org/en/latest/intro/tutorial.html

