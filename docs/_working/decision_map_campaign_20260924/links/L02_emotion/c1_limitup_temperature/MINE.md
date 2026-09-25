---
ttl: task_bound
title: L02-C1 子类目挖矿簿 · 涨停温度成分（C1_limitup_temp）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成
---

# L02 · C1 涨停温度成分

**① 职责一句话**：用当日"触板家数 / 最高连板 / 封板率"三子项分位加权，量化场内打板热度。

**② 现状实测**：`emotion_index_builder.py:240-261`；子权重 touched **0.4** / max_consec **0.3** / seal_rate **0.3**（:249）；SQL `_SQL_LIMITUP_DAILY` :89-94（`count()`、`countIf(close_sealed=1)`、`max(consec_limit)`，源 `c1_market.daban_board_event` FINAL）；分位窗 250、`_MIN_OBS=120`。**原料实测（本册 CH 只读探针）**：daban_board_event **1,454 行 / 16 个唯一交易日 / 2026-09-01→09-22**（09-23、09-24 未见=DU-14 复断仍在），逐日 57/106/73/109/135/94 行（09-15→09-22）。活行 components 实测 obs=16 → status=insufficient → weight=0.0（当前不参与合成）。考试：卡 B 判 **INSUFFICIENT**（等史自然生长至 ~2027-03）。替代源 `limit_up_down` 实测 49 唯一日、max 09-24，只可替 touched（0.4 子项）。

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：daban_board_event（derive 任务）、limit_up_down、stk_limit（涨跌停价）。外部：**涨停三板指标口径一线成例**——连板天梯三日对照与晋级率页（lianban.net，2026-09-22 快照）https://lianban.net/tianti.html ；沪深 A 股涨停板特征统计（乐咕乐股 legulegu，2026-09-17）https://legulegu.com/stockdata/stock-day-limit → 两源交叉：均以"触板数/连板高度/封板率"为口径，**与本仓三子项一致，无需改造**（A 股适配闸天然通过，本就 A 股件） |
| ②下游 | 内部：emotion_index C1 → 板块偏好第二轴 / GPU 条件包五档。外部：已查无（消费方=本仓） |
| ③算法 | 内部：子项分位再加权（非原始值加权）→ 抗分布漂移。外部：已查无（查法：以"limit up board sentiment indicator quantitative China"检索，命中为复盘文非方法文） |
| ④后端 | 内部：无独立任务（随 builder 双任务）；**无 daban 断供哨兵**（09-23/24 静默缺 2 日实证）。外部：已查无 |
| ⑤前端 | 内部：情绪页六成分明细已呈现（web/pages/sentiment.html）。外部：已查无 |
| ⑥数据字段 | 内部：touched/sealed/max_consec 三字段在；**质量画像=16 日史、周窗内 2 日断供、行数日波动 57~135**（本册实测）→ 判"数据可得"当前不成立，属闸 4 GAP |

**④ 缺口清单**：G3（daban 断供，曾在册销口后**本册实测复断**）；DU-14 附注（在册）；**L02-C1-G1 连板高度/封板率无替代源，断供即成分退化为单子项**——册内未见；**L02-C1-G2 obs=16→120 的自然生长无人排期跟踪（预承诺时点约 2027-03，无触发器）**——与 L02-C07 同案。

**⑤ 三态裁定**：G3=**施工 P0**（复通 + 断供哨兵，销 DU-14）；G1=**挂起排期**（解锁=stk_limit 派生连板高度的备胎件评估，禁硬凑纪律在前）；G2=**施工 P2**（并入 C07 触发器一件，不另立）。

**⑥ 挖矿日志**：R1 内部：子权重与 SQL 行号 + CH 原料画像→signal；R2 外部：涨停口径两源→signal（口径一致，判"不改造"）；R3 外部：英文涨停情绪方法文→noise，归因=来源贫矿（复盘文为主）。

**封矿判据**：六向封口（含已查无+查法）→ **子类目封矿**。
