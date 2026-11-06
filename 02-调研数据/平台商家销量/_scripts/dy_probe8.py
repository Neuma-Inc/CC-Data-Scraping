# -*- coding: utf-8 -*-
"""Dump full so.douyin.com page text + links for commerce-heavy keywords."""
import asyncio, json, os, urllib.parse
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts"
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

KWS = ["减肥训练营 团购", "北京减肥训练营"]


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
        for kw in KWS:
            url = "https://so.douyin.com/s?keyword=" + urllib.parse.quote(kw)
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_timeout(4000)
            for _ in range(4):
                await page.mouse.wheel(0, 1600)
                await page.wait_for_timeout(1500)
            txt = await page.evaluate("document.body.innerText")
            links = await page.evaluate("""() => Array.from(document.querySelectorAll('a')).map(a=>({t:(a.innerText||'').trim().slice(0,60), h:a.href}))""")
            print(f"===== {kw} len={len(txt)} links={len(links)}")
            print(txt)
            print("----LINKS----")
            for l in links:
                print(l["t"], "|", l["h"])
            safe = kw.replace(" ", "_")
            with open(os.path.join(OUT, f"seo_{safe}.txt"), "w", encoding="utf-8") as f:
                f.write(txt)
            with open(os.path.join(OUT, f"seo_{safe}_links.json"), "w", encoding="utf-8") as f:
                json.dump(links, f, ensure_ascii=False, indent=1)
            await page.wait_for_timeout(2500)
        await ctx.close()


asyncio.run(main())
