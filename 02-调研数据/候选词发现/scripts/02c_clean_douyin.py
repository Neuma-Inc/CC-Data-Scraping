# -*- coding: utf-8 -*-
"""清洗抖音话题搜索结果：按类目词根校验相关性、去重、去品牌/口号噪音，输出每类 15-60 个。"""
import csv
import collections
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw")

RELEVANT = {
    "体重与代谢": ["减肥", "减脂", "减重", "瘦身", "体重", "代谢", "胰岛素", "脂肪肝", "尿酸", "痛风",
                "血糖", "糖尿病", "控糖", "肥胖", "平台期", "复胖", "生酮", "断食", "代餐", "体脂",
                "热量", "糖前期", "低GI", "碳水", "皮质醇", "内脏脂肪", "暴食", "节食"],
    "心脑血管与呼吸": ["高血压", "血压", "高血脂", "血脂", "胆固醇", "甘油三酯", "心梗", "脑梗", "中风",
                  "冠心病", "心律失常", "早搏", "房颤", "斑块", "动脉硬化", "血栓", "心脏",
                  "呼吸暂停", "打呼噜", "打鼾", "胸闷", "心慌", "心悸"],
    "消化与肝胆肾": ["便秘", "幽门", "胃炎", "胃病", "胃疼", "胃痛", "养胃", "肠易激", "肠道", "益生菌",
                "肾结石", "胆结石", "胆囊", "肝硬化", "腹泻", "拉肚子", "胀气", "反酸", "胃食管",
                "痔疮", "肠镜", "胃镜", "消化不良", "脾胃", "胃溃疡"],
    "睡眠与心理": ["失眠", "睡不着", "入睡", "熬夜", "睡眠", "焦虑", "抑郁", "情绪", "内耗", "双相",
               "社恐", "早醒", "多梦", "褪黑素", "助眠", "冥想", "正念", "心理", "压力"],
    "女性健康": ["多囊", "更年期", "乳腺", "HPV", "hpv", "痛经", "备孕", "产后", "盆底", "子宫",
              "卵巢", "月经", "姨妈", "宫寒", "妇科", "孕期", "哺乳", "胎停", "不孕", "阴道炎", "宫颈"],
    "男性健康": ["前列腺", "睾酮", "精子", "补肾", "阳痿", "早泄", "男科", "男性不育", "肾虚"],
    "儿童青少年": ["儿童", "孩子", "宝宝", "身高", "骨龄", "性早熟", "近视", "过敏", "挑食", "多动",
               "自闭", "发育", "长高", "小儿", "辅食", "积食", "腺样体"],
    "老年健康": ["老年", "老人", "肌少症", "骨质疏松", "骨密度", "认知", "阿尔茨海默", "痴呆", "帕金森",
              "跌倒", "养老", "卧床", "失能", "记忆", "手抖", "白内障"],
    "骨骼关节": ["颈椎", "腰椎", "腰突", "腰痛", "膝盖", "关节", "肩周", "圆肩", "驼背", "体态",
              "坐骨神经", "腱鞘", "足底", "骨折", "康复", "拉伸", "肩颈", "富贵包", "骨盆"],
    "免疫炎症抗衰": ["免疫", "炎症", "抗炎", "抗衰", "NAD", "NMN", "衰老", "过敏", "荨麻疹", "桥本",
                "甲状腺", "红斑狼疮", "类风湿", "抗氧化", "抵抗力"],
    "皮肤毛发口腔": ["痘痘", "祛痘", "痤疮", "敏感肌", "屏障", "泛红", "脱发", "掉发", "发际线",
                "脂溢性", "牙周", "牙龈", "口腔溃疡", "湿疹", "美白", "斑点", "玫瑰痤疮",
                "头皮", "植发", "口臭", "蛀牙", "黄褐斑"],
    "眼耳鼻喉": ["干眼", "眼睛干", "飞蚊", "耳鸣", "鼻炎", "鼻塞", "咽喉", "扁桃体", "中耳炎",
              "听力", "护眼", "散光", "结膜炎", "鼻窦", "声带", "嗓子", "近视"],
    "营养补剂": ["益生菌", "维生素", "维D", "蛋白粉", "鱼油", "钙片", "补钙", "补铁", "叶酸",
              "辅酶Q10", "胶原蛋白", "补剂", "保健品", "镁", "锌", "膳食纤维", "乳清蛋白", "氨糖"],
    "中医养生": ["湿气", "祛湿", "气血", "脾虚", "艾灸", "八段锦", "宫寒", "养肝", "护肝", "上火",
              "中医", "经络", "拔罐", "刮痧", "泡脚", "阳气", "肾虚", "食疗", "药膳", "穴位", "针灸"],
    "体检就医": ["体检", "结节", "肿瘤标志物", "癌症筛查", "挂号", "就医", "复查", "指标",
              "转氨酶", "血常规", "甲功", "彩超", "CT", "核磁", "活检", "穿刺", "息肉"],
    "公共健康": ["流感", "甲流", "乙流", "疫苗", "食品安全", "预制菜", "添加剂", "空气污染", "PM2.5",
              "新冠", "支原体", "传染病", "辐射", "水质", "甲醛", "病毒", "防疫"],
    "肿瘤重症": ["癌症", "肿瘤", "化疗", "放疗", "靶向", "免疫治疗", "抗癌", "乳腺癌", "肺癌",
              "胃癌", "肠癌", "甲状腺癌", "肝癌", "白血病", "淋巴瘤", "复发", "转移", "息肉"],
    "成瘾职业": ["戒烟", "戒酒", "酒精", "久坐", "夜班", "倒班", "咖啡因", "成瘾", "加班",
              "职业病", "工作压力", "办公室", "应酬", "喝酒"],
}

