import csv
from collections import Counter
p="v3_P1_分平台词表.csv"
rows=list(csv.DictReader(open(p,encoding="utf-8-sig")))
print("rows",len(rows), "cols", list(rows[0].keys()))
print("target values", Counter(r["目标篇数"] for r in rows))
print("platforms", Counter(r["平台参数"] for r in rows))
print("priority", Counter(r["优先级"] for r in rows))
for r in rows[:3]: print(r)
