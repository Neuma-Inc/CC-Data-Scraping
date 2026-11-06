# -*- coding: utf-8 -*-
"""汇总五路信号，生成候选词池 v2（300-400 词）。
每个词必须有 evidence_ref；严格区分 demand / supply。
输出：
  候选词池_v2.csv
  raw/pool_all_candidates.csv      全部候选与评分（审计用）
  raw/pool_stats_by_category.csv   每类候选/入选/信号结构
"""
import csv
import json
import math
import os
import re
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(BASE))
RAW = os.path.join(BASE, "raw")
OUT_CSV = os.path.join(BASE, "候选词池_v2.csv")
DOC100 = os.path.join(ROOT, "01-调研报告", "大健康话题调研",
                      "05-关键词候选池-100词覆盖版.md")
PROBE_DIR = os.path.join(ROOT, "03-抓取工具", "MediaCrawler", "data", "health_probe")

CATS = ["体重与代谢", "心脑血管与呼吸", "消化与肝胆肾", "睡眠与心理", "女性健康",
        "男性健康", "儿童青少年", "老年健康", "骨骼关节", "免疫炎症抗衰",
        "皮肤毛发口腔", "眼耳鼻喉", "营养补剂", "中医养生", "体检就医",
        "公共健康", "肿瘤重症", "成瘾职业"]

