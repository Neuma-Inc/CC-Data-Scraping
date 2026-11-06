# -*- coding: utf-8 -*-
"""Rebuild 400条编码_B站.csv from source + appended code batches."""
import pandas as pd, json, os, re, sys

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, '..', '..', '400条抽样', '400条_原始_B站.csv')
codes_path = os.path.join(base, 'codes.jsonl')
out_path = os.path.join(base, '..', '400条编码_B站.csv')

COLS = ['编号', '平台', '搜索词', '帖子类型', '卡点可编码性', '谁在说', '触发事件', '目标',
        '试过什么', '卡在哪', '具体问的问题（原话）', '代表原话', '点赞', '总评论', '已抓评论',
        '链接', '置信度', '备注']

src_df = pd.read_csv(src, encoding='utf-8-sig')
codes = []
if os.path.exists(codes_path):
    with open(codes_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                codes.append(json.loads(line))
code_df = pd.DataFrame(codes).drop_duplicates(subset=['编号'], keep='last')

merged = src_df.merge(code_df, on='编号', how='left', suffixes=('', '_coded'))
missing = merged[merged['帖子类型'].isna()]['编号'].tolist()

# --- verbatim check ---
def norm(s):
    return re.sub(r'\s+', '', str(s))

def source_text(row):
    return norm(str(row['标题']) + str(row['正文摘要']) + str(row['Top10评论']))

bad = []
for _, r in merged.dropna(subset=['帖子类型']).iterrows():
    txt = source_text(r)
    for col in ['具体问的问题（原话）', '代表原话']:
        q = str(r[col]).strip()
        if not q or q.startswith('无') or q.startswith('不适用'):
            continue
        if norm(q) not in txt:
            bad.append((r['编号'], col, q))

merged['平台'] = 'B站'
out = merged[COLS].copy()
out.to_csv(out_path, index=False, encoding='utf-8-sig')

print('coded rows:', len(merged) - len(missing), '/', len(merged))
if missing:
    print('MISSING:', missing)
if bad:
    print('QUOTE CHECK FAILED:')
    for b in bad:
        print('  ', b)
else:
    print('quote check: OK')
print('written:', out_path)
print(out['帖子类型'].value_counts(dropna=False).to_string())
print(out['置信度'].value_counts(dropna=False).to_string())
