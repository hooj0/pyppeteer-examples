#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog disable web browser webdriver detect


# ===============================================================================
# 标题：disable web browser webdriver detect
# ===============================================================================
# 使用：利用 pyppeteer 框架参数禁止被爬网站进行 webdriver 的检测
# -------------------------------------------------------------------------------
# 描述：设置参数，绕过服务器的 webdriver 检测操作
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例，设置参数，绕过服务器的 webdriver 检测操作
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
    # --no-sandbox 关闭沙盒模式
    # --start-maximized  窗口最大化模式
    browser = await launch(headless=False, args=["--disable-infobars", "--no-sandbox", "--start-maximized"])
    page = await browser.newPage()

    w, h = screen_size()
    print(f'设置窗口为：width：{w} height：{h}')

    # 设置内容页面大小
    await page.setViewport(viewport={"width": w, "height": h})
    await page.goto("https://login.taobao.com/member/login.jhtml?redirectURL=https://www.taobao.com")

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

    # 模拟键盘输入用户名、密码
    await page.type("input#fm-login-id", "test_user")
    await page.type("input#fm-login-password", "test234")
    # 模拟鼠标点击登录
    await page.click("button.fm-submit")

    await asyncio.sleep(100)
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())