# -*- coding: utf-8 -*-
"""Crawl so.douyin.com SEO search for online course keywords; inventory card types."""
import asyncio, json, os, re, urllib.parse, collections
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts\seo_pages"
os.makedirs(OUT, exist_ok=True)
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

KWS = ["减脂课", "减脂课程", "线上减脂营", "减脂陪跑", "体重管理课",
       "28天减脂营", "21天减脂营", "减脂训练营", "营养师陪跑", "1v1减脂", "居家减脂课"]


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
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(4500)
                for _ in range(3):
                    await page.mouse.wheel(0, 1500)
                    await page.wait_for_timeout(1200)
                html = await page.content()
            except Exception as e:
                print("ERR", kw, e)
                continue
            fn = os.path.join(OUT, re.sub(r"[^\w\-]", "_", kw) + ".html")
            with open(fn, "w", encoding="utf-8") as f:
                f.write(html)
            print("SAVED", kw, len(html))
            await page.wait_for_timeout(1800)
        await ctx.close()


asyncio.run(main())