CATEGORY_TERMS = {
    "体重与代谢": ["胰岛素抵抗", "基础代谢", "脂肪肝", "高尿酸", "尿酸高", "痛风", "血糖高",
                "糖尿病前期", "糖前期", "糖尿病", "控糖", "肥胖", "减肥", "减脂", "减重",
                "瘦身", "体重管理", "体重", "平台期", "复胖", "生酮", "轻断食", "断食",
                "代餐", "体脂率", "体脂", "热量缺口", "热量", "代谢", "碳水", "低GI",
                "皮质醇", "内脏脂肪", "暴食", "节食", "食欲", "主食", "腰围", "低血糖",
                "增肌", "肌肉", "蛋白质", "激素", "零食", "早餐", "晚餐", "午餐", "酸奶"],
    "心脑血管与呼吸": ["高血压", "低血压", "高血脂", "血脂", "胆固醇", "甘油三酯", "心梗",
                  "脑梗", "中风", "冠心病", "心律失常", "早搏", "房颤", "颈动脉斑块",
                  "血管斑块", "斑块", "动脉硬化", "血栓", "心脏", "呼吸暂停", "打呼噜",
                  "打鼾", "胸闷", "心慌", "心悸", "脑梗后遗症", "心梗前兆"],
    "消化与肝胆肾": ["便秘", "幽门螺杆菌", "幽门螺旋杆菌", "胃炎", "胃病", "胃疼", "胃痛",
                "养胃", "肠易激", "肠道菌群", "肠道", "肾结石", "胆结石", "胆囊炎", "胆囊",
                "肝硬化", "腹泻", "拉肚子", "胀气", "反酸", "胃食管反流", "痔疮", "肠镜",
                "胃镜", "消化不良", "脾胃", "胃溃疡", "肠息肉", "肾囊肿"],
    "睡眠与心理": ["失眠", "睡不着", "入睡困难", "早醒", "多梦", "熬夜", "睡眠质量",
               "深睡眠", "睡眠障碍", "睡眠", "焦虑", "焦虑症", "抑郁", "抑郁症", "情绪低落",
               "情绪", "精神内耗", "内耗", "双相", "双相障碍", "社恐", "强迫症", "压力",
               "心理", "褪黑素", "助眠", "冥想", "正念"],
    "女性健康": ["多囊", "多囊卵巢", "月经不调", "月经", "痛经", "宫寒", "更年期", "潮热",
              "盗汗", "乳腺结节", "乳腺增生", "乳腺", "HPV", "hpv", "宫颈炎", "宫颈",
              "子宫肌瘤", "子宫", "卵巢早衰", "卵巢囊肿", "卵巢", "备孕", "产后修复",
              "产后", "盆底肌", "盆底", "漏尿", "子宫内膜", "白带", "不孕", "孕期", "哺乳"],
    "男性健康": ["前列腺炎", "前列腺增生", "前列腺", "尿频", "睾酮", "精子质量", "精子",
              "男性不育", "补肾", "阳痿", "早泄", "男性更年期", "肾虚", "精索静脉曲张", "男科"],
    "儿童青少年": ["儿童身高", "孩子长高", "长高", "骨龄", "性早熟", "儿童近视", "近视防控",
               "近视", "儿童过敏", "儿童鼻炎", "过敏", "挑食", "多动症", "多动", "自闭症",
               "自闭", "发育迟缓", "发育", "小儿推拿", "小儿", "积食", "儿童肥胖", "儿童",
               "孩子", "宝宝", "腺样体肥大", "腺样体", "手足口病", "小儿咳嗽", "辅食"],
    "老年健康": ["肌少症", "骨质疏松", "骨密度", "老年痴呆", "阿尔茨海默", "帕金森",
              "记忆力下降", "记忆", "脑萎缩", "跌倒", "失能老人", "失能", "卧床老人",
              "卧床", "老年抑郁", "老年便秘", "吞咽困难", "白内障", "老花眼", "老年",
              "老人", "长寿", "手抖", "认知"],
    "骨骼关节": ["颈椎病", "颈椎曲度变直", "颈椎", "腰椎间盘突出", "腰突", "腰肌劳损",
              "腰痛", "腰疼", "膝关节炎", "膝盖", "半月板损伤", "半月板", "肩周炎",
              "五十肩", "圆肩驼背", "驼背", "体态", "骨盆前倾", "富贵包", "腱鞘炎",
              "足底筋膜炎", "坐骨神经痛", "坐骨神经", "骨折", "康复", "拉伸", "肩颈",
              "脊柱侧弯", "脊柱", "关节"],
    "免疫炎症抗衰": ["免疫力", "免疫力低", "慢性炎症", "炎症", "抗炎饮食", "抗炎", "抗衰老",
                "抗衰", "NAD", "NMN", "自由基", "抗氧化", "过敏体质", "荨麻疹", "桥本甲状腺炎",
                "桥本", "甲减", "甲亢", "甲状腺结节", "甲状腺", "类风湿", "红斑狼疮",
                "自身免疫", "慢性疲劳", "过敏"],
    "皮肤毛发口腔": ["痘痘", "痤疮", "敏感肌", "皮肤屏障", "屏障", "泛红", "脱发", "掉发",
                "发际线后移", "发际线", "脂溢性脱发", "斑秃", "头皮屑", "头皮", "牙周炎",
                "牙周", "牙龈出血", "牙龈", "口腔溃疡", "口臭", "湿疹", "玫瑰痤疮",
                "美白", "黄褐斑", "斑点", "毛囊炎", "皮肤", "植发", "蛀牙"],
    "眼耳鼻喉": ["干眼症", "干眼", "眼睛干涩", "飞蚊症", "飞蚊", "近视", "散光", "结膜炎",
              "耳鸣", "神经性耳鸣", "鼻炎", "过敏性鼻炎", "鼻窦炎", "鼻塞", "咽炎",
              "咽喉炎", "扁桃体炎", "扁桃体", "中耳炎", "听力下降", "听力", "打鼾",
              "声带息肉", "声带", "嗓子"],
    "营养补剂": ["益生菌", "维生素D", "维生素C", "复合维生素", "维生素", "蛋白粉", "乳清蛋白",
              "鱼油", "钙片", "补钙", "铁剂", "补铁", "叶酸", "辅酶Q10", "胶原蛋白",
              "氨糖", "膳食纤维", "镁", "锌", "保健品", "补剂", "维生素B"],
    "中医养生": ["湿气重", "湿气", "祛湿", "排湿气", "气血不足", "补气血", "气血", "脾虚",
              "脾胃虚弱", "艾灸", "八段锦", "宫寒", "养肝", "护肝", "肝火旺", "上火",
              "经络", "拔罐", "刮痧", "泡脚", "肾虚", "阳虚", "食疗", "药膳", "穴位",
              "针灸", "中医", "体质"],
    "体检就医": ["体检报告", "体检指标", "体检异常", "体检", "肺结节", "肺部结节", "甲状腺结节",
              "乳腺结节", "肿瘤标志物", "癌症筛查", "转氨酶高", "转氨酶", "血常规", "甲功",
              "肠息肉", "宫颈筛查", "骨密度检查", "复查", "结节", "囊肿", "息肉", "活检",
              "穿刺", "挂号", "就医"],
    "公共健康": ["流感", "甲流", "乙流", "支原体肺炎", "支原体", "新冠", "疫苗", "食品安全",
              "预制菜", "食品添加剂", "添加剂", "空气污染", "PM2.5", "甲醛", "水质",
              "辐射", "传染病", "肺结核", "结核", "卫生巾", "登革热", "诺如病毒", "病毒", "防疫"],
    "肿瘤重症": ["癌症早期症状", "癌症前兆", "癌症", "肿瘤", "化疗", "放疗", "靶向药",
              "靶向", "免疫治疗", "抗癌", "乳腺癌", "肺癌", "胃癌", "结直肠癌", "肠癌",
              "甲状腺癌", "肝癌", "淋巴瘤", "白血病", "癌症复发", "复发", "癌症转移",
              "转移", "癌前病变", "肿瘤营养", "息肉"],
    "成瘾职业": ["戒烟", "戒酒", "酒精依赖", "酒精中毒", "酒精", "久坐", "久坐危害", "夜班",
              "倒班", "熬夜加班", "加班", "咖啡因", "手机成瘾", "游戏成瘾", "工作压力",
              "职业病", "颈椎劳损", "应酬", "喝酒"],
}

