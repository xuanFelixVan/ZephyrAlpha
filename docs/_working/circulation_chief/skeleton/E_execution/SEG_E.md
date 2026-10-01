---
ttl: task_bound
title: S3 挖矿档·E 段执行基建链（F53-F58）——W3-2
session: st-ffchief-20261001
date: 2026-10-01
status: mined
---

# E 段·执行基建链（F53-F58）六向台账（W3-2 代码级核验）

> 方法：以代码为准，skeleton 为线索；每环节 ≥1 个 grep/运行态证据。证据路径均相对仓库根 D:\ZephyrAlpha。
> 段结论：6 环节全挖干（F58 本轮翻绿，见 F58.md）。段健康：黄→绿（唯一存疑位 F58 翻绿）。

## E-01(F53) 订单生命周期与预检

| 维度 | 台账 |
|------|------|
| 上游 | F41/F46（买卖点指令、卖出执行） |
| 下游 | F56（QMT 桥）/F57（对账） |
| 生产者 | `src/zephyr/ex_core/order_manager.py:140`（class OrderManager；:272 create_order；:338 submit_order）；`src/zephyr/ex_core/pre_execution_checker.py`（MOD-EX-024 四级闸门，经 `trading_session.attach_pre_execution_gate` 挂载——start_paper_session.py:4 依赖注记）；`src/zephyr/ex_core/price_cage.py`（264 行） |
| 消费者 | execution_engine.py、order_execution_saga.py、saga_session_orchestrator.py、rejection_action_handler.py、qmt_trading_session.py、trading_session.py、eod_reconciliation.py、frontend/dashboard/app_panel.py、scripts/start_paper_session.py、compliance/manipulation_realtime_monitor.py（grep -rln "order_manager import" 12 处命中） |
| 自动化态 | 事件（信号→订单流转）；paper 会话交易日 09:25 前人工拉起（start_paper_session.py:5） |
| 运行态 | `.runtime/logs/resource_samples/sch_paper_session.jsonl` 末样本 task_id=sch_paper_session pid=28496 elapsed=289.7s（采样文件 mtime 10-01 02:56）；`tmp/live_strategy_biz.heartbeat`（09-30 09:35） |
| 三态复核 | **挖干** ✅（骨架口径挖干(P0)维持；submit_order 内嵌 C-002 五闸挂点 :348，见 SEG_F F62） |

## E-02(F54) 打板执行族

| 维度 | 台账 |
|------|------|
| 上游 | F41（打板信号） |
| 下游 | F53（订单生命周期） |
| 生产者 | `src/zephyr/ex_core/daban_execution.py:59`（DabanExecutionAlgorithm；:121 DabanTimingDecision；:163 DynamicCapacityCalculator）+ daban_signal_decision / daban_exit_decision / daban_instant_circuit_breaker / daban_load_producer / daban_monitors / daban_pit_safety / daban_named_functions |
| 消费者 | pf_core/strategies/daban_sleeve_strategy.py、data/implementations/internal_compute_provider.py、akshare_provider.py、factor/auction_strength.py、ex_core/daban_pit_safety.py |
| 自动化态 | 事件（盘中打板信号）；c1_market.daban_engine_load 完整性日检 |
| 运行态 | `data/failures/20260929_integrity_check_c1_market.daban_engine_load_150117.json`（09-29 日检实跑；0918/0924/0928 同族在案） |
| 三态复核 | **挖干** ✅；漂移注记：骨架"六件套"，实数 ex_core 下 daban_*.py=**8 件**（计数漂移登记） |

## E-03(F55) 执行算法路由 SOR

| 维度 | 台账 |
|------|------|
| 上游 | F41/F46（订单）、F58（质量先验回写） |
| 下游 | F53（经选型的订单） |
| 生产者 | `src/zephyr/ex_sor/core/algo_execution_selector.py`（:116 OrderFeatures；:422 quality_prior_provider 注入；:528 先验消费）；`src/zephyr/ex_sor/core/broker_adapter_manager.py:207`（BrokerAdapterManager；:89-101 错误契约族）；REG-EXA 并入面=EXA-TWAP/VWAP/ICEBERG/IS/POV/ALT 六件经 TDM-E-L4-06 algo_refs 消费（trading_decision_map.yaml:2343-2344） |
| 消费者 | ex_sor/core/optimal_order_router.py、ex_sor/core/__init__.py；TDM L4-06 选型节点（module_ref=algo_execution_selector.py，module_id=MOD-XS-011） |
| 自动化态 | 事件（订单→拆单/场所/算法选择） |
| 运行态 | trading_decision_map.yaml:2332-2336 L4-06 注记"2026-09-27 起接执行质量反馈环：选型总分按 total*(1+0.20*(2q-1)) 调制" |
| 三态复核 | **挖干** ✅ |

