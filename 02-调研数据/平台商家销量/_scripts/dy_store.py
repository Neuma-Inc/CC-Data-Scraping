# -*- coding: utf-8 -*-
"""Extract structured card data from so.douyin.com __SEARCH_H5_STORE__."""
import asyncio, json, os, urllib.parse
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts\api"
os.makedirs(OUT, exist_ok=True)
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

        info = await page.evaluate("""() => {
            const s = window.__SEARCH_H5_STORE__;
            const t = window._data_test_cardlist;
            const out = {};
            try { out.storeType = s ? (s.constructor ? s.constructor.name : typeof s) : null; } catch(e) { out.storeType = 'err'; }
            try { out.storeKeys = s && typeof s === 'object' ? Object.keys(s).slice(0,50) : null; } catch(e) {}
            try { out.storeStrLen = s ? JSON.stringify(s).length : 0; } catch(e) { out.storeStrLen = -1; }
            try { out.testType = t ? (t.constructor ? t.constructor.name : typeof t) : null; } catch(e) {}
            try { out.testLen = t ? JSON.stringify(t).length : 0; } catch(e) { out.testLen = -1; }
            return out;
        }""")
        print(json.dumps(info, ensure_ascii=False, indent=1))

        dump = await page.evaluate("""() => {
            const out = {};
            try { out.store = window.__SEARCH_H5_STORE__; } catch(e) {}
            try { out.cardlist = window._data_test_cardlist; } catch(e) {}
            return out;
        }""")
        with open(os.path.join(OUT, "store_dump.json"), "w", encoding="utf-8") as f:
            json.dump(dump, f, ensure_ascii=False)
        print("saved store_dump.json")
        await ctx.close()


asyncio.run(main())
