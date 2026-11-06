# -*- coding: utf-8 -*-
import pandas as pd, os

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条编码\混合标注'
OUT = BASE

def split(name, n_a):
    p = os.path.join(BASE, f'混合标注_{name}.csv')
    d = pd.read_csv(p, dtype={'编号': str})
    a = d.iloc[:n_a].copy()
    b = d.iloc[n_a:].copy()
    pa = os.path.join(OUT, f'混合标注_{name}_A.csv')
    pb = os.path.join(OUT, f'混合标注_{name}_B.csv')
    a.to_csv(pa, index=False, encoding='utf-8-sig')
    b.to_csv(pb, index=False, encoding='utf-8-sig')
    print(name, len(d), '->', len(a), len(b))

split('小红书-评论', 35)
split('抖音-评论', 37)
