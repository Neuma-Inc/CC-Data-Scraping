# -*- coding: utf-8 -*-
"""解析 challenge/search 返回结构，确认字段名。"""
import asyncio
import json
import os

from playwright.async_api import async_playwright

MC = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler"
USER_DIR = os.path.join(MC, "browser_data", "dy_user_data_dir")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


async def main():
    async with async_playwright() as pw:
        ctx = await pw.chromium.launch_persistent_context(
            USER_DIR, headless=True, user_agent=UA,
            viewport={"width": 1440, "height": 900})
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.douyin.com/", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(4)
        r = await page.evaluate(
            """async (kw) => {
                const u = '/aweme/v1/web/challenge/search/?keyword=' + encodeURIComponent(kw)
                    + '&device_platform=webapp&aid=6383&channel=channel_pc_web&count=20&offset=0';
                const res = await fetch(u, {credentials: 'include'});
                return await res.json();
            }""", "前列腺")
        lst = r.get("challenge_list") or []
        print("count", len(lst))
        for item in lst[:5]:
            ci = item.get("challenge_info") or item
            keep = {k: ci.get(k) for k in
                    ["cha_name", "cid", "challenge_id", "view_count", "user_count",
                     "create_time", "desc", "is_commerce", "sub_type"] if k in ci}
            print(json.dumps(keep, ensure_ascii=False))
        print("top keys of item:", list(lst[0].keys()) if lst else None)
        print("top keys of challenge_info:", list((lst[0].get("challenge_info") or {}).keys())[:40] if lst else None)
        await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())
