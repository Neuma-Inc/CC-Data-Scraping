# -*- coding: utf-8 -*-
import re, os
import pandas as pd

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标'
SRC = os.path.join(BASE, r'400条抽样\400条_原始_小红书.csv')
COD = os.path.join(BASE, r'400条编码\400条编码_小红书.csv')

src = pd.read_csv(SRC, encoding='utf-8-sig')
cod = pd.read_csv(COD, encoding='utf-8-sig')
src['编号'] = src['编号'].astype(str).str.strip()
cod['编号'] = cod['编号'].astype(str).str.strip()
m = cod.merge(src, on='编号', suffixes=('', '_src'))

target = m[m['帖子类型'].isin(['博主科普', '广告服务', '其他'])].copy()
print('eligible posts:', len(target))

def parse_comments(s):
    if pd.isna(s) or str(s).strip().lower() == 'nan':
        return []
    parts = [p.strip() for p in str(s).split('||')]
    out = []
    for p in parts:
        if not p:
            continue
        mm = re.match(r'^\[赞(\d+)\]\s*(.*)$', p, re.S)
        if mm:
            out.append((int(mm.group(1)), mm.group(2).strip()))
        else:
            out.append((None, p))
    return out

lines = []
for _, r in target.iterrows():
    lines.append('=' * 100)
    lines.append(f"[{r['编号']}] {r['帖子类型']} | {r['搜索词']} | 赞{r['点赞']} 评{r['总评论']} | {r['标题']}")
    cs = parse_comments(r['Top10评论'])
    if not cs:
        lines.append('  (无评论)')
    for i, (lk, tx) in enumerate(cs, 1):
        lines.append(f"  {i:02d}. [赞{lk}] {tx}")
dst = os.path.join(BASE, r'400条编码\_signals_dump.txt')
open(dst, 'w', encoding='utf-8').write('\n'.join(lines))
print('written', dst, os.path.getsize(dst))
