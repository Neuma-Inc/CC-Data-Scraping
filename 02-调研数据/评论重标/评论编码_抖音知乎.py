# -*- coding: utf-8 -*-
import pandas as pd, os

BASE = r'D:\A-灵知生物\小程序\05-市场调研\02-调研数据\评论重标'
OUTDIR = os.path.join(BASE, '400条编码')

DY = {
'DY-C088': dict(who='暴食者（身份未说明）', trig='看到暴食自救法', goal='想提前识别暴食', tried='未说明', stuck='每次都吃到撑到胃痛才知道自己暴食', q='你们是怎么提前知道自己会暴食的', conf='高', note='暴食识别需求'),
'DY-C076': dict(who='胰岛素抵抗者（性别未说明）', trig='爬坡3个月体重不变', goal='想知道为什么体重不动、怎么办', tried='爬坡3个月（30-60分钟，速度4坡度12）、一天一顿饭', stuck='体重没变化、围度只小1cm', q='怎么办', conf='高', note='胰岛素抵抗+运动+节食，典型平台期'),
'DY-C064': dict(who='反复暴食者（身份未说明）', trig='暴食33斤后', goal='停止暴食', tried='节食（导致暴食）', stuck='反复暴食、后悔、发誓，节食后必暴', q='无（非提问）', conf='高', note='暴食循环强证据'),
'DY-C047': dict(who='脸胖身瘦者（身份未说明）', trig='体重卡平台', goal='解决脸胖、身体不胖的问题', tried='未说明', stuck='脸胖但身体体重瘦', q='我脸胖 但身体体重瘦怎么办', conf='中', note='体型/局部胖需求'),
'DY-C043': dict(who='小基数身材焦虑者（自述）', trig='看到情绪/嘴馋视频', goal='正视情绪、摆脱暴食', tried='过度限制饮食', stuck='身材焦虑、暴食、催吐、过度运动', q='无（非提问）', conf='高', note='小基数+进食障碍风险；报告只做需求描述'),
'DY-C087': dict(who='减重1个月者（性别未说明）', trig='从10.6开始减', goal='继续掉秤', tried='虾/牛肉/米饭/菜叶、跳jo姐两次', stuck='只掉1斤、便秘', q='我接下来该怎么办啊', conf='高', note='饮食结构+便秘；需要具体调整'),
'DY-C135': dict(who='未说明', trig='看到胰岛素抵抗科普', goal='想知道怎么发现自己胰岛素抵抗', tried='未说明', stuck='不知道怎么判断', q='是怎么发现自己胰岛素抵抗的啊？', conf='高', note='筛查入口问题'),
'DY-C102': dict(who='轻断食实践者（身份未说明）', trig='跟着央妈轻断食', goal='减重', tried='轻断食1个月', stuck='瘦了10多斤但情绪低落、觉得活着没意思', q='无（非提问）', conf='高', note='极端/单调饮食的情绪代价'),
'DY-C001': dict(who='胰岛素抵抗+脂肪肝+糖前+超重者（身份未说明）', trig='看到减肥针新闻', goal='想打替尔泊肽但医生不给开', tried='医院就诊', stuck='医生认为没到肥胖不给开；自己乱打的人多', q='无（非提问）', conf='高', note='处方门槛与滥用反差'),
'DY-C011': dict(who='50岁控糖者（性别未说明）', trig='看到糖前饮食科普', goal='控糖、预防糖尿病', tried='控糖饮食（未详）', stuck='血糖不高但仍在控糖', q='有没有和我一样？到了50，明明血糖不高，不为减肥也在控糖的？', conf='高', note='50+控糖人群，非减重动机'),
'DY-C070': dict(who='减脂餐实践者（身份未说明）', trig='跟做减脂蒸菜', goal='不掉肌肉', tried='减脂蒸菜', stuck='肌肉掉', q='有没有不掉肌肉的吃法？', conf='高', note='蛋白质/掉肌肉问题'),
'DY-C123': dict(who='减重者（身份未说明）', trig='看到低卡餐', goal='先瘦下去', tried='未说明', stuck='控制不住食欲、怕反弹', q='无（非提问）', conf='高', note='食欲/反弹焦虑'),
'DY-C137': dict(who='控糖者（身份未说明）', trig='看到控糖饮食科普', goal='控糖', tried='鸡蛋豆浆/杂粮饭/鸡肉（吃不惯）', stuck='不能吃的都是从小吃的、能吃的都不爱吃；血糖没控制住', q='无（非提问）', conf='高', note='控糖饮食依从性差'),
'DY-C090': dict(who='极端节食者（身份未说明）', trig='看到30天减14斤视频', goal='快速减重', tried='每天土豆/鸡胸/胡萝卜/西兰花，3个月', stuck='对进食没欲望', q='无（非提问）', conf='高', note='极端单调饮食；不可复制'),
'DY-C059': dict(who='140斤减重者（性别未说明）', trig='看到大基数运动视频', goal='跟练减重', tried='帕梅拉三部曲', stuck='不知道怎么安排频率/时间', q='姐姐帕梅拉三部曲跳两遍是在不同的时间段吗，还是说做完一遍休息一会就继续做啊？', conf='中', note='运动执行细节'),
}

