---
doc_type: domain_architecture_doc
title: D-SHARED shared_services架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-SHARED shared_services架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-SHARED |
| 域名称 | shared_services |
| 架构层 | L1_platform |
| 模块总数 | 290 |
| 设计态模块 | 7 |
| 原型态模块 | 204 |
| 生产态模块 | 79 |
| 容量 | 62/150 (正常) |
| 描述 | 事件总线(event_bus) |

## 模块清单

共 290 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-SHARED/14条知识注入路径 14 Knowledge Injection Paths |  | design_only | design | 0 | 0 |
| D-SHARED/Event Schema Versioning 事件Schema版本管理 |  | design_only | design | 0 | 0 |
| D-SHARED/权重中心接口 Weight-Centric Interface |  | design_only | design | 0 | 0 |
| src/zephyr/shared/SHARED-QUICKREF.yml | MOD-SHARED | orphan | production | 0 | 0 |
| src/zephyr/shared/__init__.py | MOD-SHARED | draft | production | 30 | 0 |
| src/zephyr/shared/__version__.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/_cross_layer/__init__.py | MOD-INF-002 | draft | prototype | 1 | 0 |
| src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py | MOD-INF-002 | draft | prototype | 2 | 3 |
| src/zephyr/shared/_state_machine_registry.yaml | MOD-INF-016 | orphan | production | 0 | 0 |
| src/zephyr/shared/adaptation/execution_tuner.py | SRC-083 | draft | prototype | 1 | 0 |
| src/zephyr/shared/adaptation/prompt_version_manager.py | SRC-084 | draft | prototype | 0 | 1 |
| src/zephyr/shared/adaptive_sampler.py | MOD-SHARED | draft | production | 2 | 0 |
| src/zephyr/shared/ai_audit_guard.py | MOD-SHARED | draft | production | 1 | 0 |
| src/zephyr/shared/ai_understandability_constraint.py | MOD-SHARED | draft | production | 1 | 0 |
| src/zephyr/shared/alert_escalation.py | MOD-SHARED | draft | production | 1 | 0 |
| src/zephyr/shared/alert_manager.py | MOD-SHARED | draft | production | 4 | 0 |
| src/zephyr/shared/alert_precision_tracker.py | MOD-SHARED | draft | production | 3 | 0 |
| src/zephyr/shared/api/__init__.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/api/api_client.py | MOD-INF-016 | draft | prototype | 1 | 4 |
| src/zephyr/shared/api/api_index.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/api/dos_launcher.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/api/shared_quickref.yaml | MOD-INF-016 | orphan | production | 0 | 0 |
| src/zephyr/shared/api_client.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/api_index.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/blueprint_code_auditor.py | MOD-SHARED | draft | production | 3 | 0 |
| src/zephyr/shared/blueprint_decomposer.py | SRC-086 | draft | prototype | 1 | 4 |
| src/zephyr/shared/blueprint_scorer.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/budget_aware_prompt.py | MOD-SHARED | draft | production | 1 | 0 |
| src/zephyr/shared/cache.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/capability.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/capacity_calibrator.py | MOD-SHARED | draft | production | 2 | 0 |
| src/zephyr/shared/capacity_digital_twin.py | MOD-SHARED | draft | production | 2 | 0 |
| src/zephyr/shared/capacity_fingerprint.py | MOD-SHARED | draft | production | 2 | 0 |
| src/zephyr/shared/capacity_runbook_generator.py | MOD-SHARED | draft | production | 2 | 0 |
| src/zephyr/shared/code_economy_analyzer.py | MOD-SHARED | draft | production | 2 | 0 |
| src/zephyr/shared/combinatorial_gate.py | MOD-SHARED | draft | production | 3 | 0 |
| src/zephyr/shared/compensation/saga_compensator.py | SRC-088 | orphan | prototype | 0 | 0 |
| src/zephyr/shared/config/__init__.py | MOD-INF-016 | draft | prototype | 2 | 2 |
| src/zephyr/shared/config/loader.py | MOD-INF-016 | draft | prototype | 2 | 1 |
| src/zephyr/shared/constants.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/content_fingerprint.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/context.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/context_engine.py | SRC-089 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contract_bus.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/contract_tester.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/__init__.py | MOD-INF-016 | draft | prototype | 1 | 21 |
| src/zephyr/shared/contracts/backpressure/__init__.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/backpressure/_types.py | MOD-SHARECONTRACTS | draft | prototype | 3 | 1 |
| src/zephyr/shared/contracts/backpressure/pause.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/backpressure/resume.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/backpressure/throttle.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/core/__init__.py | MOD-INF-002 | draft | prototype | 0 | 2 |
| src/zephyr/shared/contracts/core/base_event.py | MOD-INF-002 | draft | prototype | 2 | 0 |
| src/zephyr/shared/contracts/core/enforcer.py | MOD-INF-002 | draft | prototype | 2 | 0 |
| src/zephyr/shared/contracts/core/factories.py | MOD-INF-002 | draft | prototype | 3 | 0 |
| src/zephyr/shared/contracts/core/gate_types.py | MOD-INF-002 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/core/registry.py | MOD-INF-002 | draft | prototype | 2 | 2 |
| src/zephyr/shared/contracts/core/runtime_plane_tag.py | MOD-INF-002 | draft | prototype | 2 | 0 |
| src/zephyr/shared/contracts/core/system_configuration.py | MOD-INF-002 | draft | prototype | 2 | 0 |
| src/zephyr/shared/contracts/core/telemetry_emitter.py | MOD-INF-002 | stable | production | 2 | 0 |
| src/zephyr/shared/contracts/core/timestamp.py | MOD-INF-002 | draft | prototype | 2 | 0 |
| src/zephyr/shared/contracts/core/trace_context.py | MOD-INF-002 | draft | prototype | 7 | 0 |
| src/zephyr/shared/contracts/errors/__init__.py | MOD-INF-016 | draft | prototype | 4 | 3 |
| src/zephyr/shared/contracts/errors/contract_violation_error.py | MOD-INF-016 | draft | prototype | 2 | 1 |
| src/zephyr/shared/contracts/errors/data_quality_error.py | MOD-INF-016 | draft | prototype | 2 | 1 |
| src/zephyr/shared/contracts/errors/execution_rejection_error.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/errors/factor_computation_error.py | MOD-INF-016 | draft | prototype | 2 | 1 |
| src/zephyr/shared/contracts/errors/risk_limit_violation_error.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/errors/signal_degradation_warning.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/escalation/__init__.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/contracts/escalation/budget_alert.py | MOD-INF-016 | draft | production | 14 | 0 |
| src/zephyr/shared/contracts/execution/__init__.py | MOD-INF-016 | draft | prototype | 5 | 0 |
| src/zephyr/shared/contracts/execution/capital_allocation_result.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/execution/execution_report.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/execution/fill.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/execution/model_serving_request.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/execution/order.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/experiment/__init__.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/experiment/experiment_result.py | MOD-INF-016 | draft | prototype | 3 | 1 |
| src/zephyr/shared/contracts/experiment/model_serving_response.py | MOD-INF-016 | draft | prototype | 4 | 0 |
| src/zephyr/shared/contracts/external/__init__.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/external/ext_001.py | MOD-INF-016 | draft | prototype | 2 | 0 |
| src/zephyr/shared/contracts/external/ext_002.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/external/ext_003.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/external/ext_004.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/freeze_manifest.yaml | MOD-INF-016 | orphan | production | 0 | 0 |
| src/zephyr/shared/contracts/gate/__init__.py | MOD-INF-002 | draft | prototype | 11 | 1 |
| src/zephyr/shared/contracts/gate/gate_result.py | MOD-INF-002 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/identity/__init__.py | MOD-INF-016 | draft | prototype | 1 | 2 |
| src/zephyr/shared/contracts/identity/agent_identity.py | MOD-INF-016 | draft | prototype | 3 | 0 |
| src/zephyr/shared/contracts/identity/permission.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/llm_gateway_protocol.py | MOD-INF-016 | draft | prototype | 5 | 0 |
| src/zephyr/shared/contracts/market/__init__.py | MOD-INF-016 | draft | prototype | 0 | 6 |
| src/zephyr/shared/contracts/market/factor_monitor_report.py | MOD-INF-016 | stable | production | 1 | 0 |
| src/zephyr/shared/contracts/market/factor_signal.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/market/instrument.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/market/macro_factor_signal.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/market/market_data.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/market/synthesized_signal.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/orchestration_protocol.py | MOD-INF-016 | draft | prototype | 3 | 0 |
| src/zephyr/shared/contracts/portfolio/__init__.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/contracts/portfolio/money.py | MOD-INF-016 | draft | production | 2 | 0 |
| src/zephyr/shared/contracts/portfolio/performance_attribution_report.py | MOD-INF-016 | draft | prototype | 2 | 0 |
| src/zephyr/shared/contracts/portfolio/position.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/portfolio/strategy_lifecycle_event.py | MOD-INF-016 | draft | prototype | 5 | 0 |
| src/zephyr/shared/contracts/risk/__init__.py | MOD-INF-016 | draft | prototype | 0 | 5 |
| src/zephyr/shared/contracts/risk/compliance_rule.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/risk/risk_dashboard_snapshot.py | MOD-INF-016 | stable | production | 1 | 0 |
| src/zephyr/shared/contracts/risk/risk_limits.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/risk/risk_metrics.py | MOD-INF-016 | stable | production | 1 | 0 |
| src/zephyr/shared/contracts/risk/risk_validator_protocol.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/contracts/security/__init__.py | MOD-INF-016 | draft | prototype | 4 | 1 |
| src/zephyr/shared/contracts/security/security_decision.py | MOD-INF-016 | draft | prototype | 3 | 0 |
| src/zephyr/shared/contracts/skill_protocol.py | MOD-INF-016 | draft | prototype | 4 | 0 |
| src/zephyr/shared/contracts/task_repository_protocol.py | MOD-INF-016 | draft | prototype | 21 | 0 |
| src/zephyr/shared/core_integrity_guard.py | MOD-SHARED | draft | production | 3 | 0 |
| src/zephyr/shared/cost_estimator.py | MOD-SHARED | draft | production | 1 | 0 |
| src/zephyr/shared/degradation_chain.py | MOD-SHARED | draft | production | 1 | 0 |
| src/zephyr/shared/dependency/dependency_graph.py | SRC-091 | orphan | prototype | 0 | 0 |
| src/zephyr/shared/dependency_capacity_guard.py | MOD-SHARED | draft | production | 1 | 0 |
| src/zephyr/shared/deprecation.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/diff_utils.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/draft/draft_assistant.py | SRC-093 | orphan | prototype | 0 | 0 |
| src/zephyr/shared/dual_channel_alert.py | MOD-SHARED | draft | production | 3 | 0 |
| src/zephyr/shared/env.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/error_budget_tracker.py | MOD-SHARED | draft | production | 3 | 0 |
| src/zephyr/shared/errors.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/event_bus.py | MOD-INF-016 | stable | production | 1 | 1 |
| src/zephyr/shared/events/__init__.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/events/dlq.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/events/dlq_bridge.py | MOD-INF-016 | draft | prototype | 2 | 1 |
| src/zephyr/shared/events/event_bus.py | SRC-095 | stable | production | 1 | 1 |
| src/zephyr/shared/events/event_bus_upgrade.py | MOD-INF-016 | draft | production | 2 | 0 |
| src/zephyr/shared/events/event_reactor.py | SRC-096 | draft | prototype | 0 | 1 |
| src/zephyr/shared/events/event_schemas.py | MOD-INF-016 | draft | prototype | 1 | 2 |
| src/zephyr/shared/events/hook_dispatcher.py | SRC-098 | draft | prototype | 0 | 1 |
| src/zephyr/shared/events/upgrade_strategy.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/fault_isolator.py | MOD-SHARED | draft | production | 1 | 0 |
| src/zephyr/shared/file_utils.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/flags.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/foundation/__init__.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/foundation/constants.py | MOD-INF-016 | draft | prototype | 2 | 4 |
| src/zephyr/shared/foundation/deprecation.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/foundation/env.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/foundation/errors.py | MOD-INF-016 | draft | prototype | 17 | 0 |
| src/zephyr/shared/foundation/flags.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/foundation/types.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/frontmatter_utils.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/health.py | MOD-INF-016 | stable | production | 0 | 1 |
| src/zephyr/shared/healthcheck_service.py | SRC-099 | stable | production | 0 | 1 |
| src/zephyr/shared/heartbeat_server.py | MOD-SHARED | draft | production | 2 | 0 |
| src/zephyr/shared/idempotency.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/infra/__init__.py | MOD-INF-016 | draft | prototype | 0 | 2 |
| src/zephyr/shared/infra/cache.py | MOD-INF-016 | draft | prototype | 4 | 1 |
| src/zephyr/shared/infra/idempotency.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/infra/limiter.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/infra/lock.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/infra/observer.py | MOD-INF-016 | draft | prototype | 8 | 0 |
| src/zephyr/shared/infra/outbox.py | MOD-INF-016 | draft | prototype | 1 | 2 |
| src/zephyr/shared/infra/process_lifecycle_gateway.py | MOD-INF-016 | draft | production | 3 | 2 |
| src/zephyr/shared/infra/process_pool.py | MOD-INF-016 | draft | prototype | 2 | 1 |
| src/zephyr/shared/infra_06/idempotency.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/infra_06/limiter.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/infra_06/lock.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/infra_06/observer.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/infra_06/outbox.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/io/__init__.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/io/content_fingerprint.py | MOD-INF-016 | draft | prototype | 2 | 0 |
| src/zephyr/shared/io/file_utils.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/io/frontmatter_utils.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/io/io_cache.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/io/paths.py | MOD-INF-016 | draft | prototype | 14 | 0 |
| src/zephyr/shared/io/serialization.py | MOD-INF-016 | draft | prototype | 2 | 1 |
| src/zephyr/shared/io/streaming_reader.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/knowledge/ke_linker.py | SRC-104 | draft | prototype | 1 | 1 |
| src/zephyr/shared/knowledge/ke_structurer.py | SRC-105 | draft | prototype | 1 | 0 |
| src/zephyr/shared/knowledge/kms_interface.py | SRC-106 | draft | prototype | 0 | 1 |
| src/zephyr/shared/limiter.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/lock.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/logging.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/longevity_monitor.py | MOD-SHARED | draft | production | 2 | 0 |
| src/zephyr/shared/maintenance/autonomy_monitor.py | SRC-116 | stable | production | 0 | 1 |
| src/zephyr/shared/maintenance/dogfooding.py | SRC-117 | draft | prototype | 1 | 0 |
| src/zephyr/shared/maintenance/handbook.py | SRC-118 | draft | prototype | 0 | 1 |
| src/zephyr/shared/maintenance/zero_config.py | SRC-119 | draft | prototype | 2 | 1 |
| src/zephyr/shared/metrics.py | MOD-INF-016 | stable | production | 0 | 1 |
| src/zephyr/shared/migration.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/model_capacity_probe.py | MOD-SHARED | draft | production | 2 | 0 |
| src/zephyr/shared/models.py | SRC-120 | draft | prototype | 1 | 0 |
| src/zephyr/shared/module_birth_registry.py | MOD-SHARED | draft | production | 2 | 0 |
| src/zephyr/shared/observability_02/health.py | MOD-INF-016 | stable | production | 2 | 1 |
| src/zephyr/shared/observability_02/health_discovery.py | MOD-INF-016 | stable | production | 0 | 1 |
| src/zephyr/shared/observability_02/logging.py | MOD-INF-016 | draft | prototype | 2 | 0 |
| src/zephyr/shared/observability_02/metrics.py | MOD-INF-016 | stable | production | 1 | 0 |
| src/zephyr/shared/observability_02/token_utils.py | MOD-INF-016 | draft | prototype | 1 | 0 |
| src/zephyr/shared/observability_02/tracing.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/observer.py | MOD-INF-016 | draft | prototype | 1 | 1 |
| src/zephyr/shared/outbox.py | MOD-INF-016 | draft | prototype | 0 | 1 |
| src/zephyr/shared/owner_trust_gauge.py | MOD-SHARED | draft | production | 1 | 0 |
| src/zephyr/shared/pagination.py | MOD-INF-016 | draft | prototype | 0 | 1 |

