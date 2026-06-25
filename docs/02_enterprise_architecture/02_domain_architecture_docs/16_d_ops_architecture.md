---
doc_type: domain_architecture_diagram
title: D-OPS 反馈循环架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 16_d_ops / 反馈循环 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示反馈循环（D-OPS）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 反馈循环（D-OPS）的模块分布。共 445 个模块 / 445 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (423 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   architecture_model/layers/system_telemetry.yaml  [production]  │
│   config/capacity/token_budget.yaml  [production]                │
│   docs__03_modules___domain_infra_ops__system_telemetry__blue... │
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
│   src/zephyr/governance/observability_governance/provenance_t... │
│   src/zephyr/governance/token_budget.py  [prototype]             │
│   src/zephyr/ops/__init__.py  [production]                       │
│   ...还有 405 个模块 / 405 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (22 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   F20-unified-monitor/  [design]                                 │
│   F4-budget-engine/  [design]                                    │
│   scripts/ops/auto_fix_cron.py  [production]                     │
│   scripts/ops/upgrade_headers_to_14fields.py  [production]       │
│   src/zephyr/ops/gates/safety_gate_l28_l29.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l36_l37.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l38_l39.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l40_l41.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l42_l43.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l44_l45.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l46_l47.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l48_l49.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l50_l51.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l52_l53.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l54_l55.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l56_l57.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l58_l59.py  [production]      │
│   src/zephyr/ops/gates/safety_gate_l60_l61.py  [production]      │
│   ...还有 4 个模块 / 4 more modules                              │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 445 个模块 / 445 modules）。

### L1 基础层 / Foundation Layer (423 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | architecture_model/layers/system_telemetry.yaml | architecture_model/layers/system_tele... | production | deprecated |
| 2 | config/capacity/token_budget.yaml | config/capacity/token_budget.yaml | production | deprecated |
| 3 | docs/03_modules/_domain_infra_ops/system_telemetry/bluepr... | docs__03_modules___domain_infra_ops__... | design | planned |
| 4 | src/zephyr/governance/budget_engine.py | src/zephyr/governance/budget_engine.py | prototype | generated |
| 5 | src/zephyr/governance/budget_handler.py | src/zephyr/governance/budget_handler.py | prototype | generated |
| 6 | src/zephyr/governance/budget_models.py | src/zephyr/governance/budget_models.py | prototype | generated |
| 7 | src/zephyr/governance/budget_profile_manager.py | src/zephyr/governance/budget_profile_... | prototype | generated |
| 8 | src/zephyr/governance/budget_tracker.py | src/zephyr/governance/budget_tracker.py | prototype | generated |
| 9 | src/zephyr/governance/cost_budget.py | src/zephyr/governance/cost_budget.py | prototype | generated |
| 10 | src/zephyr/governance/meta_observability.py | src/zephyr/governance/meta_observabil... | prototype | generated |
| 11 | src/zephyr/governance/observability_dashboard.py | src/zephyr/governance/observability_d... | prototype | generated |
| 12 | src/zephyr/governance/observability_governance/__init__.py | src/zephyr/governance/observability_g... | prototype | generated |
| 13 | src/zephyr/governance/observability_governance/benchmark_... | src/zephyr/governance/observability_g... | prototype | generated |
| 14 | src/zephyr/governance/observability_governance/observabil... | src/zephyr/governance/observability_g... | production | generated |
| 15 | src/zephyr/governance/observability_governance/performanc... | src/zephyr/governance/observability_g... | prototype | generated |
| 16 | src/zephyr/governance/observability_governance/provenance... | src/zephyr/governance/observability_g... | prototype | generated |
| 17 | src/zephyr/governance/token_budget.py | src/zephyr/governance/token_budget.py | prototype | generated |
| 18 | src/zephyr/ops/__init__.py | src/zephyr/ops/__init__.py | production | generated |
| 19 | src/zephyr/ops/__init___from_obs.py | src/zephyr/ops/__init___from_obs.py | prototype | generated |
| 20 | src/zephyr/ops/_budget_telemetry_bridge.py | src/zephyr/ops/_budget_telemetry_brid... | prototype | generated |
| 21 | src/zephyr/ops/_circuit_breaker.py | src/zephyr/ops/_circuit_breaker.py | prototype | generated |
| 22 | src/zephyr/ops/_extensions/__init__.py | src/zephyr/ops/_extensions/__init__.py | prototype | deprecated |
| 23 | src/zephyr/ops/_gen_inherited.py | src/zephyr/ops/_gen_inherited.py | prototype | generated |
| 24 | src/zephyr/ops/_trace_bridge.py | src/zephyr/ops/_trace_bridge.py | prototype | generated |
| 25 | src/zephyr/ops/actors/__init__.py | src/zephyr/ops/actors/__init__.py | prototype | generated |
| 26 | src/zephyr/ops/actors/action_selector.py | src/zephyr/ops/actors/action_selector.py | prototype | generated |
| 27 | src/zephyr/ops/actors/agent_lifecycle.py | src/zephyr/ops/actors/agent_lifecycle.py | prototype | generated |
| 28 | src/zephyr/ops/actors/alert_router.py | src/zephyr/ops/actors/alert_router.py | prototype | generated |
| 29 | src/zephyr/ops/actors/api_version_contract.py | src/zephyr/ops/actors/api_version_con... | prototype | generated |
| 30 | src/zephyr/ops/actors/global_action_scheduler.py | src/zephyr/ops/actors/global_action_s... | prototype | generated |
| 31 | src/zephyr/ops/actors/incident_priority_triage_automator.py | src/zephyr/ops/actors/incident_priori... | prototype | generated |
| 32 | src/zephyr/ops/actors/intent_driven_ops.py | src/zephyr/ops/actors/intent_driven_o... | prototype | generated |
| 33 | src/zephyr/ops/actors/multi_agent_orchestrator.py | src/zephyr/ops/actors/multi_agent_orc... | prototype | generated |
| 34 | src/zephyr/ops/actors/notification_personalizer.py | src/zephyr/ops/actors/notification_pe... | prototype | generated |
| 35 | src/zephyr/ops/actors/owner_absence_escalation.py | src/zephyr/ops/actors/owner_absence_e... | prototype | generated |
| 36 | src/zephyr/ops/actors/saga_compensator.py | src/zephyr/ops/actors/saga_compensato... | prototype | generated |
| 37 | src/zephyr/ops/actors/secondary_alert_channel.py | src/zephyr/ops/actors/secondary_alert... | prototype | generated |
| 38 | src/zephyr/ops/ai_behavior/__init__.py | src/zephyr/ops/ai_behavior/__init__.py | prototype | generated |
| 39 | src/zephyr/ops/ai_behavior/event_sink.py | src/zephyr/ops/ai_behavior/event_sink.py | prototype | generated |
| 40 | src/zephyr/ops/alert_dispatcher.py | src/zephyr/ops/alert_dispatcher.py | prototype | generated |
| 41 | src/zephyr/ops/alerts/__init__.py | src/zephyr/ops/alerts/__init__.py | prototype | generated |
| 42 | src/zephyr/ops/analytics_base.py | src/zephyr/ops/analytics_base.py | prototype | generated |
| 43 | src/zephyr/ops/api/__init__.py | src/zephyr/ops/api/__init__.py | prototype | deprecated |
| 44 | src/zephyr/ops/archive/__init__.py | src/zephyr/ops/archive/__init__.py | prototype | generated |
| 45 | src/zephyr/ops/archive/cold_stub.py | src/zephyr/ops/archive/cold_stub.py | prototype | generated |
| 46 | src/zephyr/ops/auto_bootstrap.py | src/zephyr/ops/auto_bootstrap.py | prototype | generated |
| 47 | src/zephyr/ops/auto_evolution.py | src/zephyr/ops/auto_evolution.py | prototype | generated |
| 48 | src/zephyr/ops/backpressure_bridge.py | src/zephyr/ops/backpressure_bridge.py | prototype | generated |
| 49 | src/zephyr/ops/circuit_breaker.py | src/zephyr/ops/circuit_breaker.py | prototype | generated |
| 50 | src/zephyr/ops/circuit_breaker_repo.py | src/zephyr/ops/circuit_breaker_repo.py | prototype | generated |
| 51 | src/zephyr/ops/circuit_breaker_types.py | src/zephyr/ops/circuit_breaker_types.py | prototype | generated |
| 52 | src/zephyr/ops/collectors/__init__.py | src/zephyr/ops/collectors/__init__.py | prototype | generated |
| 53 | src/zephyr/ops/collectors/calendar_adapter.py | src/zephyr/ops/collectors/calendar_ad... | prototype | generated |
| 54 | src/zephyr/ops/collectors/config_timeline.py | src/zephyr/ops/collectors/config_time... | prototype | generated |
| 55 | src/zephyr/ops/collectors/data_quality_validator.py | src/zephyr/ops/collectors/data_qualit... | prototype | generated |
| 56 | src/zephyr/ops/collectors/feedback_collector.py | src/zephyr/ops/collectors/feedback_co... | prototype | generated |
| 57 | src/zephyr/ops/collectors/financial_stratification.py | src/zephyr/ops/collectors/financial_s... | prototype | generated |
| 58 | src/zephyr/ops/collectors/kb_provenance.py | src/zephyr/ops/collectors/kb_provenan... | prototype | generated |
| 59 | src/zephyr/ops/collectors/knowledge_capture.py | src/zephyr/ops/collectors/knowledge_c... | prototype | generated |
| 60 | src/zephyr/ops/collectors/knowledge_freshness.py | src/zephyr/ops/collectors/knowledge_f... | prototype | generated |
| 61 | src/zephyr/ops/collectors/knowledge_injection.py | src/zephyr/ops/collectors/knowledge_i... | prototype | generated |
| 62 | src/zephyr/ops/collectors/knowledge_packaging.py | src/zephyr/ops/collectors/knowledge_p... | prototype | generated |
| 63 | src/zephyr/ops/collectors/known_unknown_registry.py | src/zephyr/ops/collectors/known_unkno... | prototype | generated |
| 64 | src/zephyr/ops/collectors/llm_cost_accounting.py | src/zephyr/ops/collectors/llm_cost_ac... | prototype | generated |
| 65 | src/zephyr/ops/collectors/market_calendar.py | src/zephyr/ops/collectors/market_cale... | prototype | generated |
| 66 | src/zephyr/ops/collectors/market_event_integrator.py | src/zephyr/ops/collectors/market_even... | prototype | generated |
| 67 | src/zephyr/ops/collectors/metrics_collector.py | src/zephyr/ops/collectors/metrics_col... | prototype | generated |
| 68 | src/zephyr/ops/collectors/notification_feedback.py | src/zephyr/ops/collectors/notificatio... | prototype | generated |
| 69 | src/zephyr/ops/collectors/schema_evolution.py | src/zephyr/ops/collectors/schema_evol... | prototype | generated |
| 70 | src/zephyr/ops/collectors/schema_migration.py | src/zephyr/ops/collectors/schema_migr... | prototype | generated |
| 71 | src/zephyr/ops/collectors/temporal_event_store.py | src/zephyr/ops/collectors/temporal_ev... | prototype | generated |
| 72 | src/zephyr/ops/collectors/token_finops.py | src/zephyr/ops/collectors/token_finop... | prototype | generated |
| 73 | src/zephyr/ops/config.py | src/zephyr/ops/config.py | prototype | generated |
| 74 | src/zephyr/ops/contract_metrics.py | src/zephyr/ops/contract_metrics.py | prototype | generated |
| 75 | src/zephyr/ops/core/__init__.py | src/zephyr/ops/core/__init__.py | prototype | deprecated |
| 76 | src/zephyr/ops/db_bridge.py | src/zephyr/ops/db_bridge.py | prototype | generated |
| 77 | src/zephyr/ops/db_writer.py | src/zephyr/ops/db_writer.py | prototype | generated |
| 78 | src/zephyr/ops/decision_engine.py | src/zephyr/ops/decision_engine.py | prototype | generated |
| 79 | src/zephyr/ops/detectors/__init__.py | src/zephyr/ops/detectors/__init__.py | prototype | generated |
| 80 | src/zephyr/ops/detectors/_anomaly.py | src/zephyr/ops/detectors/_anomaly.py | prototype | generated |
| 81 | src/zephyr/ops/detectors/_correlation.py | src/zephyr/ops/detectors/_correlation.py | prototype | generated |
| 82 | src/zephyr/ops/detectors/_drift.py | src/zephyr/ops/detectors/_drift.py | prototype | generated |
| 83 | src/zephyr/ops/detectors/_guard.py | src/zephyr/ops/detectors/_guard.py | prototype | generated |
| 84 | src/zephyr/ops/detectors/_reliability.py | src/zephyr/ops/detectors/_reliability.py | prototype | generated |
| 85 | src/zephyr/ops/detectors/action_efficacy_decay_detector.py | src/zephyr/ops/detectors/action_effic... | prototype | generated |
| 86 | src/zephyr/ops/detectors/action_interaction_detector.py | src/zephyr/ops/detectors/action_inter... | prototype | generated |
| 87 | src/zephyr/ops/detectors/action_side_effect_cumulative_de... | src/zephyr/ops/detectors/action_side_... | prototype | generated |
| 88 | src/zephyr/ops/detectors/agent_trajectory_anomaly_detecto... | src/zephyr/ops/detectors/agent_trajec... | prototype | generated |
| 89 | src/zephyr/ops/detectors/alert_desensitization_curve.py | src/zephyr/ops/detectors/alert_desens... | prototype | generated |
| 90 | src/zephyr/ops/detectors/anomaly_clustering.py | src/zephyr/ops/detectors/anomaly_clus... | prototype | generated |
| 91 | src/zephyr/ops/detectors/anomaly_detector.py | src/zephyr/ops/detectors/anomaly_dete... | prototype | generated |
| 92 | src/zephyr/ops/detectors/autoscale_remediation.py | src/zephyr/ops/detectors/autoscale_re... | prototype | generated |
| 93 | src/zephyr/ops/detectors/blast_radius.py | src/zephyr/ops/detectors/blast_radius.py | prototype | generated |
| 94 | src/zephyr/ops/detectors/blast_radius_budget.py | src/zephyr/ops/detectors/blast_radius... | prototype | generated |
| 95 | src/zephyr/ops/detectors/capacity_forecast.py | src/zephyr/ops/detectors/capacity_for... | prototype | generated |
| 96 | src/zephyr/ops/detectors/chaos_engineering.py | src/zephyr/ops/detectors/chaos_engine... | prototype | generated |
| 97 | src/zephyr/ops/detectors/concept_drift.py | src/zephyr/ops/detectors/concept_drif... | prototype | generated |
| 98 | src/zephyr/ops/detectors/config_drift.py | src/zephyr/ops/detectors/config_drift.py | prototype | generated |
| 99 | src/zephyr/ops/detectors/context_window_contamination_det... | src/zephyr/ops/detectors/context_wind... | prototype | generated |
| 100 | src/zephyr/ops/detectors/cross_signal_validator.py | src/zephyr/ops/detectors/cross_signal... | prototype | generated |
| 101 | src/zephyr/ops/detectors/cross_system_correlator.py | src/zephyr/ops/detectors/cross_system... | prototype | generated |
| 102 | src/zephyr/ops/detectors/decision_provenance.py | src/zephyr/ops/detectors/decision_pro... | prototype | generated |
| 103 | src/zephyr/ops/detectors/dependency_freshness_monitor.py | src/zephyr/ops/detectors/dependency_f... | prototype | generated |
| 104 | src/zephyr/ops/detectors/diminishing_returns_detector.py | src/zephyr/ops/detectors/diminishing_... | prototype | generated |
| 105 | src/zephyr/ops/detectors/ebpf_monitor.py | src/zephyr/ops/detectors/ebpf_monitor.py | prototype | generated |
| 106 | src/zephyr/ops/detectors/emergent_behavior_detector.py | src/zephyr/ops/detectors/emergent_beh... | prototype | generated |
| 107 | src/zephyr/ops/detectors/ensemble_detector.py | src/zephyr/ops/detectors/ensemble_det... | prototype | generated |
| 108 | src/zephyr/ops/detectors/ensemble_drift.py | src/zephyr/ops/detectors/ensemble_dri... | prototype | generated |
| 109 | src/zephyr/ops/detectors/external_health.py | src/zephyr/ops/detectors/external_hea... | prototype | generated |
| 110 | src/zephyr/ops/detectors/external_validation_checkpoint.py | src/zephyr/ops/detectors/external_val... | prototype | generated |
| 111 | src/zephyr/ops/detectors/flag_lifecycle.py | src/zephyr/ops/detectors/flag_lifecyc... | prototype | generated |
| 112 | src/zephyr/ops/detectors/flapping_detector.py | src/zephyr/ops/detectors/flapping_det... | prototype | generated |
| 113 | src/zephyr/ops/detectors/fle_performance_regression_detec... | src/zephyr/ops/detectors/fle_performa... | prototype | generated |
| 114 | src/zephyr/ops/detectors/gradual_poisoning_detector.py | src/zephyr/ops/detectors/gradual_pois... | prototype | generated |
| 115 | src/zephyr/ops/detectors/guard_cascade_detector.py | src/zephyr/ops/detectors/guard_cascad... | prototype | generated |
| 116 | src/zephyr/ops/detectors/guard_oscillation_detector.py | src/zephyr/ops/detectors/guard_oscill... | prototype | generated |
| 117 | src/zephyr/ops/detectors/heisenbug_detector.py | src/zephyr/ops/detectors/heisenbug_de... | prototype | generated |
| 118 | src/zephyr/ops/detectors/infinite_loop_detector.py | src/zephyr/ops/detectors/infinite_loo... | prototype | generated |
| 119 | src/zephyr/ops/detectors/intermittent_failure_pattern.py | src/zephyr/ops/detectors/intermittent... | prototype | generated |
| 120 | src/zephyr/ops/detectors/log_anomaly.py | src/zephyr/ops/detectors/log_anomaly.py | prototype | generated |
| 121 | src/zephyr/ops/detectors/maintenance_coordinator.py | src/zephyr/ops/detectors/maintenance_... | prototype | generated |
| 122 | src/zephyr/ops/detectors/metric_cardinality_guard.py | src/zephyr/ops/detectors/metric_cardi... | prototype | generated |
| 123 | src/zephyr/ops/detectors/multi_signal_correlator.py | src/zephyr/ops/detectors/multi_signal... | prototype | generated |
| 124 | src/zephyr/ops/detectors/openfeature.py | src/zephyr/ops/detectors/openfeature.py | prototype | generated |
| 125 | src/zephyr/ops/detectors/otel_adapter.py | src/zephyr/ops/detectors/otel_adapter.py | prototype | generated |
| 126 | src/zephyr/ops/detectors/placebo_action_detector.py | src/zephyr/ops/detectors/placebo_acti... | prototype | generated |
| 127 | src/zephyr/ops/detectors/positive_feedback_defense.py | src/zephyr/ops/detectors/positive_fee... | prototype | generated |
| 128 | src/zephyr/ops/detectors/recursive_diagnosis_trust_evalua... | src/zephyr/ops/detectors/recursive_di... | prototype | generated |
| 129 | src/zephyr/ops/detectors/regime_detector.py | src/zephyr/ops/detectors/regime_detec... | prototype | generated |
| 130 | src/zephyr/ops/detectors/regulatory_audit.py | src/zephyr/ops/detectors/regulatory_a... | prototype | generated |
| 131 | src/zephyr/ops/detectors/resolution_tracker.py | src/zephyr/ops/detectors/resolution_t... | prototype | generated |
| 132 | src/zephyr/ops/detectors/rumor_noise_filter.py | src/zephyr/ops/detectors/rumor_noise_... | prototype | generated |
| 133 | src/zephyr/ops/detectors/runbook_executor.py | src/zephyr/ops/detectors/runbook_exec... | prototype | generated |
| 134 | src/zephyr/ops/detectors/self_audit.py | src/zephyr/ops/detectors/self_audit.py | prototype | generated |
| 135 | src/zephyr/ops/detectors/self_diagnosis_data_leak_detecto... | src/zephyr/ops/detectors/self_diagnos... | prototype | generated |
| 136 | src/zephyr/ops/detectors/self_ha.py | src/zephyr/ops/detectors/self_ha.py | prototype | generated |
| 137 | src/zephyr/ops/detectors/silent_corruption_detector.py | src/zephyr/ops/detectors/silent_corru... | prototype | generated |
| 138 | src/zephyr/ops/detectors/synthetic_anomaly_generator.py | src/zephyr/ops/detectors/synthetic_an... | prototype | generated |
| 139 | src/zephyr/ops/detectors/temporal_coherence_of_self_model.py | src/zephyr/ops/detectors/temporal_coh... | prototype | generated |
| 140 | src/zephyr/ops/detectors/temporal_pattern.py | src/zephyr/ops/detectors/temporal_pat... | prototype | generated |
| 141 | src/zephyr/ops/detectors/trace_causal_bridge.py | src/zephyr/ops/detectors/trace_causal... | prototype | generated |
| 142 | src/zephyr/ops/detectors/traffic_replay_validator.py | src/zephyr/ops/detectors/traffic_repl... | prototype | generated |
| 143 | src/zephyr/ops/detectors/trend_cycle_separator.py | src/zephyr/ops/detectors/trend_cycle_... | prototype | generated |
| 144 | src/zephyr/ops/detectors/version_migrator.py | src/zephyr/ops/detectors/version_migr... | prototype | generated |
| 145 | src/zephyr/ops/diagnosers/__init__.py | src/zephyr/ops/diagnosers/__init__.py | prototype | generated |
| 146 | src/zephyr/ops/diagnosers/_cognitive.py | src/zephyr/ops/diagnosers/_cognitive.py | prototype | generated |
| 147 | src/zephyr/ops/diagnosers/_diagnosis.py | src/zephyr/ops/diagnosers/_diagnosis.py | prototype | generated |
| 148 | src/zephyr/ops/diagnosers/_health.py | src/zephyr/ops/diagnosers/_health.py | prototype | generated |
| 149 | src/zephyr/ops/diagnosers/_reliability.py | src/zephyr/ops/diagnosers/_reliabilit... | prototype | generated |
| 150 | src/zephyr/ops/diagnosers/action_composition_health_monit... | src/zephyr/ops/diagnosers/action_comp... | prototype | generated |
| 151 | src/zephyr/ops/diagnosers/adaptive_param_tuning.py | src/zephyr/ops/diagnosers/adaptive_pa... | prototype | generated |
| 152 | src/zephyr/ops/diagnosers/amplification_guard.py | src/zephyr/ops/diagnosers/amplificati... | prototype | generated |
| 153 | src/zephyr/ops/diagnosers/api_dependency_metrics.py | src/zephyr/ops/diagnosers/api_depende... | prototype | generated |
| 154 | src/zephyr/ops/diagnosers/auto_diagnosis.py | src/zephyr/ops/diagnosers/auto_diagno... | prototype | generated |
| 155 | src/zephyr/ops/diagnosers/burn_rate_alerter.py | src/zephyr/ops/diagnosers/burn_rate_a... | prototype | generated |
| 156 | src/zephyr/ops/diagnosers/burnout_alarm.py | src/zephyr/ops/diagnosers/burnout_ala... | prototype | generated |
| 157 | src/zephyr/ops/diagnosers/capacity_aware_repair.py | src/zephyr/ops/diagnosers/capacity_aw... | prototype | generated |
| 158 | src/zephyr/ops/diagnosers/causal_inference_engine.py | src/zephyr/ops/diagnosers/causal_infe... | prototype | generated |
| 159 | src/zephyr/ops/diagnosers/cognitive_load.py | src/zephyr/ops/diagnosers/cognitive_l... | prototype | generated |
| 160 | src/zephyr/ops/diagnosers/cognitive_load_budget.py | src/zephyr/ops/diagnosers/cognitive_l... | prototype | generated |
| 161 | src/zephyr/ops/diagnosers/cold_start_conservative_mode.py | src/zephyr/ops/diagnosers/cold_start_... | prototype | generated |
| 162 | src/zephyr/ops/diagnosers/collaborative_learning.py | src/zephyr/ops/diagnosers/collaborati... | prototype | generated |
| 163 | src/zephyr/ops/diagnosers/confidence_decomposer.py | src/zephyr/ops/diagnosers/confidence_... | prototype | generated |
| 164 | src/zephyr/ops/diagnosers/context_truncation.py | src/zephyr/ops/diagnosers/context_tru... | prototype | generated |
| 165 | src/zephyr/ops/diagnosers/context_window_pressure_manager.py | src/zephyr/ops/diagnosers/context_win... | prototype | generated |
| 166 | src/zephyr/ops/diagnosers/counterfactual.py | src/zephyr/ops/diagnosers/counterfact... | prototype | generated |
| 167 | src/zephyr/ops/diagnosers/cross_guard_conflict_detector.py | src/zephyr/ops/diagnosers/cross_guard... | prototype | generated |
| 168 | src/zephyr/ops/diagnosers/cross_session_consistency_valid... | src/zephyr/ops/diagnosers/cross_sessi... | prototype | generated |
| 169 | src/zephyr/ops/diagnosers/data_volume_growth_monitor.py | src/zephyr/ops/diagnosers/data_volume... | prototype | generated |
| 170 | src/zephyr/ops/diagnosers/diagnosis_engine.py | src/zephyr/ops/diagnosers/diagnosis_e... | prototype | generated |
| 171 | src/zephyr/ops/diagnosers/diagnosis_kpi.py | src/zephyr/ops/diagnosers/diagnosis_k... | prototype | generated |
| 172 | src/zephyr/ops/diagnosers/dr_resilience_metrics.py | src/zephyr/ops/diagnosers/dr_resilien... | prototype | generated |
| 173 | src/zephyr/ops/diagnosers/e2e_integration_health.py | src/zephyr/ops/diagnosers/e2e_integra... | prototype | generated |
| 174 | src/zephyr/ops/diagnosers/feedback_delay_compensator.py | src/zephyr/ops/diagnosers/feedback_de... | prototype | generated |
| 175 | src/zephyr/ops/diagnosers/fle_dogfood_monitor.py | src/zephyr/ops/diagnosers/fle_dogfood... | prototype | generated |
| 176 | src/zephyr/ops/diagnosers/fle_self_slo_metrics.py | src/zephyr/ops/diagnosers/fle_self_sl... | prototype | generated |
| 177 | src/zephyr/ops/diagnosers/gamification.py | src/zephyr/ops/diagnosers/gamificatio... | prototype | generated |
| 178 | src/zephyr/ops/diagnosers/global_health_map.py | src/zephyr/ops/diagnosers/global_heal... | prototype | generated |
| 179 | src/zephyr/ops/diagnosers/guard_interaction_topology_mapp... | src/zephyr/ops/diagnosers/guard_inter... | prototype | generated |
| 180 | src/zephyr/ops/diagnosers/guard_self_consistency_auditor.py | src/zephyr/ops/diagnosers/guard_self_... | prototype | generated |
| 181 | src/zephyr/ops/diagnosers/human_anomaly_flood_detector.py | src/zephyr/ops/diagnosers/human_anoma... | prototype | generated |
| 182 | src/zephyr/ops/diagnosers/impact_predictor.py | src/zephyr/ops/diagnosers/impact_pred... | prototype | generated |
| 183 | src/zephyr/ops/diagnosers/incident_knowledge_injector.py | src/zephyr/ops/diagnosers/incident_kn... | prototype | generated |
| 184 | src/zephyr/ops/diagnosers/interactive_diagnosis.py | src/zephyr/ops/diagnosers/interactive... | prototype | generated |
| 185 | src/zephyr/ops/diagnosers/knowledge_bus_factor_monitor.py | src/zephyr/ops/diagnosers/knowledge_b... | prototype | generated |
| 186 | src/zephyr/ops/diagnosers/knowledge_market.py | src/zephyr/ops/diagnosers/knowledge_m... | prototype | generated |
| 187 | src/zephyr/ops/diagnosers/latency_slo.py | src/zephyr/ops/diagnosers/latency_slo.py | prototype | generated |
| 188 | src/zephyr/ops/diagnosers/llm_provider_integrity.py | src/zephyr/ops/diagnosers/llm_provide... | prototype | generated |
| 189 | src/zephyr/ops/diagnosers/llm_quality_regression.py | src/zephyr/ops/diagnosers/llm_quality... | prototype | generated |
| 190 | src/zephyr/ops/diagnosers/memory_self_check.py | src/zephyr/ops/diagnosers/memory_self... | prototype | generated |
| 191 | src/zephyr/ops/diagnosers/meta_guard_latency_budget.py | src/zephyr/ops/diagnosers/meta_guard_... | prototype | generated |
| 192 | src/zephyr/ops/diagnosers/model_health.py | src/zephyr/ops/diagnosers/model_healt... | prototype | generated |
| 193 | src/zephyr/ops/diagnosers/model_rotation.py | src/zephyr/ops/diagnosers/model_rotat... | prototype | generated |
| 194 | src/zephyr/ops/diagnosers/model_rotation_v2.py | src/zephyr/ops/diagnosers/model_rotat... | prototype | generated |
| 195 | src/zephyr/ops/diagnosers/model_version_semantic_drift.py | src/zephyr/ops/diagnosers/model_versi... | prototype | generated |
| 196 | src/zephyr/ops/diagnosers/mtti_tracker.py | src/zephyr/ops/diagnosers/mtti_tracke... | prototype | generated |
| 197 | src/zephyr/ops/diagnosers/nonstationary_effectiveness.py | src/zephyr/ops/diagnosers/nonstationa... | prototype | generated |
| 198 | src/zephyr/ops/diagnosers/numerical_stability_guard.py | src/zephyr/ops/diagnosers/numerical_s... | prototype | generated |
| 199 | src/zephyr/ops/diagnosers/operational_seasonality.py | src/zephyr/ops/diagnosers/operational... | prototype | generated |
| 200 | src/zephyr/ops/diagnosers/prompt_fingerprint.py | src/zephyr/ops/diagnosers/prompt_fing... | prototype | generated |

> (仅显示前 200 个模块，共 423 个)

### 未分类 / Unclassified (22 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | F20-unified-monitor/ | F20-unified-monitor/ | design | planned |
| 2 | F4-budget-engine/ | F4-budget-engine/ | design | stable |
| 3 | scripts/ops/auto_fix_cron.py | scripts/ops/auto_fix_cron.py | production | generated |
| 4 | scripts/ops/upgrade_headers_to_14fields.py | scripts/ops/upgrade_headers_to_14fiel... | production | generated |
| 5 | src/zephyr/ops/gates/safety_gate_l28_l29.py | src/zephyr/ops/gates/safety_gate_l28_... | production | generated |
| 6 | src/zephyr/ops/gates/safety_gate_l36_l37.py | src/zephyr/ops/gates/safety_gate_l36_... | production | generated |
| 7 | src/zephyr/ops/gates/safety_gate_l38_l39.py | src/zephyr/ops/gates/safety_gate_l38_... | production | generated |
| 8 | src/zephyr/ops/gates/safety_gate_l40_l41.py | src/zephyr/ops/gates/safety_gate_l40_... | production | generated |
| 9 | src/zephyr/ops/gates/safety_gate_l42_l43.py | src/zephyr/ops/gates/safety_gate_l42_... | production | generated |
| 10 | src/zephyr/ops/gates/safety_gate_l44_l45.py | src/zephyr/ops/gates/safety_gate_l44_... | production | generated |
| 11 | src/zephyr/ops/gates/safety_gate_l46_l47.py | src/zephyr/ops/gates/safety_gate_l46_... | production | generated |
| 12 | src/zephyr/ops/gates/safety_gate_l48_l49.py | src/zephyr/ops/gates/safety_gate_l48_... | production | generated |
| 13 | src/zephyr/ops/gates/safety_gate_l50_l51.py | src/zephyr/ops/gates/safety_gate_l50_... | production | generated |
| 14 | src/zephyr/ops/gates/safety_gate_l52_l53.py | src/zephyr/ops/gates/safety_gate_l52_... | production | generated |
| 15 | src/zephyr/ops/gates/safety_gate_l54_l55.py | src/zephyr/ops/gates/safety_gate_l54_... | production | generated |
| 16 | src/zephyr/ops/gates/safety_gate_l56_l57.py | src/zephyr/ops/gates/safety_gate_l56_... | production | generated |
| 17 | src/zephyr/ops/gates/safety_gate_l58_l59.py | src/zephyr/ops/gates/safety_gate_l58_... | production | generated |
| 18 | src/zephyr/ops/gates/safety_gate_l60_l61.py | src/zephyr/ops/gates/safety_gate_l60_... | production | generated |
| 19 | src/zephyr/ops/gates/safety_gate_l62_l63.py | src/zephyr/ops/gates/safety_gate_l62_... | production | generated |
| 20 | src/zephyr/ops/gates/safety_gate_l64_l65.py | src/zephyr/ops/gates/safety_gate_l64_... | production | generated |
| 21 | src/zephyr/ops/gates/safety_gate_l66_l67.py | src/zephyr/ops/gates/safety_gate_l66_... | production | generated |
| 22 | src/zephyr/ops/observability/notifier.py | src/zephyr/ops/observability/notifier.py | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 327 条 / 327 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 327 条 / 327 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 4                               │
│   [config_depends]: 183 条 / edges                               │
│   [import_depends]: 131 条 / edges                               │
│   [runtime]: 7 条 / edges                                        │
│   [test_depends]: 6 条 / edges                                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [config_depends] (183 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   benchmark_integrity.py → __init__.py                           │
│   provenance_tracker.py → __init__.py                            │
│   performance_baseline.py → __init__.py                          │
│   config.py → __init__.py                                        │
│   exceptions.py → __init__.py                                    │
│   error_budget.py → __init__.py                                  │
│   eval_harness.py → __init__.py                                  │
│   fitness_functions.py → __init__.py                             │
│   protocols.py → __init__.py                                     │
│   slo_manager.py → __init__.py                                   │
│   template.py → __init__.py                                      │
│   _gen_inherited.py → __init__.py                                │
│   action_side_effect_cumula... → __init__.py                     │
│   action_efficacy_decay_det... → __init__.py                     │
│   action_interaction_detect... → __init__.py                     │
│   agent_trajectory_anomaly_... → __init__.py                     │
│   blast_radius.py → __init__.py                                  │
│   anomaly_clustering.py → __init__.py                            │
│   blast_radius_budget.py → __init__.py                           │
│   autoscale_remediation.py → __init__.py                         │
│   alert_desensitization_cur... → __init__.py                     │
│   capacity_forecast.py → __init__.py                             │
│   chaos_engineering.py → __init__.py                             │
│   cross_system_correlator.py → __init__.py                       │
│   config_drift.py → __init__.py                                  │
│   cross_signal_validator.py → __init__.py                        │
│   concept_drift.py → __init__.py                                 │
│   context_window_contaminat... → __init__.py                     │
│   decision_provenance.py → __init__.py                           │
│   diminishing_returns_detec... → __init__.py                     │
│   dependency_freshness_moni... → __init__.py                     │
│   ebpf_monitor.py → __init__.py                                  │
│   ensemble_detector.py → __init__.py                             │
│   emergent_behavior_detecto... → __init__.py                     │
│   external_validation_check... → __init__.py                     │
│   ensemble_drift.py → __init__.py                                │
│   flapping_detector.py → __init__.py                             │
│   external_health.py → __init__.py                               │
│   gradual_poisoning_detecto... → __init__.py                     │
│   flag_lifecycle.py → __init__.py                                │
│   fle_performance_regressio... → __init__.py                     │
│   heisenbug_detector.py → __init__.py                            │
│   guard_cascade_detector.py → __init__.py                        │
│   infinite_loop_detector.py → __init__.py                        │
│   log_anomaly.py → __init__.py                                   │
│   guard_oscillation_detecto... → __init__.py                     │
│   intermittent_failure_patt... → __init__.py                     │
│   metric_cardinality_guard.py → __init__.py                      │
│   maintenance_coordinator.py → __init__.py                       │
│   ...还有 134 条 / 134 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[import_depends]** (131 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (7 条 / edges) — 已达显示上限，省略 / limit reached

**[test_depends]** (6 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 327 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `16_d_ops_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
