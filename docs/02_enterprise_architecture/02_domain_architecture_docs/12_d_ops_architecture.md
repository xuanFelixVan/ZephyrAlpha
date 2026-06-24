---
doc_type: domain_architecture_diagram
title: D-OPS 反馈循环架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 12_d_ops / 反馈循环 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示反馈循环（D-OPS）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 反馈循环（D-OPS）的模块分布。共 701 个模块 / 701 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (426 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   architecture_model/layers/system_telemetry.yaml  [production]  │
│   config/capacity/token_budget.yaml  [production]                │
│   docs/02_enterprise_architecture/target_architecture/archite... │
│   docs__03_modules___domain_infra_ops__system_telemetry__blue... │
│   scripts/governance/observability/__init__.py  [prototype]      │
│   scripts/governance/observability/gate_cache.py  [prototype]    │
│   src/zephyr/governance/budget_engine.py  [prototype]            │
│   src/zephyr/governance/budget_handler.py  [prototype]           │
│   src/zephyr/governance/budget_models.py  [prototype]            │
│   src/zephyr/governance/budget_profile_manager.py  [prototype]   │
│   src/zephyr/governance/budget_tracker.py  [prototype]           │
│   src/zephyr/governance/cost_budget.py  [prototype]              │
│   src/zephyr/governance/meta_observability.py  [prototype]       │
│   src/zephyr/governance/observability_dashboard.py  [prototype]  │
│   src/zephyr/governance/observability_governance/__init__.py ... │
│   src/zephyr/governance/observability_governance/benchmark_in... │
│   src/zephyr/governance/observability_governance/observabilit... │
│   src/zephyr/governance/observability_governance/performance_... │
│   ...还有 408 个模块 / 408 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (275 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   GAAT Governance-Aware Agent Telemetry 治理感知遥测  [design]   │
│   GAAT Governance-Aware Telemetry GAAT治理感知遥测  [design]     │
│   Observability Dashboard 可观测性仪表盘  [design]               │
│   Trusted Telemetry Plane 可信遥测平面  [design]                 │
│   AI Agent Chaos Experiment Designer AI Agent混沌实验设计器  ... │
│   AI Autonomous Operations Closed Loop AI自治运维闭环  [design]  │
│   AI Autonomous Ops Engine AI自治运维引擎  [design]              │
│   AI Inference Dependency Discovery AI推理依赖发现  [design]     │
│   API Rate Limit Dependency Propagator API速率限制依赖传播器 ... │
│   API Traffic Policy Mapper API流量策略映射器  [design]          │
│   Adaptive Scheduler 自适应调度器  [design]                      │
│   Alert Fatigue Management 通知疲劳管理  [design]                │
│   Alert Manager 告警管理  [design]                               │
│   Anomaly Detection 异常检测  [design]                           │
│   Anomaly Detector 异常检测器  [design]                          │
│   Anomaly Propagation GNN Predictor 异常传播GNN预测器  [design]  │
│   Anomaly Propagation Tracker 异常传播追踪器  [design]           │
│   Application Layer Dependency Supplementer 应用层依赖补充器 ... │
│   ...还有 257 个模块 / 257 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 701 个模块 / 701 modules）。

### L1 基础层 / Foundation Layer (426 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | architecture_model/layers/system_telemetry.yaml | architecture_model/layers/system_tele... | production | orphan |
| 2 | config/capacity/token_budget.yaml | config/capacity/token_budget.yaml | production | orphan |
| 3 | docs/02_enterprise_architecture/target_architecture/archi... | docs/02_enterprise_architecture/targe... | production | orphan |
| 4 | docs/03_modules/_domain_infra_ops/system_telemetry/bluepr... | docs__03_modules___domain_infra_ops__... | design | design_only |
| 5 | scripts/governance/observability/__init__.py | scripts/governance/observability/__in... | prototype | draft |
| 6 | scripts/governance/observability/gate_cache.py | scripts/governance/observability/gate... | prototype | draft |
| 7 | src/zephyr/governance/budget_engine.py | src/zephyr/governance/budget_engine.py | prototype | draft |
| 8 | src/zephyr/governance/budget_handler.py | src/zephyr/governance/budget_handler.py | prototype | draft |
| 9 | src/zephyr/governance/budget_models.py | src/zephyr/governance/budget_models.py | prototype | draft |
| 10 | src/zephyr/governance/budget_profile_manager.py | src/zephyr/governance/budget_profile_... | prototype | draft |
| 11 | src/zephyr/governance/budget_tracker.py | src/zephyr/governance/budget_tracker.py | prototype | draft |
| 12 | src/zephyr/governance/cost_budget.py | src/zephyr/governance/cost_budget.py | prototype | draft |
| 13 | src/zephyr/governance/meta_observability.py | src/zephyr/governance/meta_observabil... | prototype | draft |
| 14 | src/zephyr/governance/observability_dashboard.py | src/zephyr/governance/observability_d... | prototype | draft |
| 15 | src/zephyr/governance/observability_governance/__init__.py | src/zephyr/governance/observability_g... | prototype | draft |
| 16 | src/zephyr/governance/observability_governance/benchmark_... | src/zephyr/governance/observability_g... | prototype | draft |
| 17 | src/zephyr/governance/observability_governance/observabil... | src/zephyr/governance/observability_g... | production | draft |
| 18 | src/zephyr/governance/observability_governance/performanc... | src/zephyr/governance/observability_g... | prototype | draft |
| 19 | src/zephyr/governance/observability_governance/provenance... | src/zephyr/governance/observability_g... | prototype | draft |
| 20 | src/zephyr/governance/token_budget.py | src/zephyr/governance/token_budget.py | prototype | draft |
| 21 | src/zephyr/ops/__init__.py | src/zephyr/ops/__init__.py | production | draft |
| 22 | src/zephyr/ops/__init___from_obs.py | src/zephyr/ops/__init___from_obs.py | prototype | draft |
| 23 | src/zephyr/ops/_budget_telemetry_bridge.py | src/zephyr/ops/_budget_telemetry_brid... | prototype | draft |
| 24 | src/zephyr/ops/_circuit_breaker.py | src/zephyr/ops/_circuit_breaker.py | prototype | draft |
| 25 | src/zephyr/ops/_extensions/__init__.py | src/zephyr/ops/_extensions/__init__.py | scaffold_placeholder | orphan |
| 26 | src/zephyr/ops/_gen_inherited.py | src/zephyr/ops/_gen_inherited.py | prototype | draft |
| 27 | src/zephyr/ops/_trace_bridge.py | src/zephyr/ops/_trace_bridge.py | prototype | draft |
| 28 | src/zephyr/ops/actors/__init__.py | src/zephyr/ops/actors/__init__.py | prototype | draft |
| 29 | src/zephyr/ops/actors/action_selector.py | src/zephyr/ops/actors/action_selector.py | prototype | draft |
| 30 | src/zephyr/ops/actors/agent_lifecycle.py | src/zephyr/ops/actors/agent_lifecycle.py | prototype | draft |
| 31 | src/zephyr/ops/actors/alert_router.py | src/zephyr/ops/actors/alert_router.py | prototype | draft |
| 32 | src/zephyr/ops/actors/api_version_contract.py | src/zephyr/ops/actors/api_version_con... | prototype | draft |
| 33 | src/zephyr/ops/actors/global_action_scheduler.py | src/zephyr/ops/actors/global_action_s... | prototype | draft |
| 34 | src/zephyr/ops/actors/incident_priority_triage_automator.py | src/zephyr/ops/actors/incident_priori... | prototype | draft |
| 35 | src/zephyr/ops/actors/intent_driven_ops.py | src/zephyr/ops/actors/intent_driven_o... | prototype | draft |
| 36 | src/zephyr/ops/actors/multi_agent_orchestrator.py | src/zephyr/ops/actors/multi_agent_orc... | prototype | draft |
| 37 | src/zephyr/ops/actors/notification_personalizer.py | src/zephyr/ops/actors/notification_pe... | prototype | draft |
| 38 | src/zephyr/ops/actors/owner_absence_escalation.py | src/zephyr/ops/actors/owner_absence_e... | prototype | draft |
| 39 | src/zephyr/ops/actors/saga_compensator.py | src/zephyr/ops/actors/saga_compensato... | prototype | draft |
| 40 | src/zephyr/ops/actors/secondary_alert_channel.py | src/zephyr/ops/actors/secondary_alert... | prototype | draft |
| 41 | src/zephyr/ops/ai_behavior/__init__.py | src/zephyr/ops/ai_behavior/__init__.py | prototype | draft |
| 42 | src/zephyr/ops/ai_behavior/event_sink.py | src/zephyr/ops/ai_behavior/event_sink.py | prototype | draft |
| 43 | src/zephyr/ops/alert_dispatcher.py | src/zephyr/ops/alert_dispatcher.py | prototype | draft |
| 44 | src/zephyr/ops/alerts/__init__.py | src/zephyr/ops/alerts/__init__.py | prototype | draft |
| 45 | src/zephyr/ops/analytics_base.py | src/zephyr/ops/analytics_base.py | prototype | draft |
| 46 | src/zephyr/ops/api/__init__.py | src/zephyr/ops/api/__init__.py | scaffold_placeholder | orphan |
| 47 | src/zephyr/ops/archive/__init__.py | src/zephyr/ops/archive/__init__.py | prototype | draft |
| 48 | src/zephyr/ops/archive/cold_stub.py | src/zephyr/ops/archive/cold_stub.py | prototype | draft |
| 49 | src/zephyr/ops/auto_bootstrap.py | src/zephyr/ops/auto_bootstrap.py | prototype | draft |
| 50 | src/zephyr/ops/auto_evolution.py | src/zephyr/ops/auto_evolution.py | prototype | draft |
| 51 | src/zephyr/ops/backpressure_bridge.py | src/zephyr/ops/backpressure_bridge.py | prototype | draft |
| 52 | src/zephyr/ops/circuit_breaker.py | src/zephyr/ops/circuit_breaker.py | prototype | draft |
| 53 | src/zephyr/ops/circuit_breaker_repo.py | src/zephyr/ops/circuit_breaker_repo.py | prototype | draft |
| 54 | src/zephyr/ops/circuit_breaker_types.py | src/zephyr/ops/circuit_breaker_types.py | prototype | draft |
| 55 | src/zephyr/ops/collectors/__init__.py | src/zephyr/ops/collectors/__init__.py | prototype | draft |
| 56 | src/zephyr/ops/collectors/calendar_adapter.py | src/zephyr/ops/collectors/calendar_ad... | prototype | draft |
| 57 | src/zephyr/ops/collectors/config_timeline.py | src/zephyr/ops/collectors/config_time... | prototype | draft |
| 58 | src/zephyr/ops/collectors/data_quality_validator.py | src/zephyr/ops/collectors/data_qualit... | prototype | draft |
| 59 | src/zephyr/ops/collectors/feedback_collector.py | src/zephyr/ops/collectors/feedback_co... | prototype | draft |
| 60 | src/zephyr/ops/collectors/financial_stratification.py | src/zephyr/ops/collectors/financial_s... | prototype | draft |
| 61 | src/zephyr/ops/collectors/kb_provenance.py | src/zephyr/ops/collectors/kb_provenan... | prototype | draft |
| 62 | src/zephyr/ops/collectors/knowledge_capture.py | src/zephyr/ops/collectors/knowledge_c... | prototype | draft |
| 63 | src/zephyr/ops/collectors/knowledge_freshness.py | src/zephyr/ops/collectors/knowledge_f... | prototype | draft |
| 64 | src/zephyr/ops/collectors/knowledge_injection.py | src/zephyr/ops/collectors/knowledge_i... | prototype | draft |
| 65 | src/zephyr/ops/collectors/knowledge_packaging.py | src/zephyr/ops/collectors/knowledge_p... | prototype | draft |
| 66 | src/zephyr/ops/collectors/known_unknown_registry.py | src/zephyr/ops/collectors/known_unkno... | prototype | draft |
| 67 | src/zephyr/ops/collectors/llm_cost_accounting.py | src/zephyr/ops/collectors/llm_cost_ac... | prototype | draft |
| 68 | src/zephyr/ops/collectors/market_calendar.py | src/zephyr/ops/collectors/market_cale... | prototype | draft |
| 69 | src/zephyr/ops/collectors/market_event_integrator.py | src/zephyr/ops/collectors/market_even... | prototype | draft |
| 70 | src/zephyr/ops/collectors/metrics_collector.py | src/zephyr/ops/collectors/metrics_col... | prototype | draft |
| 71 | src/zephyr/ops/collectors/notification_feedback.py | src/zephyr/ops/collectors/notificatio... | prototype | draft |
| 72 | src/zephyr/ops/collectors/schema_evolution.py | src/zephyr/ops/collectors/schema_evol... | prototype | draft |
| 73 | src/zephyr/ops/collectors/schema_migration.py | src/zephyr/ops/collectors/schema_migr... | prototype | draft |
| 74 | src/zephyr/ops/collectors/temporal_event_store.py | src/zephyr/ops/collectors/temporal_ev... | prototype | draft |
| 75 | src/zephyr/ops/collectors/token_finops.py | src/zephyr/ops/collectors/token_finop... | prototype | draft |
| 76 | src/zephyr/ops/config.py | src/zephyr/ops/config.py | prototype | draft |
| 77 | src/zephyr/ops/contract_metrics.py | src/zephyr/ops/contract_metrics.py | prototype | draft |
| 78 | src/zephyr/ops/core/__init__.py | src/zephyr/ops/core/__init__.py | scaffold_placeholder | orphan |
| 79 | src/zephyr/ops/db_bridge.py | src/zephyr/ops/db_bridge.py | prototype | draft |
| 80 | src/zephyr/ops/db_writer.py | src/zephyr/ops/db_writer.py | prototype | draft |
| 81 | src/zephyr/ops/decision_engine.py | src/zephyr/ops/decision_engine.py | prototype | draft |
| 82 | src/zephyr/ops/detectors/__init__.py | src/zephyr/ops/detectors/__init__.py | prototype | draft |
| 83 | src/zephyr/ops/detectors/_anomaly.py | src/zephyr/ops/detectors/_anomaly.py | prototype | draft |
| 84 | src/zephyr/ops/detectors/_correlation.py | src/zephyr/ops/detectors/_correlation.py | prototype | draft |
| 85 | src/zephyr/ops/detectors/_drift.py | src/zephyr/ops/detectors/_drift.py | prototype | draft |
| 86 | src/zephyr/ops/detectors/_guard.py | src/zephyr/ops/detectors/_guard.py | prototype | draft |
| 87 | src/zephyr/ops/detectors/_reliability.py | src/zephyr/ops/detectors/_reliability.py | prototype | draft |
| 88 | src/zephyr/ops/detectors/action_efficacy_decay_detector.py | src/zephyr/ops/detectors/action_effic... | prototype | draft |
| 89 | src/zephyr/ops/detectors/action_interaction_detector.py | src/zephyr/ops/detectors/action_inter... | prototype | draft |
| 90 | src/zephyr/ops/detectors/action_side_effect_cumulative_de... | src/zephyr/ops/detectors/action_side_... | prototype | draft |
| 91 | src/zephyr/ops/detectors/agent_trajectory_anomaly_detecto... | src/zephyr/ops/detectors/agent_trajec... | prototype | draft |
| 92 | src/zephyr/ops/detectors/alert_desensitization_curve.py | src/zephyr/ops/detectors/alert_desens... | prototype | draft |
| 93 | src/zephyr/ops/detectors/anomaly_clustering.py | src/zephyr/ops/detectors/anomaly_clus... | prototype | draft |
| 94 | src/zephyr/ops/detectors/anomaly_detector.py | src/zephyr/ops/detectors/anomaly_dete... | prototype | draft |
| 95 | src/zephyr/ops/detectors/autoscale_remediation.py | src/zephyr/ops/detectors/autoscale_re... | prototype | draft |
| 96 | src/zephyr/ops/detectors/blast_radius.py | src/zephyr/ops/detectors/blast_radius.py | prototype | draft |
| 97 | src/zephyr/ops/detectors/blast_radius_budget.py | src/zephyr/ops/detectors/blast_radius... | prototype | draft |
| 98 | src/zephyr/ops/detectors/capacity_forecast.py | src/zephyr/ops/detectors/capacity_for... | prototype | draft |
| 99 | src/zephyr/ops/detectors/chaos_engineering.py | src/zephyr/ops/detectors/chaos_engine... | prototype | draft |
| 100 | src/zephyr/ops/detectors/concept_drift.py | src/zephyr/ops/detectors/concept_drif... | prototype | draft |
| 101 | src/zephyr/ops/detectors/config_drift.py | src/zephyr/ops/detectors/config_drift.py | prototype | draft |
| 102 | src/zephyr/ops/detectors/context_window_contamination_det... | src/zephyr/ops/detectors/context_wind... | prototype | draft |
| 103 | src/zephyr/ops/detectors/cross_signal_validator.py | src/zephyr/ops/detectors/cross_signal... | prototype | draft |
| 104 | src/zephyr/ops/detectors/cross_system_correlator.py | src/zephyr/ops/detectors/cross_system... | prototype | draft |
| 105 | src/zephyr/ops/detectors/decision_provenance.py | src/zephyr/ops/detectors/decision_pro... | prototype | draft |
| 106 | src/zephyr/ops/detectors/dependency_freshness_monitor.py | src/zephyr/ops/detectors/dependency_f... | prototype | draft |
| 107 | src/zephyr/ops/detectors/diminishing_returns_detector.py | src/zephyr/ops/detectors/diminishing_... | prototype | draft |
| 108 | src/zephyr/ops/detectors/ebpf_monitor.py | src/zephyr/ops/detectors/ebpf_monitor.py | prototype | draft |
| 109 | src/zephyr/ops/detectors/emergent_behavior_detector.py | src/zephyr/ops/detectors/emergent_beh... | prototype | draft |
| 110 | src/zephyr/ops/detectors/ensemble_detector.py | src/zephyr/ops/detectors/ensemble_det... | prototype | draft |
| 111 | src/zephyr/ops/detectors/ensemble_drift.py | src/zephyr/ops/detectors/ensemble_dri... | prototype | draft |
| 112 | src/zephyr/ops/detectors/external_health.py | src/zephyr/ops/detectors/external_hea... | prototype | draft |
| 113 | src/zephyr/ops/detectors/external_validation_checkpoint.py | src/zephyr/ops/detectors/external_val... | prototype | draft |
| 114 | src/zephyr/ops/detectors/flag_lifecycle.py | src/zephyr/ops/detectors/flag_lifecyc... | prototype | draft |
| 115 | src/zephyr/ops/detectors/flapping_detector.py | src/zephyr/ops/detectors/flapping_det... | prototype | draft |
| 116 | src/zephyr/ops/detectors/fle_performance_regression_detec... | src/zephyr/ops/detectors/fle_performa... | prototype | draft |
| 117 | src/zephyr/ops/detectors/gradual_poisoning_detector.py | src/zephyr/ops/detectors/gradual_pois... | prototype | draft |
| 118 | src/zephyr/ops/detectors/guard_cascade_detector.py | src/zephyr/ops/detectors/guard_cascad... | prototype | draft |
| 119 | src/zephyr/ops/detectors/guard_oscillation_detector.py | src/zephyr/ops/detectors/guard_oscill... | prototype | draft |
| 120 | src/zephyr/ops/detectors/heisenbug_detector.py | src/zephyr/ops/detectors/heisenbug_de... | prototype | draft |
| 121 | src/zephyr/ops/detectors/infinite_loop_detector.py | src/zephyr/ops/detectors/infinite_loo... | prototype | draft |
| 122 | src/zephyr/ops/detectors/intermittent_failure_pattern.py | src/zephyr/ops/detectors/intermittent... | prototype | draft |
| 123 | src/zephyr/ops/detectors/log_anomaly.py | src/zephyr/ops/detectors/log_anomaly.py | prototype | draft |
| 124 | src/zephyr/ops/detectors/maintenance_coordinator.py | src/zephyr/ops/detectors/maintenance_... | prototype | draft |
| 125 | src/zephyr/ops/detectors/metric_cardinality_guard.py | src/zephyr/ops/detectors/metric_cardi... | prototype | draft |
| 126 | src/zephyr/ops/detectors/multi_signal_correlator.py | src/zephyr/ops/detectors/multi_signal... | prototype | draft |
| 127 | src/zephyr/ops/detectors/openfeature.py | src/zephyr/ops/detectors/openfeature.py | prototype | draft |
| 128 | src/zephyr/ops/detectors/otel_adapter.py | src/zephyr/ops/detectors/otel_adapter.py | prototype | draft |
| 129 | src/zephyr/ops/detectors/placebo_action_detector.py | src/zephyr/ops/detectors/placebo_acti... | prototype | draft |
| 130 | src/zephyr/ops/detectors/positive_feedback_defense.py | src/zephyr/ops/detectors/positive_fee... | prototype | draft |
| 131 | src/zephyr/ops/detectors/recursive_diagnosis_trust_evalua... | src/zephyr/ops/detectors/recursive_di... | prototype | draft |
| 132 | src/zephyr/ops/detectors/regime_detector.py | src/zephyr/ops/detectors/regime_detec... | prototype | draft |
| 133 | src/zephyr/ops/detectors/regulatory_audit.py | src/zephyr/ops/detectors/regulatory_a... | prototype | draft |
| 134 | src/zephyr/ops/detectors/resolution_tracker.py | src/zephyr/ops/detectors/resolution_t... | prototype | draft |
| 135 | src/zephyr/ops/detectors/rumor_noise_filter.py | src/zephyr/ops/detectors/rumor_noise_... | prototype | draft |
| 136 | src/zephyr/ops/detectors/runbook_executor.py | src/zephyr/ops/detectors/runbook_exec... | prototype | draft |
| 137 | src/zephyr/ops/detectors/self_audit.py | src/zephyr/ops/detectors/self_audit.py | prototype | draft |
| 138 | src/zephyr/ops/detectors/self_diagnosis_data_leak_detecto... | src/zephyr/ops/detectors/self_diagnos... | prototype | draft |
| 139 | src/zephyr/ops/detectors/self_ha.py | src/zephyr/ops/detectors/self_ha.py | prototype | draft |
| 140 | src/zephyr/ops/detectors/silent_corruption_detector.py | src/zephyr/ops/detectors/silent_corru... | prototype | draft |
| 141 | src/zephyr/ops/detectors/synthetic_anomaly_generator.py | src/zephyr/ops/detectors/synthetic_an... | prototype | draft |
| 142 | src/zephyr/ops/detectors/temporal_coherence_of_self_model.py | src/zephyr/ops/detectors/temporal_coh... | prototype | draft |
| 143 | src/zephyr/ops/detectors/temporal_pattern.py | src/zephyr/ops/detectors/temporal_pat... | prototype | draft |
| 144 | src/zephyr/ops/detectors/trace_causal_bridge.py | src/zephyr/ops/detectors/trace_causal... | prototype | draft |
| 145 | src/zephyr/ops/detectors/traffic_replay_validator.py | src/zephyr/ops/detectors/traffic_repl... | prototype | draft |
| 146 | src/zephyr/ops/detectors/trend_cycle_separator.py | src/zephyr/ops/detectors/trend_cycle_... | prototype | draft |
| 147 | src/zephyr/ops/detectors/version_migrator.py | src/zephyr/ops/detectors/version_migr... | prototype | draft |
| 148 | src/zephyr/ops/diagnosers/__init__.py | src/zephyr/ops/diagnosers/__init__.py | prototype | draft |
| 149 | src/zephyr/ops/diagnosers/_cognitive.py | src/zephyr/ops/diagnosers/_cognitive.py | prototype | draft |
| 150 | src/zephyr/ops/diagnosers/_diagnosis.py | src/zephyr/ops/diagnosers/_diagnosis.py | prototype | draft |
| 151 | src/zephyr/ops/diagnosers/_health.py | src/zephyr/ops/diagnosers/_health.py | prototype | draft |
| 152 | src/zephyr/ops/diagnosers/_reliability.py | src/zephyr/ops/diagnosers/_reliabilit... | prototype | draft |
| 153 | src/zephyr/ops/diagnosers/action_composition_health_monit... | src/zephyr/ops/diagnosers/action_comp... | prototype | draft |
| 154 | src/zephyr/ops/diagnosers/adaptive_param_tuning.py | src/zephyr/ops/diagnosers/adaptive_pa... | prototype | draft |
| 155 | src/zephyr/ops/diagnosers/amplification_guard.py | src/zephyr/ops/diagnosers/amplificati... | prototype | draft |
| 156 | src/zephyr/ops/diagnosers/api_dependency_metrics.py | src/zephyr/ops/diagnosers/api_depende... | prototype | draft |
| 157 | src/zephyr/ops/diagnosers/auto_diagnosis.py | src/zephyr/ops/diagnosers/auto_diagno... | prototype | draft |
| 158 | src/zephyr/ops/diagnosers/burn_rate_alerter.py | src/zephyr/ops/diagnosers/burn_rate_a... | prototype | draft |
| 159 | src/zephyr/ops/diagnosers/burnout_alarm.py | src/zephyr/ops/diagnosers/burnout_ala... | prototype | draft |
| 160 | src/zephyr/ops/diagnosers/capacity_aware_repair.py | src/zephyr/ops/diagnosers/capacity_aw... | prototype | draft |
| 161 | src/zephyr/ops/diagnosers/causal_inference_engine.py | src/zephyr/ops/diagnosers/causal_infe... | prototype | draft |
| 162 | src/zephyr/ops/diagnosers/cognitive_load.py | src/zephyr/ops/diagnosers/cognitive_l... | prototype | draft |
| 163 | src/zephyr/ops/diagnosers/cognitive_load_budget.py | src/zephyr/ops/diagnosers/cognitive_l... | prototype | draft |
| 164 | src/zephyr/ops/diagnosers/cold_start_conservative_mode.py | src/zephyr/ops/diagnosers/cold_start_... | prototype | draft |
| 165 | src/zephyr/ops/diagnosers/collaborative_learning.py | src/zephyr/ops/diagnosers/collaborati... | prototype | draft |
| 166 | src/zephyr/ops/diagnosers/confidence_decomposer.py | src/zephyr/ops/diagnosers/confidence_... | prototype | draft |
| 167 | src/zephyr/ops/diagnosers/context_truncation.py | src/zephyr/ops/diagnosers/context_tru... | prototype | draft |
| 168 | src/zephyr/ops/diagnosers/context_window_pressure_manager.py | src/zephyr/ops/diagnosers/context_win... | prototype | draft |
| 169 | src/zephyr/ops/diagnosers/counterfactual.py | src/zephyr/ops/diagnosers/counterfact... | prototype | draft |
| 170 | src/zephyr/ops/diagnosers/cross_guard_conflict_detector.py | src/zephyr/ops/diagnosers/cross_guard... | prototype | draft |
| 171 | src/zephyr/ops/diagnosers/cross_session_consistency_valid... | src/zephyr/ops/diagnosers/cross_sessi... | prototype | draft |
| 172 | src/zephyr/ops/diagnosers/data_volume_growth_monitor.py | src/zephyr/ops/diagnosers/data_volume... | prototype | draft |
| 173 | src/zephyr/ops/diagnosers/diagnosis_engine.py | src/zephyr/ops/diagnosers/diagnosis_e... | prototype | draft |
| 174 | src/zephyr/ops/diagnosers/diagnosis_kpi.py | src/zephyr/ops/diagnosers/diagnosis_k... | prototype | draft |
| 175 | src/zephyr/ops/diagnosers/dr_resilience_metrics.py | src/zephyr/ops/diagnosers/dr_resilien... | prototype | draft |
| 176 | src/zephyr/ops/diagnosers/e2e_integration_health.py | src/zephyr/ops/diagnosers/e2e_integra... | prototype | draft |
| 177 | src/zephyr/ops/diagnosers/feedback_delay_compensator.py | src/zephyr/ops/diagnosers/feedback_de... | prototype | draft |
| 178 | src/zephyr/ops/diagnosers/fle_dogfood_monitor.py | src/zephyr/ops/diagnosers/fle_dogfood... | prototype | draft |
| 179 | src/zephyr/ops/diagnosers/fle_self_slo_metrics.py | src/zephyr/ops/diagnosers/fle_self_sl... | prototype | draft |
| 180 | src/zephyr/ops/diagnosers/gamification.py | src/zephyr/ops/diagnosers/gamificatio... | prototype | draft |
| 181 | src/zephyr/ops/diagnosers/global_health_map.py | src/zephyr/ops/diagnosers/global_heal... | prototype | draft |
| 182 | src/zephyr/ops/diagnosers/guard_interaction_topology_mapp... | src/zephyr/ops/diagnosers/guard_inter... | prototype | draft |
| 183 | src/zephyr/ops/diagnosers/guard_self_consistency_auditor.py | src/zephyr/ops/diagnosers/guard_self_... | prototype | draft |
| 184 | src/zephyr/ops/diagnosers/human_anomaly_flood_detector.py | src/zephyr/ops/diagnosers/human_anoma... | prototype | draft |
| 185 | src/zephyr/ops/diagnosers/impact_predictor.py | src/zephyr/ops/diagnosers/impact_pred... | prototype | draft |
| 186 | src/zephyr/ops/diagnosers/incident_knowledge_injector.py | src/zephyr/ops/diagnosers/incident_kn... | prototype | draft |
| 187 | src/zephyr/ops/diagnosers/interactive_diagnosis.py | src/zephyr/ops/diagnosers/interactive... | prototype | draft |
| 188 | src/zephyr/ops/diagnosers/knowledge_bus_factor_monitor.py | src/zephyr/ops/diagnosers/knowledge_b... | prototype | draft |
| 189 | src/zephyr/ops/diagnosers/knowledge_market.py | src/zephyr/ops/diagnosers/knowledge_m... | prototype | draft |
| 190 | src/zephyr/ops/diagnosers/latency_slo.py | src/zephyr/ops/diagnosers/latency_slo.py | prototype | draft |
| 191 | src/zephyr/ops/diagnosers/llm_provider_integrity.py | src/zephyr/ops/diagnosers/llm_provide... | prototype | draft |
| 192 | src/zephyr/ops/diagnosers/llm_quality_regression.py | src/zephyr/ops/diagnosers/llm_quality... | prototype | draft |
| 193 | src/zephyr/ops/diagnosers/memory_self_check.py | src/zephyr/ops/diagnosers/memory_self... | prototype | draft |
| 194 | src/zephyr/ops/diagnosers/meta_guard_latency_budget.py | src/zephyr/ops/diagnosers/meta_guard_... | prototype | draft |
| 195 | src/zephyr/ops/diagnosers/model_health.py | src/zephyr/ops/diagnosers/model_healt... | prototype | draft |
| 196 | src/zephyr/ops/diagnosers/model_rotation.py | src/zephyr/ops/diagnosers/model_rotat... | prototype | draft |
| 197 | src/zephyr/ops/diagnosers/model_rotation_v2.py | src/zephyr/ops/diagnosers/model_rotat... | prototype | draft |
| 198 | src/zephyr/ops/diagnosers/model_version_semantic_drift.py | src/zephyr/ops/diagnosers/model_versi... | prototype | draft |
| 199 | src/zephyr/ops/diagnosers/mtti_tracker.py | src/zephyr/ops/diagnosers/mtti_tracke... | prototype | draft |
| 200 | src/zephyr/ops/diagnosers/nonstationary_effectiveness.py | src/zephyr/ops/diagnosers/nonstationa... | prototype | draft |

> (仅显示前 200 个模块，共 426 个)

### 未分类 / Unclassified (275 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-GOVERNANCE/GAAT Governance-Aware Agent Telemetry 治理感... | GAAT Governance-Aware Agent Telemetry... | design | design_only |
| 2 | D-GOVERNANCE/GAAT Governance-Aware Telemetry GAAT治理感知... | GAAT Governance-Aware Telemetry GAAT... | design | design_only |
| 3 | D-GOVERNANCE/Observability Dashboard 可观测性仪表盘 | Observability Dashboard 可观测性仪表盘 | design | design_only |
| 4 | D-GOVERNANCE/Trusted Telemetry Plane 可信遥测平面 | Trusted Telemetry Plane 可信遥测平面 | design | design_only |
| 5 | D-OPS/AI Agent Chaos Experiment Designer AI Agent混沌实验... | AI Agent Chaos Experiment Designer AI... | design | design_only |
| 6 | D-OPS/AI Autonomous Operations Closed Loop AI自治运维闭环 | AI Autonomous Operations Closed Loop ... | design | design_only |
| 7 | D-OPS/AI Autonomous Ops Engine AI自治运维引擎 | AI Autonomous Ops Engine AI自治运维引擎 | design | design_only |
| 8 | D-OPS/AI Inference Dependency Discovery AI推理依赖发现 | AI Inference Dependency Discovery AI... | design | design_only |
| 9 | D-OPS/API Rate Limit Dependency Propagator API速率限制依... | API Rate Limit Dependency Propagator ... | design | design_only |
| 10 | D-OPS/API Traffic Policy Mapper API流量策略映射器 | API Traffic Policy Mapper API流量策略... | design | design_only |
| 11 | D-OPS/Adaptive Scheduler 自适应调度器 | Adaptive Scheduler 自适应调度器 | design | design_only |
| 12 | D-OPS/Alert Fatigue Management 通知疲劳管理 | Alert Fatigue Management 通知疲劳管理 | design | design_only |
| 13 | D-OPS/Alert Manager 告警管理 | Alert Manager 告警管理 | design | design_only |
| 14 | D-OPS/Anomaly Detection 异常检测 | Anomaly Detection 异常检测 | design | design_only |
| 15 | D-OPS/Anomaly Detector 异常检测器 | Anomaly Detector 异常检测器 | design | design_only |
| 16 | D-OPS/Anomaly Propagation GNN Predictor 异常传播GNN预测器 | Anomaly Propagation GNN Predictor 异... | design | design_only |
| 17 | D-OPS/Anomaly Propagation Tracker 异常传播追踪器 | Anomaly Propagation Tracker 异常传播... | design | design_only |
| 18 | D-OPS/Application Layer Dependency Supplementer 应用层依... | Application Layer Dependency Suppleme... | design | design_only |
| 19 | D-OPS/Asset Inventory 资产盘点 | Asset Inventory 资产盘点 | design | design_only |
| 20 | D-OPS/Auto Degradation Executor 自动降级执行器 | Auto Degradation Executor 自动降级执行器 | design | design_only |
| 21 | D-OPS/Auto Dependency Replacer 自动依赖替换器 | Auto Dependency Replacer 自动依赖替换器 | design | design_only |
| 22 | D-OPS/Auto Repair Executor 自动修复执行器 | Auto Repair Executor 自动修复执行器 | design | design_only |
| 23 | D-OPS/Auto Rollback Executor 自动回滚执行器 | Auto Rollback Executor 自动回滚执行器 | design | design_only |
| 24 | D-OPS/Auto Rollback Strategy Selector 自动回滚策略选择器 | Auto Rollback Strategy Selector 自动... | design | design_only |
| 25 | D-OPS/Backup Recovery Manager 备份与恢复管理器 | Backup Recovery Manager 备份与恢复管理器 | design | design_only |
| 26 | D-OPS/Batch Simulator 批量仿真器 | Batch Simulator 批量仿真器 | design | design_only |
| 27 | D-OPS/Bidirectional Synchronizer 双向同步器 | Bidirectional Synchronizer 双向同步器 | design | design_only |
| 28 | D-OPS/Blast Radius Calculator 爆炸半径计算器 | Blast Radius Calculator 爆炸半径计算器 | design | design_only |
| 29 | D-OPS/Blast Radius Predictor 爆炸半径预测器 | Blast Radius Predictor 爆炸半径预测器 | design | design_only |
| 30 | D-OPS/Bulkhead Modeler 舱壁建模器 | Bulkhead Modeler 舱壁建模器 | design | design_only |
| 31 | D-OPS/Bus Factor Defense 巴士因子防御 | Bus Factor Defense 巴士因子防御 | design | design_only |
| 32 | D-OPS/Capacity Assurance 容量保障 | Capacity Assurance 容量保障 | design | design_only |
| 33 | D-OPS/Capacity Planning Resource Prediction 容量规划与资... | Capacity Planning Resource Prediction... | design | design_only |
| 34 | D-OPS/Carbon Budget Tracker 碳预算追踪器 | Carbon Budget Tracker 碳预算追踪器 | design | design_only |
| 35 | D-OPS/Carbon Budget Tracking Enhancer 碳预算追踪增强器 | Carbon Budget Tracking Enhancer 碳预... | design | design_only |
| 36 | D-OPS/Carbon Intensity API Integrator 碳强度API集成器 | Carbon Intensity API Integrator 碳强... | design | design_only |
| 37 | D-OPS/Carbon-Aware SDK v2 Integrator Carbon-Aware SDK v2... | Carbon-Aware SDK v2 Integrator Carbon... | design | design_only |
| 38 | D-OPS/Cascade Fault Generator 级联故障生成器 | Cascade Fault Generator 级联故障生成器 | design | design_only |
| 39 | D-OPS/Causal Inference Correlator 因果推断关联器 | Causal Inference Correlator 因果推断... | design | design_only |
| 40 | D-OPS/Change Management Engine 变更管理引擎 | Change Management Engine 变更管理引擎 | design | design_only |
| 41 | D-OPS/Change Management 变更管理 | Change Management 变更管理 | design | design_only |
| 42 | D-OPS/Change Manager 变更管理器 | Change Manager 变更管理器 | design | design_only |
| 43 | D-OPS/Change Notification Enhancer 变更通知增强器 | Change Notification Enhancer 变更通知... | design | design_only |
| 44 | D-OPS/Change Notifier 变更通知器 | Change Notifier 变更通知器 | design | design_only |
| 45 | D-OPS/Chaos Engineering Engine 混沌工程引擎 | Chaos Engineering Engine 混沌工程引擎 | design | design_only |
| 46 | D-OPS/Chaos Engineering Fault Injection 混沌工程与故障注入 | Chaos Engineering Fault Injection 混... | design | design_only |
| 47 | D-OPS/Chaos Experiment Dependency Graph Builder 混沌实验... | Chaos Experiment Dependency Graph Bui... | design | design_only |
| 48 | D-OPS/Chaos Experiment Dependency Validator 混沌实验依赖... | Chaos Experiment Dependency Validator... | design | design_only |
| 49 | D-OPS/Chaos Result Knowledge Base 混沌结果知识库 | Chaos Result Knowledge Base 混沌结果... | design | design_only |
| 50 | D-OPS/Circuit Breaker Dependency Graph Builder 熔断器依赖... | Circuit Breaker Dependency Graph Buil... | design | design_only |
| 51 | D-OPS/Circuit Breaker Modeler 熔断器建模器 | Circuit Breaker Modeler 熔断器建模器 | design | design_only |
| 52 | D-OPS/Cloud-Edge-Device Scheduler 云-边-端调度器 | Cloud-Edge-Device Scheduler 云-边-端... | design | design_only |
| 53 | D-OPS/Conditional Dependency Activation Detector 条件依赖... | Conditional Dependency Activation Det... | design | design_only |
| 54 | D-OPS/Configuration Manager 配置管理 | Configuration Manager 配置管理 | design | design_only |
| 55 | D-OPS/Critical Path Fault Generator 关键路径故障生成器 | Critical Path Fault Generator 关键路... | design | design_only |
| 56 | D-OPS/Cross-Domain Ops Event Chain Tracking 跨域运维事件... | Cross-Domain Ops Event Chain Tracking... | design | design_only |
| 57 | D-OPS/Cross-Env Dependency Diff Analyzer 跨环境依赖差异分析 | Cross-Env Dependency Diff Analyzer 跨... | design | design_only |
| 58 | D-OPS/Cross-Language Dependency Chain Fixer 跨语言依赖链... | Cross-Language Dependency Chain Fixer... | design | design_only |
| 59 | D-OPS/D-OPS | D-OPS | design | design_only |
| 60 | D-OPS/DNS Dependency Discoverer DNS依赖发现器 | DNS Dependency Discoverer DNS依赖发现器 | design | design_only |
| 61 | D-OPS/DNS Dependency Discovery Enhancer DNS依赖发现增强 | DNS Dependency Discovery Enhancer DNS... | design | design_only |
| 62 | D-OPS/DNS Query Collector DNS查询采集器 | DNS Query Collector DNS查询采集器 | design | design_only |
| 63 | D-OPS/DR Manager 灾难恢复 | DR Manager 灾难恢复 | design | design_only |
| 64 | D-OPS/DSV Encoding Enhancer DSV编码增强 | DSV Encoding Enhancer DSV编码增强 | design | design_only |
| 65 | D-OPS/Data Quality SLA Monitor 数据质量SLA监控 | Data Quality SLA Monitor 数据质量SLA监控 | design | design_only |
| 66 | D-OPS/Degradation Chain Validator 降级链验证器 | Degradation Chain Validator 降级链验证器 | design | design_only |
| 67 | D-OPS/Degradation Path Modeler 降级路径建模器 | Degradation Path Modeler 降级路径建模器 | design | design_only |
| 68 | D-OPS/Degradation Strategy Manager 降级策略管理器 | Degradation Strategy Manager 降级策略... | design | design_only |
| 69 | D-OPS/Dependency Bottleneck Resource Optimizer 依赖瓶颈资... | Dependency Bottleneck Resource Optimi... | design | design_only |
| 70 | D-OPS/Dependency Circuit Breaker 依赖断路器 | Dependency Circuit Breaker 依赖断路器 | design | design_only |
| 71 | D-OPS/Dependency Cost Tracker 依赖图成本追踪 | Dependency Cost Tracker 依赖图成本追踪 | design | design_only |
| 72 | D-OPS/Dependency Criticality DCS Scoring Enhancer 依赖关... | Dependency Criticality DCS Scoring En... | design | design_only |
| 73 | D-OPS/Dependency Criticality Scorer 依赖关键度评分器 | Dependency Criticality Scorer 依赖关... | design | design_only |
| 74 | D-OPS/Dependency Drift Distance Metric Enhancer 依赖漂移... | Dependency Drift Distance Metric Enha... | design | design_only |
| 75 | D-OPS/Dependency Graph Builder 依赖图构建器 | Dependency Graph Builder 依赖图构建器 | design | design_only |
| 76 | D-OPS/Dependency Graph Resilience Scorer 依赖图韧性评分器 | Dependency Graph Resilience Scorer 依... | design | design_only |
| 77 | D-OPS/Dependency Health Scoring Engine 依赖健康评分引擎 | Dependency Health Scoring Engine 依赖... | design | design_only |
| 78 | D-OPS/Dependency State Vector Encoder 依赖状态向量编码器 | Dependency State Vector Encoder 依赖... | design | design_only |
| 79 | D-OPS/Deploy Order CSP Solver 部署顺序CSP求解器 | Deploy Order CSP Solver 部署顺序CSP求... | design | design_only |
| 80 | D-OPS/Deployment Manager 部署管理 | Deployment Manager 部署管理 | design | design_only |
| 81 | D-OPS/Differentiable Impact Simulation Enhancer 可微分影... | Differentiable Impact Simulation Enha... | design | design_only |
| 82 | D-OPS/Differentiable Impact Simulator 可微分影响仿真器 | Differentiable Impact Simulator 可微... | design | design_only |
| 83 | D-OPS/Disaster Recovery 3-2-1-1-0 灾备架构3-2-1-1-0 | Disaster Recovery 3-2-1-1-0 灾备架构3... | design | design_only |
| 84 | D-OPS/Disaster Recovery Architecture 灾备架构 | Disaster Recovery Architecture 灾备架构 | design | design_only |
| 85 | D-OPS/Disaster Recovery Engine 灾备引擎 | Disaster Recovery Engine 灾备引擎 | design | design_only |
| 86 | D-OPS/Distributed Trace Dependency Correlator 分布式追踪... | Distributed Trace Dependency Correlat... | design | design_only |
| 87 | D-OPS/Documentation Drift Anti-Pattern Detection Enhancer... | Documentation Drift Anti-Pattern Dete... | design | design_only |
| 88 | D-OPS/Dual Machine Hot Standby 双机热备 | Dual Machine Hot Standby 双机热备 | design | design_only |
| 89 | D-OPS/Dynamic Dependency Graph Builder 动态依赖图构建器 | Dynamic Dependency Graph Builder 动态... | design | design_only |
| 90 | D-OPS/Edge Dependency Constraint Modeler 边缘依赖约束建模器 | Edge Dependency Constraint Modeler 边... | design | design_only |
| 91 | D-OPS/Emergency Life Saving Track 应急保命轨 | Emergency Life Saving Track 应急保命轨 | design | design_only |
| 92 | D-OPS/Emergency Preservation Track 应急保命轨 | Emergency Preservation Track 应急保命轨 | design | design_only |
| 93 | D-OPS/Emergency Survival Track 应急保命轨 | Emergency Survival Track 应急保命轨 | design | design_only |
| 94 | D-OPS/EmergencyDegradationTrack 保命轨 | EmergencyDegradationTrack 保命轨 | design | design_only |
| 95 | D-OPS/Envoy Dependency Extractor Envoy依赖提取器 | Envoy Dependency Extractor Envoy依赖... | design | design_only |
| 96 | D-OPS/Experiment Recorder 实验记录器 | Experiment Recorder 实验记录器 | design | design_only |
| 97 | D-OPS/Experiment Reporter 实验报告器 | Experiment Reporter 实验报告器 | design | design_only |
| 98 | D-OPS/External Dependency SLA Monitor 外部依赖SLA监控 | External Dependency SLA Monitor 外部... | design | design_only |
| 99 | D-OPS/Fault Injector 故障注入器 | Fault Injector 故障注入器 | design | design_only |
| 100 | D-OPS/Fault Scenario Definer 故障场景定义器 | Fault Scenario Definer 故障场景定义器 | design | design_only |
| 101 | D-OPS/File Access Collector 文件访问采集器 | File Access Collector 文件访问采集器 | design | design_only |
| 102 | D-OPS/File I/O Dependency Discoverer 文件I/O依赖发现器 | File I/O Dependency Discoverer 文件I/... | design | design_only |
| 103 | D-OPS/File I/O Dependency Discovery Enhancer 文件I/O依赖... | File I/O Dependency Discovery Enhance... | design | design_only |
| 104 | D-OPS/FinOps Cost Anomaly Detector FinOps成本异常检测 | FinOps Cost Anomaly Detector FinOps成... | design | design_only |
| 105 | D-OPS/GPU Scheduling GPU调度上岗 | GPU Scheduling GPU调度上岗 | design | design_only |
| 106 | D-OPS/GPU显存异常检测规则 | GPU显存异常检测规则 | design | design_only |
| 107 | D-OPS/GitOps Dependency Resolver GitOps依赖解析器 | GitOps Dependency Resolver GitOps依赖... | design | design_only |
| 108 | D-OPS/Green Deployment Strategist 绿色部署策略器 | Green Deployment Strategist 绿色部署... | design | design_only |
| 109 | D-OPS/Health Check Readiness Probe 健康检查与就绪探针 | Health Check Readiness Probe 健康检查... | design | design_only |
| 110 | D-OPS/Health Monitoring 健康监控 | Health Monitoring 健康监控 | design | design_only |
| 111 | D-OPS/High-Risk Node Fault Generator 高风险节点故障生成器 | High-Risk Node Fault Generator 高风险... | design | design_only |
| 112 | D-OPS/ISO 23247-4 Dependency Entity Model ISO 23247-4依赖... | ISO 23247-4 Dependency Entity Model I... | design | design_only |
| 113 | D-OPS/ISO 23247-4 Entity Model Enhancer ISO 23247-4实体模... | ISO 23247-4 Entity Model Enhancer ISO... | design | design_only |
| 114 | D-OPS/Implicit Dependency Discoverer 隐式依赖发现器 | Implicit Dependency Discoverer 隐式依... | design | design_only |
| 115 | D-OPS/Incremental Chaos Validation Enhancer 增量混沌验证增强 | Incremental Chaos Validation Enhancer... | design | design_only |
| 116 | D-OPS/Incremental Chaos Validator 增量混沌验证器 | Incremental Chaos Validator 增量混沌... | design | design_only |
| 117 | D-OPS/Integration Health Monitor 集成健康监控器 | Integration Health Monitor 集成健康监... | design | design_only |
| 118 | D-OPS/Istio Ambient Mode Dependency Enhancer Istio Ambien... | Istio Ambient Mode Dependency Enhance... | design | design_only |
| 119 | D-OPS/Istio Config Parser Istio配置解析器 | Istio Config Parser Istio配置解析器 | design | design_only |
| 120 | D-OPS/Istio Policy DSL Generation Enhancer Istio策略DSL生... | Istio Policy DSL Generation Enhancer ... | design | design_only |
| 121 | D-OPS/Istio Policy DSL Generator Istio策略DSL生成器 | Istio Policy DSL Generator Istio策略D... | design | design_only |
| 122 | D-OPS/LLM API SLA Monitor LLM API SLA监控 | LLM API SLA Monitor LLM API SLA监控 | design | design_only |
| 123 | D-OPS/LLM Hallucination Correlation Misjudgment Filter LL... | LLM Hallucination Correlation Misjudg... | design | design_only |
| 124 | D-OPS/Left Kan Extension Dependency Resolver 左Kan扩展依... | Left Kan Extension Dependency Resolve... | design | design_only |
| 125 | D-OPS/Linkerd Policy Generation Enhancer Linkerd策略生成增强 | Linkerd Policy Generation Enhancer Li... | design | design_only |
| 126 | D-OPS/Linkerd Policy Generator Linkerd策略生成器 | Linkerd Policy Generator Linkerd策略... | design | design_only |
| 127 | D-OPS/Log Correlator 日志关联器 | Log Correlator 日志关联器 | design | design_only |
| 128 | D-OPS/Low-Carbon Window Detection Enhancer 低碳窗口检测增... | Low-Carbon Window Detection Enhancer ... | design | design_only |
| 129 | D-OPS/Low-Carbon Window Detector 低碳窗口检测器 | Low-Carbon Window Detector 低碳窗口检... | design | design_only |
| 130 | D-OPS/Metric Correlator 指标关联器 | Metric Correlator 指标关联器 | design | design_only |
| 131 | D-OPS/Metric Dependency Anomaly Detector 指标依赖异常检测 | Metric Dependency Anomaly Detector 指... | design | design_only |
| 132 | D-OPS/Minimum Blast Radius Calculator 最小爆破半径计算器 | Minimum Blast Radius Calculator 最小... | design | design_only |
| 133 | D-OPS/Model Hot Swap 模型热交换 | Model Hot Swap 模型热交换 | design | design_only |
| 134 | D-OPS/Monitor Agent 监控Agent | Monitor Agent 监控Agent | design | design_only |
| 135 | D-OPS/Monitoring System 监控体系 | Monitoring System 监控体系 | design | design_only |
| 136 | D-OPS/Multi-Cloud SLA Aggregation Engine 多云SLA聚合引擎 | Multi-Cloud SLA Aggregation Engine 多... | design | design_only |
| 137 | D-OPS/Network Connection Collector 网络连接采集器 | Network Connection Collector 网络连接... | design | design_only |
| 138 | D-OPS/Network Resilience Scoring Engine 网络韧性评分引擎 | Network Resilience Scoring Engine 网... | design | design_only |
| 139 | D-OPS/Network Topology Discoverer 网络拓扑发现器 | Network Topology Discoverer 网络拓扑... | design | design_only |
| 140 | D-OPS/Network Topology Discovery Enhancer 网络拓扑发现增强 | Network Topology Discovery Enhancer ... | design | design_only |
| 141 | D-OPS/Neuromorphic Event-Driven Scheduler 神经形态事件驱... | Neuromorphic Event-Driven Scheduler ... | design | design_only |
| 142 | D-OPS/OTel Auto-Topology Builder OTel自动拓扑构建器 | OTel Auto-Topology Builder OTel自动拓... | design | design_only |
| 143 | D-OPS/OTel Collector Integration OTel Collector集成 | OTel Collector Integration OTel Colle... | design | design_only |
| 144 | D-OPS/OTel GenAI SemConv Integrator OTel GenAI语义约定集成器 | OTel GenAI SemConv Integrator OTel Ge... | design | design_only |
| 145 | D-OPS/OTel GenAI Semantic Conventions OTel GenAI语义约定 | OTel GenAI Semantic Conventions OTel ... | design | design_only |
| 146 | D-OPS/OpenTelemetry 2.0 | OpenTelemetry 2.0 | design | design_only |
| 147 | D-OPS/OpenTelemetry分布式追踪 分布式追踪 | OpenTelemetry分布式追踪 分布式追踪 | design | design_only |
| 148 | D-OPS/Operations Specification 运维规格 | Operations Specification 运维规格 | design | design_only |
| 149 | D-OPS/Ops Automation Runbook Engine 运维自动化Runbook引擎 | Ops Automation Runbook Engine 运维自... | design | design_only |
| 150 | D-OPS/Ops Foundation 运维基础 | Ops Foundation 运维基础 | design | design_only |
| 151 | D-OPS/OpsIncident 运维事件 | OpsIncident 运维事件 | design | design_only |
| 152 | D-OPS/Paper Live Transition 模拟实盘转换 | Paper Live Transition 模拟实盘转换 | design | design_only |
| 153 | D-OPS/Performance Baseline 性能基线 | Performance Baseline 性能基线 | design | design_only |
| 154 | D-OPS/Performance Profiler 性能分析器 | Performance Profiler 性能分析器 | design | design_only |
| 155 | D-OPS/Post Live Verification 上线后验证 | Post Live Verification 上线后验证 | design | design_only |
| 156 | D-OPS/Post Process 后处理 | Post Process 后处理 | design | design_only |
| 157 | D-OPS/Predictive System Maintenance 预测性系统维护 | Predictive System Maintenance 预测性... | design | design_only |
| 158 | D-OPS/Process Call Collector 进程调用采集器 | Process Call Collector 进程调用采集器 | design | design_only |
| 159 | D-OPS/Process Relationship Tracker 进程关系追踪器 | Process Relationship Tracker 进程关系... | design | design_only |
| 160 | D-OPS/Process Relationship Tracking Enhancer 进程关系追踪... | Process Relationship Tracking Enhance... | design | design_only |
| 161 | D-OPS/Progressive Delivery Dependency Checker 渐进式交付... | Progressive Delivery Dependency Check... | design | design_only |
| 162 | D-OPS/PubGrub Version Solver PubGrub版本求解器 | PubGrub Version Solver PubGrub版本求解器 | design | design_only |
| 163 | D-OPS/Query Router 查询路由器 | Query Router 查询路由器 | design | design_only |
| 164 | D-OPS/Query Routing Enhancer 查询路由增强器 | Query Routing Enhancer 查询路由增强器 | design | design_only |
| 165 | D-OPS/RED方法指标 请求错误延迟 | RED方法指标 请求错误延迟 | design | design_only |
| 166 | D-OPS/Rate Limiter Modeler 限流器建模器 | Rate Limiter Modeler 限流器建模器 | design | design_only |
| 167 | D-OPS/Real-time Graph Diff Enhancer 实时图差异增强器 | Real-time Graph Diff Enhancer 实时图... | design | design_only |
| 168 | D-OPS/Real-time Graph Differ 实时图差异器 | Real-time Graph Differ 实时图差异器 | design | design_only |
| 169 | D-OPS/Real-time Simulator 实时仿真器 | Real-time Simulator 实时仿真器 | design | design_only |
| 170 | D-OPS/Recovery Validator 恢复验证器 | Recovery Validator 恢复验证器 | design | design_only |
| 171 | D-OPS/Redis Cluster Sentinel Redis集群/哨兵 | Redis Cluster Sentinel Redis集群/哨兵 | design | design_only |
| 172 | D-OPS/Redis内存预测异常检测规则 | Redis内存预测异常检测规则 | design | design_only |
| 173 | D-OPS/RemediationExecuted 修复动作执行完成 | RemediationExecuted 修复动作执行完成 | design | design_only |
| 174 | D-OPS/RemediationRolledBack 修复回滚 | RemediationRolledBack 修复回滚 | design | design_only |
| 175 | D-OPS/Repair Roller 修复回滚器 | Repair Roller 修复回滚器 | design | design_only |
| 176 | D-OPS/Repair Suggester 修复建议器 | Repair Suggester 修复建议器 | design | design_only |
| 177 | D-OPS/Repair Validation Gate 修复验证门禁 | Repair Validation Gate 修复验证门禁 | design | design_only |
| 178 | D-OPS/Repair Validator 修复验证器 | Repair Validator 修复验证器 | design | design_only |
| 179 | D-OPS/Resilience Evaluator 韧性评估器 | Resilience Evaluator 韧性评估器 | design | design_only |
| 180 | D-OPS/Resilience Scorer 韧性评分器 | Resilience Scorer 韧性评分器 | design | design_only |
| 181 | D-OPS/Resource Dependency Capacity Planner 资源依赖容量规划 | Resource Dependency Capacity Planner ... | design | design_only |
| 182 | D-OPS/Retry Storm Predictor 重试风暴预测器 | Retry Storm Predictor 重试风暴预测器 | design | design_only |
| 183 | D-OPS/Retry Strategy Modeler 重试策略建模器 | Retry Strategy Modeler 重试策略建模器 | design | design_only |
| 184 | D-OPS/Runbook Automator 运维手册自动化 | Runbook Automator 运维手册自动化 | design | design_only |
| 185 | D-OPS/Runtime Architecture 运行时架构 | Runtime Architecture 运行时架构 | design | design_only |
| 186 | D-OPS/Runtime Dependency Collector 运行时依赖采集器 | Runtime Dependency Collector 运行时依... | design | design_only |
| 187 | D-OPS/Runtime vs Static Differ 运行时vs静态差异器 | Runtime vs Static Differ 运行时vs静态... | design | design_only |
| 188 | D-OPS/SLA Breach Detector SLA违约检测器 | SLA Breach Detector SLA违约检测器 | design | design_only |
| 189 | D-OPS/SLA Breach Predictor SLA违约预测器 | SLA Breach Predictor SLA违约预测器 | design | design_only |
| 190 | D-OPS/SLA Definer SLA定义器 | SLA Definer SLA定义器 | design | design_only |
| 191 | D-OPS/SLA Monitor SLA监控器 | SLA Monitor SLA监控器 | design | design_only |
| 192 | D-OPS/SLA Report Generator SLA报告生成器 | SLA Report Generator SLA报告生成器 | design | design_only |
| 193 | D-OPS/SLA-Aware Traffic Router SLA感知流量路由器 | SLA-Aware Traffic Router SLA感知流量... | design | design_only |
| 194 | D-OPS/SLO Manager SLO管理 | SLO Manager SLO管理 | design | design_only |
| 195 | D-OPS/SLO Manager SLO管理器 | SLO Manager SLO管理器 | design | design_only |
| 196 | D-OPS/SLOBreached SLO违约 | SLOBreached SLO违约 | design | design_only |
| 197 | D-OPS/SLO定义 服务等级目标 | SLO定义 服务等级目标 | design | design_only |
| 198 | D-OPS/SNN Anomaly Detection Enhancer SNN异常检测增强 | SNN Anomaly Detection Enhancer SNN异... | design | design_only |
| 199 | D-OPS/SNN Dependency Anomaly Detector SNN依赖异常检测器 | SNN Dependency Anomaly Detector SNN依... | design | design_only |
| 200 | D-OPS/STDP Dynamic Weight Engine STDP脉冲学习动态权重引擎 | STDP Dynamic Weight Engine STDP脉冲学... | design | design_only |

> (仅显示前 200 个模块，共 275 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 584 条 / 584 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 584 条 / 584 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 368 条 / edges                               │
│   [config_depends]: 192 条 / edges                               │
│   [runtime]: 7 条 / edges                                        │
│   [test_depends]: 6 条 / edges                                   │
│   [event]: 6 条 / edges                                          │
│   [contract]: 5 条 / edges                                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (368 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   budget_engine.py → budget_models.py                            │
│   budget_tracker.py → budget_models.py                           │
│   auto_evolution.py → __init__.py                                │
│   backpressure_bridge.py → __init__.py                           │
│   db_writer.py → __init__.py                                     │
│   decision_engine.py → __init__.py                               │
│   generator.py → __init__.py                                     │
│   scheduler.py → __init__.py                                     │
│   scheduler_act.py → __init__.py                                 │
│   scheduler_safety.py → __init__.py                              │
│   scheduler_collect_detect.py → __init__.py                      │
│   scheduler_health.py → __init__.py                              │
│   validator.py → __init__.py                                     │
│   action_selector.py → __init__.py                               │
│   __init___from_obs.py → __init__.py                             │
│   __init__.py → action_selector.py                               │
│   __init__.py → api_version_contract.py                          │
│   __init__.py → agent_lifecycle.py                               │
│   __init__.py → alert_router.py                                  │
│   __init__.py → global_action_scheduler.py                       │
│   __init__.py → incident_priority_triage_...                     │
│   __init__.py → owner_absence_escalation.py                      │
│   __init__.py → saga_compensator.py                              │
│   __init__.py → multi_agent_orchestrator.py                      │
│   __init__.py → intent_driven_ops.py                             │
│   __init__.py → notification_personalizer.py                     │
│   __init__.py → secondary_alert_channel.py                       │
│   __init__.py → calendar_adapter.py                              │
│   __init__.py → config_timeline.py                               │
│   __init__.py → data_quality_validator.py                        │
│   __init__.py → kb_provenance.py                                 │
│   __init__.py → financial_stratification.py                      │
│   __init__.py → feedback_collector.py                            │
│   __init__.py → knowledge_freshness.py                           │
│   __init__.py → knowledge_capture.py                             │
│   __init__.py → knowledge_packaging.py                           │
│   __init__.py → knowledge_injection.py                           │
│   __init__.py → llm_cost_accounting.py                           │
│   __init__.py → schema_evolution.py                              │
│   __init__.py → temporal_event_store.py                          │
│   __init__.py → known_unknown_registry.py                        │
│   __init__.py → market_event_integrator.py                       │
│   __init__.py → metrics_collector.py                             │
│   __init__.py → market_calendar.py                               │
│   __init__.py → schema_migration.py                              │
│   __init__.py → notification_feedback.py                         │
│   __init__.py → token_finops.py                                  │
│   anomaly_detector.py → __init__.py                              │
│   __init__.py → __init__.py                                      │
│   ...还有 319 条 / 319 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (192 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (7 条 / edges) — 已达显示上限，省略 / limit reached

**[test_depends]** (6 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (6 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (5 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 584 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `12_d_ops_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
