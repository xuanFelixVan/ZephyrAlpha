---
ttl: task_bound
completes_when: 周五 GPU 点火前 283 问全部有 outcome 后随总包归档
title: 总骨架挖矿台账——283 问五要素×三查矩阵（增补令#1）
owner: ZephyrAlpha-Owner
session: st-metaq-20260923
date: 2026-09-23
---

# 总骨架挖矿台账（增补令#1 第一优先件）

> 真源：PG meta_question 283 问｜源线谱=chain_piling_campaign/02_source_line_registry.md（29 线三档）｜PIT 闭卷切点=2025-09-09。
> 五要素=需要哪些表/字段口径/样本窗/消费方/判据可机检；三查=数据在库→口径清楚→判据可机跑（增补令#2）。机读版=[01_skeleton_ledger.json](01_skeleton_ledger.json)。

## 骨架判定总况

- **ready=275（可进答题）｜gap=8（先挖缺口）**
- 题型三类：因子效力问=84｜PIT纪律问=47｜管线挂接问=152

## 原料面探针（表级行数×时间窗）

| 库.表 | 行数 | 时间窗 |
|-------|------|--------|
| ch.adj_factor | 21,055,022 | 1990-12-19 ~ 2026-09-23 |
| ch.alt_shipping_index | 31,986 | 1988-10-19 ~ 2026-09-23 |
| ch.alt_stock_comment | 46,777 | 2026-09-11 ~ 2026-09-23 |
| ch.alt_sz_weather_warning | 10,020 | 无日期列 |
| ch.auction_book | 3,899,074 | 2026-07-21 ~ 2026-09-23 |
| ch.auction_snapshot | 266,363 | 2026-06-01 ~ 2026-09-23 |
| ch.block_trade | 1,426 | 2026-08-07 ~ 2026-09-23 |
| ch.commodity_futures_main | 153 | 2026-09-01 ~ 2026-09-23 |
| ch.commodity_spot_price | 918 | 2026-09-01 ~ 2026-09-23 |
| ch.concept_board | 750 | 无日期列 |
| ch.concept_board_constituent | 35,343 | 无日期列 |
| ch.crypto_kline_daily | 18,431 | 2025-08-08 ~ 2026-09-22 |
| ch.emotion_index | 8,647 | 1991-06-10 ~ 2026-09-23 |
| ch.execution_report | 1 | 无日期列 |
| ch.futures_warehouse_receipt | 2,909,109 | 2014-05-19 ~ 2026-09-23 |
| ch.hl_funding_history | 4,693,915 | 无日期列 |
| ch.hl_liquidation_raw | 5 | 无日期列 |
| ch.hl_oi_snapshot_daily | 1,170 | 2026-09-18 ~ 2026-09-23 |
| ch.hl_perp_snapshot_daily | 1,170 | 2026-09-18 ~ 2026-09-23 |
| ch.index_quote | 233,925 | 2026-07-14 ~ 2026-09-23 |
| ch.index_valuation_daily | 16,216 | 2010-01-04 ~ 2026-09-22 |
| ch.index_valuation_daily_quar_20260920 | 8,125 | 2010-01-01 ~ 2026-09-17 |
| ch.kline_30min | 49,107,016 | 2021-09-01 ~ 2026-09-23 |
| ch.kline_60min | 24,611,429 | 2021-09-01 ~ 2026-09-23 |
| ch.kline_daily | 10,102,587 | 1990-12-19 ~ 2026-09-23 |
| ch.kline_daily_hfq | 8,431,745 | 2015-01-05 ~ 2026-09-23 |
| ch.kline_index | 3,100,590 | 1990-12-19 ~ 2026-09-23 |
| ch.kline_sector | 96,982 | 2025-07-18 ~ 2026-09-23 |
| ch.kline_sector_880 | 443,380 | 2020-03-17 ~ 2026-09-23 |
| ch.macro_data | 59,753 | 1993-03-31 ~ 2026-09-23 |
| ch.market_breadth_snapshot | 145 | 2026-08-24 ~ 2026-09-23 |
| ch.market_china_bond_yield | 11,880 | 2025-09-23 ~ 2026-09-23 |
| ch.market_fund_flow_daily | 123 | 2026-03-27 ~ 2026-09-22 |
| ch.money_flow | 522,469 | 2026-06-01 ~ 2026-09-23 |
| ch.news_sentiment_window | 19,819 | 无日期列 |
| ch.sector_constituent_snapshot | 285,372 | 2026-09-14 ~ 2026-09-23 |
| ch.sector_fund_flow | 3,529 | 2026-09-15 ~ 2026-09-23 |
| ch.stock_daily_basic | 7,157,299 | 2021-01-04 ~ 2026-09-23 |
| ch.stock_hot_rank | 6,593 | 2026-08-04 ~ 2026-09-23 |
| ch.tick_data | 8,925,440,697 | 2025-01-02 ~ 2026-09-23 |
| ch.tick_depth_5 | 86,599,089 | 2026-07-24 ~ 2026-09-23 |
| ch.us_index | 22,630 | 1993-01-29 ~ 2026-09-22 |
| ch.weather_data | 10,033 | 无日期列 |
| ch3.balance_sheet | 339,738 | 1990-03-21 ~ 2026-09-02 |
| ch3.cashflow_statement | 310,447 | 1999-01-30 ~ 2026-09-02 |
| ch3.disclosure_plan | 316,739 | 2001-02-06 ~ 2026-08-31 |
| ch3.earnings_forecast | 125,582 | 1999-01-08 ~ 2026-07-03 |
| ch3.express_report | 28,708 | 2005-01-08 ~ 2026-07-02 |
| ch3.income_statement | 346,176 | 1995-01-05 ~ 2026-09-02 |
| ch3.irm_interactive_extracted | 74 | 无日期列 |
| ch3.irm_interactive_qa | 500 | 无日期列 |
| ch3.news_data | 8,155,360 | 无日期列 |
| ch3.shareholder_count | 514,091 | 1993-01-12 ~ 2026-09-23 |
| chb.alloc_budget_daily | 18 | 2026-09-15 ~ 2026-09-23 |
| chb.alloc_shrinkage_daily | 9 | 2026-09-15 ~ 2026-09-23 |
| chb.crisis_gate_log | 44 | 2026-07-17 ~ 2026-09-03 |
| chb.decision_daily | 69 | 2026-09-16 ~ 2026-09-24 |
| chb.hypothesis_precheck | 58 | 无日期列 |
| chb.node_verdict | 58 | 无日期列 |
| chb.regime_snapshot_history | 3,627 | 2019-04-01 ~ 2026-09-22 |
| chb.sim_trade_log | 67 | 2026-07-17 ~ 2026-09-23 |
| chb.strategy_screen | 1,340 | 无日期列 |
| pg.ig_chain | 873 | 2026-08-28 ~ 2026-09-14 |
| pg.ig_company_edge | 58,207 | 2026-08-28 ~ 2026-09-11 |
| pg.ig_edge | 1,726 | 2026-08-28 ~ 2026-09-14 |
| pg.ig_entity_code_map | 88 | 2026-09-17 ~ 2026-09-18 |
| pg.ig_equity_edge | 804 | 2022-12-31 ~ 2025-12-31 |
| pg.ig_fact | 264,072 | 2021-10-26 ~ 2021-10-26 |
| pg.ig_io_edge | 16,859 | 2020-12-31 ~ 2020-12-31 |
| pg.ig_node | 5,560 | 2026-08-28 ~ 2026-09-14 |
| pg.ig_node_company | 18,830 | 2026-08-28 ~ 2026-09-18 |
| pg.ig_product_revenue | 165,255 | 2021-10-26 ~ 2026-08-06 |
| pg.meta_question.meta_question | 283 | 无日期列 |
| pg.meta_question.meta_question_audit | 1,419 | 无日期列 |
| pg.meta_question.meta_question_exam_result | 287 | 无日期列 |
| pg.stock_concept | 61,053 | 2026-09-14 ~ 2026-09-14 |

