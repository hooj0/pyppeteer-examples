# pyppeteer book
Use python `ppeteer` lib spider book `douban.com` data.

## 介绍

利用 `Pyppeteer`库爬取豆瓣书籍信息，`Pyppeteer`和`Selenium`差不多都是一个自动化测试的工具，它们都可以用于网络爬虫中来应对 `JavaScript` 渲染的页面的抓取。也就是说正常爬虫爬取的页面是请求地址返回后的结果，但有些页面的数据通过JavaScript进行异步请求，导致不能正常爬取到数据。这个时候如果使用`Pyppeteer`自动化这类工具，就能很轻松的获取`JavaScript`二次请求的结果数据。

由于`Selenium` 相对复杂，在环境配置繁琐，对驱动和第三方浏览器依赖较强，且容易被反爬虫侦测或禁用。这里不介绍 `Selenium` 的具体使用，只对 `Pyppeteer` 的用法做实际的操作演示。

## 准备

- `python3.5.2+`
- `pyppeteer`

> 由于 `Pyppeteer` 采用了 `Python` 的 `async` 机制，所以其运行要求的 `Python` 版本为 `3.5` 及以上。

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

`Pyppeteer` 就是依赖于 `Chromium` 这个浏览器来运行的。那么有了 `Pyppeteer` 之后，我们就可以免去那些繁琐的环境配置等问题。如果第一次运行的时候，`Chromium` 浏览器没有安装。那么程序会帮我们自动安装和配置，就免去了繁琐的环境配置等工作。

`Chromium` 是谷歌为了研发 `Chrome` 而启动的项目，是完全开源的。二者基于相同的源代码构建，`Chrome` 所有的新功能都会先在 `Chromium` 上实现，待验证稳定后才会移植，因此 `Chromium` 的版本更新频率更高，也会包含很多新的功能，但作为一款独立的浏览器，`Chromium` 的用户群体要小众得多。两款浏览器“同根同源”，它们有着同样的 `Logo`，但配色不同，`Chrome` 由蓝红绿黄四种颜色组成，而 `Chromium` 由不同深度的蓝色构成。

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

