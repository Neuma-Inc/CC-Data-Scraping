# -*- coding: utf-8 -*-
"""Probe Douyin POI / life-service H5 pages with mobile UA."""
import asyncio
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"

IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

URLS = [
    ("poi_suzhou", "https://aweme.snssdk.com/falcon/poi_mwa/poi_detail?poi_id=B0FFIVSFSI"),
    ("poi_yangzhou", "https://aweme.snssdk.com/falcon/poi_mwa/poi_detail?poi_id=B0FFIVSFSI"),
    ("douyin_poi", "https://www.douyin.com/poi/7489371721737177142"),
]


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 390, "height": 844},
            user_agent=IPHONE_UA,
            is_mobile=True,
            has_touch=True,
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
            print("  TXT:", txt[:1200].replace("\n", " | "))
        await ctx.close()


asyncio.run(main())
