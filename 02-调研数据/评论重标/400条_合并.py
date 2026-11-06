# -*- coding: utf-8 -*-
import pandas as pd, os, re

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标'
OUT = os.path.join(BASE, '400条编码', '400条_帖子编码_总表.csv')

files = [
    ('小红书', os.path.join(BASE, '400条编码', '400条编码_小红书.csv'), '400抽样-小红书'),
    ('抖音',   os.path.join(BASE, '400条编码', '400条编码_抖音.csv'),   '400抽样-抖音'),
    ('知乎',   os.path.join(BASE, '400条编码', '400条编码_知乎.csv'),   '400抽样-知乎'),
    ('B站',    os.path.join(BASE, '400条编码', '400条编码_B站.csv'),    '400抽样-B站'),
    ('试点',   os.path.join(BASE, '40条试点_编码表.csv'),               '试点40'),
]

dfs = []
for name, path, source in files:
    d = pd.read_csv(path)
    d['样本来源'] = source
    dfs.append(d)

df = pd.concat(dfs, ignore_index=True)
df['帖子类型'] = df['帖子类型'].replace({'广告服务': '广告/服务'})
df['卡点可编码性'] = df['卡点可编码性'].replace({'部分': '部分（回顾性）'})

def rel(r):
    s = str(r.get('备注','')) + ' ' + str(r.get('搜索词',''))
    if re.search(r'非减重|婚姻|更年期|营养师|考证|血糖仪|小说|失眠|肠脑轴|菜谱|新闻|情感', s):
        return '否'
    if r['帖子类型'] == '广告/服务':
        return '待定'
    return '是'

df['是否减重相关'] = df.apply(rel, axis=1)

order = {'小红书': 0, '抖音': 1, '知乎': 2, 'B站': 3}
df['_o'] = df['平台'].map(order)
df = df.sort_values(['_o', '编号']).drop(columns='_o')
df.to_csv(OUT, index=False, encoding='utf-8-sig')

print('saved', len(df), OUT)
print('unique 编号', df['编号'].nunique())
print('\n类型分布:')
print(df['帖子类型'].value_counts().to_string())
print('\n置信度:')
print(df['置信度'].value_counts().to_string())
print('\n是否减重相关:')
print(df['是否减重相关'].value_counts().to_string())
print('\n分平台类型:')
print(pd.crosstab(df['平台'], df['帖子类型']).to_string())
