# -*- coding: utf-8 -*-
"""信号1：抖音话题搜索 -> 真实播放量榜。
用已登录的 dy 浏览器 profile 调 challenge/search（登录态接口），
每次查询返回约 20 个话题，含 cha_name / cid / view_count / user_count。
节奏：每次查询间隔 4-8 秒；单类 7-8 个查询；全部原始响应存 gzip JSONL。
断点续跑：每个查询的原始响应单独落盘，已存在则跳过。
"""
import asyncio
import csv
import gzip
import json
import os
import random
import time
from datetime import datetime

from playwright.async_api import async_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(BASE))
MC = os.path.join(ROOT, "03-抓取工具", "MediaCrawler")
USER_DIR = os.path.join(MC, "browser_data", "dy_user_data_dir")
RAW = os.path.join(BASE, "raw")
CACHE = os.path.join(RAW, "douyin_challenge_raw")
os.makedirs(CACHE, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

QUERIES = {
    "体重与代谢": ["减肥", "减脂", "胰岛素抵抗", "脂肪肝", "痛风", "血糖高", "轻断食", "代餐"],
    "心脑血管与呼吸": ["高血压", "高血脂", "心梗", "脑梗", "冠心病", "打呼噜", "房颤"],
    "消化与肝胆肾": ["便秘", "幽门螺杆菌", "胃炎", "肠易激", "肾结石", "肠道菌群", "肝硬化"],
    "睡眠与心理": ["失眠", "熬夜", "焦虑", "抑郁", "睡眠质量", "精神内耗", "褪黑素"],
    "女性健康": ["多囊", "更年期", "乳腺结节", "HPV", "痛经", "备孕", "产后修复", "子宫肌瘤"],
    "男性健康": ["前列腺", "前列腺炎", "睾酮", "精子质量", "男性更年期", "补肾", "阳痿"],
    "儿童青少年": ["儿童身高", "骨龄", "性早熟", "儿童近视", "儿童过敏", "挑食", "多动症", "小儿推拿"],
    "老年健康": ["肌少症", "骨质疏松", "老年痴呆", "帕金森", "跌倒", "老年便秘", "白内障"],
    "骨骼关节": ["颈椎病", "腰椎间盘突出", "肩周炎", "膝关节炎", "圆肩驼背", "腱鞘炎", "足底筋膜炎"],
    "免疫炎症抗衰": ["免疫力", "慢性炎症", "抗炎饮食", "抗衰老", "NMN", "荨麻疹", "桥本甲状腺炎", "甲状腺结节"],
    "皮肤毛发口腔": ["痘痘", "敏感肌", "脱发", "脂溢性脱发", "牙周炎", "口腔溃疡", "湿疹", "黄褐斑"],
    "眼耳鼻喉": ["干眼症", "飞蚊症", "近视", "耳鸣", "鼻炎", "咽炎", "中耳炎"],
    "营养补剂": ["益生菌", "维生素D", "蛋白粉", "鱼油", "钙片", "辅酶Q10", "胶原蛋白", "叶酸"],
    "中医养生": ["湿气重", "气血不足", "脾虚", "艾灸", "八段锦", "宫寒", "养肝", "上火"],
    "体检就医": ["体检报告", "肺结节", "甲状腺结节", "肿瘤标志物", "癌症筛查", "转氨酶高", "肠息肉"],
    "公共健康": ["流感", "甲流", "支原体肺炎", "疫苗", "食品安全", "预制菜", "空气污染", "甲醛"],
    "肿瘤重症": ["癌症早期症状", "化疗", "靶向药", "乳腺癌", "肺癌", "胃癌", "肝癌", "甲状腺癌"],
    "成瘾职业": ["戒烟", "戒酒", "酒精依赖", "久坐", "夜班", "咖啡因", "手机成瘾"],
}


def now_iso():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


async def main():
    rows = []
    started = now_iso()
    async with async_playwright() as pw:
        ctx = await pw.chromium.launch_persistent_context(
            USER_DIR, headless=True, user_agent=UA,
            viewport={"width": 1440, "height": 900},
            args=["--disable-blink-features=AutomationControlled"])
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.douyin.com/", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(4)
        print("browser ready", page.url, flush=True)

        done = 0
        for cat, queries in QUERIES.items():
            for q in queries:
                safe = q.replace("/", "_")
                cache_path = os.path.join(CACHE, f"{cat}__{safe}.json")
                if os.path.exists(cache_path):
                    data = json.load(open(cache_path, encoding="utf-8"))
                    print(f"[skip] {cat} / {q}", flush=True)
                else:
                    payload = await page.evaluate(
                        """async (kw) => {
                            const u = '/aweme/v1/web/challenge/search/?keyword=' + encodeURIComponent(kw)
                                + '&device_platform=webapp&aid=6383&channel=channel_pc_web&count=20&offset=0';
                            try {
                                const res = await fetch(u, {credentials: 'include'});
                                const t = await res.text();
                                return {status: res.status, body: t};
                            } catch (e) { return {err: String(e)}; }
                        }""", q)
                    ts = now_iso()
                    data = {"category_18": cat, "query": q, "collected_at": ts,
                            "http_status": payload.get("status"),
                            "body": payload.get("body", "")}
                    if payload.get("err"):
                        data["error"] = payload["err"]
                    json.dump(data, open(cache_path, "w", encoding="utf-8"),
                              ensure_ascii=False)
                    done += 1
                    body = data.get("body") or ""
                    if "请先登录" in body or '"status_code":2483' in body:
                        print("LOGIN REQUIRED - stop", flush=True)
                        await ctx.close()
                        return
                    print(f"[{done}] {cat} / {q} status={data['http_status']} len={len(body)}",
                          flush=True)
                    await asyncio.sleep(random.uniform(4.0, 8.0))

                body = data.get("body") or ""
                try:
                    j = json.loads(body)
                except Exception:
                    continue
                for item in (j.get("challenge_list") or []):
                    ci = item.get("challenge_info") or {}
                    name = (ci.get("cha_name") or "").strip()
                    if not name:
                        continue
                    rows.append({
                        "category_query": cat, "query": q,
                        "rank_in_query": item.get("position"),
                        "topic": name,
                        "challenge_id": str(ci.get("cid") or ""),
                        "play": int(ci.get("view_count") or 0),
                        "users": int(ci.get("user_count") or 0),
                        "is_commerce": ci.get("is_commerce"),
                        "collected_at": data.get("collected_at"),
                    })
        await ctx.close()

    # 去重：同 topic+cid 保留最小 rank
    dedup = {}
    for r in rows:
        k = (r["topic"], r["challenge_id"])
        if k not in dedup:
            dedup[k] = r
        else:
            old = dedup[k]
            try:
                if (r["rank_in_query"] or 99) < (old["rank_in_query"] or 99):
                    dedup[k] = r
            except TypeError:
                pass
    out_rows = list(dedup.values())
    out_rows.sort(key=lambda r: -r["play"])

    out = os.path.join(RAW, "douyin_topics.csv")
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["category_query", "query", "rank_in_query", "topic",
                                          "challenge_id", "play", "users", "is_commerce",
                                          "collected_at"])
        w.writeheader()
        w.writerows(out_rows)

    # 原始合并包（含每次查询的完整响应），便于复核
    rawgz = os.path.join(RAW, "douyin_challenge_search_raw.jsonl.gz")
    with gzip.open(rawgz, "wt", encoding="utf-8") as f:
        for fn in sorted(os.listdir(CACHE)):
            if fn.endswith(".json"):
                f.write(json.dumps(json.load(open(os.path.join(CACHE, fn), encoding="utf-8")),
                                   ensure_ascii=False) + "\n")

    print(f"rows {len(out_rows)} -> {out}", flush=True)
    print("raw ->", rawgz, flush=True)
    print("started", started, "ended", now_iso(), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
