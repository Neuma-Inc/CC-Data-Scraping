# -*- coding: utf-8 -*-
"""信号4：评论区挖掘（93,410 条旧评论 + 14,922 条新评论，去重后 108,332 条）。
提取：高频名词/短语、症状描述、追问句；重点找「原 100 词码表外」的词。
输出：
  raw/comment_phrases.csv
  raw/comment_phrases_outside_100.csv
  raw/comment_coverage_by_category.csv
  raw/comment_source_summary.csv
"""
import csv
import glob
import json
import os
import re
from collections import Counter, defaultdict

import jieba

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(BASE))
OUT = os.path.join(BASE, "raw")
os.makedirs(OUT, exist_ok=True)

CSV_PATH = os.path.join(ROOT, "02-调研数据", "减重课程五平台数据",
                        "03_评论总表_全量评论明细.csv")
DOC100 = os.path.join(ROOT, "01-调研报告", "大健康话题调研",
                      "05-关键词候选池-100词覆盖版.md")

DOMAIN = """胰岛素抵抗 基础代谢 脂肪肝 高尿酸 糖尿病前期 糖前期 轻断食 生酮饮食 代餐 平台期
复胖 体脂率 热量缺口 高血压 低血压 高血脂 甘油三酯 心梗 脑梗 冠心病 心律失常 房颤
颈动脉斑块 血管斑块 动脉硬化 睡眠呼吸暂停 打呼噜 幽门螺杆菌 胃食管反流 肠易激 肠道菌群
肾结石 胆结石 胆囊炎 肝硬化 胃溃疡 消化不良 入睡困难 睡眠质量 深睡眠 情绪低落 精神内耗
强迫症 多囊卵巢 月经不调 痛经 宫寒 更年期 潮热盗汗 乳腺结节 乳腺增生 宫颈炎 子宫肌瘤
卵巢早衰 卵巢囊肿 产后修复 盆底肌 腹直肌 漏尿 前列腺炎 前列腺增生 精子质量 男性不育
男性更年期 精索静脉曲张 儿童身高 骨龄 性早熟 儿童近视 近视防控 儿童过敏 腺样体肥大
发育迟缓 小儿推拿 积食 手足口病 肌少症 骨质疏松 骨密度 老年痴呆 阿尔茨海默 帕金森
记忆力下降 脑萎缩 失能老人 吞咽困难 白内障 老花眼 颈椎病 颈椎曲度变直 腰椎间盘突出
腰肌劳损 膝关节炎 半月板损伤 肩周炎 五十肩 圆肩驼背 骨盆前倾 富贵包 腱鞘炎
足底筋膜炎 坐骨神经痛 脊柱侧弯 慢性炎症 抗炎饮食 抗衰老 自由基 抗氧化 过敏体质 荨麻疹
桥本甲状腺炎 甲减 甲亢 甲状腺结节 类风湿 红斑狼疮 自身免疫 慢性疲劳 痘痘 痤疮 敏感肌
皮肤屏障 脂溢性脱发 斑秃 头皮屑 牙周炎 牙龈出血 口腔溃疡 口臭 湿疹 玫瑰痤疮 黄褐斑
毛囊炎 干眼症 飞蚊症 结膜炎 耳鸣 神经性耳鸣 鼻炎 过敏性鼻炎 鼻窦炎 咽炎 扁桃体炎
中耳炎 听力下降 声带息肉 益生菌 维生素D 维生素C 复合维生素 蛋白粉 乳清蛋白 鱼油 钙片
补钙 铁剂 叶酸 辅酶Q10 胶原蛋白 氨糖 膳食纤维 保健品 湿气重 祛湿 排湿气 气血不足
补气血 脾虚 脾胃虚弱 艾灸 八段锦 宫寒 养肝 护肝 肝火旺 上火 经络 拔罐 刮痧 泡脚
肾虚 阳虚 食疗 药膳 穴位 体检报告 体检指标 肺结节 肿瘤标志物 癌症筛查 转氨酶
血常规 甲功 肠息肉 宫颈筛查 骨密度检查 体检异常 支原体肺炎 食品安全 预制菜 食品添加剂
空气污染 传染病 卫生巾 登革热 诺如病毒 癌症早期症状 癌症前兆 化疗 放疗 靶向药
免疫治疗 乳腺癌 肺癌 胃癌 结直肠癌 甲状腺癌 肝癌 淋巴瘤 白血病 癌症复发 癌症转移
癌前病变 肿瘤营养 酒精依赖 酒精中毒 久坐危害 熬夜加班 咖啡因 手机成瘾 游戏成瘾
工作压力 职业病 颈椎劳损 应酬喝酒 司美格鲁肽 替尔泊肽 二甲双胍 奥利司他 左旋肉碱
白芸豆 抗性淀粉 血糖生成指数 动态血糖仪 连续血糖监测 体脂秤 代谢综合征 高胰岛素血症
黑棘皮 多毛 脱发 月经稀发 闭经 崩漏 黄体酮 优思明 达英35 肌醇 手性肌醇
""".split()
for w in DOMAIN:
    jieba.add_word(w, freq=10000)

