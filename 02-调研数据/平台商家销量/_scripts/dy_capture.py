# -*- coding: utf-8 -*-
"""Capture Douyin general-search API JSON to inspect commerce fields."""
import asyncio, json, os, re
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts"
KW = "减脂营"

captured = []


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1440, "height": 900},
            locale="zh-CN", timezone_id="Asia/Shanghai",
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        async def on_resp(resp):
            u = resp.url
            if "search" in u and ("/aweme/v1/web" in u or "search/single" in u):
                try:
                    body = await resp.json()
                except Exception:
                    return
                captured.append((u, body))

        page.on("response", on_resp)
        await page.goto(f"https://www.douyin.com/search/{KW}?type=general", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(6000)
        for i in range(3):
            await page.mouse.wheel(0, 1800)
            await page.wait_for_timeout(1800)

        print("CAPTURED:", len(captured))
        for idx, (u, body) in enumerate(captured):
            print(idx, u[:160], "keys:", list(body.keys())[:20] if isinstance(body, dict) else type(body))
            fn = os.path.join(OUT, f"dy_search_{idx}.json")
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(body, f, ensure_ascii=False, indent=1)
            print("  saved", fn)
        await ctx.close()


asyncio.run(main())
