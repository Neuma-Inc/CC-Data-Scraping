# -*- coding: utf-8 -*-
import csv, os, sys, importlib
import pandas as pd

SRC = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条抽样\400条_原始_小红书.csv'
OUT = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条编码\400条编码_小红书.csv'
TMP = OUT + '.tmp'

COLS = ['编号','平台','搜索词','帖子类型','卡点可编码性','谁在说','触发事件','目标',
        '试过什么','卡在哪','具体问的问题（原话）','代表原话','点赞','总评论','已抓评论',
        '链接','置信度','备注']
TYPES = {'用户求助','用户经历','博主科普','广告服务','用户吐槽','用户观点','其他'}
ENC = {'是','部分（回顾性）','部分（观点）','否'}
CONF = {'高','中','低'}

src = pd.read_csv(SRC, encoding='utf-8-sig')
src['编号'] = src['编号'].astype(str).str.strip()
by_id = {r['编号']: r for _, r in src.iterrows()}
print('源文件行数:', len(src), '唯一编号:', len(by_id))

modules = ['_encode_part1', '_encode_part1b', '_encode_part2', '_encode_part3', '_encode_part4', '_encode_part5']
rows = []
for m in modules:
    mod = importlib.import_module(m)
    rows.extend(mod.BATCHES[0])
print('编码行数:', len(rows))

# ---- 完整性检查 ----
ids = [r['id'] for r in rows]
assert len(ids) == len(set(ids)), '编号重复: ' + str([x for x in ids if ids.count(x) > 1])
missing = [i for i in sorted(by_id) if i not in set(ids)]
extra = [i for i in ids if i not in by_id]
assert not missing, '缺行: ' + str(missing)
assert not extra, '多余编号: ' + str(extra)

def haystack(rec):
    return '\n'.join(str(rec[c]) for c in ['标题','正文摘要','Top10评论'])

# ---- 逐条校验 ----
problems = []
for r in rows:
    rec = by_id[r['id']]
    hs = haystack(rec)
    if r['typ'] not in TYPES: problems.append((r['id'], '类型非法', r['typ']))
    if r['enc'] not in ENC: problems.append((r['id'], '可编码性非法', r['enc']))
    if r['conf'] not in CONF: problems.append((r['id'], '置信度非法', r['conf']))
    for k in ['who','trig','goal','tried','stuck','q','quote','note']:
        if not str(r[k]).strip(): problems.append((r['id'], '空字段', k))
    if r['quote'] not in hs:
        problems.append((r['id'], '代表原话不在原文', r['quote']))
    if not r['q'].startswith('无（') and r['q'] not in hs:
        problems.append((r['id'], '问题不在原文', r['q']))

if problems:
    print('校验失败 %d 条:' % len(problems))
    for p in problems:
        print('  ', p[0], p[1], '|', repr(p[2])[:160])
    sys.exit(1)
print('校验通过: 90 行原话/问题均可在原文中逐字找到')

# ---- 分批追加写盘，每 25 条落盘 ----
if os.path.exists(TMP):
    os.remove(TMP)
written = 0
with open(TMP, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(COLS)
    for bi, m in enumerate(modules, 1):
        mod = importlib.import_module(m)
        batch = mod.BATCHES[0]
        for r in batch:
            rec = by_id[r['id']]
            w.writerow([r['id'], '小红书', rec['搜索词'], r['typ'], r['enc'], r['who'],
                        r['trig'], r['goal'], r['tried'], r['stuck'], r['q'], r['quote'],
                        rec['点赞'], rec['总评论'], rec['已抓评论'], rec['链接'],
                        r['conf'], r['note']])
            written += 1
        f.flush()
        print('  批次%d (%s-%s) 完成，累计 %d 行' % (bi, batch[0]['id'], batch[-1]['id'], written))
        if written % 25 < len(batch):
            print('  [落盘检查点] %d 行' % written)

os.replace(TMP, OUT)
print('已写入:', OUT, os.path.getsize(OUT), 'bytes')

# ---- 分布 ----
out = pd.read_csv(OUT, encoding='utf-8-sig')
print('\n行数:', len(out), '列数:', len(out.columns))
print('\n帖子类型:')
print(out['帖子类型'].value_counts().to_string())
print('\n卡点可编码性:')
print(out['卡点可编码性'].value_counts().to_string())
print('\n置信度:')
print(out['置信度'].value_counts().to_string())
print('\n空值:', int(out.isna().sum().sum()))
