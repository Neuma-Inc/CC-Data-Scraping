# -*- coding: utf-8 -*-
"""Probe Douyin merchant profiles for commerce tabs / shop window."""
import asyncio, json
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"

USERS = [
    ("扬州鑫梦享", "MS4wLjABAAAAXYWYwaSxTltNJe107-PZngp0uo-Jlf7anFjq30d4g1NC67o4Fyzi1R6Io4Ui-SIq"),
    ("无锡净塑减肥训练营", "MS4wLjABAAAAMD3EIRgZEPKNxEJW0jkMnoonzRNHGop4RZzjPBUwCcQ"),
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
        for name, uid in USERS:
            url = f"https://www.douyin.com/user/{uid}"
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(6000)
                txt = await page.evaluate("document.body.innerText")
            except Exception as e:
                print(f"[{name}] ERR {e}")
                continue
            print(f"=== {name} len={len(txt)} sold={'已售' in txt}")
            print(txt[:1500].replace("\n", " | "))
            links = await page.evaluate("""() => Array.from(document.querySelectorAll('a')).map(a=>a.href).filter(h=>/shop|product|poi|life|goods|store/.test(h)).slice(0,20)""")
            print("LINKS:", json.dumps(links, ensure_ascii=False))
        await ctx.close()


asyncio.run(main())
