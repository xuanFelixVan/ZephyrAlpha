---
ttl: task_bound
title: D 段·交易决策消费链 TDM 四流 16 环节六向挖矿档（S3 W3-1）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
creation_token: seg-d-tdm-fourflow-w31-20261001
---

# SEG_D · 交易决策消费链（TDM 四流，D-01..D-16，16 环节）代码级核验

> 总体结论：主链 F37-F50 挖干判定全部维持，且每环均有消费者 grep 实证。**路径漂移 6 处**（skeleton 锚过期，文件均在、目录改名）：selection_funnel/negative_veto→signal_fundamental/、t_trade_coordinator/sell_execution_planner→sell_decision/core/、sell_session_router→ex_sor/core/、firm_risk_aggregator/correlation_regime_monitor→position/core/、lifecycle_state_machine→factor/governance/。

## 六向台账

| 环节 | 上游 | 下游 | 生产者代码(路径:行) | 消费者代码 | 自动化态 | 运行态 | 三态复核 |
|------|------|------|---------------------|------------|----------|--------|----------|
| D-01(F37) L0 盘前作战计划 | F33/F50 | F38-F41 | src/zephyr/plan_engine/daily_warroom_pipeline.py | daily_loop_master_switch.py+strategy_pipeline/daily_decision_orchestrator.py+pipeline_events.py（3 消费方） | 定时（盘前）+事件 | 绿 | **维持挖干** |
| D-02(F38) L1 大盘总闸+六传感器 | A 段行情 | F39-F41 | src/zephyr/regime/core/regime_detector.py+anchored_state_machine.py | src/zephyr/data/config/tasks.yaml:647 anchored_state_build（c1_backtest.regime_state_anchored，trading_day_only）+autonomy_core/module_mapper+backtest/regime_validation 族+experiment_tracking/adapters/regime_adapter | 定时（盘中判定+盘后建账） | 绿 | **维持挖干** |
| D-03(F39) L2 板块选择 | F38 | F40/F41 | src/zephyr/signal_ashare/ **156 py**；板块族在 core/：sector_conduction/sector_ecology_judge/sector_strength_aggregator/sector_strength_wiring（skeleton 写"sector/ 子目录"=路径注记） | position_sector_context.py+选股链 | 定时（盘中） | 绿 | **维持挖干** |
| D-04(F40) L3 个股选择 | F39 | F41 | src/zephyr/signal_fundamental/selection_funnel.py+negative_veto.py（skeleton 写 signal_ashare/selection/=**路径漂移**） | signal_ashare/screening/{selection_funnel_skeleton,tiered_screening_filter}.py+strategy_signal/signal_factory.py | 定时（盘中） | 绿 | **维持挖干** |
| D-05(F41) L4 买卖点与执行 | F40 | F53-F58 | src/zephyr/ex_core/（aggregate_root_manager/async_fill_dispatcher/audit_journal 全族）+ex_sor/ | pre_execution_checker→compliance/compliance_rule_engine.py+ex_core/premarket_checker.py（合规预检已挂） | 事件（信号→订单） | 绿 | **维持挖干(P0 主链)** |
| D-06(F42) P1 持仓体检 | F57 对账 | F43/F45 | src/zephyr/position/core/ **31 py** | position_checkup_orchestrator.py（imports sell_decision triage）→F43/F45 | 定时（对账驱动） | 绿 | **维持挖干** |
| D-07(F43) P2 做T与加减仓 | F42 | F44/F46 | src/zephyr/sell_decision/core/t_trade_coordinator.py（skeleton 写 position/core/=**路径漂移**）+position/core/rebalance_engine.py | position/core/core_satellite_allocator.py+signal_ashare/intraday_t0/t0_trading_pipeline.py | 事件 | 绿 | **维持挖干** |
| D-08(F44) P3 加仓决策 | F42 | F41 | src/zephyr/position/core/pyramiding_rules.py+position_sizing_engine.py | sizing→plan_engine/track_fusion.py+core_satellite_allocator.py+firm_risk_aggregator.py（3 方）；pyramiding_rules 仅包内 __init__ 导出（无包外直呼，经 sizing 链消费） | 事件 | 绿 | **维持挖干**（pyramiding 直呼缺注记） |
| D-09(F45) S1 卖出信号收集评分 | F42/F38 | F46 | src/zephyr/sell_decision/core/sell_signal_{collector,scorer,fusion_engine,accuracy_monitor}.py（六桶融合） | s1_scan_orchestrator.py+breakout_failure_detector.py+replacement_rebalance_seller.py+sell_conflict_arbitrator.py（4 消费方） | 事件 | 绿 | **维持挖干(P0 主链)** |
| D-10(F46) S2 离场执行 | F45 | F53-F57 | src/zephyr/sell_decision/core/sell_execution_planner.py（包 __init__:49 导出）+ex_sor/core/sell_session_router.py（**路径漂移**） | sell_decision 包经 position_checkup_orchestrator.py:143 进入；ex_sor algo_execution_selector/algo_trading_engine 同目录族 | 事件 | 绿 | **维持挖干(P0 主链)** |
| D-11(F47) R1 应急保命 | F59/F60 | 全流横切 | src/zephyr/security/access_control/kill_switch.py+infrastructure/capacity_assurance/kill_switch.py+infrastructure/rollback/kill_switch.py（**三实例族实证**）+infrastructure/kill_switch_sim.py+autonomy_core/kill_switch_orchestrator.py；risk/core/drawdown_state_machine.py | drawdown_state_machine→position/core/defensive_asset_whitelist.py+risk/core/drawdown_session_persistence.py+strategy_pipeline/daily_gate_snapshot.py+scripts/backtest/sim_daily_runner.py | 事件（熔断触发） | 绿 | **维持挖干(P0 主链)** |
| D-12(F48) C1 预算切分 | F27/F71 | F49 | src/zephyr/pf_alloc/core/multi_strategy_capital_allocator.py | signal_ashare/strategy_signal/signal_weight_adjuster.py+pf_alloc_daily 分配链（B-15 翻绿证据共用） | 事件 | 绿 | **维持挖干(P0 主链)** |
| D-13(F49) C2 组合聚合 | F48 | F50 | src/zephyr/position/core/firm_risk_aggregator.py+correlation_regime_monitor.py（skeleton 写 pf_core/=**路径漂移**） | pf_alloc/batched_position_builder.py+plan_engine/{boundary_revision_engine,tomorrow_boundary_planner}.py+position/core/budget_change_handler.py（4 消费方） | 事件 | 绿 | **维持挖干** |
| D-14(F50) C3 绩效归因反馈 | F49/F28 | F37/F21 回灌 | src/zephyr/pf_core/core/performance_attribution_engine.py（MOD-PF-007）+factor/governance/lifecycle_state_machine.py（**路径漂移**） | factor/factor_factory.py+factor/governance/engine.py+six_step_flow.py+governance/lifecycle_governance/factor_promotion_wiring.py | 定时（评审周期） | 绿 | **维持挖干** |
| D-15(F51) 币圈决策骨架 | — | — | TDM-C-L1..L4 **4/4 全 null**（实跑确认） | 无 | 无（V0 空壳，markets 第二实例设计内） | 红 | **维持盲区(P2 设计内)**（详 F51.md） |
| D-16(F52) 验证方法学与决策算法库 | — | F23/F35/F66 | docs/registry_of_registries.yaml:747 REG-VALM-001+:757 REG-DAL-001（+并入 REG-TECHNICAL-INDICATOR/PAT） | data/config/known_data_gaps.yaml+scripts/audit/cost_trio_exam.py+scripts/governance/d3_metadata/check_registry_consistency.py+backtest_backlog.yaml（4 引用实证） | 静态册（引用态） | 绿 | **维持挖干** |

## 本段三态变迁

零判级变迁（D 段 16 环全部维持原判）。登记 6 处**路径漂移**（上表标注）供 S2 回写 skeleton 锚。
