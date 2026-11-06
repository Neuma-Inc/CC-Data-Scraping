# -*- coding: utf-8 -*-
import pandas as pd, re, os

POST = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\减重课程五平台数据\02_内容主表_全量帖子明细.csv'
WIDE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\评论上下文宽表.csv'
PILOT = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\40条试点_分型.csv'
OUTDIR = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标\400条抽样'
os.makedirs(OUTDIR, exist_ok=True)

post = pd.read_csv(POST, dtype={'平台内容ID': str})
wide = pd.read_csv(WIDE, dtype={'内容ID': str}, usecols=['内容ID','评论正文','评论点赞数'])
post['n'] = pd.to_numeric(post['本库已抓评论数'], errors='coerce').fillna(0)
post['t'] = post['内容标题'].fillna('')
post['b'] = post['正文/详情摘要'].fillna('')
post['all'] = post['t'] + ' ' + post['b']

pilot = pd.read_csv(PILOT, dtype={'内容ID': str})
pilot_ids = set(pilot['内容ID'].astype(str))

FP = ['我','本人','自己','姐妹','宝妈','产后','大学生','打工人','上班族','基数','身高','体重','斤']
HELP = ['怎么','怎么办','求','有没有','为什么','瘦不下来','反弹','卡住','不掉秤','平台期','建议','问','正常吗','可以吗','求助','焦虑','崩溃','急','难受']
EXP = ['瘦了','减了','记录','打卡','逆袭','复盘','心得','经历','成功','失败','坚持','第','天','个月']
SCI = ['今天','分享','教程','带你','跟我','收藏','动作','食谱','科普','测评','vlog','博主','减脂餐','跟练','原理','研究','医生','营养师','指南']
AD = ['训练营','陪跑','监督','私教','1v1','收费','价格','报名','咨询','微信','课程','名额','招生','服务','包瘦']
PRICE = re.compile(r'\d+\s*元|价格|收费|报名|咨询|微信|名额|招生|月付|一节课')

def cls(r):
    s = r['all']
    fp = any(w in s for w in FP)
    hp = any(w in s for w in HELP)
    ep = any(w in s for w in EXP) or bool(re.search(r'从.{1,12}到', s))
    sp = any(w in s for w in SCI)
    ad_score = sum(1 for w in AD if w in s)
    is_ad = ad_score >= 2 and bool(PRICE.search(s)) and not s.startswith('千万不要')
    if is_ad:
        return '广告/服务'
    if fp and hp:
        return '用户求助'
    if fp and ep:
        return '用户经历'
    if sp:
        return '博主科普'
    return '其他'

post['预设类型'] = post.apply(cls, axis=1)
post = post[post['平台'].isin(['小红书','抖音','知乎','B站'])].copy()
post = post[~post['平台内容ID'].astype(str).isin(pilot_ids)].copy()

# 每平台目标：40求助 / 30经历 / 20科普 / 10广告；不足则用最大类补齐
TARGET = {'用户求助':40, '用户经历':30, '博主科普':20, '广告/服务':10}

def pick(plat):
    pool = post[post['平台']==plat].copy()
    # 评论门槛：知乎允许0，其余至少1
    if plat != '知乎':
        pool = pool[pool['n']>=1]
    picked = []
    for typ, k in TARGET.items():
        sub = pool[pool['预设类型']==typ].sort_values('n', ascending=False)
        picked.append(sub.head(k))
    out = pd.concat(picked).drop_duplicates('平台内容ID')
    # 补齐到90
    if len(out) < 90:
        rest = pool[~pool['平台内容ID'].isin(out['平台内容ID'])].sort_values('n', ascending=False)
        out = pd.concat([out, rest.head(90-len(out))])
    out = out.head(90).copy()
    return out

for plat, code in [('小红书','XHS'),('抖音','DY'),('知乎','ZH'),('B站','BILI')]:
    out = pick(plat)
    rows = []
    for i, (_, r) in enumerate(out.iterrows(), 1):
        cid = str(r['平台内容ID'])
        cm = wide[wide['内容ID']==cid].copy()
        cm['赞'] = pd.to_numeric(cm['评论点赞数'], errors='coerce').fillna(0)
        cm = cm.sort_values('赞', ascending=False).head(10)
        top = []
        for _, c in cm.iterrows():
            txt = re.sub(r'\s+', ' ', str(c['评论正文']))[:180]
            top.append(f"[赞{int(c['赞'])}] {txt}")
        rows.append({
            '编号': f'{code}{i:03d}', '平台': plat, '搜索词': r['抓取搜索词'],
            '标题': str(r['内容标题'])[:120],
            '正文摘要': re.sub(r'\s+', ' ', str(r['正文/详情摘要']))[:800],
            '作者': r['作者昵称'], '点赞': r['点赞数'], '总评论': r['原帖总评论数'],
            '已抓评论': r['本库已抓评论数'], 'Top10评论': ' || '.join(top),
            '链接': r['原帖验证链接(URL)'], '内容ID': cid, '预设类型': r['预设类型'],
        })
    df = pd.DataFrame(rows)
    path = os.path.join(OUTDIR, f'400条_原始_{plat}.csv')
    df.to_csv(path, index=False, encoding='utf-8-sig')
    print('\n', plat, len(df), path)
    print(df['预设类型'].value_counts().to_string())