## E-04(F56) QMT/miniQMT 桥

| 维度 | 台账 |
|------|------|
| 上游 | F53（订单） |
| 下游 | 券商通道→F57（回流水） |
| 生产者 | `src/zephyr/ex_core/adapters/miniqmt_broker.py:166`（MiniQmtBroker(BrokerInterface)，1401 行）；`src/zephyr/ex_core/qmt_trading_session.py:65`（QmtTradingSession，:121-129 装配 C-002 三闸）；`src/zephyr/ex_core/broker_link_probe.py:82`（BrokerLinkProbe，:51 LinkHealth） |
| 消费者 | scripts/start_paper_session.py（延迟 import miniqmt_broker）；scripts/construction/test_qmt_file_bridge_full.py；SimBridgeExecute 执行腿（scripts/backtest/sim_daily_runner.py:944-953，:1242 bridge_execute 主流程） |
| 自动化态 | 常驻（会话保活）；SimBridgeExecute=sch_sim_bridge_execute 计划任务 09:35/13:05 双时点（run_sim_bridge_execute_daily.ps1:76） |
| 运行态 | `.runtime/logs/sim_bridge_execute.log`：09-30 09:35:06 与 13:12:34 两跑 exited exit_code=0；10-01 09:35/13:05 "SKIP: non-trading day"（假日诚实跳过）。注记：sch_sim_bridge_execute 在 resource_profile_registry.yaml:2101 有登记但无 resource_samples 采样件（采样覆盖缺口，非断链） |
| 三态复核 | **挖干** ✅（骨架注"SimBridge 取证线索在案"——断腿已重建，取证档见 docs/_working/fullflow_chief_closeout/f56_simbridge_forensics.md） |

## E-05(F57) 结算对账与三方核对

| 维度 | 台账 |
|------|------|
| 上游 | F56（券商流水） |
| 下游 | F42（持仓体检）/F63（仓位对账） |
| 生产者 | `src/zephyr/trading/settlement_reconciliation.py`（:116 SettlementDrift；:83 ReconciliationConfig）；`src/zephyr/trading/three_way_reconciliation.py:111`（TradeFlow；:67 AnomalyClass）；`src/zephyr/ex_core/eod_reconciliation.py:95`（EodReconciler） |
| 消费者 | trading/broker_settlement_adapter.py、trading/recon_runner.py、scripts/run_post_settlement.py、trading/post_settlement_pipeline.py——boot_hooks.py:230-232 **事件订阅** post_settlement.recon.requested（宪法 §9.3 reconciler 事件触发合规） |
| 自动化态 | 定时盘后（sch_post_settlement）+ 事件触发双轨 |
| 运行态 | `.runtime/logs/resource_samples/sch_post_settlement.jsonl` 末样本 elapsed=47.4s（文件 mtime 09-30 00:18） |
| 三态复核 | **挖干** ✅ |

## E-06(F58) 执行成本反馈

| 维度 | 台账 |
|------|------|
| 上游 | F57（成交回报/对账） |
| 下游 | F55（选型回写）/F28（归因） |
| 生产者 | `src/zephyr/ex_sor/services/execution_quality_scorer.py`（575 行；ScorerBackedQualityPrior 适配器——algo_execution_selector.py:336 交叉引用）；先验闭环：algo_execution_selector.py:203/:212 quality_prior 字段、:339 provider 协议、:422-433 注入、:528 消费 |
| 消费者 | ex_sor/services/transaction_cost_optimizer.py、slippage_analyzer.py、algo_execution_selector.py（评分先验调制选型总分）；TDM-E-L4-14（module_ref=execution_quality_scorer.py，module_id=MOD-XS-018，trading_decision_map.yaml:2550-2561） |
| 自动化态 | 事件（盘后实测评分→次日选型先验；样本不足返 None 中性，禁假先验） |
| 运行态 | trading_decision_map.yaml:2551 note_confirmed 2026-09-27"T袋（全流通 F41）：断链已闭合、先验生产者落地"；tests/ex_sor/test_execution_quality_scorer.py 在（判别尺=反馈 3 新测+适配器 5 新测） |
| 三态复核 | **挖干（翻绿）**——骨架"存疑"过期：G4 回写选型缺已于 09-27 闭合，本轮代码级证实（quality_prior 注入+消费双端在码）。详见 F58.md |
