# -*- coding: utf-8 -*-
"""List JSON XHRs and page globals on so.douyin.com search page."""
import asyncio, json, os, urllib.parse
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
KW = "北京减肥训练营"

json_urls = []


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
            try:
                ct = resp.headers.get("content-type", "")
            except Exception:
                return
            if "json" in ct:
                json_urls.append((resp.status, resp.url, int(resp.headers.get("content-length") or 0)))

        page.on("response", on_resp)
        await page.goto("https://so.douyin.com/s?keyword=" + urllib.parse.quote(KW), wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(6000)
        for _ in range(3):
            await page.mouse.wheel(0, 1600)
            await page.wait_for_timeout(1500)

        print("JSON RESPONSES:", len(json_urls))
        seen = set()
        for st, u, ln in json_urls:
            key = u.split("?")[0]
            if key in seen:
                continue
            seen.add(key)
            print(st, ln, u[:240])

        globals_ = await page.evaluate("""() => {
            const out = [];
            for (const k of Object.keys(window)) {
                if (/SSR|INITIAL|DATA|RENDER|__/i.test(k)) out.push(k);
            }
            return out;
        }""")
        print("GLOBALS:", globals_)
        await ctx.close()


asyncio.run(main())
