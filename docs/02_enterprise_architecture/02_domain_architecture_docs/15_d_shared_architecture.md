---
doc_type: domain_architecture_diagram
title: D-SHARED 共享服务架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 15_d_shared / 共享服务 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示共享服务（D-SHARED）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:01:56
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 共享服务（D-SHARED）的模块分布。共 289 个模块 / 289 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│        L0 基础设施层 / Infrastructure Layer (73 modules)         │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/integration/shared_08/contracts/gate/gate_result... │
│   src/zephyr/shared/contracts/__init__.py  [prototype]           │
│   src/zephyr/shared/contracts/backpressure/__init__.py  [prot... │
│   src/zephyr/shared/contracts/backpressure/_types.py  [protot... │
│   src/zephyr/shared/contracts/backpressure/pause.py  [prototype] │
│   src/zephyr/shared/contracts/backpressure/resume.py  [protot... │
│   src/zephyr/shared/contracts/backpressure/throttle.py  [prot... │
│   src/zephyr/shared/contracts/core/__init__.py  [prototype]      │
│   src/zephyr/shared/contracts/core/base_event.py  [prototype]    │
│   src/zephyr/shared/contracts/core/enforcer.py  [prototype]      │
│   src/zephyr/shared/contracts/core/factories.py  [prototype]     │
│   src/zephyr/shared/contracts/core/gate_types.py  [prototype]    │
│   src/zephyr/shared/contracts/core/registry.py  [prototype]      │
│   src/zephyr/shared/contracts/core/runtime_plane_tag.py  [pro... │
│   src/zephyr/shared/contracts/core/system_configuration.py  [... │
│   src/zephyr/shared/contracts/core/telemetry_emitter.py  [pro... │
│   src/zephyr/shared/contracts/core/timestamp.py  [prototype]     │
│   src/zephyr/shared/contracts/core/trace_context.py  [prototype] │
│   ...还有 55 个模块 / 55 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (212 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/integration/shared/api_03/api_index.py  [prototype] │
│   src/zephyr/integration/shared_08/context.py  [prototype]       │
│   src/zephyr/shared/__init__.py  [production]                    │
│   src/zephyr/shared/__version__.py  [prototype]                  │
│   src/zephyr/shared/_cross_layer/__init__.py  [prototype]        │
│   src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py  [... │
│   src/zephyr/shared/_state_machine_registry.yaml  [production]   │
│   src/zephyr/shared/adaptation/execution_tuner.py  [prototype]   │
│   src/zephyr/shared/adaptation/prompt_version_manager.py  [pr... │
│   src/zephyr/shared/adaptive_sampler.py  [production]            │
│   src/zephyr/shared/ai_audit_guard.py  [production]              │
│   src/zephyr/shared/ai_understandability_constraint.py  [prod... │
│   src/zephyr/shared/alert_escalation.py  [production]            │
│   src/zephyr/shared/alert_manager.py  [production]               │
│   src/zephyr/shared/alert_precision_tracker.py  [production]     │
│   src/zephyr/shared/api/__init__.py  [prototype]                 │
│   src/zephyr/shared/api/api_client.py  [prototype]               │
│   src/zephyr/shared/api/api_index.py  [prototype]                │
│   ...还有 194 个模块 / 194 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L3 应用层 / Application Layer (1 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   tools/_gen_dedup_tests.py  [prototype]                         │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (3 modules)                 │
├──────────────────────────────────────────────────────────────────┤
│   14条知识注入路径 14 Knowledge Injection Paths  [design]        │
│   Event Schema Versioning 事件Schema版本管理  [design]           │
│   权重中心接口 Weight-Centric Interface  [design]                │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 289 个模块 / 289 modules）。

### L0 基础设施层 / Infrastructure Layer (73 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/integration/shared_08/contracts/gate/gate_resu... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 2 | src/zephyr/shared/contracts/__init__.py | src/zephyr/shared/contracts/__init__.py | prototype | draft |
| 3 | src/zephyr/shared/contracts/backpressure/__init__.py | src/zephyr/shared/contracts/backpress... | prototype | draft |
| 4 | src/zephyr/shared/contracts/backpressure/_types.py | src/zephyr/shared/contracts/backpress... | prototype | draft |
| 5 | src/zephyr/shared/contracts/backpressure/pause.py | src/zephyr/shared/contracts/backpress... | prototype | draft |
| 6 | src/zephyr/shared/contracts/backpressure/resume.py | src/zephyr/shared/contracts/backpress... | prototype | draft |
| 7 | src/zephyr/shared/contracts/backpressure/throttle.py | src/zephyr/shared/contracts/backpress... | prototype | draft |
| 8 | src/zephyr/shared/contracts/core/__init__.py | src/zephyr/shared/contracts/core/__in... | prototype | draft |
| 9 | src/zephyr/shared/contracts/core/base_event.py | src/zephyr/shared/contracts/core/base... | prototype | draft |
| 10 | src/zephyr/shared/contracts/core/enforcer.py | src/zephyr/shared/contracts/core/enfo... | prototype | draft |
| 11 | src/zephyr/shared/contracts/core/factories.py | src/zephyr/shared/contracts/core/fact... | prototype | draft |
| 12 | src/zephyr/shared/contracts/core/gate_types.py | src/zephyr/shared/contracts/core/gate... | prototype | draft |
| 13 | src/zephyr/shared/contracts/core/registry.py | src/zephyr/shared/contracts/core/regi... | prototype | draft |
| 14 | src/zephyr/shared/contracts/core/runtime_plane_tag.py | src/zephyr/shared/contracts/core/runt... | prototype | draft |
| 15 | src/zephyr/shared/contracts/core/system_configuration.py | src/zephyr/shared/contracts/core/syst... | prototype | draft |
| 16 | src/zephyr/shared/contracts/core/telemetry_emitter.py | src/zephyr/shared/contracts/core/tele... | production | stable |
| 17 | src/zephyr/shared/contracts/core/timestamp.py | src/zephyr/shared/contracts/core/time... | prototype | draft |
| 18 | src/zephyr/shared/contracts/core/trace_context.py | src/zephyr/shared/contracts/core/trac... | prototype | draft |
| 19 | src/zephyr/shared/contracts/errors/__init__.py | src/zephyr/shared/contracts/errors/__... | prototype | draft |
| 20 | src/zephyr/shared/contracts/errors/contract_violation_err... | src/zephyr/shared/contracts/errors/co... | prototype | draft |
| 21 | src/zephyr/shared/contracts/errors/data_quality_error.py | src/zephyr/shared/contracts/errors/da... | prototype | draft |
| 22 | src/zephyr/shared/contracts/errors/execution_rejection_er... | src/zephyr/shared/contracts/errors/ex... | prototype | draft |
| 23 | src/zephyr/shared/contracts/errors/factor_computation_err... | src/zephyr/shared/contracts/errors/fa... | prototype | draft |
| 24 | src/zephyr/shared/contracts/errors/risk_limit_violation_e... | src/zephyr/shared/contracts/errors/ri... | prototype | draft |
| 25 | src/zephyr/shared/contracts/errors/signal_degradation_war... | src/zephyr/shared/contracts/errors/si... | prototype | draft |
| 26 | src/zephyr/shared/contracts/escalation/__init__.py | src/zephyr/shared/contracts/escalatio... | prototype | draft |
| 27 | src/zephyr/shared/contracts/escalation/budget_alert.py | src/zephyr/shared/contracts/escalatio... | production | draft |
| 28 | src/zephyr/shared/contracts/execution/__init__.py | src/zephyr/shared/contracts/execution... | prototype | draft |
| 29 | src/zephyr/shared/contracts/execution/capital_allocation_... | src/zephyr/shared/contracts/execution... | prototype | draft |
| 30 | src/zephyr/shared/contracts/execution/execution_report.py | src/zephyr/shared/contracts/execution... | prototype | draft |
| 31 | src/zephyr/shared/contracts/execution/fill.py | src/zephyr/shared/contracts/execution... | prototype | draft |
| 32 | src/zephyr/shared/contracts/execution/model_serving_reque... | src/zephyr/shared/contracts/execution... | prototype | draft |
| 33 | src/zephyr/shared/contracts/execution/order.py | src/zephyr/shared/contracts/execution... | prototype | draft |
| 34 | src/zephyr/shared/contracts/experiment/__init__.py | src/zephyr/shared/contracts/experimen... | prototype | draft |
| 35 | src/zephyr/shared/contracts/experiment/experiment_result.py | src/zephyr/shared/contracts/experimen... | prototype | draft |
| 36 | src/zephyr/shared/contracts/experiment/model_serving_resp... | src/zephyr/shared/contracts/experimen... | prototype | draft |
| 37 | src/zephyr/shared/contracts/external/__init__.py | src/zephyr/shared/contracts/external/... | prototype | draft |
| 38 | src/zephyr/shared/contracts/external/ext_001.py | src/zephyr/shared/contracts/external/... | prototype | draft |
| 39 | src/zephyr/shared/contracts/external/ext_002.py | src/zephyr/shared/contracts/external/... | prototype | draft |
| 40 | src/zephyr/shared/contracts/external/ext_003.py | src/zephyr/shared/contracts/external/... | prototype | draft |
| 41 | src/zephyr/shared/contracts/external/ext_004.py | src/zephyr/shared/contracts/external/... | prototype | draft |
| 42 | src/zephyr/shared/contracts/freeze_manifest.yaml | src/zephyr/shared/contracts/freeze_ma... | production | orphan |
| 43 | src/zephyr/shared/contracts/identity/__init__.py | src/zephyr/shared/contracts/identity/... | prototype | draft |
| 44 | src/zephyr/shared/contracts/identity/agent_identity.py | src/zephyr/shared/contracts/identity/... | prototype | draft |
| 45 | src/zephyr/shared/contracts/identity/permission.py | src/zephyr/shared/contracts/identity/... | prototype | draft |
| 46 | src/zephyr/shared/contracts/llm_gateway_protocol.py | src/zephyr/shared/contracts/llm_gatew... | prototype | draft |
| 47 | src/zephyr/shared/contracts/market/__init__.py | src/zephyr/shared/contracts/market/__... | prototype | draft |
| 48 | src/zephyr/shared/contracts/market/factor_monitor_report.py | src/zephyr/shared/contracts/market/fa... | production | stable |
| 49 | src/zephyr/shared/contracts/market/factor_signal.py | src/zephyr/shared/contracts/market/fa... | prototype | draft |
| 50 | src/zephyr/shared/contracts/market/instrument.py | src/zephyr/shared/contracts/market/in... | prototype | draft |
| 51 | src/zephyr/shared/contracts/market/macro_factor_signal.py | src/zephyr/shared/contracts/market/ma... | prototype | draft |
| 52 | src/zephyr/shared/contracts/market/market_data.py | src/zephyr/shared/contracts/market/ma... | prototype | draft |
| 53 | src/zephyr/shared/contracts/market/synthesized_signal.py | src/zephyr/shared/contracts/market/sy... | prototype | draft |
| 54 | src/zephyr/shared/contracts/orchestration_protocol.py | src/zephyr/shared/contracts/orchestra... | prototype | draft |
| 55 | src/zephyr/shared/contracts/portfolio/__init__.py | src/zephyr/shared/contracts/portfolio... | prototype | draft |
| 56 | src/zephyr/shared/contracts/portfolio/money.py | src/zephyr/shared/contracts/portfolio... | production | draft |
| 57 | src/zephyr/shared/contracts/portfolio/performance_attribu... | src/zephyr/shared/contracts/portfolio... | prototype | draft |
| 58 | src/zephyr/shared/contracts/portfolio/position.py | src/zephyr/shared/contracts/portfolio... | prototype | draft |
| 59 | src/zephyr/shared/contracts/portfolio/strategy_lifecycle_... | src/zephyr/shared/contracts/portfolio... | prototype | draft |
| 60 | src/zephyr/shared/contracts/risk/__init__.py | src/zephyr/shared/contracts/risk/__in... | prototype | draft |
| 61 | src/zephyr/shared/contracts/risk/compliance_rule.py | src/zephyr/shared/contracts/risk/comp... | prototype | draft |
| 62 | src/zephyr/shared/contracts/risk/risk_dashboard_snapshot.py | src/zephyr/shared/contracts/risk/risk... | production | stable |
| 63 | src/zephyr/shared/contracts/risk/risk_limits.py | src/zephyr/shared/contracts/risk/risk... | prototype | draft |
| 64 | src/zephyr/shared/contracts/risk/risk_metrics.py | src/zephyr/shared/contracts/risk/risk... | production | stable |
| 65 | src/zephyr/shared/contracts/risk/risk_validator_protocol.py | src/zephyr/shared/contracts/risk/risk... | prototype | draft |
| 66 | src/zephyr/shared/contracts/security/__init__.py | src/zephyr/shared/contracts/security/... | prototype | draft |
| 67 | src/zephyr/shared/contracts/security/security_decision.py | src/zephyr/shared/contracts/security/... | prototype | draft |
| 68 | src/zephyr/shared/contracts/skill_protocol.py | src/zephyr/shared/contracts/skill_pro... | prototype | draft |
| 69 | src/zephyr/shared/contracts/task_repository_protocol.py | src/zephyr/shared/contracts/task_repo... | prototype | draft |
| 70 | ✅保留/D-INTEGRATION-11 | Event Bus Manager | design | design_only |
| 71 | ✅能建/D-INTEGRATION-33 | Integration Config Manager | design | design_only |
| 72 | ✅能建/D-INTEGRATION-43 | Local Model Integration | design | design_only |
| 73 | 移除/D-INTEGRATION-13 | Integration Health Monitor | design | design_only |

### L1 基础层 / Foundation Layer (212 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/integration/shared/api_03/api_index.py | src/zephyr/integration/shared/api_03/... | prototype | draft |
| 2 | src/zephyr/integration/shared_08/context.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 3 | src/zephyr/shared/__init__.py | src/zephyr/shared/__init__.py | production | draft |
| 4 | src/zephyr/shared/__version__.py | src/zephyr/shared/__version__.py | prototype | draft |
| 5 | src/zephyr/shared/_cross_layer/__init__.py | src/zephyr/shared/_cross_layer/__init... | prototype | draft |
| 6 | src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py | src/zephyr/shared/_cross_layer/ml_exp... | prototype | draft |
| 7 | src/zephyr/shared/_state_machine_registry.yaml | src/zephyr/shared/_state_machine_regi... | production | orphan |
| 8 | src/zephyr/shared/adaptation/execution_tuner.py | src/zephyr/shared/adaptation/executio... | prototype | draft |
| 9 | src/zephyr/shared/adaptation/prompt_version_manager.py | src/zephyr/shared/adaptation/prompt_v... | prototype | draft |
| 10 | src/zephyr/shared/adaptive_sampler.py | src/zephyr/shared/adaptive_sampler.py | production | draft |
| 11 | src/zephyr/shared/ai_audit_guard.py | src/zephyr/shared/ai_audit_guard.py | production | draft |
| 12 | src/zephyr/shared/ai_understandability_constraint.py | src/zephyr/shared/ai_understandabilit... | production | draft |
| 13 | src/zephyr/shared/alert_escalation.py | src/zephyr/shared/alert_escalation.py | production | draft |
| 14 | src/zephyr/shared/alert_manager.py | src/zephyr/shared/alert_manager.py | production | draft |
| 15 | src/zephyr/shared/alert_precision_tracker.py | src/zephyr/shared/alert_precision_tra... | production | draft |
| 16 | src/zephyr/shared/api/__init__.py | src/zephyr/shared/api/__init__.py | prototype | draft |
| 17 | src/zephyr/shared/api/api_client.py | src/zephyr/shared/api/api_client.py | prototype | draft |
| 18 | src/zephyr/shared/api/api_index.py | src/zephyr/shared/api/api_index.py | prototype | draft |
| 19 | src/zephyr/shared/api/dos_launcher.py | src/zephyr/shared/api/dos_launcher.py | prototype | draft |
| 20 | src/zephyr/shared/api/shared_quickref.yaml | src/zephyr/shared/api/shared_quickref... | production | orphan |
| 21 | src/zephyr/shared/api_client.py | src/zephyr/shared/api_client.py | prototype | draft |
| 22 | src/zephyr/shared/blueprint_code_auditor.py | src/zephyr/shared/blueprint_code_audi... | production | draft |
| 23 | src/zephyr/shared/blueprint_decomposer.py | src/zephyr/shared/blueprint_decompose... | prototype | draft |
| 24 | src/zephyr/shared/blueprint_scorer.py | src/zephyr/shared/blueprint_scorer.py | prototype | draft |
| 25 | src/zephyr/shared/budget_aware_prompt.py | src/zephyr/shared/budget_aware_prompt.py | production | draft |
| 26 | src/zephyr/shared/cache.py | src/zephyr/shared/cache.py | prototype | draft |
| 27 | src/zephyr/shared/capability.py | src/zephyr/shared/capability.py | prototype | draft |
| 28 | src/zephyr/shared/capacity_calibrator.py | src/zephyr/shared/capacity_calibrator.py | production | draft |
| 29 | src/zephyr/shared/capacity_digital_twin.py | src/zephyr/shared/capacity_digital_tw... | production | draft |
| 30 | src/zephyr/shared/capacity_fingerprint.py | src/zephyr/shared/capacity_fingerprin... | production | draft |
| 31 | src/zephyr/shared/capacity_runbook_generator.py | src/zephyr/shared/capacity_runbook_ge... | production | draft |
| 32 | src/zephyr/shared/code_economy_analyzer.py | src/zephyr/shared/code_economy_analyz... | production | draft |
| 33 | src/zephyr/shared/combinatorial_gate.py | src/zephyr/shared/combinatorial_gate.py | production | draft |
| 34 | src/zephyr/shared/compensation/saga_compensator.py | src/zephyr/shared/compensation/saga_c... | prototype | orphan |
| 35 | src/zephyr/shared/config/__init__.py | src/zephyr/shared/config/__init__.py | prototype | draft |
| 36 | src/zephyr/shared/config/loader.py | src/zephyr/shared/config/loader.py | prototype | draft |
| 37 | src/zephyr/shared/constants.py | src/zephyr/shared/constants.py | prototype | draft |
| 38 | src/zephyr/shared/content_fingerprint.py | src/zephyr/shared/content_fingerprint.py | prototype | draft |
| 39 | src/zephyr/shared/context_engine.py | src/zephyr/shared/context_engine.py | prototype | draft |
| 40 | src/zephyr/shared/contract_bus.py | src/zephyr/shared/contract_bus.py | prototype | draft |
| 41 | src/zephyr/shared/contract_tester.py | src/zephyr/shared/contract_tester.py | prototype | draft |
| 42 | src/zephyr/shared/core_integrity_guard.py | src/zephyr/shared/core_integrity_guar... | production | draft |
| 43 | src/zephyr/shared/cost_estimator.py | src/zephyr/shared/cost_estimator.py | production | draft |
| 44 | src/zephyr/shared/degradation_chain.py | src/zephyr/shared/degradation_chain.py | production | draft |
| 45 | src/zephyr/shared/dependency/dependency_graph.py | src/zephyr/shared/dependency/dependen... | prototype | orphan |
| 46 | src/zephyr/shared/dependency_capacity_guard.py | src/zephyr/shared/dependency_capacity... | production | draft |
| 47 | src/zephyr/shared/deprecation.py | src/zephyr/shared/deprecation.py | prototype | draft |
| 48 | src/zephyr/shared/diff_utils.py | src/zephyr/shared/diff_utils.py | prototype | draft |
| 49 | src/zephyr/shared/draft/draft_assistant.py | src/zephyr/shared/draft/draft_assista... | prototype | orphan |
| 50 | src/zephyr/shared/dual_channel_alert.py | src/zephyr/shared/dual_channel_alert.py | production | draft |
| 51 | src/zephyr/shared/env.py | src/zephyr/shared/env.py | prototype | draft |
| 52 | src/zephyr/shared/error_budget_tracker.py | src/zephyr/shared/error_budget_tracke... | production | draft |
| 53 | src/zephyr/shared/errors.py | src/zephyr/shared/errors.py | prototype | draft |
| 54 | src/zephyr/shared/event_bus.py | src/zephyr/shared/event_bus.py | production | stable |
| 55 | src/zephyr/shared/event_bus.py | src/zephyr/shared/event_bus.py | production | draft |
| 56 | src/zephyr/shared/events/__init__.py | src/zephyr/shared/events/__init__.py | prototype | draft |
| 57 | src/zephyr/shared/events/dlq.py | src/zephyr/shared/events/dlq.py | prototype | draft |
| 58 | src/zephyr/shared/events/dlq_bridge.py | src/zephyr/shared/events/dlq_bridge.py | prototype | draft |
| 59 | src/zephyr/shared/events/event_bus.py | src/zephyr/shared/events/event_bus.py | production | stable |
| 60 | src/zephyr/shared/events/event_bus_upgrade.py | src/zephyr/shared/events/event_bus_up... | production | draft |
| 61 | src/zephyr/shared/events/event_reactor.py | src/zephyr/shared/events/event_reacto... | prototype | draft |
| 62 | src/zephyr/shared/events/event_schemas.py | src/zephyr/shared/events/event_schema... | prototype | draft |
| 63 | src/zephyr/shared/events/hook_dispatcher.py | src/zephyr/shared/events/hook_dispatc... | prototype | draft |
| 64 | src/zephyr/shared/events/upgrade_strategy.py | src/zephyr/shared/events/upgrade_stra... | prototype | draft |
| 65 | src/zephyr/shared/fault_isolator.py | src/zephyr/shared/fault_isolator.py | production | draft |
| 66 | src/zephyr/shared/file_utils.py | src/zephyr/shared/file_utils.py | prototype | draft |
| 67 | src/zephyr/shared/flags.py | src/zephyr/shared/flags.py | prototype | draft |
| 68 | src/zephyr/shared/foundation/__init__.py | src/zephyr/shared/foundation/__init__.py | prototype | draft |
| 69 | src/zephyr/shared/foundation/constants.py | src/zephyr/shared/foundation/constant... | prototype | draft |
| 70 | src/zephyr/shared/foundation/deprecation.py | src/zephyr/shared/foundation/deprecat... | prototype | draft |
| 71 | src/zephyr/shared/foundation/env.py | src/zephyr/shared/foundation/env.py | prototype | draft |
| 72 | src/zephyr/shared/foundation/errors.py | src/zephyr/shared/foundation/errors.py | prototype | draft |
| 73 | src/zephyr/shared/foundation/flags.py | src/zephyr/shared/foundation/flags.py | prototype | draft |
| 74 | src/zephyr/shared/foundation/types.py | src/zephyr/shared/foundation/types.py | prototype | draft |
| 75 | src/zephyr/shared/frontmatter_utils.py | src/zephyr/shared/frontmatter_utils.py | prototype | draft |
| 76 | src/zephyr/shared/health.py | src/zephyr/shared/health.py | production | stable |
| 77 | src/zephyr/shared/healthcheck_service.py | src/zephyr/shared/healthcheck_service.py | production | stable |
| 78 | src/zephyr/shared/heartbeat_server.py | src/zephyr/shared/heartbeat_server.py | production | draft |
| 79 | src/zephyr/shared/idempotency.py | src/zephyr/shared/idempotency.py | prototype | draft |
| 80 | src/zephyr/shared/infra/__init__.py | src/zephyr/shared/infra/__init__.py | prototype | draft |
| 81 | src/zephyr/shared/infra/cache.py | src/zephyr/shared/infra/cache.py | prototype | draft |
| 82 | src/zephyr/shared/infra/idempotency.py | src/zephyr/shared/infra/idempotency.py | prototype | draft |
| 83 | src/zephyr/shared/infra/limiter.py | src/zephyr/shared/infra/limiter.py | prototype | draft |
| 84 | src/zephyr/shared/infra/lock.py | src/zephyr/shared/infra/lock.py | prototype | draft |
| 85 | src/zephyr/shared/infra/observer.py | src/zephyr/shared/infra/observer.py | prototype | draft |
| 86 | src/zephyr/shared/infra/outbox.py | src/zephyr/shared/infra/outbox.py | prototype | draft |
| 87 | src/zephyr/shared/infra/process_lifecycle_gateway.py | src/zephyr/shared/infra/process_lifec... | production | draft |
| 88 | src/zephyr/shared/infra/process_pool.py | src/zephyr/shared/infra/process_pool.py | prototype | draft |
| 89 | src/zephyr/shared/infra_06/idempotency.py | src/zephyr/shared/infra_06/idempotenc... | prototype | draft |
| 90 | src/zephyr/shared/infra_06/limiter.py | src/zephyr/shared/infra_06/limiter.py | prototype | draft |
| 91 | src/zephyr/shared/infra_06/lock.py | src/zephyr/shared/infra_06/lock.py | prototype | draft |
| 92 | src/zephyr/shared/infra_06/observer.py | src/zephyr/shared/infra_06/observer.py | prototype | draft |
| 93 | src/zephyr/shared/infra_06/outbox.py | src/zephyr/shared/infra_06/outbox.py | prototype | draft |
| 94 | src/zephyr/shared/io/__init__.py | src/zephyr/shared/io/__init__.py | prototype | draft |
| 95 | src/zephyr/shared/io/content_fingerprint.py | src/zephyr/shared/io/content_fingerpr... | prototype | draft |
| 96 | src/zephyr/shared/io/file_utils.py | src/zephyr/shared/io/file_utils.py | prototype | draft |
| 97 | src/zephyr/shared/io/frontmatter_utils.py | src/zephyr/shared/io/frontmatter_util... | prototype | draft |
| 98 | src/zephyr/shared/io/io_cache.py | src/zephyr/shared/io/io_cache.py | prototype | draft |
| 99 | src/zephyr/shared/io/paths.py | src/zephyr/shared/io/paths.py | prototype | draft |
| 100 | src/zephyr/shared/io/serialization.py | src/zephyr/shared/io/serialization.py | prototype | draft |
| 101 | src/zephyr/shared/io/streaming_reader.py | src/zephyr/shared/io/streaming_reader.py | prototype | draft |
| 102 | src/zephyr/shared/knowledge/ke_linker.py | src/zephyr/shared/knowledge/ke_linker.py | prototype | draft |
| 103 | src/zephyr/shared/knowledge/ke_structurer.py | src/zephyr/shared/knowledge/ke_struct... | prototype | draft |
| 104 | src/zephyr/shared/knowledge/kms_interface.py | src/zephyr/shared/knowledge/kms_inter... | prototype | draft |
| 105 | src/zephyr/shared/limiter.py | src/zephyr/shared/limiter.py | prototype | draft |
| 106 | src/zephyr/shared/lock.py | src/zephyr/shared/lock.py | prototype | draft |
| 107 | src/zephyr/shared/logging.py | src/zephyr/shared/logging.py | prototype | draft |
| 108 | src/zephyr/shared/longevity_monitor.py | src/zephyr/shared/longevity_monitor.py | production | draft |
| 109 | src/zephyr/shared/maintenance/autonomy_monitor.py | src/zephyr/shared/maintenance/autonom... | production | stable |
| 110 | src/zephyr/shared/maintenance/dogfooding.py | src/zephyr/shared/maintenance/dogfood... | prototype | draft |
| 111 | src/zephyr/shared/maintenance/handbook.py | src/zephyr/shared/maintenance/handboo... | prototype | draft |
| 112 | src/zephyr/shared/maintenance/zero_config.py | src/zephyr/shared/maintenance/zero_co... | prototype | draft |
| 113 | src/zephyr/shared/metrics.py | src/zephyr/shared/metrics.py | production | stable |
| 114 | src/zephyr/shared/migration.py | src/zephyr/shared/migration.py | prototype | draft |
| 115 | src/zephyr/shared/model_capacity_probe.py | src/zephyr/shared/model_capacity_prob... | production | draft |
| 116 | src/zephyr/shared/models.py | src/zephyr/shared/models.py | prototype | draft |
| 117 | src/zephyr/shared/module_birth_registry.py | src/zephyr/shared/module_birth_regist... | production | draft |
| 118 | src/zephyr/shared/observability_02/health.py | src/zephyr/shared/observability_02/he... | production | stable |
| 119 | src/zephyr/shared/observability_02/health_discovery.py | src/zephyr/shared/observability_02/he... | production | stable |
| 120 | src/zephyr/shared/observability_02/logging.py | src/zephyr/shared/observability_02/lo... | prototype | draft |
| 121 | src/zephyr/shared/observability_02/metrics.py | src/zephyr/shared/observability_02/me... | production | stable |
| 122 | src/zephyr/shared/observability_02/tracing.py | src/zephyr/shared/observability_02/tr... | prototype | draft |
| 123 | src/zephyr/shared/observer.py | src/zephyr/shared/observer.py | prototype | draft |
| 124 | src/zephyr/shared/outbox.py | src/zephyr/shared/outbox.py | prototype | draft |
| 125 | src/zephyr/shared/owner_trust_gauge.py | src/zephyr/shared/owner_trust_gauge.py | production | draft |
| 126 | src/zephyr/shared/pagination.py | src/zephyr/shared/pagination.py | prototype | draft |
| 127 | src/zephyr/shared/paths.py | src/zephyr/shared/paths.py | prototype | draft |
| 128 | src/zephyr/shared/ports.py | src/zephyr/shared/ports.py | prototype | draft |
| 129 | src/zephyr/shared/protocols/__init__.py | src/zephyr/shared/protocols/__init__.py | prototype | draft |
| 130 | src/zephyr/shared/protocols/a2a/__init__.py | src/zephyr/shared/protocols/a2a/__ini... | prototype | draft |
| 131 | src/zephyr/shared/protocols/a2a/a2a_coordination.py | src/zephyr/shared/protocols/a2a/a2a_c... | prototype | draft |
| 132 | src/zephyr/shared/protocols/a2a/a2a_protocol.py | src/zephyr/shared/protocols/a2a/a2a_p... | prototype | draft |
| 133 | src/zephyr/shared/protocols/a2a/a2a_registry.py | src/zephyr/shared/protocols/a2a/a2a_r... | prototype | draft |
| 134 | src/zephyr/shared/protocols/a2a/a2a_schemas.py | src/zephyr/shared/protocols/a2a/a2a_s... | prototype | draft |
| 135 | src/zephyr/shared/protocols/a2a/layer3_coordination/__ini... | src/zephyr/shared/protocols/a2a/layer... | prototype | draft |
| 136 | src/zephyr/shared/quality/quality_monitor.py | quality_monitor | production | stable |
| 137 | src/zephyr/shared/reasoning_spans.py | src/zephyr/shared/reasoning_spans.py | production | draft |
| 138 | src/zephyr/shared/registry.py | src/zephyr/shared/registry.py | prototype | draft |
| 139 | src/zephyr/shared/reliability/diff_planner.py | src/zephyr/shared/reliability/diff_pl... | prototype | draft |
| 140 | src/zephyr/shared/reliability/retry_handler.py | src/zephyr/shared/reliability/retry_h... | prototype | draft |
| 141 | src/zephyr/shared/resilience/__init__.py | src/zephyr/shared/resilience/__init__.py | prototype | draft |
| 142 | src/zephyr/shared/resilience/circuit_breaker.py | src/zephyr/shared/resilience/circuit_... | prototype | draft |
| 143 | src/zephyr/shared/resilience/fallback.py | src/zephyr/shared/resilience/fallback.py | prototype | draft |
| 144 | src/zephyr/shared/resilience/retry.py | src/zephyr/shared/resilience/retry.py | prototype | draft |
| 145 | src/zephyr/shared/sandbox_executor.py | src/zephyr/shared/sandbox_executor.py | production | draft |
| 146 | src/zephyr/shared/schema/__init__.py | src/zephyr/shared/schema/__init__.py | prototype | draft |
| 147 | src/zephyr/shared/schema/base_config.py | src/zephyr/shared/schema/base_config.py | prototype | draft |
| 148 | src/zephyr/shared/schema/schema_registry.py | src/zephyr/shared/schema/schema_regis... | prototype | draft |
| 149 | src/zephyr/shared/schema/schemas.py | src/zephyr/shared/schema/schemas.py | prototype | draft |
| 150 | src/zephyr/shared/schema/severity_types.py | src/zephyr/shared/schema/severity_typ... | prototype | draft |
| 151 | src/zephyr/shared/schema_registry.py | src/zephyr/shared/schema_registry.py | prototype | draft |
| 152 | src/zephyr/shared/schemas.py | src/zephyr/shared/schemas.py | prototype | draft |
| 153 | src/zephyr/shared/secrets.py | src/zephyr/shared/secrets.py | prototype | draft |
| 154 | src/zephyr/shared/security/__init__.py | src/zephyr/shared/security/__init__.py | prototype | draft |
| 155 | src/zephyr/shared/security/capability.py | src/zephyr/shared/security/capability.py | prototype | draft |
| 156 | src/zephyr/shared/security/secrets.py | src/zephyr/shared/security/secrets.py | prototype | draft |
| 157 | src/zephyr/shared/security/ssot_guard.py | src/zephyr/shared/security/ssot_guard.py | prototype | draft |
| 158 | src/zephyr/shared/serialization.py | src/zephyr/shared/serialization.py | prototype | draft |
| 159 | src/zephyr/shared/session/session_boundary.py | src/zephyr/shared/session/session_bou... | prototype | draft |
| 160 | src/zephyr/shared/session/session_continuity.py | src/zephyr/shared/session/session_con... | prototype | draft |
| 161 | src/zephyr/shared/session_audit.py | src/zephyr/shared/session_audit.py | prototype | draft |
| 162 | src/zephyr/shared/session_continuity.py | src/zephyr/shared/session_continuity.py | prototype | draft |
| 163 | src/zephyr/shared/shared_quickref.yaml | src/zephyr/shared/shared_quickref.yaml | production | orphan |
| 164 | src/zephyr/shared/shared_services/__init__.py | src/zephyr/shared/shared_services/__i... | production | draft |
| 165 | src/zephyr/shared/shared_services/blueprint_decomposer.py | src/zephyr/shared/shared_services/blu... | production | draft |
| 166 | src/zephyr/shared/shared_services/events/__init__.py | src/zephyr/shared/shared_services/eve... | production | draft |
| 167 | src/zephyr/shared/shared_services/infra_06/__init__.py | src/zephyr/shared/shared_services/inf... | prototype | draft |
| 168 | src/zephyr/shared/shared_services/infra_06/cache.py | src/zephyr/shared/shared_services/inf... | production | draft |
| 169 | src/zephyr/shared/shared_services/infra_06/idempotency.py | src/zephyr/shared/shared_services/inf... | production | draft |
| 170 | src/zephyr/shared/shared_services/infra_06/limiter.py | src/zephyr/shared/shared_services/inf... | prototype | draft |
| 171 | src/zephyr/shared/shared_services/infra_06/lock.py | src/zephyr/shared/shared_services/inf... | production | draft |
| 172 | src/zephyr/shared/shared_services/infra_06/observer.py | src/zephyr/shared/shared_services/inf... | production | draft |
| 173 | src/zephyr/shared/shared_services/infra_06/outbox.py | src/zephyr/shared/shared_services/inf... | production | draft |
| 174 | src/zephyr/shared/shared_services/infra_06/process_pool.py | src/zephyr/shared/shared_services/inf... | production | draft |
| 175 | src/zephyr/shared/shared_services/lifecycle/__init__.py | src/zephyr/shared/shared_services/lif... | production | draft |
| 176 | src/zephyr/shared/shared_services/lifecycle/daemon_regist... | src/zephyr/shared/shared_services/lif... | production | draft |
| 177 | src/zephyr/shared/shared_services/lifecycle/task_lifecycl... | src/zephyr/shared/shared_services/lif... | production | draft |
| 178 | src/zephyr/shared/shared_services/models.py | src/zephyr/shared/shared_services/mod... | production | draft |
| 179 | src/zephyr/shared/shared_services/observability_02/__init... | src/zephyr/shared/shared_services/obs... | prototype | draft |
| 180 | src/zephyr/shared/shared_services/observability_02/health.py | src/zephyr/shared/shared_services/obs... | production | stable |
| 181 | src/zephyr/shared/shared_services/observability_02/loggin... | src/zephyr/shared/shared_services/obs... | production | draft |
| 182 | src/zephyr/shared/shared_services/observability_02/metric... | src/zephyr/shared/shared_services/obs... | production | stable |
| 183 | src/zephyr/shared/shared_services/observability_02/sessio... | src/zephyr/shared/shared_services/obs... | production | draft |
| 184 | src/zephyr/shared/shared_services/observability_02/token_... | src/zephyr/shared/shared_services/obs... | prototype | draft |
| 185 | src/zephyr/shared/shared_services/observability_02/token_... | src/zephyr/shared/shared_services/obs... | prototype | draft |
| 186 | src/zephyr/shared/shared_services/observability_02/token_... | src/zephyr/shared/shared_services/obs... | production | draft |
| 187 | src/zephyr/shared/shared_services/observability_02/tracin... | src/zephyr/shared/shared_services/obs... | production | draft |
| 188 | src/zephyr/shared/shared_services/queue/__init__.py | src/zephyr/shared/shared_services/que... | production | draft |
| 189 | src/zephyr/shared/shared_services/queue/task_queue.py | src/zephyr/shared/shared_services/que... | prototype | draft |
| 190 | src/zephyr/shared/shared_services/session_continuity.py | src/zephyr/shared/shared_services/ses... | production | draft |
| 191 | src/zephyr/shared/shared_util/__init__.py | src/zephyr/shared/shared_util/__init_... | prototype | orphan |
| 192 | src/zephyr/shared/sla/sla_monitor.py | sla_monitor | production | stable |
| 193 | src/zephyr/shared/slo_review_assistant.py | src/zephyr/shared/slo_review_assistan... | production | draft |
| 194 | src/zephyr/shared/ssot_guard.py | src/zephyr/shared/ssot_guard.py | prototype | draft |
| 195 | src/zephyr/shared/state_machine.py | src/zephyr/shared/state_machine.py | prototype | draft |
| 196 | src/zephyr/shared/task_heartbeat.py | src/zephyr/shared/task_heartbeat.py | production | draft |
| 197 | src/zephyr/shared/task_types.py | src/zephyr/shared/task_types.py | prototype | draft |
| 198 | src/zephyr/shared/testing.py | src/zephyr/shared/testing.py | prototype | draft |
| 199 | src/zephyr/shared/time_utils.py | src/zephyr/shared/time_utils.py | prototype | draft |
| 200 | src/zephyr/shared/tracing.py | src/zephyr/shared/tracing.py | prototype | draft |

> (仅显示前 200 个模块，共 212 个)

### L3 应用层 / Application Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | tools/_gen_dedup_tests.py | tools/_gen_dedup_tests.py | prototype | orphan |

### 未分类 / Unclassified (3 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-SHARED/14条知识注入路径 14 Knowledge Injection Paths | 14条知识注入路径 14 Knowledge Injecti... | design | design_only |
| 2 | D-SHARED/Event Schema Versioning 事件Schema版本管理 | Event Schema Versioning 事件Schema版... | design | design_only |
| 3 | D-SHARED/权重中心接口 Weight-Centric Interface | 权重中心接口 Weight-Centric Interface | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 186 条 / 186 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 186 条 / 186 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 156 条 / edges                               │
│   [config_depends]: 30 条 / edges                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (156 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   api_index.py → api_index.py                                    │
│   blueprint_decomposer.py → __init__.py                          │
│   blueprint_decomposer.py → models.py                            │
│   api_client.py → api_client.py                                  │
│   capability.py → capability.py                                  │
│   cache.py → cache.py                                            │
│   constants.py → constants.py                                    │
│   content_fingerprint.py → content_fingerprint.py                │
│   context.py → context.py                                        │
│   contract_bus.py → contract_violation_error.py                  │
│   errors.py → errors.py                                          │
│   diff_utils.py → diff_utils.py                                  │
│   event_bus.py → contract_bus.py                                 │
│   env.py → env.py                                                │
│   deprecation.py → deprecation.py                                │
│   flags.py → flags.py                                            │
│   frontmatter_utils.py → frontmatter_utils.py                    │
│   file_utils.py → file_utils.py                                  │
│   idempotency.py → idempotency.py                                │
│   limiter.py → limiter.py                                        │
│   lock.py → lock.py                                              │
│   migration.py → migration.py                                    │
│   observer.py → observer.py                                      │
│   outbox.py → outbox.py                                          │
│   paths.py → paths.py                                            │
│   pagination.py → pagination.py                                  │
│   ports.py → task_repository_protocol.py                         │
│   schema_registry.py → schema_registry.py                        │
│   schemas.py → schemas.py                                        │
│   serialization.py → serialization.py                            │
│   secrets.py → secrets.py                                        │
│   session_continuity.py → __init__.py                            │
│   ssot_guard.py → ssot_guard.py                                  │
│   state_machine.py → errors.py                                   │
│   testing.py → testing.py                                        │
│   time_utils.py → time_utils.py                                  │
│   types.py → types.py                                            │
│   dos_launcher.py → schemas.py                                   │
│   api_client.py → errors.py                                      │
│   api_client.py → serialization.py                               │
│   api_client.py → retry.py                                       │
│   api_client.py → circuit_breaker.py                             │
│   loader.py → errors.py                                          │
│   __init__.py → __init__.py                                      │
│   __init__.py → loader.py                                        │
│   __init__.py → skill_protocol.py                                │
│   __init__.py → orchestration_protocol.py                        │
│   __init__.py → task_repository_protocol.py                      │
│   __init__.py → llm_gateway_protocol.py                          │
│   ...还有 107 条 / 107 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (30 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 186 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `15_d_shared_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
