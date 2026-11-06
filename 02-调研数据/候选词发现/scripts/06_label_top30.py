# -*- coding: utf-8 -*-
"""信号3 第二步：每个平台输出 Top 30 标题词，并标注 症状/人群/场景/方案。
过滤掉「健康/身体/治疗/方法」这类无法归类的泛词；保留可解释的领域词。
"""
import csv
import os
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw")

GENERIC = set("""健康 身体 治疗 方法 科普 指南 建议 推荐 分享 视频 内容 医生 医院 患者 疾病
原因 改善 预防 调理 恢复 缓解 检查 手术 药物 吃药 营养 饮食 食物 运动 训练 科学 专家
知识 生活 日常 习惯 影响 风险 长期 严重 明显 常见 有效 简单 坚持 到底 其实 很多 就是
不是 不能 不会 容易 开始 起来 做好 记住 每天 一次 一定 真的 然后 而且 但是 因为 所以
哪些 怎么办 有没有 是不是 这么 那么 还有 才能 越来越 一定 不要 不用 不能 可能 应该
博士 全文 微博 播客 偏口鱼 到底 这个 那个 什么 怎么 如何 为什么 时间 中国 最近 持续
感染 出现 导致 发现 研究 这种 一次 一直 已经 还是 只是 这样 那样 时候 现在 今年
办法 医学 反复 宝藏 情况 抖出 抖音 效果 正常 深度 甚至 看到 真正 真相 通过 问题 下降
一样 不好 只有 想要 核心 注意 看看 重要 倪海厦 一些 东西 出来 状态 轻松 三个 而是
""".split())

PEOPLE = set("""女性 男性 女生 男生 女孩子 男孩子 孩子 儿童 宝宝 婴儿 幼儿 老人 老年 老年人
孕妇 产后 宝妈 妈妈 爸爸 家长 父母 青少年 学生 上班族 打工人 程序员 中年人 年轻人
久坐族 夜班族 更年期 青春期 小儿 儿童青少年 人群""".split())

SCENE = set("""熬夜 加班 久坐 夜班 倒班 外卖 奶茶 聚餐 应酬 健身 跑步 减脂期 生理期 经期
换季 空调 办公室 睡前 饭后 早上 晚上 喝酒 抽烟 带娃 出差 旅行 居家 春节 夏天 冬天
秋天 春天 三伏天 开学 考试 月子 哺乳期 孕期""".split())

SOLUTION = set("""减肥 减脂 减重 瘦身 控糖 轻断食 生酮 代餐 运动 训练 拉伸 瑜伽 八段锦 艾灸
泡脚 按摩 刮痧 拔罐 针灸 食疗 药膳 养生 调理 改善 缓解 预防 治疗 手术 吃什么 食谱
饮食 营养 补剂 保健品 益生菌 维生素 蛋白粉 鱼油 钙片 叶酸 辅酶q10 胶原蛋白 氨糖
膳食纤维 褪黑素 助眠 冥想 正念 减脂餐 减肥餐 控糖饮食 抗炎饮食 体检 筛查 复查 疫苗
刷牙 洗牙 护肤 防晒 美白 植发 戒糖 早睡 力量训练 有氧 核心训练 跟练 教程 自测
干预 康复 训练 管理 计划 打卡 食谱 菜谱 吃法 喝法 搭配 补充 修复 护理 防护
中医 动作 备孕 自救 解读 自查 自测 锻炼 练习 习惯 养成""".split())