STOP = set("""的 了 是 在 和 与 或 有 没有 不 也 就 都 还 又 很 太 更 最 我 你 他 她 它 我们 你们
他们 自己 这个 那个 这些 那些 一个 一种 什么 怎么 怎样 如何 为什么 因为 所以 但是 如果
可以 可能 应该 需要 已经 正在 一直 还是 只是 这样 那样 时候 现在 今天 昨天 明天 今年
真的 感觉 觉得 知道 不知道 一下 一点 有点 非常 特别 比较 大家 朋友 老师 医生 博主 网友
评论 点赞 关注 收藏 转发 谢谢 好的 好吧 哈哈 哈哈哈 呵呵 嗯 哦 啊 呀 吧 呢 吗 嘛 哎 唉
这个 那个 东西 事情 问题 情况 方面 地方 时间 样子 意思 之前 之后 以后 以前 现在 最近
""".split())

# 泛化词：不能进候选池，但保留在原始统计里
GENERIC = set("""健康 身体 治疗 方法 科普 指南 建议 推荐 分享 视频 内容 医生 医院 患者 疾病
症状 原因 改善 预防 调理 恢复 缓解 检查 手术 药物 吃药 营养 饮食 食物 运动 训练 减肥
减脂 体重 焦虑 熬夜 孩子 女性 男性 女性健康 男性健康 中医 养生 科学 专家 知识 大脑
生活 日常 习惯 影响 风险 长期 严重 明显 常见 有效 简单 坚持 到底 其实 很多 就是 不是
不能 不会 容易 开始 起来 做好 记住 每天 一次 一定 真的 然后 而且 但是 因为 所以
""".split())

