# -*- coding: utf-8 -*-
"""Offline inventory of already-saved SEO pages (no network)."""
import json, os, re, sys, collections
sys.path.insert(0, r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts")
from parse_seo import extract_chunks, walk_cards, spu_info

DIR = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts\seo_pages"
OUT = r"D:\A-灵知生物\小程序\05-市场调研\02-调研数据\平台商家销量\_scripts\interim_inventory.json"


def collect_template_keys(obj, counter):
    if isinstance(obj, dict):
        tk = obj.get("templateKey")
        if isinstance(tk, str):
            counter[tk] += 1
        for v in obj.values():
            collect_template_keys(v, counter)
    elif isinstance(obj, list):
        for v in obj:
            collect_template_keys(v, counter)


def collect_awemes(obj, out):
    if isinstance(obj, dict):
        if "aweme_info" in obj and isinstance(obj["aweme_info"], dict):
            aw = obj["aweme_info"]
            au = aw.get("author") or {}
            out.append({
                "desc": (aw.get("desc") or "")[:160],
                "author": au.get("nickname"),
                "sec_uid": au.get("sec_uid"),
                "fans": au.get("follower_count"),
                "likes": (aw.get("statistics") or {}).get("digg_count"),
            })
        for v in obj.values():
            collect_awemes(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_awemes(v, out)


summary = {}
for fn in sorted(os.listdir(DIR)):
    if not fn.endswith(".html"):
        continue
    html = open(os.path.join(DIR, fn), encoding="utf-8", errors="ignore").read()
    chunks = extract_chunks(html)
    tk = collections.Counter()
    pois = []
    awemes = []
    for c in chunks:
        collect_template_keys(c, tk)
        walk_cards(c, pois)
        collect_awemes(c, awemes)
    cards = []
    for h in pois:
        cards.append({
            "poi_name": h.get("poi_name"),
            "poi_id": h.get("poi_id"),
            "avg_cost": h.get("avg_cost"),
            "score": ((h.get("poi_score") or {}).get("poi_score_info") or {}).get("score"),
            "reviews": (((h.get("poi_score") or {}).get("poi_score_info") or {}).get("rate_info") or {}).get("cnt_num"),
            "rank": h.get("rank_list"),
            "sale_tags": h.get("sale_popularity_tag"),
            "spus": [spu_info(s) for s in h.get("spu_area_spu_list", [])],
        })
    summary[fn] = {"chunks": len(chunks), "poi_cards": cards, "aweme_count": len(awemes),
                   "templates": tk.most_common(20)}

json.dump(summary, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for fn, s in summary.items():
    print("=" * 70)
    print(fn, "chunks", s["chunks"], "poi", len(s["poi_cards"]), "aweme", s["aweme_count"])
    print("templates:", s["templates"][:8])
    for c in s["poi_cards"]:
        print("  POI:", c["poi_name"], "| score", c["score"], "| rev", c["reviews"], "| avg", c["avg_cost"])
        for sp in c["spus"]:
            print("     -", sp)
print("saved", OUT)
