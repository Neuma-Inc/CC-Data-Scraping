# -*- coding: utf-8 -*-
"""检查抖音话题采集结果的类目分布与质量，并生成每类 Top N 供候选池使用。"""
import csv
import collections
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw")
p = os.path.join(RAW, "douyin_topics.csv")
rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
print("rows", len(rows))
c = collections.Counter(r["category_query"] for r in rows)
for k, v in c.items():
    print(f"{k}\t{v}")

by = collections.defaultdict(list)
for r in rows:
    by[r["category_query"]].append(r)

print("\n--- top 10 per category ---")
for k, v in by.items():
    v.sort(key=lambda x: -int(x["play"] or 0))
    print(f"\n## {k} ({len(v)})")
    print(" | ".join(f"{x['topic']}={int(x['play'])/1e8:.1f}亿" for x in v[:10]))

# 每类取 15-60：按播放量降序，最多 60；不足 15 如实标注
out = []
for k, v in by.items():
    v.sort(key=lambda x: -int(x["play"] or 0))
    keep = v[:60]
    for i, r in enumerate(keep, 1):
        out.append({"category_18": k, "rank_in_category": i, "topic": r["topic"],
                    "challenge_id": r["challenge_id"], "play": r["play"],
                    "users": r["users"], "query": r["query"],
                    "rank_in_query": r["rank_in_query"],
                    "collected_at": r["collected_at"]})
out.sort(key=lambda r: (r["category_18"], r["rank_in_category"]))
outp = os.path.join(RAW, "douyin_topics_by_category.csv")
with open(outp, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)
print("\nwrote", outp, len(out))
print("short categories (<15):", [k for k, v in by.items() if len(v) < 15])
