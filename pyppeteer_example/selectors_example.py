#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog pyppeteer selectors and eval example


# ===============================================================================
# 标题：pyppeteer selectors example
# ===============================================================================
# 使用：pyppeteer 框架选择器使用示例
# -------------------------------------------------------------------------------
# 描述：演示用selector选择器查找元素
#
#       J()：别名 querySelector() 通过 CSS 选择器来选出元素，返回单个元素
#       JJ(): 别名 querySelectorAll() 查找所有，返回一个元素数组
#       Jeval(): 利用 querySelector 选择器找到元素，并使用eval方法执行回调函数
#       JJeval(): 利用 querySelectorAllEval() 选择器找到元素，并使用eval方法执行回调函数
#       Jx(): 别名 xpath()，xpath 选择器查找元素
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手，构建选择器示例
# -------------------------------------------------------------------------------
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
    # 获取网页内容
    content = await page.content()
    print("content: ", len(content))

    # =================================================================================================================
    # ================================================ page selector ==================================================
    # =================================================================================================================

    # ------------------------------selector---------------------------------------
    # 查找 span class=text 的元素，只返回第一个
    text = await page.querySelector("span.text")
    print("text: ", text)

    # 使用别名
    text = await page.J("span.text")
    print("text: ", text)
    print("\n\n")

    # ------------------------------selectorAll-------------------------------------
    # 查找一组 span class=text 的元素，返回数组
    text_list = await page.querySelectorAll("span.text")
    print("text list[%s]: %s" % (len(text_list), text_list))

    # 使用别名
    text_list = await page.JJ("span.text")
    print("text list[%s]: %s" % (len(text_list), text_list))
    print("\n\n")

    # ------------------------------selector eval-----------------------------------
    # 查找 span class=text 的元素，并执行回调函数
    html = await page.querySelectorEval("span.text", "node => node.outerHTML")
    print("html: ", html)

    html_text = await page.Jeval("span.text", "node => { return {'html': node.outerHTML, 'text': node.textContent}; }")
    print("html&text: ", html_text)
    print("\n\n")

    # ------------------------------selectorAll eval----------------------------------
    # 查找 span class=text 的元素，并执行回调函数，返回数组
    text_list = await page.querySelectorAllEval("span.text", """nodes => {
        var arrays = [];
        for (i in nodes) {
            arrays.push(nodes[i].textContent.split(" ")[2])
        }
        return arrays;
    }""")
    print("text list: %s" % (text_list, ))

    size_list = await page.JJeval("span.text", """nodes => {
        var arrays = [];
        nodes.forEach(function (item) {
            arrays.push(item.innerText.length);
        });
        return arrays;
    }""")
    print("size list: %s" % (size_list, ))
    print("\n\n")

    # =================================================================================================================
    # ================================================ element selector ===============================================
    # =================================================================================================================

    # ------------------------------selector---------------------------------------
    # 找到一个元素
    element = await page.querySelector("div.quote")
    print("element: ", element)
    print("")

    # 在元素中继续查找
    text_element = await element.querySelector("span.text")
    print("text_element: ", text_element)
    print("text_element toString: ", text_element.toString())   # JSHandle@node
    print("text_element asElement: ", text_element.asElement()) # ElementHandle
    print("text_element getProperty: ", await text_element.getProperty("textContent")) # JSHandle
    print("text_element getProperty jsonValue: ", await (await text_element.getProperty("textContent")).jsonValue())
    print("text_element getProperty jsonValue: ", await (await text_element.getProperty("outerHTML")).jsonValue())
    print("text_element getProperty jsonValue: ", await (await text_element.getProperty("className")).jsonValue())
    print("")

    # 使用别名
    tags_elements = await element.J("div.tags")
    print("tags_elements: ", tags_elements)
    print("tags_elements getProperty jsonValue: ", await (await tags_elements.getProperty("textContent")).jsonValue())
    print("tags_elements getProperty jsonValue: ", await (await tags_elements.getProperty("outerHTML")).jsonValue())
    print("tags_elements getProperty jsonValue: ", await (await tags_elements.getProperty("className")).jsonValue())
    print("\n\n")

    # ------------------------------selectorAll---------------------------------------
    # 在元素中继续查找
    text_elements = await element.querySelectorAll("span")
    for text_el in text_elements:
        print("text_el: ", text_el)
        print("text_el getProperty: ", await text_el.getProperty("textContent")) # JSHandle
        print("text_el getProperty jsonValue: ", await (await text_el.getProperty("textContent")).jsonValue())
        print("text_el getProperty jsonValue: ", await (await text_el.getProperty("outerHTML")).jsonValue())
        print("text_el getProperty jsonValue: ", await (await text_el.getProperty("className")).jsonValue())
        print("")

    # 使用别名
    tag_elements = await element.JJ("a.tag")
    for tag_el in tag_elements:
        print("tag_el: ", tag_el)
        print("tag_el getProperty jsonValue: ", await (await tag_el.getProperty("textContent")).jsonValue())
        print("tag_el getProperty jsonValue: ", await (await tag_el.getProperty("outerHTML")).jsonValue())
        print("tag_el getProperty jsonValue: ", await (await tag_el.getProperty("className")).jsonValue())
        print("")

    print("\n\n")

    # =================================================================================================================
    # ==================================================== evaluate ===================================================
    # =================================================================================================================
    # 执行特定的JavaScript代码
    result = await page.evaluate("""() => {
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight,
            deviceScaleFactor: window.devicePixelRatio
        }
    }""")

    print("result: ", result)
    # result:  {"width': 800, 'height': 600, 'deviceScaleFactor': 1}

    # 获取网页body文本内容，force_expr=True，强制Pyppeteer作为表达式处理
    text_content = await page.evaluate("document.getElementsByClassName('footer')[0].innerText", force_expr=True)
    print("text content: ", text_content)

    element = await page.J("h1")
    # 获取 h1 标签的文本内容
    title = await page.evaluate("(element) => element.textContent", element)
    print("title: ", title)

    # 滚动到页面底部
    await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")

    object = await page.evaluate("() => ({'a': document.title, 'b': 2})")
    print(object)

    # 通过 eval 返回 Properties 对象
    handle = await page.evaluateHandle("() => ({window, document})")
    print("handle: ", handle)
    properties = await handle.getProperties()
    window_handle = properties.get("window")
    document_handle = properties.get("document")
    await handle.dispose()

    print("window.tags: ", await (await window_handle.getProperty("tags")).jsonValue())
    print("document.location: ", await (await document_handle.getProperty("location")).jsonValue())

    # 关闭浏览器
    await browser.close()

# 利用异步方式执行函数
asyncio.get_event_loop().run_until_complete(main())

