#!/usr/bin/env python3
# encoding: utf-8
# @author: hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create date: 2020-09-22
# @copyright by hoojo @2020
# @changelog pyppeteer spider taobao site


# ===============================================================================
# 标题：pyppeteer spider taobao site
# ===============================================================================
# 使用：利用 pyppeteer 框架抓取淘宝网数据
# -------------------------------------------------------------------------------
# 描述：尝试利用异步方式执行爬虫，若中途错误自动重试并返回正常的结果
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# 快速上手示例，淘宝网自动登录
# -------------------------------------------------------------------------------
import asyncio
import random
# 错误自动重试
from retrying import retry
from pyppeteer import page
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


def random_delay_time():
    return random.randint(100, 200)


def retry_if_result_none(result):
    print(result)
    return result is False


# @retry(retry_on_result=retry_if_result_none)
async def simulate_slide(page: page.Page):
    await asyncio.sleep(2)
    print("自动滑块验证……")

    try:
        slider = await page.querySelector("#nc_1_n1z")
        if slider is None:
            await page.focus("input#fm-login-password")
            await page.keyboard.press("Enter")
            await asyncio.sleep(3)

        await page.hover("#nc_1_n1z")

        await page.mouse.down()
        await page.mouse.move(3000, 0, {"steps": random.randint(50, 500)})
        await page.mouse.up()
    except Exception as e:
        print(e, ": slide login exception")
        await simulate_slide(page)
        return False
    else:
        await asyncio.sleep(3)
        slider_tips = await page.Jeval(".nc-lang-cnt", "node => node.textContent")
        if slider_tips != "验证通过":
            print(slider_tips)
            await simulate_slide(page)
            return False
        else:
            await page.screenshot(path="tmp/taobao-slider-success.png")
            print("滑动条验证通过")
            return True


async def cookie(page: page.Page):
    content = await page.content()
    print("content length: ", len(content))

    cookies = await page.cookies()
    cookie_list = []
    for cookie in cookies:
        cookie_list.append("{}={}".format(cookie.get("name"), cookie.get("value")))

    print("cookies: ", cookie_list)
    return ";".join(cookie_list)


async def close(browser):
    for page in await browser.pages():
        await page.close()
    await browser.close()


async def login(url, useranme, password):

    width, height = screen_size()

    browser = await launch(headless=False, dumpio=True, userDataDir='./user-data', args=["--disable-infobars", "--start-maximized"])

    page = await browser.newPage()
    await page.setViewport(viewport={"width": width, "height": height})
    await page.setUserAgent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36")
    response = await page.goto(url)
    print("response status: ", response.status)

    js_script = """
    () =>{ 
        Object.defineProperties(navigator,{ webdriver:{ get: () => false } });
        window.navigator.chrome = { runtime: {},  };
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5, 6], });
     }
    """

    await page.evaluate(js_script)
    # await page.evaluate("""() => { Object.defineProperties(navigator,{ webdriver:{ get: () => false } }); }""")

    # password_login_mode = await page.querySelector("a.password-login-tab-item")
    # print(await (await password_login_mode.getProperty('textContent')).jsonValue())
    # await password_login_mode.click()
    await page.click("a.password-login-tab-item")

    await page.type("input#fm-login-id", useranme, {"delay": random_delay_time() - 50})
    await page.type("input#fm-login-password", password, {"delay": random_delay_time()})

    await page.screenshot(path="tmp/taobao-input-finish.png")
    await asyncio.sleep(2)

    slider = await page.Jeval("#nocaptcha-password", "node => node.style.display")
    if slider != "none":
        print("滑块验证……")
        await page.screenshot(path="tmp/taobao-slider-login.png")

        successed = await simulate_slide(page)
        if successed:
            print("login success: ", page.url)
            # await page.focus("input#fm-login-password")
            await page.keyboard.press("Enter")
            cookies = await cookie(page)
            print("cookies: ", cookies)
        else:
            # await page.focus("input#fm-login-password")
            # await page.keyboard.press("Enter")
            # await page.waitFor(20)
            # await page.waitForNavigation()
            try:
                global error
                error = await page.Jeval(".errloading", "node => node.textContent")
            except Exception as e:
                error = None
                print(e, "验证出错了……")
            finally:
                if error:
                    print("确保账户安全，请重新输入")
                else:
                    print("login success: ", page.url)
                    # 无需重复登录，可以使用cookie
                    await page.goto("https://www.taobao.com")
                    await cookie(page)
    else:
        print("没有滑块验证……")
        await page.keyboard.press("Enter")
        cookies = await cookie(page)
        print("cookies: ", cookies)

    await close(browser)


asyncio.get_event_loop().run_until_complete(login("https://login.taobao.com/member/login.jhtml", "test112", "abc234234"))