SYNONYMS = {
    "尿酸高": "高尿酸", "高尿酸血症": "高尿酸",
    "心肌梗死": "心梗", "急性心梗": "心梗",
    "脑梗死": "脑梗", "脑梗塞": "脑梗",
    "血压高": "高血压", "血糖偏高": "血糖高",
    "睡不着": "失眠", "入睡困难": "失眠",
    "掉发": "脱发", "掉头发": "脱发",
    "痤疮": "痘痘", "长痘": "痘痘",
    "过敏性鼻炎": "鼻炎",
    "多囊卵巢": "多囊", "多囊卵巢综合征": "多囊",
    "围绝经期": "更年期",
    "腰突": "腰椎间盘突出", "腰间盘突出": "腰椎间盘突出",
    "帕金森病": "帕金森",
    "阿尔茨海默": "老年痴呆", "阿尔茨海默病": "老年痴呆",
    "肌肉流失": "肌少症",
    "骨密度低": "骨质疏松",
    "眼睛干涩": "干眼症",
    "神经性耳鸣": "耳鸣",
    "维D": "维生素D", "维生素d": "维生素D",
    "乳清蛋白": "蛋白粉", "深海鱼油": "鱼油",
    "湿气": "湿气重", "祛湿": "湿气重", "湿气太重": "湿气重",
    "气血虚": "气血不足", "脾胃虚弱": "脾虚",
    "护肝": "养肝", "肝火旺": "上火",
    "养肝护肝": "养肝", "护肝养肝": "养肝", "春季养肝": "养肝",
    "体检指标": "体检报告", "肺部结节": "肺结节",
    "化疗后调理": "化疗", "靶向治疗": "靶向药",
    "戒酒": "酒精依赖", "久坐危害": "久坐", "倒班": "夜班",
    "幽门螺旋杆菌": "幽门螺杆菌",
    "颈椎": "颈椎病", "过敏性鼻炎": "鼻炎",
}

