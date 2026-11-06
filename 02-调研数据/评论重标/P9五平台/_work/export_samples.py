# -*- coding: utf-8 -*-
import pandas as pd, os, re

BASE = r"D:\A-灵知生物\小程序\05-市场调研"
SRC = os.path.join(BASE, r"02-调研数据\评论重标\评论上下文宽表.csv")
OUT = os.path.join(BASE, r"02-调研数据\评论重标\P9五平台\_work")
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(SRC, dtype=str, keep_default_na=False)
p9 = df[df["主标签"] == "P9"].copy()

for pf in ["抖音", "B站", "知乎", "微博"]:
    sub = p9[p9["平台"] == pf].reset_index(drop=True)
    s = sub.sample(n=100, random_state=42).reset_index(drop=True)
    s.insert(0, "样本序号", range(1, 101))
    s.to_csv(os.path.join(OUT, pf + "_sample_raw.csv"), index=False, encoding="utf-8-sig")

    lines = []
    for _, r in s.iterrows():
        body = re.sub(r"\s+", " ", str(r["评论正文"]))[:230]
        title = re.sub(r"\s+", " ", str(r["原帖标题"]))[:45]
        lines.append("[%03d] %s  ## T:%s ## K:%s ## N:%s" % (
            r["样本序号"], body, title, str(r["抓取搜索词"])[:18], str(r["备注"])[:24]))
    with open(os.path.join(OUT, pf + "_sample.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(pf, len(sub), "saved")
