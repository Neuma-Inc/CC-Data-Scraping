# -*- coding: utf-8 -*-
import csv
from collections import Counter
rows = list(csv.DictReader(open(r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\竞品价格\竞品SKU价格审计.csv", encoding="utf-8-sig")))

def b(r):
    t = r["退款政策"]
    if "不退" in t or "不可退" in t: return "明确不退/虚拟商品不退"
    if t.strip() == "免费" or "全免" in t: return "免费"
    if "可退" in t or "退订" in t or "退费" in t or "退还" in t: return "承诺可退/有条件可退"
    if "医保" in t or "自费" in t: return "医保结算/自费（非退款条款）"
    if "未公开" in t: return "未公开"
    return "其他"

print("--退款--")
for k, v in Counter(b(r) for r in rows).most_common(): print(k, v)
print("--证据--")
for k, v in Counter(r["证据类型"] for r in rows).most_common(): print(k, v)
print("--置信--")
for k, v in Counter(r["置信度"] for r in rows).most_common(): print(k, v)
print("--交付物--")
for k in ["营养师", "社群", "打卡", "代餐", "1v1", "体测", "食宿", "处方", "监测"]:
    print(k, sum(1 for r in rows if k in r["交付物"]))
print("--品牌数--", len(set(r["品牌/机构"] for r in rows)))
print("--含社群--", sum(1 for r in rows if r["是否含社群/打卡"].startswith("是")))
print("--含营养师--", sum(1 for r in rows if r["是否含营养师"].startswith("是")))
print("--销量有值--", sum(1 for r in rows if r["销量/报名人数(如有)"] != "未公开"))
