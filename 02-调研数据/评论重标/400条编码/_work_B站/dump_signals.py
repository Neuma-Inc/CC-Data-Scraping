# -*- coding: utf-8 -*-
"""Dump Top10 comments with like counts for posts needing comment-signal coding."""
import pandas as pd, re, os, json

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, '..', '..', '400条抽样', '400条_原始_B站.csv')
out_csv = os.path.join(base, '..', '400条编码_B站.csv')

src_df = pd.read_csv(src, encoding='utf-8-sig')
post = pd.read_csv(out_csv, encoding='utf-8-sig')
target = post[post['帖子类型'].isin(['博主科普', '广告服务', '其他'])]['编号'].tolist()
src_df = src_df[src_df['编号'].isin(target)].copy()

print('target posts:', len(src_df))


def parse_comments(raw):
    parts = [p.strip() for p in str(raw).split('||')]
    out = []
    for p in parts:
        m = re.match(r'^\[赞(\d+)\]\s*(.*)$', p, re.S)
        if m:
            out.append((int(m.group(1)), m.group(2).strip()))
        elif p:
            out.append((0, p))
    return out


all_data = {}
for _, r in src_df.iterrows():
    all_data[r['编号']] = {
        'title': str(r['标题']),
        'type': post.loc[post['编号'] == r['编号'], '帖子类型'].iloc[0],
        'comments': parse_comments(r['Top10评论']),
    }

with open(os.path.join(base, 'comments_parsed.json'), 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=1)

# dump in chunks of 10
ids = list(all_data.keys())
for c in range(0, len(ids), 10):
    lines = []
    for pid in ids[c:c + 10]:
        d = all_data[pid]
        lines.append('=' * 90)
        lines.append('{} | {} | {}'.format(pid, d['type'], d['title']))
        for i, (likes, text) in enumerate(d['comments'], 1):
            text = re.sub(r'\s+', ' ', text)
            lines.append('[{}] 赞{}: {}'.format(i, likes, text))
    with open(os.path.join(base, 'sig_chunk{}.txt'.format(c // 10 + 1)), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
print('chunks:', (len(ids) + 9) // 10)
