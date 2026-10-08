---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_08_market_state.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-08 市场感知与状态判定 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/trading_decision_map.yaml nodes[layer∈{L0,L1}]（5+10=15）+ state_matrix（6 态×4 节点=24 cells）；骨架=01_skeleton_environments.md §2-丙
- **职责一句话**：L0 盘前作战计划闭环（生成→偏离监控→复盘定界→明日预测）+ L1 大盘总闸（8 传感器→锚定状态机判 6 态），总闸输出广播全四流
- **节点清单（15）**：L0 盘前作战计划(gate)｜L0-01 计划生成｜L0-02 偏离监控与修订｜L0-03 收盘复盘与明日边界｜L0-04 明日情绪盘中滚动预测｜L1 大盘总闸(gate,critical,verified)｜L1-S1 指数传感器｜L1-S2 涨停跟进结构｜L1-S3 赚钱效应/LHB 溢价｜L1-S4 合成VIX｜L1-S0 宏观环境｜L1-S0-1 新闻情绪语义｜L1-S5 日级市场条件｜L1-AGG 市场状态判定(aggregation,critical)｜TDM-C-L1 币圈总闸(not_built)
- **图面状态**：confidence proposed=13 / verified=1（L1）/ untested=1；activation premarket8/intraday4/postmarket1/continuous2；critical=L1+L1-AGG；state_matrix 24 cells confidence 全 proposed

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 外部 | 判定 |
|---|---|---|---|
| ①上游 | 图内 IN 11 边：F-C3-01/04 归因与校准回喂 L0、F-C3-05/01→L1-AGG、L2-09-2→L0-02、L9-G4/G5→L1-AGG/S0、L9-V1→L0-01、L9-E2→L0、L9-A09→S0-1——总闸被反馈环与知识供给双向喂 | 状态机六态划分（capitulation→distribution）对位 Wyckoff/情绪周期相位说，非仓内独创 | signal |
| ②下游 | 图内 OUT 18 边：L1-AGG 广播 8 流（L2-05-1 水温、L2、P-P1、P-P3-01、P-P2-01、X-S1、X-S1-04、F-C1 预算切分）——全图唯一"一节点喂四流"的枢纽。grep 消费方：src/zephyr/autonomy_core/module_factory/module_mapper.py、backtest/regime_validation/chart_condition_package.py+shrinkage_provider.py、experiment_tracking/adapters/regime_adapter.py、factor/analysis/bma_signal_weighter.py、frontend/dashboard/api_server.py | — | signal |
| ③算法机制 | 锚定状态机（src/zephyr/regime/core/anchored_state_machine.py，6 态）；合成VIX（regime/features/synthetic_vix.py）；涨停跟进（signal_ashare/limit_up/limit_up_followthrough.py）；LHB 溢价（limit_up/lhb_premium_analyzer.py）；政策预期（alt_data/policy_expectation_analyzer.py）；新闻情绪（intelligence/news_sentiment_analyzer.py）；L0 五件套管线 daily_warroom_pipeline→daily_trade_plan→plan_deviation_monitor→tomorrow_boundary_planner→intraday_tomorrow_forecast（均在 src/zephyr/plan_engine/） | — | signal |
| ④后端代码 | 14/15 有码全部在盘（唯一无码=TDM-C-L1 币圈，not_built 域外）。tests/：tests/legacy_zephyr/regime/test_anchored_state_machine.py、tests/fle/test_fle_regime_detector.py、tests/plan_engine/{test_warroom,test_daily_loop_master_switch,test_intraday_l1_tracker,test_judgment_settler,test_next_day_forecaster}、tests/frontend/test_warroom.py | — | signal |
| ⑤前端呈现（只登记） | src/zephyr/frontend/dashboard/components/warroom.py（作战室）、web/index.html、api_server.py regime 读出面 | — | signal（登记） |
| ⑥数据字段 | data_refs=DS-150/082/107/098/108/059；state_matrix 24 cells 挂载 9 策略：STR-VREV-025/026/027、STR-DABAN-023、STR-MOMTREND-033、daban-sleeve、intraday-surge-fall、orderbook-imbalance、vwap-reversion（cells 结构 node_id×state→mounted+confidence） | — | signal |

## §2 挖干自评

- **三扫收敛?** 收敛。代码轮证实 14/15 有码且测试在盘；消费方轮新增 module_mapper/regime_adapter/bma 三处下游，之后归零。
- **未挖长尾**：(a) 8 传感器逐个 freshness/打卡读数（本批禁直查 DB，实查待施工批）；(b) state_matrix→L1-AGG 的 cells 读取接线是否存在代码证据（已查无直接消费 cells 的模块，待验证）；(c) L1-S2 与 S5 对 limit_up 族的双传感器职责切分细化。
- **🌑不可得**：①24 cells 全 proposed 的激活闸门在谁的 flag 上（生产翻转属 Owner 门位，非挖矿可得）；②L0-04 明日情绪预测的历史命中率台账（无归因面证据）。

## §3 挖后自审闸三态裁定

**挂起排期（激活与接线两缺口）**

- 理由：实现面成立（代码+测试在盘、L1 唯一 verified），但图语义里"cells 挂载策略随状态激活"这条主干无代码消费证据（mounted 字段已查无读取方）——典型"图语义→代码施工令"缺口；且 24 cells/9 策略全 proposed，激活升 verified 需 sim 腿先跑+Owner production 门位，非施工可独解。币圈 C-L1=not_built 外域，随 ENV 币圈线另议，本簿不收。
- 解锁条件：①cells 消费接线施工令（L1-AGG 读 state_matrix 挂载表并输出 activation 指令）；②PP-001 整装仿真（ENV-14）跑通后 Owner 门位把 cells 逐态升 verified。
- 挂起期间 L1 总闸单机读面（regime_detector 直读）不得删改——它是唯一 verified 锚。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：L0/L1 15 节点+state_matrix 24 cells 结构切片 | signal | 6 态×4 节点（L1/L4/P-P2/F-C1）矩阵；9 挂载策略清单；L1 全场唯一 verified |
| 2 | 代码轮：regime+plan_engine 九模块真身与测试核验 | signal | 14/15 有码零失踪；anchored_state_machine 测试在 legacy_zephyr（历史件，非 tests/regime 专目录） |
| 3 | 消费方轮：regime_detector/anchored_state_machine 全 src 反查+cells 读取方反查 | signal | 6+ 下游文件；cells 无消费方=挂起裁定核心证据（待验证留档） |