NOISE = re.compile(
    r"卫生巾|酸奶|饮料|奶粉|胶囊|口服液|精华|面膜|旗舰店|官方|同款|好物|测评|推荐|购买|链接|团购|"
    r"我家|一定要|低质量的|高质量的|乖宝宝|萌娃|人类幼崽|动漫|剧情|电影|电视剧|明星|演员|"
    r"鞋子|衣服|穿搭|美妆|减肥营|训练营|招商|加盟|代购|微商|"
    r"每天坚持|坚持锻炼|加强运动|强身健体|增强抵抗力|提高免疫力$|"
    r"表情包|文案|头像|壁纸|歌曲|歌词|"
    r"狗狗|猫咪|宠物|三姐|三哥|阿姨|大叔|宝贝|什么也|不嗨|手势舞|每天一题|"
    r"专家[\u4e00-\u9fffA-Za-z]{2,6}$"
)
SLOGAN = re.compile(r"每天|坚持|一定要|记得|建议|千万|别再|学会|教你|一定要看|必看|收藏")

# 纯造物主/个人 tag 特征：不含疾病词、以人名/宝宝结尾
PERSONAL = re.compile(r"宝宝$|乖乖$|宸宸|小可爱|萌娃|日常$|vlog|Vlog|日记$")


def norm(s):
    return re.sub(r"\s+", "", s).lower()


def main():
    rows = list(csv.DictReader(open(os.path.join(RAW, "douyin_topics.csv"),
                                    encoding="utf-8-sig")))
    # 1. 按话题名去重，保留播放量最大的一条
    best = {}
    for r in rows:
        k = norm(r["topic"])
        play = int(r["play"] or 0)
        if k not in best or play > int(best[k]["play"] or 0):
            best[k] = r
    print("raw", len(rows), "dedup by name", len(best))

    # 2. 相关性 + 噪音过滤
    clean = []
    dropped = []
    for r in best.values():
        cat = r["category_query"]
        name = r["topic"].strip()
        roots = RELEVANT[cat]
        if not any(x.lower() in name.lower() for x in roots):
            dropped.append((cat, name, "no_root"))
            continue
        if NOISE.search(name):
            dropped.append((cat, name, "noise"))
            continue
        if len(name) > 14 and SLOGAN.search(name):
            dropped.append((cat, name, "slogan"))
            continue
        if PERSONAL.search(name) and not re.search(r"病|症|炎|痛|高|低|虚|癌|瘤|结节|近视|过敏|挑食", name):
            dropped.append((cat, name, "personal"))
            continue
        clean.append(r)
    print("clean", len(clean), "dropped", len(dropped))
    dc = collections.Counter(d[2] for d in dropped)
    print("drop reasons", dict(dc))

    by = collections.defaultdict(list)
    for r in clean:
        by[r["category_query"]].append(r)

    out = []
    for cat in RELEVANT:
        v = sorted(by.get(cat, []), key=lambda x: -int(x["play"] or 0))
        keep = v[:60]
        for i, r in enumerate(keep, 1):
            out.append({"category_18": cat, "rank_in_category": i, "topic": r["topic"],
                        "challenge_id": r["challenge_id"], "play": r["play"],
                        "users": r["users"], "query": r["query"],
                        "rank_in_query": r["rank_in_query"],
                        "collected_at": r["collected_at"]})
        print(f"{cat}: clean {len(v)}, kept {len(keep)}")

    outp = os.path.join(RAW, "douyin_topics_clean.csv")
    with open(outp, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print("wrote", outp, len(out))

    with open(os.path.join(RAW, "douyin_dropped_sample.txt"), "w", encoding="utf-8") as f:
        for cat, name, why in dropped:
            f.write(f"{cat}\t{name}\t{why}\n")

    print("\n--- clean top 12 per category ---")
    for cat in RELEVANT:
        v = [r for r in out if r["category_18"] == cat][:12]
        print(f"\n## {cat}")
        print(" | ".join(f"{r['topic']}={int(r['play'])/1e8:.1f}亿" for r in v))


if __name__ == "__main__":
    main()
