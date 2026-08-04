---
doc_type: audit_report
title: 作战地图对齐报告
version: "1.0"
status: active
date: 2026-08-04
owner: auto-generator
ttl: permanent
---

# 作战地图对齐报告 (Battle Map Alignment Report)

- 生成时间: 2026-08-04 10:44:23
- 数据源: depgraph (PostgreSQL)
- 三表统计: steps=285 / anchors=381 / edges=119 / 叙事真源=285
- 业务域模块: 1765（BM-INV-007 扫描范围，业务域白名单内 depgraph 节点）
- 问题总数: 1160
  - 孤儿环节（BM-INV-001，无锚点=悬空决策）: 0
  - 幽灵锚点（BM-INV-002，target_id 找不到）: 0
  - 缺失叙事（BM-INV-003，翻译真源无环节）: 0
  - 悬空边（edge 指向不存在环节）: 0
  - 域漂移（BM-INV-004，target domain 不在 flow_stage 允许列表）: 0
  - 父子嵌套问题（BM-INV-006，父不存在/跨阶段/成环/depth超限）: 0
  - 孤儿模块（BM-INV-007，业务域模块无作战锚点=造出来没用上）: 1160

## 1. 孤儿环节（BM-INV-001：环节无锚点 = 悬空决策）

> 君子协定：每个 battle_map_steps 必须至少有一个 battle_map_anchors。无锚点环节 = 没有模块承载 = AI 写决策时凭记忆推断 = 幻觉风险。

> ✅ 无孤儿环节，所有环节均已挂载锚点。

## 2. 幽灵锚点（BM-INV-002：target_id 在目标图找不到）

> 君子协定：anchor.target_id 必须能在 target_graph 对应的图/仓库里找到。找不到 = 幽灵锚点 = 指向不存在的模块/候选/蓝图。

> ✅ 无幽灵锚点（或锚点表为空，无对象校验）。

## 3. 缺失叙事（BM-INV-003：翻译真源无对应环节）

> 君子协定：DB 每个环节必须在翻译真源 `battle_map_steps` 段有叙事（name_zh/plain_zh/mechanism_zh/indicators_zh）。缺失 = 生成器降级到 DB step_name。

> ✅ 无缺失叙事，所有环节在翻译真源均已登记。

## 4. 悬空边（edge 指向不存在的环节）

> ✅ 无悬空边，所有流转边两端均为合法环节。

## 5. 域漂移（BM-INV-004：target domain 不在 flow_stage 允许列表）

> 君子协定：anchor 的 target module/candidate 的 domain 必须在 step.flow_stage 对应的允许域列表里。不在 = 域漂移 = 语义错位（如把卖出决策挂在买入流程）。规则真源：`docs/01_policies_and_standards/_registry/catalogs/battle_map_domain_policy.yaml`。

> ✅ 无域漂移，所有锚点 target domain 都在对应 flow_stage 允许列表里。

## 6. 父子嵌套问题（BM-INV-006：父不存在/跨阶段/成环/depth超限）

> 君子协定：parent_step_id 必须指向同 flow_stage 的已存在环节，depth≤3，parent 链不能成环。规则真源：battle_map_positioning.md §8.4。

> ✅ 无父子嵌套问题。

## 7. 孤儿模块（BM-INV-007：业务域模块无作战锚点 = 造出来没用上）

> 君子协定：业务域（battle_map_domain_policy.yaml 所有 flow_stage 的 allowed 域并集）内的 depgraph 模块，必须至少有一个 battle_map_anchors 指向它（target_graph=depgraph，target_id 命中其 blueprint_id 或 path）。无任何锚点指向 = 没有作战使命 = 造出来没用上 = 幻觉/浪费风险。非业务域（D_GOVERNANCE/D_GOV_SCRIPTS/D_FRONTEND 等基础设施/治理/工具）天然排除，不在此扫。

