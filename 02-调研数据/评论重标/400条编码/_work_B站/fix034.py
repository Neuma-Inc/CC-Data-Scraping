# -*- coding: utf-8 -*-
import json, os

base = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base, 'codes.jsonl')
lines = open(path, encoding='utf-8').read().splitlines()
out = []
fixed = 0
for line in lines:
    if not line.strip():
        continue
    r = json.loads(line)
    if r['编号'] == 'BILI034':
        r['代表原话'] = '"绝经"是一个点，是一个结果；但"围绝经期"是一段路，是一个窗口期。'
        fixed += 1
    out.append(json.dumps(r, ensure_ascii=False))
with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out) + '\n')
print('fixed', fixed, 'total', len(out))
