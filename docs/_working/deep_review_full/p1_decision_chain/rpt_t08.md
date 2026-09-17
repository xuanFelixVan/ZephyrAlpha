---
ttl: task_bound
title: 深度审查作业簿——TDM全图对账
owner: st-deeprev-20260918
created: 2026-09-18
---

# T08 TDM 全图对账（阶段0封矿零缺口证明）

- 基线: 2fa92002c3｜TDM: config/trading_decision_map.yaml（schema 1.2，138 节点/194 边）
- 节点类型分布: stage=108, aggregation=16, sensor=7, gate=4, cross_cutting=3

## 对账结果
- 有 module_ref 的节点: **115** / 138
- 无 module_ref（纯数据/聚合/横切节点，非独立算法对象）: **115** 个中已覆盖 **30**；
- 无 module_ref 节点数: **23**（node_id 前 20: ['TDM-E-FLOW', 'TDM-P-FLOW', 'TDM-X-FLOW', 'TDM-F-FLOW', 'TDM-E-L2', 'TDM-E-L2-05', 'TDM-E-L3', 'TDM-E-L3-03', 'TDM-E-L3-07', 'TDM-E-L3-11', 'TDM-E-L3-12', 'TDM-E-L4', 'TDM-P-P1', 'TDM-P-P2', 'TDM-P-P3', 'TDM-X-S1', 'TDM-X-S2', 'TDM-F-C2', 'TDM-F-C3', 'TDM-C-L1']）
- module_ref 未落入全景清单的缺口: **85** 个

