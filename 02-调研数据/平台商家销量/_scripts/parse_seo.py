# -*- coding: utf-8 -*-
"""Parse Douyin SEO search SSR chunks -> groupbuy POI cards."""
import json, re, sys, os

CHUNK_RE = re.compile(r"<script[^>]*>\s*try\s*\{\s*let data = ", re.S)


def extract_chunks(html: str):
    """Return list of parsed JSON objects from SSR chunks."""
    out = []
    for m in CHUNK_RE.finditer(html):
        start = m.end()
        # find the terminating ';' that closes the assignment: scan with a brace counter
        depth = 0
        i = start
        in_str = False
        esc = False
        while i < len(html):
            ch = html[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        blob = html[start:i + 1]
                        try:
                            out.append(json.loads(blob))
                        except Exception as e:
                            print("PARSE_ERR", e, file=sys.stderr)
                        break
            i += 1
    return out


def walk_cards(obj, hits):
    if isinstance(obj, dict):
        if "spu_area_spu_list" in obj and obj.get("spu_area_spu_list"):
            hits.append(obj)
        for v in obj.values():
            walk_cards(v, hits)
    elif isinstance(obj, list):
        for v in obj:
            walk_cards(v, hits)


def spu_info(spu):
    name = None
    for k in ("spu_name", "title", "product_name", "name"):
        if spu.get(k):
            name = spu[k]
            break
    if not name:
        # sometimes nested
        for k in ("spu_title", "content"):
            if spu.get(k):
                name = spu[k]
                break
    price = None
    ps = spu.get("price_strong_style") or {}
    if ps.get("content"):
        price = ps.get("prefix", "") + ps.get("content", "")
    sold = None
    for sp in (spu.get("sale_popularity") or []):
        if sp.get("content"):
            sold = sp["content"]
            break
    orig = None
    ip = spu.get("introduce_price") or {}
    if ip.get("best_final_price"):
        orig = ip["best_final_price"] / 100 if ip["best_final_price"] > 1000 else ip["best_final_price"]
    return {"name": name, "price_raw": price, "display_price": spu.get("display_price"), "sold": sold, "orig": orig}


if __name__ == "__main__":
    p = sys.argv[1]
    html = open(p, encoding="utf-8", errors="ignore").read()
    chunks = extract_chunks(html)
    print("chunks:", len(chunks))
    hits = []
    for c in chunks:
        walk_cards(c, hits)
    print("poi cards:", len(hits))
    for h in hits:
        print("=" * 60)
        print("name:", h.get("poi_name") or h.get("name"))
        print("poi_id:", h.get("poi_id") or h.get("poi_shelf_id"))
        print("score:", (h.get("score_info") or {}).get("score_text") if isinstance(h.get("score_info"), dict) else h.get("score_text"))
        print("cost:", h.get("cost"), "rank:", h.get("rank_list"))
        print("sale_tags:", h.get("sale_popularity_tag"))
        print("addr:", h.get("address") or h.get("poi_address"))
        print("keys sample:", [k for k in h.keys()][:40])
        for s in h["spu_area_spu_list"]:
            print("   SPU:", spu_info(s))
