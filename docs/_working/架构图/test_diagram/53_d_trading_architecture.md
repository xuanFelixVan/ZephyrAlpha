---
doc_type: domain_architecture_diagram
title: D-TRADING 交易运营架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 53_d_trading / 交易运营 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示交易运营（D-TRADING）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 20:42:59
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 交易运营（D-TRADING）的模块分布。共 249 个模块 / 249 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (163 modules)              │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/trading/__init__.py  [production]                   │
│   src/zephyr/trading/__init___from_orches.py  [prototype]        │
│   src/zephyr/trading/__main__.py  [prototype]                    │
│   src/zephyr/trading/_extensions/__init__.py  [scaffold_place... │
│   src/zephyr/trading/action_dispatcher.py  [prototype]           │
│   src/zephyr/trading/admission_controller.py  [prototype]        │
│   src/zephyr/trading/ai_audit_logger.py  [prototype]             │
│   src/zephyr/trading/api/__init__.py  [scaffold_placeholder]     │
│   src/zephyr/trading/auto_dispatcher.py  [prototype]             │
│   src/zephyr/trading/auto_integrator.py  [prototype]             │
│   src/zephyr/trading/auto_runtime_core.py  [production]          │
│   src/zephyr/trading/auto_task_generator.py  [prototype]         │
│   src/zephyr/trading/autopilot.py  [prototype]                   │
│   src/zephyr/trading/boot_cron_jobs.py  [prototype]              │
│   src/zephyr/trading/boot_hooks.py  [prototype]                  │
│   src/zephyr/trading/capability_card.py  [prototype]             │
│   src/zephyr/trading/capability_registry.py  [prototype]         │
│   src/zephyr/trading/capability_sync.py  [prototype]             │
│   ...还有 145 个模块 / 145 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (86 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   7 Architecture Decisions 架构决策7项  [design]                 │
│   A-Share Pre-Market Standardized Workflow A股盘前标准化工作...  │
│   Annual Statistics 年度统计  [design]                           │
│   Approval Flow 审批流  [design]                                 │
│   Approval Token Verification 审批令牌验证  [design]             │
│   Autonomy Core Dependency Edge 自治核心依赖边  [design]         │
│   Cash Flow Manager 现金流管理器  [design]                       │
│   Cash Management 资金与现金管理  [design]                       │
│   Chase High Prevention 踏空追高防范  [design]                   │
│   Closed Loop Optimization 15 Dimensions 闭环优化15维度  [des... │
│   Config Signature Verification 配置签名验证  [design]           │
│   CorporateActionAdjusted 公司行为调整  [design]                 │
│   Cross Layer Runtime Architecture 横切层运行时架构  [design]    │
│   D-TRADING  [design]                                            │
│   DORA ICT Event Report DORA ICT事件报告  [design]               │
│   Data Degradation Processing 数据降级处理  [design]             │
│   Data Signature Verification 数据签名验证  [design]             │
│   Deterministic Validation 确定性校验  [design]                  │
│   ...还有 68 个模块 / 68 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 249 个模块 / 249 modules）。

### L2 领域层 / Domain Layer (163 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/trading/__init__.py | src/zephyr/trading/__init__.py | production | draft |
| 2 | src/zephyr/trading/__init___from_orches.py | src/zephyr/trading/__init___from_orch... | prototype | draft |
| 3 | src/zephyr/trading/__main__.py | src/zephyr/trading/__main__.py | prototype | draft |
| 4 | src/zephyr/trading/_extensions/__init__.py | src/zephyr/trading/_extensions/__init... | scaffold_placeholder | orphan |
| 5 | src/zephyr/trading/action_dispatcher.py | src/zephyr/trading/action_dispatcher.py | prototype | draft |
| 6 | src/zephyr/trading/admission_controller.py | src/zephyr/trading/admission_controll... | prototype | draft |
| 7 | src/zephyr/trading/ai_audit_logger.py | src/zephyr/trading/ai_audit_logger.py | prototype | draft |
| 8 | src/zephyr/trading/api/__init__.py | src/zephyr/trading/api/__init__.py | scaffold_placeholder | orphan |
| 9 | src/zephyr/trading/auto_dispatcher.py | src/zephyr/trading/auto_dispatcher.py | prototype | draft |
| 10 | src/zephyr/trading/auto_integrator.py | src/zephyr/trading/auto_integrator.py | prototype | draft |
| 11 | src/zephyr/trading/auto_runtime_core.py | src/zephyr/trading/auto_runtime_core.py | production | draft |
| 12 | src/zephyr/trading/auto_task_generator.py | src/zephyr/trading/auto_task_generato... | prototype | draft |
| 13 | src/zephyr/trading/autopilot.py | src/zephyr/trading/autopilot.py | prototype | draft |
| 14 | src/zephyr/trading/boot_cron_jobs.py | src/zephyr/trading/boot_cron_jobs.py | prototype | draft |
| 15 | src/zephyr/trading/boot_hooks.py | src/zephyr/trading/boot_hooks.py | prototype | draft |
| 16 | src/zephyr/trading/capability_card.py | src/zephyr/trading/capability_card.py | prototype | draft |
| 17 | src/zephyr/trading/capability_registry.py | src/zephyr/trading/capability_registr... | prototype | draft |
| 18 | src/zephyr/trading/capability_sync.py | src/zephyr/trading/capability_sync.py | prototype | draft |
| 19 | src/zephyr/trading/circadian_scheduler.py | src/zephyr/trading/circadian_schedule... | prototype | draft |
| 20 | src/zephyr/trading/conductor.py | src/zephyr/trading/conductor.py | prototype | draft |
| 21 | src/zephyr/trading/core/__init__.py | src/zephyr/trading/core/__init__.py | scaffold_placeholder | orphan |
| 22 | src/zephyr/trading/dream_cycle.py | src/zephyr/trading/dream_cycle.py | prototype | draft |
| 23 | src/zephyr/trading/feedback_loop.py | src/zephyr/trading/feedback_loop.py | prototype | draft |
| 24 | src/zephyr/trading/finalizer.py | src/zephyr/trading/finalizer.py | prototype | draft |
| 25 | src/zephyr/trading/gpu_consensus_scheduler.py | src/zephyr/trading/gpu_consensus_sche... | prototype | draft |
| 26 | src/zephyr/trading/gpu_monitor.py | src/zephyr/trading/gpu_monitor.py | prototype | draft |
| 27 | src/zephyr/trading/health_monitor.py | src/zephyr/trading/health_monitor.py | prototype | draft |
| 28 | src/zephyr/trading/ide_health_daemon.py | src/zephyr/trading/ide_health_daemon.py | prototype | draft |
| 29 | src/zephyr/trading/infrastructure/__init__.py | src/zephyr/trading/infrastructure/__i... | scaffold_placeholder | orphan |
| 30 | src/zephyr/trading/integration_registry.py | src/zephyr/trading/integration_regist... | prototype | draft |
| 31 | src/zephyr/trading/lifecycle_manager.py | src/zephyr/trading/lifecycle_manager.py | prototype | draft |
| 32 | src/zephyr/trading/models/__init__.py | src/zephyr/trading/models/__init__.py | scaffold_placeholder | orphan |
| 33 | src/zephyr/trading/module_onboarding_scanner.py | src/zephyr/trading/module_onboarding_... | prototype | draft |
| 34 | src/zephyr/trading/night_shift_queue.py | src/zephyr/trading/night_shift_queue.py | prototype | draft |
| 35 | src/zephyr/trading/orchestrator/__init__.py | src/zephyr/trading/orchestrator/__ini... | prototype | draft |
| 36 | src/zephyr/trading/orchestrator/agent_health_monitor.py | src/zephyr/trading/orchestrator/agent... | prototype | draft |
| 37 | src/zephyr/trading/orchestrator/agent_orchestrator.py | src/zephyr/trading/orchestrator/agent... | prototype | draft |
| 38 | src/zephyr/trading/orchestrator/agent_quality.py | src/zephyr/trading/orchestrator/agent... | prototype | draft |
| 39 | src/zephyr/trading/orchestrator/alert_handler.py | src/zephyr/trading/orchestrator/alert... | prototype | draft |
| 40 | src/zephyr/trading/orchestrator/autonomy_guard.py | src/zephyr/trading/orchestrator/auton... | prototype | draft |
| 41 | src/zephyr/trading/orchestrator/backup_manager.py | src/zephyr/trading/orchestrator/backu... | prototype | draft |
| 42 | src/zephyr/trading/orchestrator/batch_orchestrator.py | src/zephyr/trading/orchestrator/batch... | prototype | draft |
| 43 | src/zephyr/trading/orchestrator/benchmark_runner.py | src/zephyr/trading/orchestrator/bench... | prototype | draft |
| 44 | src/zephyr/trading/orchestrator/blind_spot_closure.py | src/zephyr/trading/orchestrator/blind... | prototype | draft |
| 45 | src/zephyr/trading/orchestrator/blueprint_health.py | src/zephyr/trading/orchestrator/bluep... | prototype | draft |
| 46 | src/zephyr/trading/orchestrator/blueprint_scorer.py | src/zephyr/trading/orchestrator/bluep... | prototype | draft |
| 47 | src/zephyr/trading/orchestrator/bulkhead_manager.py | src/zephyr/trading/orchestrator/bulkh... | prototype | draft |
| 48 | src/zephyr/trading/orchestrator/canary_manager.py | src/zephyr/trading/orchestrator/canar... | prototype | draft |
| 49 | src/zephyr/trading/orchestrator/capacity_budget.py | src/zephyr/trading/orchestrator/capac... | prototype | draft |
| 50 | src/zephyr/trading/orchestrator/chaos_engine.py | src/zephyr/trading/orchestrator/chaos... | prototype | draft |
| 51 | src/zephyr/trading/orchestrator/chaos_hooks.py | src/zephyr/trading/orchestrator/chaos... | prototype | draft |
| 52 | src/zephyr/trading/orchestrator/config_manager.py | src/zephyr/trading/orchestrator/confi... | prototype | draft |
| 53 | src/zephyr/trading/orchestrator/construction_guide.py | src/zephyr/trading/orchestrator/const... | prototype | draft |
| 54 | src/zephyr/trading/orchestrator/context_bridge.py | src/zephyr/trading/orchestrator/conte... | prototype | draft |
| 55 | src/zephyr/trading/orchestrator/contract_registry.py | src/zephyr/trading/orchestrator/contr... | prototype | draft |
| 56 | src/zephyr/trading/orchestrator/contract_router.py | src/zephyr/trading/orchestrator/contr... | prototype | draft |
| 57 | src/zephyr/trading/orchestrator/core/__init__.py | src/zephyr/trading/orchestrator/core/... | prototype | draft |
| 58 | src/zephyr/trading/orchestrator/core/agent_orchestrator.py | src/zephyr/trading/orchestrator/core/... | prototype | draft |
| 59 | src/zephyr/trading/orchestrator/core/task_queue.py | src/zephyr/trading/orchestrator/core/... | prototype | draft |
| 60 | src/zephyr/trading/orchestrator/core/trigger_router.py | src/zephyr/trading/orchestrator/core/... | prototype | draft |
| 61 | src/zephyr/trading/orchestrator/core/wave_generator.py | src/zephyr/trading/orchestrator/core/... | prototype | draft |
| 62 | src/zephyr/trading/orchestrator/data_lifecycle.py | src/zephyr/trading/orchestrator/data_... | prototype | draft |
| 63 | src/zephyr/trading/orchestrator/deferred_queue.py | src/zephyr/trading/orchestrator/defer... | prototype | draft |
| 64 | src/zephyr/trading/orchestrator/degrade_cascade.py | src/zephyr/trading/orchestrator/degra... | prototype | draft |
| 65 | src/zephyr/trading/orchestrator/dependency_lock.py | src/zephyr/trading/orchestrator/depen... | prototype | draft |
| 66 | src/zephyr/trading/orchestrator/design_decisions.py | src/zephyr/trading/orchestrator/desig... | prototype | draft |
| 67 | src/zephyr/trading/orchestrator/disk_guard.py | src/zephyr/trading/orchestrator/disk_... | prototype | draft |
| 68 | src/zephyr/trading/orchestrator/dlq_manager.py | src/zephyr/trading/orchestrator/dlq_m... | prototype | draft |
| 69 | src/zephyr/trading/orchestrator/failure_matcher.py | src/zephyr/trading/orchestrator/failu... | prototype | draft |
| 70 | src/zephyr/trading/orchestrator/fault_types.py | src/zephyr/trading/orchestrator/fault... | prototype | draft |
| 71 | src/zephyr/trading/orchestrator/feature_flag.py | src/zephyr/trading/orchestrator/featu... | prototype | draft |
| 72 | src/zephyr/trading/orchestrator/file_task_mapper.py | src/zephyr/trading/orchestrator/file_... | prototype | draft |
| 73 | src/zephyr/trading/orchestrator/finding_bridge.py | src/zephyr/trading/orchestrator/findi... | prototype | draft |
| 74 | src/zephyr/trading/orchestrator/hallucination_detector.py | src/zephyr/trading/orchestrator/hallu... | prototype | draft |
| 75 | src/zephyr/trading/orchestrator/housekeeping.py | src/zephyr/trading/orchestrator/house... | prototype | draft |
| 76 | src/zephyr/trading/orchestrator/incident_postmortem.py | src/zephyr/trading/orchestrator/incid... | prototype | draft |
| 77 | src/zephyr/trading/orchestrator/ke_quality.py | src/zephyr/trading/orchestrator/ke_qu... | prototype | draft |
| 78 | src/zephyr/trading/orchestrator/knowledge_freshness.py | src/zephyr/trading/orchestrator/knowl... | prototype | draft |
| 79 | src/zephyr/trading/orchestrator/lean_scanner.py | src/zephyr/trading/orchestrator/lean_... | prototype | draft |
| 80 | src/zephyr/trading/orchestrator/memory_writer.py | src/zephyr/trading/orchestrator/memor... | prototype | draft |
| 81 | src/zephyr/trading/orchestrator/model_registry.py | src/zephyr/trading/orchestrator/model... | prototype | draft |
| 82 | src/zephyr/trading/orchestrator/network_partition.py | src/zephyr/trading/orchestrator/netwo... | prototype | draft |
| 83 | src/zephyr/trading/orchestrator/path_index.py | src/zephyr/trading/orchestrator/path_... | prototype | draft |
| 84 | src/zephyr/trading/orchestrator/phase_executor.py | src/zephyr/trading/orchestrator/phase... | prototype | draft |
| 85 | src/zephyr/trading/orchestrator/prompt_version.py | src/zephyr/trading/orchestrator/promp... | prototype | draft |
| 86 | src/zephyr/trading/orchestrator/reconciliation_loop.py | src/zephyr/trading/orchestrator/recon... | prototype | draft |
| 87 | src/zephyr/trading/orchestrator/resilience/__init__.py | src/zephyr/trading/orchestrator/resil... | prototype | draft |
| 88 | src/zephyr/trading/orchestrator/resilience/deferred_queue.py | src/zephyr/trading/orchestrator/resil... | prototype | draft |
| 89 | src/zephyr/trading/orchestrator/resilience/failure_matche... | src/zephyr/trading/orchestrator/resil... | prototype | draft |
| 90 | src/zephyr/trading/orchestrator/resilience/hallucination_... | src/zephyr/trading/orchestrator/resil... | prototype | draft |
| 91 | src/zephyr/trading/orchestrator/resilience/rollback_manag... | src/zephyr/trading/orchestrator/resil... | prototype | draft |
| 92 | src/zephyr/trading/orchestrator/risk_registry.py | src/zephyr/trading/orchestrator/risk_... | prototype | draft |
| 93 | src/zephyr/trading/orchestrator/rollback_manager.py | src/zephyr/trading/orchestrator/rollb... | prototype | draft |
| 94 | src/zephyr/trading/orchestrator/rolling_upgrade.py | src/zephyr/trading/orchestrator/rolli... | prototype | draft |
| 95 | src/zephyr/trading/orchestrator/schema_migration.py | src/zephyr/trading/orchestrator/schem... | prototype | draft |
| 96 | src/zephyr/trading/orchestrator/script_runner.py | src/zephyr/trading/orchestrator/scrip... | prototype | draft |
| 97 | src/zephyr/trading/orchestrator/session_conflict.py | src/zephyr/trading/orchestrator/sessi... | prototype | draft |
| 98 | src/zephyr/trading/orchestrator/session_handoff.py | src/zephyr/trading/orchestrator/sessi... | prototype | draft |
| 99 | src/zephyr/trading/orchestrator/session_manager.py | src/zephyr/trading/orchestrator/sessi... | prototype | draft |
| 100 | src/zephyr/trading/orchestrator/stability_guard.py | src/zephyr/trading/orchestrator/stabi... | prototype | draft |
| 101 | src/zephyr/trading/orchestrator/startup_sequencer.py | src/zephyr/trading/orchestrator/start... | prototype | draft |
| 102 | src/zephyr/trading/orchestrator/state/__init__.py | src/zephyr/trading/orchestrator/state... | prototype | draft |
| 103 | src/zephyr/trading/orchestrator/state/agent_health_monito... | src/zephyr/trading/orchestrator/state... | prototype | draft |
| 104 | src/zephyr/trading/orchestrator/state/file_task_mapper.py | src/zephyr/trading/orchestrator/state... | prototype | draft |
| 105 | src/zephyr/trading/orchestrator/state/session_manager.py | src/zephyr/trading/orchestrator/state... | prototype | draft |
| 106 | src/zephyr/trading/orchestrator/state/state_synchronizer.py | src/zephyr/trading/orchestrator/state... | prototype | draft |
| 107 | src/zephyr/trading/orchestrator/state_propagation.py | src/zephyr/trading/orchestrator/state... | prototype | draft |
| 108 | src/zephyr/trading/orchestrator/state_synchronizer.py | src/zephyr/trading/orchestrator/state... | prototype | draft |
| 109 | src/zephyr/trading/orchestrator/system_transfer.py | src/zephyr/trading/orchestrator/syste... | prototype | draft |
| 110 | src/zephyr/trading/orchestrator/task_queue.py | src/zephyr/trading/orchestrator/task_... | prototype | draft |
| 111 | src/zephyr/trading/orchestrator/teardown_manager.py | src/zephyr/trading/orchestrator/teard... | prototype | draft |
| 112 | src/zephyr/trading/orchestrator/trigger_router.py | src/zephyr/trading/orchestrator/trigg... | prototype | draft |
| 113 | src/zephyr/trading/orchestrator/version_manifest.py | src/zephyr/trading/orchestrator/versi... | prototype | draft |
| 114 | src/zephyr/trading/orchestrator/wave_generator.py | src/zephyr/trading/orchestrator/wave_... | prototype | draft |
| 115 | src/zephyr/trading/orphan_detector.py | src/zephyr/trading/orphan_detector.py | prototype | draft |
| 116 | src/zephyr/trading/ports.py | src/zephyr/trading/ports.py | prototype | draft |
| 117 | src/zephyr/trading/protection_index.py | src/zephyr/trading/protection_index.py | prototype | draft |
| 118 | src/zephyr/trading/resource_optimization.py | src/zephyr/trading/resource_optimizat... | prototype | draft |
| 119 | src/zephyr/trading/runtime_config.py | src/zephyr/trading/runtime_config.py | prototype | draft |
| 120 | src/zephyr/trading/services/__init__.py | src/zephyr/trading/services/__init__.py | scaffold_placeholder | orphan |
| 121 | src/zephyr/trading/session_lifecycle.py | src/zephyr/trading/session_lifecycle.py | prototype | draft |
| 122 | src/zephyr/trading/speed_baseline_checker.py | src/zephyr/trading/speed_baseline_che... | prototype | draft |
| 123 | src/zephyr/trading/staging_area.py | src/zephyr/trading/staging_area.py | prototype | draft |
| 124 | src/zephyr/trading/status_dashboard.py | src/zephyr/trading/status_dashboard.py | prototype | draft |
| 125 | src/zephyr/trading/stop_gate.py | src/zephyr/trading/stop_gate.py | prototype | draft |
| 126 | src/zephyr/trading/task_gate.py | src/zephyr/trading/task_gate.py | prototype | draft |
| 127 | src/zephyr/trading/trading_contracts/__init__.py | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 128 | src/zephyr/trading/trading_contracts/execution/__init__.py | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 129 | src/zephyr/trading/trading_contracts/execution/capital_al... | src/zephyr/trading/trading_contracts/... | production | draft |
| 130 | src/zephyr/trading/trading_contracts/execution/execution_... | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 131 | src/zephyr/trading/trading_contracts/execution/execution_... | src/zephyr/trading/trading_contracts/... | production | draft |
| 132 | src/zephyr/trading/trading_contracts/execution/fill.py | src/zephyr/trading/trading_contracts/... | production | draft |
| 133 | src/zephyr/trading/trading_contracts/execution/model_serv... | src/zephyr/trading/trading_contracts/... | production | draft |
| 134 | src/zephyr/trading/trading_contracts/execution/order.py | src/zephyr/trading/trading_contracts/... | production | draft |
| 135 | src/zephyr/trading/trading_contracts/execution/position.py | src/zephyr/trading/trading_contracts/... | production | draft |
| 136 | src/zephyr/trading/trading_contracts/factories.py | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 137 | src/zephyr/trading/trading_contracts/market/__init__.py | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 138 | src/zephyr/trading/trading_contracts/market/factor_monito... | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 139 | src/zephyr/trading/trading_contracts/market/factor_signal.py | src/zephyr/trading/trading_contracts/... | production | draft |
| 140 | src/zephyr/trading/trading_contracts/market/instrument.py | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 141 | src/zephyr/trading/trading_contracts/market/macro_factor_... | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 142 | src/zephyr/trading/trading_contracts/market/market_data.py | src/zephyr/trading/trading_contracts/... | production | draft |
| 143 | src/zephyr/trading/trading_contracts/market/signal_degrad... | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 144 | src/zephyr/trading/trading_contracts/market/synthesized_s... | src/zephyr/trading/trading_contracts/... | production | draft |
| 145 | src/zephyr/trading/trading_contracts/portfolio/contracts/... | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 146 | src/zephyr/trading/trading_contracts/portfolio/contracts/... | src/zephyr/trading/trading_contracts/... | production | draft |
| 147 | src/zephyr/trading/trading_contracts/portfolio/contracts/... | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 148 | src/zephyr/trading/trading_contracts/portfolio/contracts/... | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 149 | src/zephyr/trading/trading_contracts/risk/__init__.py | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 150 | src/zephyr/trading/trading_contracts/risk/compliance_rule.py | src/zephyr/trading/trading_contracts/... | prototype | draft |
| 151 | src/zephyr/trading/trading_contracts/risk/risk_dashboard_... | src/zephyr/trading/trading_contracts/... | production | draft |
| 152 | src/zephyr/trading/trading_contracts/risk/risk_limit_viol... | src/zephyr/trading/trading_contracts/... | production | draft |
| 153 | src/zephyr/trading/trading_contracts/risk/risk_limits.py | src/zephyr/trading/trading_contracts/... | production | draft |
| 154 | src/zephyr/trading/trading_contracts/risk/risk_metrics.py | src/zephyr/trading/trading_contracts/... | production | draft |
| 155 | src/zephyr/trading/trading_contracts/risk/risk_validator_... | src/zephyr/trading/trading_contracts/... | production | draft |
| 156 | src/zephyr/trading/verdict_engine.py | src/zephyr/trading/verdict_engine.py | prototype | draft |
| 157 | src/zephyr/trading/windows_service.py | src/zephyr/trading/windows_service.py | prototype | draft |
| 158 | src/zephyr/trading/work_dag.py | src/zephyr/trading/work_dag.py | prototype | draft |
| 159 | src/zephyr/trading/work_orchestrator.py | src/zephyr/trading/work_orchestrator.py | prototype | draft |
| 160 | src/zephyr/trading/zombie_scanner.py | src/zephyr/trading/zombie_scanner.py | prototype | draft |
| 161 | 交易域-监控/D-TRADING-06 | Intraday P&L Monitor | design | design_only |
| 162 | 交易域-资金/D-TRADING-12 | Cash Flow Manager | design | design_only |
| 163 | 交易运营域/D-TRADING-04 | EOD Processor | design | design_only |

### 未分类 / Unclassified (86 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-TRADING/7 Architecture Decisions 架构决策7项 | 7 Architecture Decisions 架构决策7项 | design | design_only |
| 2 | D-TRADING/A-Share Pre-Market Standardized Workflow A股盘... | A-Share Pre-Market Standardized Workf... | design | design_only |
| 3 | D-TRADING/Annual Statistics 年度统计 | Annual Statistics 年度统计 | design | design_only |
| 4 | D-TRADING/Approval Flow 审批流 | Approval Flow 审批流 | design | design_only |
| 5 | D-TRADING/Approval Token Verification 审批令牌验证 | Approval Token Verification 审批令牌验证 | design | design_only |
| 6 | D-TRADING/Autonomy Core Dependency Edge 自治核心依赖边 | Autonomy Core Dependency Edge 自治核... | design | design_only |
| 7 | D-TRADING/Cash Flow Manager 现金流管理器 | Cash Flow Manager 现金流管理器 | design | design_only |
| 8 | D-TRADING/Cash Management 资金与现金管理 | Cash Management 资金与现金管理 | design | design_only |
| 9 | D-TRADING/Chase High Prevention 踏空追高防范 | Chase High Prevention 踏空追高防范 | design | design_only |
| 10 | D-TRADING/Closed Loop Optimization 15 Dimensions 闭环优化... | Closed Loop Optimization 15 Dimension... | design | design_only |
| 11 | D-TRADING/Config Signature Verification 配置签名验证 | Config Signature Verification 配置签... | design | design_only |
| 12 | D-TRADING/CorporateActionAdjusted 公司行为调整 | CorporateActionAdjusted 公司行为调整 | design | design_only |
| 13 | D-TRADING/Cross Layer Runtime Architecture 横切层运行时架构 | Cross Layer Runtime Architecture 横切... | design | design_only |
| 14 | D-TRADING/D-TRADING | D-TRADING | design | design_only |
| 15 | D-TRADING/DORA ICT Event Report DORA ICT事件报告 | DORA ICT Event Report DORA ICT事件报告 | design | design_only |
| 16 | D-TRADING/Data Degradation Processing 数据降级处理 | Data Degradation Processing 数据降级处理 | design | design_only |
| 17 | D-TRADING/Data Signature Verification 数据签名验证 | Data Signature Verification 数据签名验证 | design | design_only |
| 18 | D-TRADING/Deterministic Validation 确定性校验 | Deterministic Validation 确定性校验 | design | design_only |
| 19 | D-TRADING/EOD Processor日终处理器 | EOD Processor日终处理器 | design | design_only |
| 20 | D-TRADING/End-of-Day Processor 日终处理器 | End-of-Day Processor 日终处理器 | design | design_only |
| 21 | D-TRADING/Execution Core Dependency Edge 执行核心依赖边 | Execution Core Dependency Edge 执行核... | design | design_only |
| 22 | D-TRADING/Fee PnL Data 费率PnL数据 | Fee PnL Data 费率PnL数据 | design | design_only |
| 23 | D-TRADING/GOV-TRD-001 单票持仓集中度规则 | GOV-TRD-001 单票持仓集中度规则 | design | design_only |
| 24 | D-TRADING/Gift Declaration Form Engine 礼品申报表引擎 | Gift Declaration Form Engine 礼品申报... | design | design_only |
| 25 | D-TRADING/Global State Aggregator 全局状态聚合器 | Global State Aggregator 全局状态聚合器 | design | design_only |
| 26 | D-TRADING/Hard Boundary Constraints 硬边界约束 | Hard Boundary Constraints 硬边界约束 | design | design_only |
| 27 | D-TRADING/Infra Runtime Dependency Edge 基础设施运行时依赖边 | Infra Runtime Dependency Edge 基础设... | design | design_only |
| 28 | D-TRADING/Intraday Instant Reaction Decision Engine 盘中... | Intraday Instant Reaction Decision En... | design | design_only |
| 29 | D-TRADING/Intraday PnL Monitor 日内盈亏监控 | Intraday PnL Monitor 日内盈亏监控 | design | design_only |
| 30 | D-TRADING/Intraday Trading Agent 日内交易代理 | Intraday Trading Agent 日内交易代理 | design | design_only |
| 31 | D-TRADING/L0 L1 L2 Data Flow Artery L0→L1→L2数据流主动脉 | L0 L1 L2 Data Flow Artery L0→L1→L2... | design | design_only |
| 32 | D-TRADING/L2数据流主动脉 | L2数据流主动脉 | design | design_only |
| 33 | D-TRADING/LP-020 Trading Operations Domain Substitute 交... | LP-020 Trading Operations Domain Subs... | design | design_only |
| 34 | D-TRADING/Log Signature 日志签名 | Log Signature 日志签名 | design | design_only |
| 35 | D-TRADING/Loss Revenge Prevention 亏损报复防范 | Loss Revenge Prevention 亏损报复防范 | design | design_only |
| 36 | D-TRADING/Margin Calculator保证金计算器 | Margin Calculator保证金计算器 | design | design_only |
| 37 | D-TRADING/MarginAccount 保证金账户 | MarginAccount 保证金账户 | design | design_only |
| 38 | D-TRADING/MarginUnavailable 保证金不可用 | MarginUnavailable 保证金不可用 | design | design_only |
| 39 | D-TRADING/MarginWarning 保证金预警 | MarginWarning 保证金预警 | design | design_only |
| 40 | D-TRADING/Market Data 行情数据 | Market Data 行情数据 | design | design_only |
| 41 | D-TRADING/MultiAccountAllocated 多账户分配完成 | MultiAccountAllocated 多账户分配完成 | design | design_only |
| 42 | D-TRADING/Order Status 订单状态 | Order Status 订单状态 | design | design_only |
| 43 | D-TRADING/Portfolio Core Dependency Edge 组合核心依赖边 | Portfolio Core Dependency Edge 组合核... | design | design_only |
| 44 | D-TRADING/Position Accountant持仓会计 | Position Accountant持仓会计 | design | design_only |
| 45 | D-TRADING/Position Accounting 持仓会计 | Position Accounting 持仓会计 | design | design_only |
| 46 | D-TRADING/Position Data 持仓数据 | Position Data 持仓数据 | design | design_only |
| 47 | D-TRADING/Post-Market Review 盘后复盘 | Post-Market Review 盘后复盘 | design | design_only |
| 48 | D-TRADING/Pre-Market Checker盘前检查器 | Pre-Market Checker盘前检查器 | design | design_only |
| 49 | D-TRADING/Pre-Market Review 盘前复核 | Pre-Market Review 盘前复核 | design | design_only |
| 50 | D-TRADING/Process-Level Isolation 进程级隔离 | Process-Level Isolation 进程级隔离 | design | design_only |
| 51 | D-TRADING/Profit Pride Warning 盈利骄傲警告 | Profit Pride Warning 盈利骄傲警告 | design | design_only |
| 52 | D-TRADING/Reconciliation Engine对账引擎 | Reconciliation Engine对账引擎 | design | design_only |
| 53 | D-TRADING/ReconciliationCompleted 对账完成 | ReconciliationCompleted 对账完成 | design | design_only |
| 54 | D-TRADING/Reference Data Manager 参考数据管理 | Reference Data Manager 参考数据管理 | design | design_only |
| 55 | D-TRADING/Reporting Dependency Edge 报告域依赖边 | Reporting Dependency Edge 报告域依赖边 | design | design_only |
| 56 | D-TRADING/Risk Dependency Edge 风控依赖边 | Risk Dependency Edge 风控依赖边 | design | design_only |
| 57 | D-TRADING/Settlement Manager结算管理器 | Settlement Manager结算管理器 | design | design_only |
| 58 | D-TRADING/Settlement Reconciliation 结算与对账 | Settlement Reconciliation 结算与对账 | design | design_only |
| 59 | D-TRADING/SettlementCompleted 结算完成 | SettlementCompleted 结算完成 | design | design_only |
| 60 | D-TRADING/SettlementRecord 结算记录 | SettlementRecord 结算记录 | design | design_only |
| 61 | D-TRADING/Signature Chain 签名链 | Signature Chain 签名链 | design | design_only |
| 62 | D-TRADING/Strategy Capacity Academic Framework 策略容量学... | Strategy Capacity Academic Framework ... | design | design_only |
| 63 | D-TRADING/Strategy Parameters 策略参数 | Strategy Parameters 策略参数 | design | design_only |
| 64 | D-TRADING/Trader 交易员角色 | Trader 交易员角色 | design | design_only |
| 65 | D-TRADING/Trading Calendar Engine交易日历引擎 | Trading Calendar Engine交易日历引擎 | design | design_only |
| 66 | D-TRADING/Trading Cost Analyzer交易成本分析 | Trading Cost Analyzer交易成本分析 | design | design_only |
| 67 | D-TRADING/Trading Operations Data 交易运营数据 | Trading Operations Data 交易运营数据 | design | design_only |
| 68 | D-TRADING/Trading Operations Domain 交易运营域 | Trading Operations Domain 交易运营域 | design | design_only |
| 69 | D-TRADING/Trading Order 交易指令 | Trading Order 交易指令 | design | design_only |
| 70 | D-TRADING/TradingOrder 交易订单 | TradingOrder 交易订单 | design | design_only |
| 71 | D-TRADING/Trapped Position Adding Prevention 被套补仓防范 | Trapped Position Adding Prevention 被... | design | design_only |
| 72 | D-TRADING/Treasury Manager 资金管理器 | Treasury Manager 资金管理器 | design | design_only |
| 73 | D-TRADING/WeChat Interaction Hub 微信交互中心 | WeChat Interaction Hub 微信交互中心 | design | design_only |
| 74 | D-TRADING/miniQMT Connection Credential miniQMT连接凭证 | miniQMT Connection Credential miniQMT... | design | design_only |
| 75 | D-TRADING/不做高频交易 No High-Frequency Trading | 不做高频交易 No High-Frequency Trading | design | design_only |
| 76 | D-TRADING/交易决策约束 Trading Decision Constraints | 交易决策约束 Trading Decision Constra... | design | design_only |
| 77 | D-TRADING/交易决策防漂移契约 Contract | 交易决策防漂移契约 Contract | design | design_only |
| 78 | D-TRADING/交易域规则目录 Trading Domain Rule Catalog | 交易域规则目录 Trading Domain Rule Ca... | design | design_only |
| 79 | D-TRADING/交易执行流程 Execution Workflow | 交易执行流程 Execution Workflow | design | design_only |
| 80 | D-TRADING/交易运营 Trading Operations | 交易运营 Trading Operations | design | design_only |
| 81 | D-TRADING/延迟归因器 Latency Attributor | 延迟归因器 Latency Attributor | design | design_only |
| 82 | D-TRADING/延迟预算分配器 Latency Budget Allocator | 延迟预算分配器 Latency Budget Allocator | design | design_only |
| 83 | D-TRADING/架构决策引用 Architecture Decision Reference | 架构决策引用 Architecture Decision Re... | design | design_only |
| 84 | D-TRADING/禁止AI自主执行大额下单 No AI Auto-Execute Large... | 禁止AI自主执行大额下单 No AI Auto-Exe... | design | design_only |
| 85 | D-TRADING/禁止非交易时段提交订单 Order | 禁止非交易时段提交订单 Order | design | design_only |
| 86 | D-TRADING/纳秒级关键路径分析器 Nanosecond Critical Path A... | 纳秒级关键路径分析器 Nanosecond Criti... | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 225 条 / 225 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 225 条 / 225 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 5                               │
│   [import_depends]: 147 条 / edges                               │
│   [config_depends]: 59 条 / edges                                │
│   [event]: 14 条 / edges                                         │
│   [contract]: 4 条 / edges                                       │
│   [data]: 1 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (147 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   auto_dispatcher.py → __init__.py                               │
│   auto_integrator.py → __init__.py                               │
│   auto_runtime_core.py → __init__.py                             │
│   boot_cron_jobs.py → __init__.py                                │
│   boot_hooks.py → __init__.py                                    │
│   conductor.py → __init__.py                                     │
│   circadian_scheduler.py → __init__.py                           │
│   capability_registry.py → __init__.py                           │
│   capability_sync.py → __init__.py                               │
│   gpu_consensus_scheduler.py → __init__.py                       │
│   health_monitor.py → __init__.py                                │
│   lifecycle_manager.py → __init__.py                             │
│   module_onboarding_scanner.py → __init__.py                     │
│   resource_optimization.py → __init__.py                         │
│   orphan_detector.py → __init__.py                               │
│   protection_index.py → __init__.py                              │
│   status_dashboard.py → __init__.py                              │
│   windows_service.py → __init__.py                               │
│   work_orchestrator.py → __init__.py                             │
│   __main__.py → __init__.py                                      │
│   agent_health_monitor.py → __init__.py                          │
│   chaos_hooks.py → __init__.py                                   │
│   contract_router.py → __init__.py                               │
│   state_synchronizer.py → __init__.py                            │
│   trigger_router.py → __init__.py                                │
│   task_queue.py → __init__.py                                    │
│   __init__.py → __init__.py                                      │
│   trigger_router.py → __init__.py                                │
│   __init__.py → trigger_router.py                                │
│   agent_health_monitor.py → __init__.py                          │
│   __init__.py → session_manager.py                               │
│   state_synchronizer.py → __init__.py                            │
│   __init__.py → deferred_queue.py                                │
│   __init__.py → failure_matcher.py                               │
│   __init__.py → __init__.py                                      │
│   __init__.py → execution_rejection_error.py                     │
│   __init__.py → execution_report.py                              │
│   __init__.py → fill.py                                          │
│   __init__.py → model_serving_request.py                         │
│   __init__.py → capital_allocation_result.py                     │
│   __init__.py → position.py                                      │
│   __init__.py → order.py                                         │
│   __init__.py → factor_monitor_report.py                         │
│   __init__.py → market_data.py                                   │
│   __init__.py → factor_signal.py                                 │
│   __init__.py → instrument.py                                    │
│   __init__.py → signal_degradation_warnin...                     │
│   __init__.py → synthesized_signal.py                            │
│   __init__.py → macro_factor_signal.py                           │
│   ...还有 98 条 / 98 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (59 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (14 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (4 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 225 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `53_d_trading_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
