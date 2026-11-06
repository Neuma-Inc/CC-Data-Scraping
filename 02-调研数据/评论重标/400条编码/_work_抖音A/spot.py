# -*- coding: utf-8 -*-
import pandas as pd

P = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条编码\混合标注_抖音-评论_A_已标注.csv'
d = pd.read_csv(P, dtype=str).fillna('')
print('帖子类型:', d['帖子类型'].unique().tolist())
print('总行数:', len(d))
for i in (17, 93, 96):
    r = d.iloc[i]
    print('-' * 70)
    for k in d.columns:
        print(k, ':', r[k])