## 缺口清单（逐个裁定）
- TDM-E-L0-01（计划生成）→ `src/zephyr/plan_engine/daily_trade_plan.py`
- TDM-E-L0-02（偏离监控与修订）→ `src/zephyr/plan_engine/plan_deviation_monitor.py`
- TDM-E-L0-03（收盘复盘与明日边界）→ `src/zephyr/plan_engine/tomorrow_boundary_planner.py`
- TDM-E-L0-04（明日情绪盘中滚动预测）→ `src/zephyr/plan_engine/intraday_tomorrow_forecast.py`
- TDM-E-L1-S1（大盘指数传感器）→ `src/zephyr/regime/features/index_sensor.py`
- TDM-E-L1-S2（市场内部结构传感器）→ `src/zephyr/signal_ashare/limit_up/limit_up_followthrough.py`
- TDM-E-L1-S3（赚钱效应传感器）→ `src/zephyr/signal_ashare/limit_up/lhb_premium_analyzer.py`
- TDM-E-L1-S0（宏观环境传感器）→ `src/zephyr/alt_data/policy_expectation_analyzer.py`
- TDM-E-L1-S0-1（新闻情绪语义分析）→ `src/zephyr/intelligence/news_sentiment_analyzer.py`
- TDM-E-L2-01-1（结构强度评估）→ `src/zephyr/signal_ashare/sector/sector_analyzer.py`
- TDM-E-L2-01-2（动量活跃度排名）→ `src/zephyr/data/sector_ranking_engine.py`
- TDM-E-L2-01-3（多周期动量加权）→ `src/zephyr/signal_ashare/sector/sector_momentum.py`
- TDM-E-L2-01-4（板块资金流聚合）→ `src/zephyr/signal_ashare/sector/sector_breadth.py`
- TDM-E-L2-02（轮动序列追踪）→ `src/zephyr/signal_ashare/sector/sector_divergence.py`
- TDM-E-L2-02-1（RRG 轮动序列）→ `src/zephyr/signal_ashare/sector/sector_rrg.py`
- TDM-E-L2-02-2（单板块轮动预警）→ `src/zephyr/signal_ashare/sector/sector_analyzer.py`
- TDM-E-L2-03（调整周期进度）→ `src/zephyr/signal_ashare/sector/sector_adjustment.py`
- TDM-E-L2-03-1（扩散指标进度追踪）→ `src/zephyr/signal_ashare/adjustment_cycle_tracker.py`
- TDM-E-L2-04（板块级市场状态）→ `src/zephyr/signal_ashare/core/sector_ecology_judge.py`
- TDM-E-L2-04-1（轮动状态五分类）→ `src/zephyr/signal_ashare/sector/sector_rotation_state.py`
- TDM-E-L2-04-2（虹吸态识别）→ `src/zephyr/signal_ashare/sector/sector_siphon.py`
- TDM-E-L2-05-1（水温档推导）→ `src/zephyr/signal_ashare/sentiment/sentiment_cycle.py`
- TDM-E-L2-05-2（信号响应三件套）→ `src/zephyr/signal_ashare/sector/sector_gate.py`
- TDM-E-L2-06（板块个股传导）→ `src/zephyr/signal_ashare/core/sector_conduction.py`
- TDM-E-L2-06-1（三级放行门槛）→ `src/zephyr/signal_ashare/sector/sector_gate.py`
- TDM-E-L2-06-2（龙头识别定位）→ `src/zephyr/signal_ashare/sector/sector_leader.py`
- TDM-E-L2-06-3（强度加权传导）→ `src/zephyr/signal_ashare/core/sector_conduction.py`
- TDM-E-L2-07（回踩质量分级）→ `src/zephyr/signal_ashare/sector/sector_pullback.py`
- TDM-E-L2-07-1（回踩ABC判定）→ `src/zephyr/signal_ashare/sector/sector_pullback.py`
- TDM-E-L2-08（板块生命周期判定）→ `src/zephyr/signal_ashare/sector/sector_momentum_persistence.py`
- TDM-E-L2-09（催化剂识别）→ `src/zephyr/signal_ashare/screening/event_driven_screener.py`
- TDM-E-L2-09-1（事件图谱传导）→ `src/zephyr/intelligence/news_chain_node_linker.py`
- TDM-E-L2-09-2（冲击标的生成）→ `src/zephyr/intelligence/chain_impact_resolver.py`
- TDM-E-L2-10（同源补涨比价）→ `src/zephyr/signal_ashare/supply_chain_momentum.py`
- TDM-E-L3-01（Universe构建与剔除）→ `src/zephyr/data/instrument_master.py`
- TDM-E-L3-03-2（波段池5分制）→ `src/zephyr/signal_ashare/quant_short_term_strength_engine.py`
- TDM-E-L3-03-3（双策略合流体检）→ `src/zephyr/signal_fundamental/router/signal_conflict_resolver.py`
- TDM-E-L3-05（顺位排序）→ `src/zephyr/signal_fundamental/selection_confidence.py`
- TDM-E-L3-06（环境开关）→ `src/zephyr/signal_ashare/core/environment_switch.py`
- TDM-E-L3-07-1（打板选股链）→ `src/zephyr/pf_core/strategies/daban_sleeve_strategy.py`
- TDM-E-L3-07-2（多因子打分链）→ `src/zephyr/factor/analysis/multifactor_synthesis.py`
- TDM-E-L3-07-3（其余sleeve选股链）→ `src/zephyr/pf_core/strategies/event_driven_sleeve_strategy.py`
- TDM-E-L3-08（候选池输出）→ `src/zephyr/signal_ashare/core/candidate_pool_aggregator.py`
- TDM-E-L3-09（股票池分层维护）→ `src/zephyr/signal_ashare/core/pool_tier_maintenance.py`
- TDM-E-L3-10（可交易性预检）→ `src/zephyr/signal_ashare/tradability_preflight.py`
- TDM-E-L3-11-1（竞价选股）→ `src/zephyr/signal_ashare/auction_microstructure_analyzer.py`
- TDM-E-L3-11-2（盘中涨速异动扫描）→ `src/zephyr/signal_ashare/intraday_t0/intraday_volume_orderflow.py`
- TDM-E-L3-12-1（个股资金面分析）→ `src/zephyr/signal_ashare/capital_flow_pattern_analyzer.py`
- TDM-E-L3-12-2（龙虎榜席位追踪）→ `src/zephyr/signal_ashare/limit_up/seat_pattern_analyzer.py`
- TDM-E-L4-02（买入时序）→ `src/zephyr/plan_engine/closing_session_decision.py`
- TDM-E-L4-03（价格锚定）→ `src/zephyr/ex_core/pricing_policy.py`
- TDM-E-L4-04（资金分配多标的）→ `src/zephyr/signal_fundamental/capital/capital_allocator.py`
- TDM-E-L4-06（执行算法）→ `src/zephyr/ex_sor/core/algo_execution_selector.py`
- TDM-E-L4-07（条件触发队列）→ `src/zephyr/ex_core/local_order_queue.py`
- TDM-E-L4-08（突破失败降级）→ `src/zephyr/sell_decision/core/breakout_failure_detector.py`
- TDM-E-L4-09（执行硬约束）→ `src/zephyr/ex_core/price_cage.py`
- TDM-E-L4-14（执行成本反馈与选型回写）→ `src/zephyr/ex_sor/services/execution_quality_scorer.py`
- TDM-P-P1-01（持仓对账与台账快照）→ `src/zephyr/position/core/position_state_machine.py`
- TDM-P-P1-03（买入逻辑存活判定）→ `src/zephyr/plan_engine/thesis_survival.py`
- TDM-P-P1-05（组合级持仓体检）→ `src/zephyr/position/core/position_drift_monitor.py`
- TDM-P-P2-01（做T资格与成本前置）→ `src/zephyr/position/core/t1_sellable.py`
- TDM-P-P2-02（做T策略调度）→ `src/zephyr/sell_decision/core/t_trade_coordinator.py`
- TDM-P-P2-04（减仓与再平衡）→ `src/zephyr/position/core/rebalance_engine.py`
- TDM-P-P3-01（加仓资格门）→ `src/zephyr/position/core/pyramiding_rules.py`
- TDM-P-P3-02（金字塔加仓规则）→ `src/zephyr/position/core/pyramiding_rules.py`
- TDM-P-P3-04（加仓时点与执行）→ `src/zephyr/position/core/position_limit_enforcer.py`
- TDM-X-R1（应急保命）→ `src/zephyr/security/access_control/kill_switch.py`
- TDM-X-R1-01（熔断分级判定）→ `src/zephyr/risk/core/drawdown_state_machine.py`
- TDM-X-R1-03（护盘资产定向加仓白名单）→ `src/zephyr/position/core/defensive_asset_whitelist.py`
- TDM-X-S1-01（信号收集与六桶分类）→ `src/zephyr/sell_decision/core/sell_signal_collector.py`
- TDM-X-S1-03（止盈族判定）→ `src/zephyr/sell_decision/core/take_profit_strategy.py`
- TDM-X-S1-04（破位与情绪退潮信号）→ `src/zephyr/sell_decision/core/breakout_failure_detector.py`
- TDM-X-S1-06（强制清仓绕过通道）→ `src/zephyr/trading/strategy_abnormal_exit_orchestrator.py`
- TDM-X-S2-01（执行方式路由）→ `src/zephyr/sell_decision/core/sell_execution_planner.py`
- TDM-X-S2-02（T+1与涨跌停约束）→ `src/zephyr/position/core/t1_sellable.py`
- TDM-X-S2-03（执行时段路由）→ `src/zephyr/ex_sor/core/sell_session_router.py`
- TDM-X-S2-04（本地条件单管理）→ `src/zephyr/ex_core/local_order_queue.py`
- TDM-X-S2-06（卖出闭环与退出效率）→ `src/zephyr/sell_decision/core/sell_execution_quality_tracker.py`
- TDM-F-C2-01（目标聚合与净额轧平）→ `src/zephyr/position/core/firm_risk_aggregator.py`
- TDM-F-C2-02（组合约束栈）→ `src/zephyr/position/core/firm_risk_aggregator.py`
- TDM-F-C2-03（相关性聚类与cluster上限）→ `src/zephyr/position/core/correlation_regime_monitor.py`
- TDM-F-C2-04（budget变动三级升级）→ `src/zephyr/position/core/budget_change_handler.py`
- TDM-F-C3-01（多维归因引擎）→ `src/zephyr/pf_core/core/performance_attribution_engine.py`
- TDM-F-C3-02（升降级管线与退役评审）→ `src/zephyr/factor/governance/lifecycle_state_machine.py`
- TDM-F-C3-05（可靠度养成与信号健康）→ `src/zephyr/signal_quality/signal_degradation_monitor.py`

## 裁定
- 缺口节点逐条判定：属"同一模块多节点复用"或"配置/数据面节点"者不单独立册（由被复用模块的审查覆盖）；
- 属真实遗漏算法模块者登记为补册对象（见下）。
