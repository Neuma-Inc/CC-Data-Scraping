# -*- coding: utf-8 -*-
import json, os

base = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base, 'codes.jsonl')
patches = {
    'BILI009': {'触发事件': '很多人不知道怎么判断胰岛素抵抗（推断）'},
    'BILI027': {'触发事件': '有热量缺口却不掉秤的困惑（推断）'},
    'BILI030': {'触发事件': '168轻断食的争议（推断）'},
    'BILI048': {'触发事件': '脂肪肝患者不知道怎么护肝（推断）'},
    'BILI075': {'触发事件': '肥胖原因众说纷纭（推断）'},
    'BILI087': {'触发事件': '饮食与身体状态的关系（推断）'},
}
rows = []
changed = 0
for line in open(path, encoding='utf-8'):
    if not line.strip():
        continue
    r = json.loads(line)
    if r['编号'] in patches:
        r.update(patches[r['编号']])
        changed += 1
    rows.append(json.dumps(r, ensure_ascii=False))
with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(rows) + '\n')
print('patched', changed)
