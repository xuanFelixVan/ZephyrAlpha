---
doc_type: domain_architecture_doc
title: D-SHARED shared_services架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 15_d_shared 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 15 | Number | 15 |
| 域ID | D-SHARED | Domain ID | D-SHARED |
| 域名称 | shared_services | Domain Name | shared_services |
| 层级 | L1_platform | Layer | L1_platform |
| 模块数 | 290 | Module Count | 290 |
| 域内依赖 | 187 | Internal Dependencies | 187 |
| 跨域入边 | 517 | Cross-domain Incoming | 517 |
| 跨域出边 | 29 | Cross-domain Outgoing | 29 |
| 设计态模块 | 7 | Design Modules | 7 |
| 原型态模块 | 204 | Prototype Modules | 204 |
| 生产态模块 | 79 | Production Modules | 79 |
| 容量 | 290/150 (超容) | Capacity | 290/150 (超容) |
| 描述 | 事件总线(event_bus) | Description | 事件总线(event_bus) |

## 模块清单 / Module List

共 290 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
| D-SHARED/14条知识注入路径 14 Knowledge Injection Paths | 14条知识注入路径 14 Knowledge Injection Paths | design | design_only | D-SHARED/14条知识注入路径 14 Knowledge Injection Paths | 14条知识注入路径 14 Knowledge Injection Paths | design | design_only |
| D-SHARED/Event Schema Versioning 事件Schema版本管理 | Event Schema Versioning 事件Schema版本管理 | design | design_only | D-SHARED/Event Schema Versioning 事件Schema版本管理 | Event Schema Versioning 事件Schema版本管理 | design | design_only |
| D-SHARED/权重中心接口 Weight-Centric Interface | 权重中心接口 Weight-Centric Interface | design | design_only | D-SHARED/权重中心接口 Weight-Centric Interface | 权重中心接口 Weight-Centric Interface | design | design_only |
| src/zephyr/shared/SHARED-QUICKREF.yml |  | production | orphan | src/zephyr/shared/SHARED-QUICKREF.yml |  | production | orphan |
| src/zephyr/shared/__init__.py |  | production | draft | src/zephyr/shared/__init__.py |  | production | draft |
| src/zephyr/shared/__version__.py |  | prototype | draft | src/zephyr/shared/__version__.py |  | prototype | draft |
| src/zephyr/shared/_cross_layer/__init__.py |  | prototype | draft | src/zephyr/shared/_cross_layer/__init__.py |  | prototype | draft |
| src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py |  | prototype | draft | src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py |  | prototype | draft |
| src/zephyr/shared/_state_machine_registry.yaml |  | production | orphan | src/zephyr/shared/_state_machine_registry.yaml |  | production | orphan |
| src/zephyr/shared/adaptation/execution_tuner.py |  | prototype | draft | src/zephyr/shared/adaptation/execution_tuner.py |  | prototype | draft |
| src/zephyr/shared/adaptation/prompt_version_manager.py |  | prototype | draft | src/zephyr/shared/adaptation/prompt_version_manager.py |  | prototype | draft |
| src/zephyr/shared/adaptive_sampler.py |  | production | draft | src/zephyr/shared/adaptive_sampler.py |  | production | draft |
| src/zephyr/shared/ai_audit_guard.py |  | production | draft | src/zephyr/shared/ai_audit_guard.py |  | production | draft |
| src/zephyr/shared/ai_understandability_constraint.py |  | production | draft | src/zephyr/shared/ai_understandability_constraint.py |  | production | draft |
| src/zephyr/shared/alert_escalation.py |  | production | draft | src/zephyr/shared/alert_escalation.py |  | production | draft |
| src/zephyr/shared/alert_manager.py |  | production | draft | src/zephyr/shared/alert_manager.py |  | production | draft |
| src/zephyr/shared/alert_precision_tracker.py |  | production | draft | src/zephyr/shared/alert_precision_tracker.py |  | production | draft |
| src/zephyr/shared/api/__init__.py |  | prototype | draft | src/zephyr/shared/api/__init__.py |  | prototype | draft |
| src/zephyr/shared/api/api_client.py |  | prototype | draft | src/zephyr/shared/api/api_client.py |  | prototype | draft |
| src/zephyr/shared/api/api_index.py |  | prototype | draft | src/zephyr/shared/api/api_index.py |  | prototype | draft |
| src/zephyr/shared/api/dos_launcher.py |  | prototype | draft | src/zephyr/shared/api/dos_launcher.py |  | prototype | draft |
| src/zephyr/shared/api/shared_quickref.yaml |  | production | orphan | src/zephyr/shared/api/shared_quickref.yaml |  | production | orphan |
| src/zephyr/shared/api_client.py |  | prototype | draft | src/zephyr/shared/api_client.py |  | prototype | draft |
| src/zephyr/shared/api_index.py |  | prototype | draft | src/zephyr/shared/api_index.py |  | prototype | draft |
| src/zephyr/shared/blueprint_code_auditor.py |  | production | draft | src/zephyr/shared/blueprint_code_auditor.py |  | production | draft |
| src/zephyr/shared/blueprint_decomposer.py |  | prototype | draft | src/zephyr/shared/blueprint_decomposer.py |  | prototype | draft |
| src/zephyr/shared/blueprint_scorer.py |  | prototype | draft | src/zephyr/shared/blueprint_scorer.py |  | prototype | draft |
| src/zephyr/shared/budget_aware_prompt.py |  | production | draft | src/zephyr/shared/budget_aware_prompt.py |  | production | draft |
| src/zephyr/shared/cache.py |  | prototype | draft | src/zephyr/shared/cache.py |  | prototype | draft |
| src/zephyr/shared/capability.py |  | prototype | draft | src/zephyr/shared/capability.py |  | prototype | draft |
| src/zephyr/shared/capacity_calibrator.py |  | production | draft | src/zephyr/shared/capacity_calibrator.py |  | production | draft |
| src/zephyr/shared/capacity_digital_twin.py |  | production | draft | src/zephyr/shared/capacity_digital_twin.py |  | production | draft |
| src/zephyr/shared/capacity_fingerprint.py |  | production | draft | src/zephyr/shared/capacity_fingerprint.py |  | production | draft |
| src/zephyr/shared/capacity_runbook_generator.py |  | production | draft | src/zephyr/shared/capacity_runbook_generator.py |  | production | draft |
| src/zephyr/shared/code_economy_analyzer.py |  | production | draft | src/zephyr/shared/code_economy_analyzer.py |  | production | draft |
| src/zephyr/shared/combinatorial_gate.py |  | production | draft | src/zephyr/shared/combinatorial_gate.py |  | production | draft |
| src/zephyr/shared/compensation/saga_compensator.py |  | prototype | orphan | src/zephyr/shared/compensation/saga_compensator.py |  | prototype | orphan |
| src/zephyr/shared/config/__init__.py |  | prototype | draft | src/zephyr/shared/config/__init__.py |  | prototype | draft |
| src/zephyr/shared/config/loader.py |  | prototype | draft | src/zephyr/shared/config/loader.py |  | prototype | draft |
| src/zephyr/shared/constants.py |  | prototype | draft | src/zephyr/shared/constants.py |  | prototype | draft |
| src/zephyr/shared/content_fingerprint.py |  | prototype | draft | src/zephyr/shared/content_fingerprint.py |  | prototype | draft |
| src/zephyr/shared/context.py |  | prototype | draft | src/zephyr/shared/context.py |  | prototype | draft |
| src/zephyr/shared/context_engine.py |  | prototype | draft | src/zephyr/shared/context_engine.py |  | prototype | draft |
| src/zephyr/shared/contract_bus.py |  | prototype | draft | src/zephyr/shared/contract_bus.py |  | prototype | draft |
| src/zephyr/shared/contract_tester.py |  | prototype | draft | src/zephyr/shared/contract_tester.py |  | prototype | draft |
| src/zephyr/shared/contracts/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/backpressure/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/backpressure/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/backpressure/_types.py |  | prototype | draft | src/zephyr/shared/contracts/backpressure/_types.py |  | prototype | draft |
| src/zephyr/shared/contracts/backpressure/pause.py |  | prototype | draft | src/zephyr/shared/contracts/backpressure/pause.py |  | prototype | draft |
| src/zephyr/shared/contracts/backpressure/resume.py |  | prototype | draft | src/zephyr/shared/contracts/backpressure/resume.py |  | prototype | draft |
| src/zephyr/shared/contracts/backpressure/throttle.py |  | prototype | draft | src/zephyr/shared/contracts/backpressure/throttle.py |  | prototype | draft |
| src/zephyr/shared/contracts/core/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/core/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/core/base_event.py |  | prototype | draft | src/zephyr/shared/contracts/core/base_event.py |  | prototype | draft |
| src/zephyr/shared/contracts/core/enforcer.py |  | prototype | draft | src/zephyr/shared/contracts/core/enforcer.py |  | prototype | draft |
| src/zephyr/shared/contracts/core/factories.py |  | prototype | draft | src/zephyr/shared/contracts/core/factories.py |  | prototype | draft |
| src/zephyr/shared/contracts/core/gate_types.py |  | prototype | draft | src/zephyr/shared/contracts/core/gate_types.py |  | prototype | draft |
| src/zephyr/shared/contracts/core/registry.py |  | prototype | draft | src/zephyr/shared/contracts/core/registry.py |  | prototype | draft |
| src/zephyr/shared/contracts/core/runtime_plane_tag.py |  | prototype | draft | src/zephyr/shared/contracts/core/runtime_plane_tag.py |  | prototype | draft |
| src/zephyr/shared/contracts/core/system_configuration.py |  | prototype | draft | src/zephyr/shared/contracts/core/system_configuration.py |  | prototype | draft |
| src/zephyr/shared/contracts/core/telemetry_emitter.py |  | production | stable | src/zephyr/shared/contracts/core/telemetry_emitter.py |  | production | stable |
| src/zephyr/shared/contracts/core/timestamp.py |  | prototype | draft | src/zephyr/shared/contracts/core/timestamp.py |  | prototype | draft |
| src/zephyr/shared/contracts/core/trace_context.py |  | prototype | draft | src/zephyr/shared/contracts/core/trace_context.py |  | prototype | draft |
| src/zephyr/shared/contracts/errors/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/errors/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/errors/contract_violation_error.py |  | prototype | draft | src/zephyr/shared/contracts/errors/contract_violation_error.py |  | prototype | draft |
| src/zephyr/shared/contracts/errors/data_quality_error.py |  | prototype | draft | src/zephyr/shared/contracts/errors/data_quality_error.py |  | prototype | draft |
| src/zephyr/shared/contracts/errors/execution_rejection_error.py |  | prototype | draft | src/zephyr/shared/contracts/errors/execution_rejection_error.py |  | prototype | draft |
| src/zephyr/shared/contracts/errors/factor_computation_error.py |  | prototype | draft | src/zephyr/shared/contracts/errors/factor_computation_error.py |  | prototype | draft |
| src/zephyr/shared/contracts/errors/risk_limit_violation_error.py |  | prototype | draft | src/zephyr/shared/contracts/errors/risk_limit_violation_error.py |  | prototype | draft |
| src/zephyr/shared/contracts/errors/signal_degradation_warning.py |  | prototype | draft | src/zephyr/shared/contracts/errors/signal_degradation_warning.py |  | prototype | draft |
| src/zephyr/shared/contracts/escalation/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/escalation/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/escalation/budget_alert.py |  | production | draft | src/zephyr/shared/contracts/escalation/budget_alert.py |  | production | draft |
| src/zephyr/shared/contracts/execution/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/execution/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/execution/capital_allocation_result.py |  | prototype | draft | src/zephyr/shared/contracts/execution/capital_allocation_result.py |  | prototype | draft |
| src/zephyr/shared/contracts/execution/execution_report.py |  | prototype | draft | src/zephyr/shared/contracts/execution/execution_report.py |  | prototype | draft |
| src/zephyr/shared/contracts/execution/fill.py |  | prototype | draft | src/zephyr/shared/contracts/execution/fill.py |  | prototype | draft |
| src/zephyr/shared/contracts/execution/model_serving_request.py |  | prototype | draft | src/zephyr/shared/contracts/execution/model_serving_request.py |  | prototype | draft |
| src/zephyr/shared/contracts/execution/order.py |  | prototype | draft | src/zephyr/shared/contracts/execution/order.py |  | prototype | draft |
| src/zephyr/shared/contracts/experiment/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/experiment/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/experiment/experiment_result.py |  | prototype | draft | src/zephyr/shared/contracts/experiment/experiment_result.py |  | prototype | draft |
| src/zephyr/shared/contracts/experiment/model_serving_response.py |  | prototype | draft | src/zephyr/shared/contracts/experiment/model_serving_response.py |  | prototype | draft |
| src/zephyr/shared/contracts/external/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/external/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/external/ext_001.py |  | prototype | draft | src/zephyr/shared/contracts/external/ext_001.py |  | prototype | draft |
| src/zephyr/shared/contracts/external/ext_002.py |  | prototype | draft | src/zephyr/shared/contracts/external/ext_002.py |  | prototype | draft |
| src/zephyr/shared/contracts/external/ext_003.py |  | prototype | draft | src/zephyr/shared/contracts/external/ext_003.py |  | prototype | draft |
| src/zephyr/shared/contracts/external/ext_004.py |  | prototype | draft | src/zephyr/shared/contracts/external/ext_004.py |  | prototype | draft |
| src/zephyr/shared/contracts/freeze_manifest.yaml |  | production | orphan | src/zephyr/shared/contracts/freeze_manifest.yaml |  | production | orphan |
| src/zephyr/shared/contracts/gate/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/gate/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/gate/gate_result.py |  | prototype | draft | src/zephyr/shared/contracts/gate/gate_result.py |  | prototype | draft |
| src/zephyr/shared/contracts/identity/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/identity/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/identity/agent_identity.py |  | prototype | draft | src/zephyr/shared/contracts/identity/agent_identity.py |  | prototype | draft |
| src/zephyr/shared/contracts/identity/permission.py |  | prototype | draft | src/zephyr/shared/contracts/identity/permission.py |  | prototype | draft |
| src/zephyr/shared/contracts/llm_gateway_protocol.py |  | prototype | draft | src/zephyr/shared/contracts/llm_gateway_protocol.py |  | prototype | draft |
| src/zephyr/shared/contracts/market/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/market/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/market/factor_monitor_report.py |  | production | stable | src/zephyr/shared/contracts/market/factor_monitor_report.py |  | production | stable |
| src/zephyr/shared/contracts/market/factor_signal.py |  | prototype | draft | src/zephyr/shared/contracts/market/factor_signal.py |  | prototype | draft |
| src/zephyr/shared/contracts/market/instrument.py |  | prototype | draft | src/zephyr/shared/contracts/market/instrument.py |  | prototype | draft |
| src/zephyr/shared/contracts/market/macro_factor_signal.py |  | prototype | draft | src/zephyr/shared/contracts/market/macro_factor_signal.py |  | prototype | draft |
| src/zephyr/shared/contracts/market/market_data.py |  | prototype | draft | src/zephyr/shared/contracts/market/market_data.py |  | prototype | draft |
| src/zephyr/shared/contracts/market/synthesized_signal.py |  | prototype | draft | src/zephyr/shared/contracts/market/synthesized_signal.py |  | prototype | draft |
| src/zephyr/shared/contracts/orchestration_protocol.py |  | prototype | draft | src/zephyr/shared/contracts/orchestration_protocol.py |  | prototype | draft |
| src/zephyr/shared/contracts/portfolio/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/portfolio/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/portfolio/money.py |  | production | draft | src/zephyr/shared/contracts/portfolio/money.py |  | production | draft |
| src/zephyr/shared/contracts/portfolio/performance_attribution_report.py |  | prototype | draft | src/zephyr/shared/contracts/portfolio/performance_attribution_report.py |  | prototype | draft |
| src/zephyr/shared/contracts/portfolio/position.py |  | prototype | draft | src/zephyr/shared/contracts/portfolio/position.py |  | prototype | draft |
| src/zephyr/shared/contracts/portfolio/strategy_lifecycle_event.py |  | prototype | draft | src/zephyr/shared/contracts/portfolio/strategy_lifecycle_event.py |  | prototype | draft |
| src/zephyr/shared/contracts/risk/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/risk/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/risk/compliance_rule.py |  | prototype | draft | src/zephyr/shared/contracts/risk/compliance_rule.py |  | prototype | draft |
| src/zephyr/shared/contracts/risk/risk_dashboard_snapshot.py |  | production | stable | src/zephyr/shared/contracts/risk/risk_dashboard_snapshot.py |  | production | stable |
| src/zephyr/shared/contracts/risk/risk_limits.py |  | prototype | draft | src/zephyr/shared/contracts/risk/risk_limits.py |  | prototype | draft |
| src/zephyr/shared/contracts/risk/risk_metrics.py |  | production | stable | src/zephyr/shared/contracts/risk/risk_metrics.py |  | production | stable |
| src/zephyr/shared/contracts/risk/risk_validator_protocol.py |  | prototype | draft | src/zephyr/shared/contracts/risk/risk_validator_protocol.py |  | prototype | draft |
| src/zephyr/shared/contracts/security/__init__.py |  | prototype | draft | src/zephyr/shared/contracts/security/__init__.py |  | prototype | draft |
| src/zephyr/shared/contracts/security/security_decision.py |  | prototype | draft | src/zephyr/shared/contracts/security/security_decision.py |  | prototype | draft |
| src/zephyr/shared/contracts/skill_protocol.py |  | prototype | draft | src/zephyr/shared/contracts/skill_protocol.py |  | prototype | draft |
| src/zephyr/shared/contracts/task_repository_protocol.py |  | prototype | draft | src/zephyr/shared/contracts/task_repository_protocol.py |  | prototype | draft |
| src/zephyr/shared/core_integrity_guard.py |  | production | draft | src/zephyr/shared/core_integrity_guard.py |  | production | draft |
| src/zephyr/shared/cost_estimator.py |  | production | draft | src/zephyr/shared/cost_estimator.py |  | production | draft |
| src/zephyr/shared/degradation_chain.py |  | production | draft | src/zephyr/shared/degradation_chain.py |  | production | draft |
| src/zephyr/shared/dependency/dependency_graph.py |  | prototype | orphan | src/zephyr/shared/dependency/dependency_graph.py |  | prototype | orphan |
| src/zephyr/shared/dependency_capacity_guard.py |  | production | draft | src/zephyr/shared/dependency_capacity_guard.py |  | production | draft |
| src/zephyr/shared/deprecation.py |  | prototype | draft | src/zephyr/shared/deprecation.py |  | prototype | draft |
| src/zephyr/shared/diff_utils.py |  | prototype | draft | src/zephyr/shared/diff_utils.py |  | prototype | draft |
| src/zephyr/shared/draft/draft_assistant.py |  | prototype | orphan | src/zephyr/shared/draft/draft_assistant.py |  | prototype | orphan |
| src/zephyr/shared/dual_channel_alert.py |  | production | draft | src/zephyr/shared/dual_channel_alert.py |  | production | draft |
| src/zephyr/shared/env.py |  | prototype | draft | src/zephyr/shared/env.py |  | prototype | draft |
| src/zephyr/shared/error_budget_tracker.py |  | production | draft | src/zephyr/shared/error_budget_tracker.py |  | production | draft |
| src/zephyr/shared/errors.py |  | prototype | draft | src/zephyr/shared/errors.py |  | prototype | draft |
| src/zephyr/shared/event_bus.py |  | production | stable | src/zephyr/shared/event_bus.py |  | production | stable |
| src/zephyr/shared/events/__init__.py |  | prototype | draft | src/zephyr/shared/events/__init__.py |  | prototype | draft |
| src/zephyr/shared/events/dlq.py |  | prototype | draft | src/zephyr/shared/events/dlq.py |  | prototype | draft |
| src/zephyr/shared/events/dlq_bridge.py |  | prototype | draft | src/zephyr/shared/events/dlq_bridge.py |  | prototype | draft |
| src/zephyr/shared/events/event_bus.py |  | production | stable | src/zephyr/shared/events/event_bus.py |  | production | stable |
| src/zephyr/shared/events/event_bus_upgrade.py |  | production | draft | src/zephyr/shared/events/event_bus_upgrade.py |  | production | draft |
| src/zephyr/shared/events/event_reactor.py |  | prototype | draft | src/zephyr/shared/events/event_reactor.py |  | prototype | draft |
| src/zephyr/shared/events/event_schemas.py |  | prototype | draft | src/zephyr/shared/events/event_schemas.py |  | prototype | draft |
| src/zephyr/shared/events/hook_dispatcher.py |  | prototype | draft | src/zephyr/shared/events/hook_dispatcher.py |  | prototype | draft |
| src/zephyr/shared/events/upgrade_strategy.py |  | prototype | draft | src/zephyr/shared/events/upgrade_strategy.py |  | prototype | draft |
| src/zephyr/shared/fault_isolator.py |  | production | draft | src/zephyr/shared/fault_isolator.py |  | production | draft |
| src/zephyr/shared/file_utils.py |  | prototype | draft | src/zephyr/shared/file_utils.py |  | prototype | draft |
| src/zephyr/shared/flags.py |  | prototype | draft | src/zephyr/shared/flags.py |  | prototype | draft |
| src/zephyr/shared/foundation/__init__.py |  | prototype | draft | src/zephyr/shared/foundation/__init__.py |  | prototype | draft |
| src/zephyr/shared/foundation/constants.py |  | prototype | draft | src/zephyr/shared/foundation/constants.py |  | prototype | draft |
| src/zephyr/shared/foundation/deprecation.py |  | prototype | draft | src/zephyr/shared/foundation/deprecation.py |  | prototype | draft |
| src/zephyr/shared/foundation/env.py |  | prototype | draft | src/zephyr/shared/foundation/env.py |  | prototype | draft |
| src/zephyr/shared/foundation/errors.py |  | prototype | draft | src/zephyr/shared/foundation/errors.py |  | prototype | draft |
| src/zephyr/shared/foundation/flags.py |  | prototype | draft | src/zephyr/shared/foundation/flags.py |  | prototype | draft |
| src/zephyr/shared/foundation/types.py |  | prototype | draft | src/zephyr/shared/foundation/types.py |  | prototype | draft |
| src/zephyr/shared/frontmatter_utils.py |  | prototype | draft | src/zephyr/shared/frontmatter_utils.py |  | prototype | draft |
| src/zephyr/shared/health.py |  | production | stable | src/zephyr/shared/health.py |  | production | stable |
| src/zephyr/shared/healthcheck_service.py |  | production | stable | src/zephyr/shared/healthcheck_service.py |  | production | stable |
| src/zephyr/shared/heartbeat_server.py |  | production | draft | src/zephyr/shared/heartbeat_server.py |  | production | draft |
| src/zephyr/shared/idempotency.py |  | prototype | draft | src/zephyr/shared/idempotency.py |  | prototype | draft |
| src/zephyr/shared/infra/__init__.py |  | prototype | draft | src/zephyr/shared/infra/__init__.py |  | prototype | draft |
| src/zephyr/shared/infra/cache.py |  | prototype | draft | src/zephyr/shared/infra/cache.py |  | prototype | draft |
| src/zephyr/shared/infra/idempotency.py |  | prototype | draft | src/zephyr/shared/infra/idempotency.py |  | prototype | draft |
| src/zephyr/shared/infra/limiter.py |  | prototype | draft | src/zephyr/shared/infra/limiter.py |  | prototype | draft |
| src/zephyr/shared/infra/lock.py |  | prototype | draft | src/zephyr/shared/infra/lock.py |  | prototype | draft |
| src/zephyr/shared/infra/observer.py |  | prototype | draft | src/zephyr/shared/infra/observer.py |  | prototype | draft |
| src/zephyr/shared/infra/outbox.py |  | prototype | draft | src/zephyr/shared/infra/outbox.py |  | prototype | draft |
| src/zephyr/shared/infra/process_lifecycle_gateway.py |  | production | draft | src/zephyr/shared/infra/process_lifecycle_gateway.py |  | production | draft |
| src/zephyr/shared/infra/process_pool.py |  | prototype | draft | src/zephyr/shared/infra/process_pool.py |  | prototype | draft |
| src/zephyr/shared/infra_06/idempotency.py |  | prototype | draft | src/zephyr/shared/infra_06/idempotency.py |  | prototype | draft |
| src/zephyr/shared/infra_06/limiter.py |  | prototype | draft | src/zephyr/shared/infra_06/limiter.py |  | prototype | draft |
| src/zephyr/shared/infra_06/lock.py |  | prototype | draft | src/zephyr/shared/infra_06/lock.py |  | prototype | draft |
| src/zephyr/shared/infra_06/observer.py |  | prototype | draft | src/zephyr/shared/infra_06/observer.py |  | prototype | draft |
| src/zephyr/shared/infra_06/outbox.py |  | prototype | draft | src/zephyr/shared/infra_06/outbox.py |  | prototype | draft |
| src/zephyr/shared/io/__init__.py |  | prototype | draft | src/zephyr/shared/io/__init__.py |  | prototype | draft |
| src/zephyr/shared/io/content_fingerprint.py |  | prototype | draft | src/zephyr/shared/io/content_fingerprint.py |  | prototype | draft |
| src/zephyr/shared/io/file_utils.py |  | prototype | draft | src/zephyr/shared/io/file_utils.py |  | prototype | draft |
| src/zephyr/shared/io/frontmatter_utils.py |  | prototype | draft | src/zephyr/shared/io/frontmatter_utils.py |  | prototype | draft |
| src/zephyr/shared/io/io_cache.py |  | prototype | draft | src/zephyr/shared/io/io_cache.py |  | prototype | draft |
| src/zephyr/shared/io/paths.py |  | prototype | draft | src/zephyr/shared/io/paths.py |  | prototype | draft |
| src/zephyr/shared/io/serialization.py |  | prototype | draft | src/zephyr/shared/io/serialization.py |  | prototype | draft |
| src/zephyr/shared/io/streaming_reader.py |  | prototype | draft | src/zephyr/shared/io/streaming_reader.py |  | prototype | draft |
| src/zephyr/shared/knowledge/ke_linker.py |  | prototype | draft | src/zephyr/shared/knowledge/ke_linker.py |  | prototype | draft |
| src/zephyr/shared/knowledge/ke_structurer.py |  | prototype | draft | src/zephyr/shared/knowledge/ke_structurer.py |  | prototype | draft |
| src/zephyr/shared/knowledge/kms_interface.py |  | prototype | draft | src/zephyr/shared/knowledge/kms_interface.py |  | prototype | draft |
| src/zephyr/shared/limiter.py |  | prototype | draft | src/zephyr/shared/limiter.py |  | prototype | draft |
| src/zephyr/shared/lock.py |  | prototype | draft | src/zephyr/shared/lock.py |  | prototype | draft |
| src/zephyr/shared/logging.py |  | prototype | draft | src/zephyr/shared/logging.py |  | prototype | draft |
| src/zephyr/shared/longevity_monitor.py |  | production | draft | src/zephyr/shared/longevity_monitor.py |  | production | draft |
| src/zephyr/shared/maintenance/autonomy_monitor.py |  | production | stable | src/zephyr/shared/maintenance/autonomy_monitor.py |  | production | stable |
| src/zephyr/shared/maintenance/dogfooding.py |  | prototype | draft | src/zephyr/shared/maintenance/dogfooding.py |  | prototype | draft |
| src/zephyr/shared/maintenance/handbook.py |  | prototype | draft | src/zephyr/shared/maintenance/handbook.py |  | prototype | draft |
| src/zephyr/shared/maintenance/zero_config.py |  | prototype | draft | src/zephyr/shared/maintenance/zero_config.py |  | prototype | draft |
| src/zephyr/shared/metrics.py |  | production | stable | src/zephyr/shared/metrics.py |  | production | stable |
| src/zephyr/shared/migration.py |  | prototype | draft | src/zephyr/shared/migration.py |  | prototype | draft |
| src/zephyr/shared/model_capacity_probe.py |  | production | draft | src/zephyr/shared/model_capacity_probe.py |  | production | draft |
| src/zephyr/shared/models.py |  | prototype | draft | src/zephyr/shared/models.py |  | prototype | draft |
| src/zephyr/shared/module_birth_registry.py |  | production | draft | src/zephyr/shared/module_birth_registry.py |  | production | draft |
| src/zephyr/shared/observability_02/health.py |  | production | stable | src/zephyr/shared/observability_02/health.py |  | production | stable |
| src/zephyr/shared/observability_02/health_discovery.py |  | production | stable | src/zephyr/shared/observability_02/health_discovery.py |  | production | stable |
| src/zephyr/shared/observability_02/logging.py |  | prototype | draft | src/zephyr/shared/observability_02/logging.py |  | prototype | draft |
| src/zephyr/shared/observability_02/metrics.py |  | production | stable | src/zephyr/shared/observability_02/metrics.py |  | production | stable |
| src/zephyr/shared/observability_02/token_utils.py |  | prototype | draft | src/zephyr/shared/observability_02/token_utils.py |  | prototype | draft |
| src/zephyr/shared/observability_02/tracing.py |  | prototype | draft | src/zephyr/shared/observability_02/tracing.py |  | prototype | draft |
| src/zephyr/shared/observer.py |  | prototype | draft | src/zephyr/shared/observer.py |  | prototype | draft |
| src/zephyr/shared/outbox.py |  | prototype | draft | src/zephyr/shared/outbox.py |  | prototype | draft |
| src/zephyr/shared/owner_trust_gauge.py |  | production | draft | src/zephyr/shared/owner_trust_gauge.py |  | production | draft |
| src/zephyr/shared/pagination.py |  | prototype | draft | src/zephyr/shared/pagination.py |  | prototype | draft |