SYMPTOM = set("""失眠 睡不着 焦虑 抑郁 脱发 掉发 湿疹 鼻炎 痛风 脂肪肝 高血压 低血压 高血脂
心梗 脑梗 中风 肺结节 结节 便秘 胃炎 肠易激 多囊 更年期 痛经 乳腺结节 糖尿病 胰岛素抵抗
肥胖 偏头痛 头痛 头晕 耳鸣 干眼症 近视 口腔溃疡 痘痘 痤疮 敏感肌 荨麻疹 过敏 胃疼 胃痛
腰疼 腰痛 颈椎 腰椎 膝盖 关节 癌症 肿瘤 化疗 放疗 甲状腺 甲减 甲亢 贫血 低血糖 高尿酸
尿酸 血脂 胆固醇 斑块 囊肿 息肉 结石 炎症 慢性炎症 肌少症 骨质疏松 帕金森 痴呆
阿尔茨海默 性早熟 骨龄 多动症 自闭症 发育 身高 前额叶 脑雾 潮热 盗汗 发际线 黄褐斑
斑点 牙周炎 牙龈出血 口臭 鼻窦炎 咽炎 扁桃体 中耳炎 飞蚊症 散光 结膜炎 声带 尿频
前列腺 睾酮 精子 月经 子宫 卵巢 宫颈 HPV 乙肝 肝硬化 胆囊 肾结石 胃食管 反酸 胀气
腹泻 痔疮 睡眠 睡眠质量 早醒 多梦 情绪 内耗 精神内耗 压力 社恐 双相 强迫症 心理
手抖 跌倒 骨折 腱鞘炎 足底筋膜炎 坐骨神经 圆肩驼背 驼背 体态 富贵包 骨盆前倾
脊柱侧弯 半月板 膝关节炎 肩周炎 颈椎病 腰突 腰椎间盘突出 腰肌劳损 干眼 眼睛干涩
老花眼 白内障 吞咽困难 失能 卧床 记忆 记忆力下降 脑萎缩 脑梗后遗症 心梗前兆
幽门螺杆菌 脂肪瘤 甲状腺结节 乳腺增生 子宫肌瘤 卵巢囊肿 前列腺炎 前列腺增生
慢性胃炎 萎缩性胃炎 胃溃疡 肠息肉 肾囊肿 巧克力囊肿 腺样体肥大 积食 手足口病
抑郁 焦虑症 双相障碍 睡眠障碍 神经性耳鸣 过敏性鼻炎 慢性咽炎 牙周 牙龈 蛀牙
体重 免疫力 前额 大脑 早期 查出 皮肤 肌肉 表现 认知 信号 食欲 代谢 激素 皮质醇 流感
""".split())

HASHTAG_NOTE = {
    "dy": "hashtag 样本充足（1,350/1,338 帖带标签），但前几位被平台活动标签占据",
    "weibo": "hashtag 多为平台活动标签（健闻登顶计划等），领域信号弱",
    "bili": "仅 70/1,848 帖带 hashtag，样本不足以代表平台用词",
    "zhihu": "仅 16/1,780 帖带 hashtag，不可用",
    "xhs": "抓取字段未保留 hashtag，本次无 hashtag 信号",
}


def label(term):
    t = term.lower()
    if term in PEOPLE or t in {x.lower() for x in PEOPLE}:
        return "人群"
    if term in SCENE:
        return "场景"
    if term in SOLUTION or t in {x.lower() for x in SOLUTION}:
        return "方案"
    if term in SYMPTOM or any(k in term for k in
                              ["疼", "痛", "痒", "晕", "胀", "炎", "症", "病", "高", "低",
                               "结", "石", "癌", "瘤", "虚", "湿", "痘", "疹", "斑", "囊",
                               "近视", "脱发", "失眠", "便秘", "过敏", "肥胖", "脂肪"]):
        return "症状"
    return "未标注"


def main():
    rows = list(csv.DictReader(open(os.path.join(RAW, "title_terms_by_platform.csv"),
                                    encoding="utf-8-sig")))
    by = defaultdict(list)
    for r in rows:
        w = r["word"]
        if w in GENERIC or len(w) < 2:
            continue
        by[r["platform"]].append(r)

    out = []
    md = ["# 各平台标题词 Top 30（已标注语义类型）\n",
          "> 口径：按帖子去重后，统计词出现在多少条帖子的标题里（doc_freq）。"
          "已剔除「健康/身体/治疗/方法」等无法归类的泛词。"
          "语义类型四选一：症状 / 人群 / 场景 / 方案。\n"]
    for pf in ["bili", "dy", "weibo", "zhihu", "xhs"]:
        v = sorted(by.get(pf, []), key=lambda x: -int(x["doc_freq"]))[:30]
        md.append(f"\n## {pf}\n")
        md.append("| 排名 | 词 | doc_freq | 语义类型 | 示例内容ID |")
        md.append("|---:|---|---:|---|---|")
        for i, r in enumerate(v, 1):
            lab = label(r["word"])
            out.append({"platform": pf, "rank": i, "word": r["word"],
                        "doc_freq": r["doc_freq"], "semantic_type": lab,
                        "example_content_ids": r["example_content_ids"]})
            md.append(f"| {i} | {r['word']} | {r['doc_freq']} | {lab} | "
                      f"{r['example_content_ids'].split(';')[0]} |")
        md.append(f"\n> hashtag 可用性：{HASHTAG_NOTE.get(pf,'')}\n")

    with open(os.path.join(RAW, "title_top30_labeled.csv"), "w",
              encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["platform", "rank", "word", "doc_freq",
                                          "semantic_type", "example_content_ids"])
        w.writeheader()
        w.writerows(out)
    open(os.path.join(RAW, "title_top30_labeled.md"), "w", encoding="utf-8").write(
        "\n".join(md))

    unmatched = sorted({r["word"] for r in out if r["semantic_type"] == "未标注"})
    print("rows", len(out), "unmatched", len(unmatched))
    print("、".join(unmatched))


if __name__ == "__main__":
    main()
