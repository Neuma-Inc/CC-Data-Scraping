# -*- coding: utf-8 -*-
import pandas as pd, os

p = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条抽样\400条_原始_小红书.csv'
df = pd.read_csv(p, encoding='utf-8-sig')
out = []
for i, r in df.iterrows():
    out.append('=' * 100)
    out.append(f"[{r['编号']}] 预设={r['预设类型']} | 搜索词={r['搜索词']} | 赞={r['点赞']} 总评={r['总评论']} 抓取={r['已抓评论']}")
    out.append('标题: ' + str(r['标题']))
    out.append('正文: ' + str(r['正文摘要']))
    out.append('作者: ' + str(r['作者']))
    out.append('Top10评论: ' + str(r['Top10评论']))
dst = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条编码\_xhs_dump.txt'
open(dst, 'w', encoding='utf-8').write('\n'.join(out))
print('written', dst, 'chars', os.path.getsize(dst))
