# -*- coding: utf-8 -*-
"""快速探测：微博 visitor cookie 流程 + 联想接口是否可用。只读探测，不入库。"""
import json
import re
import time

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})

fp = json.dumps({
    "os": "1", "browser": "Chrome131", "fonts": "undefined",
    "screenInfo": "1920*1080*24", "plugins": "",
}, ensure_ascii=False)

r = s.post("https://passport.weibo.com/visitor/genvisitor",
           data={"cb": "gen_callback", "fp": fp}, timeout=20)
print("genvisitor", r.status_code, r.text[:300])
m = re.search(r'"tid":"(.*?)"', r.text)
if m:
    tid = m.group(1)
    r2 = s.get("https://passport.weibo.com/visitor/visitor", params={
        "a": "incarnate", "t": tid, "w": "2", "c": "095",
        "gc": "", "cb": "cross_domain", "from": "weibo", "_)": "1",
    }, timeout=20)
    print("incarnate", r2.status_code, list(s.cookies.keys()))
    time.sleep(3)
    for url in ["https://weibo.com/ajax/side/searchsuggest",
                "https://s.weibo.com/ajax/searchsuggest"]:
        r3 = s.get(url, params={"q": "失眠"}, timeout=20,
                   headers={"Referer": "https://weibo.com/"})
        print(url, r3.status_code, r3.text[:400].replace("\n", " "))
        time.sleep(3)
