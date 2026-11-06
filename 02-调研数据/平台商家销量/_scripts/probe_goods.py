# -*- coding: utf-8 -*-
"""Test product-intent queries for ecom cards with 已售 (one pass, no retries)."""
import asyncio, json, os, re, urllib.parse, collections
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts\acct"
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

KWS = ["减脂课 多少钱", "减脂课 购买", "宁哥有礼 课程"]


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
            try:
                await page.goto("https://so.douyin.com/s?keyword=" + urllib.parse.quote(kw),
                                wait_until="domcontentloaded", timeout=50000)
                await page.wait_for_timeout(6000)
                for _ in range(2):
                    await page.mouse.wheel(0, 1500)
                    await page.wait_for_timeout(1200)
                html = await page.content()
            except Exception as e:
                print("ERR", kw, e)
                continue
            fn = os.path.join(OUT, "q_" + re.sub(r"[^\w\-]", "_", kw) + ".html")
            open(fn, "w", encoding="utf-8").write(html)
            tks = collections.Counter(re.findall(r'"templateKey":"([^"]+)"', html))
            print("==", kw, "len", len(html), "sold", html.count("已售"))
            for k, v in tks.most_common(6):
                print("   ", v, k)
            await page.wait_for_timeout(1500)
        await ctx.close()


asyncio.run(main())
