# -*- coding: utf-8 -*-
"""One profile pass: capture bio + offer signals for candidate online-course accounts."""
import asyncio, json, os, re
from playwright.async_api import async_playwright

PROFILE = r"D:\A-灵知生物\小程序\05-市场调研\03-抓取工具\MediaCrawler\browser_data\dy_user_data_dir"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts\acct"

TARGETS = [
    ("闫帅奇", None),
    ("张大胆吃挺好", "MS4wLjABAAAAGzeynxRaRg-wPdlyLxLmG0LEykPhNEtKuQpyZo2vXIXJ2C9p9wduKIqEHDQtrQAx"),
    ("马教练（线上指导）", "MS4wLjABAAAAZ8TEevzitenh7A2AQL6VgPfXbKDdnhT77nfOI5ZuMeY"),
    ("仲昭金Adam", "MS4wLjABAAAA4whuX4CzkbgVvYmh2f8wNG4HlkD2Jsu0g6qqa1xRdRI"),
    ("巅峰减重健身训练营", "MS4wLjABAAAAulDjVPlc3_sYMYoJ1IlrTakIQl2IIiOzF7ikqg5OiPkYMSiQGqK2KKVh9zx4FgJo"),
    ("猫宁逆袭记", "MS4wLjABAAAAV0ndd_B0c8mywU4jSvogprEhr3Onala4BBI3p0y1-p4"),
    ("这个Ruby有点憨", "MS4wLjABAAAAq8_azjctpCjAU79-O3OuBmT_0Zu4KITgiWSNmB7Fg2Y"),
]

results = []


async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            PROFILE, headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1440, "height": 900},
            locale="zh-CN", timezone_id="Asia/Shanghai",
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        for name, uid in TARGETS:
            rec = {"name": name, "sec_uid": uid}
            try:
                if uid:
                    await page.goto(f"https://www.douyin.com/user/{uid}", wait_until="domcontentloaded", timeout=45000)
                else:
                    await page.goto("https://www.douyin.com/search/" + name + "?type=user", wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(5000)
                txt = await page.evaluate("document.body.innerText")
            except Exception as e:
                rec["error"] = str(e)
                results.append(rec)
                print("ERR", name, e)
                continue
            rec["text_len"] = len(txt)
            m = re.search(r"粉丝[\s\S]{0,20}?([\d\.]+万?)", txt)
            rec["fans_near"] = m.group(1) if m else None
            lines = [l.strip() for l in txt.split("\n") if l.strip()]
            rec["bio"] = " | ".join(lines[:25])[:600]
            rec["offer_hits"] = [l for l in lines if re.search(r"课程|训练营|橱窗|私信|报名|元|价格|陪跑|打卡", l)][:15]
            results.append(rec)
            print("==", name, "len", len(txt))
            print("  bio:", rec["bio"][:250])
            print("  hits:", rec["offer_hits"][:8])
            await page.wait_for_timeout(1200)
        await ctx.close()
    json.dump(results, open(os.path.join(OUT, "profile_pass.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


asyncio.run(main())
