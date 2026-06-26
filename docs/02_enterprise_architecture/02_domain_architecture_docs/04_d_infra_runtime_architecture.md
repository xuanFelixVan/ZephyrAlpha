---
doc_type: architecture_view
title: D-INFRA_RUNTIME 运行时集成架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 04_d_infra_runtime / 运行时集成 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示运行时集成（D-INFRA_RUNTIME）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 运行时集成（D-INFRA_RUNTIME）的模块分布。共 148 个模块 / 148 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│         L0 基础设施层 / Infrastructure Layer (3 modules)         │
├──────────────────────────────────────────────────────────────────┤
│   Backup Manager(架构版)  [design]                               │
│   数据源可用性SLA追踪器  [design]                                │
│   配置管理器  [design]                                           │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (145 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/__init__.py  [production]                           │
│   src/zephyr/autonomy_core/pipeline_orchestrator.py  [product... │
│   src/zephyr/infrastructure/__init__.py  [production]            │
│   src/zephyr/infrastructure/__init___from_infra.py  [production] │
│   src/zephyr/infrastructure/_base_server.py  [production]        │
│   src/zephyr/infrastructure/_extensions/__init__.py  [prototype] │
│   src/zephyr/infrastructure/adaptation/__init__.py  [production] │
│   src/zephyr/infrastructure/api/__init__.py  [prototype]         │
│   src/zephyr/infrastructure/asset_inventory/__init__.py  [pro... │
│   src/zephyr/infrastructure/asset_inventory/__main__.py  [pro... │
│   src/zephyr/infrastructure/asset_inventory/classifier.py  [p... │
│   src/zephyr/infrastructure/asset_inventory/dashboard.py  [pr... │
│   src/zephyr/infrastructure/asset_inventory/dependency.py  [p... │
│   src/zephyr/infrastructure/asset_inventory/index_generator.p... │
│   src/zephyr/infrastructure/asset_inventory/lifecycle.py  [pr... │
│   src/zephyr/infrastructure/asset_inventory/mcp_server.py  [p... │
│   src/zephyr/infrastructure/asset_inventory/metadata.py  [pro... │
│   src/zephyr/infrastructure/asset_inventory/models.py  [produ... │
│   ...还有 127 个模块 / 127 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 148 个模块 / 148 modules）。

### L0 基础设施层 / Infrastructure Layer (3 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 运维基础设施域/D-INFRA-03 | Backup Manager(架构版) | design | planned |
| 2 | 运维基础设施域/D-INFRA-321 | 数据源可用性SLA追踪器 | design | planned |
| 3 | 运行时基础设施域-配置管理/D-INFRA-06 | 配置管理器 | design | planned |

### L1 基础层 / Foundation Layer (145 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/__init__.py | src/zephyr/__init__.py | production | generated |
| 2 | src/zephyr/autonomy_core/pipeline_orchestrator.py | src/zephyr/autonomy_core/pipeline_orc... | production | generated |
| 3 | src/zephyr/infrastructure/__init__.py | src/zephyr/infrastructure/__init__.py | production | generated |
| 4 | src/zephyr/infrastructure/__init___from_infra.py | src/zephyr/infrastructure/__init___fr... | production | generated |
| 5 | src/zephyr/infrastructure/_base_server.py | src/zephyr/infrastructure/_base_serve... | production | generated |
| 6 | src/zephyr/infrastructure/_extensions/__init__.py | src/zephyr/infrastructure/_extensions... | prototype | deprecated |
| 7 | src/zephyr/infrastructure/adaptation/__init__.py | src/zephyr/infrastructure/adaptation/... | production | generated |
| 8 | src/zephyr/infrastructure/api/__init__.py | src/zephyr/infrastructure/api/__init_... | prototype | deprecated |
| 9 | src/zephyr/infrastructure/asset_inventory/__init__.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 10 | src/zephyr/infrastructure/asset_inventory/__main__.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 11 | src/zephyr/infrastructure/asset_inventory/classifier.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 12 | src/zephyr/infrastructure/asset_inventory/dashboard.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 13 | src/zephyr/infrastructure/asset_inventory/dependency.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 14 | src/zephyr/infrastructure/asset_inventory/index_generator.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 15 | src/zephyr/infrastructure/asset_inventory/lifecycle.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 16 | src/zephyr/infrastructure/asset_inventory/mcp_server.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 17 | src/zephyr/infrastructure/asset_inventory/metadata.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 18 | src/zephyr/infrastructure/asset_inventory/models.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 19 | src/zephyr/infrastructure/asset_inventory/reconciler.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 20 | src/zephyr/infrastructure/asset_inventory/registry_adapte... | src/zephyr/infrastructure/asset_inven... | production | generated |
| 21 | src/zephyr/infrastructure/asset_inventory/scanner.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 22 | src/zephyr/infrastructure/asset_inventory/telemetry.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 23 | src/zephyr/infrastructure/asset_inventory/trust_anchor.py | src/zephyr/infrastructure/asset_inven... | production | generated |
| 24 | src/zephyr/infrastructure/audit_logger.py | src/zephyr/infrastructure/audit_logge... | production | generated |
| 25 | src/zephyr/infrastructure/auto_diagnostics.py | src/zephyr/infrastructure/auto_diagno... | production | generated |
| 26 | src/zephyr/infrastructure/blueprint_code_sync.py | src/zephyr/infrastructure/blueprint_c... | production | generated |
| 27 | src/zephyr/infrastructure/blueprint_search_server.py | src/zephyr/infrastructure/blueprint_s... | production | generated |
| 28 | src/zephyr/infrastructure/capacity_assurance/__init__.py | src/zephyr/infrastructure/capacity_as... | production | generated |
| 29 | src/zephyr/infrastructure/capacity_assurance/contracts/__... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 30 | src/zephyr/infrastructure/capacity_assurance/contracts/ba... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 31 | src/zephyr/infrastructure/capacity_assurance/contracts/ba... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 32 | src/zephyr/infrastructure/capacity_assurance/contracts/co... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 33 | src/zephyr/infrastructure/capacity_assurance/cross_module... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 34 | src/zephyr/infrastructure/capacity_assurance/modules/__in... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 35 | src/zephyr/infrastructure/capacity_assurance/modules/ai_s... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 36 | src/zephyr/infrastructure/capacity_assurance/modules/capa... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 37 | src/zephyr/infrastructure/capacity_assurance/modules/clif... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 38 | src/zephyr/infrastructure/capacity_assurance/modules/cold... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 39 | src/zephyr/infrastructure/capacity_assurance/modules/conf... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 40 | src/zephyr/infrastructure/capacity_assurance/modules/cont... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 41 | src/zephyr/infrastructure/capacity_assurance/modules/degr... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 42 | src/zephyr/infrastructure/capacity_assurance/modules/dr_d... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 43 | src/zephyr/infrastructure/capacity_assurance/modules/grac... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 44 | src/zephyr/infrastructure/capacity_assurance/modules/hawt... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 45 | src/zephyr/infrastructure/capacity_assurance/modules/mult... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 46 | src/zephyr/infrastructure/capacity_assurance/modules/obse... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 47 | src/zephyr/infrastructure/capacity_assurance/modules/owne... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 48 | src/zephyr/infrastructure/capacity_assurance/modules/per_... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 49 | src/zephyr/infrastructure/capacity_assurance/modules/star... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 50 | src/zephyr/infrastructure/capacity_assurance/modules/sunk... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 51 | src/zephyr/infrastructure/capacity_assurance/modules/time... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 52 | src/zephyr/infrastructure/capacity_assurance/modules/toke... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 53 | src/zephyr/infrastructure/capacity_assurance/modules/trac... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 54 | src/zephyr/infrastructure/capacity_assurance/modules/winf... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 55 | src/zephyr/infrastructure/capacity_assurance/risk_mitigat... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 56 | src/zephyr/infrastructure/capacity_assurance/schema.py | src/zephyr/infrastructure/capacity_as... | production | generated |
| 57 | src/zephyr/infrastructure/capacity_assurance/sli_instrume... | src/zephyr/infrastructure/capacity_as... | production | generated |
| 58 | src/zephyr/infrastructure/capacity_assurance/tech_stack.py | src/zephyr/infrastructure/capacity_as... | production | generated |
| 59 | src/zephyr/infrastructure/compensation/__init__.py | src/zephyr/infrastructure/compensatio... | production | generated |
| 60 | src/zephyr/infrastructure/config/__init__.py | src/zephyr/infrastructure/config/__in... | production | generated |
| 61 | src/zephyr/infrastructure/config/shared/config/__init__.py | src/zephyr/infrastructure/config/shar... | production | generated |
| 62 | src/zephyr/infrastructure/config/shared/config/loader.py | src/zephyr/infrastructure/config/shar... | production | generated |
| 63 | src/zephyr/infrastructure/config_validator.py | src/zephyr/infrastructure/config_vali... | production | generated |
| 64 | src/zephyr/infrastructure/contract_tester.py | src/zephyr/infrastructure/contract_te... | production | generated |
| 65 | src/zephyr/infrastructure/core/__init__.py | src/zephyr/infrastructure/core/__init... | prototype | deprecated |
| 66 | src/zephyr/infrastructure/cost_tracker.py | src/zephyr/infrastructure/cost_tracke... | production | generated |
| 67 | src/zephyr/infrastructure/dashboard/__init__.py | src/zephyr/infrastructure/dashboard/_... | production | deprecated |
| 68 | src/zephyr/infrastructure/dashboard/components/__init__.py | src/zephyr/infrastructure/dashboard/c... | production | deprecated |
| 69 | src/zephyr/infrastructure/db/__init__.py | src/zephyr/infrastructure/db/__init__.py | production | generated |
| 70 | src/zephyr/infrastructure/db/atomic_transaction_manager.py | src/zephyr/infrastructure/db/atomic_t... | production | generated |
| 71 | src/zephyr/infrastructure/db/audit_schema.py | src/zephyr/infrastructure/db/audit_sc... | production | generated |
| 72 | src/zephyr/infrastructure/db/base_repo.py | src/zephyr/infrastructure/db/base_rep... | production | generated |
| 73 | src/zephyr/infrastructure/db/circuit_breaker_repo.py | src/zephyr/infrastructure/db/circuit_... | production | generated |
| 74 | src/zephyr/infrastructure/db/circuit_breaker_types.py | src/zephyr/infrastructure/db/circuit_... | production | generated |
| 75 | src/zephyr/infrastructure/db/database_manager.py | src/zephyr/infrastructure/db/database... | production | generated |
| 76 | src/zephyr/infrastructure/db/gate_repo.py | src/zephyr/infrastructure/db/gate_rep... | production | generated |
| 77 | src/zephyr/infrastructure/db/olap_engine.py | src/zephyr/infrastructure/db/olap_eng... | production | generated |
| 78 | src/zephyr/infrastructure/db/query.py | src/zephyr/infrastructure/db/query.py | production | generated |
| 79 | src/zephyr/infrastructure/db/query_metrics.py | src/zephyr/infrastructure/db/query_me... | production | generated |
| 80 | src/zephyr/infrastructure/db/sqlite_schema.py | src/zephyr/infrastructure/db/sqlite_s... | production | generated |
| 81 | src/zephyr/infrastructure/db/task_repo.py | src/zephyr/infrastructure/db/task_rep... | production | generated |
| 82 | src/zephyr/infrastructure/db/transition.py | src/zephyr/infrastructure/db/transiti... | production | generated |
| 83 | src/zephyr/infrastructure/dependency/__init__.py | src/zephyr/infrastructure/dependency/... | production | generated |
| 84 | src/zephyr/infrastructure/doc_guard_server.py | src/zephyr/infrastructure/doc_guard_s... | production | generated |
| 85 | src/zephyr/infrastructure/draft/__init__.py | src/zephyr/infrastructure/draft/__ini... | production | generated |
| 86 | src/zephyr/infrastructure/dry_run_simulator.py | src/zephyr/infrastructure/dry_run_sim... | production | generated |
| 87 | src/zephyr/infrastructure/error_codes.py | src/zephyr/infrastructure/error_codes.py | production | generated |
| 88 | src/zephyr/infrastructure/event_bus_upgrade.py | src/zephyr/infrastructure/event_bus_u... | production | generated |
| 89 | src/zephyr/infrastructure/event_store.py | src/zephyr/infrastructure/event_store.py | production | generated |
| 90 | src/zephyr/infrastructure/file_watcher.py | src/zephyr/infrastructure/file_watche... | production | generated |
| 91 | src/zephyr/infrastructure/finding_task_bridge.py | src/zephyr/infrastructure/finding_tas... | production | generated |
| 92 | src/zephyr/infrastructure/gate_engine_server.py | src/zephyr/infrastructure/gate_engine... | production | generated |
| 93 | src/zephyr/infrastructure/gateway_server.py | src/zephyr/infrastructure/gateway_ser... | production | generated |
| 94 | src/zephyr/infrastructure/handoff_auto_loader.py | src/zephyr/infrastructure/handoff_aut... | production | generated |
| 95 | src/zephyr/infrastructure/health_monitor/__init__.py | src/zephyr/infrastructure/health_moni... | production | generated |
| 96 | src/zephyr/infrastructure/health_monitor/health_aggregato... | src/zephyr/infrastructure/health_moni... | production | generated |
| 97 | src/zephyr/infrastructure/hooks/__init__.py | src/zephyr/infrastructure/hooks/__ini... | production | generated |
| 98 | src/zephyr/infrastructure/hooks/event_hook.py | src/zephyr/infrastructure/hooks/event... | production | generated |
| 99 | src/zephyr/infrastructure/impact/__init__.py | src/zephyr/infrastructure/impact/__in... | production | generated |
| 100 | src/zephyr/infrastructure/impact/impact_propagator.py | src/zephyr/infrastructure/impact/impa... | production | generated |
| 101 | src/zephyr/infrastructure/impact/llm_impact_analyzer.py | src/zephyr/infrastructure/impact/llm_... | production | generated |
| 102 | src/zephyr/infrastructure/infra_06/__init__.py | src/zephyr/infrastructure/infra_06/__... | production | generated |
| 103 | src/zephyr/infrastructure/infra_06/cache.py | src/zephyr/infrastructure/infra_06/ca... | production | generated |
| 104 | src/zephyr/infrastructure/infra_06/process_lifecycle_gate... | src/zephyr/infrastructure/infra_06/pr... | production | generated |
| 105 | src/zephyr/infrastructure/infra_06/process_pool.py | src/zephyr/infrastructure/infra_06/pr... | production | generated |
| 106 | src/zephyr/infrastructure/infrastructure/__init__.py | src/zephyr/infrastructure/infrastruct... | prototype | deprecated |
| 107 | src/zephyr/infrastructure/infrastructure_base.py | src/zephyr/infrastructure/infrastruct... | production | generated |
| 108 | src/zephyr/infrastructure/kill_switch_sim.py | src/zephyr/infrastructure/kill_switch... | production | generated |
| 109 | src/zephyr/infrastructure/knowledge/__init__.py | src/zephyr/infrastructure/knowledge/_... | production | generated |
| 110 | src/zephyr/infrastructure/knowledge_base_server.py | src/zephyr/infrastructure/knowledge_b... | production | generated |
| 111 | src/zephyr/infrastructure/lifecycle/__init__.py | src/zephyr/infrastructure/lifecycle/_... | production | generated |
| 112 | src/zephyr/infrastructure/lifecycle/lazy_loader.py | src/zephyr/infrastructure/lifecycle/l... | production | generated |
| 113 | src/zephyr/infrastructure/lifecycle/resource_optimization... | src/zephyr/infrastructure/lifecycle/r... | production | generated |
| 114 | src/zephyr/infrastructure/lifecycle/scope_guard.py | src/zephyr/infrastructure/lifecycle/s... | production | generated |
| 115 | src/zephyr/infrastructure/lifecycle/task_lifecycle_manage... | src/zephyr/infrastructure/lifecycle/t... | production | generated |
| 116 | src/zephyr/infrastructure/maintenance/__init__.py | src/zephyr/infrastructure/maintenance... | production | generated |
| 117 | src/zephyr/infrastructure/models/__init__.py | src/zephyr/infrastructure/models/__in... | prototype | deprecated |
| 118 | src/zephyr/infrastructure/observability_02/__init__.py | src/zephyr/infrastructure/observabili... | production | generated |
| 119 | src/zephyr/infrastructure/observability_02/session_audit.py | src/zephyr/infrastructure/observabili... | production | generated |
| 120 | src/zephyr/infrastructure/prompt_provider.py | src/zephyr/infrastructure/prompt_prov... | production | generated |
| 121 | src/zephyr/infrastructure/pydantic_v2_migrator.py | src/zephyr/infrastructure/pydantic_v2... | production | generated |
| 122 | src/zephyr/infrastructure/rate_limiter.py | src/zephyr/infrastructure/rate_limite... | production | generated |
| 123 | src/zephyr/infrastructure/resource_provider.py | src/zephyr/infrastructure/resource_pr... | production | generated |
| 124 | src/zephyr/infrastructure/runtime/__init__.py | src/zephyr/infrastructure/runtime/__i... | production | generated |
| 125 | src/zephyr/infrastructure/runtime/startup_shutdown.py | src/zephyr/infrastructure/runtime/sta... | production | generated |
| 126 | src/zephyr/infrastructure/sandbox_server.py | src/zephyr/infrastructure/sandbox_ser... | production | generated |
| 127 | src/zephyr/infrastructure/script_system/__init__.py | src/zephyr/infrastructure/script_syst... | production | generated |
| 128 | src/zephyr/infrastructure/script_system/finding.py | src/zephyr/infrastructure/script_syst... | production | generated |
| 129 | src/zephyr/infrastructure/script_system/gate_bridge.py | src/zephyr/infrastructure/script_syst... | production | generated |
| 130 | src/zephyr/infrastructure/script_system/kb_bridge.py | src/zephyr/infrastructure/script_syst... | production | generated |
| 131 | src/zephyr/infrastructure/sentinel_server.py | src/zephyr/infrastructure/sentinel_se... | production | generated |
| 132 | src/zephyr/infrastructure/services/__init__.py | src/zephyr/infrastructure/services/__... | prototype | deprecated |
| 133 | src/zephyr/infrastructure/task_manager_server.py | src/zephyr/infrastructure/task_manage... | production | generated |
| 134 | src/zephyr/infrastructure/telemetry_server.py | src/zephyr/infrastructure/telemetry_s... | production | generated |
| 135 | src/zephyr/infrastructure/vector_memory_server.py | src/zephyr/infrastructure/vector_memo... | production | generated |
| 136 | src/zephyr/infrastructure/warm_hot_gate.py | src/zephyr/infrastructure/warm_hot_ga... | production | generated |
| 137 | src/zephyr/shared/lifecycle/__init__.py | src/zephyr/shared/lifecycle/__init__.py | production | generated |
| 138 | src/zephyr/shared/lifecycle/daemon_registry.py | src/zephyr/shared/lifecycle/daemon_re... | production | generated |
| 139 | src/zephyr/shared/lifecycle/daemon_registry_from_infra.py | src/zephyr/shared/lifecycle/daemon_re... | production | generated |
| 140 | src/zephyr/shared/lifecycle/hooks.py | src/zephyr/shared/lifecycle/hooks.py | production | generated |
| 141 | src/zephyr/shared/lifecycle/hooks_from_infra.py | src/zephyr/shared/lifecycle/hooks_fro... | production | generated |
| 142 | src/zephyr/shared/lifecycle/lazy_loader.py | src/zephyr/shared/lifecycle/lazy_load... | production | generated |
| 143 | src/zephyr/shared/lifecycle/resource_optimization_engine.py | src/zephyr/shared/lifecycle/resource_... | production | generated |
| 144 | src/zephyr/shared/lifecycle/resource_optimization_models.py | src/zephyr/shared/lifecycle/resource_... | production | generated |
| 145 | src/zephyr/shared/lifecycle/resource_optimization_models_... | src/zephyr/shared/lifecycle/resource_... | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 101 条 / 101 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 101 条 / 101 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 63 条 / edges                                │
│   [config_depends]: 38 条 / edges                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (63 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   blueprint_search_server.py → __init__.py                       │
│   doc_guard_server.py → __init__.py                              │
│   gateway_server.py → __init__.py                                │
│   knowledge_base_server.py → __init__.py                         │
│   gate_engine_server.py → __init__.py                            │
│   sentinel_server.py → __init__.py                               │
│   vector_memory_server.py → __init__.py                          │
│   sandbox_server.py → __init__.py                                │
│   warm_hot_gate.py → __init__.py                                 │
│   _base_server.py → __init__.py                                  │
│   __init__.py → __init__.py                                      │
│   classifier.py → __init__.py                                    │
│   index_generator.py → __init__.py                               │
│   lifecycle.py → __init__.py                                     │
│   dashboard.py → __init__.py                                     │
│   reconciler.py → __init__.py                                    │
│   scanner.py → __init__.py                                       │
│   registry_adapter.py → __init__.py                              │
│   telemetry.py → __init__.py                                     │
│   __main__.py → __init__.py                                      │
│   contract_bus.py → __init__.py                                  │
│   __init__.py → __init__.py                                      │
│   __init__.py → context_budget_guard.py                          │
│   __init__.py → degradation_spiral_detect...                     │
│   __init__.py → dr_drill_scheduler.py                            │
│   __init__.py → graceful_shutdown.py                             │
│   __init__.py → hawthorne_blind.py                               │
│   __init__.py → multi_model_vendor_risk.py                       │
│   __init__.py → observer_effect_compensat...                     │
│   __init__.py → owner_health_monitor.py                          │
│   __init__.py → per_task_token_budget.py                         │
│   __init__.py → cliff_detector.py                                │
│   __init__.py → capacity_testing_harness.py                      │
│   __init__.py → ai_skill_monitor.py                              │
│   __init__.py → sunk_cost_intervention.py                        │
│   __init__.py → config_reload_semantic.py                        │
│   __init__.py → token_value_attribution.py                       │
│   __init__.py → time_partitioned_slo.py                          │
│   __init__.py → startup_guard.py                                 │
│   __init__.py → cold_start_estimator.py                          │
│   __init__.py → trace_capacity_injector.py                       │
│   __init__.py → winfs_defense.py                                 │
│   __init__.py → __init__.py                                      │
│   __init__.py → __init__.py                                      │
│   circuit_breaker_repo.py → __init__.py                          │
│   database_manager.py → __init__.py                              │
│   query.py → __init__.py                                         │
│   __init__.py → __init__.py                                      │
│   transition.py → __init__.py                                    │
│   ...还有 14 条 / 14 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (38 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 101 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `04_d_infra_runtime_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
