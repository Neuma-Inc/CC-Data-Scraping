# -*- coding: utf-8 -*-
import pandas as pd, re, os

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, '..', '..', '400条抽样', '400条_原始_B站.csv')
df = pd.read_csv(src, encoding='utf-8-sig')


def clean(s):
    s = str(s)
    s = re.sub(r'\[赞\d+\]\s*', '', s)
    return s


for b in range(9):
    chunk = df.iloc[b * 10:(b + 1) * 10]
    lines = []
    for _, r in chunk.iterrows():
        lines.append('=' * 80)
        lines.append('编号: {} | 搜索词: {} | 预设类型: {} | 点赞: {} | 总评论: {} | 已抓评论: {}'.format(
            r['编号'], r['搜索词'], r['预设类型'], r['点赞'], r['总评论'], r['已抓评论']))
        lines.append('标题: {}'.format(r['标题']))
        lines.append('作者: {}'.format(r['作者']))
        lines.append('--- 正文摘要 ---')
        lines.append(clean(r['正文摘要']))
        lines.append('--- Top10评论 ---')
        lines.append(clean(r['Top10评论']))
        lines.append('')
    with open(os.path.join(base, 'batch{}.txt'.format(b + 1)), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

print('done', df.shape)
print(df[['编号', '搜索词', '预设类型']].to_string(max_colwidth=40))
