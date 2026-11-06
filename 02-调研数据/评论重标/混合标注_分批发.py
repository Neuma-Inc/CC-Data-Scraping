# -*- coding: utf-8 -*-
import pandas as pd, os

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标'
OUT = os.path.join(BASE, '400条编码', '混合标注')
os.makedirs(OUT, exist_ok=True)

post = pd.read_csv(os.path.join(BASE, '400条编码', '400条_帖子编码_总表.csv'), dtype={'编号': str})

srcs = []
for plat in ['小红书', '抖音', '知乎', 'B站']:
    s = pd.read_csv(os.path.join(BASE, '400条抽样', f'400条_原始_{plat}.csv'), dtype={'编号': str})
    srcs.append(s[['编号', '标题', '正文摘要', 'Top10评论']])
pilot = pd.read_csv(os.path.join(BASE, '40条试点_分型.csv'), dtype={'编号': str})
srcs.append(pilot[['编号', '标题', '正文摘要', 'Top10评论']])
src = pd.concat(srcs, ignore_index=True).drop_duplicates('编号')

df = post.merge(src, on='编号', how='left')

def unit(r):
    if r['帖子类型'] in ['用户求助', '用户经历']:
        return '帖子'
    return '评论'

df['编码单位'] = df.apply(unit, axis=1)
df['批次'] = df['平台'] + '-' + df['编码单位']

cols = ['编号', '平台', '搜索词', '标题', '正文摘要', '帖子类型', '点赞',
        '总评论', '已抓评论', 'Top10评论', '链接', '编码单位']

for batch, sub in df.groupby('批次'):
    d = sub[cols].copy()
    path = os.path.join(OUT, f'混合标注_{batch}.csv')
    d.to_csv(path, index=False, encoding='utf-8-sig')
    print(batch, len(d), path)

print('\n汇总:')
print(df.groupby(['平台', '编码单位']).size().to_string())
print('\n总帖子', len(df))
