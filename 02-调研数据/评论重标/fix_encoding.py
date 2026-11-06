# -*- coding: utf-8 -*-
p = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\40条试点_编码表.py'
s = open(p, encoding='utf-8').read()
old = """raw = pd.read_csv(RAW)
typ = pd.read_csv(TYPE)[['编号','帖子类型','卡点可编码性']]
df = raw.merge(typ, on='编号', how='left')"""
new = """df = pd.read_csv(TYPE)"""
assert old in s, 'pattern not found'
s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s)
print('patched')
