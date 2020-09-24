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

```shell
# 利用pip安装pyppeteer
pip3 install pyppeteer
```

如果没有错误安装成功后，即可开始下面的工作。

## 使用

利用一个简单的小网页数据 `http://quotes.toscrape.com/js/`，这个网页中的数据是通过`JavaScript`渲染出来，如果利用普通的爬虫方式无法获取到我们见到的完整的网页数据。下面进行上手演示示例：

```python
import asyncio
from pyppeteer import launch
from pyquery import PyQuery


async def main():

    # 启动浏览器
    browser = await launch()
    # 打开一个新页面
    page = await browser.newPage()
    # 地址栏跳转到当前网址
    await page.goto("http://quotes.toscrape.com/js/")

    # 获取网页内容，关键一步
    content = await page.content()

    # 转换数据，利用PyQeruy进行数据查找
    query = PyQuery(content)
    print("quote：", query(".quote").length)

    # 关闭浏览器
    await browser.close()

# 利用异步方式执行函数
asyncio.get_event_loop().run_until_complete(main())
```

上面是一个简单的示例代码，首先，` launch` 方法会新建一个 `Browser` 对象，赋值给 `browser`。接着调用 `newPage`  方法，相当于浏览器中新建了一个选项卡，同时新建了一个 `Page` 对象。然后 `Page` 对象调用了 `goto` 方法就相当于在浏览器中输入了这个 `URL`，浏览器跳转到了对应的页面进行加载，加载完成之后再调用 `content` 方法，返回当前浏览器页面的源代码。最后进一步利用 `pyquery` 进行同样地解析，就可以得到 `JavaScript` 渲染的结果了。

首次利用 `main` 函数运行示例后，会看到如下内容：

```shell
# 首次运行，程序会自动下载Chromium 
[W:pyppeteer.chromium_downloader] start chromium download.
Download may take a few minutes.
 81%|████████  | 110622720/136913619 [03:09<00:40, 649705.84it/s]
```

`Pyppeteer` 就是依赖于 `Chromium` 这个浏览器来运行的。那么有了 `Pyppeteer` 之后，我们就可以免去那些繁琐的环境配置等问题。如果第一次运行的时候，`Chromium` 浏览器没有安装。那么程序会帮我们自动安装和配置，就免去了繁琐的环境配置等工作。

`Chromium` 是谷歌为了研发 `Chrome` 而启动的项目，是完全开源的。二者基于相同的源代码构建，`Chrome` 所有的新功能都会先在 `Chromium` 上实现，待验证稳定后才会移植，因此 `Chromium` 的版本更新频率更高，也会包含很多新的功能，但作为一款独立的浏览器，`Chromium` 的用户群体要小众得多。两款浏览器“同根同源”，它们有着同样的 `Logo`，但配色不同，`Chrome` 由蓝红绿黄四种颜色组成，而 `Chromium` 由不同深度的蓝色构成。


## 问题

### 首次运行出现 `Python` 库不兼容错误

在执行爬虫时出现错误代码，如下：

```shell
C:\Users\Administrator\AppData\Local\Programs\Python\Python36\lib\site-packages\requests\__init__.py:80: RequestsDependencyWarning: urllib3 (1.25.10) or chardet (3.0.4) doesn't match a supported version!
  RequestsDependencyWarning)
```

原因：`python`库中`urllib3`  or `chardet`   的版本不兼容，解决办法如下：

```shell
pip uninstall urllib3
pip uninstall chardet
pip install --upgrade requests
```

### 首次运行下载`Chromium`错误

在首次运行程序会下载`Chromium` 浏览器，若出现以下错误可以手动下载

```shell
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1056)
```

在`pyppeteer.chromium_downloader`模块代码中可以看到下载指向的`downloadURLs`、`chromiumExecutable`等变量，很明显指的就是下载链接和`chromium`的可执行文件路径。我们重点关注一下可执行文件路径

