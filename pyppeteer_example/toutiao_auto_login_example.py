#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog use pyppeteer auto login toutiao site


# ===============================================================================
# 标题：use pyppeteer auto login toutiao site
# ===============================================================================
# 使用：利用 pyppeteer 框架自动登录头条网站
# -------------------------------------------------------------------------------
# 描述：用框架查找到手机输入、验证码输入，自动提交登录头条号
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例，自动登录操作
# -------------------------------------------------------------------------------
import asyncio
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


async def main():

    # disable-infobars 关掉提示："Chrome 正受到自动测试软件的控制"
    # dumpio=True 防止 chromium浏览器多开页面卡死问题
    # '--window-size=1366,850' 设置窗口大小
    browser = await launch(headless=False, dumpio=True, args=["--disable-infobars", "--no-sandbox", '--window-size=1366,850'])
    page = await browser.newPage()

    w, h = screen_size()
    print("w: %s, h: %s" % (w, h))

    # 设置内容页面大小
    await page.setViewport(viewport={"width": w, "height": h})
    await page.goto("https://sso.toutiao.com/login")

    # 利用浏览器执行特定脚本，绕过 webdriver 检测
    await page.evaluate("""() => {
        Object.defineProperties(navigator, {
            webdriver: {
                    get: () => false
                }
            })
    }""")

    # JS脚本获取 webdriver 状态
    await page.evaluate("""() => { alert(window.navigator.webdriver); }""")

    phone_no = await page.xpath("//form//input[@id='user-mobile']")
    phone_code = await page.xpath("//form//input[@id='mobile-code']")
    send_code = await page.xpath("//form//span[@class='get-code']")
    submit = await page.xpath("//form//button[1]")

    print(phone_no[0])
    await phone_no[0].type("151XXXX2131")
    await send_code[0].click()

    code = input("请输入验证码：")
    await phone_code[0].type(str(code))

    # await page.waitFor(1000)
    await submit[0].click()

    await asyncio.sleep(3)
    await page.goto("https://sso.toutiao.com")

    await asyncio.sleep(100)
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())