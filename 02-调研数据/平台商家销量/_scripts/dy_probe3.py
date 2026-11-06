# -*- coding: utf-8 -*-
"""Probe Douyin life-service surfaces (desktop)."""
import asyncio
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
KW = "减脂营"

URLS = [
    ("life_root", "https://www.douyin.com/life"),
    ("life_search_q", f"https://www.douyin.com/life/search?keyword={KW}"),
    ("life_search_p", f"https://www.douyin.com/life/search/{KW}"),
    ("life_tab", f"https://www.douyin.com/search/{KW}?type=general&source=life"),
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
                await page.wait_for_timeout(4500)
                txt = await page.evaluate("document.body.innerText")
            except Exception as e:
                print(f"[{name}] ERR {e}")
                continue
            print(f"[{name}] final={page.url} title={await page.title()!r} len={len(txt)} sold={'已售' in txt}")
            print("  HEAD:", txt[:300].replace("\n", " | "))
        await ctx.close()


asyncio.run(main())