```shell
chromiumExecutable：
chromiumExecutable = {
'linux': DOWNLOADS_FOLDER / REVISION / 'chrome-linux' / 'chrome',
'mac': (DOWNLOADS_FOLDER / REVISION / 'chrome-mac' / 'Chromium.app' /
'Contents' / 'MacOS' / 'Chromium'),
'win32': DOWNLOADS_FOLDER / REVISION / 'chrome-win32' / 'chrome.exe',
'win64': DOWNLOADS_FOLDER / REVISION / 'chrome-win32' / 'chrome.exe',
}
```

可以看到 `win`平台的地址 `'win64': DOWNLOADS_FOLDER / REVISION / 'chrome-win32' / 'chrome.exe'`，通过代码可以看到完整的下载地址和安装地址：

```python
import pyppeteer.chromium_downloader

print('默认版本是：{}'.format(pyppeteer.__chromium_revision__))
print('可执行文件默认路径：{}'.format(pyppeteer.chromium_downloader.chromiumExecutable.get('win64')))
print('win64平台下载链接为：{}'.format(pyppeteer.chromium_downloader.downloadURLs.get('win64')))
```

输出下载地址如下：

```shell
默认版本是：588429
可执行文件默认路径：C:\Users\Administrator\AppData\Local\pyppeteer\pyppeteer\local-chromium\588429\chrome-win32\chrome.exe
win64平台下载链接为：https://storage.googleapis.com/chromium-browser-snapshots/Win_x64/588429/chrome-win32.zip
```

如果想要改变默认的安装可执行文件路径，可以配置下`PYPPETEER_HOME`环境变量：

```python
import os
# 也可以在系统中配置环境变量，这样后续安装就直接指向环境变量的位置
os.environ['PYPPETEER_HOME'] = 'D:\Program Files'

# 一定要在导入模块之前配置环境变量
import pyppeteer.chromium_downloader
print('默认版本是：{}'.format(pyppeteer.__chromium_revision__))
print('可执行文件默认路径：{}'.format(pyppeteer.chromium_downloader.chromiumExecutable.get('win64')))
print('win64平台下载链接为：{}'.format(pyppeteer.chromium_downloader.downloadURLs.get('win64')))
```

结果看到环境变量生效：

```shell
默认版本是：588429
可执行文件默认路径：D:\Program Files\local-chromium\588429\chrome-win32\chrome.exe
win64平台下载链接为：https://storage.googleapis.com/chromium-browser-snapshots/Win_x64/588429/chrome-win32.zip
```

在系统中配置好`PYPPETEER_HOME`环境变量，通过下载链接进行下载，下载完成后解压压缩包到指定目录`D:\Program Files`下即可。

### 出现 `OSError: Unable to remove Temporary User Data` 错误

设置必要的缓存目录即可

```shell
browser = await launch(headless=False, userDataDir="user-data")
```

### 出现 `Target.sendMessageToTarget: Target closed.`错误

先关闭浏览器中的页面，再关闭浏览器

```shell
pyppeteer.errors.NetworkError: Protocol error Target.sendMessageToTarget: Target closed.

# 关闭网页
await page.close()
# 关闭浏览器
await browser.close()
```

### 出现`Navigation Timeout Exceeded: 30000 ms exceeded`超时问题

```shell
pyppeteer.errors.TimeoutError: Navigation Timeout Exceeded: 30000 ms exceeded.
```

解决办法可以使用浏览器 `dumpio=True` 参数，缓解卡顿问题，同时让程序在可视化窗口下运行：

```shell
browser = await launch(headless=False, dumpio=True)

# 或者试试设置超时限制，但有时候还是会超时
browser = await launch(headless=True, dumpio=True, timeout=(1000 * timeout))
```

### 出现`argument 'ping_interval'`错误

当运行代码出现`TypeError: create_connection() got an unexpected keyword argument 'ping_interval'`错误时，解决办法可以升级到最新的`websockets`库：

```shell
pip install -U websockets

#指定安装6.0版本
pip install websockets==8.0 
```



## 参考
`Pyppeteer` 参考文档： https://ld246.com/article/1566221786951
`Pyppeteer API` 参考文档：https://github.com/puppeteer/puppeteer/blob/v2.1.1/docs/api.md
`PyQuery API` 参考文档：https://pythonhosted.org/pyquery/api.html
`xpath`选择器参考：https://www.cnblogs.com/huchong/p/10287427.html