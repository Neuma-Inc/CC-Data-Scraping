# -*- coding: utf-8 -*-
import pandas as pd, os, glob

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标'
CODE = os.path.join(BASE, '400条编码')
BATCH = os.path.join(CODE, '混合标注')
OUT1 = os.path.join(CODE, '400条_混合标注_总表.csv')
OUT2 = os.path.join(CODE, '400帖覆盖表.csv')

files = [
    (os.path.join(CODE, '混合标注_B站-帖子_已标注.csv'), '帖子', 'B站-帖子'),
    (os.path.join(CODE, '混合标注_B站-评论_已标注.csv'), '评论', 'B站-评论'),
    (os.path.join(CODE, '混合标注_抖音-帖子_已标注.csv'), '帖子', '抖音-帖子'),
    (os.path.join(CODE, '混合标注_抖音-评论_A_已标注.csv'), '评论', '抖音-评论A'),
    (os.path.join(CODE, '混合标注_抖音-评论_B_已标注.csv'), '评论', '抖音-评论B'),
    (os.path.join(CODE, '混合标注_知乎-帖子_已标注.csv'), '帖子', '知乎-帖子'),
    (os.path.join(CODE, '混合标注_知乎-评论_已标注.csv'), '评论', '知乎-评论'),
    (os.path.join(CODE, '混合标注_小红书-评论_A_已标注.csv'), '评论', '小红书-评论A'),
    (os.path.join(CODE, '混合标注_小红书-评论_B_已标注.csv'), '评论', '小红书-评论B'),
    (os.path.join(BATCH, '混合标注_小红书-帖子_已标注.csv'), '帖子', '小红书-帖子'),
]

dfs = []
for path, unit, batch in files:
    d = pd.read_csv(path, dtype={'来源帖子编号': str})
    d['编码单位'] = unit
    d['批次'] = batch
    dfs.append(d)

df = pd.concat(dfs, ignore_index=True)
df['帖子类型'] = df['帖子类型'].replace({'广告服务': '广告/服务'})

post = pd.read_csv(os.path.join(CODE, '400条_帖子编码_总表.csv'), dtype={'编号': str})
rel = post.set_index('编号')['是否减重相关'].to_dict()
df['是否减重相关'] = df['来源帖子编号'].map(rel).fillna('待定')

order = {'小红书': 0, '抖音': 1, '知乎': 2, 'B站': 3}
df['_o'] = df['平台'].map(order)
df = df.sort_values(['_o', '编码单位', '来源帖子编号', '信号编号']).drop(columns='_o')
df.to_csv(OUT1, index=False, encoding='utf-8-sig')

print('saved', len(df), OUT1)
print('unique 信号编号', df['信号编号'].nunique())
print('\n平台×单位:')
print(df.groupby(['平台', '编码单位']).size().to_string())
print('\n置信度:')
print(df['置信度'].value_counts().to_string())
print('\n类型:')
print(df['帖子类型'].value_counts().to_string())

# 覆盖表
bases = [
    os.path.join(BATCH, '混合标注_小红书-帖子.csv'),
    os.path.join(BATCH, '混合标注_小红书-评论.csv'),
    os.path.join(BATCH, '混合标注_抖音-帖子.csv'),
    os.path.join(BATCH, '混合标注_抖音-评论.csv'),
    os.path.join(BATCH, '混合标注_知乎-帖子.csv'),
    os.path.join(BATCH, '混合标注_知乎-评论.csv'),
    os.path.join(BATCH, '混合标注_B站-帖子.csv'),
    os.path.join(BATCH, '混合标注_B站-评论.csv'),
]
unit_map = {}
for b in bases:
    d = pd.read_csv(b, dtype={'编号': str})
    for _, r in d.iterrows():
        unit_map[r['编号']] = r['编码单位']

counts = df.groupby('来源帖子编号').size()
conf = df.groupby('来源帖子编号')['置信度'].agg(lambda s: '高' if '高' in set(s) else ('中' if '中' in set(s) else '低'))
batch_map = df.groupby('来源帖子编号')['批次'].agg(lambda s: '/'.join(sorted(set(s))))

cov = post[['编号', '平台', '帖子类型', '是否减重相关']].copy()
cov['编码单位'] = cov['编号'].map(unit_map).fillna('未分配')
cov['信号数'] = cov['编号'].map(counts).fillna(0).astype(int)
cov['最高置信度'] = cov['编号'].map(conf).fillna('')
cov['标注批次'] = cov['编号'].map(batch_map).fillna('')

def status(r):
    if r['信号数'] > 0:
        return '是'
    if r['编码单位'] == '评论':
        return '无可用信号'
    if r['编码单位'] == '帖子':
        return '未覆盖'
    return '未分配'

cov['是否覆盖'] = cov.apply(status, axis=1)
cov.to_csv(OUT2, index=False, encoding='utf-8-sig')

print('\n覆盖表 saved', len(cov), OUT2)
print(cov['是否覆盖'].value_counts().to_string())
print('\n分平台覆盖:')
print(pd.crosstab(cov['平台'], cov['是否覆盖']).to_string())
print('\n分单位覆盖:')
print(pd.crosstab(cov['编码单位'], cov['是否覆盖']).to_string())
