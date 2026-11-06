# -*- coding: utf-8 -*-
"""探测微博联想接口的多个历史路径。"""
import json
import re
import time

import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})
fp = json.dumps({"os": "1", "browser": "Chrome131", "fonts": "undefined",
                 "screenInfo": "1920*1080*24", "plugins": ""}, ensure_ascii=False)
r = s.post("https://passport.weibo.com/visitor/genvisitor",
           data={"cb": "gen_callback", "fp": fp}, timeout=20)
tid = re.search(r'"tid":"(.*?)"', r.text).group(1)
s.get("https://passport.weibo.com/visitor/visitor", params={
    "a": "incarnate", "t": tid, "w": "2", "c": "095",
    "gc": "", "cb": "cross_domain", "from": "weibo", "_)": "1"}, timeout=20)
print("cookies", list(s.cookies.keys()))
time.sleep(3)

urls = [
    ("https://s.weibo.com/ajax/jsonp/suggestion", {"key": "失眠", "_": str(int(time.time() * 1000))}),
    ("https://s.weibo.com/suggest/suggrequest.php", {"key": "失眠", "json": "1", "count": "10"}),
    ("https://weibo.com/ajax/search/suggest", {"q": "失眠"}),
    ("https://s.weibo.com/ajax/searchsuggest", {"key": "失眠"}),
]
for url, params in urls:
    try:
        r3 = s.get(url, params=params, timeout=20,
                   headers={"Referer": "https://s.weibo.com/"})
        body = r3.text.replace("\n", " ")
        print("\n==", url, r3.status_code, r3.headers.get("content-type"))
        print(body[:500])
    except Exception as e:
        print(url, "ERR", e)
    time.sleep(4)
