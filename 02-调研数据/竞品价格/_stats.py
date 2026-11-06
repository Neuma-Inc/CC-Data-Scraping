# -*- coding: utf-8 -*-
import csv, math, re
from collections import Counter

P = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\竞品价格\竞品SKU价格审计.csv"
rows = list(csv.DictReader(open(P, encoding="utf-8-sig")))
print("total rows", len(rows))

def num(cell):
    try:
        return float(str(cell).replace(",", "").strip())
    except Exception:
        return None

def pct(v, p):
    v = sorted(v)
    if not v: return None
    k = (len(v) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    return v[f] if f == c else v[f] + (v[c] - v[f]) * (k - f)

CONF = {"高": 3, "中高": 2.5, "中": 2, "中低": 1, "低": 0.5, "未公开": 0}

# 证据分级：1=官方页/电商页/官方公示；2=媒体调查（记者实采/引合同）；3=访谈/评论
def tier(kind):
    if kind in ("官方页", "官方商城", "官方公告", "官方公示/媒体", "媒体（引医院价）", "媒体（引电商价）",
                "媒体（引官方页价）", "官方媒体", "分销公开页", "电商比价页", "比价站",
                "海淘比价页", "二手导航站"):
        return 1
    if kind in ("媒体调查", "公开页", "媒体公开页（品牌匿名）", "媒体"):
        return 2
    if kind in ("媒体访谈", "评论/投诉"):
        return 3
    return 2

def days(cyc, name=""):
    m = re.search(r"(\d+)\s*天", cyc)
    if m: return float(m.group(1))
    if "2个月" in cyc: return 60.0
    if "1个月" in cyc: return 30.0
    if "4周" in cyc: return 28.0
    if "2周" in cyc: return 14.0
    if "1周" in cyc: return 7.0
    if "月" in cyc: return 30.0
    return None

def eff(r):
    c = num(r["优惠价(如有)"])
    return c if c is not None else num(r["标价"])

def sel(cat_prefix, tier_max=1, month_norm=False, pred=None):
    out = []
    for r in rows:
        if not r["付费去向分类"].startswith(cat_prefix): continue
        if tier(r["证据类型"]) > tier_max: continue
        v = eff(r)
        if v is None: continue
        if pred and not pred(r): continue
        if month_norm:
            d = days(r["计价周期"], r["产品名"])
            if not d: continue
            v = v / d * 30
        out.append((r["品牌/机构"], r["产品名"], v, r["置信度"], r["证据类型"]))
    return out

def show(name, s):
    v = [x[2] for x in s]
    if not v:
        print(f"{name}: n=0"); return
    print(f"{name}: n={len(v)} min={min(v):.0f} P25={pct(v,.25):.0f} P50={pct(v,.5):.0f} P75={pct(v,.75):.0f} max={max(v):.0f}")

groups = []
# 类1：月化价（价/服务天数×30），仅官方+电商 与 含媒体调查 两版
groups.append(("C1 线下营 月化价（官方页口径）", sel("1-", tier_max=1, month_norm=True)))
groups.append(("C1 线下营 月化价（含媒体调查）", sel("1-", tier_max=2, month_norm=True)))
groups.append(("C1 线下营 每期实付（含媒体调查）", sel("1-", tier_max=2)))
groups.append(("C1 成人营 月化（含媒体调查）",
    sel("1-", tier_max=2, month_norm=True, pred=lambda r: "青少年" not in r["产品名"] and "超能瘦身" not in r["产品名"])))

# 类2
groups.append(("C2 线上营 月化价（官方/电商口径）", sel("2-", tier_max=1, month_norm=True)))
groups.append(("C2 线上营 月化价（含媒体调查）", sel("2-", tier_max=2, month_norm=True)))
groups.append(("C2 线上营 月化价（仅媒体访谈/评论）", sel("2-", tier_max=3, month_norm=True)))
groups.append(("C2 线上营 年卡", sel("2-", tier_max=2, pred=lambda r: "年" in r["计价周期"])))

# 类3：28天折算
groups.append(("C3 营养师套餐 28天折算（官方口径）", sel("3-", tier_max=1, month_norm=True, pred=lambda r: (eff(r) or 0) > 100)))
# 类4
groups.append(("C4 单件零售（罐/盒）", sel("4-", tier_max=2, pred=lambda r: "罐" in r["计价周期"] or "盒" in r["计价周期"])))
groups.append(("C4 周期套餐（天）", sel("4-", tier_max=2, pred=lambda r: "天" in r["计价周期"])))
groups.append(("C4 全部", sel("4-", tier_max=2)))
# 类5
groups.append(("C5 药品 月成本（28天折算）", sel("5-", tier_max=2, month_norm=True, pred=lambda r: "诺特" not in r["品牌/机构"])))
groups.append(("C5 药+服务包", sel("5-", tier_max=2, pred=lambda r: "诺特" in r["品牌/机构"])))
groups.append(("C5 全部", sel("5-", tier_max=2)))
# 类6
groups.append(("C6 单项服务(<=100)", sel("6-", tier_max=2, pred=lambda r: (eff(r) or 0) <= 100)))
groups.append(("C6 体检套餐", sel("6-", tier_max=2, pred=lambda r: "体检" in r["产品名"])))
# 类7
groups.append(("C7 正课/期（>=190，官方+媒体调查）", sel("7-", tier_max=2, pred=lambda r: (eff(r) or 0) >= 190)))
groups.append(("C7 全部", sel("7-", tier_max=2)))
groups.append(("C7 引流价（<190）", sel("7-", tier_max=2, pred=lambda r: (eff(r) or 0) < 190)))

for name, s in groups:
    show(name, s)
    for x in s:
        print(f"    {x[0]} | {x[1]} | {x[2]:.1f} | {x[3]} | {x[4]}")

print("\n=== 证据类型分布 ===")
for k, v in Counter(r["证据类型"] for r in rows).most_common(): print(f"{k}\t{v}")
print("\n=== 置信度分布 ===")
for k, v in Counter(r["置信度"] for r in rows).most_common(): print(f"{k}\t{v}")

print("\n=== 退款政策 ===")
for r in rows: print(f"{r['退款政策'][:60]}")
