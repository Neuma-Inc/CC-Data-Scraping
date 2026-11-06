# -*- coding: utf-8 -*-
"""合并知乎90条编码 JSON -> CSV，并校验"""
import json, glob, os, re
import pandas as pd

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标'
SRC = os.path.join(BASE, r'400条抽样\400条_原始_知乎.csv')
OUT = os.path.join(BASE, r'400条编码\400条编码_知乎.csv')
COLS = ['编号','平台','搜索词','帖子类型','卡点可编码性','谁在说','触发事件','目标',
        '试过什么','卡在哪','具体问的问题（原话）','代表原话','点赞','总评论',
        '已抓评论','链接','置信度','备注']

src = pd.read_csv(SRC, encoding='utf-8-sig')
recs = []
for f in sorted(glob.glob(os.path.join(BASE, r'_dump\enc_*.json'))):
    with open(f, encoding='utf-8') as fh:
        recs.extend(json.load(fh))

print('records', len(recs))
by_id = {r['编号']: r for r in recs}
print('unique', len(by_id))

missing = [i for i in src['编号'] if i not in by_id]
print('missing', missing)

rows = []
for _, s in src.iterrows():
    r = by_id[s['编号']]
    row = {c: r.get(c, '') for c in COLS}
    row['点赞'] = s['点赞']
    row['总评论'] = s['总评论']
    row['已抓评论'] = s['已抓评论']
    row['链接'] = s['链接']
    rows.append(row)

df = pd.DataFrame(rows, columns=COLS)

# 校验：原话必须是原文子串
src_full = {}
for _, s in src.iterrows():
    src_full[s['编号']] = ''.join(str(s[c]) for c in ['标题','正文摘要','Top10评论'])
problems = []
for _, r in df.iterrows():
    full = src_full[r['编号']]
    norm = re.sub(r'\s+', '', full)
    for col in ['具体问的问题（原话）','代表原话']:
        v = str(r[col])
        if v.startswith('无'):
            continue
        if re.sub(r'\s+', '', v) not in norm:
            problems.append((r['编号'], col, v))
print('verbatim problems:', len(problems))
for p in problems:
    print('  ', p[0], p[1], '=>', p[2][:80])

# 空值校验
for c in COLS:
    empties = df[df[c].astype(str).str.strip() == '']
    if len(empties):
        print('EMPTY in', c, list(empties['编号']))

# 平台/搜索词 与源文件一致
for _, r in df.iterrows():
    s = src[src['编号'] == r['编号']].iloc[0]
    if str(r['平台']).strip() != str(s['平台']).strip():
        print('PLATFORM MISMATCH', r['编号'], r['平台'], s['平台'])
    if str(r['搜索词']).strip() != str(s['搜索词']).strip():
        print('TERM MISMATCH', r['编号'], r['搜索词'], '!=', s['搜索词'])

# 用户求助必须有具体问题
for _, r in df.iterrows():
    if r['帖子类型'] == '用户求助' and str(r['具体问的问题（原话）']).startswith('无'):
        print('HELP WITHOUT QUESTION', r['编号'])
    if r['帖子类型'] != '用户求助' and not str(r['具体问的问题（原话）']).startswith('无'):
        print('NON-HELP WITH QUESTION', r['编号'], r['帖子类型'], r['具体问的问题（原话）'][:40])

# 枚举值校验
allowed = {
 '帖子类型': {'用户求助','用户经历','博主科普','广告服务','用户吐槽','用户观点','其他'},
 '卡点可编码性': {'是','部分（回顾性）','部分（观点）','否'},
 '置信度': {'高','中','低'},
}
for c, vals in allowed.items():
    bad = set(df[c]) - vals
    print('BAD VALUES', c, bad) if bad else None

os.makedirs(os.path.dirname(OUT), exist_ok=True)
df.to_csv(OUT, index=False, encoding='utf-8-sig')
print('written', OUT, df.shape)
print('--- 帖子类型')
print(df['帖子类型'].value_counts().to_string())
print('--- 卡点可编码性')
print(df['卡点可编码性'].value_counts().to_string())
print('--- 置信度')
print(df['置信度'].value_counts().to_string())
