---
ttl: task_bound
title: L02-C3 子类目挖矿簿 · 市场广度成分（C3_breadth，六成分唯一 KEEP）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成
---

# L02 · C3 广度成分

**① 一句话**：上涨家数占比 + 沪深300 日收益的秩分位加权（0.6/0.4），度量"普涨/普跌"。

**② 实测**：`emotion_index_builder.py:270-293`（`_SQL_AD_DAILY` :106-112 = `countIf(pct_change>0)/count()` + sum(amount) + median(turnover)，源 kline_daily；`_SQL_INDEX_CLOSE` :113-117 限 symbol='000300'）；子权重 `wb={"up_ratio":0.6,"index_ret":0.4}` :282。考试（`emotion_line/exam_report_v1.md` 卡 B）：**唯一 KEEP 成分**，RankIC −0.176 / t −2.10 / n 143；与 C1 冗余 ρ=0.824（REDUNDANT-warn）。

**③ 六向**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：kline_daily 全市场 + kline_index 000300。外部：广度指标标准件=Advance/Decline 线族——Advance-Decl Ratio 定义（TradeStation 帮助文档，2025-01）https://help.tradestation.com/09_01/tradestationhelp/subsystems/elanalysis/indicator/advance_decl_ratio_indicator_.htm 与 Breadth of the Market（Macroption，口径综述）https://www.macroption.com/breadth-of-the-market/ → **两源一致**：外部主流为"涨家数−跌家数（净广度）或 A/D 比"，本仓用"上涨占比 up_ratio"（等价单调、且对停牌免疫性不同）→ 差异登记，A 股适配闸：涨跌停 10%/20% 与 ST 5% 使"占比"分布左偏，分位化处理已消化 |
| ②下游 | 内部：C3→指数；同时 C3_breadth 与 regime F4 ad_ratio（`market_features.ad_ratio`，399106 口径）**是两套广度实现**（一用 kline_daily 全市场、一用 399106 综指家数）→ 跨环节净新增发现：**广度双口径并存无对表件** |
| ③算法 | 外部：广度用于资产配置的研究件——Financial asset allocation strategies using statistical…（Applied Soft Computing / ScienceDirect 索引页，2025-06）https://www.sciencedirect.com/science/article/abs/pii/S1568494625005046 （单源，仅登记不入图） |
| ④后端 | 内部：无独立任务；断供面=kline_daily（在产）。外部：已查无 |
| ⑤前端 | 内部：情绪页成分卡 + 板块/市场宽度卡（`market_breadth_*` 件属 L03/L09）。外部：已查无 |
| ⑥数据字段 | 内部：pct_change/amount/turnover 在；质量画像=全市场日级完整（1991 起回放可用，但 1991-2018 为 237 只 stub 宇宙→分位不可比，B 册已记） |

**④ 缺口**：REDUNDANT C1×C3（在册）；**L02-C3-G1 广度双口径（kline_daily 占比 vs 399106 家数比）无对表/无单一供数件**——册内未见；**L02-C3-G2 stub 宇宙段的分位口径未打 universe_honest_ok 到情绪表（只打在 GPU 输入包）**——册内未见。

**⑤ 三态裁定**：G1=**施工 P2**（广度取数收敛一件，净 -1 读面；不改判据）；G2=**施工 P2**（把已有诚实标记列沿用到表侧，或登记"消费方必须自行截断 2019 前"）；REDUNDANT=挂起（降档与否属考试族）。

**⑥ 日志**：R1 内部行号+考试判档复核→signal；R2 内部广度双口径 grep→signal（净新增）；R3 外部 A/D 两源→signal；R4 外部广度择时学术件→noise（单源不可入图，归因=收费墙题录，只登记）。

**封矿判据**：六向封口 → **子类目封矿**。
