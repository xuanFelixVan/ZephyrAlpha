---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_14_pp_plan.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-14 组合与预算 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/trading_decision_map.yaml nodes[layer∈{C1,C2}]（1+5=6，portfolio_flow 前段；C3 归因反馈归 ENV-16）+ portfolio_plan（PP-001）；骨架=01_skeleton_environments.md §2-丙
- **职责一句话**：C1 总预算切给各 sleeve（Millennium pod 单体版，状态分布加权插值非查表）→C2 各 sleeve 信号/持仓聚合成组合净指令（净额轧平/约束栈/相关性 cluster 上限/budget 三级升级）
- **节点清单（6）**：C1 预算切分(gate,multi_strategy_capital_allocator)｜C2 组合聚合(structural)｜C2-01 目标聚合与净额轧平(firm_risk_aggregator)｜C2-02 组合约束栈(firm_risk_aggregator 同件)｜C2-03 相关性聚类与 cluster 上限(correlation_regime_monitor)｜C2-04 budget 变动三级升级(budget_change_handler)
- **图面状态**：confidence proposed=5 / untested=1；activation premarket1/continuous5；red_reason：F-C2 structural；**PP-001「整装仿真组合 V0」confidence=proposed**：16 sleeves（default-equity 0.126、multifactor 0.126、daban 0.0945、eventdriven/topn/intraday 各 0.063、orderbook/vwap 各 0.04725、STR-VREV-025 0.045 等，部分带 activation_state 门），aggregator={max_total_position:1.0, max_single_sleeve:0.25, correlation_cap:0.7}

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 外部 | 判定 |
|---|---|---|---|
| ①上游 | 图内 IN 3 边：L1-AGG→C1（状态插值进预算）、F-C3-03 sleeve 调权回喂 C1、X-R1 应急→C2-01（保命直改组合目标）。物质上游=PP-001 sleeves 清单（TDM portfolio_plan，生成器产物 fw-tdm-current：config/framework_plans.yaml:235「当前挂图 PP-001，sha12=d8d65f0e8b53」，plan_ref: PP-001:296） | pod 预算切分+组合约束栈（总仓/单 pod 上限/相关性帽）为多经理平台标配形态 | signal |
| ②下游 | 图内 OUT 3 边：C2→C3 归因（ENV-16）、C2-01→L4 买入执行、C2-01→X-S2-01 卖出执行——组合净指令是买卖两层的共同源头。grep 消费方：src/zephyr/pf_alloc/allocation_orchestrator.py+batched_position_builder.py、signal_ashare/strategy_signal/signal_weight_adjuster.py、plan_engine/boundary_revision_engine.py、strategy_pipeline/daily_gate_snapshot.py、risk/core/adaptive_risk_monitor.py、position/core/single_name_cap_caliber.py+strategy_book.py；日循环挂点：pf_alloc_rebalance_check 槽（trading_day_cycle_map.yaml:4331/4465/5026）+allocation_inputs.py:206（:2486） | — | signal |
| ③算法机制 | C1=状态分布加权插值切预算（非查表，图 decision_question 原文）+多策略资本分配器（pf_alloc/core/multi_strategy_capital_allocator.py）；C2-01/02 净额轧平+约束栈（position/core/firm_risk_aggregator.py 一件两节点）；C2-03 相关性体制监测（correlation_regime_monitor.py）；C2-04 budget 三级升级（budget_change_handler.py）；sleeve 权重回喂=regime_meta_allocator.py（归 ENV-16 域） | — | signal |
| ④后端代码 | 5/6 节点挂 4 个去重 module_ref 全在盘（firm_risk_aggregator 一件挂 C2-01/02 两节点；唯一无码=C2 族头 structural）。tests/：tests/pf_alloc/{test_multi_strategy_capital_allocator,test_regime_bma_weighting,test_batched_position_builder}.py、tests/position/test_budget_change_handler.py；PP-001 sleeves 16 策略 ref 中 pf_core 策略件在盘（src/zephyr/pf_core/default_equity_strategy.py+strategies/{daban,multifactor}_sleeve_strategy.py）、STR-VREV 系登记于 pf_alloc/allocation_config.py+scripts/backtest/sim_paper_ledger.py | — | signal |
| ⑤前端呈现（只登记） | dashboard/api_server.py+web/features/backtest/bt-engine.js（sleeve/组合读出面，grep 命中 sleeve 名） | — | signal（登记） |
| ⑥数据字段 | data_refs：本切片 6 节点 data_refs 为空（已查无）——组合层输入是各 sleeve 信号/持仓面而非原始表，字段链经 C2-01 聚合面承接；budget 台账经 budget_change_handler+strategy_book | — | 空缺登记 |

## §2 挖干自评

- **三扫收敛?** 收敛。消费方轮证实组合净指令双下游（L4/X-S2-01）与日循环 rebalance 槽实接，此后归零。
- **未挖长尾**：(a) 16 sleeves 逐 sleeve 的 strategy_ref→策略件对位表（3 件已证，余 13 待逐个核——含 STR-MOMTREND-033/STR-VREV-026/027 等注册面）；(b) C2-04 三级升级的阈值表与升级动作对应；(c) correlation_cap 0.7 与 correlation_regime_monitor 阈值的一致性核对。
- **🌑不可得**：①PP-001 权重和校验（16 sleeve 权重是否归一，本批未算——生成器产物以 sha12 为准不手算）；②整装仿真的历史跑批证据（proposed 状态、sim 腿未跑）。

## §3 挖后自审闸三态裁定

**挂起排期——PP-001 proposed→整装仿真施工令缺口**

- 理由：实现面成立（4 件码+4 件测试+日循环 rebalance 槽实接），但 PP-001 全案停 proposed：16 sleeves 多数 activation_state 未挂、整装仿真 V0 未跑、C1/C2 无一 verified。组合层是全决策链的"总装车间"，其激活前提恰是 ENV-08 状态机（插值输入）与 ENV-11/13 执行双腿（净指令出口）先动——它天然排在激活链最后一环，提前施工=总装上线而零件未验。按纪律挂起排期。
- 施工令候选（解锁后顺位）：①整装仿真 V0 跑批（scripts/backtest/sim_paper_ledger.py 已有登记面，补 16 sleeve 对位与跑批闸）②C2-04 三级升级阈值表落册 ③C1 插值参数考试。
- 解锁条件：ENV-08 state_matrix 激活（插值输入就位）+ENV-11/13 sim 腿通过+Owner 对 PP-001 升 verified 的门位裁定；C3-03 调权回喂由 ENV-16 批次施工，本簿只收 C1/C2。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：C1/C2 六节点切片+PP-001 全案（16 sleeves/aggregator 三帽） | signal | proposed 单态确认；fw-tdm-current 生成器产物锚（sha12=d8d65f0e8b53） |
| 2 | 代码轮：4 module_ref+sleeve 策略件+STR-VREV 注册面核验 | signal | 全在盘零失踪；sleeve 16 中 3 件策略码在盘已证 |
| 3 | 消费方轮：allocation_orchestrator/firm_risk/day-cycle 反查 | signal | 双下游净指令锚+rebalance_check 槽三处+data_refs 空缺登记 |
