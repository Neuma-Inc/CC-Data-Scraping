# -*- coding: utf-8 -*-
import pandas as pd, os

p = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\40条试点_编码表.csv'
df = pd.read_csv(p, encoding='utf-8-sig')
out = []
for i, r in df.iterrows():
    out.append('-' * 90)
    for c in df.columns:
        out.append(f'{c}: {r[c]}')
dst = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条编码\_pilot_dump.txt'
open(dst, 'w', encoding='utf-8').write('\n'.join(out))
print('written', os.path.getsize(dst))
print(df['帖子类型'].value_counts())
print(df['卡点可编码性'].value_counts())
print(df['置信度'].value_counts())
