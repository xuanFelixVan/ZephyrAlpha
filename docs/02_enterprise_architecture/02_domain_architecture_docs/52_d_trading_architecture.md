---
doc_type: architecture_view
title: D-TRADING 交易运营架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 52_d_trading / 交易运营 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示交易运营（D-TRADING）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:21
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 交易运营（D-TRADING）的模块分布。共 169 个模块 / 169 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (163 modules)              │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/trading/__init__.py  [production]                   │
│   src/zephyr/trading/__init___from_orches.py  [prototype]        │
│   src/zephyr/trading/__main__.py  [prototype]                    │
│   src/zephyr/trading/_extensions/__init__.py  [prototype]        │
│   src/zephyr/trading/action_dispatcher.py  [prototype]           │
│   src/zephyr/trading/admission_controller.py  [prototype]        │
│   src/zephyr/trading/ai_audit_logger.py  [prototype]             │
│   src/zephyr/trading/api/__init__.py  [prototype]                │
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
│                未分类 / Unclassified (6 modules)                 │
├──────────────────────────────────────────────────────────────────┤
│   F1-autopilot/  [design]                                        │
│   F17-archived/  [design]                                        │
│   F26-runtime-integration/  [design]                             │
│   src/zephyr/trading/runtime/__init__.py  [production]           │
│   src/zephyr/trading/runtime/async_runtime.py  [production]      │
│   tests/trading/runtime/test_async_runtime.py  [production]      │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 169 个模块 / 169 modules）。

