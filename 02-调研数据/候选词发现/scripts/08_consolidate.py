# -*- coding: utf-8 -*-
"""对候选池做一次可解释的粒度合并：
同一大类内，如果长词 = 修饰词 + 已选短词（或反之），合并到短词，
把长词的证据并入短词 evidence_ref，并记录合并日志。
只处理修饰性前后缀，不合并并发症类差异（如 糖尿病足 不并入 糖尿病）。
"""
import csv, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW = os.path.join(ROOT, "02-调研数据", "候选词发现", "raw")
POOL = os.path.join(ROOT, "02-调研数据", "候选词发现", "候选词池_v2.csv")
LOG = os.path.join(RAW, "pool_merge_log.csv")
STATS = os.path.join(RAW, "pool_stats_by_category.csv")

MODS = ["上", "值", "科学", "吧", "护士", "生活", "难熬", "新闻", "模式开启", "操",
        "打卡", "方法", "的症状", "的表现", "的人会", "的人", "术后", "手术",
        "筛查", "升高", "高发期", "如何应对", "关注", "儿童", "拿到", "入园", "甲型",
        "请尽早戒烟", "病毒"]
MODS = sorted(set(MODS), key=len, reverse=True)


def merge_once(rows):
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category_18"], []).append(r)
    drop = {}
    merges = []
    for cat, rs in by_cat.items():
        words = {r["word"] for r in rs}
        for r in rs:
            w = r["word"]
            if w in drop:
                continue
            for m in MODS:
                if w.startswith(m) and len(w) > len(m):
                    base = w[len(m):]
                    if base in words and base not in drop:
                        drop[w] = (base, m, "prefix")
                        merges.append((w, base, m, "prefix"))
                        break
                if w.endswith(m) and len(w) > len(m):
                    base = w[:-len(m)]
                    if base in words and base not in drop:
                        drop[w] = (base, m, "suffix")
                        merges.append((w, base, m, "suffix"))
                        break
    if not drop:
        return rows, merges
    kept = []
    base_of = {w: v[0] for w, v in drop.items()}
    # 解析多级合并
    def root(w):
        seen = set()
        while w in base_of and w not in seen:
            seen.add(w)
            w = base_of[w]
        return w
    for r in rows:
        if r["word"] in drop:
            continue
        kept.append(r)
    idx = {r["word"]: r for r in kept}
    for w, base, m, pos in merges:
        tgt = idx.get(root(base))
        if not tgt:
            continue
        src = next((x for x in rows if x["word"] == w), None)
        if not src:
            continue
        refs = tgt["evidence_ref"].split(" | ") if tgt["evidence_ref"] else []
        for x in src["evidence_ref"].split(" | "):
            if x and x not in refs and len(refs) < 12:
                refs.append(x)
        tgt["evidence_ref"] = " | ".join(refs)
        srcs = set(tgt["signal_sources"].split(";")) | set(src["signal_sources"].split(";"))
        tgt["signal_sources"] = ";".join(sorted(x for x in srcs if x))
        tgt["demand_signal"] = "1" if (tgt["demand_signal"] == "1" or src["demand_signal"] == "1") else "0"
        tgt["supply_signal"] = "1" if (tgt["supply_signal"] == "1" or src["supply_signal"] == "1") else "0"
        plats = set(tgt["platforms_seen"].split(";")) | set(src["platforms_seen"].split(";"))
        tgt["platforms_seen"] = ";".join(sorted(x for x in plats if x))
    return kept, merges


def main():
    with open(POOL, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    all_merges = []
    for _ in range(4):
        rows, ms = merge_once(rows)
        all_merges += ms
        if not ms:
            break
    rows.sort(key=lambda r: (r["category_18"], r["cand_id"]))
    fields = list(rows[0].keys())
    with open(POOL, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open(LOG, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["merged_word", "into_word", "modifier", "position"])
        w.writerows(all_merges)
    # 重算分类统计
    cov = {}
    for r in csv.DictReader(open(os.path.join(RAW, "comment_coverage_by_category.csv"), encoding="utf-8-sig")):
        cov[r["category_18"]] = r.get("coverage") or r.get("comment_coverage") or ""
    cats = []
    for r in rows:
        if r["category_18"] not in cats:
            cats.append(r["category_18"])
    with open(STATS, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category_18", "selected", "demand", "supply", "both", "outside_100", "comment_coverage"])
        for c in cats:
            rs = [r for r in rows if r["category_18"] == c]
            w.writerow([c, len(rs),
                        sum(1 for r in rs if r["demand_signal"] == "1"),
                        sum(1 for r in rs if r["supply_signal"] == "1"),
                        sum(1 for r in rs if r["demand_signal"] == "1" and r["supply_signal"] == "1"),
                        sum(1 for r in rs if r["in_original_100"] == "0"),
                        cov.get(c, "")])
    print("rows", len(rows), "merges", len(all_merges))
    for m in all_merges:
        print("  ", m[0], "->", m[1], f"({m[3]} {m[2]})")


if __name__ == "__main__":
    main()
