---
ttl: task_bound
title: "情绪涨停T0族数据用途挖矿作业簿"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
topic: fullflow_mine_20261001
---

# L06 车道：情绪/涨停/T0 信号族数据用途挖矿

> 方法论：onboarding_sop §9A 六问 + §9B 12 应用面 + mining_sop 六向寻路/自审闸三态。
> 实勘 2026-10-01，CH c1_market 只读（zephyr_reader）；census=data/runtime/consumption_census_ledger.json（读数 2026-09-30）。

## 0. 结论速览

实体 14（CH 13 表+分量 C1~C6 面新鲜 1 项）：10 鲜 / 3 断供 / 1 短史。已接线（tasks.yaml 有任务+代码有消费）=10；零消费成分=C1/C3/C4/C5/C6（census 五岛实证）；三断供=market_signal_history(09-04)、news_sentiment_window.symbol(08-20)、emotion_index.auction(09-23)。接线工单 8 条（top5 见 §4）。三态裁定=**挂起排期**（工单移交，本车道不施工）。

## 1. 实体清单（CH 实证：行数+max date+断供判定）

| 实体 (c1_market) | 行数 | max(date) | 判定 |
|---|---|---|---|
| emotion_index | 8,655 | 2026-09-30（close_final 溯 1991-06-10 replay 全史） | 鲜；但 auction stage 死档（17 行止 09-23，无任务） |
| ├ 分量 C1~C6 | — | 09-30（components JSON：C1/C2 w=0 insufficient obs19；C3~C6 w=0.25 ok） | 鲜；分量级零直读=census 五岛 |
| limit_up_pool | 1,276 | 2026-09-30 | 鲜 |
| limit_up_down | 5,162 | 2026-09-30 | 鲜 |
| market_breadth_snapshot | 165（24 日） | 2026-09-30 | 鲜但短史（08-24 起，盘中分钟） |
| market_signal_history | 329 | **2026-09-04** | **断供 27 天**：写侧仅 compute_signals/run_backtest 手动脚本 |
| news_sentiment_window | 19,824 | market 窗 09-28（缺 09-29/30）；**symbol 窗 08-20 死档 19,635 行** | **双断供**；nightly_sentiment 开关在（disabled flag 无，.bak 09-21 复启用） |
| alt_regime_signal | 10,864 | 2026-09-30 | 鲜；10 信号定义 8 在表：F10 暖机（hog_province_spot 09 起，130 obs 约至 2026-11）、F25 暖机（cb_premium 10 obs）、F7 台风死档（止 2018-11 源停采） |
| market_pattern_event | 31,895,820 | 2026-09-30 | 鲜 |
| market_pattern_win_rate | 4,251 | 2026-09-30 | 鲜（DAG 链随事件增量重物化） |
| market_pattern_certification | 68 | 2026-09-30 | 鲜（认证门严，设计使然） |
| daban_board_event | 3,106 | 2026-09-28 | 周窗滞后 by-design（tasks:1660 weekend_calibration），非断供 |
| daban_engine_load | 1,745 | 2026-09-28 | 同上（tasks:3441 依赖 derive） |
| sentiment_panel | 40 | 2026-09-30 | 鲜；fear_greed 30 obs + cb_premium 10 obs 双 metric 不同步 |

## 2. 逐实体六问矩阵（Q1 因子/Q2 策略/Q3 模块/Q4 环节/Q5 地图/Q6 盲点）

