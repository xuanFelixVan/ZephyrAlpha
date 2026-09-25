---
ttl: task_bound
title: L01-S2 子模块挖矿簿 · overlay 覆盖层与八转换评分引擎（r10/r11/r12）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（六向封口，逐行公式对表余量如实记 §6）
---

# L01 · S2 overlay 覆盖层与转换评分引擎

**① 职责一句话**：在 HMM 四态之上用规则评分引擎叠加三个危机/复苏/突破 overlay 态（r10/r11/r12）与 8 条转换通路的分维打分，负责"HMM 看不见的结构性事件"。

**② 现状实测**

| 件 | 行数 | MATURITY | 关键实测 |
|---|---|---|---|
| `src/zephyr/regime/overlay_signals_builder.py` | 850 | production（头注 :7） | `_TRANSITION_DIMS` :95 起：S1=4 维 / S2=13 维（含 breadth_thrust V 反转析取）/ T1=3 维 / T2=1 维 / T3=7 维…；`build_for_date` :195；`_warn_threshold_ledger_debt` :228/:253（阈值债出声）；`_compute_vix_pct` :602；`_compute_t3_inputs` :677；`_compute_sector_metrics` :733；`_compute_limit_up_metrics` :763 |
| `src/zephyr/regime/features/overlay_features.py` | 1,383 | production（:7） | 35 个评分函数，命名即通路：s1_vix_panic:168 / s1_correlation:205 / s1_liquidity:232 / s1_flash_recover:252 / s2_capitulation:291 / s2_vix:506 / s2_wyckoff:537 / s2_valuation:571 / s2_valuation_score_fundamental:598 / s2_fund:651 / s2_spring:727 / s2_three_yang:796 / s2_breadth_thrust:887 / s2_break_sc_low:926 / s2_vix_new_high:937 / s2_fund_outflow:948 / t1_bqs:967 / t1_rcs:986 / t1_frs:1004 / t2_continue_decline:1028 / t3_volume_price:1045 / t3_ma_trend:1063 / t3_sentiment:1085 / t3_money_effect:1102 / t3_mainline:1137 / t3_leader:1172 / t3_one_day_mainline:1202 / t4_shrink_flat:1230 / t5_leader_break:1248 / t5_rebound_wrap:1283 / t6_sudden_volume:1302 / s2_policy:1320 / s2_bad_news_flat:1354 |
| `regime_detector.py` 融合段 | — | — | TRANSITION_CONFIG 阶段配置（trigger/confirm/strong_confirm 三段）、`_merge_probabilities` 压缩 HMM 质量、危机期门控（overlay 仅在 #1<1.0 生效） |
| 生产触发面 | — | — | 无独立排班：随 S6 印教材链逐日 `build_for_date(dt)`；**盘中实时触发面缺位**（8 转换无盘中评分任务，tasks.yaml 实测仅 anchored_state_build:647 / alt_regime_signal_refresh:2783 两条 regime 系任务，无 overlay 盘中槽） |
| 测试面 | — | — | `tests/regime/test_overlay_features.py`、`test_overlay_signals_builder.py`、`test_overlay_signals_builder_valuation.py`（实测在册） |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：合成 VIX / Wyckoff FSM / LPPL / 广度乖离 / 板块 HHI / 连板晋级（S3 供数件，另册）+ kline_index 四指数 + money_flow + sector_kline + limit_up_down + news_sentiment + index_valuation。hk_connect_flow 永久退役→NaN→0 降级（tasks.yaml:209）。外部：危机/赶顶识别外部候选=LPPLS 族，"Identifying and Quantifying Financial Bubbles with the Hyped Log-Periodic…"（arXiv 预印本，2025-10-13）https://arxiv.org/html/2510.10878v1 ；LPPLS 两百年 S&P 指标（Physica A / ScienceDirect，2016-09）https://www.sciencedirect.com/science/article/abs/pii/S0378437116301017 |
| ②下游 | 内部：P_overlay(r10/r11/r12) 取各转换最高分→`_merge_probabilities`→S5 Shrinkage→S6 落库→全消费面。外部：已查无（查法：以"regime overlay consumption portfolio risk"检索未见新可入图件；下游面已在 S10 册实测 24 文件） |
| ③算法 | 内部：三段确认（trigger/confirm/strong_confirm）+ keys_or_gte 析取=防单维误触发。外部：波动率管理/波动目标作为危机缩额机制的行业实证——"波动率目标：趋势的另一种形式"（腾讯财经转载，2025-09-19）https://new.qq.com/rain/a/20250919A04Z9100 、"Volatility-Managed Portfolios"（期刊摘要镜像 alljournals，2024-12）https://economy.alljournals.cn/view_abstract.aspx?aid=C0AA8CB0927F7510A298847FF5ED4F80 （Moreira-Muir 系，两源跨验通过；本仓对应现役件=volatility_regime_alerter/squeeze_breakout，见 S3 册） |
| ④后端 | 内部：`_warn_threshold_ledger_debt` 明示"阈值债"有登记但**阈值账本文件未在仓内定位**（本册 grep 全仓未寻得该账本落盘件）→ 缺口。外部：LPPLS 有现成开源实现可复用——`Boulder-Investment-Technologies/lppls`（GitHub，2020-04）https://github.com/Boulder-Investment-Technologies/lppls 、R 包 `sabato96/lppls`（GitHub）https://github.com/sabato96/lppls （许可证本册未核验，登记为采纳前置核验项，禁虚构） |
| ⑤前端 | 内部：转换触发记录（stage 四态）现只随快照 probs_json 出，无独立呈现面；仪表盘仅呈现 7 态概率。外部：已查无（呈现惯例=状态卡，无新点） |
| ⑥数据字段 | 内部：T3 通路需 sector_hhi/top_sector_pct/max_consec/promotion_rate/ad_ratio/inflow_pct——**连板晋级与板块集中度现只在盘后口径可用**（D2/D3 family 级无 FCT 条目，需求册在册）；policy/bad_news 两维需新闻分类。质量画像：limit_up_down 实测 49 个唯一交易日、max 2026-09-24（本册 CH 只读探针）→ 深史不足是硬约束，非字段缺失 |

