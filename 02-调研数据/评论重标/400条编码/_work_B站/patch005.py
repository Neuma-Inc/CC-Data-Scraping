# -*- coding: utf-8 -*-
import json, os

base = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base, 'codes.jsonl')
rows = []
for line in open(path, encoding='utf-8'):
    if not line.strip():
        continue
    r = json.loads(line)
    if r['编号'] == 'BILI005':
        r['备注'] = '观点/劝退帖；正文缺失（仅标题）；预设类型误判；评论多为反驳及用药者经历'
    rows.append(json.dumps(r, ensure_ascii=False))
with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(rows) + '\n')
print('ok', len(rows))
