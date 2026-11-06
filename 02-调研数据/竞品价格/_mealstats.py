# -*- coding: utf-8 -*-
import csv, math, re
P = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\竞品价格\代餐品牌_SKU价格.csv"
rows = list(csv.DictReader(open(P, encoding="utf-8-sig")))
print("rows", len(rows))

def f(x):
    m = re.match(r"\s*([\d.]+)", str(x))
    return float(m.group(1)) if m else None

def pct(v, p):
    v = sorted(v)
    k = (len(v) - 1) * p
    a, b = math.floor(k), math.ceil(k)
    return v[a] if a == b else v[a] + (v[b] - v[a]) * (k - a)

meal = [(r["品牌"], r["产品名"], f(r["折合每餐"]), r["置信度"]) for r in rows if f(r["折合每餐"])]
print("\n每餐 n=%d" % len(meal))
for x in sorted(meal, key=lambda t: t[2]): print(f"   {x[2]:5.1f}  {x[0]:8s} {x[1][:34]} [{x[3]}]")
v = [x[2] for x in meal]
print(f"min={min(v):.1f} P25={pct(v,.25):.1f} P50={pct(v,.5):.1f} P75={pct(v,.75):.1f} max={max(v):.1f}")

# 全餐型每天（一日3餐的套餐）
day = [(r["品牌"], r["产品名"], f(r["折合每天"]), r["置信度"]) for r in rows
       if f(r["折合每天"]) and ("21天" in r["规格"] or "3天" in r["规格"] or "2个月" in r["规格"])]
print("\n全餐型每天 n=%d" % len(day))
for x in sorted(day, key=lambda t: t[2]): print(f"   {x[2]:5.1f}  {x[0]:8s} {x[1][:34]} [{x[3]}]")
v2 = [x[2] for x in day]
print(f"min={min(v2):.1f} P25={pct(v2,.25):.1f} P50={pct(v2,.5):.1f} P75={pct(v2,.75):.1f} max={max(v2):.1f}")

print("\n每月：", [(r["品牌"], r["折合每月"]) for r in rows if "≈" in r["折合每月"] or "元" in r["折合每月"]])
print("\n品牌集中度：")
from collections import Counter
for k, c in Counter(r["品牌"] for r in rows).most_common(): print(" ", k, c)
print("\n未取得价格：", [(r["品牌"], r["产品名"][:20]) for r in rows if r["页面价"] in ("需登录", "未公开")])