| 实体 | Q1 因子 | Q2 策略 | Q3 模块 | Q4 环节 | Q5 地图 | Q6 盲点 |
|---|---|---|---|---|---|---|
| emotion_index | 温度计 0-1+band5/band3 轴（t0_gpu_condition_pack:52） | regime 择时（condition_package）、板块偏好重映射 | sector_state_pipeline:59/109、aggregator、board_index_supply（共享 reader）、l9_readiness | close_final 日批 tasks:3471+pre_open tasks:3485 已挂；**auction 无任务** | TDM 大盘职能+emotion_index_skeleton_v0 | 分量 JSON 整读不拆用；obs<120 全指数暖机态至约 2026-11 |
| C1~C6 分量 | C1 涨停温度/C2 晋级率/C3 广度/C4 量能/C5 杠杆/C6 新闻=六因子候选 | 各自可挂择时/轮动卡（均未挂） | builder 内闭环；census 实证 C1/C3/C4/C5/C6 零直读 | 随母表两班 | 情绪线骨架 v0.2 | **算完就躺典型案**：c2 外五岛无一接线 |
| limit_up_pool | 连板高度/封单比/开板次数/一字率 | 打板接力族（STR-DABAN 系）、followthrough | sector_state_pipeline:25、deriver、ml_train/limit_up_classifier、intraday_l1_tracker | tasks:1646 已挂 | 涨停生态图/战争池 | 板块归属拆解 proxy 未回接（tracker:16 "表空"注释已 stale——数据已在） |
| limit_up_down | 涨跌停计数/炸板代理 | regime overlay（regime_feature_builder/overlay_signals_builder） | akshare_provider、sector_report_builder、api 目录 | tasks:1446 已挂 | 大盘情绪地图 | 与 pool 双源差异面未登记 |
| market_breadth_snapshot | breadth_ratio/涨跌家数比/涨停数（盘中） | L1 进攻证据代理（intraday_l1_tracker:40-44）、daily_plan | intraday_sentiment_loop、daban_load_producer、similar_day_inference | tasks:496 minute 已挂 | 大盘盘中状态 | 24 日短史无回补批次 |
| market_signal_history | 信号留痕（factor_composite_v1/strategy_weight） | framework_composer（pf_core）读 | api 信号两接口（api_server:1179）、signal_history_writer | **写侧零 tasks 挂钩=断供根因** | 回测留痕地图 | 写了没人读+没人定期写双向盲 |
| news_sentiment_window | C6 源（rule）；symbol 个股情绪因子（已断） | event_sentiment_adapter（pf_core） | nightly_sentiment 产、l9_readiness、calendar_coverage_checker | scheduler 服务班 08:20；09-29/30 缺 2 日 | 文本情绪面 | symbol 窗死 1.5 月无告警=盲点本体 |
| alt_regime_signal | F4/F7/F8/F10-12/F14-15/F23/F25 跨资产族 | regime overlay、F23 喂涨停情绪 | regime_data_loader、alt_source_bootstrap | tasks:2802 已挂 | 宏观/币圈/商品/猪价链地图 | F10/F25 暖机、F7 死档三态并存无标注册 |
| market_pattern_event | 形态×方向×regime 事件流 | candlestick_scanner、chart_condition_package | pattern_event_job/store、internal_compute_provider、api:4770 | tasks:3376 已挂+DAG | TDM 形态职能 | 31.9M 行大体量无分区查询审计 |
| market_pattern_win_rate | 前视命中率/前向收益 | pattern_win_rate_provider（MOD-SIG-115） | chart_cell_materializer、api:4819 | tasks:3395 已挂 | 形态证据地图 | —（链内闭环） |
| market_pattern_certification | shrunk_rate/wilson_lb/q_value 认证态 | 认证后形态方可引用（反过拟合 v1.0） | pattern_evidence_certifier | tasks:3408 已挂 | 证据认证地图 | 68 行=准入门严（设计） |
| daban_board_event | 触板/封板/开板/一字事件、C1/C2 源 | 打板四引擎（cohort_daily_ledger） | emotion builder、daban_load_producer、api | tasks:1660 周窗（T+1~T+4 滞后 by-design） | 打板/涨停生态图 | 周窗滞后 vs 日频消费者期望=契约未书面化 |
| daban_engine_load | 引擎负载复合（封板速度/板块涨停数） | STR-DABAN-022（daban_sleeve_strategy:99 PIT 真读铁律）、framework_composer | daban_load_producer 产 | tasks:3441 已挂 | 打板负载地图 | 周窗下 T 读 T-1 实为上周五，陈旧度无告警 |
| sentiment_panel | 恐贪/转债溢价中位分位 | F15/F25 源、crypto_universe_selector | sentiment_panel_provider | tasks:2779/2791 已挂 | 币圈/转债情绪地图 | 双 metric 生命周期不同步 |

## 3. 12 应用面逐格判定（●=适用+消费目标＝工单；○=不适用一句话）

| 族＼面 | 大盘 | 板块 | 个股 | 做T | 转债 | ETF/LOF | 期货商品 | 币圈 | 宏观择时 | 产业链 | 事件 | 文本 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 情绪指数族(温度计/news/sentiment_panel) | ●sector_state_pipeline | ●板块偏好重映射 | ●symbol 窗修复后（W-02） | ●band5 轴 t0_gpu | ●F25 | ○无对应标的情绪 | ●F11 | ●F14/F15 | ●regime overlay | ○情绪无链上传导面 | ●event_sentiment_adapter | ●C6/news |
| 涨停族(pool/down/daban) | ●breadth 计数 | ●板块拆解（W-03） | ●连板明细 | ●intraday_t0 连板/开板特征 | ○无涨跌停机制 | ○同左 | ○同左 | ○异市场 | ○非宏观源 | ○非链数据 | ●F23/daban_event | ○无文本维度 |
| 信号留痕族(signal_history) | ●api 信号接口 | ○无板块粒度 | ●factor_composite 个股信号 | ○无日内信号 | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 形态族(pattern 三表) | ○按 symbol 存 | ○ | ●形态事件个股查询 | ●timeframe 含日内窗 | ○ | ○ | ○ | ○ | ○regime_tag 仅切片 | ○ | ●形态触发=事件源 | ○ |
| 跨资产 regime 族(alt_regime) | ●大盘 regime | ○ | ○ | ○ | ●F25 转债偏好 | ○ | ●F10/F11 | ●F14/F15 | ●择时 overlay | ●猪价链 F11/F12 | ●F7/F8 | ○ |

## 4. 接线工单汇总（entity→消费者→动作）

