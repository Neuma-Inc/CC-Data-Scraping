# -*- coding: utf-8 -*-
"""Probe multiple Douyin commerce URL patterns."""
import asyncio, os, re
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts"
KW = "减脂营"

URLS = [
    ("commodity", f"https://www.douyin.com/search/{KW}?type=commodity"),
    ("shop", f"https://www.douyin.com/search/{KW}?type=shop"),
    ("life", f"https://www.douyin.com/search/{KW}?type=life"),
    ("haohuo", f"https://haohuo.jinritemai.com/views/search/index?search_key={KW}"),
    ("mall", f"https://www.douyin.com/mall/search?keyword={KW}"),
]


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1440, "height": 900},
            locale="zh-CN", timezone_id="Asia/Shanghai",
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        for name, url in URLS:
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(5000)
                txt = await page.evaluate("document.body.innerText")
            except Exception as e:
                print(f"[{name}] ERR {e}")
                continue
            has_sold = "已售" in txt
            print(f"[{name}] url={page.url} title={await page.title()!r} len={len(txt)} sold={has_sold}")
            if has_sold:
                idx = txt.find("已售")
                print("  CTX:", txt[max(0, idx - 300):idx + 300].replace("\n", " | "))
            else:
                print("  HEAD:", txt[:400].replace("\n", " | "))
        await ctx.close()


asyncio.run(main())
