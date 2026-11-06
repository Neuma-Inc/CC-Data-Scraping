# -*- coding: utf-8 -*-
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(BASE, "raw", "pool_all_candidates.csv"),
                                encoding="utf-8-sig")))
for cat in ["眼耳鼻喉", "成瘾职业", "中医养生", "体检就医", "公共健康", "肿瘤重症"]:
    v = [r for r in rows if r["category_18"] == cat]
    print(f"\n## {cat} ({len(v)})")
    print("、".join(f"{r['word']}[{r['signal_sources']}]" for r in v[:50]))