| # | entity | 建议消费者 | 具体动作 | 类型 |
|---|---|---|---|---|
| W-01 | market_signal_history | compute_signals/run_backtest | tasks.yaml 登记日批挂钩，或册面登记 manual-only 语义（二选一裁决） | 代码接线/册面 |
| W-02 | news_sentiment_window(symbol+market) | nightly_sentiment 班 | 排障：symbol 窗 08-20 死档+market 窗 09-29/30 缺 2 日；修复后解 C6/个股情绪因子 | 代码接线 |
| W-03 | limit_up_pool→板块 | intraday_l1_tracker | 回接 stale proxy：`limit_up_pool×sector_constituent` 板块涨停拆解（注释"表空"已失效，数据 09-30 鲜） | 代码接线 |
| W-04 | emotion 分量 C1/C3/C4/C5/C6 | 面板/仪表盘 | components JSON 拆露为六分量时间序列；不接则 census 岛 defer 登记 | 册面+defer |
| W-05 | daban_engine_load 周窗滞后 | daban_sleeve 等日频消费者 | 周窗 T-1 实距语义书面化入任务描述+陈旧度告警 | 册面登记 |
| W-06 | emotion_index.auction stage | — | 09-23 死档无任务：判退役（stage 移除）或补任务；挂账待裁 | defer |
| W-07 | market_breadth_snapshot | 回补批次 | 24 日短史，挂 §9C 存量回补队列 | 挂账 |
| W-08 | STR-DABAN-022（census 零消费） | 组合层 | daban_sleeve 已接 load；策略下游组合级消费缺→defer 登记 | defer |

**top5 = W-01/W-02/W-03/W-04/W-05**（W-02 影响双数据断供最急）。

## 5. 六向台账（signal/noise/查无 记档）

- **signal①**：daban 链"断供"实为 weekend_calibration 周窗 by-design——排障误判风险解除，改立契约工单 W-05。
- **signal②**：alt_regime 10 定义 8 在表=暖机机制非故障（F10 130 obs/F25 250 分位），2026-11 自然出值。
- **signal③**：pattern 三表增量→胜率→认证 DAG 闭环在位，是本族接线最完整链（可作他链模板）。
- **signal④**：board_index_supply（st-boardidx-20260928）已把做T 6.1/6.2 与 C1/C2 登记消费者（CTR-P1-018）——C2 消费≠零的 census 侧写吻合。
- **noise**：intraday_l1_tracker "limit_up_pool 表空 0 行"注释（:16/:44）为 stale 情报，非真断供——归因：注释早于 pool 数据积累。
- **查无①**：涨停族×转债/ETF/期货/币圈/产业链 5 面查无（机制异市场，无挂点）——留痕。
- **查无②**：signal_history 除留痕/api 外无策略直连卡挂 data_refs——Q2 查无，工单 W-01 一并裁决。
- **查无③**：情绪族×产业链面查无（无 BOM 叶可挂）——留痕。

## 6. 自审闸三态（mining_sop §6）

**裁定：挂起排期（接线移交），本车道不施工、不封矿。**

- 理由①（终局有位）：族内 10/14 实体已接线在跑，pattern 链闭环+emotion 双班+regime overlay 均终局架构在位；工单 8 条全是"补最后一公里"非新建中间层。
- 理由②（时序未到）：W-04 分量拆露受全指数暖机期（obs<120，约 2026-11 满）压制，现在接面板吃到的是 insufficient 态——解锁条件=暖机满或 Owner 点名要先看分量。
- 理由③（不封矿）：六向有活矿（W-01~W-03 代码接线三条立即可做），矿脉未枯竭。
- 禁漏判检查：§9B 12 面逐格判定已落 §3，两态全留痕；census 五岛（C1/C3/C4/C5/C6）全部有出口（W-04 接或 defer），无静默岛。

## 附：证据锚

- CH 实勘 2026-10-01 zephyr_reader@c1_market（行数/max 见 §1，查询=本车道 tmp 脚本口径 count()+max(date_col)）。
- tasks.yaml=src/zephyr/data/config/tasks.yaml（行号见 §2/§4 引用）。
- census=data/runtime/consumption_census_ledger.json（emotion_component 5 岛+STR-DABAN-022+FCT-INTRADAY-*6+factor.ashare_intraday）。
- 关键代码：src/zephyr/data/sector_state_pipeline.py、src/zephyr/frontend/dashboard/api_server.py、src/zephyr/plan_engine/intraday_l1_tracker.py、src/zephyr/pf_core/strategies/daban_sleeve_strategy.py、src/zephyr/alt_data/{emotion_index_builder,alt_regime_signals,board_index_supply}.py、src/zephyr/ex_core/daban_load_producer.py、src/zephyr/signal_ashare/{sentiment,limit_up,intraday_t0,strategy_signal}/。
- 未挖长尾：FCT-INTRADAY-016~026 八岛（做T 因子卡零需求声明）属 strategy/factor 族车道，本簿仅记档不跨道开挖。

## 切换记录

- 2026-10-01 v1.0.0 初稿：14 实体实勘+六问矩阵+12 面判定+工单 8 条+三态裁定（挂起排期）。
