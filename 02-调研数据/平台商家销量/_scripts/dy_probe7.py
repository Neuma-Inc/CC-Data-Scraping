# -*- coding: utf-8 -*-
"""Probe so.douyin.com SEO search across keywords; detect tabs and commerce signals."""
import asyncio, urllib.parse
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

KWS = ["减肥训练营", "减脂陪跑", "营养师1v1", "减肥训练营 团购", "北京减肥训练营", "体重管理"]


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
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(5000)
                txt = await page.evaluate("document.body.innerText")
            except Exception as e:
                print(f"[{kw}] ERR {e}")
                continue
            head = txt[:120].replace("\n", " | ")
            print(f"[{kw}] len={len(txt)} sold={'已售' in txt} price={'¥' in txt or '元' in txt}")
            print("   TABS:", head)
            if "已售" in txt:
                i = txt.find("已售")
                print("   SOLDCTX:", txt[max(0, i-200):i+120].replace("\n", " | "))
            await page.wait_for_timeout(2500)
        await ctx.close()


asyncio.run(main())
