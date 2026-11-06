# -*- coding: utf-8 -*-
"""信号1 第一步：从抖音 21 万话题索引中，按 18 大类词库筛选候选话题。
只读索引，不发请求。输出 candidates_douyin.csv 供人工检查与后续取播放量。
"""
import csv
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(BASE))
CACHE = os.path.join(ROOT, "03-抓取工具", "MediaCrawler", "data", "macro_cache")
OUT = os.path.join(BASE, "raw")
os.makedirs(OUT, exist_ok=True)

# 每类：include 正则（命中任一即候选），exclude 正则（排除噪音）
CATS = {
    "体重与代谢": {
        "inc": r"减脂|减肥|瘦身|掉秤|体重|基础代谢|代谢|胰岛素抵抗|脂肪肝|尿酸|痛风|血糖|糖尿病|控糖|肥胖|平台期|复胖|生酮|断食|代餐|轻食|燃脂|马甲线|体脂",
        "exc": r"减脂营|减肥药|减肥产品|代餐奶昔|招商|加盟|训练营|食谱书|瘦身衣|束腰|减肥贴|瘦腿针",
    },
    "心脑血管与呼吸": {
        "inc": r"高血压|血压|高血脂|血脂|胆固醇|甘油三酯|心梗|脑梗|脑出血|中风|心脏|冠心病|心律失常|早搏|房颤|血管|斑块|动脉硬化|血栓|呼吸暂停|打呼噜|打鼾|胸闷|心慌|心悸",
        "exc": r"血压计|降压药|降压茶|保健品|手表|手环|广告",
    },
    "消化与肝胆肾": {
        "inc": r"便秘|幽门|胃炎|胃疼|胃痛|养胃|肠易激|肠道|益生菌|肾结石|胆结石|胆囊|肝炎|肝硬化|腹泻|拉肚子|胀气|反酸|胃食管|痔疮|肠镜|胃镜|消化不良|脾胃",
        "exc": r"益生菌广告|益生菌软糖|便秘药|肠润茶|排石茶|护肝片|养胃饼干|胃药",
    },
    "睡眠与心理": {
        "inc": r"失眠|睡不着|入睡|熬夜|睡眠|焦虑|抑郁|情绪|压力|内耗|精神内耗|双相|社恐|早醒|多梦|褪黑素|助眠|冥想|正念|心理|emo|孤独|强迫",
        "exc": r"失眠文案|失眠表情包|失眠熊|失眠飞行|助眠仪|睡眠面膜|睡眠仪|褪黑素广告|心理测试",
    },
    "女性健康": {
        "inc": r"多囊|更年期|乳腺|HPV|痛经|备孕|产后|盆底|子宫|卵巢|月经|姨妈|宫寒|妇科|孕期|哺乳|胎停|不孕|阴道炎|宫颈|白带|涨奶|堵奶",
        "exc": r"乳腺贴|散结茶|暖宫贴|产后修复机构|束腹带|HPV预约|HPV疫苗广告|多囊偏方|更年期保健品",
    },
    "男性健康": {
        "inc": r"前列腺|睾酮|精子|补肾|阳痿|早泄|男科|男性不育|壮阳|肾虚|男性健康|男士",
        "exc": r"壮阳药|前列腺贴|补肾广告|保健品|成人用品",
    },
    "儿童青少年": {
        "inc": r"儿童|孩子|宝宝|婴儿|幼儿|身高|骨龄|性早熟|近视|过敏|挑食|多动|自闭|发育|长高|小儿|辅食|疫苗|奶粉|积食",
        "exc": r"增高药|生长激素|增高鞋|近视矫正广告|护眼灯|挑食偏方|奶粉广告|早教",
    },
    "老年健康": {
        "inc": r"老年|老人|银发|肌少症|骨质疏松|骨密度|认知|阿尔茨海默|痴呆|帕金森|跌倒|长寿|养老|卧床|失能|记忆|手抖",
        "exc": r"跌倒报警器|老年鞋|保健品|记忆枕|养老院广告|干细胞",
    },
    "骨骼关节": {
        "inc": r"颈椎|腰椎|腰突|腰痛|膝盖|膝关节|关节炎|肩周|圆肩|驼背|体态|坐骨神经|腱鞘|足底|骨折|康复|拉伸|肩颈|富贵包|骨盆前倾|脊柱",
        "exc": r"颈椎按摩仪|颈椎贴|膏药|背背佳|体态矫正课|氨糖|按摩仪|护腰",
    },
    "免疫炎症抗衰": {
        "inc": r"免疫|炎症|抗炎|抗衰|NAD|NMN|衰老|过敏|荨麻疹|自身免疫|桥本|甲状腺|红斑狼疮|类风湿|抗氧化|自由基|细胞",
        "exc": r"免疫力保健品|抗炎书|抗炎食谱|姜黄素|NAD针|NMN广告|干细胞|抗衰针|免疫球蛋白",
    },
    "皮肤毛发口腔": {
        "inc": r"痘痘|祛痘|敏感肌|屏障|泛红|脱发|掉发|发际线|脂溢性|牙周|牙龈|口腔溃疡|湿疹|荨麻疹|美白|斑点|玫瑰痤疮|头皮|植发|口臭|刷牙|蛀牙",
        "exc": r"祛痘产品|刷酸|敏感肌护肤品|修护霜|植发广告|生发液|牙科广告|种植牙|湿疹药膏|口腔溃疡贴",
    },
    "眼耳鼻喉": {
        "inc": r"干眼|眼睛干|近视|飞蚊|耳鸣|鼻炎|鼻塞|过敏性鼻炎|咽喉|扁桃体|中耳炎|听力|护眼|散光|结膜炎|打鼾|鼻窦|声带|嗓子",
        "exc": r"滴眼液广告|耳鸣治疗仪|鼻炎贴|鼻炎偏方|近视矫正广告|护眼灯|助听器广告",
    },
    "营养补剂": {
        "inc": r"益生菌|维生素|维D|维生素D|蛋白粉|鱼油|钙片|补钙|补铁|叶酸|辅酶Q10|胶原蛋白|补剂|保健品|镁|锌|膳食纤维|乳清蛋白|氨糖|葡萄籽",
        "exc": r"益生菌广告|维D软糖|蛋白粉广告|鱼油广告|智商税|保健品骗局|招商",
    },
    "中医养生": {
        "inc": r"湿气|祛湿|排湿|气血|脾虚|艾灸|八段锦|宫寒|养肝|护肝|上火|中医|经络|拔罐|刮痧|泡脚|阳气|肾虚|食疗|药膳|穴位|按摩|针灸|体质",
        "exc": r"祛湿茶|祛湿贴|艾灸仪|艾灸贴|养肝茶|护肝片|健脾丸|补血口服液|按摩仪|养生馆",
    },
    "体检就医": {
        "inc": r"体检|体检报告|结节|肿瘤标志物|癌症筛查|甲状腺结节|肺结节|乳腺结节|挂号|就医|复查|指标|转氨酶|血常规|甲功|彩超|CT|核磁|活检|穿刺",
        "exc": r"体检套餐|体检机构|散结茶|散结|癌变|早筛广告|代体检",
    },
    "公共健康": {
        "inc": r"流感|甲流|乙流|疫苗|食品安全|预制菜|添加剂|空气污染|PM2\.5|新冠|支原体|传染病|辐射|水质|甲醛|病毒|防疫|卫生巾|食品安全事件",
        "exc": r"流感药|疫苗预约|黄牛|检测仪|净化器广告|食品安全谣言",
    },
    "肿瘤重症": {
        "inc": r"癌症|肿瘤|化疗|放疗|靶向|免疫治疗|抗癌|乳腺癌|肺癌|胃癌|肠癌|甲状腺癌|白血病|淋巴瘤|复发|转移|癌前|息肉|活检",
        "exc": r"抗癌食物|抗癌偏方|神药|靶向药代购|印度仿制药|饥饿疗法|保健品",
    },
    "成瘾职业": {
        "inc": r"戒烟|戒酒|酒精|久坐|夜班|倒班|咖啡因|手机成瘾|游戏成瘾|加班|职业病|工作压力|办公室|工位|熬夜加班|应酬|喝酒",
        "exc": r"戒烟药|电子烟|解酒药|戒酒偏方|夜班补贴|熬夜神器|久坐神器",
    },
}