BLOCK = re.compile(
    r"减肥药|减肥针|减肥产品|代餐奶昔|瘦身衣|束腰|减肥贴|瘦腿针|降压药|降压茶|"
    r"血压计|血糖仪|降糖茶|护肝片|养胃饼干|益生菌软糖|排石茶|散结茶|乳腺贴|暖宫贴|"
    r"HPV疫苗广告|生长激素|增高药|增高鞋|植发广告|生发液|牙科广告|种植牙|"
    r"滴眼液|治疗仪|鼻炎贴|呼吸机|制氧机|按摩仪|颈椎贴|膏药|艾灸仪|泡脚桶|"
    r"广告|旗舰店|官方|同款|好物|测评|推荐|购买|链接|团购|代购|微商|招商|加盟|"
    r"神器|智商税|骗局|偏方|秘方|"
    r"服务气血|气血管理|分析服务|科普视频|体检中心|甲状软骨|食品科学|食品工程|"
    r"食品检验|食品经营|食品生产|食品包装|食品机械|食品伙伴|食品饮料|食品级|食品袋|"
    r"食品化学|食品工艺|预制检查井|肺结核科普|老中医|肺结石|"
    r"眼霜|洗发水|护背|撑腰|欧倍青|hbn|王老吉|科兴|中维|一院|专科|主任|教授|"
    r"之王|总结核心|我的体检|看看我的|有害健康|请尽早戒烟|戒酒戒酒"
)

GENERIC = set("""健康 身体 科普 医生 医院 治疗 方法 症状 原因 调理 改善 预防 检查 手术
药物 营养 饮食 食物 运动 训练 科学 专家 知识 生活 日常 习惯 影响 风险 长期 严重
明显 常见 有效 简单 坚持 到底 其实 很多 就是 不是 不能 不会 容易 开始 起来 做好
记住 每天 一次 一定 真的 然后 而且 但是 因为 所以 哪些 怎么办 有没有 是不是
一些 东西 出来 状态 轻松 三个 而是 一样 不好 只有 想要 核心 注意 看看 重要
""".split())

STOP_SUFFIX = re.compile(
    r"(怎么调理|怎么改善|怎么治|怎么办|怎么才能|如何改善|如何调理|如何治疗|"
    r"怎么补|怎么吃|怎么喝|吃什么|吃什么好|吃什么药|能治好吗|能好吗|能根治吗|的症状|"
    r"的表现|的人|会有多|有多累|的真实经历|术后|手术后|消融|"
    r"有哪些|是什么原因|的原因|原因|危害|方法|食谱|偏方|自测|检查|治疗|调理|改善|"
    r"多久能好|严重吗|可怕吗|打卡|必备|冠军|小妙招|困扰)+$"
)

HEALTH = re.compile(
    r"病|症|炎|痛|疼|痒|晕|胀|麻|酸|高|低|血|糖|脂|肝|肾|胃|肠|心|脑|肺|骨|关节|肌|"
    r"皮|痘|发|眠|便|尿|经|孕|产|乳|卵|巢|腺|瘤|癌|药|针|手术|检查|体检|指标|补|维|菌|"
    r"湿|气|虚|毒|免疫|过敏|激素|胰岛|代谢|胖|瘦|肥|食|餐|饿|卡|热|蛋白|钙|铁|锌|镁|"
    r"眼|耳|鼻|喉|牙|口|腔|斑|疹|疮|囊|石|栓|压|糖化|尿酸|嘌呤|抗|衰|老|龄|脊|颈|腰|"
    r"烟|酒|瘾|坐|班|咖|啡|熬夜|劳损|应酬"
)

PLAT_LABEL = {"bili": "B站", "zhihu": "知乎", "douyin": "抖音", "baidu": "百度",
              "weibo": "微博", "xhs": "小红书"}