CAT_LEX = {
    "体重与代谢": ["胰岛素抵抗", "基础代谢", "脂肪肝", "高尿酸", "尿酸", "痛风", "血糖", "糖尿病",
                "控糖", "肥胖", "减肥", "减脂", "减重", "体重", "平台期", "复胖", "生酮",
                "轻断食", "代餐", "体脂", "热量", "代谢", "司美", "替尔泊肽", "二甲双胍", "多囊"],
    "心脑血管与呼吸": ["高血压", "血压", "高血脂", "血脂", "胆固醇", "甘油三酯", "心梗", "脑梗",
                  "中风", "冠心病", "心律失常", "早搏", "房颤", "斑块", "动脉硬化", "血栓",
                  "心脏", "呼吸暂停", "打呼噜", "打鼾", "胸闷", "心慌", "心悸"],
    "消化与肝胆肾": ["便秘", "幽门", "胃炎", "胃疼", "胃痛", "养胃", "肠易激", "肠道", "益生菌",
                "肾结石", "胆结石", "胆囊", "肝硬化", "腹泻", "拉肚子", "胀气", "反酸",
                "胃食管", "痔疮", "肠镜", "胃镜", "消化不良", "脾胃"],
    "睡眠与心理": ["失眠", "睡不着", "入睡", "熬夜", "睡眠", "焦虑", "抑郁", "情绪", "内耗",
               "双相", "社恐", "早醒", "多梦", "褪黑素", "助眠", "冥想", "正念", "心理", "压力"],
    "女性健康": ["多囊", "更年期", "乳腺", "HPV", "痛经", "备孕", "产后", "盆底", "子宫", "卵巢",
              "月经", "姨妈", "宫寒", "妇科", "孕期", "哺乳", "胎停", "不孕", "阴道炎", "宫颈"],
    "男性健康": ["前列腺", "睾酮", "精子", "补肾", "阳痿", "早泄", "男科", "男性不育", "肾虚"],
    "儿童青少年": ["儿童", "孩子", "宝宝", "身高", "骨龄", "性早熟", "近视", "过敏", "挑食",
               "多动", "自闭", "发育", "长高", "小儿", "辅食", "积食"],
    "老年健康": ["老年", "老人", "肌少症", "骨质疏松", "骨密度", "认知", "阿尔茨海默", "痴呆",
              "帕金森", "跌倒", "养老", "卧床", "失能", "记忆", "手抖"],
    "骨骼关节": ["颈椎", "腰椎", "腰突", "腰痛", "膝盖", "关节", "肩周", "圆肩", "驼背", "体态",
              "坐骨神经", "腱鞘", "足底", "骨折", "康复", "拉伸", "肩颈", "富贵包", "骨盆"],
    "免疫炎症抗衰": ["免疫", "炎症", "抗炎", "抗衰", "NAD", "NMN", "衰老", "过敏", "荨麻疹",
                "桥本", "甲状腺", "红斑狼疮", "类风湿", "抗氧化"],
    "皮肤毛发口腔": ["痘痘", "祛痘", "痤疮", "敏感肌", "屏障", "泛红", "脱发", "掉发", "发际线",
                "脂溢性", "牙周", "牙龈", "口腔溃疡", "湿疹", "美白", "斑点", "玫瑰痤疮",
                "头皮", "植发", "口臭", "蛀牙"],
    "眼耳鼻喉": ["干眼", "眼睛干", "飞蚊", "耳鸣", "鼻炎", "鼻塞", "咽喉", "扁桃体", "中耳炎",
              "听力", "护眼", "散光", "结膜炎", "鼻窦", "声带", "嗓子"],
    "营养补剂": ["益生菌", "维生素", "维D", "蛋白粉", "鱼油", "钙片", "补钙", "补铁", "叶酸",
              "辅酶Q10", "胶原蛋白", "补剂", "保健品", "镁", "锌", "膳食纤维", "乳清蛋白", "氨糖"],
    "中医养生": ["湿气", "祛湿", "气血", "脾虚", "艾灸", "八段锦", "宫寒", "养肝", "护肝", "上火",
              "中医", "经络", "拔罐", "刮痧", "泡脚", "阳气", "肾虚", "食疗", "药膳", "穴位", "针灸"],
    "体检就医": ["体检", "结节", "肿瘤标志物", "癌症筛查", "挂号", "就医", "复查", "指标",
              "转氨酶", "血常规", "甲功", "彩超", "CT", "核磁", "活检", "穿刺"],
    "公共健康": ["流感", "甲流", "疫苗", "食品安全", "预制菜", "添加剂", "空气污染", "PM2.5",
              "新冠", "支原体", "传染病", "辐射", "水质", "甲醛", "病毒", "防疫"],
    "肿瘤重症": ["癌症", "肿瘤", "化疗", "放疗", "靶向", "免疫治疗", "抗癌", "乳腺癌", "肺癌",
              "胃癌", "肠癌", "甲状腺癌", "白血病", "淋巴瘤", "复发", "转移", "息肉"],
    "成瘾职业": ["戒烟", "戒酒", "酒精", "久坐", "夜班", "倒班", "咖啡因", "成瘾", "加班",
              "职业病", "工作压力", "办公室", "应酬", "喝酒"],
}

SYMPTOM = re.compile(
    r"(疼|痛|痒|胀|晕|麻|酸|堵|闷|慌|肿|出血|失眠|便秘|腹泻|反酸|胀气|恶心|心慌|手抖|"
    r"耳鸣|掉发|脱发|长痘|泛红|乏力|疲倦|盗汗|潮热|口干|口苦|嗳气|烧心|尿频|尿急|"
    r"月经不调|闭经|痛经|爆痘|脱皮|瘙痒|刺痛|麻木|僵硬|弹响|水肿|抽筋|打嗝|放屁)"
)
PATTERNS = [
    re.compile(r"[\u4e00-\u9fff]{1,6}(?:疼|痛|痒|胀|晕|麻|酸|堵|闷|慌|肿|出血|失眠|便秘|腹泻|反酸|胀气|恶心|心慌|手抖|耳鸣|掉发|脱发|长痘|泛红|乏力|盗汗|潮热|烧心|尿频)"),
    re.compile(r"(?:半夜|凌晨|饭后|睡前|早上|经期|一吃|一喝|一熬夜|每次)[\u4e00-\u9fff]{0,6}(?:醒|疼|痛|胀|晕|拉|吐|困|饿|胖|肿|咳)"),
    re.compile(r"(?:吃完|吃完饭|一吃|一喝|饿|熬夜|睡前|半夜|早上|下午)[\u4e00-\u9fff]{0,4}(?:困|饿|醒|胀|疼|痛|晕|心慌|手抖|冒汗|出汗|犯困|想吃|暴食)"),
    re.compile(r"[\u4e00-\u9fff]{2,8}(?:偏高|偏低|超标|异常|升高|降低)"),
]

