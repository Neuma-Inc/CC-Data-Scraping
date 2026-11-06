# -*- coding: utf-8 -*-
import json, os

base = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base, 'codes.jsonl')
# These rows already had 用户经历 as preset and were coded 用户经历 -> not a misjudgment.
same_type = {'BILI044', 'BILI046', 'BILI047', 'BILI050', 'BILI055',
             'BILI056', 'BILI060', 'BILI063', 'BILI065', 'BILI068'}
rows = []
changed = 0
for line in open(path, encoding='utf-8'):
    if not line.strip():
        continue
    r = json.loads(line)
    if r['编号'] in same_type and '预设类型误判' in r['备注']:
        r['备注'] = r['备注'].replace('预设类型误判', '预设类型一致')
        changed += 1
    if r['编号'] == 'BILI071':
        r['备注'] = r['备注'].replace('预设类型为博主科普', '预设类型一致')
        changed += 1
    rows.append(json.dumps(r, ensure_ascii=False))
with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(rows) + '\n')
print('fixed notes', changed)