**④ 缺口清单**

| 编号 | 内容 | 册内出处 |
|---|---|---|
| D2/D3 | 涨停/炸板/连板梯队 family 级无 FCT 条目 → T3 money_effect/leader 维原料受限 | 需求册沿用 |
| L01-S2-G1 | **阈值债账本未落盘**：`_warn_threshold_ledger_debt` 出声但全仓寻无阈值账本文件，35 维评分阈值散在代码常量 | 册内未见 |
| L01-S2-G2 | **盘中 overlay 触发面缺位**：8 转换只日级出数，r10/r12 型事件（跳水/突破）盘中不可见 | 册内未见 |
| L01-S2-G3 | LPPL/Wyckoff/evolution 供数件零外部调用（另册 S3 实测：lppl_detector/evolution_signals/chip/index_sensor 全仓 import 计数=0） | 册内未见 |

**⑤ 自审闸三态裁定**

| 缺口 | 裁定 | 理由 |
|---|---|---|
| D2/D3 | 挂起排期 | 解锁条件=连板梯队明细 DDL（GAP-F-13）落地；终局要（无源不成像） |
| L01-S2-G1 | 施工（P2） | 阈值无账本=每次调参都需人工通读 1,383 行，直接违反终局"一切可自动化"；净零：账本并入既有规则 YAML，不新建 gate |
| L01-S2-G2 | 挂起排期 | 终局要盘中危机识别，但解锁条件=盘中数据链（kline_sector_intraday 真值腿，另见 L03-B1 册）+ 触发成本实算；**反驳者一问**三条"不该做"：①盘中评分抖动→假危机信号污染门（真实）②现役危机门是日级语义，改盘中=改判据（禁止）③分钟链尚在建设中（真实）——故挂起而非施工 |
| L01-S2-G3 | 施工（并入 S3 册 C 项） | 零消费件按宪法 §4.2 判据走"退役/接线"二选一，禁继续挂着 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | noise 归因 |
|---|---|---|---|
| R1 | 内部：_TRANSITION_DIMS + 35 函数全清单行号 | signal | — |
| R2 | 内部：阈值账本寻文件 | signal（判"无落盘件"） | — |
| R3 | 外部：LPPLS 论文 + 开源实现 | signal（2 件带 URL+年份；license 未核） | — |
| R4 | 外部：波动率管理两源 | signal（跨验 2 源） | — |
| R5 | 外部："overlay consumption"检索 | noise | 归因=查询词偏组合层、本层本就无外部消费惯例可引 → 改判"已查无" |
| R6 | 外部：盘中危机识别（BOCPD 族） | 沿用 SKEL §14.2（ruptures/bocd 等 6 件带 URL），本册不重复收录 | 净零 |

**本册封矿判据**：六向封口（含已查无+查法）；未挖长尾=35 维评分函数的**公式级逐行对表**（约 1,383 行，属施工级而非挖矿级余量，已随 S2/S3 册挂施工项）→ 子模块**封矿**，余量以施工清单形式移交。