### L2 领域层 / Domain Layer (163 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/trading/__init__.py | src/zephyr/trading/__init__.py | production | generated |
| 2 | src/zephyr/trading/__init___from_orches.py | src/zephyr/trading/__init___from_orch... | prototype | generated |
| 3 | src/zephyr/trading/__main__.py | src/zephyr/trading/__main__.py | prototype | generated |
| 4 | src/zephyr/trading/_extensions/__init__.py | src/zephyr/trading/_extensions/__init... | prototype | deprecated |
| 5 | src/zephyr/trading/action_dispatcher.py | src/zephyr/trading/action_dispatcher.py | prototype | generated |
| 6 | src/zephyr/trading/admission_controller.py | src/zephyr/trading/admission_controll... | prototype | generated |
| 7 | src/zephyr/trading/ai_audit_logger.py | src/zephyr/trading/ai_audit_logger.py | prototype | generated |
| 8 | src/zephyr/trading/api/__init__.py | src/zephyr/trading/api/__init__.py | prototype | deprecated |
| 9 | src/zephyr/trading/auto_dispatcher.py | src/zephyr/trading/auto_dispatcher.py | prototype | generated |
| 10 | src/zephyr/trading/auto_integrator.py | src/zephyr/trading/auto_integrator.py | prototype | generated |
| 11 | src/zephyr/trading/auto_runtime_core.py | src/zephyr/trading/auto_runtime_core.py | production | generated |
| 12 | src/zephyr/trading/auto_task_generator.py | src/zephyr/trading/auto_task_generato... | prototype | generated |
| 13 | src/zephyr/trading/autopilot.py | src/zephyr/trading/autopilot.py | prototype | generated |
| 14 | src/zephyr/trading/boot_cron_jobs.py | src/zephyr/trading/boot_cron_jobs.py | prototype | generated |
| 15 | src/zephyr/trading/boot_hooks.py | src/zephyr/trading/boot_hooks.py | prototype | generated |
| 16 | src/zephyr/trading/capability_card.py | src/zephyr/trading/capability_card.py | prototype | generated |
| 17 | src/zephyr/trading/capability_registry.py | src/zephyr/trading/capability_registr... | prototype | generated |
| 18 | src/zephyr/trading/capability_sync.py | src/zephyr/trading/capability_sync.py | prototype | generated |
| 19 | src/zephyr/trading/circadian_scheduler.py | src/zephyr/trading/circadian_schedule... | prototype | generated |
| 20 | src/zephyr/trading/conductor.py | src/zephyr/trading/conductor.py | prototype | generated |
| 21 | src/zephyr/trading/core/__init__.py | src/zephyr/trading/core/__init__.py | prototype | deprecated |
| 22 | src/zephyr/trading/dream_cycle.py | src/zephyr/trading/dream_cycle.py | prototype | generated |
| 23 | src/zephyr/trading/feedback_loop.py | src/zephyr/trading/feedback_loop.py | prototype | generated |
| 24 | src/zephyr/trading/finalizer.py | src/zephyr/trading/finalizer.py | prototype | generated |
| 25 | src/zephyr/trading/gpu_consensus_scheduler.py | src/zephyr/trading/gpu_consensus_sche... | prototype | generated |
| 26 | src/zephyr/trading/gpu_monitor.py | src/zephyr/trading/gpu_monitor.py | prototype | generated |
| 27 | src/zephyr/trading/health_monitor.py | src/zephyr/trading/health_monitor.py | prototype | generated |
| 28 | src/zephyr/trading/ide_health_daemon.py | src/zephyr/trading/ide_health_daemon.py | prototype | generated |
| 29 | src/zephyr/trading/infrastructure/__init__.py | src/zephyr/trading/infrastructure/__i... | prototype | deprecated |
| 30 | src/zephyr/trading/integration_registry.py | src/zephyr/trading/integration_regist... | prototype | generated |
| 31 | src/zephyr/trading/lifecycle_manager.py | src/zephyr/trading/lifecycle_manager.py | prototype | generated |
| 32 | src/zephyr/trading/models/__init__.py | src/zephyr/trading/models/__init__.py | prototype | deprecated |
| 33 | src/zephyr/trading/module_onboarding_scanner.py | src/zephyr/trading/module_onboarding_... | prototype | generated |
| 34 | src/zephyr/trading/night_shift_queue.py | src/zephyr/trading/night_shift_queue.py | prototype | generated |
| 35 | src/zephyr/trading/orchestrator/__init__.py | src/zephyr/trading/orchestrator/__ini... | prototype | generated |
| 36 | src/zephyr/trading/orchestrator/agent_health_monitor.py | src/zephyr/trading/orchestrator/agent... | prototype | generated |
| 37 | src/zephyr/trading/orchestrator/agent_orchestrator.py | src/zephyr/trading/orchestrator/agent... | prototype | generated |
| 38 | src/zephyr/trading/orchestrator/agent_quality.py | src/zephyr/trading/orchestrator/agent... | prototype | generated |
| 39 | src/zephyr/trading/orchestrator/alert_handler.py | src/zephyr/trading/orchestrator/alert... | prototype | generated |
| 40 | src/zephyr/trading/orchestrator/autonomy_guard.py | src/zephyr/trading/orchestrator/auton... | prototype | generated |
| 41 | src/zephyr/trading/orchestrator/backup_manager.py | src/zephyr/trading/orchestrator/backu... | prototype | generated |
| 42 | src/zephyr/trading/orchestrator/batch_orchestrator.py | src/zephyr/trading/orchestrator/batch... | prototype | generated |
| 43 | src/zephyr/trading/orchestrator/benchmark_runner.py | src/zephyr/trading/orchestrator/bench... | prototype | generated |
| 44 | src/zephyr/trading/orchestrator/blind_spot_closure.py | src/zephyr/trading/orchestrator/blind... | prototype | generated |
| 45 | src/zephyr/trading/orchestrator/blueprint_health.py | src/zephyr/trading/orchestrator/bluep... | prototype | generated |
| 46 | src/zephyr/trading/orchestrator/blueprint_scorer.py | src/zephyr/trading/orchestrator/bluep... | prototype | generated |
| 47 | src/zephyr/trading/orchestrator/bulkhead_manager.py | src/zephyr/trading/orchestrator/bulkh... | prototype | generated |
| 48 | src/zephyr/trading/orchestrator/canary_manager.py | src/zephyr/trading/orchestrator/canar... | prototype | generated |
| 49 | src/zephyr/trading/orchestrator/capacity_budget.py | src/zephyr/trading/orchestrator/capac... | prototype | generated |
| 50 | src/zephyr/trading/orchestrator/chaos_engine.py | src/zephyr/trading/orchestrator/chaos... | prototype | generated |
| 51 | src/zephyr/trading/orchestrator/chaos_hooks.py | src/zephyr/trading/orchestrator/chaos... | prototype | generated |
| 52 | src/zephyr/trading/orchestrator/config_manager.py | src/zephyr/trading/orchestrator/confi... | prototype | generated |
| 53 | src/zephyr/trading/orchestrator/construction_guide.py | src/zephyr/trading/orchestrator/const... | prototype | generated |
| 54 | src/zephyr/trading/orchestrator/context_bridge.py | src/zephyr/trading/orchestrator/conte... | prototype | generated |
| 55 | src/zephyr/trading/orchestrator/contract_registry.py | src/zephyr/trading/orchestrator/contr... | prototype | generated |
| 56 | src/zephyr/trading/orchestrator/contract_router.py | src/zephyr/trading/orchestrator/contr... | prototype | generated |
| 57 | src/zephyr/trading/orchestrator/core/__init__.py | src/zephyr/trading/orchestrator/core/... | prototype | generated |
| 58 | src/zephyr/trading/orchestrator/core/agent_orchestrator.py | src/zephyr/trading/orchestrator/core/... | prototype | generated |
| 59 | src/zephyr/trading/orchestrator/core/task_queue.py | src/zephyr/trading/orchestrator/core/... | prototype | generated |
| 60 | src/zephyr/trading/orchestrator/core/trigger_router.py | src/zephyr/trading/orchestrator/core/... | prototype | generated |
| 61 | src/zephyr/trading/orchestrator/core/wave_generator.py | src/zephyr/trading/orchestrator/core/... | prototype | generated |
| 62 | src/zephyr/trading/orchestrator/data_lifecycle.py | src/zephyr/trading/orchestrator/data_... | prototype | generated |
| 63 | src/zephyr/trading/orchestrator/deferred_queue.py | src/zephyr/trading/orchestrator/defer... | prototype | generated |
| 64 | src/zephyr/trading/orchestrator/degrade_cascade.py | src/zephyr/trading/orchestrator/degra... | prototype | generated |
| 65 | src/zephyr/trading/orchestrator/dependency_lock.py | src/zephyr/trading/orchestrator/depen... | prototype | generated |
| 66 | src/zephyr/trading/orchestrator/design_decisions.py | src/zephyr/trading/orchestrator/desig... | prototype | generated |
| 67 | src/zephyr/trading/orchestrator/disk_guard.py | src/zephyr/trading/orchestrator/disk_... | prototype | generated |
| 68 | src/zephyr/trading/orchestrator/dlq_manager.py | src/zephyr/trading/orchestrator/dlq_m... | prototype | generated |
| 69 | src/zephyr/trading/orchestrator/failure_matcher.py | src/zephyr/trading/orchestrator/failu... | prototype | generated |
| 70 | src/zephyr/trading/orchestrator/fault_types.py | src/zephyr/trading/orchestrator/fault... | prototype | generated |
| 71 | src/zephyr/trading/orchestrator/feature_flag.py | src/zephyr/trading/orchestrator/featu... | prototype | generated |
| 72 | src/zephyr/trading/orchestrator/file_task_mapper.py | src/zephyr/trading/orchestrator/file_... | prototype | generated |
| 73 | src/zephyr/trading/orchestrator/finding_bridge.py | src/zephyr/trading/orchestrator/findi... | prototype | generated |
| 74 | src/zephyr/trading/orchestrator/hallucination_detector.py | src/zephyr/trading/orchestrator/hallu... | prototype | generated |
| 75 | src/zephyr/trading/orchestrator/housekeeping.py | src/zephyr/trading/orchestrator/house... | prototype | generated |
| 76 | src/zephyr/trading/orchestrator/incident_postmortem.py | src/zephyr/trading/orchestrator/incid... | prototype | generated |
| 77 | src/zephyr/trading/orchestrator/ke_quality.py | src/zephyr/trading/orchestrator/ke_qu... | prototype | generated |
| 78 | src/zephyr/trading/orchestrator/knowledge_freshness.py | src/zephyr/trading/orchestrator/knowl... | prototype | generated |
| 79 | src/zephyr/trading/orchestrator/lean_scanner.py | src/zephyr/trading/orchestrator/lean_... | prototype | generated |
| 80 | src/zephyr/trading/orchestrator/memory_writer.py | src/zephyr/trading/orchestrator/memor... | prototype | generated |
| 81 | src/zephyr/trading/orchestrator/model_registry.py | src/zephyr/trading/orchestrator/model... | prototype | generated |
| 82 | src/zephyr/trading/orchestrator/network_partition.py | src/zephyr/trading/orchestrator/netwo... | prototype | generated |
| 83 | src/zephyr/trading/orchestrator/path_index.py | src/zephyr/trading/orchestrator/path_... | prototype | generated |
| 84 | src/zephyr/trading/orchestrator/phase_executor.py | src/zephyr/trading/orchestrator/phase... | prototype | generated |
| 85 | src/zephyr/trading/orchestrator/prompt_version.py | src/zephyr/trading/orchestrator/promp... | prototype | generated |
| 86 | src/zephyr/trading/orchestrator/reconciliation_loop.py | src/zephyr/trading/orchestrator/recon... | prototype | generated |
| 87 | src/zephyr/trading/orchestrator/resilience/__init__.py | src/zephyr/trading/orchestrator/resil... | prototype | generated |
| 88 | src/zephyr/trading/orchestrator/resilience/deferred_queue.py | src/zephyr/trading/orchestrator/resil... | prototype | generated |
| 89 | src/zephyr/trading/orchestrator/resilience/failure_matche... | src/zephyr/trading/orchestrator/resil... | prototype | generated |
| 90 | src/zephyr/trading/orchestrator/resilience/hallucination_... | src/zephyr/trading/orchestrator/resil... | prototype | generated |
| 91 | src/zephyr/trading/orchestrator/resilience/rollback_manag... | src/zephyr/trading/orchestrator/resil... | prototype | generated |
| 92 | src/zephyr/trading/orchestrator/risk_registry.py | src/zephyr/trading/orchestrator/risk_... | prototype | generated |
| 93 | src/zephyr/trading/orchestrator/rollback_manager.py | src/zephyr/trading/orchestrator/rollb... | prototype | generated |
| 94 | src/zephyr/trading/orchestrator/rolling_upgrade.py | src/zephyr/trading/orchestrator/rolli... | prototype | generated |
| 95 | src/zephyr/trading/orchestrator/schema_migration.py | src/zephyr/trading/orchestrator/schem... | prototype | generated |
| 96 | src/zephyr/trading/orchestrator/script_runner.py | src/zephyr/trading/orchestrator/scrip... | prototype | generated |
| 97 | src/zephyr/trading/orchestrator/session_conflict.py | src/zephyr/trading/orchestrator/sessi... | prototype | generated |
| 98 | src/zephyr/trading/orchestrator/session_handoff.py | src/zephyr/trading/orchestrator/sessi... | prototype | generated |
| 99 | src/zephyr/trading/orchestrator/session_manager.py | src/zephyr/trading/orchestrator/sessi... | prototype | generated |
| 100 | src/zephyr/trading/orchestrator/stability_guard.py | src/zephyr/trading/orchestrator/stabi... | prototype | generated |
| 101 | src/zephyr/trading/orchestrator/startup_sequencer.py | src/zephyr/trading/orchestrator/start... | prototype | generated |
| 102 | src/zephyr/trading/orchestrator/state/__init__.py | src/zephyr/trading/orchestrator/state... | prototype | generated |
| 103 | src/zephyr/trading/orchestrator/state/agent_health_monito... | src/zephyr/trading/orchestrator/state... | prototype | generated |
| 104 | src/zephyr/trading/orchestrator/state/file_task_mapper.py | src/zephyr/trading/orchestrator/state... | prototype | generated |
| 105 | src/zephyr/trading/orchestrator/state/session_manager.py | src/zephyr/trading/orchestrator/state... | prototype | generated |
| 106 | src/zephyr/trading/orchestrator/state/state_synchronizer.py | src/zephyr/trading/orchestrator/state... | prototype | generated |
| 107 | src/zephyr/trading/orchestrator/state_propagation.py | src/zephyr/trading/orchestrator/state... | prototype | generated |
| 108 | src/zephyr/trading/orchestrator/state_synchronizer.py | src/zephyr/trading/orchestrator/state... | prototype | generated |
| 109 | src/zephyr/trading/orchestrator/system_transfer.py | src/zephyr/trading/orchestrator/syste... | prototype | generated |
| 110 | src/zephyr/trading/orchestrator/task_queue.py | src/zephyr/trading/orchestrator/task_... | prototype | generated |
| 111 | src/zephyr/trading/orchestrator/teardown_manager.py | src/zephyr/trading/orchestrator/teard... | prototype | generated |
| 112 | src/zephyr/trading/orchestrator/trigger_router.py | src/zephyr/trading/orchestrator/trigg... | prototype | generated |
| 113 | src/zephyr/trading/orchestrator/version_manifest.py | src/zephyr/trading/orchestrator/versi... | prototype | generated |
| 114 | src/zephyr/trading/orchestrator/wave_generator.py | src/zephyr/trading/orchestrator/wave_... | prototype | generated |
| 115 | src/zephyr/trading/orphan_detector.py | src/zephyr/trading/orphan_detector.py | prototype | generated |
| 116 | src/zephyr/trading/ports.py | src/zephyr/trading/ports.py | prototype | generated |
| 117 | src/zephyr/trading/protection_index.py | src/zephyr/trading/protection_index.py | prototype | generated |
| 118 | src/zephyr/trading/resource_optimization.py | src/zephyr/trading/resource_optimizat... | prototype | generated |
| 119 | src/zephyr/trading/runtime_config.py | src/zephyr/trading/runtime_config.py | prototype | generated |
| 120 | src/zephyr/trading/services/__init__.py | src/zephyr/trading/services/__init__.py | prototype | deprecated |
| 121 | src/zephyr/trading/session_lifecycle.py | src/zephyr/trading/session_lifecycle.py | prototype | generated |
| 122 | src/zephyr/trading/speed_baseline_checker.py | src/zephyr/trading/speed_baseline_che... | prototype | generated |
| 123 | src/zephyr/trading/staging_area.py | src/zephyr/trading/staging_area.py | prototype | generated |
| 124 | src/zephyr/trading/status_dashboard.py | src/zephyr/trading/status_dashboard.py | prototype | generated |
| 125 | src/zephyr/trading/stop_gate.py | src/zephyr/trading/stop_gate.py | prototype | generated |
| 126 | src/zephyr/trading/task_gate.py | src/zephyr/trading/task_gate.py | prototype | generated |
| 127 | src/zephyr/trading/trading_contracts/__init__.py | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 128 | src/zephyr/trading/trading_contracts/execution/__init__.py | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 129 | src/zephyr/trading/trading_contracts/execution/capital_al... | src/zephyr/trading/trading_contracts/... | production | generated |
| 130 | src/zephyr/trading/trading_contracts/execution/execution_... | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 131 | src/zephyr/trading/trading_contracts/execution/execution_... | src/zephyr/trading/trading_contracts/... | production | generated |
| 132 | src/zephyr/trading/trading_contracts/execution/fill.py | src/zephyr/trading/trading_contracts/... | production | generated |
| 133 | src/zephyr/trading/trading_contracts/execution/model_serv... | src/zephyr/trading/trading_contracts/... | production | generated |
| 134 | src/zephyr/trading/trading_contracts/execution/order.py | src/zephyr/trading/trading_contracts/... | production | generated |
| 135 | src/zephyr/trading/trading_contracts/execution/position.py | src/zephyr/trading/trading_contracts/... | production | generated |
| 136 | src/zephyr/trading/trading_contracts/factories.py | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 137 | src/zephyr/trading/trading_contracts/market/__init__.py | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 138 | src/zephyr/trading/trading_contracts/market/factor_monito... | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 139 | src/zephyr/trading/trading_contracts/market/factor_signal.py | src/zephyr/trading/trading_contracts/... | production | generated |
| 140 | src/zephyr/trading/trading_contracts/market/instrument.py | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 141 | src/zephyr/trading/trading_contracts/market/macro_factor_... | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 142 | src/zephyr/trading/trading_contracts/market/market_data.py | src/zephyr/trading/trading_contracts/... | production | generated |
| 143 | src/zephyr/trading/trading_contracts/market/signal_degrad... | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 144 | src/zephyr/trading/trading_contracts/market/synthesized_s... | src/zephyr/trading/trading_contracts/... | production | generated |
| 145 | src/zephyr/trading/trading_contracts/portfolio/contracts/... | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 146 | src/zephyr/trading/trading_contracts/portfolio/contracts/... | src/zephyr/trading/trading_contracts/... | production | generated |
| 147 | src/zephyr/trading/trading_contracts/portfolio/contracts/... | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 148 | src/zephyr/trading/trading_contracts/portfolio/contracts/... | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 149 | src/zephyr/trading/trading_contracts/risk/__init__.py | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 150 | src/zephyr/trading/trading_contracts/risk/compliance_rule.py | src/zephyr/trading/trading_contracts/... | prototype | generated |
| 151 | src/zephyr/trading/trading_contracts/risk/risk_dashboard_... | src/zephyr/trading/trading_contracts/... | production | generated |
| 152 | src/zephyr/trading/trading_contracts/risk/risk_limit_viol... | src/zephyr/trading/trading_contracts/... | production | generated |
| 153 | src/zephyr/trading/trading_contracts/risk/risk_limits.py | src/zephyr/trading/trading_contracts/... | production | generated |
| 154 | src/zephyr/trading/trading_contracts/risk/risk_metrics.py | src/zephyr/trading/trading_contracts/... | production | generated |
| 155 | src/zephyr/trading/trading_contracts/risk/risk_validator_... | src/zephyr/trading/trading_contracts/... | production | generated |
| 156 | src/zephyr/trading/verdict_engine.py | src/zephyr/trading/verdict_engine.py | prototype | generated |
| 157 | src/zephyr/trading/windows_service.py | src/zephyr/trading/windows_service.py | prototype | generated |
| 158 | src/zephyr/trading/work_dag.py | src/zephyr/trading/work_dag.py | prototype | generated |
| 159 | src/zephyr/trading/work_orchestrator.py | src/zephyr/trading/work_orchestrator.py | prototype | generated |
| 160 | src/zephyr/trading/zombie_scanner.py | src/zephyr/trading/zombie_scanner.py | prototype | generated |
| 161 | 交易域-监控/D-TRADING-06 | Intraday P&L Monitor | design | planned |
| 162 | 交易域-资金/D-TRADING-12 | Cash Flow Manager | design | planned |
| 163 | 交易运营域/D-TRADING-04 | EOD Processor | design | planned |

### 未分类 / Unclassified (6 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | F1-autopilot/ | F1-autopilot/ | design | stable |
| 2 | F17-archived/ | F17-archived/ | design | deprecated |
| 3 | F26-runtime-integration/ | F26-runtime-integration/ | design | stable |
| 4 | src/zephyr/trading/runtime/__init__.py | src/zephyr/trading/runtime/__init__.py | production | generated |
| 5 | src/zephyr/trading/runtime/async_runtime.py | src/zephyr/trading/runtime/async_runt... | production | generated |
| 6 | tests/trading/runtime/test_async_runtime.py | tests/trading/runtime/test_async_runt... | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 140 条 / 140 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 140 条 / 140 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 83 条 / edges                                │
│   [config_depends]: 57 条 / edges                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (83 条 / edges)                 │
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
│   ...还有 34 条 / 34 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (57 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 140 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `52_d_trading_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
