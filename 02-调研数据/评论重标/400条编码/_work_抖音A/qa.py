# -*- coding: utf-8 -*-
"""交付前校验：原话逐字、赞数、每帖<=3、编号连续、字段完整、无重复评论。"""
import pandas as pd
import re
import sys

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条编码'
SRC = BASE + r'\混合标注\混合标注_抖音-评论_A.csv'
DST = BASE + r'\混合标注_抖音-评论_A_已标注.csv'

src = pd.read_csv(SRC, dtype=str).fillna('')
out = pd.read_csv(DST, dtype=str).fillna('')

print('源帖数=%d  信号数=%d  列数=%d' % (len(src), len(out), len(out.columns)))
print('列名:', out.columns.tolist())

# 1. 15列与顺序
EXPECT = ['信号编号', '平台', '来源帖子编号', '来源帖子标题', '帖子类型', '谁在说',
          '触发事件', '目标', '试过什么', '卡在哪', '具体问题（原话）', '代表原话',
          '评论赞', '置信度', '备注']
assert out.columns.tolist() == EXPECT, '列不一致'

# 2. 编号连续
ids = out['信号编号'].tolist()
assert ids == ['DY-CA%02d' % i for i in range(1, len(out) + 1)], '编号不连续'
print('编号: %s ... %s' % (ids[0], ids[-1]))

# 3. 原话逐字 + 赞数 + 每帖<=3 + 不重复取同一评论
posts = {}
for _, r in src.iterrows():
    cs = [c.strip() for c in r['Top10评论'].split('||') if c.strip()]
    parsed = []
    for c in cs:
        m = re.match(r'^\[赞(\d+)\]\s*(.*)$', c)
        parsed.append((int(m.group(1)), m.group(2).strip()) if m else (0, c))
    posts[r['编号']] = (r, parsed)

used = set()
errs = []
for _, r in out.iterrows():
    pid, like, text = r['来源帖子编号'], int(r['评论赞']), r['代表原话']
    if pid not in posts:
        errs.append('未知帖子 %s' % pid); continue
    srow, cs = posts[pid]
    matches = [(i, l, t) for i, (l, t) in enumerate(cs, 1) if t == text and l == like]
    if not matches:
        errs.append('%s 原话/赞数不匹配: %r [赞%s]' % (r['信号编号'], text[:40], r['评论赞']))
    else:
        used.add((pid, matches[0][0]))
    if r['来源帖子标题'] != srow['标题']:
        errs.append('%s 标题不一致' % r['信号编号'])
    if r['帖子类型'] != srow['帖子类型']:
        errs.append('%s 帖子类型不一致' % r['信号编号'])
    if r['平台'] != '抖音':
        errs.append('%s 平台错误' % r['信号编号'])
    q = r['具体问题（原话）']
    if q != '无（非提问）' and q not in text:
        errs.append('%s 问题非原话: %s' % (r['信号编号'], q))
    if r['置信度'] not in ('高', '中', '低'):
        errs.append('%s 置信度异常' % r['信号编号'])
    for col in EXPECT:
        if str(r[col]).strip() == '':
            errs.append('%s 空字段 %s' % (r['信号编号'], col))

cnt = out['来源帖子编号'].value_counts()
over = cnt[cnt > 3]
if len(over):
    errs.append('超3条: %s' % over.to_dict())

# 4. 每个来源帖只覆盖一次、且信号数=不同评论数
dup = out.duplicated(subset=['来源帖子编号', '代表原话']).sum()
if dup:
    errs.append('重复评论 %d 条' % dup)

print('每帖≤3:', 'OK' if not len(over) else 'FAIL')
print('原话逐字+赞数:', 'OK' if not errs else 'FAIL')
print('置信度分布:', out['置信度'].value_counts().to_dict())
print('来源帖数:', out['来源帖子编号'].nunique())
print('未产出信号帖:', sorted(set(src['编号']) - set(out['来源帖子编号'])))
if errs:
    print('--- 问题明细 ---')
    for e in errs[:30]:
        print(e)
    sys.exit(1)
print('ALL CHECKS PASSED')
