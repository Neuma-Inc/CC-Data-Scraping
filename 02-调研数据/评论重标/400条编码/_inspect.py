# -*- coding: utf-8 -*-
import pandas as pd
p = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条编码\400条编码_小红书.csv'
df = pd.read_csv(p, encoding='utf-8-sig')
print(df.shape, list(df.columns))
print('\n--- 前3行 ---')
for i in range(3):
    print('=' * 80)
    for c in df.columns:
        print(f'{c}: {df.iloc[i][c]}')
print('\n--- 求助帖 ---')
print(df[df['帖子类型'] == '用户求助'][['编号','搜索词','卡点可编码性','谁在说','具体问的问题（原话）','置信度']].to_string())
print('\n--- 低置信度 ---')
print(df[df['置信度'] == '低'][['编号','帖子类型','搜索词','备注']].to_string())
print('\n--- 字段长度极值 ---')
for c in ['谁在说','触发事件','目标','试过什么','卡在哪','代表原话','备注']:
    print(c, 'max', df[c].astype(str).str.len().max(), '| min', df[c].astype(str).str.len().min())
print('\n链接示例:', df['链接'].iloc[0][:90])
print('编号首尾:', df['编号'].iloc[0], df['编号'].iloc[-1])
