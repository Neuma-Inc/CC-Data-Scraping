# -*- coding: utf-8 -*-
"""Exact-match user lookup for fan counts (one pass)."""
import asyncio, json, os
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts\acct"

NAMES = ["闫帅奇", "张大胆吃挺好", "马教练（线上指导）", "仲昭金Adam",
         "巅峰减重健身训练营", "猫宁逆袭记", "这个Ruby有点憨", "宁哥继续有礼"]
found = {}


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1440, "height": 900},
            locale="zh-CN", timezone_id="Asia/Shanghai",
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        for name in NAMES:
            box = {}

            async def on_resp(resp, box=box):
                if "/aweme/v1/web/discover/search/" in resp.url or "/aweme/v1/web/general/search/single/" in resp.url:
                    try:
                        box.setdefault("d", []).append(await resp.json())
                    except Exception:
                        pass

            page.on("response", on_resp)
            try:
                await page.goto("https://www.douyin.com/search/" + name + "?type=user",
                                wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(4000)
            except Exception as e:
                print("ERR", name, e)
            page.remove_listener("response", on_resp)
            best = None
            for r in box.get("d", []):
                for u in (r.get("user_list") or []):
                    info = u.get("user_info") or u.get("user") or {}
                    if info.get("nickname") == name:
                        best = {"sec_uid": info.get("sec_uid"), "fans": info.get("follower_count"),
                                "signature": (info.get("signature") or "")[:120]}
                        break
                if best:
                    break
            found[name] = best
            print(name, "->", best)
            await page.wait_for_timeout(1000)
        await ctx.close()
    json.dump(found, open(os.path.join(OUT, "fans_lookup.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


asyncio.run(main())
