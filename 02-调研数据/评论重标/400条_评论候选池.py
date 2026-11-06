# -*- coding: utf-8 -*-
import pandas as pd, os, re

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标'
POST = os.path.join(BASE, '400条编码', '400条_帖子编码_总表.csv')
OUT = os.path.join(BASE, '400条编码', '400条_评论需求_候选池.csv')

sources = [
    ('小红书', os.path.join(BASE, '400条抽样', '400条_原始_小红书.csv')),
    ('抖音',   os.path.join(BASE, '400条抽样', '400条_原始_抖音.csv')),
    ('知乎',   os.path.join(BASE, '400条抽样', '400条_原始_知乎.csv')),
    ('B站',    os.path.join(BASE, '400条抽样', '400条_原始_B站.csv')),
    ('试点',   os.path.join(BASE, '40条试点_分型.csv')),
]

post = pd.read_csv(POST, dtype={'编号': str})
post_map = post.set_index('编号')[['帖子类型','是否减重相关']].to_dict('index')

rows = []
for plat, path in sources:
    d = pd.read_csv(path, dtype={'编号': str})
    for _, r in d.iterrows():
        raw = str(r.get('Top10评论',''))
        if not raw or raw == 'nan':
            continue
        for m in re.finditer(r'\[赞(\d+)\]\s*([^|]+)', raw):
            likes = int(m.group(1))
            text = re.sub(r'\s+', ' ', m.group(2)).strip()
            if len(text) < 8 or len(text) > 220:
                continue
            # 排除纯加油/纯情绪/纯广告
            if re.match(r'^(加油|厉害|牛逼|收藏|哈哈|支持|优秀|真棒|羡慕|打卡|来了|第一|沙发|姐姐加油|姐妹加油)', text):
                continue
            is_q = bool(re.search(r'[?？]|怎么|能不能|可以吗|为什么|怎么办|多少|求|有没有|正常吗|建议|吃什么|喝多少', text))
            is_ad = bool(re.search(r'加V|加微|微信|私我|链接|店铺|下单|购买|代理|招商|报名|咨询|课程|训练营|私教|收费|价格', text))
            if is_ad and not is_q:
                continue
            self_hit = bool(re.search(r'我|本人|我是|今年|身高|体重|斤|岁|产后|多囊|胰岛素|血糖|反弹|平台期|暴食|闭经|吃药|打针|替尔|司美|甲减|桥本|糖前', text))
            pain = bool(re.search(r'愁|崩溃|难受|急|焦虑|失败|不掉|瘦不下来|胖|副作用|恶心|头晕|便秘|失眠|害怕', text))
            score = (2 if is_q else 0) + (2 if self_hit else 0) + (1 if pain else 0) + (1 if len(text) >= 20 else 0)
            if score < 3:
                continue
            # 信号类型
            if re.search(r'多少钱|怎么收费|价格|报名|怎么买|链接|哪里买|求链接|课程|训练营|私教', text):
                sig = '问价/购买'
            elif re.search(r'副作用|反弹|复胖|恶心|头晕|便秘|失眠|停药|掉发', text):
                sig = '副作用/反弹'
            elif is_q:
                sig = '求助/方法'
            elif self_hit:
                sig = '自述/指标'
            else:
                sig = '其他'
            # 身份
            age = re.search(r'(\d{2})\s*岁', text)
            hgt = re.search(r'(?:身高\s*)?(\d{3})\s*(?:cm|厘米)', text)
            wgt = re.search(r'(?:体重\s*)?(\d{2,3})\s*斤', text)
            ident = []
            for w in ['产后','宝妈','多囊','大学生','上班族','打工人','更年期','糖前','胰岛素抵抗','健身教练','护士','医生']:
                if w in text: ident.append(w)
            gender = ''
            if re.search(r'我是女|女生|宝妈|产后|多囊|姐妹', text): gender = '女'
            elif re.search(r'我是男|男生|老公|兄弟|哥们', text): gender = '男'
            who = '，'.join([x for x in [gender, (age.group(1)+'岁' if age else ''), (hgt.group(1)+'cm' if hgt else ''), (wgt.group(1)+'斤' if wgt else ''), '/'.join(ident)] if x])
            if not who: who = '未说明'
            # 卡点
            if re.search(r'反弹|复胖', text): stuck = '反弹'
            elif re.search(r'平台|不掉秤|不掉称', text): stuck = '平台期'
            elif re.search(r'暴食|暴饮暴食', text): stuck = '暴食'
            elif re.search(r'产后', text): stuck = '产后体重滞留'
            elif re.search(r'多囊|闭经|姨妈|月经', text): stuck = '多囊/月经'
            elif re.search(r'胰岛素|血糖|糖前', text): stuck = '血糖/胰岛素抵抗'
            elif re.search(r'副作用|恶心|头晕|便秘|失眠|掉发', text): stuck = '药物副作用'
            elif re.search(r'坚持不了|管不住|嘴馋|食欲', text): stuck = '坚持/食欲'
            elif re.search(r'不知道吃什么|怎么吃|主食|早餐', text): stuck = '不知道怎么吃'
            elif re.search(r'训练营|私教|监督', text): stuck = '监督/训练营'
            else: stuck = '待编码'
            # 试过
            methods = []
            for w in ['节食','断食','轻断食','16+8','代餐','跳操','跑步','健身房','私教','训练营','打针','司美','替尔','吃药','中药','针灸','拔罐','生酮','液断','碳水循环']:
                if w in text: methods.append(w)
            tried = '/'.join(dict.fromkeys(methods)) if methods else '未说明'
            q = text if is_q else '无（非提问）'
            rows.append({
                '信号编号': f'SIG{len(rows)+1:04d}',
                '平台': plat,
                '来源帖子编号': r['编号'],
                '来源帖子标题': str(r.get('标题',''))[:80],
                '帖子类型': post_map.get(r['编号'],{}).get('帖子类型',''),
                '评论原文': text,
                '评论赞': likes,
                '信号类型': sig,
                '谁在说': who,
                '触发事件': '待编码',
                '目标': '待编码',
                '试过什么': tried,
                '卡在哪': stuck,
                '具体问的问题（原话）': q,
                '代表原话': text,
                '置信度': '中' if (is_q or self_hit) else '低',
                '备注': '规则抽取，待人工复核；来源Top10评论',
            })

out = pd.DataFrame(rows)
out = out.sort_values(['平台','评论赞'], ascending=[True, False])
out.to_csv(OUT, index=False, encoding='utf-8-sig')
print('saved', len(out), OUT)
print(out.groupby('平台').size().to_string())
print('\n信号类型:')
print(out['信号类型'].value_counts().to_string())
print('\nTop 8 per platform:')
for plat in ['小红书','抖音','知乎','B站']:
    print('\n==', plat)
    sub = out[out['平台']==plat].head(8)
    for _, x in sub.iterrows():
        print(x['评论赞'], '|', x['信号类型'], '|', x['谁在说'], '|', x['卡在哪'], '|', x['评论原文'][:90])
