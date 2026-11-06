# -*- coding: utf-8 -*-
import json, os

base = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base, 'signals.jsonl')
fix = {
    'BILI029-S2': {'谁在说': '尝试168断食者（性别未说明）'},
    'BILI029-S3': {'谁在说': '询问碳循环是否适合女性的网友（身份未说明）'},
}
rows, n = [], 0
for line in open(path, encoding='utf-8'):
    if not line.strip():
        continue
    r = json.loads(line)
    if r['信号编号'] in fix:
        r.update(fix[r['信号编号']])
        n += 1
    rows.append(json.dumps(r, ensure_ascii=False))
with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(rows) + '\n')
print('fixed', n, 'total', len(rows))