## 缺口清单（verdict=gap，增补令#2 precondition_gap）

| q_id | 层 | 线 | 题型 | 缺什么 |
|------|----|----|------|--------|
| PQ-0025 | L1 | SL-A06 | 因子效力问 | 闭卷窗内零样本（候选表均始于 2025-09-09 之后） |
| PQ-0026 | L1 | SL-A06 | 因子效力问 | 闭卷窗内零样本（候选表均始于 2025-09-09 之后） |
| PQ-0125 | L1 | SL-A06 | 因子效力问 | 闭卷窗内零样本（候选表均始于 2025-09-09 之后） |
| PQ-0126 | L1 | SL-A06 | 因子效力问 | 闭卷窗内零样本（候选表均始于 2025-09-09 之后） |
| PQ-0127 | L1 | SL-A06 | 因子效力问 | 闭卷窗内零样本（候选表均始于 2025-09-09 之后） |
| PQ-0158 | L1 | SL-A06 | 因子效力问 | 闭卷窗内零样本（候选表均始于 2025-09-09 之后） |
| PQ-0161 | L1 | SL-A06 | PIT纪律问 | 闭卷窗内零样本（候选表均始于 2025-09-09 之后） |
| PQ-0163 | L1 | SL-A06 | 因子效力问 | 闭卷窗内零样本（候选表均始于 2025-09-09 之后） |

## ready 集合分波（挖干即开工）

- L0: 4 问 ready
- L1: 192 问 ready
- L2: 18 问 ready
- L3: 20 问 ready
- L4: 18 问 ready
- L5: 14 问 ready
- L6: 9 问 ready

## 答题纪律（增补令#5 诚实铁律内嵌）

- 因子效力问 fail 只认真实数据数字：『因子无预测力』→登记退役标记即闭环，禁改参数重跑（换卷作弊）；『数据缺失/管线断』→转 fail 大挖矿作业簿。两类区分写进作业簿。
- 全部结论带证据（查询原文+数字+窗口）；窗口一律 ≤ PIT 切点 2025-09-09。
- 主表状态机走合法边：registered→in_exam→answered（outcome 三态落 exam_result.outcome，主表不造新状态值）。
- JSONL 审计账 meta_question_audit.jsonl 全盘不存在（find 零命中）——PQ-0062/0102 双轨对账的既有事实考点，答题时如实记。