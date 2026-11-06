# -*- coding: utf-8 -*-
"""信号2：搜索下拉联想（需求信号）。
覆盖 B站 / 知乎 / 抖音 / 百度。每平台按字符前缀逐级请求，记录每一级联想词及顺序。
节奏：每平台串行，4-7 秒随机间隔；单平台上限 300 次；出现验证码/登录异常立即停。
小红书：等采集 agent 交付后再做，不在本脚本内。
微博：DOM 方案另跑，不在本脚本内。
"""
import csv
import hashlib
import json
import os
import random
import re
import threading
import time
from datetime import datetime

import requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw")
CACHE = os.path.join(RAW, "suggest_cache")
os.makedirs(CACHE, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

SEEDS = {
    "体重与代谢": ["减肥", "胰岛素抵抗", "脂肪肝", "痛风"],
    "心脑血管与呼吸": ["高血压", "高血脂", "心梗", "打呼噜"],
    "消化与肝胆肾": ["便秘", "幽门螺杆菌", "胃炎", "肠易激"],
    "睡眠与心理": ["失眠", "熬夜", "焦虑", "抑郁"],
    "女性健康": ["多囊", "更年期", "乳腺结节", "痛经"],
    "男性健康": ["前列腺", "睾酮", "精子质量", "补肾"],
    "儿童青少年": ["儿童身高", "性早熟", "儿童近视", "挑食"],
    "老年健康": ["肌少症", "骨质疏松", "老年痴呆", "帕金森"],
    "骨骼关节": ["颈椎病", "腰椎间盘突出", "肩周炎", "膝关节炎"],
    "免疫炎症抗衰": ["免疫力", "慢性炎症", "抗衰老", "荨麻疹"],
    "皮肤毛发口腔": ["痘痘", "敏感肌", "脱发", "口腔溃疡"],
    "眼耳鼻喉": ["干眼症", "耳鸣", "鼻炎", "飞蚊症"],
    "营养补剂": ["益生菌", "维生素D", "蛋白粉", "鱼油"],
    "中医养生": ["湿气重", "气血不足", "脾虚", "艾灸"],
    "体检就医": ["体检报告", "肺结节", "甲状腺结节", "肿瘤标志物"],
    "公共健康": ["流感", "疫苗", "食品安全", "预制菜"],
    "肿瘤重症": ["癌症早期症状", "化疗", "靶向药", "乳腺癌"],
    "成瘾职业": ["戒烟", "戒酒", "久坐", "夜班"],
}

PLATFORMS = ["bili", "zhihu", "douyin", "baidu"]
MAX_REQ_PER_PLATFORM = 300
STOP_WORDS = ("验证码", "captcha", "请先登录", "访问异常", "操作过于频繁")


def now_iso():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def prefixes(seed):
    if len(seed) <= 2:
        return [seed]
    out = [seed[:2], seed[: max(3, len(seed) // 2 + 1)], seed]
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def cache_path(platform, prefix):
    h = hashlib.md5(prefix.encode("utf-8")).hexdigest()[:12]
    return os.path.join(CACHE, f"{platform}_{h}.json")


class Adapter:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})

    def warm(self):
        pass

    def fetch(self, prefix):
        raise NotImplementedError


class Bili(Adapter):
    def fetch(self, prefix):
        r = self.s.get("https://s.search.bilibili.com/main/suggest",
                       params={"term": prefix, "main_ver": "v1"}, timeout=15)
        j = r.json()
        tags = (j.get("result") or {}).get("tag") or []
        return [t.get("value") for t in tags if t.get("value")], r.status_code


class Zhihu(Adapter):
    def warm(self):
        self.s.get("https://www.zhihu.com/", timeout=20)

    def fetch(self, prefix):
        from urllib.parse import quote
        r = self.s.get("https://www.zhihu.com/api/v4/search/suggest",
                       params={"q": prefix, "token": "", "max_matches": 10,
                               "use_similar": 1},
                       headers={"Referer": "https://www.zhihu.com/search?q=" + quote(prefix),
                                "x-requested-with": "fetch"}, timeout=15)
        j = r.json()
        return [x.get("query") for x in (j.get("suggest") or []) if x.get("query")], r.status_code


class Douyin(Adapter):
    def fetch(self, prefix):
        r = self.s.get("https://www.douyin.com/aweme/v1/web/search/sug/",
                       params={"keyword": prefix, "device_platform": "webapp",
                               "aid": "6383", "channel": "channel_pc_web"},
                       headers={"Referer": "https://www.douyin.com/"}, timeout=15)
        j = r.json()
        return [x.get("content") for x in (j.get("sug_list") or []) if x.get("content")], r.status_code


class Baidu(Adapter):
    def fetch(self, prefix):
        r = self.s.get("https://suggestion.baidu.com/su",
                       params={"wd": prefix, "action": "0"}, timeout=15)
        r.encoding = "gbk"
        t = r.text
        m = re.search(r"s:\[(.*?)\]", t, re.S)
        if not m:
            return [], r.status_code
        items = re.findall(r'"([^"]+)"', m.group(1))
        return items, r.status_code


ADAPTERS = {"bili": Bili, "zhihu": Zhihu, "douyin": Douyin, "baidu": Baidu}


def run_platform(platform):
    adapter = ADAPTERS[platform]()
    adapter.warm()
    out_path = os.path.join(RAW, f"suggestions_{platform}.csv")
    log_path = os.path.join(RAW, f"suggestions_{platform}_log.csv")
    row_f = open(out_path, "w", encoding="utf-8-sig", newline="")
    row_w = csv.writer(row_f)
    row_w.writerow(["platform", "category_18", "seed", "typed_prefix", "suggestion",
                    "rank", "collected_at"])
    log_f = open(log_path, "w", encoding="utf-8-sig", newline="")
    log_w = csv.writer(log_f)
    log_w.writerow(["platform", "typed_prefix", "http_status", "n_results",
                    "collected_at", "note"])

    n_req = 0
    n_rows = 0
    stop = False
    for cat, seeds in SEEDS.items():
        if stop:
            break
        for seed in seeds:
            if stop:
                break
            for pre in prefixes(seed):
                if n_req >= MAX_REQ_PER_PLATFORM:
                    stop = True
                    log_w.writerow([platform, pre, "", "", now_iso(), "MAX_REQ_REACHED"])
                    break
                cp = cache_path(platform, pre)
                cached = None
                if os.path.exists(cp):
                    cached = json.load(open(cp, encoding="utf-8"))
                    if cached.get("status") != 200 or not cached.get("items"):
                        cached = None
                if cached:
                    data = cached
                else:
                    try:
                        items, status = adapter.fetch(pre)
                    except Exception as e:
                        items, status = [], f"ERR:{str(e)[:80]}"
                    ts = now_iso()
                    data = {"platform": platform, "typed_prefix": pre, "status": status,
                            "items": items, "collected_at": ts}
                    json.dump(data, open(cp, "w", encoding="utf-8"), ensure_ascii=False)
                    n_req += 1
                    note = ""
                    body_join = " ".join(items)
                    if any(w in body_join for w in STOP_WORDS):
                        note = "STOP_WORD"
                        stop = True
                    if isinstance(status, str) or status != 200:
                        note = (note + ";HTTP_" + str(status)).strip(";")
                    log_w.writerow([platform, pre, status, len(items), ts, note])
                    log_f.flush()
                    if stop:
                        print(f"[{platform}] STOP at {pre}: {note}", flush=True)
                        break
                    time.sleep(random.uniform(4.0, 7.0))
                for i, sug in enumerate(data["items"], 1):
                    row_w.writerow([platform, cat, seed, pre, sug, i, data["collected_at"]])
                    n_rows += 1
                row_f.flush()
            print(f"[{platform}] {cat}/{seed} done, req={n_req}, rows={n_rows}", flush=True)
    row_f.close()
    log_f.close()
    print(f"[{platform}] FINISHED req={n_req} rows={n_rows}", flush=True)


def main():
    import sys
    targets = sys.argv[1:] or PLATFORMS
    threads = []
    for p in targets:
        t = threading.Thread(target=run_platform, args=(p,), daemon=False)
        t.start()
        threads.append(t)
        time.sleep(1.5)
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
