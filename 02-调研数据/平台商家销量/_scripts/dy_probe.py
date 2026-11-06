# -*- coding: utf-8 -*-
"""Probe Douyin search page with cached MediaCrawler profile."""
import asyncio, os, sys
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts"

KEYWORD = "减脂营"


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            viewport={"width": 1440, "height": 900},
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        url = f"https://www.douyin.com/search/{KEYWORD}?type=general"
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print("GOTO_ERR:", e)
        await page.wait_for_timeout(7000)
        print("TITLE:", await page.title())
        print("URL:", page.url)
        txt = await page.evaluate("document.body.innerText")
        print("TEXTLEN:", len(txt))
        print("----TEXT----")
        print(txt[:4000])
        await page.screenshot(path=os.path.join(OUT, "dy_probe.png"))
        with open(os.path.join(OUT, "dy_probe.html"), "w", encoding="utf-8") as f:
            f.write(await page.content())
        await ctx.close()


asyncio.run(main())
