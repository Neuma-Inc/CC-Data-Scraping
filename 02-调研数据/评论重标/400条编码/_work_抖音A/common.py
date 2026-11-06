# -*- coding: utf-8 -*-
"""混合标注·抖音-评论A 公共构建脚本。

- 代表原话 / 评论赞 一律从源 CSV 的 Top10评论 自动提取，保证一字不改。
- 具体问题若不是“无（非提问）”，强制校验为其代表原话的子串。
- 每批 add() 后调用 build()，增量落盘最终交付 CSV。
"""
import os
import re
import json
import pandas as pd

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条编码'
SRC = os.path.join(BASE, '混合标注', '混合标注_抖音-评论_A.csv')
WORK = os.path.join(BASE, '_work_抖音A')
JSONL = os.path.join(WORK, 'signals.jsonl')
DST = os.path.join(BASE, '混合标注_抖音-评论_A_已标注.csv')

COLS = ['信号编号', '平台', '来源帖子编号', '来源帖子标题', '帖子类型', '谁在说',
        '触发事件', '目标', '试过什么', '卡在哪', '具体问题（原话）', '代表原话',
        '评论赞', '置信度', '备注']

os.makedirs(WORK, exist_ok=True)


def load_posts():
    df = pd.read_csv(SRC, dtype=str).fillna('')
    posts, order = {}, []
    for _, r in df.iterrows():
        pid = r['编号']
        order.append(pid)
        cs = [c.strip() for c in r['Top10评论'].split('||') if c.strip()]
        parsed = []
        for c in cs:
            m = re.match(r'^\[赞(\d+)\]\s*(.*)$', c)
            parsed.append((int(m.group(1)), m.group(2).strip()) if m else (0, c))
        posts[pid] = {'row': r, 'comments': parsed}
    return posts, order


POSTS, ORDER = load_posts()


def add(pid, ci, who, trigger, goal, tried, block, q, conf, note):
    assert pid in POSTS, '未知帖子编号 %s' % pid
    likes, text = POSTS[pid]['comments'][ci - 1]
    if q != '无（非提问）':
        assert q in text, '问题原话不匹配 %s#%d:\n  q=%r\n  text=%r' % (pid, ci, q, text)
    assert conf in ('高', '中', '低'), conf
    rec = dict(pid=pid, ci=ci, who=who, trigger=trigger, goal=goal, tried=tried,
               block=block, q=q, text=text, likes=likes, conf=conf, note=note)
    with open(JSONL, 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def build(verbose=True):
    recs = {}
    if os.path.exists(JSONL):
        with open(JSONL, encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                recs[(r['pid'], r['ci'])] = r
    ordered = sorted(recs.values(), key=lambda r: (ORDER.index(r['pid']), r['ci']))
    rows = []
    for i, r in enumerate(ordered, 1):
        p = POSTS[r['pid']]['row']
        rows.append({
            '信号编号': 'DY-CA%02d' % i,
            '平台': '抖音',
            '来源帖子编号': r['pid'],
            '来源帖子标题': p['标题'],
            '帖子类型': p['帖子类型'],
            '谁在说': r['who'],
            '触发事件': r['trigger'],
            '目标': r['goal'],
            '试过什么': r['tried'],
            '卡在哪': r['block'],
            '具体问题（原话）': r['q'],
            '代表原话': r['text'],
            '评论赞': r['likes'],
            '置信度': r['conf'],
            '备注': r['note'],
        })
    out = pd.DataFrame(rows, columns=COLS)
    out.to_csv(DST, index=False, encoding='utf-8-sig')
    if verbose:
        covered = sorted({r['pid'] for r in ordered}, key=ORDER.index)
        conf = out['置信度'].value_counts().to_dict() if len(out) else {}
        skipped = [p for p in ORDER if p not in covered]
        print('rows=%d posts=%d/%d conf=%s' % (len(out), len(covered), len(ORDER), conf))
        print('skipped=%s' % (','.join(skipped) if skipped else '无'))
        print('->', DST)
    return out