ZH = {
'ZH-C032': dict(who='月经期暴食者（身份未说明）', trig='月经期又暴食', goal='停止暴食、恢复正常', tried='未说明', stuck='一吃就停不下来、撑到想吐、害怕好不了', q='怎么现在成这样了', conf='高', note='暴食+月经期；情绪风险高'),
'ZH-C013': dict(who='190斤购买者（身份未说明）', trig='看到减肥产品', goal='看能不能瘦', tried='买了10盒（产品名未说明）', stuck='刚开始、未知效果', q='无（非提问）', conf='高', note='购买意向+自报体重；产品名缺失'),
'ZH-C087': dict(who='GLP-1使用者（自述胰岛素抵抗、糖耐量异常）', trig='体检发现胰岛素抵抗、2小时血糖高', goal='长期体重管理', tried='替尔泊肽2.5-5-5-2.5、控制饮食、提高活动', stuck='恶心、睡眠浅、烦躁、焦虑', q='无（非提问）', conf='高', note='GLP-1真实用药体验；指标改善+情绪副作用'),
'ZH-C097': dict(who='男性，176cm，154.7斤，办公室', trig='开始打替尔泊肽', goal='减到120斤', tried='替尔泊肽2.4ml、一天一顿', stuck='健身坚持不了、管不住嘴', q='无（非提问）', conf='高', note='男性样本；腹型肥胖+久坐'),
'ZH-C098': dict(who='女性，比对方大10岁，126→86斤', trig='看到替尔泊肽帖子', goal='分享经验、劝正常吃', tried='打针、正常饮食（肉+碳水）', stuck='平台期想液断、打针到90多斤掉头发', q='无（非提问）', conf='高', note='女性+掉发+平台期'),
'ZH-C057': dict(who='替尔泊肽停药反弹者（身份未说明）', trig='停药7周反弹22斤', goal='解释反弹、反驳“躺着瘦”', tried='替尔泊肽、控制饮食+锻炼', stuck='停药反弹；胰岛素抵抗需长期管理', q='无（非提问）', conf='中', note='反弹争议；观点强于个人数据'),
'ZH-C024': dict(who='反复减重者（身份未说明）', trig='看到协和食谱讨论', goal='找到能长期保持的方法', tried='食谱/代餐/大量运动（反复瘦胖）', stuck='短期方法难保持', q='如何保持？', conf='高', note='“瘦是一种习惯”；长期主义'),
'ZH-C079': dict(who='司美格鲁肽使用者（身份未说明）', trig='看到司美减重讨论', goal='减重', tried='司美格鲁肽', stuck='打了好久一斤不掉、仍然很饿', q='无（非提问）', conf='高', note='GLP-1无应答/食欲仍在'),
'ZH-C040': dict(who='171斤购买者（身份未说明）', trig='看到祛湿减肥讨论', goal='看有没有效果', tried='买了祛湿产品', stuck='刚开始、未知', q='无（非提问）', conf='中', note='购买意向；产品/价格缺失'),
'ZH-C030': dict(who='170斤肉食者（身份未说明）', trig='看到教科书饮食', goal='想知道怎么吃', tried='按推荐量吃蔬菜', stuck='吃不下那么多蔬菜', q='有人懂一个肉食者面对一大碗娃娃菜的绝望吗？', conf='中', note='饮食依从性；蔬菜量'),
'ZH-C053': dict(who='准备假期减肥者（身份未说明）', trig='看到两个月40斤', goal='假期减肥', tried='未说明', stuck='怕反弹', q='有反弹吗？', conf='中', note='快速减重+反弹焦虑'),
'ZH-C073': dict(who='52岁女性', trig='看到更年期讨论', goal='讨论运动与更年期', tried='运动', stuck='朋友运动多但症状重', q='会不会是运动太多造成的身体过度使用啊？', conf='中', note='非减重；50+女性健康'),
}

def build(plat, code, src_file, mapping):
    src = pd.read_csv(os.path.join(OUTDIR, src_file))
    rows = []
    for i, (cid, c) in enumerate(mapping.items(), 1):
        s = src[src['编号'] == cid]
        if s.empty:
            print('MISS', cid); continue
        s = s.iloc[0]
        comment = str(s['评论原文'])
        q = c['q']
        if q != '无（非提问）' and q not in comment:
            print('Q NOT VERBATIM', cid, '|', q)
        rows.append({
            '信号编号': f'{code}-S{i:02d}',
            '平台': plat,
            '来源帖子编号': s['来源帖子编号'],
            '来源帖子标题': s['来源帖子标题'],
            '帖子类型': s['帖子类型'],
            '谁在说': c['who'],
            '触发事件': c['trig'],
            '目标': c['goal'],
            '试过什么': c['tried'],
            '卡在哪': c['stuck'],
            '具体问题（原话）': q,
            '代表原话': comment,
            '评论赞': int(s['评论赞']),
            '置信度': c['conf'],
            '备注': c['note'] + f'；来源评论{cid}',
        })
    out = pd.DataFrame(rows)
    path = os.path.join(OUTDIR, f'400条_评论需求_{plat}.csv')
    out.to_csv(path, index=False, encoding='utf-8-sig')
    print('saved', len(out), path)
    return out

dy = build('抖音', 'DY', '评论短名单_抖音.csv', DY)
zh = build('知乎', 'ZH', '评论短名单_知乎.csv', ZH)
print('\n抖音样本:')
print(dy[['信号编号','谁在说','卡在哪','具体问题（原话）','置信度']].head(5).to_string(index=False))
print('\n知乎样本:')
print(zh[['信号编号','谁在说','卡在哪','具体问题（原话）','置信度']].head(5).to_string(index=False))
