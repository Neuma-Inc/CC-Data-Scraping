# -*- coding: utf-8 -*-
"""汇总候选池数字，供 02-发现结果.md 和汇报使用。"""
import csv, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW = os.path.join(ROOT, "02-调研数据", "候选词发现", "raw")
POOL = os.path.join(ROOT, "02-调研数据", "候选词发现", "候选词池_v2.csv")


def n_src(r):
    return len([x for x in r["signal_sources"].split(";") if x])


def main():
    rows = list(csv.DictReader(open(POOL, encoding="utf-8-sig")))
    print("== TOTAL ==", len(rows))
    print("demand", sum(1 for r in rows if r["demand_signal"] == "1"),
          "supply", sum(1 for r in rows if r["supply_signal"] == "1"),
          "both", sum(1 for r in rows if r["demand_signal"] == "1" and r["supply_signal"] == "1"),
          "outside100", sum(1 for r in rows if r["in_original_100"] == "0"))
    cats = []
    for r in rows:
        if r["category_18"] not in cats:
            cats.append(r["category_18"])
    print("\n== BY CATEGORY ==")
    for c in cats:
        rs = [r for r in rows if r["category_18"] == c]
        print(f"{c}\t{len(rs)}\tdemand={sum(1 for r in rs if r['demand_signal']=='1')}"
              f"\tsupply={sum(1 for r in rs if r['supply_signal']=='1')}"
              f"\toutside={sum(1 for r in rs if r['in_original_100']=='0')}"
              f"\tcov={rs[0]['comment_coverage']}")
    print("\n== OUTSIDE-100 TOP3 PER CATEGORY ==")
    HEADS = {"减肥", "癌症", "肿瘤", "皮肤", "关节", "体检", "病毒", "气血", "老年", "乳腺",
             "代谢", "血压", "血糖", "血脂", "失眠", "焦虑", "抑郁", "便秘", "脱发", "痘痘",
             "鼻炎", "耳鸣", "疫苗", "流感", "甲醛", "胃病", "肠道", "前列腺", "补肾",
             "脾虚", "湿气重", "甲状腺", "肺结节", "多囊", "痛经", "更年期", "骨质疏松",
             "颈椎病", "腰椎间盘突出", "幽门螺杆菌", "脂肪肝", "痛风", "高血压", "高血脂",
             "糖尿病", "心梗", "脑梗", "荨麻疹", "湿疹", "干眼症", "咽炎", "鼻窦炎"}
    for c in cats:
        rs = [r for r in rows if r["category_18"] == c and r["in_original_100"] == "0"]
        long_tail = [r for r in rs if len(r["word"]) >= 3 and r["word"] not in HEADS]
        long_tail.sort(key=lambda r: (n_src(r), r["demand_signal"] == "1", r["supply_signal"] == "1",
                                      len(r["platforms_seen"].split(";"))), reverse=True)
        print(f"\n## {c}  (outside={len(rs)}, longtail={len(long_tail)})")
        for r in long_tail[:3]:
            print(f"  {r['word']}\tsrc={n_src(r)}\t{r['signal_sources']}\t{r['evidence_ref'][:80]}")
    print("\n== SOURCE COUNTS ==")
    from collections import Counter
    c = Counter()
    for r in rows:
        for s in r["signal_sources"].split(";"):
            if s:
                c[s] += 1
    for k, v in c.most_common():
        print(f"  {k}\t{v}")


if __name__ == "__main__":
    main()
