# -*- coding: utf-8 -*-
"""信号3：hashtag 与标题词频，按平台分开。
输入：data/health_probe/{platform}_items.jsonl（只读）
输出：
  raw/hashtag_freq_by_platform.csv   hashtag, platform, doc_freq, example_content_ids, is_generic
  raw/title_terms_by_platform.csv    word, platform, doc_freq, example_content_ids, term_len
  raw/title_top40_by_platform.txt    供人工标注语义类型
"""
import csv
import json
import os
import re
from collections import Counter, defaultdict

import jieba

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(BASE))
DATA = os.path.join(ROOT, "03-抓取工具", "MediaCrawler", "data", "health_probe")
OUT = os.path.join(BASE, "raw")
os.makedirs(OUT, exist_ok=True)

PLATFORMS = ["bili", "dy", "weibo", "zhihu", "xhs"]

# 领域词典：保证长术语不被切碎
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
工作压力 职业病 颈椎劳损 应酬喝酒"""
for w in DOMAIN.split():
    jieba.add_word(w, freq=10000)

STOP = set("""的 了 是 在 和 与 或 有 没有 不 也 就 都 还 又 很 太 更 最 我 你 他 她 它 我们 你们
他们 自己 这个 那个 这些 那些 一个 一种 什么 怎么 怎样 如何 为什么 因为 所以 但是 如果
可以 可能 应该 需要 已经 正在 一直 还是 只是 这样 那样 时候 现在 今天 昨天 明天 今年
分享 视频 内容 合集 第 集 篇 条 个 种 次 天 年 月 日 岁 斤 公斤 米 小时 分钟 说 看 做
吃 用 买 去 来 上 下 里 外 中 后 前 多 少 好 坏 大 小 高 低 快 慢 真 假 一 二 三 四 五
六 七 八 九 十 百 千 万 亿 哈哈 哈哈哈 啊 呀 吧 呢 哦 嗯 真的 感觉 觉得 知道 不知道
一下 一点 有点 非常 特别 比较 大家 朋友 老师 医生 博主 网友 评论 点赞 关注 收藏 转发
""".split())

GENERIC_TAGS = set("""健康 科普 涨知识 医学科普 健康科普 女生健康 女性健康 中医 养生 健康养生
抖出健康知识宝藏 健闻登顶计划 微博视频号续航计划 微博视频精选大赏 健康奥斯卡
一分钟精选视频扶持计划 国医的精诚力量 科普有答案 微博视频号迎新计划 热门 上热门
我要上热门 小助手 抖音小助手 健康知识 健康生活 我的健康生活 干货 分享 日常 生活
""".split())

HASHTAG_RE = re.compile(r"#([^#\s@，。！？,.!?]{1,30})#?")


def load_posts(pf):
    path = os.path.join(DATA, f"{pf}_items.jsonl")
    posts = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            cid = str(d.get("content_id") or "")
            if not cid:
                continue
            if cid in posts:
                continue
            posts[cid] = d
    return posts


def main():
    tag_rows = []
    term_rows = []
    top_txt = []

    for pf in PLATFORMS:
        posts = load_posts(pf)
        print(pf, "unique posts", len(posts))

        tag_df = Counter()
        tag_ex = defaultdict(list)
        term_df = Counter()
        term_ex = defaultdict(list)

        for cid, d in posts.items():
            text = ((d.get("title") or "") + " " + (d.get("text") or "")).strip()
            # hashtag
            for t in HASHTAG_RE.findall(text):
                t = t.strip().strip("#")
                if not t or len(t) < 2:
                    continue
                if t.startswith("/") or re.search(r"[A-Za-z]{6,}", t):
                    continue
                tag_df[t] += 1
                if len(tag_ex[t]) < 3:
                    tag_ex[t].append(cid)

            # title terms（标题为主，正文只取前 200 字，避免长文案主导）
            title = (d.get("title") or "").strip()
            if not title:
                title = (d.get("text") or "")[:120]
            title = HASHTAG_RE.sub(" ", title)
            for w in jieba.cut(title):
                w = w.strip()
                if len(w) < 2 or w in STOP:
                    continue
                if not re.search(r"[\u4e00-\u9fffA-Za-z]", w):
                    continue
                if re.fullmatch(r"[A-Za-z]+", w) and w.lower() not in {"hpv", "nmn", "nad", "pm"}:
                    continue
                term_df[w] += 1
                if len(term_ex[w]) < 3:
                    term_ex[w].append(cid)

        for t, n in tag_df.most_common():
            tag_rows.append({"hashtag": t, "platform": pf, "doc_freq": n,
                             "example_content_ids": ";".join(tag_ex[t]),
                             "is_generic": 1 if t in GENERIC_TAGS else 0})
        for w, n in term_df.most_common():
            if n < 3:
                continue
            term_rows.append({"word": w, "platform": pf, "doc_freq": n,
                              "example_content_ids": ";".join(term_ex[w]),
                              "term_len": len(w)})

        top_txt.append(f"\n## {pf}  (posts={len(posts)}, tags={len(tag_df)}, terms={len(term_df)})\n")
        top_txt.append("### hashtag top40\n")
        top_txt.append("、".join(f"{t}({n})" for t, n in tag_df.most_common(40)) + "\n")
        top_txt.append("### title terms top60\n")
        top_txt.append("、".join(f"{w}({n})" for w, n in term_df.most_common(60)) + "\n")

    with open(os.path.join(OUT, "hashtag_freq_by_platform.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["hashtag", "platform", "doc_freq",
                                          "example_content_ids", "is_generic"])
        w.writeheader()
        w.writerows(tag_rows)
    with open(os.path.join(OUT, "title_terms_by_platform.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["word", "platform", "doc_freq",
                                          "example_content_ids", "term_len"])
        w.writeheader()
        w.writerows(term_rows)
    with open(os.path.join(OUT, "title_top40_by_platform.txt"), "w", encoding="utf-8") as f:
        f.writelines(top_txt)

    print("hashtag rows", len(tag_rows), "term rows", len(term_rows))


if __name__ == "__main__":
    main()
