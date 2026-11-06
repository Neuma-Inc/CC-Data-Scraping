# -*- coding: utf-8 -*-
"""探测：用已登录的抖音浏览器 profile 调 challenge/search，看是否能拿到话题列表。"""
import asyncio
import json
import os
import sys

from playwright.async_api import async_playwright

MC = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler"
USER_DIR = os.path.join(MC, "browser_data", "dy_user_data_dir")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


async def main():
    async with async_playwright() as pw:
        ctx = await pw.chromium.launch_persistent_context(
            USER_DIR, headless=True, user_agent=UA,
            viewport={"width": 1440, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.douyin.com/", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)
        print("url", page.url)
        print("title", await page.title())

        for kw in ["前列腺", "儿童身高"]:
            r = await page.evaluate(
                """async (kw) => {
                    const u = '/aweme/v1/web/challenge/search/?keyword=' + encodeURIComponent(kw)
                        + '&device_platform=webapp&aid=6383&channel=channel_pc_web&count=20&offset=0';
                    try {
                        const res = await fetch(u, {credentials: 'include'});
                        const t = await res.text();
                        return {status: res.status, body: t.slice(0, 1200)};
                    } catch (e) { return {err: String(e)}; }
                }""", kw)
            print("\n===", kw, json.dumps(r, ensure_ascii=False)[:1500])
            await asyncio.sleep(5)

        await ctx.close()


if __name__ == "__main__":
    asyncio.run(main())
