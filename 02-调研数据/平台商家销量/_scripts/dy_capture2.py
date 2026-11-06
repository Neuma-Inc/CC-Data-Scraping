# -*- coding: utf-8 -*-
"""Capture so.douyin.com search API responses to find 团购/已售 fields."""
import asyncio, json, os, urllib.parse
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts\api"
os.makedirs(OUT, exist_ok=True)
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
KW = "北京减肥训练营"

hits = []


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

        async def on_resp(resp):
            u = resp.url
            if "douyin" not in u and "toutiao" not in u and "snssdk" not in u:
                return
            try:
                ct = resp.headers.get("content-type", "")
                if "json" not in ct and "text" not in ct:
                    return
                body = await resp.text()
            except Exception:
                return
            if any(k in body for k in ("已售", "sales", "团购", "poi_list", "price")):
                hits.append((u, body))

        page.on("response", on_resp)
        url = "https://so.douyin.com/s?keyword=" + urllib.parse.quote(KW)
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(6000)
        for _ in range(4):
            await page.mouse.wheel(0, 1600)
            await page.wait_for_timeout(1800)

        print("HITS:", len(hits))
        for i, (u, body) in enumerate(hits):
            print(i, len(body), u[:200])
            fn = os.path.join(OUT, f"hit_{i}.json")
            with open(fn, "w", encoding="utf-8") as f:
                f.write(body)
        await ctx.close()


asyncio.run(main())
