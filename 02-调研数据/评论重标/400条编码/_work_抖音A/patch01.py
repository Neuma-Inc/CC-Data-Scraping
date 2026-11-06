# -*- coding: utf-8 -*-
"""定点修订：DY048 第5条换成第一人称目标偏差；DY046 第4条训练描述改为原文口径。"""
import json
import os
import sys

sys.path.insert(0, r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条编码\_work_抖音A')
import common
from common import add, build

DROP = {('DY048', 5), ('DY046', 4)}
keep = []
with open(common.JSONL, encoding='utf-8') as f:
    for line in f:
        if not line.strip():
            continue
        r = json.loads(line)
        if (r['pid'], r['ci']) in DROP:
            continue
        keep.append(r)
with open(common.JSONL, 'w', encoding='utf-8') as f:
    for r in keep:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')

add('DY046', 4,
    '胰岛素抵抗者（自述）',
    '爬坡3个月，体重不变、围度只小1cm',
    '减重、减围度', '爬坡3个月（原文：30-1小时、速度4坡度12）、一天一顿饭',
    '体重没变化，围度几乎没变',
    '怎么办', '高', '胰岛素抵抗/平台')

add('DY048', 6,
    '减重者（自述，现105斤）',
    '看减肥后维持体重视频',
    '减到100斤', '未说明',
    '原以为还差5斤，现在看还差10斤',
    '无（非提问）', '中', '目标与现状偏差/短')

build()
