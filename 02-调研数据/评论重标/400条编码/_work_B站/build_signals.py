# -*- coding: utf-8 -*-
"""Build 400条_评论需求_B站.csv from appended signal batches, with verbatim checks."""
import pandas as pd, json, os, re

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, '..', '..', '400条抽样', '400条_原始_B站.csv')
post_path = os.path.join(base, '..', '400条编码_B站.csv')
sig_path = os.path.join(base, 'signals.jsonl')
out_path = os.path.join(base, '..', '400条_评论需求_B站.csv')

COLS = ['信号编号', '平台', '来源帖子编号', '来源帖子标题', '帖子类型', '谁在说',
        '触发事件', '目标', '试过什么', '卡在哪', '具体问题（原话）', '代表原话',
        '评论赞', '置信度', '备注']

src = pd.read_csv(src, encoding='utf-8-sig')
post = pd.read_csv(post_path, encoding='utf-8-sig')
sig = []
if os.path.exists(sig_path):
    for line in open(sig_path, encoding='utf-8'):
        if line.strip():
            sig.append(json.loads(line))
sdf = pd.DataFrame(sig).drop_duplicates(subset=['信号编号'], keep='last')


def parse_comments(raw):
    out = []
    for p in [x.strip() for x in str(raw).split('||')]:
        m = re.match(r'^\[赞(\d+)\]\s*(.*)$', p, re.S)
        if m:
            out.append((int(m.group(1)), m.group(2).strip()))
        elif p:
            out.append((0, p))
    return out


def norm(s):
    return re.sub(r'\s+', '', str(s))


comments = {r['编号']: parse_comments(r['Top10评论']) for _, r in src.iterrows()}
pmap = post.set_index('编号')
title_map = src.set_index('编号')['标题']
problems = []
for _, r in sdf.iterrows():
    pid = r['来源帖子编号']
    cmts = comments.get(pid, [])
    txt_all = norm(''.join(c[1] for c in cmts))
    for col in ['具体问题（原话）', '代表原话']:
        q = str(r[col]).strip()
        if not q or q.startswith('无'):
            continue
        if norm(q) not in txt_all:
            problems.append((r['信号编号'], col, 'not found', q[:40]))
            continue
        if not any(norm(q) in norm(c[1]) and int(c[0]) == int(r['评论赞']) for c in cmts):
            problems.append((r['信号编号'], col, 'likes mismatch', r['评论赞']))

if not sdf.empty:
    sdf['平台'] = 'B站'
    sdf['来源帖子标题'] = sdf['来源帖子编号'].map(title_map)
    sdf['帖子类型'] = sdf['来源帖子编号'].map(pmap['帖子类型'])
    out = sdf[COLS].sort_values('信号编号')
    out.to_csv(out_path, index=False, encoding='utf-8-sig')
    print('signals:', len(out))
    print(out['置信度'].value_counts().to_string())
    print('source posts:', out['来源帖子编号'].nunique())
else:
    print('no signals yet')

if problems:
    print('CHECK PROBLEMS:')
    for p in problems:
        print('  ', p)
else:
    print('quote/like check: OK')
print('written:', out_path)