BAD_NAME = re.compile(r"[\s#@【】\[\]（）()「」\"“”'’,，。.!！?？:：;；/\\|~\-—_+=*&%$^<>]|^\d+$")
PHARMA_AD = re.compile(r"广告|招商|加盟|代理|批发|旗舰店|官网|购买|下单|优惠|福利|领券|直播间|小店|同款|链接")


def clean_name(n):
    return (n or "").strip().lstrip("#")


def main():
    idx = json.load(open(os.path.join(CACHE, "douyin_hashtag_index_big.json"), encoding="utf-8"))
    print("index size", len(idx))

    rows = []
    seen = set()
    for cat, rule in CATS.items():
        inc, exc = re.compile(rule["inc"]), re.compile(rule["exc"])
        hits = []
        for name, cid in idx.items():
            n = clean_name(name)
            if not (2 <= len(n) <= 14):
                continue
            if BAD_NAME.search(n) or PHARMA_AD.search(n):
                continue
            if not inc.search(n):
                continue
            if exc.search(n):
                continue
            hits.append((n, str(cid)))
        # 按名称长度升序（短名通常更核心），去重
        hits.sort(key=lambda x: (len(x[0]), x[0]))
        for n, cid in hits:
            key = (n, cid)
            if key in seen:
                continue
            seen.add(key)
            rows.append({"category_18": cat, "topic": n, "challenge_id": cid,
                         "name_len": len(n)})
        print(f"{cat}: {len(hits)} hits")

    out = os.path.join(OUT, "douyin_topic_candidates.csv")
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["category_18", "topic", "challenge_id", "name_len"])
        w.writeheader()
        w.writerows(rows)
    print("total unique", len(rows), "->", out)

    # 每类抽样 15 个，便于人工检查词库是否跑偏
    with open(os.path.join(OUT, "douyin_topic_candidates_sample.txt"), "w", encoding="utf-8") as f:
        for cat in CATS:
            sub = [r["topic"] for r in rows if r["category_18"] == cat]
            f.write(f"\n## {cat} ({len(sub)})\n")
            f.write("、".join(sub[:40]) + "\n")
            print(f"\n## {cat} ({len(sub)})\n" + "、".join(sub[:25]))


if __name__ == "__main__":
    main()
