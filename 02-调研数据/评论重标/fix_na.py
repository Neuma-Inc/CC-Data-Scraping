# -*- coding: utf-8 -*-
p = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\40条试点_编码表.py'
s = open(p, encoding='utf-8').read()
n = s.count("'N/A'")
s = s.replace("'N/A'", "'不适用'")
open(p, 'w', encoding='utf-8').write(s)
print('replaced', n)
