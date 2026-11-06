# -*- coding: utf-8 -*-
"""Dump Redux state keys and locate card list on so.douyin.com."""
import asyncio, json, os, urllib.parse
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts\api"
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
             "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
KW = "北京减肥训练营"


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
        await page.goto("https://so.douyin.com/s?keyword=" + urllib.parse.quote(KW), wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(7000)

        keys = await page.evaluate("""() => {
            const st = window.__SEARCH_H5_STORE__.getState();
            const out = {};
            for (const k of Object.keys(st)) {
                let v = st[k];
                let size = 0, type = typeof v;
                try { size = JSON.stringify(v).length; } catch(e) { size = -1; }
                out[k] = {type, size, sub: (v && typeof v === 'object' && !Array.isArray(v)) ? Object.keys(v).slice(0,20) : null};
            }
            return out;
        }""")
        print(json.dumps(keys, ensure_ascii=False, indent=1))
        await ctx.close()


asyncio.run(main())