> (仅显示前 200 个模块，共 290 个)

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

```mermaid
graph TD
    subgraph D_SHARED["D-SHARED shared_services"]
        D_SHARED_14_14_Knowledge_Injection_Paths["14条知识注入路径 14 Knowledge Injection Paths design"]
        D_SHARED_Event_Schema_Versioning_Schema["Event Schema Versioning 事件Schema版本管理 design"]
        D_SHARED_Weight_Centric_Interface["权重中心接口 Weight-Centric Interface design"]
        src_zephyr_shared_SHARED_QUICKREF_yml["src/zephyr/shared/SHARED-QUICKREF.yml production"]
        src_zephyr_shared_init_py["src/zephyr/shared/__init__.py production"]
        src_zephyr_shared_version_py["src/zephyr/shared/__version__.py prototype"]
        src_zephyr_shared_cross_layer_init_py["src/zephyr/shared/_cross_layer/__init__.py prototype"]
        src_zephyr_shared_cross_layer_ml_experiment_pipeline_py["src/zephyr/shared/_cross_layer/ml_experiment_pi... prototype"]
        src_zephyr_shared_state_machine_registry_yaml["src/zephyr/shared/_state_machine_registry.yaml production"]
        src_zephyr_shared_adaptation_execution_tuner_py["src/zephyr/shared/adaptation/execution_tuner.py prototype"]
        src_zephyr_shared_adaptation_prompt_version_manager_py["src/zephyr/shared/adaptation/prompt_version_man... prototype"]
        src_zephyr_shared_adaptive_sampler_py["src/zephyr/shared/adaptive_sampler.py production"]
        src_zephyr_shared_ai_audit_guard_py["src/zephyr/shared/ai_audit_guard.py production"]
        src_zephyr_shared_ai_understandability_constraint_py["src/zephyr/shared/ai_understandability_constrai... production"]
        src_zephyr_shared_alert_escalation_py["src/zephyr/shared/alert_escalation.py production"]
        src_zephyr_shared_alert_manager_py["src/zephyr/shared/alert_manager.py production"]
        src_zephyr_shared_alert_precision_tracker_py["src/zephyr/shared/alert_precision_tracker.py production"]
        src_zephyr_shared_api_init_py["src/zephyr/shared/api/__init__.py prototype"]
        src_zephyr_shared_api_api_client_py["src/zephyr/shared/api/api_client.py prototype"]
        src_zephyr_shared_api_api_index_py["src/zephyr/shared/api/api_index.py prototype"]
        src_zephyr_shared_api_dos_launcher_py["src/zephyr/shared/api/dos_launcher.py prototype"]
        src_zephyr_shared_api_shared_quickref_yaml["src/zephyr/shared/api/shared_quickref.yaml production"]
        src_zephyr_shared_api_client_py["src/zephyr/shared/api_client.py prototype"]
        src_zephyr_shared_api_index_py["src/zephyr/shared/api_index.py prototype"]
        src_zephyr_shared_blueprint_code_auditor_py["src/zephyr/shared/blueprint_code_auditor.py production"]
        src_zephyr_shared_blueprint_decomposer_py["src/zephyr/shared/blueprint_decomposer.py prototype"]
        src_zephyr_shared_blueprint_scorer_py["src/zephyr/shared/blueprint_scorer.py prototype"]
        src_zephyr_shared_budget_aware_prompt_py["src/zephyr/shared/budget_aware_prompt.py production"]
        src_zephyr_shared_cache_py["src/zephyr/shared/cache.py prototype"]
        src_zephyr_shared_capability_py["src/zephyr/shared/capability.py prototype"]
    end
    src_zephyr_shared_api_index_py -.->|import_depends| src_zephyr_shared_api_api_index_py
    src_zephyr_shared_blueprint_decomposer_py -.->|import_depends| src_zephyr_shared_init_py
    src_zephyr_shared_api_client_py -.->|import_depends| src_zephyr_shared_api_api_client_py
    src_zephyr_shared_blueprint_scorer_py -.->|config_depends| src_zephyr_shared_init_py
    src_zephyr_shared_adaptation_prompt_version_manager_py -.->|config_depends| src_zephyr_shared_adaptation_execution_tuner_py
    src_zephyr_shared_api_init_py -.->|config_depends| src_zephyr_shared_api_dos_launcher_py
    D_INTEGRATION["D-INTEGRATION production"]
    src_zephyr_shared_blueprint_decomposer_py -.->|import_depends| D_INTEGRATION
    src_zephyr_shared_blueprint_decomposer_py -.->|import_depends| D_INTEGRATION
    D_ML_TRAIN["D-ML_TRAIN prototype"]
    src_zephyr_shared_cross_layer_ml_experiment_pipeline_py -.->|import_depends| D_ML_TRAIN
    src_zephyr_shared_cross_layer_ml_experiment_pipeline_py -.->|import_depends| D_ML_TRAIN
    D_SIMULATION["D-SIMULATION prototype"]
    src_zephyr_shared_cross_layer_ml_experiment_pipeline_py -.->|import_depends| D_SIMULATION
    D_OPS["D-OPS prototype"]
    D_OPS -.->|import_depends| src_zephyr_shared_adaptive_sampler_py
    D_GOVERNANCE["D-GOVERNANCE prototype"]
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_adaptive_sampler_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_ai_understandability_constraint_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_alert_escalation_py
    D_INFRA_RUNTIME["D-INFRA_RUNTIME production"]
    D_INFRA_RUNTIME -->|import_depends| src_zephyr_shared_alert_manager_py
    D_OPS -.->|import_depends| src_zephyr_shared_alert_manager_py
    D_SECURITY["D-SECURITY production"]
    D_SECURITY -->|import_depends| src_zephyr_shared_alert_manager_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_alert_manager_py
    D_INFRA_RUNTIME -->|import_depends| src_zephyr_shared_alert_precision_tracker_py
    D_OPS -.->|import_depends| src_zephyr_shared_alert_precision_tracker_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_alert_precision_tracker_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_ai_audit_guard_py
    D_GOVERNANCE -->|import_depends| src_zephyr_shared_blueprint_code_auditor_py
    D_GOV_RULE["D-GOV_RULE production"]
    D_GOV_RULE -->|import_depends| src_zephyr_shared_blueprint_code_auditor_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_blueprint_code_auditor_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_SHARED_QUICKREF_yml,src_zephyr_shared_init_py,src_zephyr_shared_state_machine_registry_yaml,src_zephyr_shared_adaptive_sampler_py,src_zephyr_shared_ai_audit_guard_py,src_zephyr_shared_ai_understandability_constraint_py,src_zephyr_shared_alert_escalation_py,src_zephyr_shared_alert_manager_py,src_zephyr_shared_alert_precision_tracker_py,src_zephyr_shared_api_shared_quickref_yaml,src_zephyr_shared_blueprint_code_auditor_py,src_zephyr_shared_budget_aware_prompt_py production
    class D_SHARED_14_14_Knowledge_Injection_Paths,D_SHARED_Event_Schema_Versioning_Schema,D_SHARED_Weight_Centric_Interface,src_zephyr_shared_version_py,src_zephyr_shared_cross_layer_init_py,src_zephyr_shared_cross_layer_ml_experiment_pipeline_py,src_zephyr_shared_adaptation_execution_tuner_py,src_zephyr_shared_adaptation_prompt_version_manager_py,src_zephyr_shared_api_init_py,src_zephyr_shared_api_api_client_py,src_zephyr_shared_api_api_index_py,src_zephyr_shared_api_dos_launcher_py,src_zephyr_shared_api_client_py,src_zephyr_shared_api_index_py,src_zephyr_shared_blueprint_decomposer_py,src_zephyr_shared_blueprint_scorer_py,src_zephyr_shared_cache_py,src_zephyr_shared_capability_py design
    class D_INTEGRATION,D_INFRA_RUNTIME,D_SECURITY,D_GOV_RULE external_prod
    class D_ML_TRAIN,D_SIMULATION,D_OPS,D_GOVERNANCE external_design
```

