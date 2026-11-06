# -*- coding: utf-8 -*-
"""Capture Douyin user + general search for target accounts/course keywords."""
import asyncio, json, os, urllib.parse
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts\acct"
os.makedirs(OUT, exist_ok=True)

JOBS = [
    ("user", "宁哥有礼"),
    ("general", "宁哥有礼"),
    ("general", "线上减脂营"),
    ("general", "28天减脂营"),
    ("general", "减脂课"),
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

        for kind, kw in JOBS:
            captured = []

            async def on_resp(resp, captured=captured):
                u = resp.url
                if "/aweme/v1/web/general/search/single/" in u or "/aweme/v1/web/discover/search/" in u:
                    try:
                        captured.append(await resp.json())
                    except Exception:
                        pass

            page.on("response", on_resp)
            url = f"https://www.douyin.com/search/{urllib.parse.quote(kw)}?type={kind}"
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=50000)
                await page.wait_for_timeout(5000)
                for _ in range(2):
                    await page.mouse.wheel(0, 1500)
                    await page.wait_for_timeout(1200)
            except Exception as e:
                print("ERR", kind, kw, e)
            page.remove_listener("response", on_resp)
            fn = os.path.join(OUT, f"{kind}_{kw}.json")
            json.dump(captured, open(fn, "w", encoding="utf-8"), ensure_ascii=False)
            print("SAVED", kind, kw, "responses", len(captured))
            await page.wait_for_timeout(1500)
        await ctx.close()


asyncio.run(main())