| blueprint_id | 名称 / Name | domain_id | build_status | path |
|---|---|---|---|---|
| None | zephyr-sqlite-task-db — database 节点 (ARCH-053) | D_INFRA_RUNTIME | stable | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-001 |
| None | zephyr-chroma-vector-db — database 节点 (ARCH-053) | D_INFRA_RUNTIME | stable | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-002 |
| MOD-ML-003 | — | D_ML_TRAIN | planned | src/zephyr/ml_train/training_dataset_manager/ |
| None | zephyr-depgraph-db — database 节点 (ARCH-053) | D_INFRA_RUNTIME | stable | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-003 |
| None | zephyr-clickhouse-c1-market — database 节点 (ARCH-053) | D_INFRA_RUNTIME | stable | docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml#INFRA-DB-006 |
| MOD-EX-051 | — | D_EX_CORE | planned | src/zephyr/ex_core/value_objects.py |
| MOD-L10-001 | 异步intercept队列 / async_intercept_queue | D_COMPLIANCE | planned | src/zephyr/compliance/async_intercept_queue.py |
| MOD-EX-029 | 停止亏损止盈利润执行器 / stop_loss_take_profit_executor | D_EX_CORE | planned | src/zephyr/ex_core/stop_loss_take_profit_executor.py |
| MOD-SIG-009 | 信号优先级路由器 / Signal Priority Router | D_FUNDAMENTAL_SIGNAL | planned | src/zephyr/signal_fundamental/router/signal_priority_router.py |
| MOD-POS-005 | — | D_POSITION | planned | src/zephyr/position/core/cross_strategy_position_merger.py |
| MOD-POS-011 | — | D_POSITION | planned | src/zephyr/position/core/covariance_estimator.py |
| MOD-H1_REDIS_HOT | — | D_INFRA_RUNTIME | deprecated | src/zephyr/infrastructure/h1_redis_hot/h1_factor_source.py |
| MOD-POS-015 | — | D_POSITION | planned | src/zephyr/position/core/position_time_budget.py |
| MOD-EX-012 | — | D_EX_CORE | planned | src/zephyr/ex_core/execution_tca.py |
| MOD-EX-021 | — | D_EX_CORE | planned | src/zephyr/ex_core/deployment_consistency_manager.py |
| MOD-EX-036 | — | D_EX_CORE | planned | src/zephyr/ex_core/performance_monitor.py |
| MOD-L00-005 | 连接器 | D_DATA | planned | src/zephyr/data/connectors/ |
| MOD-L00-007 | 存储 | D_DATA | planned | src/zephyr/data/storage/ |
| MOD-L00-004 | — | D_DATA | deprecated | src/zephyr/data/data_lineage/ |
| MOD-L00-004 | — | D_DATA | deprecated | zephyr.data.kline_resampler |
| MOD-L00-004 | — | D_DATA | deprecated | zephyr.data.sector_snapshot_collector |
| MOD-EX-015 | 执行报告 / execution_report | D_EX_CORE | deprecated | src/zephyr/ex_core/execution_report.py |
| MOD-SIG-010 | 信号冲突解决器 / Signal Conflict Resolver | D_FUNDAMENTAL_SIGNAL | planned | src/zephyr/signal_fundamental/router/signal_conflict_resolver.py |
| MOD-EX-031 | 批次止盈利润执行器 / batch_take_profit_executor | D_EX_CORE | planned | src/zephyr/ex_core/batch_take_profit_executor.py |
| MOD-EX-032 | 拍卖偏差执行器 / auction_deviation_executor | D_EX_CORE | planned | src/zephyr/ex_core/auction_deviation_executor.py |
| MOD-RSK-009 | — | D_RISK | deprecated | src/zephyr/risk/ashare_stop_loss_rule_engine.py |
| None | — | D_ALT_DATA | deprecated | test_trigger_A.py |
| MOD-EX-059 | 执行MCP服务端 / execution_mcp_server | D_EX_CORE | planned | src/zephyr/ex_core/execution_mcp_server.py |
| MOD-INF-034 | docs__03_modules___cross_layer__model_profiler__blueprint_md | D_ML_TRAIN | planned | docs/03_modules/_cross_layer/model_profiler/blueprint.md |
| MOD-EX-042 | conditional订单管理器 / conditional_order_manager | D_EX_CORE | planned | src/zephyr/ex_core/conditional_order_manager.py |
| MOD-L00-008 | 缓存 | D_DATA | planned | src/zephyr/data/cache/ |
| None | — | D_ASHARE_SIGNAL | deprecated | test_trigger_B.py |
| MOD-L00-006 | 归一化器 | D_DATA | planned | src/zephyr/data/normalizers/ |
| MOD-GATE_ENGINE | 部署抑制 / Deployment Suppression — v0.37.0 R464 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/deployment_suppression.py |
| MOD-GATE_ENGINE | 安全门禁l1l27 / Safety Gates L1-L27 — Unified Pipeline (MOD-FEEDBACK_LOOP §3 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l1_l27.py |
| MOD-INF-023 | — | D_SECURITY | generated | src/zephyr/gov_drift/state_machine.py |
| MOD-RISK-001 | — | D_RISK | deprecated | src/zephyr/risk/drawdown_tracker/ |
| MOD-PF-004 | — | D_PF_CORE | deprecated | src/zephyr/pf_core/strategies/min_variance_strategy.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_diff.py |
| MOD-INTEGRATION | — | D_INTEGRATION | generated | src/zephyr/integration/shared/contracts/errors/contract_violation_error.py |
| MOD-INTEGRATION | — | D_INTEGRATION | generated | src/zephyr/integration/shared/contracts/errors/data_quality_error.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/convergence_checker.py |
| MOD-INF-011 | docs__03_modules___domain_knowledge__vector_memory__blueprint_md | D_KNOWLEDGE | planned | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/staging_area.py |
| MOD-INF-016 | — | D_TRADING | generated | src/zephyr/trading/trading_contracts/risk/compliance_rule.py |
| MOD-PF-005 | — | D_PF_CORE | deprecated | src/zephyr/pf_core/strategies/risk_parity_strategy.py |
| MOD-EX-004 | redis幂等性 | D_EX_CORE | planned | src/zephyr/ex_core/redis_idempotency/ |
| MOD-EX-035 | 实盘仿真切换器 / live_simulation_switcher | D_EX_CORE | planned | src/zephyr/ex_core/live_simulation_switcher.py |
| MOD-POS-012 | — | D_POSITION | planned | src/zephyr/position/core/correlation_regime_monitor.py |
| MOD-POS-013 | — | D_POSITION | planned | src/zephyr/position/core/position_risk_budget_allocator.py |
| MOD-POS-018 | — | D_POSITION | planned | src/zephyr/position/core/intraday_position_constraint.py |
| MOD-POS-019 | — | D_POSITION | planned | src/zephyr/position/core/position_behavior_classifier.py |
| MOD-EX-052 | — | D_EX_CORE | planned | src/zephyr/ex_core/factory.py |
| MOD-EX-058 | — | D_EX_CORE | planned | src/zephyr/ex_core/miniqmt_channel_manager.py |
| MOD-EX-037 | — | D_EX_CORE | planned | src/zephyr/ex_core/blueprint_implementer.py |
| MOD-EX-060 | — | D_EX_CORE | planned | src/zephyr/ex_core/rl_optimal_executor.py |
| MOD-EX-061 | — | D_EX_CORE | planned | src/zephyr/ex_core/microstructure_modeler.py |
| MOD-RSK-011 | — | D_RISK | deprecated | src/zephyr/risk/drawdown_realtime_tracker.py |
| MOD-RSK-010 | — | D_RISK | deprecated | src/zephyr/risk/ashare_systemic_risk_detector.py |
| MOD-EX-033 | 卖出优先级调度器 / sell_priority_scheduler | D_EX_CORE | planned | src/zephyr/ex_core/sell_priority_scheduler.py |
| MOD-L10-001 | 包入口 / D_COMPLIANCE Compliance | D_COMPLIANCE | generated | src/zephyr/compliance/zero_knowledge_audit_stub/__init__.py |
| MOD-L00-004 | 本地replay / local_replay | D_DATA | generated | src/zephyr/data/local_replay.py |
| MOD-L00-004 | 880xxx 板块动态排名引擎——5因子复合排名调整99只推送池。 / sector_ranking_engine | D_DATA | stable | src/zephyr/data/sector_ranking_engine.py |
| MOD-L00-004 | TQCenter提供器 / tqcenter_provider | D_DATA | generated | src/zephyr/data/implementations/tqcenter_provider.py |
| MOD-L00-001 | 包入口 / D_DATA Data Source | D_DATA | generated | src/zephyr/data/satellite_geospatial_engine/__init__.py |
| MOD-L00-004 | 归一化器 / normalizer | D_DATA | generated | src/zephyr/data/symbol_normalizer/normalizer.py |
| MOD-L00-004 | 包入口 / __init__ | D_DATA | stable | src/zephyr/data/symbol_normalizer/__init__.py |
| MOD-L00-006 | WAL 段编解码模块（MOD-L00-006）。 / __init__ | D_DATA | stable | src/zephyr/data/wal_codec/__init__.py |
| MOD-EX-055 | — | D_EX_CORE | stable | src/zephyr/ex_core/multi_contract_adapter.py |
| MOD-EX_SOR | 包入口 / __init__ | D_EX_SOR | generated | src/zephyr/ex_sor/models/__init__.py |
| MOD-L02_ANA | 包入口 / __init__ | D_FACTOR | stable | src/zephyr/factor/analysis/__init__.py |
| MOD-L02_GOV | 包入口 / __init__ | D_FACTOR | generated | src/zephyr/factor/governance/__init__.py |
| MOD-FEEDBACK_LOOP | 教师迁移 / Teacher Transfer — v0.6.0 R53 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/teacher_transfer.py |
| MOD-FEEDBACK_LOOP | 提示自优化循环 / R502: PromptSelfOptimizationLoop | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/prompt_self_optimization_loop.py |
| MOD-GATE_ENGINE | 自治信用 / Autonomy Credit System — v0.7.0 R87 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/autonomy_credit.py |
| MOD-GATE_ENGINE | 标志生命周期管理器 / Flag Lifecycle Manager — v0.3.0 R11 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/flag_lifecycle_manager.py |
| MOD-FEEDBACK_LOOP | preflight模拟器 / Pre-Flight Simulator — v0.12.0 R169b | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/pre_flight_simulator.py |
| MOD-GOVERNANCE | — | D_OPS | stable | src/zephyr/governance/observability_governance/observability_dashboard.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/dependency.py |
| MOD-INF-042 | — | D_INTEGRATION | stable | src/zephyr/integration/local_model/cache_layer.py |
| MOD-INF-013 | — | D_INTEGRATION | generated | src/zephyr/integration/mcp/handoff_auto_loader.py |
| MOD-INF-016 | — | D_INTEGRATION | stable | src/zephyr/integration/shared/events/upgrade_strategy.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/exam_test_cases.py |
| MOD-INF-022 | — | D_POSITION | stable | src/zephyr/position/position_reconciler.py |
| MOD-INF-030 | — | D_SECURITY | stable | src/zephyr/security/adversarial_validation/constitution_engine.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/injection_engine.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/orchestration_protocol.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/contracts/identity/agent_identity.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/maintenance/owner_trust_gauge.py |
| MOD-SIGNAL_ASHARE | 包入口 / __init__ | D_ASHARE_SIGNAL | generated | src/zephyr/signal_ashare/_extensions/__init__.py |
| MOD-L13-001 | — | D_SIMULATION | stable | src/zephyr/simulation/pipeline_base.py |
| MOD-L13-001 | — | D_SIMULATION | stable | src/zephyr/simulation/implementations/default_experiment_pipeline.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/capability_card.py |
| MOD-INF-033 | — | D_TRADING | stable | src/zephyr/trading/protection_index.py |
| MOD-INF-033 | — | D_TRADING | stable | src/zephyr/trading/verdict_engine.py |
| MOD-INF-035 | — | D_TRADING | stable | src/zephyr/trading/runtime/async_runtime.py |
| MOD-L00-001 | — | D_TRADING | generated | src/zephyr/trading/trading_contracts/portfolio/contracts/money.py |
| MOD-L00-001 | — | D_TRADING | generated | src/zephyr/trading/trading_contracts/portfolio/contracts/strategy_lifecycle_event.py |
| MOD-L00-004 | — | D_DATA | generated | scripts/ops/ch_health_probe.py |
| MOD-L00-004 | 告警通道端到端验证（B2，#ARCH-CH-023，2026-07-25）。 / verify_alert_channels | D_DATA | generated | scripts/ops/verify_alert_channels.py |
| MOD-L02-024 | — | D_FACTOR | generated | tests/factor/test_dag_executor_dual_mode.py |
| MOD-L02-025 | — | D_FACTOR | generated | tests/factor/test_incremental_compute.py |
| MOD-L04-002 | 行情l2逐笔 / market_l2_tick | D_DATA | generated | schemas/categories/market_l2_tick.py |
| MOD-L00-004 | — | D_DATA | generated | scripts/start_ch_health_probe.ps1 |
| MOD-L00-004 | 注册aux任务 / register_aux_tasks | D_DATA | generated | scripts/register_aux_tasks.ps1 |
| MOD-ALT_DATA | 包入口 / __init__ | D_ALT_DATA | generated | src/zephyr/alt_data/models/__init__.py |
| MOD-BT-022 | 数据质量检查器 / data_quality_checker | D_BACKTEST | stable | src/zephyr/backtest/services/data_quality_checker.py |
| MOD-BT-018 | decay监控器 / decay_monitor | D_BACKTEST | stable | src/zephyr/backtest/services/decay_monitor.py |
| MOD-BT-023 | 回测异常诊断器 / Anomaly Diagnoser | D_BACKTEST | stable | src/zephyr/backtest/services/anomaly_diagnoser.py |
| MOD-BT-020 | 回测缓存管理器 / Backtest Cache Manager | D_BACKTEST | stable | src/zephyr/backtest/services/cache_manager.py |
| MOD-BT-024 | 回测结果比较器 / Result Comparator | D_BACKTEST | stable | src/zephyr/backtest/services/result_comparator.py |
| MOD-BT-026 | nan处理器 / nan_processor | D_BACKTEST | stable | src/zephyr/backtest/services/nan_processor.py |
| MOD-BT-021 | 参数优化结果分析器 / Parameter Analyzer | D_BACKTEST | stable | src/zephyr/backtest/services/param_analyzer.py |
| MOD-BT-019 | 回测报告生成器 / Backtest Report Generator | D_BACKTEST | stable | src/zephyr/backtest/services/report_generator.py |
| MOD-BT-017 | D-BACKTEST BT-17 回测自动调度器——批量+参数网格+队列管理+结 / scheduler | D_BACKTEST | stable | src/zephyr/backtest/services/scheduler.py |
| MOD-INF-033 | 包入口 / __init__ | D_COMPLIANCE | generated | src/zephyr/compliance/behavioral_auditor/__init__.py |
| MOD-CROSS_ASSET | 包入口 / __init__ | D_CROSS_ASSET | generated | src/zephyr/cross_asset/__init__.py |
| MOD-CROSS_ASSET | 包入口 / __init__ | D_CROSS_ASSET | generated | src/zephyr/cross_asset/api/__init__.py |
| MOD-CROSS_ASSET | 包入口 / __init__ | D_CROSS_ASSET | generated | src/zephyr/cross_asset/core/__init__.py |
| MOD-CROSS_ASSET | 包入口 / __init__ | D_CROSS_ASSET | generated | src/zephyr/cross_asset/services/__init__.py |
| MOD-CROSS_ASSET | 包入口 / __init__ | D_CROSS_ASSET | generated | src/zephyr/cross_asset/models/__init__.py |
| MOD-CROSS_ASSET | 包入口 / __init__ | D_CROSS_ASSET | generated | src/zephyr/cross_asset/infrastructure/__init__.py |
| MOD-CROSS_ASSET | 包入口 / __init__ | D_CROSS_ASSET | generated | src/zephyr/cross_asset/_extensions/__init__.py |
| MOD-H1_REDIS_HOT | — | D_INFRA_RUNTIME | stable | src/zephyr/data/tick_redis_cache.py |
| MOD-DATA_GOV-003 | 元数据注册表 / metadata_registry | D_DATA_GOV | stable | src/zephyr/data_governance/core/metadata_registry.py |
| MOD-DATA_GOV-002 | lineage追踪器 / lineage_tracker | D_DATA_GOV | stable | src/zephyr/data_governance/core/lineage_tracker.py |
| MOD-DATA_GOV-001 | 模式注册表 / schema_registry | D_DATA_GOV | stable | src/zephyr/data_governance/core/schema_registry.py |
| MOD-DIGITAL_TWIN | 包入口 / __init__ | D_DIGITAL_TWIN | generated | src/zephyr/digital_twin/api/__init__.py |
| MOD-DIGITAL_TWIN | 包入口 / __init__ | D_DIGITAL_TWIN | generated | src/zephyr/digital_twin/__init__.py |
| MOD-DIGITAL_TWIN | 包入口 / __init__ | D_DIGITAL_TWIN | generated | src/zephyr/digital_twin/core/__init__.py |
| MOD-EXEC_SIM | 包入口 / __init__ | D_EXEC_SIM | generated | src/zephyr/execution_simulation/__init__.py |
| MOD-DIGITAL_TWIN | 包入口 / __init__ | D_DIGITAL_TWIN | generated | src/zephyr/digital_twin/infrastructure/__init__.py |
| MOD-EXEC_SIM | 包入口 / __init__ | D_EXEC_SIM | generated | src/zephyr/execution_simulation/api/__init__.py |
| MOD-DIGITAL_TWIN | 包入口 / __init__ | D_DIGITAL_TWIN | generated | src/zephyr/digital_twin/models/__init__.py |
| MOD-DIGITAL_TWIN | 包入口 / __init__ | D_DIGITAL_TWIN | generated | src/zephyr/digital_twin/_extensions/__init__.py |
| MOD-DIGITAL_TWIN | 包入口 / __init__ | D_DIGITAL_TWIN | generated | src/zephyr/digital_twin/services/__init__.py |
| MOD-EXEC_SIM | 包入口 / __init__ | D_EXEC_SIM | generated | src/zephyr/execution_simulation/core/__init__.py |
| MOD-EXEC_SIM | 包入口 / __init__ | D_EXEC_SIM | generated | src/zephyr/execution_simulation/infrastructure/__init__.py |
| MOD-EXEC_SIM | 包入口 / __init__ | D_EXEC_SIM | generated | src/zephyr/execution_simulation/models/__init__.py |
| MOD-EXEC_SIM | 包入口 / __init__ | D_EXEC_SIM | generated | src/zephyr/execution_simulation/services/__init__.py |
| MOD-EX-049 | — | D_EX_CORE | stable | src/zephyr/ex_core/aggregate_root_manager.py |
| MOD-EXEC_SIM | 包入口 / __init__ | D_EXEC_SIM | generated | src/zephyr/execution_simulation/_extensions/__init__.py |
| MOD-EX-001 | 部分成交处理器 | D_EX_CORE | stable | src/zephyr/ex_core/fill_handler.py |
| MOD-EX-003 | — | D_EX_CORE | stable | src/zephyr/ex_core/audit_journal/auditor.py |
| MOD-EX-050 | — | D_EX_CORE | stable | src/zephyr/ex_core/repository_interface.py |
| MOD-EX-003 | — | D_EX_CORE | generated | src/zephyr/ex_core/audit_journal/__init__.py |
| MOD-EX_SOR | 包入口 / __init__ | D_EX_SOR | generated | src/zephyr/ex_sor/__init__.py |
| MOD-XS-014 | — | D_EX_SOR | stable | src/zephyr/ex_sor/api/api_rate_limiter.py |
| MOD-EX_SOR | 包入口 / __init__ | D_EX_SOR | generated | src/zephyr/ex_sor/api/__init__.py |
| MOD-XS-013 | — | D_EX_SOR | stable | src/zephyr/ex_sor/api/broker_api_connector.py |
| MOD-XS-011 | 算法执行选择器 / algo_execution_selector | D_EX_SOR | stable | src/zephyr/ex_sor/core/algo_execution_selector.py |
| MOD-EX_SOR_EXT-001 | 滑点分析器 / slippage_analyzer | D_EX_SOR | stable | src/zephyr/ex_sor/services/slippage_analyzer.py |
| MOD-EX_SOR | 包入口 / __init__ | D_EX_SOR | generated | src/zephyr/ex_sor/core/__init__.py |
| MOD-EX_SOR_EXT-002 | 执行质量评分器 / execution_quality_scorer | D_EX_SOR | stable | src/zephyr/ex_sor/services/execution_quality_scorer.py |
| MOD-EX_SOR | 包入口 / __init__ | D_EX_SOR | generated | src/zephyr/ex_sor/services/__init__.py |
| MOD-EX_SOR_EXT-003 | 交易成本优化器 / transaction_cost_optimizer | D_EX_SOR | stable | src/zephyr/ex_sor/services/transaction_cost_optimizer.py |
| MOD-EX_SOR | 包入口 / __init__ | D_EX_SOR | generated | src/zephyr/ex_sor/_extensions/__init__.py |
| MOD-EX_SOR | 包入口 / __init__ | D_EX_SOR | generated | src/zephyr/ex_sor/infrastructure/__init__.py |
| MOD-FEEDBACK_LOOP | 自动进化 / auto_evolution | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/auto_evolution.py |
| MOD-FEEDBACK_LOOP | alert分发器 / alert_dispatcher | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/alert_dispatcher.py |
| MOD-FEEDBACK_LOOP | 背压桥接 / backpressure_bridge | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/backpressure_bridge.py |
| MOD-FEEDBACK_LOOP | 配置 / config | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/config.py |
| MOD-FEEDBACK_LOOP | 决策引擎 / Feedback Loop Decision Engine | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/decision_engine.py |
| MOD-INF-035 | 核心 / core | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/core.py |
| MOD-FEEDBACK_LOOP | 错误预算 / error_budget | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/error_budget.py |
| MOD-FEEDBACK_LOOP | db写入器 / db_writer | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/db_writer.py |
| MOD-FEEDBACK_LOOP | 数据库桥接 / db_bridge | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/db_bridge.py |
| MOD-FEEDBACK_LOOP | 适应度functions / fitness_functions | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/fitness_functions.py |
| MOD-FEEDBACK_LOOP | 异常 / exceptions | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/exceptions.py |
| MOD-FEEDBACK_LOOP | 进化引擎 / evolution_engine | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution_engine.py |
| MOD-FEEDBACK_LOOP | 生成器 / generator | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/generator.py |
| MOD-FEEDBACK_LOOP | 评估harness / eval_harness | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/eval_harness.py |
| MOD-FEEDBACK_LOOP | 反馈收集器 / FeedbackCollector: collect task execution feedback | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/feedback_collector.py |
| MOD-FEEDBACK_LOOP | 调度器 / scheduler | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/scheduler.py |
| MOD-FEEDBACK_LOOP | 调度器collectdetect / scheduler_collect_detect | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/scheduler_collect_detect.py |
| MOD-FEEDBACK_LOOP | 指标收集器 / MetricsCollector: append-only metrics recording. | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/metrics_collector.py |
| MOD-FEEDBACK_LOOP | SLO管理器 / slo_manager | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/slo_manager.py |
| MOD-FEEDBACK_LOOP | 协议 / protocols | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/protocols.py |
| MOD-FEEDBACK_LOOP | 返回尚未生成的骨骼文件列表. / validator | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/validator.py |
| MOD-FEEDBACK_LOOP | 模板 / template | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/template.py |
| MOD-FEEDBACK_LOOP | 调度器安全 / scheduler_safety | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/scheduler_safety.py |
| MOD-FEEDBACK_LOOP | 自诊断 / self_diagnosis | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/self_diagnosis.py |
| MOD-FEEDBACK_LOOP | 会话学习器 / session_learner | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/session_learner.py |
| MOD-FEEDBACK_LOOP | 动作选择器 / action_selector | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/action_selector.py |
| MOD-FEEDBACK_LOOP | 调度器健康 / scheduler_health | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/scheduler_health.py |
| MOD-FEEDBACK_LOOP | 代理生命周期 / Agent Lifecycle Manager — v0.12.0 R159c | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/agent_lifecycle.py |
| MOD-FEEDBACK_LOOP | 生成inherited / _gen_inherited | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/_gen_inherited.py |
| MOD-FEEDBACK_LOOP | 调度器act / scheduler_act | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/scheduler_act.py |
| MOD-FEEDBACK_LOOP | 告警路由器 / alert_router.py — Severity-based alert channel router. | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/alert_router.py |
| MOD-FEEDBACK_LOOP | API版本契约 / API Version Contract — v0.14.0 R188 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/api_version_contract.py |
| MOD-FEEDBACK_LOOP | intentdriven运维 / Intent-Driven Ops — v0.12.0 R159 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/intent_driven_ops.py |
| MOD-FEEDBACK_LOOP | 全局动作调度器 / Global Action Scheduler — v0.16.0 R226 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/global_action_scheduler.py |
| MOD-FEEDBACK_LOOP | 包入口 / Feedback Loop Engine — MOD-FEEDBACK_LOOP. | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/__init__.py |
| MOD-FEEDBACK_LOOP | ownerabsence升级 / Owner Absence Escalation — v0.37.0 R462 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/owner_absence_escalation.py |
| MOD-FEEDBACK_LOOP | 日历适配器 / Calendar Adapter — v0.8.0 R102b | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/calendar_adapter.py |
| MOD-FEEDBACK_LOOP | incident优先级分诊automator / Incident Priority Triage Automator — v0.37.0 R463 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/incident_priority_triage_automator.py |
| MOD-FEEDBACK_LOOP | 多代理编排器 / Multi-Agent Orchestrator — v0.12.0 R159b | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/multi_agent_orchestrator.py |
| MOD-FEEDBACK_LOOP | 包入口 / feedback-loop.actors — auto-generated package init. | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/__init__.py |
| MOD-FEEDBACK_LOOP | 通知personalizer / Notification Personalizer — v0.6.0 R67 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/notification_personalizer.py |
| MOD-FEEDBACK_LOOP | secondary告警通道 / Secondary Alert Channel — v0.37.0 R461 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/secondary_alert_channel.py |
| MOD-FEEDBACK_LOOP | 配置timeline / Config Timeline — v0.8.0 R99 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/config_timeline.py |
| MOD-FEEDBACK_LOOP | 金融分层 / Financial Stratification — v0.5.0 R50 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/financial_stratification.py |
| MOD-FEEDBACK_LOOP | Saga补偿器 / Saga Compensator — v0.3.0 R19b | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/actors/saga_compensator.py |
| MOD-FEEDBACK_LOOP | 数据质量校验器 / Data Quality Validator — v0.9.0 R110 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/data_quality_validator.py |
| MOD-FEEDBACK_LOOP | 反馈收集器 / feedback_collector | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/feedback_collector.py |
| MOD-FEEDBACK_LOOP | 知识库溯源 / KB Provenance — v0.10.0 R136 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/kb_provenance.py |
| MOD-FEEDBACK_LOOP | 知识注入 / Knowledge Injection — v0.8.0 R102 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/knowledge_injection.py |
| MOD-FEEDBACK_LOOP | LLM成本accounting / LLM Cost Accounting — v0.4.0 R35 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/llm_cost_accounting.py |
| MOD-FEEDBACK_LOOP | knownunknown注册表 / Known-Unknown Registry — v0.16.0 R229 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/known_unknown_registry.py |
| MOD-FEEDBACK_LOOP | 知识capture / Knowledge Capture — v0.4.0 R30 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/knowledge_capture.py |
| MOD-FEEDBACK_LOOP | 知识packaging / Knowledge Packaging — v0.9.0 R123 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/knowledge_packaging.py |
| MOD-FEEDBACK_LOOP | 知识freshness / Knowledge Freshness — v0.5.0 R47 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/knowledge_freshness.py |
| MOD-FEEDBACK_LOOP | 通知反馈 / Notification Feedback — v0.9.0 R118 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/notification_feedback.py |
| MOD-FEEDBACK_LOOP | 行情日历 / Market Calendar — v0.5.0 R48 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/market_calendar.py |
| MOD-FEEDBACK_LOOP | 行情事件integrator / Market Event Integrator — v0.14.0 R197 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/market_event_integrator.py |
| MOD-FEEDBACK_LOOP | 指标收集器 / metrics_collector | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/metrics_collector.py |
| MOD-FEEDBACK_LOOP | 模式迁移 / Schema Migration — v0.14.0 R190 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/schema_migration.py |
| MOD-FEEDBACK_LOOP | 模式进化 / Schema Evolution — v0.9.0 R111 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/schema_evolution.py |
| MOD-FEEDBACK_LOOP | temporal事件存储 / Temporal Event Store — v0.3.0 R9 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/temporal_event_store.py |
| MOD-FEEDBACK_LOOP | 包入口 / feedback-loop.collectors — auto-generated package init. | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/collectors/__init__.py |
| MOD-FEEDBACK_LOOP | 异常聚类 / Anomaly Clustering — v0.9.0 R119 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/anomaly/anomaly_clustering.py |
| MOD-FEEDBACK_LOOP | 令牌finops / Token FinOps — v0.12.0 R162 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/collectors/token_finops.py |
| MOD-FEEDBACK_LOOP | 包入口 / __init__ | D_FBL_DETECTORS | generated | src/zephyr/feedback_loop/detectors/__init__.py |
| MOD-FEEDBACK_LOOP | flapping检测器 / Flapping Detector — v0.40.0 R494 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/anomaly/flapping_detector.py |
| MOD-FEEDBACK_LOOP | 异常检测器 / anomaly_detector | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/anomaly/anomaly_detector.py |
| MOD-FEEDBACK_LOOP | emergentbehavior检测器 / Emergent Behavior Detector — v0.38.0 R473 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/anomaly/emergent_behavior_detector.py |
| MOD-FEEDBACK_LOOP | silentcorruption检测器 / Silent Corruption Detector — v0.40.0 R499 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/anomaly/silent_corruption_detector.py |
| MOD-FEEDBACK_LOOP | heisenbug检测器 / Heisenbug Detector — v0.38.0 R470 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/anomaly/heisenbug_detector.py |
| MOD-FEEDBACK_LOOP | infinite循环检测器 / Infinite Loop Detector — v0.15.0 R219 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/anomaly/infinite_loop_detector.py |
| MOD-FEEDBACK_LOOP | intermittent故障pattern / Intermittent Failure Pattern Detector — v0.40.0 R501 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/anomaly/intermittent_failure_pattern.py |
| MOD-FEEDBACK_LOOP | 日志异常 / Log Anomaly Detector — v0.6.0 R61 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/anomaly/log_anomaly.py |
| MOD-FEEDBACK_LOOP | synthetic异常generator / Synthetic Anomaly Generator — v0.9.0 R112 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/anomaly/synthetic_anomaly_generator.py |
| MOD-FEEDBACK_LOOP | temporal模式 / Temporal Pattern Detector — v0.12.0 R164 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/anomaly/temporal_pattern.py |
| MOD-FEEDBACK_LOOP | 包入口 / __init__ | D_FBL_DETECTORS | generated | src/zephyr/feedback_loop/detectors/anomaly/__init__.py |
| MOD-FEEDBACK_LOOP | 行为interaction检测器 / Action Interaction Detector — v0.38.0 R472 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/action_interaction_detector.py |
| MOD-FEEDBACK_LOOP | 行为sideeffectcumulative检测器 / R526: ActionSideEffectCumulativeDetector | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/action_side_effect_cumulative_detector.py |
| MOD-FEEDBACK_LOOP | 跨信号校验器 / Cross-Signal Validator — v0.6.0 R63 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/cross_signal_validator.py |
| MOD-FEEDBACK_LOOP | 代理trajectory异常检测器 / R503: AgentTrajectoryAnomalyDetector | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/agent_trajectory_anomaly_detector.py |
| MOD-FEEDBACK_LOOP | 跨系统关联器 / Cross-System Correlator — v0.13.0 R185 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/cross_system_correlator.py |
| MOD-FEEDBACK_LOOP | fle绩效回归检测器 / R532: FLEPerformanceRegressionDetector | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/fle_performance_regression_detector.py |
| MOD-FEEDBACK_LOOP | 决策溯源 / Decision Provenance — v0.12.0 R166 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/decision_provenance.py |
| MOD-FEEDBACK_LOOP | 依赖freshness监控器 / Dependency Freshness Monitor — v0.38.0 R474 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/dependency_freshness_monitor.py |
| MOD-FEEDBACK_LOOP | 行为efficacydecay检测器 / R507: ActionEfficacyDecayDetector | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/action_efficacy_decay_detector.py |
| MOD-FEEDBACK_LOOP | ensemble检测器 / Ensemble Detector — v0.4.0 R21 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/ensemble_detector.py |
| MOD-FEEDBACK_LOOP | 外部验证检查点 / R524: ExternalValidationCheckpoint | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/external_validation_checkpoint.py |
| MOD-FEEDBACK_LOOP | 外部健康 / External Health Monitor — v0.14.0 R193 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/external_health.py |
| MOD-FEEDBACK_LOOP | 包入口 / __init__ | D_FBL_DETECTORS | generated | src/zephyr/feedback_loop/detectors/correlation/__init__.py |
| MOD-FEEDBACK_LOOP | rumornoise过滤器 / Rumor Noise Filter — v0.37.0 R460 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/rumor_noise_filter.py |
| MOD-FEEDBACK_LOOP | 多信号关联器 / Multi-Signal Correlator — v0.4.0 R22 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/multi_signal_correlator.py |
| MOD-FEEDBACK_LOOP | trafficreplay校验器 / Traffic Replay Validator — v0.14.0 R202 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/traffic_replay_validator.py |
| MOD-FEEDBACK_LOOP | 配置漂移 / Config Drift Detector — v0.13.0 R182 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/drift/config_drift.py |
| MOD-FEEDBACK_LOOP | concept漂移 / Concept Drift Detector — v0.5.0 R42 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/drift/concept_drift.py |
| MOD-FEEDBACK_LOOP | 追踪causal桥接 / Trace Causal Bridge — v0.6.0 R62 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/correlation/trace_causal_bridge.py |
| MOD-FEEDBACK_LOOP | ensemble漂移 / Ensemble Drift — v0.5.0 R43 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/drift/ensemble_drift.py |
| MOD-FEEDBACK_LOOP | gradualpoisoning检测器 / Gradual Poisoning Detector — v0.15.0 R210 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/drift/gradual_poisoning_detector.py |
| MOD-FEEDBACK_LOOP | diminishingreturns检测器 / R528: DiminishingReturnsDetector | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/drift/diminishing_returns_detector.py |
| MOD-FEEDBACK_LOOP | 上下文windowcontamination检测器 / Context Window Contamination Detector — v0.38.0 R471 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/drift/context_window_contamination_detector.py |
| MOD-FEEDBACK_LOOP | 告警desensitizationcurve / Alert Desensitization Curve — v0.37.0 R492 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/guard/alert_desensitization_curve.py |
| MOD-FEEDBACK_LOOP | 包入口 / __init__ | D_FBL_DETECTORS | generated | src/zephyr/feedback_loop/detectors/drift/__init__.py |
| MOD-FEEDBACK_LOOP | 守卫级联检测器 / R520: GuardCascadeDetector | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/guard/guard_cascade_detector.py |
| MOD-FEEDBACK_LOOP | 趋势cycleseparator / Trend-Cycle Separator — v0.9.0 R113 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/drift/trend_cycle_separator.py |
| MOD-FEEDBACK_LOOP | positive反馈防御 / Positive Feedback Defense — v0.4.0 R28 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/guard/positive_feedback_defense.py |
| MOD-FEEDBACK_LOOP | 守卫振荡检测器 / R519: GuardOscillationDetector | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/guard/guard_oscillation_detector.py |
| MOD-FEEDBACK_LOOP | 自审计 / Self Audit — v0.13.0 R183 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/guard/self_audit.py |
| MOD-FEEDBACK_LOOP | placebo行为检测器 / R508: PlaceboActionDetector | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/guard/placebo_action_detector.py |
| MOD-FEEDBACK_LOOP | self诊断数据leak检测器 / R530: SelfDiagnosisDataLeakDetector | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/guard/self_diagnosis_data_leak_detector.py |
| MOD-FEEDBACK_LOOP | 包入口 / __init__ | D_FBL_DETECTORS | generated | src/zephyr/feedback_loop/detectors/guard/__init__.py |
| MOD-FEEDBACK_LOOP | recursive诊断trustevaluator / R517: RecursiveDiagnosisTrustEvaluator | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/guard/recursive_diagnosis_trust_evaluator.py |
| MOD-FEEDBACK_LOOP | blastradius预算 / Blast Radius Budget — v0.13.0 R178 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/blast_radius_budget.py |
| MOD-FEEDBACK_LOOP | 自动伸缩修复 / Autoscale Remediation — v0.13.0 R174 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/autoscale_remediation.py |
| MOD-FEEDBACK_LOOP | temporalcoherenceofself模型 / R525: TemporalCoherenceOfSelfModel | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/guard/temporal_coherence_of_self_model.py |
| MOD-FEEDBACK_LOOP | 自ha / Self HA — v0.13.0 R173 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/guard/self_ha.py |
| MOD-FEEDBACK_LOOP | 容量预测 / Capacity Forecast — v0.13.0 R186b | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/capacity_forecast.py |
| MOD-FEEDBACK_LOOP | 混沌工程 / Chaos Engineering — v0.13.0 R172 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/chaos_engineering.py |
| MOD-FEEDBACK_LOOP | 爆炸半径 / Blast Radius Detector — v0.12.0 R167 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/blast_radius.py |
| MOD-FEEDBACK_LOOP | ebpf监控器 / eBPF Monitor — v0.6.0 R64 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/ebpf_monitor.py |
| MOD-FEEDBACK_LOOP | 标志生命周期 / Flag Lifecycle Detector — v0.13.0 R180 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/flag_lifecycle.py |
| MOD-FEEDBACK_LOOP | maintenance协调器 / Maintenance Coordinator — v0.12.0 R168 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/maintenance_coordinator.py |
| MOD-FEEDBACK_LOOP | OpenFeature / OpenFeature Integration — v0.13.0 R181 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/openfeature.py |
| MOD-FEEDBACK_LOOP | otel适配器 / OTel Adapter — v0.12.0 R170 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/otel_adapter.py |
| MOD-FEEDBACK_LOOP | 指标cardinality守卫 / Metric Cardinality Guard — v0.40.0 R495 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/metric_cardinality_guard.py |
| MOD-FEEDBACK_LOOP | 版本migrator / Version Migrator — v0.12.0 R169 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/version_migrator.py |
| MOD-FEEDBACK_LOOP | runbook执行器 / Runbook Executor — v0.13.0 R186a | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/runbook_executor.py |
| MOD-FEEDBACK_LOOP | regulatory审计 / Regulatory Audit Detector — v0.13.0 R184 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/regulatory_audit.py |
| MOD-FEEDBACK_LOOP | 包入口 / __init__ | D_FBL_DETECTORS | generated | src/zephyr/feedback_loop/detectors/reliability/__init__.py |
| MOD-FEEDBACK_LOOP | resolution追踪器 / Resolution Tracker — v0.12.0 R165 | D_FBL_DETECTORS | stable | src/zephyr/feedback_loop/detectors/reliability/resolution_tracker.py |
| MOD-FEEDBACK_LOOP | 自适应参数调优 / Adaptive Parameter Tuning — v0.37.0 R452 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/cognitive/adaptive_param_tuning.py |
| MOD-FEEDBACK_LOOP | 认知load / Cognitive Load Estimator — v0.6.0 R68 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/cognitive/cognitive_load.py |
| MOD-FEEDBACK_LOOP | 包入口 / __init__ | D_FBL_DIAGNOSERS | generated | src/zephyr/feedback_loop/diagnosers/__init__.py |
| MOD-FEEDBACK_LOOP | 认知load预算 / Cognitive Load Budget — v0.16.0 R223 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/cognitive/cognitive_load_budget.py |
| MOD-FEEDBACK_LOOP | 协同学习 / Collaborative Learning — v0.7.0 R82 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/cognitive/collaborative_learning.py |
| MOD-FEEDBACK_LOOP | 置信度分解器 / Confidence Decomposer — v0.7.0 R83 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/cognitive/confidence_decomposer.py |
| MOD-FEEDBACK_LOOP | tone适配器v2 / Tone Adapter v2 — v0.10.0 R141 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/cognitive/tone_adapter_v2.py |
| MOD-FEEDBACK_LOOP | 苏格拉底式提问 / Socratic Questions — v0.7.0 R81 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/cognitive/socratic_questions.py |
| MOD-FEEDBACK_LOOP | 包入口 / __init__ | D_FBL_DIAGNOSERS | generated | src/zephyr/feedback_loop/diagnosers/cognitive/__init__.py |
| MOD-FEEDBACK_LOOP | tone适配器 / Tone Adapter — v0.9.0 R127 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/cognitive/tone_adapter.py |
| MOD-FEEDBACK_LOOP | 游戏化 / Gamification — v0.8.0 R101 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/cognitive/gamification.py |
| MOD-FEEDBACK_LOOP | 元守卫latency预算 / R516: MetaGuardLatencyBudget | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/cognitive/meta_guard_latency_budget.py |
| MOD-FEEDBACK_LOOP | 自动诊断 / Auto Diagnosis — v0.3.0 R16 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/auto_diagnosis.py |
| MOD-FEEDBACK_LOOP | 诊断kpi / Diagnosis KPI — v0.9.0 R116 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/diagnosis_kpi.py |
| MOD-FEEDBACK_LOOP | causalinference引擎 / Causal Inference Engine — v0.3.0 R5-R7 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/causal_inference_engine.py |
| MOD-FEEDBACK_LOOP | 反事实 / Counterfactual Engine — v0.6.0 R60 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/counterfactual.py |
| MOD-FEEDBACK_LOOP | 诊断引擎 / diagnosis_engine | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/diagnosis_engine.py |
| MOD-FEEDBACK_LOOP | 冲击预测器 / Impact Predictor — v0.9.0 R121 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/impact_predictor.py |
| MOD-FEEDBACK_LOOP | statisticalhygiene审计器 / Statistical Hygiene Auditor — v0.38.0 R476 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/statistical_hygiene_auditor.py |
| MOD-FEEDBACK_LOOP | mtti追踪器 / MTTI Tracker — v0.16.0 R221 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/mtti_tracker.py |
| MOD-FEEDBACK_LOOP | 知识总线因子监控 / Knowledge Bus Factor Monitor — v0.38.0 R481 | D_FBL_DIAGNOSERS | generated | src/zephyr/feedback_loop/diagnosers/diagnosis/knowledge_bus_factor_monitor.py |
| MOD-FEEDBACK_LOOP | 知识市场 / Knowledge Market — v0.9.0 R126 | D_FBL_DIAGNOSERS | generated | src/zephyr/feedback_loop/diagnosers/diagnosis/knowledge_market.py |
| MOD-FEEDBACK_LOOP | interactive诊断 / Interactive Diagnosis — v0.7.0 R80 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/interactive_diagnosis.py |
| MOD-FEEDBACK_LOOP | incident知识injector / R504: IncidentKnowledgeInjector | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/incident_knowledge_injector.py |
| MOD-FEEDBACK_LOOP | 非平稳有效性 / Nonstationary Effectiveness — v0.37.0 R455 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/nonstationary_effectiveness.py |
| MOD-FEEDBACK_LOOP | 包入口 / __init__ | D_FBL_DIAGNOSERS | generated | src/zephyr/feedback_loop/diagnosers/diagnosis/__init__.py |
| MOD-FEEDBACK_LOOP | dr韧性指标 / DR Resilience Metrics — v0.17.0+ R231-R236 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/dr_resilience_metrics.py |
| MOD-FEEDBACK_LOOP | 端到端集成健康 / E2E Integration Health Monitor — v0.39.0 R489 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/e2e_integration_health.py |
| MOD-FEEDBACK_LOOP | 行为composition健康监控器 / R511: ActionCompositionHealthMonitor | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/action_composition_health_monitor.py |
| MOD-FEEDBACK_LOOP | vertical自assessment / Vertical Self Assessment — v0.10.0 R137 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/diagnosis/vertical_self_assessment.py |
| MOD-FEEDBACK_LOOP | 全局健康map / Global Health Map — v0.8.0 R103 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/global_health_map.py |
| MOD-FEEDBACK_LOOP | 自基准 / Self Benchmark — v0.9.0 R115 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/self_benchmark.py |
| MOD-FEEDBACK_LOOP | 记忆自检查 / Memory Self Check — v0.8.0 R105 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/memory_self_check.py |
| MOD-FEEDBACK_LOOP | fledogfood监控器 / FLE Dogfood Monitor — v0.38.0 R480 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/fle_dogfood_monitor.py |
| MOD-FEEDBACK_LOOP | 模型健康 / Model Health Monitor — v0.5.0 R40 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/model_health.py |
| MOD-FEEDBACK_LOOP | fle自SLO指标 / FLE Self SLO Metrics — v0.17.0+ R249-R254 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/fle_self_slo_metrics.py |
| MOD-FEEDBACK_LOOP | 自健康监控 / Self Health Monitor — v0.4.0 R29 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/self_health_monitor.py |
| MOD-FEEDBACK_LOOP | selfbottleneck检测器 / Self-Bottleneck Detector — v0.38.0 R479 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/self_bottleneck_detector.py |
| MOD-FEEDBACK_LOOP | 包入口 / __init__ | D_FBL_DIAGNOSERS | generated | src/zephyr/feedback_loop/diagnosers/health/__init__.py |
| MOD-FEEDBACK_LOOP | 倦怠告警 / Burnout Alarm — v0.8.0 R100 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/burnout_alarm.py |
| MOD-FEEDBACK_LOOP | amplification守卫 / Amplification Guard — v0.10.0 R134 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/amplification_guard.py |
| MOD-FEEDBACK_LOOP | API依赖指标 / API Dependency Metrics — v0.17.0+ R237-R242 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/api_dependency_metrics.py |
| MOD-FEEDBACK_LOOP | 自LLM可观测性 / Self LLM Observability — v0.12.0 R160 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/health/self_llm_observability.py |
| MOD-FEEDBACK_LOOP | 上下文truncation / Context Truncation Detector — v0.9.0 R122 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/context_truncation.py |
| MOD-FEEDBACK_LOOP | 容量感知修复 / Capacity Aware Repair — v0.9.0 R120 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/capacity_aware_repair.py |
| MOD-FEEDBACK_LOOP | 跨守卫冲突检测器 / R513: CrossGuardConflictDetector | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/cross_guard_conflict_detector.py |
| MOD-FEEDBACK_LOOP | 冷启动conservativemode / R509: ColdStartConservativeMode | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/cold_start_conservative_mode.py |
| MOD-FEEDBACK_LOOP | burn速率告警器 / Burn Rate Alerter — v0.14.0 R200 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/burn_rate_alerter.py |
| MOD-FEEDBACK_LOOP | 数据volumegrowth监控器 / Data Volume Growth Monitor — v0.39.0 R492 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/data_volume_growth_monitor.py |
| MOD-FEEDBACK_LOOP | 上下文windowpressure管理器 / R506: ContextWindowPressureManager | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/context_window_pressure_manager.py |
| MOD-FEEDBACK_LOOP | 守卫interactiontopologymapper / R518: GuardInteractionTopologyMapper | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/guard_interaction_topology_mapper.py |
| MOD-FEEDBACK_LOOP | 跨会话一致性校验器 / R510: CrossSessionConsistencyValidator | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/cross_session_consistency_validator.py |
| MOD-FEEDBACK_LOOP | 延迟SLO / Latency SLO Monitor — v0.14.0 R192 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/latency_slo.py |
| MOD-FEEDBACK_LOOP | llm提供器完整性 / LLM Provider Integrity — v0.15.0 R217 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/llm_provider_integrity.py |
| MOD-FEEDBACK_LOOP | 反馈延迟补偿器 / Feedback Delay Compensator — v0.38.0 R477 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/feedback_delay_compensator.py |
| MOD-FEEDBACK_LOOP | 守卫自一致性审计器 / R512: GuardSelfConsistencyAuditor | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/guard_self_consistency_auditor.py |
| MOD-FEEDBACK_LOOP | human异常flood检测器 / Human Anomaly Flood Detector — v0.40.0 R500 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/human_anomaly_flood_detector.py |
| MOD-FEEDBACK_LOOP | 模型rotation / Model Rotation — v0.9.0 R125 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/model_rotation.py |
| MOD-FEEDBACK_LOOP | llm质量回归 / LLM Quality Regression — v0.12.0 R161 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/llm_quality_regression.py |
| MOD-FEEDBACK_LOOP | 模型rotationv2 / Model Rotation v2 — v0.10.0 R140 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/model_rotation_v2.py |
| MOD-FEEDBACK_LOOP | 恢复timestats / Recovery Time Statistics — v0.37.0 R454 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/recovery_time_stats.py |
| MOD-FEEDBACK_LOOP | 运营季节性 / Operational Seasonality — v0.16.0 R228 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/operational_seasonality.py |
| MOD-FEEDBACK_LOOP | 提示清洗器 / Prompt Sanitizer — v0.10.0 R133 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/prompt_sanitizer.py |
| MOD-FEEDBACK_LOOP | 提示指纹 / Prompt Fingerprint — v0.3.0 R14 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/prompt_fingerprint.py |
| MOD-FEEDBACK_LOOP | 模型版本semantic漂移 / Model Version Semantic Drift Monitor — v0.39.0 R493 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/model_version_semantic_drift.py |
| MOD-FEEDBACK_LOOP | numericalstability守卫 / Numerical Stability Guard — v0.38.0 R475 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/numerical_stability_guard.py |
| MOD-FEEDBACK_LOOP | 市场状态增益调度 / Regime Gain Scheduling — v0.37.0 R453 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/regime_gain_scheduling.py |
| MOD-FEEDBACK_LOOP | 退役规划器 / Retirement Planner — v0.10.0 R139 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/retirement_planner.py |
| MOD-FEEDBACK_LOOP | SLO容量指标 / SLO Capacity Metrics — v0.17.0+ R243-R248 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/slo_capacity_metrics.py |
| MOD-FEEDBACK_LOOP | valueadded基线 / Value Added Baseline — v0.10.0 R138 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/value_added_baseline.py |
| MOD-FEEDBACK_LOOP | 系统熵监控 / R527: SystemEntropyMonitor | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/system_entropy_monitor.py |
| MOD-FEEDBACK_LOOP | temporal完整性守卫 / Temporal Integrity Guard — v0.38.0 R478 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/temporal_integrity_guard.py |
| MOD-FEEDBACK_LOOP | 时区语义推理器 / Timezone Semantic Reasoner — v0.37.0 R456 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/timezone_semantic_reasoner.py |
| MOD-FEEDBACK_LOOP | zombiefle检测器 / Zombie FLE Detector — v0.16.0 R222 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/zombie_fle_detector.py |
| MOD-FEEDBACK_LOOP | 包入口 / feedback-loop.docs — auto-generated package init. | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/docs/__init__.py |
| MOD-FEEDBACK_LOOP | 苦力量化 / Toil Quantification — v0.37.0 R457 | D_FBL_DIAGNOSERS | stable | src/zephyr/feedback_loop/diagnosers/reliability/toil_quantification.py |
| MOD-FEEDBACK_LOOP | 自动奖励 / Auto Reward — v0.7.0 R76 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/auto_reward.py |
| MOD-FEEDBACK_LOOP | conformal预测 / Conformal Prediction — v0.7.0 R74 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/conformal_prediction.py |
| MOD-FEEDBACK_LOOP | 跨gen验证 / Cross-Gen Validation — v0.7.0 R78 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/cross_gen_validation.py |
| MOD-FEEDBACK_LOOP | 包入口 / __init__ | D_FBL_DIAGNOSERS | generated | src/zephyr/feedback_loop/diagnosers/reliability/__init__.py |
| MOD-FEEDBACK_LOOP | 冷启动手册 / cold_start_manual | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/docs/cold_start_manual.py |
| MOD-FEEDBACK_LOOP | 故障replay / Failure Replay — v0.7.0 R77 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/failure_replay.py |
| MOD-FEEDBACK_LOOP | ewc知识库审查 / EWC KB Review — v0.6.0 R51 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/ewc_kb_review.py |
| MOD-FEEDBACK_LOOP | 动态阈值 / Dynamic Threshold — v0.7.0 R71 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/dynamic_threshold.py |
| MOD-FEEDBACK_LOOP | online特征importance / Online Feature Importance — v0.7.0 R73 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/online_feature_importance.py |
| MOD-FEEDBACK_LOOP | 提示优化回归检测器 / R514: PromptOptimizationRegressionDetector | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/prompt_optimization_regression_detector.py |
| MOD-FEEDBACK_LOOP | graduatedactivation协议 / Graduated Activation Protocol — v0.38.0 R485 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/graduated_activation_protocol.py |
| MOD-FEEDBACK_LOOP | selfmodification速率限制器 / R522: SelfModificationRateLimiter | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/self_modification_rate_limiter.py |
| MOD-FEEDBACK_LOOP | 超网络 / HyperNetwork — v0.7.0 R72 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/hypernetwork.py |
| MOD-FEEDBACK_LOOP | selfupgrade金丝雀 / Self Upgrade Canary — v0.14.0 R194 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/self_upgrade_canary.py |
| MOD-FEEDBACK_LOOP | 知识distillation / Knowledge Distillation — v0.6.0 R52 | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/evolution/knowledge_distillation.py |
| MOD-FEEDBACK_LOOP | automatedrcapostmortem生成器 / Automated RCA Postmortem Generator — v0.38.0 R486 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/automated_rca_postmortem_generator.py |
| MOD-FEEDBACK_LOOP | 提示工厂治理 / Prompt Factory Governance — v0.16.0 R224 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/prompt_factory_governance.py |
| MOD-FEEDBACK_LOOP | boot完整性attestation / Boot Integrity Attestation — v0.38.0 R487 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/boot_integrity_attestation.py |
| MOD-FEEDBACK_LOOP | 自reflection / Self Reflection — v0.7.0 R75 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/self_reflection.py |
| MOD-FEEDBACK_LOOP | 架构职责分离 / Architectural SoD — v0.15.0 R205 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/architectural_sod.py |
| MOD-FEEDBACK_LOOP | semanticintentpreservation守卫 / R505: SemanticIntentPreservationGuard | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/semantic_intent_preservation_guard.py |
| MOD-FEEDBACK_LOOP | 守卫complexity预算 / R523: GuardComplexityBudget | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/guard_complexity_budget.py |
| MOD-FEEDBACK_LOOP | training数据治理 / Training Data Governance — v0.14.0 R191 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/evolution/training_data_gov.py |
| MOD-FEEDBACK_LOOP | 加密自举 / Cryptographic Bootstrap — v0.15.0 R204 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/crypto_bootstrap.py |
| MOD-FEEDBACK_LOOP | 外部验证器 / External Verifier — v0.15.0 R203 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/external_verifier.py |
| MOD-FEEDBACK_LOOP | fleupgrade安全校验器 / R529: FLEUpgradeSafetyValidator | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/fle_upgrade_safety_validator.py |
| MOD-FEEDBACK_LOOP | 守卫配置漂移监控 / R521: GuardConfigurationDriftMonitor | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/guard_configuration_drift_monitor.py |
| MOD-FEEDBACK_LOOP | 包入口 / feedback-loop.evolution — auto-generated package init. | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/evolution/__init__.py |
| MOD-FEEDBACK_LOOP | 点入时间reconstructor / Point-in-Time Reconstructor — v0.37.0 R465 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/point_in_time_reconstructor.py |
| MOD-FEEDBACK_LOOP | 知识注入preflight验证器 / R515: KnowledgeInjectionPreFlightVerifier | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/forensic/knowledge_injection_pre_flight_verifier.py |
| MOD-FEEDBACK_LOOP | deterministic回放 / Deterministic Replay — v0.15.0 R206 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/deterministic_replay.py |
| MOD-FEEDBACK_LOOP | TOCTOU守卫 / TOCTOU Guard — v0.15.0 R207 | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/forensic/toctou_guard.py |
| MOD-FEEDBACK_LOOP | interruptcoherence校验器 / R531: InterruptCoherenceValidator | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/interrupt_coherence_validator.py |
| MOD-FEEDBACK_LOOP | serializationformat追踪器 / Serialization Format Tracker — v0.39.0 R488 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/serialization_format_tracker.py |
| MOD-FEEDBACK_LOOP | wormwrite完整性 / WORM Write Integrity — v0.15.0 R216 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/worm_write_integrity.py |
| MOD-GATE_ENGINE | 行为reversibility / Action Reversibility — v0.15.0 R208 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/action_reversibility.py |
| MOD-FEEDBACK_LOOP | 包入口 / feedback-loop.forensic — auto-generated package init. | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/forensic/__init__.py |
| MOD-FEEDBACK_LOOP | selfmodification审计 / Self-Modification Audit — v0.15.0 R218 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/self_modification_audit.py |
| MOD-FEEDBACK_LOOP | sub代理collusion / Sub-Agent Collusion Detector — v0.15.0 R213 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/sub_agent_collusion.py |
| MOD-FEEDBACK_LOOP | 状态迁移校验器 / State Migration Validator — v0.40.0 R497 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/forensic/state_migration_validator.py |
| MOD-GATE_ENGINE | 对抗验证 / Adversarial Validation Gate — FLE-ADVERSARIAL-VALIDATION + R | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/adversarial_validation.py |
| MOD-GATE_ENGINE | 自治成熟度 / Autonomy Maturity Ladder — v0.7.0 R86 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/autonomy_maturity.py |
| MOD-GATE_ENGINE | 蓝图代码协调器 / Blueprint-Code Reconciler — v0.14.0 R195 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/blueprint_code_reconciler.py |
| MOD-GATE_ENGINE | 配置complexity预算 / Config Complexity Budget — v0.16.0 R227 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/config_complexity_budget.py |
| MOD-GATE_ENGINE | 蓝图校验器 / Blueprint Validator — v0.8.0 R108 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/blueprint_validator.py |
| MOD-GATE_ENGINE | 并发变更deconfliction / Concurrent Change Deconfliction — v0.16.0 R230 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/concurrent_change_deconfliction.py |
| MOD-GATE_ENGINE | 配置治理 / Config Governance — v0.3.0 R8 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/config_governance.py |
| MOD-GATE_ENGINE | 检查点管理器 / Checkpoint Manager — v0.3.0 R18 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/checkpoint_manager.py |
| MOD-GATE_ENGINE | 数据库完整性 / DB Integrity Gate — v0.3.0 R17 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/db_integrity.py |
| MOD-GATE_ENGINE | cicdpre扫描器 / CI/CD Pre-Scanner — v0.8.0 R107 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/ci_cd_pre_scanner.py |
| MOD-GATE_ENGINE | 冲突仲裁 / Conflict Arbitration — v0.10.0 R130 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/conflict_arbitration.py |
| MOD-GATE_ENGINE | 数据质量门禁 / Data Quality Gate — v0.11.0 R143 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/data_quality_gate.py |
| MOD-GATE_ENGINE | cve扫描器 / CVE Scanner — v0.8.0 R106 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/cve_scanner.py |
| MOD-GATE_ENGINE | license合规 / License Compliance — v0.14.0 R198 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/license_compliance.py |
| MOD-GATE_ENGINE | merkle审计root / Merkle Audit Root — v0.8.0 R104 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/merkle_audit_root.py |
| MOD-GATE_ENGINE | llm成本路由器 / LLM Cost Router — v0.3.0 R20 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/llm_cost_router.py |
| MOD-GATE_ENGINE | 动态llm成本路由器 / Dynamic LLM Cost Router — v0.8.0 R109 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/dynamic_llm_cost_router.py |
| MOD-GATE_ENGINE | 紧急takeover / Emergency Takeover — v0.7.0 R88 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/emergency_takeover.py |
| MOD-GATE_ENGINE | federated安全 / Federated Security — v0.10.0 R131 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/federated_security.py |
| MOD-GATE_ENGINE | 元绩效门禁 / Meta Performance Gate — v0.11.0 R158 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/meta_performance_gate.py |
| MOD-GATE_ENGINE | parameterized安全门禁 / GateVerdict — GateVerdict | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/parameterized_safety_gate.py |
| MOD-GATE_ENGINE | 安全门禁l38l39 / Safety Gates L38-L39 — Deterministic Safety + Architectural  | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l38_l39.py |
| MOD-GATE_ENGINE | 安全门禁l40l41 / Safety Gates L40-L41 — Self-Integrity + Container Immutabili | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l40_l41.py |
| MOD-GATE_ENGINE | 安全门禁l42l43 / Safety Gates L42-L43 — Causal Integrity + Survivability | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l42_l43.py |
| MOD-GATE_ENGINE | 安全门禁l36l37 / Safety Gates L36-L37 — AI Code Integrity + Vibe Maintainabil | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l36_l37.py |
| MOD-GATE_ENGINE | 安全门禁l28l29 / Safety Gates L28-L29 — DR Readiness + Supply Chain (MOD-FEED | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l28_l29.py |
| MOD-GATE_ENGINE | 安全门禁l44l45 / Safety Gates L44-L45 — Operational Excellence + Causal Inter | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l44_l45.py |
| MOD-GATE_ENGINE | 安全门禁l50l51 / Safety Gates L50-L55 — Coherence + Integrity Ladder (double- | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l50_l51.py |
| MOD-GATE_ENGINE | 安全门禁l56l57 / Safety Gates L56-L57 — Evolutionary Integrity + Cross-Genera | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l56_l57.py |
| MOD-GATE_ENGINE | 安全门禁l46l47 / Safety Gates L46-L47 — Systemic Emergence + Ontological Cons | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l46_l47.py |
| MOD-GATE_ENGINE | 安全门禁l52l53 / Safety Gates L52-L53 — Boot Integrity + OSS License | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l52_l53.py |
| MOD-GATE_ENGINE | 安全门禁l58l59 / Safety Gates L58-L59 — Over-the-Horizon + Temporal Integrity | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l58_l59.py |
| MOD-GATE_ENGINE | 安全门禁l48l49 / Safety Gates L48-L49 — Supply Chain Integrity + Cognitive Sa | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l48_l49.py |
| MOD-GATE_ENGINE | 安全门禁l54l55 / Safety Gates L54-L55 — Final Gate + Full Integration | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l54_l55.py |
| MOD-GATE_ENGINE | 安全门禁l64l65 / Safety Gates L64-L65 — Financial Integrity + VibeOps:Solo | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l64_l65.py |
| MOD-GATE_ENGINE | 安全门禁l62l63 / Safety Gates L62-L63 — Infrastructure Reality + Market Reali | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l62_l63.py |
| MOD-GATE_ENGINE | 安全门禁l66l67 / Safety Gates L66-L67 — Financial Prudence + Full Integration | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l66_l67.py |
| MOD-GATE_ENGINE | 安全门禁l60l61 / Safety Gates L60-L61 — Environmental Grounding + Meta-System | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/safety_gate_l60_l61.py |
| MOD-GATE_ENGINE | 安全门禁 / _security_gates | D_FBL_VERIFICATION | generated | src/zephyr/feedback_loop/gates/_security_gates.py |
| MOD-GATE_ENGINE | 安全门禁 / _safety_gates | D_FBL_VERIFICATION | generated | src/zephyr/feedback_loop/gates/_safety_gates.py |
| MOD-GATE_ENGINE | 运营门禁 / _operational_gates | D_FBL_VERIFICATION | generated | src/zephyr/feedback_loop/gates/_operational_gates.py |
| MOD-GATE_ENGINE | 作用域creep监控器 / Scope Creep Monitor — v0.15.0 R220 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/gates/scope_creep_monitor.py |
| MOD-GATE_ENGINE | 治理门禁 / _governance_gates | D_FBL_VERIFICATION | generated | src/zephyr/feedback_loop/gates/_governance_gates.py |
| MOD-FEEDBACK_LOOP | 配置hotreload守卫 / Config Hot-Reload Guard — v0.40.0 R498 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/resilience/config_hot_reload_guard.py |
| MOD-FEEDBACK_LOOP | deadman开关 / Deadman Switch — v0.15.0 R212 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/resilience/deadman_switch.py |
| MOD-GATE_ENGINE | 包入口 / feedback-loop.gates — auto-generated package init. | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/gates/__init__.py |
| MOD-FEEDBACK_LOOP | 灾备自动化 / DR Automation — v0.14.0 R187 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/resilience/dr_automation.py |
| MOD-FEEDBACK_LOOP | 多instancecoord / Multi-Instance Coordinator — v0.14.0 R199 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/resilience/multi_instance_coord.py |
| MOD-FEEDBACK_LOOP | 资源starvation感知 / Resource Starvation Aware — v0.15.0 R209 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/resilience/resource_starvation_aware.py |
| MOD-FEEDBACK_LOOP | 代理技能守卫 / Agent Skill Guard — v0.14.0 R201 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/security/agent_skill_guard.py |
| MOD-FEEDBACK_LOOP | 拆分brainquorum / Split-Brain Quorum — v0.37.0 R451 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/resilience/split_brain_quorum.py |
| MOD-FEEDBACK_LOOP | gracefuldegradation规划器 / Graceful Degradation Planner — v0.40.0 R496 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/resilience/graceful_degradation_planner.py |
| MOD-FEEDBACK_LOOP | 振荡阻尼 / Oscillation Damping — v0.37.0 R450 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/resilience/oscillation_damping.py |
| MOD-FEEDBACK_LOOP | 依赖CVE关联器 / Dependency CVE Correlator — v0.14.0 R196 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/security/dep_cve_correlator.py |
| MOD-FEEDBACK_LOOP | 自API限流器防御 / Self API Throttle Defense — v0.39.0 R491 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/resilience/self_api_throttle_defense.py |
| MOD-FEEDBACK_LOOP | 远程attestation / Remote Attestation — v0.15.0 R211 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/security/remote_attestation.py |
| MOD-FEEDBACK_LOOP | 包入口 / feedback-loop.resilience — auto-generated package init. | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/resilience/__init__.py |
| MOD-FEEDBACK_LOOP | 神经劫持防护 / Wireheading Prevention — v0.37.0 R486 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/security/wireheading_prevention.py |
| MOD-FEEDBACK_LOOP | 指标提示扫描器 / Metric-Prompt Scanner — v0.15.0 R215 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/security/metric_prompt_scanner.py |
| MOD-FEEDBACK_LOOP | 包入口 / feedback-loop.security — auto-generated package init. | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/security/__init__.py |
| MOD-FEEDBACK_LOOP | 集成测试管线 / E2E Integration Test Pipeline — TASK-MOD-FEEDBACK_LOOP-0028  | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/tests/e2e/integration_test_pipeline.py |
| MOD-FEEDBACK_LOOP | 密钥rotation / Secret Rotation — v0.14.0 R189 | D_FEEDBACK_LOOP | stable | src/zephyr/feedback_loop/security/secret_rotation.py |
| MOD-FEEDBACK_LOOP | 行为explainability / Action Explainability — v0.3.0 R15 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/action_explainability.py |
| MOD-FEEDBACK_LOOP | 包入口 / feedback-loop.tests.e2e — auto-generated package init. | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/tests/e2e/__init__.py |
| MOD-FEEDBACK_LOOP | AI评论真实性 / AI Comment Veracity — v0.37.0 R459 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/ai_comment_veracity.py |
| MOD-FEEDBACK_LOOP | ab测试 / A/B Test Verifier — v0.9.0 R117 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/ab_test.py |
| MOD-FEEDBACK_LOOP | 级联回滚分析器 / Cascading Rollback Analyzer — v0.38.0 R482 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/cascading_rollback_analyzer.py |
| MOD-FEEDBACK_LOOP | 自动回滚 / Auto Rollback — v0.8.0 R93 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/auto_rollback.py |
| MOD-FEEDBACK_LOOP | 攻击模拟器 / Attack Simulator — v0.6.0 R57 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/attack_simulator.py |
| MOD-FEEDBACK_LOOP | 金丝雀修复 / Canary Repair — v0.8.0 R104b | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/canary_repair.py |
| MOD-FEEDBACK_LOOP | 跨会话知识完整性 / Cross-Session Knowledge Integrity — v0.16.0 R225 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/cross_session_knowledge_integrity.py |
| MOD-FEEDBACK_LOOP | 跨蓝图契约漂移 / Cross-Blueprint Contract Drift Monitor — v0.39.0 R490 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/cross_blueprint_contract_drift.py |
| MOD-FEEDBACK_LOOP | dry运行沙箱 / Dry Run Sandbox — v0.3.0 R19 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/dry_run_sandbox.py |
| MOD-FEEDBACK_LOOP | 跨模块集成 / Cross-Module Integration Verifier — v0.5.0 R39 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/cross_module_integration.py |
| MOD-FEEDBACK_LOOP | buildreproducibility验证器 / Build Reproducibility Verifier — v0.38.0 R484 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/build_reproducibility_verifier.py |
| MOD-FEEDBACK_LOOP | federated协议 / Federated Protocol — v0.10.0 R129 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/federated_protocol.py |
| MOD-FEEDBACK_LOOP | noLLM退化 / No-LLM Degradation Mode — v0.8.0 R94 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/no_llm_degradation.py |
| MOD-FEEDBACK_LOOP | golden测试external / Golden Test External — v0.15.0 R214 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/golden_test_external.py |
| MOD-FEEDBACK_LOOP | 数字孪生沙箱 / Digital Twin Sandbox — v0.6.0 R55 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/digital_twin_sandbox.py |
| MOD-FEEDBACK_LOOP | 仿真到实盘校准 / Sim2Real Calibration — v0.6.0 R56 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/sim2real_calibration.py |
| MOD-FEEDBACK_LOOP | 回滚完整性 / Rollback Integrity — v0.3.0 R18b | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/rollback_integrity.py |
| MOD-FEEDBACK_LOOP | stochastic诊断验证器 / Stochastic Diagnosis Verifier — v0.38.0 R483 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/stochastic_diagnosis_verifier.py |
| MOD-FEEDBACK_LOOP | 验证引擎 / verification_engine | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/verification_engine.py |
| MOD-FEEDBACK_LOOP | 包入口 / feedback-loop.verifiers — auto-generated package init. | D_FEEDBACK_LOOP | generated | src/zephyr/feedback_loop/verifiers/__init__.py |
| MOD-FEEDBACK_LOOP | TOCTOU重新验证 / TOCTOU Revalidation — v0.37.0 R458 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/toctou_revalidation.py |
| MOD-FEEDBACK_LOOP | 预防性修复 / Preventive Repair — v0.6.0 R69 | D_FBL_VERIFICATION | stable | src/zephyr/feedback_loop/verifiers/preventive_repair.py |
| MOD-GOV_AGENT_RBAC | — | D_SECURITY | generated | src/zephyr/governance/agent-rbac/contracts.py |
| MOD-INF-022 | 订单状态escalator / order_state_escalator | D_EX_CORE | stable | src/zephyr/governance/escalation/order_state_escalator.py |
| MOD-INF-024 | — | D_OPS | stable | src/zephyr/governance/ops_governance/budget_engine.py |
| MOD-INF-024 | — | D_OPS | stable | src/zephyr/governance/ops_governance/budget_tracker.py |
| MOD-INF-022 | — | D_OPS | stable | src/zephyr/governance/ops_governance/budget_handler.py |
| MOD-INF-024 | — | D_OPS | stable | src/zephyr/governance/ops_governance/budget_profile_manager.py |
| MOD-INF-024 | — | D_OPS | stable | src/zephyr/governance/ops_governance/budget_models.py |
| MOD-INF-024 | — | D_OPS | stable | src/zephyr/governance/ops_governance/cost_budget.py |
| MOD-INF-022 | — | D_OPS | stable | src/zephyr/governance/ops_governance/meta_observability.py |
| MOD-INF-024 | — | D_OPS | generated | src/zephyr/governance/ops_governance/token_budget.py |
| MOD-INF-023 | — | D_SECURITY | generated | src/zephyr/gov_drift/alert_router.py |
| MOD-INF-023 | — | D_SECURITY | stable | src/zephyr/gov_drift/cold_start.py |
| MOD-INF-023 | — | D_SECURITY | stable | src/zephyr/gov_drift/events.py |
| MOD-INF-023 | — | D_SECURITY | generated | src/zephyr/gov_drift/reconciler.py |
| MOD-INF-023 | — | D_SECURITY | generated | src/zephyr/gov_drift/runbook_generator.py |
| MOD-INF-011 | — | D_SECURITY | generated | src/zephyr/gov_drift/_core.py |
| MOD-INF-011 | — | D_SECURITY | generated | src/zephyr/gov_drift/_drift.py |
| MOD-INF-011 | — | D_SECURITY | generated | src/zephyr/gov_drift/_infrastructure.py |
| MOD-INF-011 | — | D_SECURITY | generated | src/zephyr/gov_drift/_analysis.py |
| MOD-INF-011 | — | D_SECURITY | generated | src/zephyr/gov_drift/_scanners.py |
| MOD-INF-023 | — | D_SECURITY | generated | src/zephyr/gov_drift/__main__.py |
| MOD-INF-003 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/git_batcher.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/classifier.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/dashboard.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/index_generator.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/lifecycle.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/metadata.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/models.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/reconciler.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/registry_adapter.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/asset_inventory/mcp_server.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/scanner.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/trust_anchor.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/asset_inventory/telemetry.py |
| MOD-INF-026 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/asset_inventory/__main__.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/all_completer.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/config_fixer.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/alignment_syncer.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/batch_fixer.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/compliance_auditor.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/dep_version_fixer.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/dedup_extractor.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/escalation_bridge.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/engine.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/event_hooks.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_budget.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/drift_fixer.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_reliability.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_report.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_pattern_miner.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_health_check.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/import_fixer.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_scheduler.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/fix_safety.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/llm_fix_adapter.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/self_heal_agent.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/interrupt_guard.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/models.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/shadow_workspace.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/scaffold_registrar.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/state_machine.py |
| MOD-INF-024 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/budget_enforcement/__init__.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/auto_fix_engine/__main__.py |
| MOD-INF-024 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/budget_enforcement/rbac_bridge.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/capacity_assurance/cross_module_integration.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/capacity_assurance/host_resource_governor.py |
| MOD-INF-031 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/auto_fix_engine/zombie_cleaner.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/capacity_assurance/risk_mitigation.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/capacity_assurance/tech_stack.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/capacity_assurance/budget_forecaster.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/capacity_assurance/kill_switch.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/capacity_assurance/sli_instrumentation.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/capacity_assurance/schema.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/capacity_assurance/token_budget.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/capacity_assurance/contracts/batch1_infra.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/capacity_assurance/contracts/batch3_integration.py |
| MOD-INF-001 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/capacity_assurance/contracts/contract_bus.py |
| MOD-H1_REDIS_HOT | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/h1_redis_hot/h1_cqrs_projectors.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/events/event_store.py |
| MOD-H1_REDIS_HOT | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/h1_redis_hot/h1_redis_reader.py |
| MOD-H1_REDIS_HOT | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/h1_redis_hot/h1_integration.py |
| MOD-H1_REDIS_HOT | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/h1_redis_hot/h1_redis_schema.py |
| MOD-H1_REDIS_HOT | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/h1_redis_hot/h1_redis_writer.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/health_monitor/health_aggregator.py |
| MOD-H1_REDIS_HOT | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/h1_redis_hot/__init__.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/impact/impact_propagator.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/impact/llm_impact_analyzer.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/lifecycle/scope_guard.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/lifecycle/task_lifecycle_manager.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/observability/trace_decorator.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/observability/notifier.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/backpressure_manager.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/backpressure_types.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/circuit_breaker_manager.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/ct_pipe_routing.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/models.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/llm_gateway.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/cost_tracker.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/dead_letter_queue.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/model_router.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/pipeline_lock.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/pipeline_agent_bridge.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/preemption_manager.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/routing_plugins.py |
| MOD-INF-009 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/pipeline/pipeline_roadmap.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/queue/task_queue.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/quality/quality_monitor.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/reliability/circuit_breaker.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/reliability/context_guard.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/queue/task_scheduler.py |
| MOD-GOVERNANCE | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/runtime/startup_shutdown.py |
| MOD-INF-005 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/script_system/gate_bridge.py |
| MOD-INF-005 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/script_system/finding.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/sla/sla_monitor.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/auto_bootstrap.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/health_aggregator.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/facade.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/contract_metrics.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/metrics_bridge.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/watchdog.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/_budget_telemetry_bridge.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/_trace_bridge.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/health_probes.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/logs/structured_sink.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/metrics/blueprint_metrics.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | stable | src/zephyr/infrastructure/system_telemetry/logs/__init__.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/archive/cold_stub.py |
| MOD-INF-015 | — | D_INFRA_RUNTIME | generated | src/zephyr/infrastructure/system_telemetry/traces/span_stub.py |
| MOD-INF-026 | — | D_INTEGRATION | generated | src/zephyr/integration/mcp_server.py |
| MOD-INF-009 | — | D_INTEGRATION | generated | src/zephyr/integration/ports.py |
| MOD-INF-028 | — | D_INTEGRATION | generated | src/zephyr/integration/llm_bridge.py |
| MOD-INF-009 | — | D_INTEGRATION | stable | src/zephyr/integration/pipeline_orchestrator.py |
| MOD-GOVERNANCE | — | D_INTEGRATION | stable | src/zephyr/integration/behavioral_admission/admission_response.py |
| MOD-INF-042 | — | D_INTEGRATION | stable | src/zephyr/integration/local_model/embedding_router.py |
| MOD-INF-001 | — | D_INTEGRATION | generated | src/zephyr/integration/budget_enforcer/degradation_spiral_detector.py |
| MOD-INF-042 | — | D_INTEGRATION | generated | src/zephyr/integration/local_model/local_model_scheduler.py |
| MOD-INF-042 | — | D_INTEGRATION | generated | src/zephyr/integration/local_model/ollama_embedding.py |
| MOD-INF-042 | — | D_INTEGRATION | generated | src/zephyr/integration/local_model/ollama_chat.py |
| MOD-INF-013 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/audit_logger.py |
| MOD-INF-013 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/blueprint_search_server.py |
| MOD-INF-013 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/doc_guard_server.py |
| MOD-INF-013 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/error_codes.py |
| MOD-INF-013 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/gate_engine_server.py |
| MOD-INF-013 | — | D_INTEGRATION | generated | src/zephyr/integration/mcp/resource_provider.py |
| MOD-INF-013 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/gateway_server.py |
| MOD-INF-013 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/rate_limiter.py |
| MOD-INF-013 | — | D_INTEGRATION | generated | src/zephyr/integration/mcp/sandbox_server.py |
| MOD-INF-013 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/task_manager_server.py |
| MOD-INF-013 | — | D_INTEGRATION | generated | src/zephyr/integration/mcp/prompt_provider.py |
| MOD-INF-013 | — | D_INTEGRATION | generated | src/zephyr/integration/mcp/vector_memory_server.py |
| MOD-INF-014 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/rule_discovery_server.py |
| MOD-INF-013 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/telemetry_server.py |
| MOD-INF-013 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/sentinel_server.py |
| MOD-INTEGRATION | — | D_INTEGRATION | generated | src/zephyr/integration/shared/contracts/errors/factor_computation_error.py |
| MOD-INF-009 | — | D_INTEGRATION | generated | src/zephyr/integration/shared/contracts/errors/risk_limit_violation_error.py |
| MOD-INF-009 | — | D_INTEGRATION | generated | src/zephyr/integration/shared/contracts/errors/signal_degradation_warning.py |
| MOD-INF-009 | — | D_INTEGRATION | generated | src/zephyr/integration/shared/contracts/errors/execution_rejection_error.py |
| MOD-INF-016 | — | D_INTEGRATION | generated | src/zephyr/integration/shared/events/event_bus_upgrade.py |
| MOD-INF-016 | — | D_INTEGRATION | generated | src/zephyr/integration/shared/events/dlq_bridge.py |
| MOD-INF-016 | — | D_INTEGRATION | generated | src/zephyr/integration/shared/events/event_schemas.py |
| MOD-INF-028 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/bm25_index.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/bridge_layer.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/chunk_strategy_router.py |
| MOD-INF-011 | — | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/delegated_vector_memory.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/collection_manager.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/collection_schemas.py |
| MOD-INF-011 | — | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/cross_collection_retriever.py |
| MOD-INF-011 | — | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/context_ingest.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/hybrid_retriever.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/design_principles.py |
| MOD-INF-011 | — | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/faiss_collection_manager.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/index_health_monitor.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/in_process_vector_memory.py |
| MOD-INF-011 | — | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/migrate_chroma_to_faiss.py |
| MOD-INF-011 | — | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/interface.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/in_memory_fake_vms.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/provenance_enforcer.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/in_memory_memory_backend.py |
| MOD-INF-011 | — | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/sqlite_metadata_store.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/retrieval_feedback.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/vms_errors.py |
| MOD-INF-011 | — | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/vector_bridge.py |
| MOD-INF-011 | — | D_INTEGRATION | generated | src/zephyr/integration/vector_memory/vms_memory_backend.py |
| MOD-INF-021 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_drift_detector.py |
| MOD-INF-011 | — | D_INTEGRATION | stable | src/zephyr/integration/vector_memory/vms_schemas.py |
| MOD-INF-036 | — | D_INTELLIGENCE | generated | src/zephyr/intelligence/model_evaluation/activate.py |
| MOD-INF-036 | — | D_INTELLIGENCE | generated | src/zephyr/intelligence/model_evaluation/_memory_backend.py |
| MOD-INF-036 | — | D_INTELLIGENCE | generated | src/zephyr/intelligence/model_evaluation/reranker.py |
| MOD-INF-036 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_evaluation/unified_memory_api.py |
| MOD-INF-036 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_evaluation/inference_base.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/cli.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/capability_passport.py |
| MOD-INF-036 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_evaluation/implementations/default_inference_engine.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/deepseek_v4_chat.py |
| MOD-INF-034 | — | D_INTELLIGENCE | generated | src/zephyr/intelligence/model_profiling/benchmark_suite.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/exam_checks.py |
| MOD-INF-034 | — | D_INTELLIGENCE | generated | src/zephyr/intelligence/model_profiling/case_assembler.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/exam_judge.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/exam_orchestrator.py |
| MOD-INF-034 | — | D_INTELLIGENCE | generated | src/zephyr/intelligence/model_profiling/exam_executor.py |
| MOD-INF-034 | — | D_INTELLIGENCE | generated | src/zephyr/intelligence/model_profiling/exam_rubric.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/job_matcher.py |
| MOD-INF-034 | — | D_INTELLIGENCE | generated | src/zephyr/intelligence/model_profiling/profiler.py |
| MOD-INF-034 | — | D_INTELLIGENCE | generated | src/zephyr/intelligence/model_profiling/task_model_learner.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/results_writer.py |
| MOD-INF-034 | — | D_INTELLIGENCE | generated | src/zephyr/intelligence/model_profiling/pipeline_routing/cli.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/pipeline_routing/benchmark_suite.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/model_discovery.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/provider_data.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/pipeline_routing/results_writer.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/pipeline_routing/task_model_learner.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | src/zephyr/intelligence/model_profiling/pipeline_routing/profiler.py |
| MOD-ML_SERVE | — | D_ML_SERVE | generated | src/zephyr/ml_serve/api/__init__.py |
| MOD-ML_SERVE | — | D_ML_SERVE | generated | src/zephyr/ml_serve/infrastructure/__init__.py |
| MOD-ML_SERVE | — | D_ML_SERVE | generated | src/zephyr/ml_serve/__init__.py |
| MOD-ML_SERVE | — | D_ML_SERVE | generated | src/zephyr/ml_serve/core/__init__.py |
| MOD-ML_SERVE | — | D_ML_SERVE | generated | src/zephyr/ml_serve/_extensions/__init__.py |
| MOD-ML_SERVE | — | D_ML_SERVE | generated | src/zephyr/ml_serve/models/__init__.py |
| MOD-ML_SERVE | — | D_ML_SERVE | generated | src/zephyr/ml_serve/services/__init__.py |
| MOD-FEEDBACK_LOOP | — | D_ORCHESTRATOR | generated | src/zephyr/orchestrator/contracts/alert_handler.py |
| MOD-INF-016 | — | D_PF_ALLOC | generated | src/zephyr/pf_alloc/strategy_lifecycle_event.py |
| MOD-POS_SERVICES | — | D_POSITION | generated | src/zephyr/position/services/__init__.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/red_blue_validator/__init__.py |
| MOD-RPT-004 | — | D_REPORTING | stable | src/zephyr/reporting/realtime_pnl_dashboard.py |
| MOD-RPT-013 | — | D_REPORTING | stable | src/zephyr/reporting/report_version_manager.py |
| MOD-RPT-017 | — | D_REPORTING | stable | src/zephyr/reporting/report_watermark_tracker.py |
| MOD-INF-029 | — | D_SECURITY | stable | src/zephyr/security/access_control/orphan_judge/cascade_analyzer.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/config_loader.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/drift_bridge.py |
| MOD-INF-029 | — | D_SECURITY | stable | src/zephyr/security/access_control/orphan_judge/deprecation_tracker.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/db.py |
| MOD-INF-029 | — | D_SECURITY | stable | src/zephyr/security/access_control/orphan_judge/decision_table.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/escalation_bridge.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/duplicate_detector.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/feedback_bridge.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/kb_bridge.py |
| MOD-INF-029 | — | D_SECURITY | stable | src/zephyr/security/access_control/orphan_judge/judge.py |
| MOD-INF-029 | — | D_SECURITY | stable | src/zephyr/security/access_control/orphan_judge/orphan_detector.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/mcp_integration.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/orphan_collector.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/reference_graph_engine.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/rbac_bridge.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/models.py |
| MOD-INF-029 | — | D_SECURITY | stable | src/zephyr/security/access_control/orphan_judge/safety_fence.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/registration_checker.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/__main__.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/standalone_evaluator.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/unique_analyzer.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/swid_tag.py |
| MOD-INF-029 | — | D_SECURITY | generated | src/zephyr/security/access_control/orphan_judge/report_generator.py |
| MOD-INF-030 | — | D_SECURITY | stable | src/zephyr/security/adversarial_validation/async_monitor.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/blast_radius.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/ai_attack_generator.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/attack_registry.py |
| MOD-INF-030 | — | D_SECURITY | stable | src/zephyr/security/adversarial_validation/circuit_breaker.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/cleanup.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/bypass_recorder.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/commit_trigger.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/cold_start.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/constitution_guard.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/cli.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/defense_runner.py |
| MOD-INF-030 | — | D_SECURITY | stable | src/zephyr/security/adversarial_validation/game_day_scheduler.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/game_day_runner.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/scenario_loader.py |
| MOD-SEC-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/validator_event_bridge.py |
| MOD-INF-030 | — | D_SECURITY | stable | src/zephyr/security/adversarial_validation/models.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/mcp_endpoints.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/validator.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/steady_state.py |
| MOD-INF-030 | — | D_SECURITY | generated | src/zephyr/security/adversarial_validation/__main__.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/gateway.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/behavior_audit_logger.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/input_sanitizer.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/process_sandbox.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/layers/l0_supply_chain.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/runtime_interceptor.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/protocol.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/layers/l1_input.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/layers/l2_prompt_protection.py |
| MOD-LLM_SECURITY | — | D_SECURITY | generated | src/zephyr/security/llm_defense/llm_security/dashboard/app.py |
| MOD-LLM_SECURITY | — | D_SECURITY | generated | src/zephyr/security/llm_defense/llm_security/layers/l6_data_flow.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/layers/l2a_process_sandbox.py |
| MOD-LLM_SECURITY | — | D_SECURITY | generated | src/zephyr/security/llm_defense/llm_security/layers/l8_compliance.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/layers/l4_agent.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/layers/l5_resource_protection.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/layers/l3_output.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/layers/l6_observability.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/layers/l8_multi_agent.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/patterns/injection_patterns.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/patterns/secrets.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/self_protection/adversarial_mutator.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/self_protection/code_integrity.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/self_protection/red_team_scanner.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/self_protection/l7_validation.py |
| MOD-LLM_SECURITY | — | D_SECURITY | stable | src/zephyr/security/llm_defense/llm_security/self_protection/isolation.py |
| MOD-SELL_DECISION | — | D_SELL_DECISION | generated | src/zephyr/sell_decision/api/__init__.py |
| MOD-SELL_DECISION | — | D_SELL_DECISION | generated | src/zephyr/sell_decision/__init__.py |
| MOD-SELL_DECISION | — | D_SELL_DECISION | generated | src/zephyr/sell_decision/services/__init__.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/event_bus.py |
| MOD-SELL_DECISION | — | D_SELL_DECISION | generated | src/zephyr/sell_decision/infrastructure/__init__.py |
| MOD-SELL_DECISION | — | D_SELL_DECISION | generated | src/zephyr/sell_decision/models/__init__.py |
| MOD-SELL_DECISION | — | D_SELL_DECISION | generated | src/zephyr/sell_decision/_extensions/__init__.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/adaptation/execution_tuner.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/__version__.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/ai_guards/ai_audit_guard.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/alerts/alert_manager.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/ai_guards/combinatorial_gate.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/ai_guards/core_integrity_guard.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/adaptation/prompt_version_manager.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/alerts/heartbeat_server.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/api/dos_launcher.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/alerts/alert_precision_tracker.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/alerts/alert_escalation.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/alerts/dual_channel_alert.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/api/api_index.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/api/api_client.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/blueprint_tools/ai_understandability_constraint.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/blueprint_tools/blueprint_code_auditor.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/blueprint_tools/blueprint_scorer.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/capacity_governance/capacity_calibrator.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/capacity_governance/adaptive_sampler.py |
| SH-MAIN-001 | — | D_SHARED | stable | src/zephyr/shared/blueprint_tools/blueprint_decomposer.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/capacity_governance/capacity_digital_twin.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/capacity_governance/budget_aware_prompt.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/capacity_governance/cost_estimator.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/capacity_governance/capacity_runbook_generator.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/capacity_governance/capacity_fingerprint.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/capacity_governance/dependency_capacity_guard.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/compensation/saga_compensator.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/capacity_governance/model_capacity_probe.py |
| MOD-INF-016 | — | D_INTEGRATION | stable | src/zephyr/shared/contracts/approval_types.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/contract_bus.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/context/context_engine.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/llm_gateway_protocol.py |
| MOD-INF-016 | — | D_INTEGRATION | stable | src/zephyr/shared/contracts/rollback_types.py |
| MOD-INF-035 | — | D_INTEGRATION | stable | src/zephyr/shared/contracts/runtime_types.py |
| MOD-INF-016 | — | D_INTEGRATION | generated | src/zephyr/shared/contracts/protocols.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/skill_protocol.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/task_repository_protocol.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/backpressure/pause.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/backpressure/_types.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/backpressure/throttle.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/backpressure/resume.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/contracts/enums/order_enums.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/errors/data_quality_error.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/errors/execution_rejection_error.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/errors/contract_violation_error.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/enums/__init__.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/errors/factor_computation_error.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/errors/risk_limit_violation_error.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/contracts/escalation/budget_alert.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/execution/capital_allocation_result.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/errors/signal_degradation_warning.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/execution/execution_report.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/execution/model_serving_request.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/execution/fill.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/experiment/experiment_result.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/external/ext_001.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/experiment/model_serving_response.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/execution/order.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/external/ext_002.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/external/ext_003.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/external/ext_004.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/contracts/portfolio/money.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/contracts/identity/permission.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/market/instrument.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/risk/compliance_rule.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/portfolio/position.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/risk/risk_limits.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/contracts/risk/risk_metrics.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/contracts/risk/risk_dashboard_snapshot.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/contracts/risk/risk_validator_protocol.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/contracts/security/security_decision.py |
| SH-DB-001 | — | D_SHARED | generated | src/zephyr/shared/database/database_crud_mixin.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/dependency/dependency_graph.py |
| SH-DB-001 | — | D_SHARED | generated | src/zephyr/shared/database/__init__.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/draft/draft_assistant.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/events/event_bus_upgrade.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/events/dlq_bridge.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/events/hook_dispatcher.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/events/event_schemas.py |
| MOD-GOVERNANCE | — | D_INTEGRATION | stable | src/zephyr/shared/evaluation/evals.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/events/dlq.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/events/upgrade_strategy.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/foundation/constants.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/events/event_reactor.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/foundation/errors.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/foundation/types.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/foundation/env.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/foundation/models.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/foundation/flags.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/foundation/deprecation.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/infra/limiter.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/infra/idempotency.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/infra/lock.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/infra/observer.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/infra/cache.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/infra/outbox.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/infra/process_lifecycle_gateway.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/io/content_fingerprint.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/io/file_utils.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/io/frontmatter_utils.py |
| MOD-SHARED-002 | — | D_SHARED | generated | src/zephyr/shared/io/sqlite_factory.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/io/paths.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/io/io_cache.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/io/streaming_reader.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/io/serialization.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/infra/process_pool.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/shared/lifecycle/daemon_registry.py |
| MOD-SHR_IO_YAML | — | D_SHARED | generated | src/zephyr/shared/io/yaml_utils.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/io/workspace_telemetry.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/lifecycle/health.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/lifecycle/healthcheck_service.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/lifecycle/health_discovery.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/shared/lifecycle/hooks.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/shared/lifecycle/lazy_loader.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/lifecycle/longevity_monitor.py |
| MOD-INF-016 | — | D_INFRA_RUNTIME | stable | src/zephyr/shared/lifecycle/resource_optimization_models.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/lifecycle/task_heartbeat.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/lifecycle/ttl_cleanup_engine.py |
| SH-MAIN-001 | — | D_SHARED | stable | src/zephyr/shared/maintenance/dogfooding.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/maintenance/code_economy_analyzer.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/maintenance/autonomy_monitor.py |
| SH-MAIN-001 | — | D_SHARED | stable | src/zephyr/shared/maintenance/handbook.py |
| MOD-INF-038 | — | D_SHARED | stable | src/zephyr/shared/lifecycle/state_machine.py |
| SH-MAIN-001 | — | D_SHARED | stable | src/zephyr/shared/maintenance/zero_config.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/observability/metrics_server.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/observability/metrics.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/observability/reasoning_spans.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/maintenance/slo_review_assistant.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/observability/tracing.py |
| MOD-INF-044 | — | D_SHARED | stable | src/zephyr/shared/observability/dashboard/__init__.py |
| MOD-SHARED-001 | — | D_SHARED | generated | src/zephyr/shared/protocols/a2a/a2a_coordination.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/protocols/module_birth_registry.py |
| MOD-SHARED-001 | — | D_SHARED | generated | src/zephyr/shared/protocols/ports.py |
| MOD-SHARED-001 | — | D_SHARED | generated | src/zephyr/shared/protocols/a2a/a2a_protocol.py |
| MOD-SHARED-001 | — | D_SHARED | generated | src/zephyr/shared/protocols/registry.py |
| MOD-SHARED-001 | — | D_SHARED | generated | src/zephyr/shared/protocols/a2a/a2a_schemas.py |
| MOD-SHARED-001 | — | D_SHARED | generated | src/zephyr/shared/protocols/a2a/a2a_registry.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/reliability/diff_planner.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/resilience/circuit_breaker.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/reliability/retry_handler.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/resilience/degradation_chain.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/resilience/fault_isolator.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/resilience/error_budget_tracker.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/resilience/fallback.py |
| MOD-GOVERNANCE | — | D_INTEGRATION | stable | src/zephyr/shared/resilience/durable_execution.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/schema/base_config.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/schema/severity_types.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/resilience/retry.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/schema/schemas.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/schema/task_types.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/schema/schema_registry.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/schema/execution_model.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/security/sandbox_executor.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/security/ssot_guard.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/security/capability.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/security/secrets.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/session/session_boundary.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/session/session_continuity.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/session/session_audit.py |
| MOD-INF-016 | — | D_SHARED | generated | src/zephyr/shared/utils/async_utils.py |
| MOD-SHR_CONVERTERS | — | D_SHARED | stable | src/zephyr/shared/utils/converters.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/utils/cli_summary.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/utils/context.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/utils/db_utils.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/utils/diff_utils.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/utils/migration.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/utils/pagination.py |
| MOD-GOVERNANCE | — | D_INTEGRATION | stable | src/zephyr/shared/versioning/version_negotiation.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/utils/zephyr_logger.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/utils/time_utils.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/utils/testing.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/utils/logging.py |
| MOD-INF-016 | — | D_SHARED | stable | src/zephyr/shared/versioning/vibe_experiment_tracker.py |
| MOD-SIGNAL_ASHARE | 包入口 / __init__ | D_ASHARE_SIGNAL | generated | src/zephyr/signal_ashare/api/__init__.py |
| MOD-SIGNAL_ASHARE | 包入口 / __init__ | D_ASHARE_SIGNAL | generated | src/zephyr/signal_ashare/infrastructure/__init__.py |
| MOD-SIGNAL_ASHARE | 包入口 / __init__ | D_ASHARE_SIGNAL | generated | src/zephyr/signal_ashare/core/__init__.py |
| MOD-SIGNAL_ASHARE | 包入口 / __init__ | D_ASHARE_SIGNAL | generated | src/zephyr/signal_ashare/services/__init__.py |
| MOD-SIGNAL_ASHARE | 包入口 / __init__ | D_ASHARE_SIGNAL | generated | src/zephyr/signal_ashare/models/__init__.py |
| MOD-INF-040 | — | D_SIGQC | generated | src/zephyr/signal_quality/__init__.py |
| MOD-SIGQC-001 | — | D_SIGQC | generated | src/zephyr/signal_quality/degradation_monitor_base.py |
| MOD-SIM-024 | — | D_SIMULATION | stable | src/zephyr/simulation/deflated_sharpe_calculator.py |
| MOD-SIM-022 | — | D_SIMULATION | stable | src/zephyr/simulation/look_ahead_bias_detector.py |
| MOD-SIM-021 | — | D_SIMULATION | stable | src/zephyr/simulation/parameter_robustness_tester.py |
| MOD-SIM-023 | — | D_SIMULATION | stable | src/zephyr/simulation/sharpe_calculator_fixer.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/ai_audit_logger.py |
| MOD-INF-033 | — | D_TRADING | stable | src/zephyr/trading/admission_controller.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/action_dispatcher.py |
| SH-DB-001 | — | D_TRADING | stable | src/zephyr/trading/autopilot.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/auto_integrator.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/auto_task_generator.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/boot_hooks.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/capability_sync.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/capability_registry.py |
| SH-DB-001 | — | D_TRADING | stable | src/zephyr/trading/conductor.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/auto_runtime_core.py |
| MOD-INF-033 | — | D_TRADING | stable | src/zephyr/trading/gpu_consensus_scheduler.py |
| MOD-RESOURCE_OPTIMIZATION_ENGINE | — | D_TRADING | generated | src/zephyr/trading/gpu_monitor.py |
| MOD-RESOURCE_OPTIMIZATION_ENGINE | — | D_TRADING | stable | src/zephyr/trading/ide_health_daemon.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/dream_cycle.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/finalizer.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/health_monitor.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/integration_registry.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/module_onboarding_scanner.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/lifecycle_manager.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | generated | src/zephyr/trading/ports.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/night_shift_queue.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | generated | src/zephyr/trading/orphan_detector.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/runtime_config.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/resource_optimization.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/task_gate.py |
| MOD-RESOURCE_OPTIMIZATION_ENGINE | — | D_TRADING | generated | src/zephyr/trading/speed_baseline_checker.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/stop_gate.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/status_dashboard.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/work_dag.py |
| MOD-INF-035 | — | D_TRADING | generated | src/zephyr/trading/action_dispatcher/_annotation_writer.py |
| MOD-RESOURCE_OPTIMIZATION_ENGINE | — | D_INFRA_RUNTIME | generated | src/zephyr/trading/zombie_scanner.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | generated | src/zephyr/trading/windows_service.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | stable | src/zephyr/trading/work_orchestrator.py |
| MOD-INF-035 | — | D_INFRA_RUNTIME | generated | src/zephyr/trading/__main__.py |
| MOD-INF-035 | — | D_TRADING | generated | src/zephyr/trading/action_dispatcher/_file_lifecycle_manager.py |
| MOD-INF-035 | — | D_TRADING | generated | src/zephyr/trading/action_dispatcher/__init__.py |
| MOD-INF-035 | — | D_TRADING | generated | src/zephyr/trading/action_dispatcher/_search_replace_engine.py |
| MOD-INF-035 | — | D_TRADING | generated | src/zephyr/trading/action_dispatcher/_audit_log_writer.py |
| MOD-TRADING-001 | — | D_TRADING | generated | src/zephyr/trading/trading_contracts/factories.py |
| MOD-INF-016 | — | D_TRADING | generated | src/zephyr/trading/trading_contracts/execution/execution_rejection_error.py |
| MOD-INF-016 | — | D_TRADING | stable | src/zephyr/trading/trading_contracts/execution/capital_allocation_result.py |
| MOD-INF-016 | — | D_TRADING | stable | src/zephyr/trading/trading_contracts/execution/fill.py |
| MOD-INF-016 | — | D_TRADING | generated | src/zephyr/trading/trading_contracts/market/signal_degradation_warning.py |
| MOD-INF-016 | — | D_TRADING | stable | src/zephyr/trading/trading_contracts/execution/model_serving_request.py |
| MOD-INF-016 | — | D_TRADING | stable | src/zephyr/trading/trading_contracts/execution/execution_report.py |
| MOD-INF-016 | — | D_TRADING | generated | src/zephyr/trading/trading_contracts/market/instrument.py |
| MOD-INF-016 | — | D_TRADING | stable | src/zephyr/trading/trading_contracts/execution/position.py |
| MOD-INF-016 | — | D_TRADING | stable | src/zephyr/trading/trading_contracts/execution/order.py |
| MOD-INF-016 | — | D_TRADING | stable | src/zephyr/trading/trading_contracts/risk/risk_limit_violation_error.py |
| MOD-INF-016 | — | D_TRADING | generated | src/zephyr/trading/trading_contracts/risk/risk_limits.py |
| MOD-INF-016 | — | D_TRADING | stable | src/zephyr/trading/trading_contracts/risk/risk_metrics.py |
| MOD-INF-016 | — | D_TRADING | stable | src/zephyr/trading/trading_contracts/risk/risk_dashboard_snapshot.py |
| MOD-INF-016 | — | D_TRADING | stable | src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py |
| MOD-INF-016 | — | D_TRADING | stable | src/zephyr/trading/trading_contracts/risk/risk_validator_protocol.py |
| MOD-INF-034 | — | D_INTELLIGENCE | stable | scripts/calibrate_model_diff.py |
| MOD-INF-034 | — | D_INTELLIGENCE | generated | scripts/quick_profile.py |
| MOD-OPS-018 | — | D_OPS | generated | scripts/setup_dev_env.py |
| MOD-INF-043 | 恢复演练：轮询备份完成 → 恢复小表到临时库 → 行数校验 → 清理。 / _recovery_drill | D_DATA | generated | scripts/ch/_recovery_drill.py |
| MOD-GOV_GATE_CACHE | — | D_OPS | generated | scripts/governance/observability/gate_cache.py |
| MOD-BT-022 | — | D_BACKTEST | generated | tests/backtest/test_data_quality_checker.py |
| MOD-BT-020 | — | D_BACKTEST | generated | tests/backtest/test_cache_manager.py |
| MOD-BT-023 | — | D_BACKTEST | generated | tests/backtest/test_anomaly_diagnoser.py |
| MOD-BT-026 | — | D_BACKTEST | generated | tests/backtest/test_nan_processor.py |
| MOD-BT-021 | — | D_BACKTEST | generated | tests/backtest/test_param_analyzer.py |
| MOD-BT-017 | — | D_BACKTEST | generated | tests/backtest/test_data_handler_pit.py |
| MOD-BT-018 | — | D_BACKTEST | generated | tests/backtest/test_decay_monitor.py |
| MOD-BT-024 | — | D_BACKTEST | generated | tests/backtest/test_result_comparator.py |
| MOD-BT-017 | — | D_BACKTEST | generated | tests/backtest/test_scheduler.py |
| MOD-BT-019 | — | D_BACKTEST | generated | tests/backtest/test_report_generator.py |
| MOD-E2E-001 | — | D_BACKTEST | generated | tests/factor/test_backtest_factor_e2e.py |
| MOD-TEST_SURGE_FALL_STRATEGY | — | D_PF_CORE | generated | tests/pf_core/test_intraday_surge_fall_strategy.py |
| MOD-TEST_STRATEGY_RUNNER_TICK | — | D_PF_CORE | generated | tests/pf_core/test_strategy_runner_tick.py |
| MOD-RPT-017 | — | D_REPORTING | generated | tests/reporting/test_report_watermark_tracker.py |
| MOD-RPT-004 | — | D_REPORTING | generated | tests/reporting/test_realtime_pnl_dashboard.py |
| MOD-RPT-013 | — | D_REPORTING | generated | tests/reporting/test_report_version_manager.py |
| MOD-SIM-024 | — | D_SIMULATION | generated | tests/simulation/test_deflated_sharpe_calculator.py |
| MOD-SIM-023 | — | D_SIMULATION | generated | tests/simulation/test_sharpe_calculator_fixer.py |
| MOD-SIM-022 | — | D_SIMULATION | generated | tests/simulation/test_look_ahead_bias_detector.py |
| MOD-SIM-021 | — | D_SIMULATION | generated | tests/simulation/test_parameter_robustness_tester.py |
| MOD-H1_REDIS_HOT | — | D_INFRA_RUNTIME | generated | tests/zephyr/data/test_tick_redis_cache.py |
| MOD-RUNTIME_INTRADAY | — | D_INFRA_RUNTIME | generated | tests/zephyr/runtime/test_intraday_main.py |
| MOD-TEST_METRICS_SERVER | — | D_SHARED | generated | tests/zephyr/shared/observability/test_metrics_server.py |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/data_product_manager/ |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/data_lake_manager/ |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/knowledge_cleaning/ |
| MOD-L00-004 | — | D_DATA | deprecated | src/zephyr/data/realtime_push_manager/ |
| MOD-L00-004 | — | D_DATA | deprecated | src/zephyr/data/feature_store/ |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/data_profiling/ |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/synthetic_data/ |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/training_data_manager/ |
| MOD-L00-004 | — | D_DATA | deprecated | src/zephyr/data/data_observability/ |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/data_compression/ |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/schema_evolution/ |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/stream_processing/ |
| MOD-L00-004 | — | D_DATA | deprecated | src/zephyr/data/symbol_normalizer/ |
| MOD-L00-004 | — | D_DATA | deprecated | src/zephyr/data/tick_data_manager/ |
| MOD-INF-038 | 包入口 / __init__ | D_ASHARE_SIGNAL | stable | src/zephyr/signal_ashare/__init__.py |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/data_catalog/ |
| MOD-INF-013 | — | D_INTEGRATION | stable | src/zephyr/integration/mcp/_base_server.py |
| MOD-L00-004 | 可观测性指标采集（MOD-L00-004 §11）。 / metrics | D_DATA | generated | src/zephyr/data/metrics.py |
| MOD-L00-004 | 统一进度存储（MOD-L00-004 §7）。 / progress_store | D_DATA | generated | src/zephyr/data/progress_store.py |
| MOD-L00-004 | 板块klinedownloader / sector_kline_downloader | D_DATA | stable | src/zephyr/data/sector_kline_downloader.py |
| MOD-L00-004 | 包入口 / __init__ | D_DATA | generated | src/zephyr/data/implementations/__init__.py |
| MOD-ALT_DATA | 包入口 / __init__ | D_ALT_DATA | generated | src/zephyr/alt_data/infrastructure/__init__.py |
| MOD-ALT_DATA | 包入口 / __init__ | D_ALT_DATA | generated | src/zephyr/alt_data/services/__init__.py |
| MOD-L00-004 | A 股交易日历守卫（MOD-L00-004）。 / trading_calendar | D_DATA | generated | src/zephyr/data/trading_calendar.py |
| MOD-L00-004 | #ARCH-CH-021 P0-5: 财报 PIT 查询能力测试。 / test_pit_query | D_DATA | generated | tests/data/test_pit_query.py |
| MOD-L00-004 | tickflow提供器 / tickflow_provider | D_DATA | generated | src/zephyr/data/implementations/tickflow_provider.py |
| MOD-L00-004 | ch读取器 / ch_reader | D_DATA | generated | src/zephyr/data/ch_reader.py |
| MOD-L00-004 | tdx提供器 / tdx_provider | D_DATA | generated | src/zephyr/data/implementations/tdx_provider.py |
| MOD-L00-004 | 质量门禁 / quality_gate | D_DATA | stable | src/zephyr/data/quality_gate.py |
| MOD-DATA_SEC | 包入口 / __init__ | D_DATA_SEC | generated | src/zephyr/data_security/_extensions/__init__.py |
| MOD-DATA_SEC | 包入口 / __init__ | D_DATA_SEC | generated | src/zephyr/data_security/services/__init__.py |
| MOD-ALT_DATA | 包入口 / __init__ | D_ALT_DATA | generated | src/zephyr/alt_data/core/__init__.py |
| MOD-L00-004 | table注册表 / table_registry | D_DATA | stable | src/zephyr/data/table_registry.py |
| MOD-L00-004 | 任务依赖图 + 优先级队列（MOD-L00-004 §6.3 任务依赖图 + § / task_queue | D_DATA | generated | src/zephyr/data/task_queue.py |
| MOD-L00-005 | 测试跨源校验器 / test_cross_source_validator | D_DATA | generated | tests/zephyr/data/test_cross_source_validator.py |
| MOD-DATA_ENG | 包入口 / __init__ | D_DATA_ENG | generated | src/zephyr/data_eng/core/__init__.py |
| MOD-L00-004 | wal写入器 / wal_writer | D_DATA | stable | src/zephyr/data/wal_writer.py |
| MOD-DATA_GOV | 包入口 / __init__ | D_DATA_GOV | generated | src/zephyr/data_governance/api/__init__.py |
| MOD-DATA_ENG | 包入口 / __init__ | D_DATA_ENG | generated | src/zephyr/data_eng/_extensions/__init__.py |
| MOD-L00-004 | #ARCH-CH-021 P0-4: 写入路径异常值校验器四门禁测试。 / test_market_quality_validator | D_DATA | generated | tests/data/test_market_quality_validator.py |
| MOD-DATA_GOV | 包入口 / __init__ | D_DATA_GOV | generated | src/zephyr/data_governance/infrastructure/__init__.py |
| MOD-ALT_DATA | 包入口 / __init__ | D_ALT_DATA | generated | src/zephyr/alt_data/api/__init__.py |
| MOD-L00-004 | 主入口 / __main__ | D_DATA | generated | src/zephyr/data/__main__.py |
| MOD-DATA_GOV | 包入口 / __init__ | D_DATA_GOV | generated | src/zephyr/data_governance/models/__init__.py |
| MOD-DATA_SEC | 包入口 / __init__ | D_DATA_SEC | generated | src/zephyr/data_security/__init__.py |
|  | 任务 / tasks | D_DATA | generated | src/zephyr/data/config/tasks.yaml |
| MOD-L00-004 | rss提供器 / rss_provider | D_DATA | generated | src/zephyr/data/implementations/rss_provider.py |
| MOD-L00-004 | 能力校验器 / capability_validator | D_DATA | generated | src/zephyr/data/capability_validator.py |
| MOD-L00-004 | 数据源集成器 CLI（MOD-L00-004 §8.4）。 / cli | D_DATA | stable | src/zephyr/data/cli.py |
| MOD-DATA_SEC | 包入口 / __init__ | D_DATA_SEC | generated | src/zephyr/data_security/infrastructure/__init__.py |
| MOD-L00-004 | 数据源调度编排层（MOD-L00-004 §6）。 / scheduler | D_DATA | generated | src/zephyr/data/scheduler.py |
| MOD-DATA_ENG | 包入口 / __init__ | D_DATA_ENG | generated | src/zephyr/data_eng/infrastructure/__init__.py |
| MOD-DATA_SEC | 包入口 / __init__ | D_DATA_SEC | generated | src/zephyr/data_security/models/__init__.py |
| MOD-DATA_GOV | 包入口 / __init__ | D_DATA_GOV | generated | src/zephyr/data_governance/services/__init__.py |
| MOD-L00-004 | akshare提供器 / akshare_provider | D_DATA | generated | src/zephyr/data/implementations/akshare_provider.py |
| MOD-DATA_GOV | 包入口 / __init__ | D_DATA_GOV | generated | src/zephyr/data_governance/__init__.py |
| MOD-DATA_GOV | 包入口 / __init__ | D_DATA_GOV | generated | src/zephyr/data_governance/core/__init__.py |
|  | 调度计划 / schedule | D_DATA | generated | src/zephyr/data/config/schedule.yaml |
| MOD-L00-004 | 提供器基类 / provider_base | D_DATA | generated | src/zephyr/data/provider_base.py |
| MOD-L00-004 | 策略注册表 / policy_registry | D_DATA | stable | src/zephyr/data/policy_registry.py |
| MOD-DATA_ENG | 包入口 / __init__ | D_DATA_ENG | generated | src/zephyr/data_eng/api/__init__.py |
| MOD-L00-004 | 数据源错误分类器——根据错误字符串判断可恢复性。 / error_classifier | D_DATA | stable | src/zephyr/data/error_classifier.py |
| MOD-L00-004 | 启动调度器 / start_scheduler | D_DATA | generated | scripts/start_scheduler.ps1 |
| MOD-L00-004 | eastmoney新闻提供器 / eastmoney_news_provider | D_DATA | generated | src/zephyr/data/implementations/eastmoney_news_provider.py |
| MOD-L00-004 | 新闻数据去重模块（MOD-L00-004 §4.3）。 / news_dedup | D_DATA | generated | src/zephyr/data/news_dedup.py |
| MOD-L00-004 | pit查询 / pit_query | D_DATA | stable | src/zephyr/data/pit_query.py |
| MOD-L00-004 | 包入口 / __init__ | D_DATA | stable | src/zephyr/data/__init__.py |
| MOD-L00-005 | 数据源冗余与热切换模块（MOD-L00-005）。 / __init__ | D_DATA | generated | src/zephyr/data/redundant_source/__init__.py |
| MOD-L00-004 | 批量聚合写入器（MOD-L00-004 §18.3 裁定 #ARCH-CH-003 / buffered_writer | D_DATA | generated | src/zephyr/data/buffered_writer.py |
| MOD-L00-005 | 测试逐笔订阅器 / test_tick_subscriber | D_DATA | generated | tests/zephyr/data/test_tick_subscriber.py |
| MOD-DATA_ENG | 包入口 / __init__ | D_DATA_ENG | generated | src/zephyr/data_eng/services/__init__.py |
| MOD-L00-004 | 启动逐笔订阅器 / start_tick_subscriber | D_DATA | generated | scripts/start_tick_subscriber.ps1 |
| MOD-L00-001 | 逐笔订阅器 / tick_subscriber | D_DATA | stable | src/zephyr/data/tick_subscriber.py |
| MOD-DATA_ENG | 包入口 / __init__ | D_DATA_ENG | generated | src/zephyr/data_eng/__init__.py |
| MOD-L00-004 | tushare提供器 / tushare_provider | D_DATA | generated | src/zephyr/data/implementations/tushare_provider.py |
| MOD-DATA_SEC | 包入口 / __init__ | D_DATA_SEC | generated | src/zephyr/data_security/core/__init__.py |
| MOD-L00-004 | 数据完整性巡检器——每天盘后检测全表当日数据是否达标。 / integrity_checker | D_DATA | stable | src/zephyr/data/integrity_checker.py |
| MOD-DATA_SEC | 包入口 / __init__ | D_DATA_SEC | generated | src/zephyr/data_security/api/__init__.py |
| MOD-L00-004 | 注册守卫任务 / register_guard_tasks | D_DATA | generated | scripts/register_guard_tasks.ps1 |
| MOD-L00-004 | 跨源校验器 / cross_source_validator | D_DATA | stable | src/zephyr/data/cross_source_validator.py |
| MOD-L00-004 | 880xxx 板块K线合成器——从 1m/5m 合成 15m/30m/60m 写 / kline_resampler | D_DATA | stable | src/zephyr/data/kline_resampler.py |
| MOD-L00-004 | L10 周末补下载检测器——检测过去N天缺失数据并精准补下载。 / backfill_checker | D_DATA | generated | src/zephyr/data/backfill_checker.py |
| MOD-RUNTIME_INTRADAY | — | D_INFRA_RUNTIME | stable | src/zephyr/runtime/intraday_main.py |
| MOD-DATA_ENG | 包入口 / __init__ | D_DATA_ENG | generated | src/zephyr/data_eng/models/__init__.py |
| MOD-L00-004 | ifind提供器 / ifind_provider | D_DATA | generated | src/zephyr/data/implementations/ifind_provider.py |
|  | 策略 / policies | D_DATA | generated | src/zephyr/data/config/policies.yaml |
| MOD-L00-004 | ch写入器 / ch_writer | D_DATA | stable | src/zephyr/data/ch_writer.py |
| MOD-L00-004 | 告警管理（MOD-L00-004 §6.5 失败重试与告警 + §8 可观测性） / alerter | D_DATA | generated | src/zephyr/data/alerter.py |
| MOD-L00-004 | miniqmt提供器 / miniqmt_provider | D_DATA | generated | src/zephyr/data/implementations/miniqmt_provider.py |
| MOD-L00-004 | ch配置 / ch_config | D_DATA | generated | src/zephyr/data/ch_config.py |
| MOD-L00-004 | 数据源测速器（MOD-L00-004 §8.5）。 / speed_tester | D_DATA | generated | src/zephyr/data/speed_tester.py |
| MOD-L00-004 | 板块快照收集器 / sector_snapshot_collector | D_DATA | stable | src/zephyr/data/sector_snapshot_collector.py |
| MOD-DATA_GOV | 包入口 / __init__ | D_DATA_GOV | generated | src/zephyr/data_governance/_extensions/__init__.py |
| MOD-L00-004 | baostock提供器 / baostock_provider | D_DATA | generated | src/zephyr/data/implementations/baostock_provider.py |
| MOD-L00-004 | cls提供器 / cls_provider | D_DATA | generated | src/zephyr/data/implementations/cls_provider.py |
| MOD-ALT_DATA | 包入口 / __init__ | D_ALT_DATA | generated | src/zephyr/alt_data/_extensions/__init__.py |
| MOD-ALT_DATA | 包入口 / __init__ | D_ALT_DATA | generated | src/zephyr/alt_data/__init__.py |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/data_replication/ |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/drift_aware_scheduler/ |
| MOD-DATA_ENG | — | D_DATA_ENG | deprecated | src/zephyr/data_eng/services/gpu_resource_manager/ |
| MOD-BT-025 | 结果deployer / result_deployer | D_BACKTEST | planned | src/zephyr/backtest/services/result_deployer.py |

## 8. 处置建议

- 孤儿环节：用 `apply_battle_map.py --add-anchor` 为环节挂载承载模块/候选/蓝图（草图 §12 迁移第二批「锚点」）
- 幽灵锚点：修正 target_id 指向真实存在的模块/候选，或删除该锚点
- 缺失叙事：在 `module_translation_registry.yaml` §battle_map_steps 段补齐环节叙事（name_zh/plain_zh/mechanism_zh/indicators_zh）
- 悬空边：修正 edge 的 from/to step_id，或删除孤立边
- 域漂移：① 确认锚点是否挂错环节（如 D_SELL_DECISION 不应在 buy_flow）；② 若挂错，迁移到正确环节或删除；③ 若认为该 domain 应被允许，修改 `battle_map_domain_policy.yaml` 的 `flow_stage_allowed_domains` 段（真源在 YAML，禁止改代码）；④ target_domains 含多个 domain 时，任一在允许列表即通过（跨域蓝图如 MOD-INF-002 含 80+ 子模块跨 8 domain）
- 孤儿模块：① 确认该模块是否该挂到某作战环节——若是，用 `apply_battle_map.py --add-anchor --target-graph depgraph --target-id <blueprint_id>` 挂到对应 step；② 若确无作战使命（造出来用不上），走弃用流程——`apply_depgraph.py` 软删除（build_status→deprecated）+ 在 `candidate_module_registry.yaml` 记 rejected 条目（含否决理由，防未来误重设）；③ build_status=planned 的孤儿 = 设计了却没想好挂哪，优先评审其作战归属再决定建/弃