REJECT_SUFFIX = re.compile(r"(科普|视频|中心|机构|许可证|工程|技术|专业|学院|大学|公司|厂家|品牌|官网)$")
FOOD_OK = {"食品安全", "食品添加剂", "食品配料表", "食品保质期", "食品中毒", "食品卫生",
           "食品营养", "食品标签", "食品防腐剂", "食品干燥剂"}
EXAM_OK = {"体检", "体检报告", "体检指标", "体检异常", "体检项目", "体检套餐", "体检结果",
           "体检发现", "体检前", "体检后", "体检空腹"}


def load_orig():
    text = open(DOC100, encoding="utf-8").read()
    terms = set()
    for line in text.splitlines():
        if not line.startswith("| H"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        terms.add(cells[1])
        for x in re.split(r"[,，、]", cells[3]):
            if x.strip():
                terms.add(x.strip())
    return terms


def load_orig_map():
    """返回 原100词/主搜索词 -> 18类 的映射（从 ### 标题解析）。"""
    text = open(DOC100, encoding="utf-8").read()
    cur = None
    m = {}
    for line in text.splitlines():
        if line.startswith("### "):
            cur = line[4:].split("（")[0].strip()
        elif line.startswith("| H"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 5 or cur not in CATS:
                continue
            m[cells[1]] = cur
            for x in re.split(r"[,，、]", cells[3]):
                if x.strip():
                    m[x.strip()] = cur
    return m


def clean(w):
    w = re.sub(r"\s+", "", str(w or ""))
    w = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9\.\+]", "", w)
    return w


def canonical(w):
    w = clean(w)
    # 叠词/重复短语归一：戒酒戒酒戒酒 -> 戒酒
    for L in (2, 3, 4):
        if len(w) >= L * 2 and len(w) % L == 0:
            unit = w[:L]
            if unit * (len(w) // L) == w:
                w = unit
                break
    for _ in range(3):
        nw = STOP_SUFFIX.sub("", w)
        if nw == w:
            break
        w = nw
    w = SYNONYMS.get(w, w)
    return w


def assign_cat(w, hint=None):
    best, blen = None, 0
    for cat, terms in CATEGORY_TERMS.items():
        for t in terms:
            if t in w and len(t) > blen:
                best, blen = cat, len(t)
    if best:
        return best
    return hint


def longest_term_in(text):
    best, blen = None, 0
    for cat, terms in CATEGORY_TERMS.items():
        for t in terms:
            if t in text and len(t) > blen:
                best, blen = t, len(t)
    return best


ALL_TERMS = {t for terms in CATEGORY_TERMS.values() for t in terms}
EXTRA_OK = set()


def ok_word(w):
    if not w or len(w) < 2 or len(w) > 12:
        return False
    if w in GENERIC or BLOCK.search(w):
        return False
    if not HEALTH.search(w) and w not in EXTRA_OK:
        return False
    if re.fullmatch(r"[0-9\.\+]+", w):
        return False
    # 机构/媒体/课程类尾部词，不是搜索需求词
    if REJECT_SUFFIX.search(w):
        return False
    if w.startswith("食品") and w not in FOOD_OK:
        return False
    if w.startswith("体检") and w not in EXAM_OK:
        return False
    return True


class Cand:
    def __init__(self, word):
        self.word = word
        self.cat = None
        self.demand_refs = []
        self.supply_refs = []
        self.comment_refs = []
        self.sources = set()
        self.demand_platforms = set()
        self.platforms = set()
        self.play = 0
        self.comment_freq = 0
        self.title_freq = 0
        self.hashtag_freq = 0
        self.seeds = set()
        self.comment_outside = False

    def ensure_cat(self, hint):
        if not self.cat:
            self.cat = assign_cat(self.word) or hint


def main():
    global EXTRA_OK
    orig = load_orig()
    orig_canon = {canonical(x) for x in orig}
    EXTRA_OK = set(orig) | orig_canon
    cands = {}

    def get(w):
        w = canonical(w)
        if w not in cands:
            cands[w] = Cand(w)
        return cands[w]

    # ---------- 信号1：抖音话题 ----------
    p = os.path.join(RAW, "douyin_topics_clean.csv")
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        w = canonical(r["topic"])
        if not ok_word(w):
            continue
        c = get(w)
        c.ensure_cat(r["category_18"])
        c.sources.add("douyin_topic")
        c.supply_refs.append(f"douyin_topics_clean.csv#challenge_id={r['challenge_id']}")
        c.platforms.add("抖音")
        c.play = max(c.play, int(float(r["play"] or 0)))
        c.title_freq += 0

    # ---------- 信号2：下拉联想 ----------
    for pf in ["bili", "zhihu", "douyin", "baidu"]:
        fp = os.path.join(RAW, f"suggestions_{pf}.csv")
        if not os.path.exists(fp):
            continue
        seed_cat = {}
        for r in csv.DictReader(open(fp, encoding="utf-8-sig")):
            seed_cat.setdefault(r["seed"], r["category_18"])
            sug = clean(r["suggestion"])
            head = longest_term_in(sug)
            if not head:
                h = canonical(sug)
                # 只用整句兜底时，必须命中词表或包含完整种子词，
                # 否则前缀截断会带出“胰岛果”这类无关实体
                if ok_word(h) and (h in ALL_TERMS or r["seed"] in sug):
                    head = h
            if not head:
                continue
            w = canonical(head)
            if not ok_word(w):
                continue
            c = get(w)
            c.ensure_cat(r["category_18"])
            src = f"{pf}_suggest"
            c.sources.add(src)
            c.demand_platforms.add(PLAT_LABEL.get(pf, pf))
            c.platforms.add(PLAT_LABEL.get(pf, pf))
            c.seeds.add(r["seed"])
            if len(c.demand_refs) < 6:
                c.demand_refs.append(
                    f"suggestions_{pf}.csv#seed={r['seed']};prefix={r['typed_prefix']};rank={r['rank']}")
        # 种子词本身也是“被搜索验证过”的需求词，单独记一条证据
        for sd, cat in seed_cat.items():
            w = canonical(sd)
            if not ok_word(w):
                continue
            c = get(w)
            c.ensure_cat(cat)
            c.sources.add(f"{pf}_suggest")
            c.demand_platforms.add(PLAT_LABEL.get(pf, pf))
            c.platforms.add(PLAT_LABEL.get(pf, pf))
            c.seeds.add(sd)
            if len(c.demand_refs) < 6:
                c.demand_refs.append(
                    f"suggestions_{pf}.csv#seed={sd};prefix={sd};rank=seed_queried")

    # ---------- 信号3：标题词频 + hashtag ----------
    p = os.path.join(RAW, "title_terms_by_platform.csv")
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        n = int(r["doc_freq"])
        if n < 5:
            continue
        w = canonical(r["word"])
        if not ok_word(w):
            continue
        c = get(w)
        c.ensure_cat(None)
        c.sources.add("title_freq")
        c.supply_refs.append(f"title_terms_by_platform.csv#word={r['word']};platform={r['platform']}")
        c.platforms.add(PLAT_LABEL.get(r["platform"], r["platform"]))
        c.title_freq = max(c.title_freq, n)

    p = os.path.join(RAW, "hashtag_freq_by_platform.csv")
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        if r.get("is_generic") == "1":
            continue
        n = int(r["doc_freq"])
        if n < 5:
            continue
        w = canonical(r["hashtag"])
        if not ok_word(w):
            continue
        c = get(w)
        c.ensure_cat(None)
        c.sources.add("hashtag")
        c.supply_refs.append(f"hashtag_freq_by_platform.csv#hashtag={r['hashtag']};platform={r['platform']}")
        c.platforms.add(PLAT_LABEL.get(r["platform"], r["platform"]))
        c.hashtag_freq = max(c.hashtag_freq, n)

    # ---------- 信号4：评论 ----------
    p = os.path.join(RAW, "comment_phrases.csv")
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        n = int(r["freq"])
        if n < 10:
            continue
        w = canonical(r["phrase"])
        if not ok_word(w):
            continue
        c = get(w)
        c.ensure_cat(r["category_guess"] if r["category_guess"] != "未归类" else None)
        c.sources.add("comment")
        c.comment_refs.append(f"comment_phrases.csv#phrase={r['phrase']};ids={r['sample_comment_ids']}")
        c.comment_freq = max(c.comment_freq, n)
        c.comment_outside = c.comment_outside or (r["in_original_100"] == "0")

    # ---------- 打分与筛选 ----------
    for c in cands.values():
        if not c.cat:
            c.cat = assign_cat(c.word)
    all_rows = []
    for c in cands.values():
        if not c.cat or not (c.demand_refs or c.supply_refs or c.comment_refs):
            continue
        demand = 1 if c.demand_refs else 0
        supply = 1 if c.supply_refs else 0
        score = (3 * len(c.sources) + 2 * len(c.demand_platforms)
                 + min(6.0, math.log10(c.play + 1))
                 + min(3.0, c.comment_freq / 200.0)
                 + min(2.0, c.title_freq / 20.0))
        all_rows.append({
            "word": c.word, "category_18": c.cat, "score": round(score, 2),
            "signal_sources": ";".join(sorted(c.sources)),
            "demand_signal": demand, "supply_signal": supply,
            "platforms_seen": ";".join(sorted(c.platforms)),
            "in_original_100": 1 if c.word in orig_canon else 0,
            "play": c.play, "comment_freq": c.comment_freq,
            "title_freq": c.title_freq, "hashtag_freq": c.hashtag_freq,
            "n_sources": len(c.sources), "n_demand_platforms": len(c.demand_platforms),
            "comment_outside": 1 if c.comment_outside else 0,
            "evidence_ref": ";".join((c.supply_refs + c.demand_refs + c.comment_refs)[:4]),
            "notes": "",
            "_cand": c,
        })

    by_cat = defaultdict(list)
    for r in all_rows:
        by_cat[r["category_18"]].append(r)
    for cat in by_cat:
        by_cat[cat].sort(key=lambda x: (-x["score"], -x["demand_signal"], -x["play"]))

    # 每类先取 20，保证 15-60；总计目标 300-400
    selected = []
    for cat in CATS:
        selected.extend(by_cat.get(cat, [])[:20])

    # 评论锚定补位：每类至少 2 个“只有评论证据”的高频词，
    # 避免纯供给排序把评论里的真实需求词挤掉（早餐/主食/热量/食欲等）
    used = {(r["word"], r["category_18"]) for r in selected}
    anchored = []
    for cat in CATS:
        have = [r for r in selected if r["category_18"] == cat and r["comment_freq"] > 0
                and not r["n_demand_platforms"] and r["play"] == 0]
        need = 2 - len(have)
        if need <= 0:
            continue
        pool = [r for r in by_cat.get(cat, [])
                if (r["word"], cat) not in used and r["comment_freq"] >= 200
                and not r["n_demand_platforms"] and r["play"] == 0]
        for r in pool[:need]:
            anchored.append(r)
            used.add((r["word"], cat))

    # 评论高频补位：每类再补最多 3 个评论 >=400 的词（早餐/主食/热量这类生活方式词）
    for cat in CATS:
        pool = [r for r in by_cat.get(cat, [])
                if (r["word"], cat) not in used and r["comment_freq"] >= 400]
        pool.sort(key=lambda r: -r["comment_freq"])
        for r in pool[:3]:
            anchored.append(r)
            used.add((r["word"], cat))
    selected.extend(anchored)

    if len(selected) < 300:
        used = {(r["word"], r["category_18"]) for r in selected}
        rest = [r for r in all_rows if (r["word"], r["category_18"]) not in used]
        rest.sort(key=lambda x: -x["score"])
        selected.extend(rest[: 340 - len(selected)])
    elif len(selected) > 400:
        selected.sort(key=lambda x: -x["score"])
        selected = selected[:400]

    selected.sort(key=lambda r: (CATS.index(r["category_18"]), -r["score"], r["word"]))

    # 评论覆盖度
    cov_map = {}
    p = os.path.join(RAW, "comment_coverage_by_category.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            cov_map[r["category_18"]] = r["coverage"]

    # 写候选池
    fields = ["cand_id", "word", "category_18", "signal_sources", "evidence_ref",
              "demand_signal", "supply_signal", "platforms_seen", "in_original_100",
              "notes", "comment_coverage"]
    rows_out = []
    for i, r in enumerate(selected, 1):
        notes = []
        if r["play"] > 0:
            notes.append(f"抖音播放{r['play']/1e8:.1f}亿")
        if r["n_demand_platforms"]:
            notes.append(f"下拉{r['n_demand_platforms']}平台")
        if r["comment_freq"]:
            notes.append(f"评论{r['comment_freq']}条")
        if r["comment_outside"]:
            notes.append("评论码表外")
        if r["in_original_100"]:
            notes.append("原100词")
        if r["demand_signal"] and r["supply_signal"]:
            notes.append("需求供给交叉")
        elif r["demand_signal"]:
            notes.append("仅需求")
        elif r["supply_signal"]:
            notes.append("仅供给")
        rows_out.append({
            "cand_id": f"V2-{i:04d}", "word": r["word"], "category_18": r["category_18"],
            "signal_sources": r["signal_sources"], "evidence_ref": r["evidence_ref"],
            "demand_signal": r["demand_signal"], "supply_signal": r["supply_signal"],
            "platforms_seen": r["platforms_seen"], "in_original_100": r["in_original_100"],
            "notes": "；".join(notes),
            "comment_coverage": cov_map.get(r["category_18"], "none"),
        })
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_out)

    # 审计表
    with open(os.path.join(RAW, "pool_all_candidates.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in all_rows[0].keys() if k != "_cand"])
        w.writeheader()
        for r in sorted(all_rows, key=lambda x: -x["score"]):
            w.writerow({k: v for k, v in r.items() if k != "_cand"})

    # 分类统计
    stats = []
    for cat in CATS:
        v = by_cat.get(cat, [])
        sel = [r for r in rows_out if r["category_18"] == cat]
        stats.append({
            "category_18": cat, "candidates": len(v), "selected": len(sel),
            "demand": sum(1 for r in sel if r["demand_signal"] == 1),
            "supply": sum(1 for r in sel if r["supply_signal"] == 1),
            "both": sum(1 for r in sel if r["demand_signal"] == 1 and r["supply_signal"] == 1),
            "comment_outside": sum(1 for r in sel if "评论码表外" in r["notes"]),
            "original_100": sum(1 for r in sel if r["in_original_100"] == 1),
            "comment_coverage": cov_map.get(cat, "none"),
        })
    with open(os.path.join(RAW, "pool_stats_by_category.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(stats[0].keys()))
        w.writeheader()
        w.writerows(stats)

    print("all candidates", len(all_rows), "selected", len(rows_out))
    print("demand", sum(r["demand_signal"] for r in rows_out),
          "supply", sum(r["supply_signal"] for r in rows_out),
          "both", sum(1 for r in rows_out if r["demand_signal"] and r["supply_signal"]))
    print("outside 100", sum(1 for r in rows_out if r["in_original_100"] == 0))
    for s in stats:
        print(s)


if __name__ == "__main__":
    main()
