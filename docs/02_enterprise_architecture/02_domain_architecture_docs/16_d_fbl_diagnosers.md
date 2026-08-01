---
doc_type: architecture_view
title: D_FBL_DIAGNOSERS 反馈诊断器架构文档
version: "1.0"
status: active
date: 2026-08-01
owner: auto-generator
ttl: permanent
---

# 16_d_fbl_diagnosers / 反馈诊断器域 / Feedback Diagnosers

> **功能简介 / Overview**: 反馈诊断器，负责异常根因诊断、模型健康监控、可靠性诊断和上下文窗口压力管理

> **文档作用 / Purpose**: 展示 反馈诊断器（D_FBL_DIAGNOSERS）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/16_d_fbl_diagnosers.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 16 | Number | 16 |
| 域ID | D_FBL_DIAGNOSERS | Domain ID | D_FBL_DIAGNOSERS |
| 域名称 | 反馈诊断器 | Domain Name | Feedback Diagnosers |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 76 | Module Count | 76 |
| 域内依赖 | 6 | Internal Dependencies | 6 |
| 跨域入边 | 7 | Cross-domain Incoming | 7 |
| 跨域出边 | 1 | Cross-domain Outgoing | 1 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 76 | Production Modules | 76 |
| 容量 | 76/150 (正常) | Capacity | 76/150 (正常) |
| 描述 | 反馈诊断器，负责异常根因诊断、模型健康监控、可靠性诊断和上下文窗口压力管理 | Description | 反馈诊断器，负责异常根因诊断、模型健康监控、可靠性诊断和上下文窗口压力管理 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 76 个模块（生产态 76 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_feedback_loop_diagnosers_init_py["(生产态 / production) feedback-loop.diagnosers — GOV-DOC-018: 71个叶子模块拆分为4个逻辑子包(cognit...<br/>文件: diagnosers/__init__.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py["(生产态 / production) Adaptive Parameter Tuning — v0.37.0 R452<br/>文件: cognitive/adaptive_param_tuning.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py["(生产态 / production) Cognitive Load Estimator — v0.6.0 R68<br/>文件: cognitive/cognitive_load.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py["(生产态 / production) Cognitive Load Budget — v0.16.0 R223<br/>文件: cognitive/cognitive_load_budget.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py["(生产态 / production) Collaborative Learning — v0.7.0 R82<br/>文件: cognitive/collaborative_learning.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py["(生产态 / production) Confidence Decomposer — v0.7.0 R83<br/>文件: cognitive/confidence_decomposer.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py["(生产态 / production) Gamification — v0.8.0 R101<br/>文件: cognitive/gamification.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py["(生产态 / production) R516: MetaGuardLatencyBudget<br/>文件: cognitive/meta_guard_latency_budget.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py["(生产态 / production) Socratic Questions — v0.7.0 R81<br/>文件: cognitive/socratic_questions.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py["(生产态 / production) Tone Adapter — v0.9.0 R127<br/>文件: cognitive/tone_adapter.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py["(生产态 / production) Tone Adapter v2 — v0.10.0 R141<br/>文件: cognitive/tone_adapter_v2.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py["(生产态 / production) Auto Diagnosis — v0.3.0 R16<br/>文件: diagnosis/auto_diagnosis.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py["(生产态 / production) Causal Inference Engine — v0.3.0 R5-R7<br/>文件: diagnosis/causal_inference_engine.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py["(生产态 / production) Counterfactual Engine — v0.6.0 R60<br/>文件: diagnosis/counterfactual.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py["(生产态 / production) diagnosis/diagnosis_engine.py<br/>文件: diagnosis/diagnosis_engine.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py["(生产态 / production) Diagnosis KPI — v0.9.0 R116<br/>文件: diagnosis/diagnosis_kpi.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py["(生产态 / production) Impact Predictor — v0.9.0 R121<br/>文件: diagnosis/impact_predictor.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py["(生产态 / production) R504: IncidentKnowledgeInjector<br/>文件: diagnosis/incident_knowledge_injector.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py["(生产态 / production) Interactive Diagnosis — v0.7.0 R80<br/>文件: diagnosis/interactive_diagnosis.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py["(生产态 / production) Knowledge Bus Factor Monitor — v0.38.0 R481<br/>文件: diagnosis/knowledge_bus_factor_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py["(生产态 / production) Knowledge Market — v0.9.0 R126<br/>文件: diagnosis/knowledge_market.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py["(生产态 / production) MTTI Tracker — v0.16.0 R221<br/>文件: diagnosis/mtti_tracker.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py["(生产态 / production) Nonstationary Effectiveness — v0.37.0 R455<br/>文件: diagnosis/nonstationary_effectiveness.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py["(生产态 / production) Statistical Hygiene Auditor — v0.38.0 R476<br/>文件: diagnosis/statistical_hygiene_auditor.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py["(生产态 / production) Vertical Self Assessment — v0.10.0 R137<br/>文件: diagnosis/vertical_self_assessment.py"]
    src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py["(生产态 / production) R511: ActionCompositionHealthMonitor<br/>文件: health/action_composition_health_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py["(生产态 / production) DR Resilience Metrics — v0.17.0+ R231-R236<br/>文件: health/dr_resilience_metrics.py"]
    src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py["(生产态 / production) E2E Integration Health Monitor — v0.39.0 R489<br/>文件: health/e2e_integration_health.py"]
    src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py["(生产态 / production) FLE Dogfood Monitor — v0.38.0 R480<br/>文件: health/fle_dogfood_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py["(生产态 / production) FLE Self SLO Metrics — v0.17.0+ R249-R254<br/>文件: health/fle_self_slo_metrics.py"]
    src_zephyr_feedback_loop_diagnosers_health_global_health_map_py["(生产态 / production) Global Health Map — v0.8.0 R103<br/>文件: health/global_health_map.py"]
    src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py["(生产态 / production) Memory Self Check — v0.8.0 R105<br/>文件: health/memory_self_check.py"]
    src_zephyr_feedback_loop_diagnosers_health_model_health_py["(生产态 / production) Model Health Monitor — v0.5.0 R40<br/>文件: health/model_health.py"]
    src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py["(生产态 / production) Self Benchmark — v0.9.0 R115<br/>文件: health/self_benchmark.py"]
    src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py["(生产态 / production) Self-Bottleneck Detector — v0.38.0 R479<br/>文件: health/self_bottleneck_detector.py"]
    src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py["(生产态 / production) Self Health Monitor — v0.4.0 R29<br/>文件: health/self_health_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py["(生产态 / production) Self LLM Observability — v0.12.0 R160<br/>文件: health/self_llm_observability.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py["(生产态 / production) Amplification Guard — v0.10.0 R134<br/>文件: reliability/amplification_guard.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py["(生产态 / production) API Dependency Metrics — v0.17.0+ R237-R242<br/>文件: reliability/api_dependency_metrics.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py["(生产态 / production) Burn Rate Alerter — v0.14.0 R200<br/>文件: reliability/burn_rate_alerter.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py["(生产态 / production) Burnout Alarm — v0.8.0 R100<br/>文件: reliability/burnout_alarm.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py["(生产态 / production) Capacity Aware Repair — v0.9.0 R120<br/>文件: reliability/capacity_aware_repair.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py["(生产态 / production) R509: ColdStartConservativeMode<br/>文件: reliability/cold_start_conservative_mode.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py["(生产态 / production) Context Truncation Detector — v0.9.0 R122<br/>文件: reliability/context_truncation.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py["(生产态 / production) R506: ContextWindowPressureManager<br/>文件: reliability/context_window_pressure_manager.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py["(生产态 / production) R513: CrossGuardConflictDetector<br/>文件: reliability/cross_guard_conflict_detector.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py["(生产态 / production) R510: CrossSessionConsistencyValidator<br/>文件: reliability/cross_session_consistency_validator.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py["(生产态 / production) Data Volume Growth Monitor — v0.39.0 R492<br/>文件: reliability/data_volume_growth_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py["(生产态 / production) Feedback Delay Compensator — v0.38.0 R477<br/>文件: reliability/feedback_delay_compensator.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py["(生产态 / production) R518: GuardInteractionTopologyMapper<br/>文件: reliability/guard_interaction_topology_mapper.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py["(生产态 / production) R512: GuardSelfConsistencyAuditor<br/>文件: reliability/guard_self_consistency_auditor.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py["(生产态 / production) Human Anomaly Flood Detector — v0.40.0 R500<br/>文件: reliability/human_anomaly_flood_detector.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py["(生产态 / production) Latency SLO Monitor — v0.14.0 R192<br/>文件: reliability/latency_slo.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py["(生产态 / production) LLM Provider Integrity — v0.15.0 R217<br/>文件: reliability/llm_provider_integrity.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py["(生产态 / production) LLM Quality Regression — v0.12.0 R161<br/>文件: reliability/llm_quality_regression.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py["(生产态 / production) Model Rotation — v0.9.0 R125<br/>文件: reliability/model_rotation.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py["(生产态 / production) Model Rotation v2 — v0.10.0 R140<br/>文件: reliability/model_rotation_v2.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py["(生产态 / production) Model Version Semantic Drift Monitor — v0.39.0 R493<br/>文件: reliability/model_version_semantic_drift.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py["(生产态 / production) Numerical Stability Guard — v0.38.0 R475<br/>文件: reliability/numerical_stability_guard.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py["(生产态 / production) Operational Seasonality — v0.16.0 R228<br/>文件: reliability/operational_seasonality.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py["(生产态 / production) Prompt Fingerprint — v0.3.0 R14<br/>文件: reliability/prompt_fingerprint.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py["(生产态 / production) Prompt Sanitizer — v0.10.0 R133<br/>文件: reliability/prompt_sanitizer.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py["(生产态 / production) Recovery Time Statistics — v0.37.0 R454<br/>文件: reliability/recovery_time_stats.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py["(生产态 / production) Regime Gain Scheduling — v0.37.0 R453<br/>文件: reliability/regime_gain_scheduling.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py["(生产态 / production) Retirement Planner — v0.10.0 R139<br/>文件: reliability/retirement_planner.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py["(生产态 / production) SLO Capacity Metrics — v0.17.0+ R243-R248<br/>文件: reliability/slo_capacity_metrics.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py["(生产态 / production) R527: SystemEntropyMonitor<br/>文件: reliability/system_entropy_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py["(生产态 / production) Temporal Integrity Guard — v0.38.0 R478<br/>文件: reliability/temporal_integrity_guard.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py["(生产态 / production) Timezone Semantic Reasoner — v0.37.0 R456<br/>文件: reliability/timezone_semantic_reasoner.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py["(生产态 / production) Toil Quantification — v0.37.0 R457<br/>文件: reliability/toil_quantification.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py["(生产态 / production) Value Added Baseline — v0.10.0 R138<br/>文件: reliability/value_added_baseline.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py["(生产态 / production) Zombie FLE Detector — v0.16.0 R222<br/>文件: reliability/zombie_fle_detector.py"]
    src_zephyr_feedback_loop_diagnosers_init_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py
    src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py
    src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py
    src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py
    src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py
    src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py
    src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py ~~~ src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py
    src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py
    src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py ~~~ src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py
    src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py ~~~ src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py
    src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py
    src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py ~~~ src_zephyr_feedback_loop_diagnosers_health_global_health_map_py
    src_zephyr_feedback_loop_diagnosers_health_global_health_map_py ~~~ src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py
    src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py ~~~ src_zephyr_feedback_loop_diagnosers_health_model_health_py
    src_zephyr_feedback_loop_diagnosers_health_model_health_py ~~~ src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py
    src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py ~~~ src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py
    src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py ~~~ src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py
    src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py
    src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py
    src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py
    src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py
    src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py
    src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py
    src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py
    src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py
    src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py
    src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py
    src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py
    src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py
    src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py
    src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py
    src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py
    src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py
    src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py
    src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py
    src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py
    src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py
    src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py
    src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py
    src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py
    src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py
    src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py
    src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py
    src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py
    src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py
    src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py
    src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py
    src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py
    src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py
    src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py
    src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py
    src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py
    src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py
    src_zephyr_feedback_loop_diagnosers_cognitive_init_py["(生产态 / production) cognitive/__init__.py<br/>文件: cognitive/__init__.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_init_py["(生产态 / production) diagnosis/__init__.py<br/>文件: diagnosis/__init__.py"]
    src_zephyr_feedback_loop_diagnosers_health_init_py["(生产态 / production) health/__init__.py<br/>文件: health/__init__.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_init_py["(生产态 / production) reliability/__init__.py<br/>文件: reliability/__init__.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_init_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_init_py ~~~ src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_init_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py -->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py -->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py -->|导入依赖 / import_depends| D_SHARED
    D_FEEDBACK_LOOP["(生产态 / production) 反馈循环引擎 / Feedback Loop Engine<br/>反馈循环引擎，负责系统自我改进闭环：异常检测、根因诊断、自动修复和自我进化<br/>跨域节点 / cross-domain"]
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_diagnosers_init_py,src_zephyr_feedback_loop_diagnosers_cognitive_init_py,src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py,src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py,src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py,src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py,src_zephyr_feedback_loop_diagnosers_diagnosis_init_py,src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py,src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py,src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py,src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py,src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py,src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py,src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py,src_zephyr_feedback_loop_diagnosers_health_init_py,src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py,src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py,src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py,src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py,src_zephyr_feedback_loop_diagnosers_health_global_health_map_py,src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py,src_zephyr_feedback_loop_diagnosers_health_model_health_py,src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py,src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py,src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py,src_zephyr_feedback_loop_diagnosers_reliability_init_py,src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py,src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py,src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py,src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py,src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py,src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py,src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py,src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py,src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py,src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py,src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py,src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py,src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py,src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py,src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py,src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py,src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py,src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py,src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py production
    class D_SHARED,D_FEEDBACK_LOOP external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 76 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_feedback_loop_diagnosers_init_py["(生产态 / production) feedback-loop.diagnosers — GOV-DOC-018: 71个叶子模块拆分为4个逻辑子包(cognit...<br/>文件: diagnosers/__init__.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py["(生产态 / production) Adaptive Parameter Tuning — v0.37.0 R452<br/>文件: cognitive/adaptive_param_tuning.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py["(生产态 / production) Cognitive Load Estimator — v0.6.0 R68<br/>文件: cognitive/cognitive_load.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py["(生产态 / production) Cognitive Load Budget — v0.16.0 R223<br/>文件: cognitive/cognitive_load_budget.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py["(生产态 / production) Collaborative Learning — v0.7.0 R82<br/>文件: cognitive/collaborative_learning.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py["(生产态 / production) Confidence Decomposer — v0.7.0 R83<br/>文件: cognitive/confidence_decomposer.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py["(生产态 / production) Gamification — v0.8.0 R101<br/>文件: cognitive/gamification.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py["(生产态 / production) R516: MetaGuardLatencyBudget<br/>文件: cognitive/meta_guard_latency_budget.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py["(生产态 / production) Socratic Questions — v0.7.0 R81<br/>文件: cognitive/socratic_questions.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py["(生产态 / production) Tone Adapter — v0.9.0 R127<br/>文件: cognitive/tone_adapter.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py["(生产态 / production) Tone Adapter v2 — v0.10.0 R141<br/>文件: cognitive/tone_adapter_v2.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py["(生产态 / production) Auto Diagnosis — v0.3.0 R16<br/>文件: diagnosis/auto_diagnosis.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py["(生产态 / production) Causal Inference Engine — v0.3.0 R5-R7<br/>文件: diagnosis/causal_inference_engine.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py["(生产态 / production) Counterfactual Engine — v0.6.0 R60<br/>文件: diagnosis/counterfactual.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py["(生产态 / production) diagnosis/diagnosis_engine.py<br/>文件: diagnosis/diagnosis_engine.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py["(生产态 / production) Diagnosis KPI — v0.9.0 R116<br/>文件: diagnosis/diagnosis_kpi.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py["(生产态 / production) Impact Predictor — v0.9.0 R121<br/>文件: diagnosis/impact_predictor.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py["(生产态 / production) R504: IncidentKnowledgeInjector<br/>文件: diagnosis/incident_knowledge_injector.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py["(生产态 / production) Interactive Diagnosis — v0.7.0 R80<br/>文件: diagnosis/interactive_diagnosis.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py["(生产态 / production) Knowledge Bus Factor Monitor — v0.38.0 R481<br/>文件: diagnosis/knowledge_bus_factor_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py["(生产态 / production) Knowledge Market — v0.9.0 R126<br/>文件: diagnosis/knowledge_market.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py["(生产态 / production) MTTI Tracker — v0.16.0 R221<br/>文件: diagnosis/mtti_tracker.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py["(生产态 / production) Nonstationary Effectiveness — v0.37.0 R455<br/>文件: diagnosis/nonstationary_effectiveness.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py["(生产态 / production) Statistical Hygiene Auditor — v0.38.0 R476<br/>文件: diagnosis/statistical_hygiene_auditor.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py["(生产态 / production) Vertical Self Assessment — v0.10.0 R137<br/>文件: diagnosis/vertical_self_assessment.py"]
    src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py["(生产态 / production) R511: ActionCompositionHealthMonitor<br/>文件: health/action_composition_health_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py["(生产态 / production) DR Resilience Metrics — v0.17.0+ R231-R236<br/>文件: health/dr_resilience_metrics.py"]
    src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py["(生产态 / production) E2E Integration Health Monitor — v0.39.0 R489<br/>文件: health/e2e_integration_health.py"]
    src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py["(生产态 / production) FLE Dogfood Monitor — v0.38.0 R480<br/>文件: health/fle_dogfood_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py["(生产态 / production) FLE Self SLO Metrics — v0.17.0+ R249-R254<br/>文件: health/fle_self_slo_metrics.py"]
    src_zephyr_feedback_loop_diagnosers_health_global_health_map_py["(生产态 / production) Global Health Map — v0.8.0 R103<br/>文件: health/global_health_map.py"]
    src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py["(生产态 / production) Memory Self Check — v0.8.0 R105<br/>文件: health/memory_self_check.py"]
    src_zephyr_feedback_loop_diagnosers_health_model_health_py["(生产态 / production) Model Health Monitor — v0.5.0 R40<br/>文件: health/model_health.py"]
    src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py["(生产态 / production) Self Benchmark — v0.9.0 R115<br/>文件: health/self_benchmark.py"]
    src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py["(生产态 / production) Self-Bottleneck Detector — v0.38.0 R479<br/>文件: health/self_bottleneck_detector.py"]
    src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py["(生产态 / production) Self Health Monitor — v0.4.0 R29<br/>文件: health/self_health_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py["(生产态 / production) Self LLM Observability — v0.12.0 R160<br/>文件: health/self_llm_observability.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py["(生产态 / production) Amplification Guard — v0.10.0 R134<br/>文件: reliability/amplification_guard.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py["(生产态 / production) API Dependency Metrics — v0.17.0+ R237-R242<br/>文件: reliability/api_dependency_metrics.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py["(生产态 / production) Burn Rate Alerter — v0.14.0 R200<br/>文件: reliability/burn_rate_alerter.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py["(生产态 / production) Burnout Alarm — v0.8.0 R100<br/>文件: reliability/burnout_alarm.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py["(生产态 / production) Capacity Aware Repair — v0.9.0 R120<br/>文件: reliability/capacity_aware_repair.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py["(生产态 / production) R509: ColdStartConservativeMode<br/>文件: reliability/cold_start_conservative_mode.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py["(生产态 / production) Context Truncation Detector — v0.9.0 R122<br/>文件: reliability/context_truncation.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py["(生产态 / production) R506: ContextWindowPressureManager<br/>文件: reliability/context_window_pressure_manager.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py["(生产态 / production) R513: CrossGuardConflictDetector<br/>文件: reliability/cross_guard_conflict_detector.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py["(生产态 / production) R510: CrossSessionConsistencyValidator<br/>文件: reliability/cross_session_consistency_validator.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py["(生产态 / production) Data Volume Growth Monitor — v0.39.0 R492<br/>文件: reliability/data_volume_growth_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py["(生产态 / production) Feedback Delay Compensator — v0.38.0 R477<br/>文件: reliability/feedback_delay_compensator.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py["(生产态 / production) R518: GuardInteractionTopologyMapper<br/>文件: reliability/guard_interaction_topology_mapper.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py["(生产态 / production) R512: GuardSelfConsistencyAuditor<br/>文件: reliability/guard_self_consistency_auditor.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py["(生产态 / production) Human Anomaly Flood Detector — v0.40.0 R500<br/>文件: reliability/human_anomaly_flood_detector.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py["(生产态 / production) Latency SLO Monitor — v0.14.0 R192<br/>文件: reliability/latency_slo.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py["(生产态 / production) LLM Provider Integrity — v0.15.0 R217<br/>文件: reliability/llm_provider_integrity.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py["(生产态 / production) LLM Quality Regression — v0.12.0 R161<br/>文件: reliability/llm_quality_regression.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py["(生产态 / production) Model Rotation — v0.9.0 R125<br/>文件: reliability/model_rotation.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py["(生产态 / production) Model Rotation v2 — v0.10.0 R140<br/>文件: reliability/model_rotation_v2.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py["(生产态 / production) Model Version Semantic Drift Monitor — v0.39.0 R493<br/>文件: reliability/model_version_semantic_drift.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py["(生产态 / production) Numerical Stability Guard — v0.38.0 R475<br/>文件: reliability/numerical_stability_guard.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py["(生产态 / production) Operational Seasonality — v0.16.0 R228<br/>文件: reliability/operational_seasonality.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py["(生产态 / production) Prompt Fingerprint — v0.3.0 R14<br/>文件: reliability/prompt_fingerprint.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py["(生产态 / production) Prompt Sanitizer — v0.10.0 R133<br/>文件: reliability/prompt_sanitizer.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py["(生产态 / production) Recovery Time Statistics — v0.37.0 R454<br/>文件: reliability/recovery_time_stats.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py["(生产态 / production) Regime Gain Scheduling — v0.37.0 R453<br/>文件: reliability/regime_gain_scheduling.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py["(生产态 / production) Retirement Planner — v0.10.0 R139<br/>文件: reliability/retirement_planner.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py["(生产态 / production) SLO Capacity Metrics — v0.17.0+ R243-R248<br/>文件: reliability/slo_capacity_metrics.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py["(生产态 / production) R527: SystemEntropyMonitor<br/>文件: reliability/system_entropy_monitor.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py["(生产态 / production) Temporal Integrity Guard — v0.38.0 R478<br/>文件: reliability/temporal_integrity_guard.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py["(生产态 / production) Timezone Semantic Reasoner — v0.37.0 R456<br/>文件: reliability/timezone_semantic_reasoner.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py["(生产态 / production) Toil Quantification — v0.37.0 R457<br/>文件: reliability/toil_quantification.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py["(生产态 / production) Value Added Baseline — v0.10.0 R138<br/>文件: reliability/value_added_baseline.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py["(生产态 / production) Zombie FLE Detector — v0.16.0 R222<br/>文件: reliability/zombie_fle_detector.py"]
    src_zephyr_feedback_loop_diagnosers_init_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py
    src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py
    src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py
    src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py
    src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py
    src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py
    src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py ~~~ src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py ~~~ src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py
    src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py
    src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py ~~~ src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py
    src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py ~~~ src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py
    src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py
    src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py ~~~ src_zephyr_feedback_loop_diagnosers_health_global_health_map_py
    src_zephyr_feedback_loop_diagnosers_health_global_health_map_py ~~~ src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py
    src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py ~~~ src_zephyr_feedback_loop_diagnosers_health_model_health_py
    src_zephyr_feedback_loop_diagnosers_health_model_health_py ~~~ src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py
    src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py ~~~ src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py
    src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py ~~~ src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py
    src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py
    src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py
    src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py
    src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py
    src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py
    src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py
    src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py
    src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py
    src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py
    src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py
    src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py
    src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py
    src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py
    src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py
    src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py
    src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py
    src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py
    src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py
    src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py
    src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py
    src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py
    src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py
    src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py
    src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py
    src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py
    src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py
    src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py
    src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py
    src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py
    src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py
    src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py
    src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py
    src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py
    src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py
    src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py
    src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py
    src_zephyr_feedback_loop_diagnosers_cognitive_init_py["(生产态 / production) cognitive/__init__.py<br/>文件: cognitive/__init__.py"]
    src_zephyr_feedback_loop_diagnosers_diagnosis_init_py["(生产态 / production) diagnosis/__init__.py<br/>文件: diagnosis/__init__.py"]
    src_zephyr_feedback_loop_diagnosers_health_init_py["(生产态 / production) health/__init__.py<br/>文件: health/__init__.py"]
    src_zephyr_feedback_loop_diagnosers_reliability_init_py["(生产态 / production) reliability/__init__.py<br/>文件: reliability/__init__.py"]
    src_zephyr_feedback_loop_diagnosers_cognitive_init_py ~~~ src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_init_py ~~~ src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_init_py ~~~ src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py -->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py -->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_diagnosers_init_py,src_zephyr_feedback_loop_diagnosers_cognitive_init_py,src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py,src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py,src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py,src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py,src_zephyr_feedback_loop_diagnosers_diagnosis_init_py,src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py,src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py,src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py,src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py,src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py,src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py,src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py,src_zephyr_feedback_loop_diagnosers_health_init_py,src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py,src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py,src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py,src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py,src_zephyr_feedback_loop_diagnosers_health_global_health_map_py,src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py,src_zephyr_feedback_loop_diagnosers_health_model_health_py,src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py,src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py,src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py,src_zephyr_feedback_loop_diagnosers_reliability_init_py,src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py,src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py,src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py,src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py,src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py,src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py,src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py,src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py,src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py,src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py,src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py,src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py,src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py,src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py,src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py,src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py,src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py,src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py,src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | Operational Seasonality — v0.16.0 R228 (reliability/oper... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_FEEDBACK_LOOP 反馈循环引擎: FLE 全链路调度器 —— collect->detect->diagnose->act->ver... | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶子模块拆分... | 导入依赖 / import_depends |
| 2 | D_FEEDBACK_LOOP 反馈循环引擎: FLE 全链路调度器 —— collect->detect->diagnose->act->ver... | → | diagnosis/diagnosis_engine.py | 导入依赖 / import_depends |
| 3 | D_FEEDBACK_LOOP 反馈循环引擎: feedback_loop/scheduler_act.py | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶子模块拆分... | 导入依赖 / import_depends |
| 4 | D_FEEDBACK_LOOP 反馈循环引擎: feedback_loop/scheduler_collect_detect.py | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶子模块拆分... | 导入依赖 / import_depends |
| 5 | D_FEEDBACK_LOOP 反馈循环引擎: feedback_loop/scheduler_health.py | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶子模块拆分... | 导入依赖 / import_depends |
| 6 | D_FEEDBACK_LOOP 反馈循环引擎: feedback_loop/scheduler_safety.py | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶子模块拆分... | 导入依赖 / import_depends |
| 7 | D_FEEDBACK_LOOP 反馈循环引擎: E2E Integration Test Pipeline — TASK-MOD-FEEDBACK_LOOP-0... | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶子模块拆分... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 2 个外部域直接连接（出边 1 条 + 入边 7 条 = 8 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_FBL_DIAGNOSERS["D_FBL_DIAGNOSERS<br/>反馈诊断器"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_FBL_DIAGNOSERS -->|1条 导入依赖 / import_depends| D_SHARED
    D_FEEDBACK_LOOP -->|7条 导入依赖 / import_depends| D_FBL_DIAGNOSERS
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