> (依赖图最多显示前 30 个节点，共 290 个)

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-INTEGRATION | 9 | contract,import_depends | D-INTEGRATION | 9 | contract,import_depends |
| D-INFRA_RUNTIME | 7 | import_depends | D-INFRA_RUNTIME | 7 | import_depends |
| D-OPS | 6 | import_depends | D-OPS | 6 | import_depends |
| D-GOVERNANCE | 3 | import_depends | D-GOVERNANCE | 3 | import_depends |
| D-ML_TRAIN | 2 | import_depends | D-ML_TRAIN | 2 | import_depends |
| D-SIMULATION | 1 | import_depends | D-SIMULATION | 1 | import_depends |
| D-GOV_AUDIT | 1 | import_depends | D-GOV_AUDIT | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-GOVERNANCE | 221 | test_depends,import_depends,data,event,contract | D-GOVERNANCE | 221 | test_depends,import_depends,data,event,contract |
| D-INTEGRATION | 73 | import_depends,event,data,contract | D-INTEGRATION | 73 | import_depends,event,data,contract |
| D-INFRA_RUNTIME | 67 | import_depends,contract,event,data | D-INFRA_RUNTIME | 67 | import_depends,contract,event,data |
| D-TRADING | 43 | import_depends,contract | D-TRADING | 43 | import_depends,contract |
| D-GOV_AUDIT | 42 | import_depends,test_depends | D-GOV_AUDIT | 42 | import_depends,test_depends |
| D-OPS | 14 | import_depends,test_depends | D-OPS | 14 | import_depends,test_depends |
| D-SECURITY | 9 | import_depends,data,event,contract | D-SECURITY | 9 | import_depends,data,event,contract |
| D-GOV_RULE | 9 | import_depends | D-GOV_RULE | 9 | import_depends |
| D-AUTONOMY_CORE | 6 | import_depends | D-AUTONOMY_CORE | 6 | import_depends |
| D-KNOWLEDGE | 4 | contract,data,event | D-KNOWLEDGE | 4 | contract,data,event |
| D-DATA_ENG | 4 | contract,data,event | D-DATA_ENG | 4 | contract,data,event |
| D-ALT_DATA | 4 | contract,data,event | D-ALT_DATA | 4 | contract,data,event |
| D-MKT_DATA | 3 | event,data,contract | D-MKT_DATA | 3 | event,data,contract |
| D-DATA_GOV | 3 | data,contract,event | D-DATA_GOV | 3 | data,contract,event |
| D-PF_ALLOC | 2 | contract,import_depends | D-PF_ALLOC | 2 | contract,import_depends |
| D-ML_TRAIN | 2 | import_depends | D-ML_TRAIN | 2 | import_depends |
| D-SELL_DECISION | 1 | contract | D-SELL_DECISION | 1 | contract |
| D-RISK | 1 | import_depends | D-RISK | 1 | import_depends |
| D-POSITION | 1 | contract | D-POSITION | 1 | contract |
| D-ML_SERVE | 1 | contract | D-ML_SERVE | 1 | contract |
| D-INTELLIGENCE | 1 | import_depends | D-INTELLIGENCE | 1 | import_depends |
| D-INFRA_OPS | 1 | import_depends | D-INFRA_OPS | 1 | import_depends |
| D-FRONTEND | 1 | import_depends | D-FRONTEND | 1 | import_depends |
| D-FACTOR | 1 | import_depends | D-FACTOR | 1 | import_depends |
| D-EX_SOR | 1 | contract | D-EX_SOR | 1 | contract |
| D-CROSS_ASSET | 1 | import_depends | D-CROSS_ASSET | 1 | import_depends |
| D-BEHAVIORAL_AUDIT | 1 | import_depends | D-BEHAVIORAL_AUDIT | 1 | import_depends |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