# 健康相关性字符/词：短语必须命中，否则丢弃
HEALTH_CHARS = re.compile(
    r"病|症|炎|痛|疼|痒|晕|胀|麻|酸|高|低|血|糖|脂|肝|肾|胃|肠|心|脑|肺|骨|关节|肌|"
    r"皮|痘|发|眠|便|尿|经|孕|产|乳|卵|巢|腺|瘤|癌|药|针|手术|检查|体检|指标|补|维|菌|"
    r"湿|气|虚|毒|免疫|过敏|激素|胰岛|代谢|胖|瘦|肥|食|餐|饿|卡|热|蛋白|钙|铁|锌|镁|"
    r"眼|耳|鼻|喉|牙|口|腔|斑|疹|疮|囊|石|栓|压|糖化|尿酸|嘌呤|抗|衰|老|龄|骨|脊|颈|腰"
)
QUESTION = re.compile(r"(?:怎么|如何|能不能|要不要|该不该|有没有|是不是|为什么)")

# 仅保留健康领域的名词/动名词；DOMAIN 词无条件保留
DOMAIN_SET = set(DOMAIN)


def load_original_100():
    text = open(DOC100, encoding="utf-8").read()
    terms = set()
    for line in text.splitlines():
        if not line.startswith("| H"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        topic = cells[1]
        terms.add(topic)
        for extra in re.split(r"[,，、]", cells[3]):
            if extra.strip():
                terms.add(extra.strip())
    return terms


def clean(t):
    t = re.sub(r"http\S+|www\.\S+", " ", t)
    t = re.sub(r"@[^\s]+", " ", t)
    t = re.sub(r"\[[^\]]{1,6}\]", " ", t)  # [呲牙] 类表情
    t = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def candidates(text):
    import jieba.posseg as pseg
    toks = [(w, f) for w, f in pseg.cut(text) if w.strip()]
    out = set()
    zh = []
    for w, f in toks:
        if not re.search(r"[\u4e00-\u9fff]", w):
            continue
        if len(w) < 2 or w in STOP or w in GENERIC:
            continue
        keep = (w in DOMAIN_SET) or f.startswith("n") or f in ("vn", "an")
        if not keep:
            continue
        out.add(w)
        zh.append(w)
    for i in range(len(zh) - 1):
        b = zh[i] + zh[i + 1]
        if 3 <= len(b) <= 10 and b not in STOP:
            out.add(b)
        if i < len(zh) - 2:
            c = b + zh[i + 2]
            if 4 <= len(c) <= 12:
                out.add(c)
    for pat in PATTERNS:
        for m in pat.findall(text):
            if 2 <= len(m) <= 12:
                out.add(m)
    # 追问句：必须含健康字，否则「怎么办」这类泛问句会被收进来
    for m in re.findall(r"(?:怎么|如何|能不能|要不要|该不该|有没有|是不是|为什么)[\u4e00-\u9fff]{1,8}", text):
        if HEALTH_CHARS.search(m) and len(m) <= 12:
            out.add(m)
    return out


def is_health_phrase(ph):
    if ph in GENERIC or ph in STOP:
        return False
    if not HEALTH_CHARS.search(ph):
        return False
    # 纯口语/时间/数量词排除
    if re.fullmatch(r"[一二三四五六七八九十百千万两0-9]+(天|年|月|日|次|斤|公斤|小时|分钟|个|岁)", ph):
        return False
    if re.search(r"^(回复|正常|控制|不吃|不要|这么|一样|这种|还有|确实|直接|或者|的话|两个|那么|效果|总结|力量|开始|起来|做好|记住|每天|一次|一定|真的)$", ph):
        return False
    return True


def assign_cat(phrase):
    best, best_len = "未归类", 0
    for cat, lex in CAT_LEX.items():
        for w in lex:
            if w in phrase and len(w) > best_len:
                best, best_len = cat, len(w)
    return best


def main():
    orig = load_original_100()
    print("original terms", len(orig))

    comments = {}  # id -> dict
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cid = str(row.get("评论ID") or "").strip()
            txt = (row.get("评论原文") or "").strip()
            if not cid or not txt:
                continue
            comments[cid] = {"id": cid, "platform": row.get("平台") or "",
                             "text": txt, "source": "legacy_csv",
                             "post_cat": row.get("所属内容主分类") or ""}

    added = 0
    for p in glob.glob(os.path.join(ROOT, "03-抓取工具", "MediaCrawler", "data",
                                    "*", "jsonl", "search_comments_*.jsonl")):
        plat = p.split(os.sep + "data" + os.sep)[1].split(os.sep)[0]
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                cid = str(d.get("comment_id") or "").strip()
                txt = (d.get("content") or "").strip()
                if not cid or not txt or cid in comments:
                    continue
                comments[cid] = {"id": cid, "platform": plat, "text": txt,
                                 "source": "new_jsonl", "post_cat": ""}
                added += 1
    print("comments total", len(comments), "new added", added)

    freq = Counter()
    examples = defaultdict(list)
    plats = defaultdict(Counter)
    srcs = defaultdict(Counter)

    for cid, c in comments.items():
        text = clean(c["text"])
        if len(text) < 2:
            continue
        for ph in candidates(text):
            freq[ph] += 1
            if len(examples[ph]) < 3:
                examples[ph].append(cid)
            plats[ph][c["platform"]] += 1
            srcs[ph][c["source"]] += 1

    rows = []
    for ph, n in freq.items():
        if n < 5 or len(ph) < 2:
            continue
        if not is_health_phrase(ph):
            continue
        if re.search(r"(我的|你的|他的|她的|这个|那个|就是|不是|真的|感觉|觉得|可以|什么|怎么)", ph):
            continue
        rows.append({
            "phrase": ph, "freq": n,
            "sample_comment_ids": ";".join(examples[ph]),
            "platforms": ";".join(f"{k}:{v}" for k, v in plats[ph].most_common()),
            "source_mix": ";".join(f"{k}:{v}" for k, v in srcs[ph].most_common()),
            "category_guess": assign_cat(ph),
            "in_original_100": 1 if any(o in ph or ph in o for o in orig) else 0,
        })
    rows.sort(key=lambda r: -r["freq"])

    # 冗余收敛：若短词是长词子串且频次接近，保留长词
    rows_by_ph = {r["phrase"]: r for r in rows}
    drop = set()
    for r in rows:
        ph = r["phrase"]
        for longer in rows:
            lp = longer["phrase"]
            if lp != ph and ph in lp and longer["freq"] >= r["freq"] * 0.9:
                if len(lp) <= len(ph) + 6:
                    drop.add(ph)
                    break
    kept = [r for r in rows if r["phrase"] not in drop]
    print("phrases raw", len(rows), "kept", len(kept), "dropped redundant", len(drop))

    cols = ["phrase", "freq", "sample_comment_ids", "platforms", "source_mix",
            "category_guess", "in_original_100"]
    with open(os.path.join(OUT, "comment_phrases.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(kept)

    outside = [r for r in kept if r["in_original_100"] == 0 and r["freq"] >= 10]
    outside.sort(key=lambda r: -r["freq"])
    with open(os.path.join(OUT, "comment_phrases_outside_100.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(outside)

    # 评论覆盖度：按类核心词命中的唯一评论数
    cov = []
    for cat, lex in CAT_LEX.items():
        hit_comments = 0
        pf = Counter()
        for cid, c in comments.items():
            t = c["text"]
            if any(w in t for w in lex):
                hit_comments += 1
                pf[c["platform"]] += 1
        if hit_comments >= 300 and len(pf) >= 3:
            level = "full"
        elif hit_comments >= 30:
            level = "partial"
        else:
            level = "none"
        cov.append({"category_18": cat, "comments_hit": hit_comments,
                    "platforms_hit": len(pf),
                    "platform_breakdown": ";".join(f"{k}:{v}" for k, v in pf.most_common()),
                    "coverage": level})
    cov.sort(key=lambda r: -r["comments_hit"])
    with open(os.path.join(OUT, "comment_coverage_by_category.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["category_18", "comments_hit", "platforms_hit",
                                          "platform_breakdown", "coverage"])
        w.writeheader()
        w.writerows(cov)

    # 数据源小结
    src_count = Counter(c["source"] for c in comments.values())
    plat_count = Counter(c["platform"] for c in comments.values())
    with open(os.path.join(OUT, "comment_source_summary.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["维度", "值", "评论数"])
        for k, v in src_count.items():
            w.writerow(["source", k, v])
        for k, v in plat_count.items():
            w.writerow(["platform", k, v])
        w.writerow(["total", "unique_comments", len(comments)])

    print("coverage:")
    for r in cov:
        print(" ", r["category_18"], r["comments_hit"], r["coverage"])
    print("top outside-100:")
    for r in outside[:30]:
        print(f"  {r['phrase']}({r['freq']}) -> {r['category_guess']}")


if __name__ == "__main__":
    main()