> (仅显示前 200 个模块，共 290 个)

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-INTEGRATION | 9 | contract,import_depends |
| D-INFRA_RUNTIME | 7 | import_depends |
| D-OPS | 6 | import_depends |
| D-GOVERNANCE | 3 | import_depends |
| D-ML_TRAIN | 2 | import_depends |
| D-SIMULATION | 1 | import_depends |
| D-GOV_AUDIT | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 269 | test_depends,import_depends,data,event,contract |
| D-INTEGRATION | 73 | import_depends,event,data,contract |
| D-INFRA_RUNTIME | 67 | import_depends,contract,event,data |
| D-TRADING | 43 | import_depends,contract |
| D-SECURITY | 9 | import_depends,data,event,contract |
| D-GOV_RULE | 9 | import_depends |
| D-OPS | 7 | import_depends |
| D-AUTONOMY_CORE | 6 | import_depends |
| D-KNOWLEDGE | 4 | contract,data,event |
| D-DATA_ENG | 4 | contract,data,event |
| D-ALT_DATA | 4 | contract,data,event |
| D-MKT_DATA | 3 | event,data,contract |
| D-DATA_GOV | 3 | data,contract,event |
| D-PF_ALLOC | 2 | contract,import_depends |
| D-ML_TRAIN | 2 | import_depends |
| D-SELL_DECISION | 1 | contract |
| D-RISK | 1 | import_depends |
| D-POSITION | 1 | contract |
| D-ML_SERVE | 1 | contract |
| D-INTELLIGENCE | 1 | import_depends |
| D-INFRA_OPS | 1 | import_depends |
| D-GOV_AUDIT | 1 | import_depends |
| D-FRONTEND | 1 | import_depends |
| D-FACTOR | 1 | import_depends |
| D-EX_SOR | 1 | contract |
| D-CROSS_ASSET | 1 | import_depends |
| D-BEHAVIORAL_AUDIT | 1 | import_depends |

## 域内依赖图

详见 [d_shared_dependency.mmd](d_shared_dependency.mmd)
