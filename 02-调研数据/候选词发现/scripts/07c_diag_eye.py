# -*- coding: utf-8 -*-
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw")
clean = list(csv.DictReader(open(os.path.join(RAW, "douyin_topics_clean.csv"),
                                 encoding="utf-8-sig")))
pool = list(csv.DictReader(open(os.path.join(RAW, "pool_all_candidates.csv"),
                               encoding="utf-8-sig")))
pcat = {r["word"]: r["category_18"] for r in pool}

for cat in ["眼耳鼻喉", "成瘾职业"]:
    v = [r for r in clean if r["category_18"] == cat]
    print(f"\n## clean {cat} ({len(v)})")
    print("、".join(r["topic"] for r in v[:30]))
    print("in pool as:")
    for r in v[:30]:
        print(f"  {r['topic']} -> {pcat.get(r['topic'], 'MISSING')}")
