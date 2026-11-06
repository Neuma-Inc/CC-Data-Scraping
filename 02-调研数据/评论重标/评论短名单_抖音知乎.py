# -*- coding: utf-8 -*-
import pandas as pd, os, re, math

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标'
POST = os.path.join(BASE, '400条编码', '400条_帖子编码_总表.csv')
post = pd.read_csv(POST, dtype={'编号': str}).set_index('编号')[['帖子类型']].to_dict('index')

COND = re.compile(r'产后|多囊|胰岛素|血糖|糖前|更年期|暴食|反弹|平台|司美|替尔|GLP|训练营|私教|减肥针|甲减|桥本|闭经|月经|吃药|打针|身高|体重|斤|岁|BMI|脂肪肝|血压|糖化')
FIRST = re.compile(r'我|本人|我是|自己|姐妹|宝妈')
Q = re.compile(r'[?？]|怎么|能不能|可以吗|多少|吃什么|有没有|建议|正常吗')
PAIN = re.compile(r'愁|崩溃|难受|急|焦虑|失败|不掉|瘦不下来|胖|副作用|恶心|头晕|便秘|失眠|害怕|反弹|暴食')
BAD = re.compile(r'博主|视频|这期|老师|教授|UP|收藏|打卡|哈哈|笑死|老公|婚姻|孩子|离婚|彩礼|沙发|第一')

def shortlist(plat, code):
    src = pd.read_csv(os.path.join(BASE, '400条抽样', f'400条_原始_{plat}.csv'), dtype={'编号': str})
    rows = []
    seen = set()
    for _, r in src.iterrows():
        raw = str(r.get('Top10评论',''))
        if not raw or raw == 'nan':
            continue
        for m in re.finditer(r'\[赞(\d+)\]\s*([^|]+)', raw):
            likes = int(m.group(1))
            text = re.sub(r'\s+', ' ', m.group(2)).strip()
            if len(text) < 10 or len(text) > 220:
                continue
            if text in seen:
                continue
            if BAD.search(text):
                continue
            cond = bool(COND.search(text))
            first = bool(FIRST.search(text))
            q = bool(Q.search(text))
            pain = bool(PAIN.search(text))
            if not ((cond and (first or q)) or (q and pain)):
                continue
            score = (2 if cond else 0) + (2 if first else 0) + (2 if q else 0) + (1 if pain else 0) + math.log1p(likes)/3
            seen.add(text)
            rows.append({
                '编号': f'{code}-C{len(rows)+1:03d}',
                '平台': plat,
                '来源帖子编号': r['编号'],
                '来源帖子标题': str(r.get('标题',''))[:80],
                '帖子类型': post.get(r['编号'],{}).get('帖子类型',''),
                '评论原文': text,
                '评论赞': likes,
                '得分': round(score,1),
            })
    df = pd.DataFrame(rows).sort_values(['得分','评论赞'], ascending=False).head(40)
    path = os.path.join(BASE, '400条编码', f'评论短名单_{plat}.csv')
    df.to_csv(path, index=False, encoding='utf-8-sig')
    print('\n====', plat, len(df), path)
    for _, x in df.head(20).iterrows():
        print(f"{x['评论赞']:>5} | {x['来源帖子标题'][:28]} | {x['评论原文'][:95]}")
    return df

shortlist('抖音','DY')
shortlist('知乎','ZH')
