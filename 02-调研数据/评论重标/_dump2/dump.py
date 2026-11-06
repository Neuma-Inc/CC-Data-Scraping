# -*- coding: utf-8 -*-
import pandas as pd, os, re

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标'
code = pd.read_csv(os.path.join(BASE, r'400条编码\400条编码_知乎.csv'), encoding='utf-8-sig')
src = pd.read_csv(os.path.join(BASE, r'400条抽样\400条_原始_知乎.csv'), encoding='utf-8-sig')
sel = code[code['帖子类型'].isin(['博主科普', '广告服务', '其他'])][['编号', '帖子类型']]
m = sel.merge(src[['编号', '标题', 'Top10评论']], on='编号')

os.makedirs(os.path.join(BASE, '_dump2'), exist_ok=True)
blocks = []
for _, r in m.iterrows():
    s = ['### %s | %s | %s' % (r['编号'], r['帖子类型'], r['标题'])]
    parts = [p for p in str(r['Top10评论']).split(' || ') if p.strip()]
    for i, p in enumerate(parts, 1):
        mm = re.match(r'\[赞(\d+)\]\s*(.*)', p, re.S)
        like = mm.group(1) if mm else '?'
        txt = mm.group(2) if mm else p
        s.append('C%d [赞%s] %s' % (i, like, txt))
    blocks.append('\n'.join(s))

n = len(blocks)
per = (n + 2) // 3
for b in range(3):
    chunk = blocks[b * per:(b + 1) * per]
    path = os.path.join(BASE, '_dump2', 'cm_%d.txt' % b)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(chunk) + '\n')
    print('cm_%d' % b, len(chunk), 'posts', sum(len(x) for x in chunk), 'chars')
