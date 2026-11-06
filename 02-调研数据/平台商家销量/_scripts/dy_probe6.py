# -*- coding: utf-8 -*-
"""Probe mobile Douyin / haohuo commerce search surfaces."""
import asyncio
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
KW = "减脂营"

URLS = [
    ("m_search", f"https://m.douyin.com/search/{KW}"),
    ("www_mobile", f"https://www.douyin.com/search/{KW}?type=general"),
    ("haohuo_ecom", f"https://haohuo.jinritemai.com/ecommerce/trade/search?keyword={KW}"),
    ("haohuo_search2", f"https://haohuo.jinritemai.com/views/search/index?search_key={KW}&from=home"),
]


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 390, "height": 844},
            user_agent=IPHONE_UA, is_mobile=True, has_touch=True,
            locale="zh-CN", timezone_id="Asia/Shanghai",
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        for name, url in URLS:
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(6000)
                txt = await page.evaluate("document.body.innerText")
            except Exception as e:
                print(f"[{name}] ERR {e}")
                continue
            print(f"[{name}] final={page.url} title={await page.title()!r} len={len(txt)} sold={'已售' in txt}")
            print("  TXT:", txt[:700].replace("\n", " | "))
        await ctx.close()


asyncio.run(main())
