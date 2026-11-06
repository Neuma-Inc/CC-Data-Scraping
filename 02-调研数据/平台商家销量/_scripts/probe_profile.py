# -*- coding: utf-8 -*-
"""Open Douyin profile and locate shop window / commerce entries."""
import asyncio, json, os
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts\acct"
os.makedirs(OUT, exist_ok=True)

UID = "MS4wLjABAAAAfjLVnweIBHoVsLVTdmUmdmgR7PyDSU1p9uKITFeFTInGSDbdubMgWcJ6VM7_jhDE"


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1440, "height": 900},
            locale="zh-CN", timezone_id="Asia/Shanghai",
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        captured = []

        async def on_resp(resp):
            u = resp.url
            if "user/profile" in u or "shop" in u or "commerce" in u:
                try:
                    captured.append((u, await resp.json()))
                except Exception:
                    pass

        page.on("response", on_resp)
        await page.goto(f"https://www.douyin.com/user/{UID}", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(7000)

        txt = await page.evaluate("document.body.innerText")
        print("TEXTLEN", len(txt))
        print(txt[:1800].replace("\n", " | "))

        entries = await page.evaluate("""() => {
            const out = [];
            document.querySelectorAll('a,button,div,span').forEach(el => {
                const t = (el.innerText || '').trim();
                if (t && t.length < 30 && /橱窗|店铺|商品|小店|课程|团购|专栏/.test(t)) {
                    out.push({tag: el.tagName, text: t, href: el.href || null});
                }
            });
            return out.slice(0, 40);
        }""")
        print("ENTRIES:", json.dumps(entries, ensure_ascii=False, indent=1))

        links = await page.evaluate("""() => Array.from(document.querySelectorAll('a')).map(a=>a.href).filter(h=>/shop|product|haohuo|store|goods|course|column/.test(h)).slice(0,30)""")
        print("LINKS:", json.dumps(links, ensure_ascii=False, indent=1))

        for i, (u, body) in enumerate(captured):
            if isinstance(body, dict):
                ks = [k for k in body.keys() if any(x in k for x in ("shop", "commerce", "good", "product"))]
                print("API", i, u[:120], "keys:", ks)
                with open(os.path.join(OUT, f"profile_api_{i}.json"), "w", encoding="utf-8") as f:
                    json.dump(body, f, ensure_ascii=False)
        await ctx.close()


asyncio.run(main())
