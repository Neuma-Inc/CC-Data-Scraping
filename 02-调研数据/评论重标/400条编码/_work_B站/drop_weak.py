# -*- coding: utf-8 -*-
import json, os

base = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base, 'signals.jsonl')
drop = {'BILI013-S3', 'BILI015-S2', 'BILI028-S2', 'BILI037-S2', 'BILI039-S1',
        'BILI039-S3', 'BILI041-S2', 'BILI043-S1', 'BILI049-S1', 'BILI008-S2',
        'BILI004-S2', 'BILI025-S3'}
rows = []
for line in open(path, encoding='utf-8'):
    if not line.strip():
        continue
    r = json.loads(line)
    if r['信号编号'] not in drop:
        rows.append(json.dumps(r, ensure_ascii=False))
with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(rows) + '\n')
print('kept', len(rows), 'dropped', len(drop))
