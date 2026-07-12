---
doc_type: architecture_view
title: D_FEEDBACK_LOOP 反馈循环引擎架构文档
version: "1.0"
status: active
date: 2026-07-13
owner: auto-generator
ttl: permanent
---

# 12_d_feedback_loop / feedback_loop_engine / 反馈循环引擎 / Feedback Loop Engine

> **功能简介 / Overview**: 反馈循环引擎，负责系统自我改进闭环：异常检测、根因诊断、自动修复和自我进化

> **文档作用 / Purpose**: 展示 反馈循环引擎（D_FEEDBACK_LOOP）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-13 07:00:07
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 12 | Number | 12 |
| 域ID | D_FEEDBACK_LOOP | Domain ID | D_FEEDBACK_LOOP |
| 域名称 | 反馈循环引擎 | Domain Name | Feedback Loop Engine |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 358 | Module Count | 358 |
| 域内依赖 | 238 | Internal Dependencies | 238 |
| 跨域入边 | 233 | Cross-domain Incoming | 233 |
| 跨域出边 | 119 | Cross-domain Outgoing | 119 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 251 | Prototype Modules | 251 |
| 生产态模块 | 107 | Production Modules | 107 |
| 容量 | 107/150 (正常) | Capacity | 107/150 (正常) |
| 描述 | 反馈收集器(collectors) | Description | 反馈收集器(collectors) |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 358 个模块 / 358 modules）。

### L2 领域层 / Domain Layer (358 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/feedback_loop/__init__.py | Feedback Loop Engine — MOD-FEEDBACK_LOOP. | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 2 | src/zephyr/feedback_loop/_gen_inherited.py | _gen_inherited.py | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 3 | src/zephyr/feedback_loop/actors/action_selector.py | action_selector.py | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 4 | src/zephyr/feedback_loop/actors/agent_lifecycle.py | Agent Lifecycle Manager — v0.12.0 R159c | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 5 | src/zephyr/feedback_loop/actors/api_version_contract.py | API Version Contract — v0.14.0 R188 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 6 | src/zephyr/feedback_loop/actors/global_action_scheduler.py | Global Action Scheduler — v0.16.0 R226 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 7 | src/zephyr/feedback_loop/actors/incident_priority_triage_... | Incident Priority Triage Automator — v0.37.0 R463 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 8 | src/zephyr/feedback_loop/actors/intent_driven_ops.py | Intent-Driven Ops — v0.12.0 R159 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 9 | src/zephyr/feedback_loop/actors/multi_agent_orchestrator.py | Multi-Agent Orchestrator — v0.12.0 R159b | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 10 | src/zephyr/feedback_loop/actors/notification_personalizer.py | Notification Personalizer — v0.6.0 R67 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 11 | src/zephyr/feedback_loop/actors/owner_absence_escalation.py | Owner Absence Escalation — v0.37.0 R462 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 12 | src/zephyr/feedback_loop/actors/saga_compensator.py | Saga Compensator — v0.3.0 R19b | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 13 | src/zephyr/feedback_loop/actors/secondary_alert_channel.py | Secondary Alert Channel — v0.37.0 R461 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 14 | src/zephyr/feedback_loop/alert_dispatcher.py | FLE->Orc 告警分派器 — dispatch() 生产者 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 15 | src/zephyr/feedback_loop/auto_evolution.py | auto_evolution.py | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 16 | src/zephyr/feedback_loop/backpressure_bridge.py | FLE -> Pipeline 背压桥接（CTR-BP-001~003） | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 17 | src/zephyr/feedback_loop/collectors/calendar_adapter.py | Calendar Adapter — v0.8.0 R102b | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 18 | src/zephyr/feedback_loop/collectors/config_timeline.py | Config Timeline — v0.8.0 R99 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 19 | src/zephyr/feedback_loop/collectors/data_quality_validato... | Data Quality Validator — v0.9.0 R110 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 20 | src/zephyr/feedback_loop/collectors/feedback_collector.py | feedback_collector.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 21 | src/zephyr/feedback_loop/collectors/financial_stratificat... | Financial Stratification — v0.5.0 R50 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 22 | src/zephyr/feedback_loop/collectors/kb_provenance.py | KB Provenance — v0.10.0 R136 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 23 | src/zephyr/feedback_loop/collectors/knowledge_capture.py | Knowledge Capture — v0.4.0 R30 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 24 | src/zephyr/feedback_loop/collectors/knowledge_freshness.py | Knowledge Freshness — v0.5.0 R47 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 25 | src/zephyr/feedback_loop/collectors/knowledge_injection.py | Knowledge Injection — v0.8.0 R102 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 26 | src/zephyr/feedback_loop/collectors/knowledge_packaging.py | Knowledge Packaging — v0.9.0 R123 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 27 | src/zephyr/feedback_loop/collectors/known_unknown_registr... | Known-Unknown Registry — v0.16.0 R229 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 28 | src/zephyr/feedback_loop/collectors/llm_cost_accounting.py | LLM Cost Accounting — v0.4.0 R35 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 29 | src/zephyr/feedback_loop/collectors/market_calendar.py | Market Calendar — v0.5.0 R48 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 30 | src/zephyr/feedback_loop/collectors/market_event_integrat... | Market Event Integrator — v0.14.0 R197 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 31 | src/zephyr/feedback_loop/collectors/metrics_collector.py | metrics_collector.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 32 | src/zephyr/feedback_loop/collectors/notification_feedback.py | Notification Feedback — v0.9.0 R118 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 33 | src/zephyr/feedback_loop/collectors/schema_evolution.py | Schema Evolution — v0.9.0 R111 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 34 | src/zephyr/feedback_loop/collectors/schema_migration.py | Schema Migration — v0.14.0 R190 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 35 | src/zephyr/feedback_loop/collectors/temporal_event_store.py | Temporal Event Store — v0.3.0 R9 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 36 | src/zephyr/feedback_loop/collectors/token_finops.py | Token FinOps — v0.12.0 R162 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 37 | src/zephyr/feedback_loop/config.py | config.py | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 38 | src/zephyr/feedback_loop/core.py | FeedbackLoop core — 反馈闭环核心类。 | 原型态 / prototype | [MOD-INF-035](../../03_modules/_cross_layer/auto_runtime_core/blueprint.md) |
| 39 | src/zephyr/feedback_loop/db_bridge.py | FLE DB契约适配器 — 通过规范zephyr.governance.s... | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 40 | src/zephyr/feedback_loop/db_writer.py | FLE 持久化写入器 — 写 metrics/alerts/dispatch_... | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 41 | src/zephyr/feedback_loop/decision_engine.py | Feedback Loop Decision Engine | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 42 | src/zephyr/feedback_loop/detectors/anomaly/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 43 | src/zephyr/feedback_loop/detectors/anomaly/anomaly_cluste... | Anomaly Clustering — v0.9.0 R119 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 44 | src/zephyr/feedback_loop/detectors/anomaly/anomaly_detect... | anomaly_detector.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 45 | src/zephyr/feedback_loop/detectors/anomaly/emergent_behav... | Emergent Behavior Detector — v0.38.0 R473 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 46 | src/zephyr/feedback_loop/detectors/anomaly/flapping_detec... | Flapping Detector — v0.40.0 R494 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 47 | src/zephyr/feedback_loop/detectors/anomaly/heisenbug_dete... | Heisenbug Detector — v0.38.0 R470 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 48 | src/zephyr/feedback_loop/detectors/anomaly/infinite_loop_... | Infinite Loop Detector — v0.15.0 R219 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 49 | src/zephyr/feedback_loop/detectors/anomaly/intermittent_f... | Intermittent Failure Pattern Detector — v0.40.... | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 50 | src/zephyr/feedback_loop/detectors/anomaly/log_anomaly.py | Log Anomaly Detector — v0.6.0 R61 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 51 | src/zephyr/feedback_loop/detectors/anomaly/silent_corrupt... | Silent Corruption Detector — v0.40.0 R499 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 52 | src/zephyr/feedback_loop/detectors/anomaly/synthetic_anom... | Synthetic Anomaly Generator — v0.9.0 R112 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 53 | src/zephyr/feedback_loop/detectors/anomaly/temporal_patte... | Temporal Pattern Detector — v0.12.0 R164 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 54 | src/zephyr/feedback_loop/detectors/correlation/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 55 | src/zephyr/feedback_loop/detectors/correlation/action_eff... | R507: ActionEfficacyDecayDetector | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 56 | src/zephyr/feedback_loop/detectors/correlation/action_int... | Action Interaction Detector — v0.38.0 R472 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 57 | src/zephyr/feedback_loop/detectors/correlation/action_sid... | R526: ActionSideEffectCumulativeDetector | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 58 | src/zephyr/feedback_loop/detectors/correlation/agent_traj... | R503: AgentTrajectoryAnomalyDetector | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 59 | src/zephyr/feedback_loop/detectors/correlation/cross_sign... | Cross-Signal Validator — v0.6.0 R63 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 60 | src/zephyr/feedback_loop/detectors/correlation/cross_syst... | Cross-System Correlator — v0.13.0 R185 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 61 | src/zephyr/feedback_loop/detectors/correlation/decision_p... | Decision Provenance — v0.12.0 R166 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 62 | src/zephyr/feedback_loop/detectors/correlation/dependency... | Dependency Freshness Monitor — v0.38.0 R474 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 63 | src/zephyr/feedback_loop/detectors/correlation/ensemble_d... | Ensemble Detector — v0.4.0 R21 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 64 | src/zephyr/feedback_loop/detectors/correlation/external_h... | External Health Monitor — v0.14.0 R193 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 65 | src/zephyr/feedback_loop/detectors/correlation/external_v... | R524: ExternalValidationCheckpoint | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 66 | src/zephyr/feedback_loop/detectors/correlation/fle_perfor... | R532: FLEPerformanceRegressionDetector | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 67 | src/zephyr/feedback_loop/detectors/correlation/multi_sign... | Multi-Signal Correlator — v0.4.0 R22 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 68 | src/zephyr/feedback_loop/detectors/correlation/rumor_nois... | Rumor Noise Filter — v0.37.0 R460 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 69 | src/zephyr/feedback_loop/detectors/correlation/trace_caus... | Trace Causal Bridge — v0.6.0 R62 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 70 | src/zephyr/feedback_loop/detectors/correlation/traffic_re... | Traffic Replay Validator — v0.14.0 R202 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 71 | src/zephyr/feedback_loop/detectors/drift/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 72 | src/zephyr/feedback_loop/detectors/drift/concept_drift.py | Concept Drift Detector — v0.5.0 R42 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 73 | src/zephyr/feedback_loop/detectors/drift/config_drift.py | Config Drift Detector — v0.13.0 R182 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 74 | src/zephyr/feedback_loop/detectors/drift/context_window_c... | Context Window Contamination Detector — v0.38.... | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 75 | src/zephyr/feedback_loop/detectors/drift/diminishing_retu... | R528: DiminishingReturnsDetector | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 76 | src/zephyr/feedback_loop/detectors/drift/ensemble_drift.py | Ensemble Drift — v0.5.0 R43 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 77 | src/zephyr/feedback_loop/detectors/drift/gradual_poisonin... | Gradual Poisoning Detector — v0.15.0 R210 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 78 | src/zephyr/feedback_loop/detectors/drift/trend_cycle_sepa... | Trend-Cycle Separator — v0.9.0 R113 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 79 | src/zephyr/feedback_loop/detectors/guard/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 80 | src/zephyr/feedback_loop/detectors/guard/alert_desensitiz... | Alert Desensitization Curve — v0.37.0 R492 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 81 | src/zephyr/feedback_loop/detectors/guard/guard_cascade_de... | R520: GuardCascadeDetector | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 82 | src/zephyr/feedback_loop/detectors/guard/guard_oscillatio... | R519: GuardOscillationDetector | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 83 | src/zephyr/feedback_loop/detectors/guard/placebo_action_d... | R508: PlaceboActionDetector | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 84 | src/zephyr/feedback_loop/detectors/guard/positive_feedbac... | Positive Feedback Defense — v0.4.0 R28 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 85 | src/zephyr/feedback_loop/detectors/guard/recursive_diagno... | R517: RecursiveDiagnosisTrustEvaluator | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 86 | src/zephyr/feedback_loop/detectors/guard/self_audit.py | Self Audit — v0.13.0 R183 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 87 | src/zephyr/feedback_loop/detectors/guard/self_diagnosis_d... | R530: SelfDiagnosisDataLeakDetector | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 88 | src/zephyr/feedback_loop/detectors/guard/self_ha.py | Self HA — v0.13.0 R173 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 89 | src/zephyr/feedback_loop/detectors/guard/temporal_coheren... | R525: TemporalCoherenceOfSelfModel | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 90 | src/zephyr/feedback_loop/detectors/reliability/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 91 | src/zephyr/feedback_loop/detectors/reliability/autoscale_... | Autoscale Remediation — v0.13.0 R174 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 92 | src/zephyr/feedback_loop/detectors/reliability/blast_radi... | Blast Radius Detector — v0.12.0 R167 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 93 | src/zephyr/feedback_loop/detectors/reliability/blast_radi... | Blast Radius Budget — v0.13.0 R178 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 94 | src/zephyr/feedback_loop/detectors/reliability/capacity_f... | Capacity Forecast — v0.13.0 R186b | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 95 | src/zephyr/feedback_loop/detectors/reliability/chaos_engi... | Chaos Engineering — v0.13.0 R172 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 96 | src/zephyr/feedback_loop/detectors/reliability/ebpf_monit... | eBPF Monitor — v0.6.0 R64 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 97 | src/zephyr/feedback_loop/detectors/reliability/flag_lifec... | Flag Lifecycle Detector — v0.13.0 R180 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 98 | src/zephyr/feedback_loop/detectors/reliability/maintenanc... | Maintenance Coordinator — v0.12.0 R168 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 99 | src/zephyr/feedback_loop/detectors/reliability/metric_car... | Metric Cardinality Guard — v0.40.0 R495 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 100 | src/zephyr/feedback_loop/detectors/reliability/openfeatur... | OpenFeature Integration — v0.13.0 R181 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 101 | src/zephyr/feedback_loop/detectors/reliability/otel_adapt... | OTel Adapter — v0.12.0 R170 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 102 | src/zephyr/feedback_loop/detectors/reliability/regulatory... | Regulatory Audit Detector — v0.13.0 R184 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 103 | src/zephyr/feedback_loop/detectors/reliability/resolution... | Resolution Tracker — v0.12.0 R165 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 104 | src/zephyr/feedback_loop/detectors/reliability/runbook_ex... | Runbook Executor — v0.13.0 R186a | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 105 | src/zephyr/feedback_loop/detectors/reliability/version_mi... | Version Migrator — v0.12.0 R169 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 106 | src/zephyr/feedback_loop/diagnosers/cognitive/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 107 | src/zephyr/feedback_loop/diagnosers/cognitive/adaptive_pa... | Adaptive Parameter Tuning — v0.37.0 R452 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 108 | src/zephyr/feedback_loop/diagnosers/cognitive/cognitive_l... | Cognitive Load Estimator — v0.6.0 R68 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 109 | src/zephyr/feedback_loop/diagnosers/cognitive/cognitive_l... | Cognitive Load Budget — v0.16.0 R223 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 110 | src/zephyr/feedback_loop/diagnosers/cognitive/collaborati... | Collaborative Learning — v0.7.0 R82 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 111 | src/zephyr/feedback_loop/diagnosers/cognitive/confidence_... | Confidence Decomposer — v0.7.0 R83 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 112 | src/zephyr/feedback_loop/diagnosers/cognitive/gamificatio... | Gamification — v0.8.0 R101 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 113 | src/zephyr/feedback_loop/diagnosers/cognitive/meta_guard_... | R516: MetaGuardLatencyBudget | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 114 | src/zephyr/feedback_loop/diagnosers/cognitive/socratic_qu... | Socratic Questions — v0.7.0 R81 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 115 | src/zephyr/feedback_loop/diagnosers/cognitive/tone_adapte... | Tone Adapter — v0.9.0 R127 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 116 | src/zephyr/feedback_loop/diagnosers/cognitive/tone_adapte... | Tone Adapter v2 — v0.10.0 R141 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 117 | src/zephyr/feedback_loop/diagnosers/diagnosis/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 118 | src/zephyr/feedback_loop/diagnosers/diagnosis/auto_diagno... | Auto Diagnosis — v0.3.0 R16 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 119 | src/zephyr/feedback_loop/diagnosers/diagnosis/causal_infe... | Causal Inference Engine — v0.3.0 R5-R7 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 120 | src/zephyr/feedback_loop/diagnosers/diagnosis/counterfact... | Counterfactual Engine — v0.6.0 R60 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 121 | src/zephyr/feedback_loop/diagnosers/diagnosis/diagnosis_e... | diagnosis_engine.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 122 | src/zephyr/feedback_loop/diagnosers/diagnosis/diagnosis_k... | Diagnosis KPI — v0.9.0 R116 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 123 | src/zephyr/feedback_loop/diagnosers/diagnosis/impact_pred... | Impact Predictor — v0.9.0 R121 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 124 | src/zephyr/feedback_loop/diagnosers/diagnosis/incident_kn... | R504: IncidentKnowledgeInjector | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 125 | src/zephyr/feedback_loop/diagnosers/diagnosis/interactive... | Interactive Diagnosis — v0.7.0 R80 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 126 | src/zephyr/feedback_loop/diagnosers/diagnosis/knowledge_b... | Knowledge Bus Factor Monitor — v0.38.0 R481 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 127 | src/zephyr/feedback_loop/diagnosers/diagnosis/knowledge_m... | Knowledge Market — v0.9.0 R126 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 128 | src/zephyr/feedback_loop/diagnosers/diagnosis/mtti_tracke... | MTTI Tracker — v0.16.0 R221 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 129 | src/zephyr/feedback_loop/diagnosers/diagnosis/nonstationa... | Nonstationary Effectiveness — v0.37.0 R455 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 130 | src/zephyr/feedback_loop/diagnosers/diagnosis/statistical... | Statistical Hygiene Auditor — v0.38.0 R476 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 131 | src/zephyr/feedback_loop/diagnosers/diagnosis/vertical_se... | Vertical Self Assessment — v0.10.0 R137 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 132 | src/zephyr/feedback_loop/diagnosers/health/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 133 | src/zephyr/feedback_loop/diagnosers/health/action_composi... | R511: ActionCompositionHealthMonitor | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 134 | src/zephyr/feedback_loop/diagnosers/health/dr_resilience_... | DR Resilience Metrics — v0.17.0+ R231-R236 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 135 | src/zephyr/feedback_loop/diagnosers/health/e2e_integratio... | E2E Integration Health Monitor — v0.39.0 R489 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 136 | src/zephyr/feedback_loop/diagnosers/health/fle_dogfood_mo... | FLE Dogfood Monitor — v0.38.0 R480 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 137 | src/zephyr/feedback_loop/diagnosers/health/fle_self_slo_m... | FLE Self SLO Metrics — v0.17.0+ R249-R254 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 138 | src/zephyr/feedback_loop/diagnosers/health/global_health_... | Global Health Map — v0.8.0 R103 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 139 | src/zephyr/feedback_loop/diagnosers/health/memory_self_ch... | Memory Self Check — v0.8.0 R105 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 140 | src/zephyr/feedback_loop/diagnosers/health/model_health.py | Model Health Monitor — v0.5.0 R40 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 141 | src/zephyr/feedback_loop/diagnosers/health/self_benchmark.py | Self Benchmark — v0.9.0 R115 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 142 | src/zephyr/feedback_loop/diagnosers/health/self_bottlenec... | Self-Bottleneck Detector — v0.38.0 R479 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 143 | src/zephyr/feedback_loop/diagnosers/health/self_health_mo... | Self Health Monitor — v0.4.0 R29 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 144 | src/zephyr/feedback_loop/diagnosers/health/self_llm_obser... | Self LLM Observability — v0.12.0 R160 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 145 | src/zephyr/feedback_loop/diagnosers/reliability/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 146 | src/zephyr/feedback_loop/diagnosers/reliability/amplifica... | Amplification Guard — v0.10.0 R134 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 147 | src/zephyr/feedback_loop/diagnosers/reliability/api_depen... | API Dependency Metrics — v0.17.0+ R237-R242 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 148 | src/zephyr/feedback_loop/diagnosers/reliability/burn_rate... | Burn Rate Alerter — v0.14.0 R200 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 149 | src/zephyr/feedback_loop/diagnosers/reliability/burnout_a... | Burnout Alarm — v0.8.0 R100 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 150 | src/zephyr/feedback_loop/diagnosers/reliability/capacity_... | Capacity Aware Repair — v0.9.0 R120 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 151 | src/zephyr/feedback_loop/diagnosers/reliability/cold_star... | R509: ColdStartConservativeMode | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 152 | src/zephyr/feedback_loop/diagnosers/reliability/context_t... | Context Truncation Detector — v0.9.0 R122 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 153 | src/zephyr/feedback_loop/diagnosers/reliability/context_w... | R506: ContextWindowPressureManager | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 154 | src/zephyr/feedback_loop/diagnosers/reliability/cross_gua... | R513: CrossGuardConflictDetector | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 155 | src/zephyr/feedback_loop/diagnosers/reliability/cross_ses... | R510: CrossSessionConsistencyValidator | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 156 | src/zephyr/feedback_loop/diagnosers/reliability/data_volu... | Data Volume Growth Monitor — v0.39.0 R492 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 157 | src/zephyr/feedback_loop/diagnosers/reliability/feedback_... | Feedback Delay Compensator — v0.38.0 R477 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 158 | src/zephyr/feedback_loop/diagnosers/reliability/guard_int... | R518: GuardInteractionTopologyMapper | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 159 | src/zephyr/feedback_loop/diagnosers/reliability/guard_sel... | R512: GuardSelfConsistencyAuditor | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 160 | src/zephyr/feedback_loop/diagnosers/reliability/human_ano... | Human Anomaly Flood Detector — v0.40.0 R500 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 161 | src/zephyr/feedback_loop/diagnosers/reliability/latency_s... | Latency SLO Monitor — v0.14.0 R192 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 162 | src/zephyr/feedback_loop/diagnosers/reliability/llm_provi... | LLM Provider Integrity — v0.15.0 R217 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 163 | src/zephyr/feedback_loop/diagnosers/reliability/llm_quali... | LLM Quality Regression — v0.12.0 R161 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 164 | src/zephyr/feedback_loop/diagnosers/reliability/model_rot... | Model Rotation — v0.9.0 R125 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 165 | src/zephyr/feedback_loop/diagnosers/reliability/model_rot... | Model Rotation v2 — v0.10.0 R140 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 166 | src/zephyr/feedback_loop/diagnosers/reliability/model_ver... | Model Version Semantic Drift Monitor — v0.39.0... | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 167 | src/zephyr/feedback_loop/diagnosers/reliability/numerical... | Numerical Stability Guard — v0.38.0 R475 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 168 | src/zephyr/feedback_loop/diagnosers/reliability/operation... | Operational Seasonality — v0.16.0 R228 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 169 | src/zephyr/feedback_loop/diagnosers/reliability/prompt_fi... | Prompt Fingerprint — v0.3.0 R14 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 170 | src/zephyr/feedback_loop/diagnosers/reliability/prompt_sa... | Prompt Sanitizer — v0.10.0 R133 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 171 | src/zephyr/feedback_loop/diagnosers/reliability/recovery_... | Recovery Time Statistics — v0.37.0 R454 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 172 | src/zephyr/feedback_loop/diagnosers/reliability/regime_ga... | Regime Gain Scheduling — v0.37.0 R453 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 173 | src/zephyr/feedback_loop/diagnosers/reliability/retiremen... | Retirement Planner — v0.10.0 R139 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 174 | src/zephyr/feedback_loop/diagnosers/reliability/slo_capac... | SLO Capacity Metrics — v0.17.0+ R243-R248 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 175 | src/zephyr/feedback_loop/diagnosers/reliability/system_en... | R527: SystemEntropyMonitor | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 176 | src/zephyr/feedback_loop/diagnosers/reliability/temporal_... | Temporal Integrity Guard — v0.38.0 R478 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 177 | src/zephyr/feedback_loop/diagnosers/reliability/timezone_... | Timezone Semantic Reasoner — v0.37.0 R456 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 178 | src/zephyr/feedback_loop/diagnosers/reliability/toil_quan... | Toil Quantification — v0.37.0 R457 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 179 | src/zephyr/feedback_loop/diagnosers/reliability/value_add... | Value Added Baseline — v0.10.0 R138 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 180 | src/zephyr/feedback_loop/diagnosers/reliability/zombie_fl... | Zombie FLE Detector — v0.16.0 R222 | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 181 | src/zephyr/feedback_loop/docs/cold_start_manual.py | cold_start_manual.py | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 182 | src/zephyr/feedback_loop/error_budget.py | Error Budget 状态机——monthly budget + burn_ra... | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 183 | src/zephyr/feedback_loop/eval_harness.py | eval_harness.py | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 184 | src/zephyr/feedback_loop/evolution/auto_reward.py | Auto Reward — v0.7.0 R76 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 185 | src/zephyr/feedback_loop/evolution/conformal_prediction.py | Conformal Prediction — v0.7.0 R74 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 186 | src/zephyr/feedback_loop/evolution/cross_gen_validation.py | Cross-Gen Validation — v0.7.0 R78 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 187 | src/zephyr/feedback_loop/evolution/dynamic_threshold.py | Dynamic Threshold — v0.7.0 R71 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 188 | src/zephyr/feedback_loop/evolution/ewc_kb_review.py | EWC KB Review — v0.6.0 R51 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 189 | src/zephyr/feedback_loop/evolution/failure_replay.py | Failure Replay — v0.7.0 R77 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 190 | src/zephyr/feedback_loop/evolution/graduated_activation_p... | Graduated Activation Protocol — v0.38.0 R485 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 191 | src/zephyr/feedback_loop/evolution/hypernetwork.py | HyperNetwork — v0.7.0 R72 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 192 | src/zephyr/feedback_loop/evolution/knowledge_distillation.py | Knowledge Distillation — v0.6.0 R52 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 193 | src/zephyr/feedback_loop/evolution/online_feature_importa... | Online Feature Importance — v0.7.0 R73 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 194 | src/zephyr/feedback_loop/evolution/prompt_factory_governa... | Prompt Factory Governance — v0.16.0 R224 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 195 | src/zephyr/feedback_loop/evolution/prompt_optimization_re... | R514: PromptOptimizationRegressionDetector | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 196 | src/zephyr/feedback_loop/evolution/prompt_self_optimizati... | R502: PromptSelfOptimizationLoop | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 197 | src/zephyr/feedback_loop/evolution/self_modification_rate... | R522: SelfModificationRateLimiter | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 198 | src/zephyr/feedback_loop/evolution/self_reflection.py | Self Reflection — v0.7.0 R75 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 199 | src/zephyr/feedback_loop/evolution/self_upgrade_canary.py | Self Upgrade Canary — v0.14.0 R194 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 200 | src/zephyr/feedback_loop/evolution/semantic_intent_preser... | R505: SemanticIntentPreservationGuard | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |

> (仅显示前 200 个模块，共 358 个)

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分四个视图：合并全景图、运营态子图、设计态子图、原型态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **虚线边框 = 原型态模块**（prototype，代码已写，验证中未稳定上线）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 358 个模块（生产态 107 + 设计态 0 + 原型态 251），标签标注成熟度。

#### 第 1 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        src_zephyr_feedback_loop_init_py["(生产态 / production) Feedback Loop Engine — MOD-FEEDBACK_LOOP.<br/>文件: __init__.py"]
        src_zephyr_feedback_loop_gen_inherited_py["(生产态 / production) _gen_inherited.py"]
        src_zephyr_feedback_loop_actors_action_selector_py["(生产态 / production) action_selector.py"]
        src_zephyr_feedback_loop_actors_agent_lifecycle_py["(生产态 / production) Agent Lifecycle Manager — v0.12.0 R159c<br/>文件: agent_lifecycle.py"]
        src_zephyr_feedback_loop_actors_api_version_contract_py["(生产态 / production) API Version Contract — v0.14.0 R188<br/>文件: api_version_contract.py"]
        src_zephyr_feedback_loop_actors_global_action_scheduler_py["(生产态 / production) Global Action Scheduler — v0.16.0 R226<br/>文件: global_action_scheduler.py"]
        src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py["(生产态 / production) Incident Priority Triage Automator — v0.37.0 R463<br/>文件: incident_priority_triage_automator.py"]
        src_zephyr_feedback_loop_actors_intent_driven_ops_py["(生产态 / production) Intent-Driven Ops — v0.12.0 R159<br/>文件: intent_driven_ops.py"]
        src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py["(生产态 / production) Multi-Agent Orchestrator — v0.12.0 R159b<br/>文件: multi_agent_orchestrator.py"]
        src_zephyr_feedback_loop_actors_notification_personalizer_py["(生产态 / production) Notification Personalizer — v0.6.0 R67<br/>文件: notification_personalizer.py"]
        src_zephyr_feedback_loop_actors_owner_absence_escalation_py["(生产态 / production) Owner Absence Escalation — v0.37.0 R462<br/>文件: owner_absence_escalation.py"]
        src_zephyr_feedback_loop_actors_saga_compensator_py["(原型态 / prototype) Saga Compensator — v0.3.0 R19b<br/>文件: saga_compensator.py"]
        src_zephyr_feedback_loop_actors_secondary_alert_channel_py["(生产态 / production) Secondary Alert Channel — v0.37.0 R461<br/>文件: secondary_alert_channel.py"]
        src_zephyr_feedback_loop_alert_dispatcher_py["(原型态 / prototype) FLE->Orc 告警分派器 — dispatch() 生产者<br/>文件: alert_dispatcher.py"]
        src_zephyr_feedback_loop_auto_evolution_py["(生产态 / production) auto_evolution.py"]
        src_zephyr_feedback_loop_backpressure_bridge_py["(生产态 / production) FLE -> Pipeline 背压桥接（CTR-BP-001~003）<br/>文件: backpressure_bridge.py"]
        src_zephyr_feedback_loop_collectors_calendar_adapter_py["(生产态 / production) Calendar Adapter — v0.8.0 R102b<br/>文件: calendar_adapter.py"]
        src_zephyr_feedback_loop_collectors_config_timeline_py["(生产态 / production) Config Timeline — v0.8.0 R99<br/>文件: config_timeline.py"]
        src_zephyr_feedback_loop_collectors_data_quality_validator_py["(生产态 / production) Data Quality Validator — v0.9.0 R110<br/>文件: data_quality_validator.py"]
        src_zephyr_feedback_loop_collectors_feedback_collector_py["(原型态 / prototype) feedback_collector.py"]
        src_zephyr_feedback_loop_collectors_financial_stratification_py["(生产态 / production) Financial Stratification — v0.5.0 R50<br/>文件: financial_stratification.py"]
        src_zephyr_feedback_loop_collectors_kb_provenance_py["(生产态 / production) KB Provenance — v0.10.0 R136<br/>文件: kb_provenance.py"]
        src_zephyr_feedback_loop_collectors_knowledge_capture_py["(生产态 / production) Knowledge Capture — v0.4.0 R30<br/>文件: knowledge_capture.py"]
        src_zephyr_feedback_loop_collectors_knowledge_freshness_py["(生产态 / production) Knowledge Freshness — v0.5.0 R47<br/>文件: knowledge_freshness.py"]
        src_zephyr_feedback_loop_collectors_knowledge_injection_py["(生产态 / production) Knowledge Injection — v0.8.0 R102<br/>文件: knowledge_injection.py"]
        src_zephyr_feedback_loop_collectors_knowledge_packaging_py["(生产态 / production) Knowledge Packaging — v0.9.0 R123<br/>文件: knowledge_packaging.py"]
        src_zephyr_feedback_loop_collectors_known_unknown_registry_py["(生产态 / production) Known-Unknown Registry — v0.16.0 R229<br/>文件: known_unknown_registry.py"]
        src_zephyr_feedback_loop_collectors_llm_cost_accounting_py["(生产态 / production) LLM Cost Accounting — v0.4.0 R35<br/>文件: llm_cost_accounting.py"]
        src_zephyr_feedback_loop_collectors_market_calendar_py["(生产态 / production) Market Calendar — v0.5.0 R48<br/>文件: market_calendar.py"]
        src_zephyr_feedback_loop_collectors_market_event_integrator_py["(生产态 / production) Market Event Integrator — v0.14.0 R197<br/>文件: market_event_integrator.py"]
    end
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_feedback_loop_alert_dispatcher_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_ORCHESTRATOR["(原型态 / prototype) D_ORCHESTRATOR"]
    src_zephyr_feedback_loop_alert_dispatcher_py -.->|导入依赖 / import_depends| D_ORCHESTRATOR
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    src_zephyr_feedback_loop_backpressure_bridge_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_feedback_loop_actors_api_version_contract_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_agent_lifecycle_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_api_version_contract_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_global_action_scheduler_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_intent_driven_ops_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_notification_personalizer_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_owner_absence_escalation_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_saga_compensator_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_secondary_alert_channel_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_calendar_adapter_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_config_timeline_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_data_quality_validator_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_init_py,src_zephyr_feedback_loop_gen_inherited_py,src_zephyr_feedback_loop_actors_action_selector_py,src_zephyr_feedback_loop_actors_agent_lifecycle_py,src_zephyr_feedback_loop_actors_api_version_contract_py,src_zephyr_feedback_loop_actors_global_action_scheduler_py,src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py,src_zephyr_feedback_loop_actors_intent_driven_ops_py,src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py,src_zephyr_feedback_loop_actors_notification_personalizer_py,src_zephyr_feedback_loop_actors_owner_absence_escalation_py,src_zephyr_feedback_loop_actors_secondary_alert_channel_py,src_zephyr_feedback_loop_auto_evolution_py,src_zephyr_feedback_loop_backpressure_bridge_py,src_zephyr_feedback_loop_collectors_calendar_adapter_py,src_zephyr_feedback_loop_collectors_config_timeline_py,src_zephyr_feedback_loop_collectors_data_quality_validator_py,src_zephyr_feedback_loop_collectors_financial_stratification_py,src_zephyr_feedback_loop_collectors_kb_provenance_py,src_zephyr_feedback_loop_collectors_knowledge_capture_py,src_zephyr_feedback_loop_collectors_knowledge_freshness_py,src_zephyr_feedback_loop_collectors_knowledge_injection_py,src_zephyr_feedback_loop_collectors_knowledge_packaging_py,src_zephyr_feedback_loop_collectors_known_unknown_registry_py,src_zephyr_feedback_loop_collectors_llm_cost_accounting_py,src_zephyr_feedback_loop_collectors_market_calendar_py,src_zephyr_feedback_loop_collectors_market_event_integrator_py production
    class src_zephyr_feedback_loop_actors_saga_compensator_py,src_zephyr_feedback_loop_alert_dispatcher_py,src_zephyr_feedback_loop_collectors_feedback_collector_py design
    class D_GOVERNANCE,D_INFRA_RUNTIME,D_SHARED external_prod
    class D_ORCHESTRATOR external_design
```

#### 第 2 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        src_zephyr_feedback_loop_collectors_metrics_collector_py["(原型态 / prototype) metrics_collector.py"]
        src_zephyr_feedback_loop_collectors_notification_feedback_py["(生产态 / production) Notification Feedback — v0.9.0 R118<br/>文件: notification_feedback.py"]
        src_zephyr_feedback_loop_collectors_schema_evolution_py["(生产态 / production) Schema Evolution — v0.9.0 R111<br/>文件: schema_evolution.py"]
        src_zephyr_feedback_loop_collectors_schema_migration_py["(生产态 / production) Schema Migration — v0.14.0 R190<br/>文件: schema_migration.py"]
        src_zephyr_feedback_loop_collectors_temporal_event_store_py["(生产态 / production) Temporal Event Store — v0.3.0 R9<br/>文件: temporal_event_store.py"]
        src_zephyr_feedback_loop_collectors_token_finops_py["(生产态 / production) Token FinOps — v0.12.0 R162<br/>文件: token_finops.py"]
        src_zephyr_feedback_loop_config_py["(生产态 / production) config.py"]
        src_zephyr_feedback_loop_core_py["(原型态 / prototype) FeedbackLoop core — 反馈闭环核心类。<br/>文件: core.py"]
        src_zephyr_feedback_loop_db_bridge_py["(生产态 / production) FLE DB契约适配器 — 通过规范zephyr.governance.s...<br/>文件: db_bridge.py"]
        src_zephyr_feedback_loop_db_writer_py["(原型态 / prototype) FLE 持久化写入器 — 写 metrics/alerts/dispatch_...<br/>文件: db_writer.py"]
        src_zephyr_feedback_loop_decision_engine_py["(生产态 / production) Feedback Loop Decision Engine<br/>文件: decision_engine.py"]
        src_zephyr_feedback_loop_detectors_anomaly_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_detectors_anomaly_anomaly_clustering_py["(原型态 / prototype) Anomaly Clustering — v0.9.0 R119<br/>文件: anomaly_clustering.py"]
        src_zephyr_feedback_loop_detectors_anomaly_anomaly_detector_py["(原型态 / prototype) anomaly_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_emergent_behavior_detector_py["(原型态 / prototype) Emergent Behavior Detector — v0.38.0 R473<br/>文件: emergent_behavior_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_flapping_detector_py["(原型态 / prototype) Flapping Detector — v0.40.0 R494<br/>文件: flapping_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_heisenbug_detector_py["(原型态 / prototype) Heisenbug Detector — v0.38.0 R470<br/>文件: heisenbug_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_infinite_loop_detector_py["(原型态 / prototype) Infinite Loop Detector — v0.15.0 R219<br/>文件: infinite_loop_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_intermittent_failure_pattern_py["(原型态 / prototype) Intermittent Failure Pattern Detector — v0.40....<br/>文件: intermittent_failure_pattern.py"]
        src_zephyr_feedback_loop_detectors_anomaly_log_anomaly_py["(原型态 / prototype) Log Anomaly Detector — v0.6.0 R61<br/>文件: log_anomaly.py"]
        src_zephyr_feedback_loop_detectors_anomaly_silent_corruption_detector_py["(原型态 / prototype) Silent Corruption Detector — v0.40.0 R499<br/>文件: silent_corruption_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_synthetic_anomaly_generator_py["(原型态 / prototype) Synthetic Anomaly Generator — v0.9.0 R112<br/>文件: synthetic_anomaly_generator.py"]
        src_zephyr_feedback_loop_detectors_anomaly_temporal_pattern_py["(原型态 / prototype) Temporal Pattern Detector — v0.12.0 R164<br/>文件: temporal_pattern.py"]
        src_zephyr_feedback_loop_detectors_correlation_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_detectors_correlation_action_efficacy_decay_detector_py["(原型态 / prototype) R507: ActionEfficacyDecayDetector<br/>文件: action_efficacy_decay_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_action_interaction_detector_py["(原型态 / prototype) Action Interaction Detector — v0.38.0 R472<br/>文件: action_interaction_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_action_side_effect_cumulative_detector_py["(原型态 / prototype) R526: ActionSideEffectCumulativeDetector<br/>文件: action_side_effect_cumulative_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_agent_trajectory_anomaly_detector_py["(原型态 / prototype) R503: AgentTrajectoryAnomalyDetector<br/>文件: agent_trajectory_anomaly_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_cross_signal_validator_py["(原型态 / prototype) Cross-Signal Validator — v0.6.0 R63<br/>文件: cross_signal_validator.py"]
        src_zephyr_feedback_loop_detectors_correlation_cross_system_correlator_py["(原型态 / prototype) Cross-System Correlator — v0.13.0 R185<br/>文件: cross_system_correlator.py"]
    end
    src_zephyr_feedback_loop_detectors_anomaly_anomaly_detector_py -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_detectors_anomaly_anomaly_clustering_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_emergent_behavior_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_flapping_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_infinite_loop_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_heisenbug_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_intermittent_failure_pattern_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_temporal_pattern_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_silent_corruption_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_correlation_action_interaction_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_anomaly_synthetic_anomaly_generator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_log_anomaly_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_correlation_action_efficacy_decay_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_action_side_effect_cumulative_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_agent_trajectory_anomaly_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_cross_signal_validator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_cross_system_correlator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    src_zephyr_feedback_loop_core_py -.->|导入依赖 / import_depends| D_INTEGRATION
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_feedback_loop_core_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_core_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_feedback_loop_db_writer_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_INFRA_RUNTIME["(原型态 / prototype) D_INFRA_RUNTIME"]
    src_zephyr_feedback_loop_db_writer_py -.->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_feedback_loop_db_bridge_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_notification_feedback_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_schema_evolution_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_schema_migration_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_temporal_event_store_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_token_finops_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    D_ORCHESTRATOR["(生产态 / production) D_ORCHESTRATOR"]
    D_ORCHESTRATOR -->|导入依赖 / import_depends| src_zephyr_feedback_loop_decision_engine_py
    D_DATA["(原型态 / prototype) D_DATA"]
    D_DATA -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_db_bridge_py
    D_INTELLIGENCE["(原型态 / prototype) D_INTELLIGENCE"]
    D_INTELLIGENCE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_decision_engine_py
    D_GOV_AUDIT["(原型态 / prototype) D_GOV_AUDIT"]
    D_GOV_AUDIT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_collectors_schema_evolution_py
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_config_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_db_bridge_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_decision_engine_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_collectors_notification_feedback_py,src_zephyr_feedback_loop_collectors_schema_evolution_py,src_zephyr_feedback_loop_collectors_schema_migration_py,src_zephyr_feedback_loop_collectors_temporal_event_store_py,src_zephyr_feedback_loop_collectors_token_finops_py,src_zephyr_feedback_loop_config_py,src_zephyr_feedback_loop_db_bridge_py,src_zephyr_feedback_loop_decision_engine_py production
    class src_zephyr_feedback_loop_collectors_metrics_collector_py,src_zephyr_feedback_loop_core_py,src_zephyr_feedback_loop_db_writer_py,src_zephyr_feedback_loop_detectors_anomaly_init_py,src_zephyr_feedback_loop_detectors_anomaly_anomaly_clustering_py,src_zephyr_feedback_loop_detectors_anomaly_anomaly_detector_py,src_zephyr_feedback_loop_detectors_anomaly_emergent_behavior_detector_py,src_zephyr_feedback_loop_detectors_anomaly_flapping_detector_py,src_zephyr_feedback_loop_detectors_anomaly_heisenbug_detector_py,src_zephyr_feedback_loop_detectors_anomaly_infinite_loop_detector_py,src_zephyr_feedback_loop_detectors_anomaly_intermittent_failure_pattern_py,src_zephyr_feedback_loop_detectors_anomaly_log_anomaly_py,src_zephyr_feedback_loop_detectors_anomaly_silent_corruption_detector_py,src_zephyr_feedback_loop_detectors_anomaly_synthetic_anomaly_generator_py,src_zephyr_feedback_loop_detectors_anomaly_temporal_pattern_py,src_zephyr_feedback_loop_detectors_correlation_init_py,src_zephyr_feedback_loop_detectors_correlation_action_efficacy_decay_detector_py,src_zephyr_feedback_loop_detectors_correlation_action_interaction_detector_py,src_zephyr_feedback_loop_detectors_correlation_action_side_effect_cumulative_detector_py,src_zephyr_feedback_loop_detectors_correlation_agent_trajectory_anomaly_detector_py,src_zephyr_feedback_loop_detectors_correlation_cross_signal_validator_py,src_zephyr_feedback_loop_detectors_correlation_cross_system_correlator_py design
    class D_INTEGRATION,D_SHARED,D_GOVERNANCE,D_ORCHESTRATOR external_prod
    class D_INFRA_RUNTIME,D_DATA,D_INTELLIGENCE,D_GOV_AUDIT,D_AUTONOMY_CORE external_design
```

#### 第 3 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        src_zephyr_feedback_loop_detectors_correlation_decision_provenance_py["(原型态 / prototype) Decision Provenance — v0.12.0 R166<br/>文件: decision_provenance.py"]
        src_zephyr_feedback_loop_detectors_correlation_dependency_freshness_monitor_py["(原型态 / prototype) Dependency Freshness Monitor — v0.38.0 R474<br/>文件: dependency_freshness_monitor.py"]
        src_zephyr_feedback_loop_detectors_correlation_ensemble_detector_py["(原型态 / prototype) Ensemble Detector — v0.4.0 R21<br/>文件: ensemble_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_external_health_py["(原型态 / prototype) External Health Monitor — v0.14.0 R193<br/>文件: external_health.py"]
        src_zephyr_feedback_loop_detectors_correlation_external_validation_checkpoint_py["(原型态 / prototype) R524: ExternalValidationCheckpoint<br/>文件: external_validation_checkpoint.py"]
        src_zephyr_feedback_loop_detectors_correlation_fle_performance_regression_detector_py["(原型态 / prototype) R532: FLEPerformanceRegressionDetector<br/>文件: fle_performance_regression_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_multi_signal_correlator_py["(原型态 / prototype) Multi-Signal Correlator — v0.4.0 R22<br/>文件: multi_signal_correlator.py"]
        src_zephyr_feedback_loop_detectors_correlation_rumor_noise_filter_py["(原型态 / prototype) Rumor Noise Filter — v0.37.0 R460<br/>文件: rumor_noise_filter.py"]
        src_zephyr_feedback_loop_detectors_correlation_trace_causal_bridge_py["(原型态 / prototype) Trace Causal Bridge — v0.6.0 R62<br/>文件: trace_causal_bridge.py"]
        src_zephyr_feedback_loop_detectors_correlation_traffic_replay_validator_py["(原型态 / prototype) Traffic Replay Validator — v0.14.0 R202<br/>文件: traffic_replay_validator.py"]
        src_zephyr_feedback_loop_detectors_drift_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_detectors_drift_concept_drift_py["(原型态 / prototype) Concept Drift Detector — v0.5.0 R42<br/>文件: concept_drift.py"]
        src_zephyr_feedback_loop_detectors_drift_config_drift_py["(原型态 / prototype) Config Drift Detector — v0.13.0 R182<br/>文件: config_drift.py"]
        src_zephyr_feedback_loop_detectors_drift_context_window_contamination_detector_py["(原型态 / prototype) Context Window Contamination Detector — v0.38....<br/>文件: context_window_contamination_detector.py"]
        src_zephyr_feedback_loop_detectors_drift_diminishing_returns_detector_py["(原型态 / prototype) R528: DiminishingReturnsDetector<br/>文件: diminishing_returns_detector.py"]
        src_zephyr_feedback_loop_detectors_drift_ensemble_drift_py["(原型态 / prototype) Ensemble Drift — v0.5.0 R43<br/>文件: ensemble_drift.py"]
        src_zephyr_feedback_loop_detectors_drift_gradual_poisoning_detector_py["(原型态 / prototype) Gradual Poisoning Detector — v0.15.0 R210<br/>文件: gradual_poisoning_detector.py"]
        src_zephyr_feedback_loop_detectors_drift_trend_cycle_separator_py["(原型态 / prototype) Trend-Cycle Separator — v0.9.0 R113<br/>文件: trend_cycle_separator.py"]
        src_zephyr_feedback_loop_detectors_guard_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_detectors_guard_alert_desensitization_curve_py["(原型态 / prototype) Alert Desensitization Curve — v0.37.0 R492<br/>文件: alert_desensitization_curve.py"]
        src_zephyr_feedback_loop_detectors_guard_guard_cascade_detector_py["(原型态 / prototype) R520: GuardCascadeDetector<br/>文件: guard_cascade_detector.py"]
        src_zephyr_feedback_loop_detectors_guard_guard_oscillation_detector_py["(原型态 / prototype) R519: GuardOscillationDetector<br/>文件: guard_oscillation_detector.py"]
        src_zephyr_feedback_loop_detectors_guard_placebo_action_detector_py["(原型态 / prototype) R508: PlaceboActionDetector<br/>文件: placebo_action_detector.py"]
        src_zephyr_feedback_loop_detectors_guard_positive_feedback_defense_py["(原型态 / prototype) Positive Feedback Defense — v0.4.0 R28<br/>文件: positive_feedback_defense.py"]
        src_zephyr_feedback_loop_detectors_guard_recursive_diagnosis_trust_evaluator_py["(原型态 / prototype) R517: RecursiveDiagnosisTrustEvaluator<br/>文件: recursive_diagnosis_trust_evaluator.py"]
        src_zephyr_feedback_loop_detectors_guard_self_audit_py["(原型态 / prototype) Self Audit — v0.13.0 R183<br/>文件: self_audit.py"]
        src_zephyr_feedback_loop_detectors_guard_self_diagnosis_data_leak_detector_py["(原型态 / prototype) R530: SelfDiagnosisDataLeakDetector<br/>文件: self_diagnosis_data_leak_detector.py"]
        src_zephyr_feedback_loop_detectors_guard_self_ha_py["(原型态 / prototype) Self HA — v0.13.0 R173<br/>文件: self_ha.py"]
        src_zephyr_feedback_loop_detectors_guard_temporal_coherence_of_self_model_py["(原型态 / prototype) R525: TemporalCoherenceOfSelfModel<br/>文件: temporal_coherence_of_self_model.py"]
        src_zephyr_feedback_loop_detectors_reliability_init_py["(原型态 / prototype) __init__.py"]
    end
    src_zephyr_feedback_loop_detectors_drift_concept_drift_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_drift_config_drift_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_drift_context_window_contamination_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_drift_diminishing_returns_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_drift_trend_cycle_separator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_drift_gradual_poisoning_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_guard_alert_desensitization_curve_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_guard_cascade_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_drift_ensemble_drift_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_guard_guard_oscillation_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_placebo_action_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_positive_feedback_defense_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_recursive_diagnosis_trust_evaluator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_self_audit_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_self_diagnosis_data_leak_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_self_ha_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_temporal_coherence_of_self_model_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_detectors_correlation_decision_provenance_py,src_zephyr_feedback_loop_detectors_correlation_dependency_freshness_monitor_py,src_zephyr_feedback_loop_detectors_correlation_ensemble_detector_py,src_zephyr_feedback_loop_detectors_correlation_external_health_py,src_zephyr_feedback_loop_detectors_correlation_external_validation_checkpoint_py,src_zephyr_feedback_loop_detectors_correlation_fle_performance_regression_detector_py,src_zephyr_feedback_loop_detectors_correlation_multi_signal_correlator_py,src_zephyr_feedback_loop_detectors_correlation_rumor_noise_filter_py,src_zephyr_feedback_loop_detectors_correlation_trace_causal_bridge_py,src_zephyr_feedback_loop_detectors_correlation_traffic_replay_validator_py,src_zephyr_feedback_loop_detectors_drift_init_py,src_zephyr_feedback_loop_detectors_drift_concept_drift_py,src_zephyr_feedback_loop_detectors_drift_config_drift_py,src_zephyr_feedback_loop_detectors_drift_context_window_contamination_detector_py,src_zephyr_feedback_loop_detectors_drift_diminishing_returns_detector_py,src_zephyr_feedback_loop_detectors_drift_ensemble_drift_py,src_zephyr_feedback_loop_detectors_drift_gradual_poisoning_detector_py,src_zephyr_feedback_loop_detectors_drift_trend_cycle_separator_py,src_zephyr_feedback_loop_detectors_guard_init_py,src_zephyr_feedback_loop_detectors_guard_alert_desensitization_curve_py,src_zephyr_feedback_loop_detectors_guard_guard_cascade_detector_py,src_zephyr_feedback_loop_detectors_guard_guard_oscillation_detector_py,src_zephyr_feedback_loop_detectors_guard_placebo_action_detector_py,src_zephyr_feedback_loop_detectors_guard_positive_feedback_defense_py,src_zephyr_feedback_loop_detectors_guard_recursive_diagnosis_trust_evaluator_py,src_zephyr_feedback_loop_detectors_guard_self_audit_py,src_zephyr_feedback_loop_detectors_guard_self_diagnosis_data_leak_detector_py,src_zephyr_feedback_loop_detectors_guard_self_ha_py,src_zephyr_feedback_loop_detectors_guard_temporal_coherence_of_self_model_py,src_zephyr_feedback_loop_detectors_reliability_init_py design
    class D_GOVERNANCE external_prod
```

#### 第 4 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        src_zephyr_feedback_loop_detectors_reliability_autoscale_remediation_py["(原型态 / prototype) Autoscale Remediation — v0.13.0 R174<br/>文件: autoscale_remediation.py"]
        src_zephyr_feedback_loop_detectors_reliability_blast_radius_py["(原型态 / prototype) Blast Radius Detector — v0.12.0 R167<br/>文件: blast_radius.py"]
        src_zephyr_feedback_loop_detectors_reliability_blast_radius_budget_py["(原型态 / prototype) Blast Radius Budget — v0.13.0 R178<br/>文件: blast_radius_budget.py"]
        src_zephyr_feedback_loop_detectors_reliability_capacity_forecast_py["(原型态 / prototype) Capacity Forecast — v0.13.0 R186b<br/>文件: capacity_forecast.py"]
        src_zephyr_feedback_loop_detectors_reliability_chaos_engineering_py["(原型态 / prototype) Chaos Engineering — v0.13.0 R172<br/>文件: chaos_engineering.py"]
        src_zephyr_feedback_loop_detectors_reliability_ebpf_monitor_py["(原型态 / prototype) eBPF Monitor — v0.6.0 R64<br/>文件: ebpf_monitor.py"]
        src_zephyr_feedback_loop_detectors_reliability_flag_lifecycle_py["(原型态 / prototype) Flag Lifecycle Detector — v0.13.0 R180<br/>文件: flag_lifecycle.py"]
        src_zephyr_feedback_loop_detectors_reliability_maintenance_coordinator_py["(原型态 / prototype) Maintenance Coordinator — v0.12.0 R168<br/>文件: maintenance_coordinator.py"]
        src_zephyr_feedback_loop_detectors_reliability_metric_cardinality_guard_py["(原型态 / prototype) Metric Cardinality Guard — v0.40.0 R495<br/>文件: metric_cardinality_guard.py"]
        src_zephyr_feedback_loop_detectors_reliability_openfeature_py["(原型态 / prototype) OpenFeature Integration — v0.13.0 R181<br/>文件: openfeature.py"]
        src_zephyr_feedback_loop_detectors_reliability_otel_adapter_py["(原型态 / prototype) OTel Adapter — v0.12.0 R170<br/>文件: otel_adapter.py"]
        src_zephyr_feedback_loop_detectors_reliability_regulatory_audit_py["(原型态 / prototype) Regulatory Audit Detector — v0.13.0 R184<br/>文件: regulatory_audit.py"]
        src_zephyr_feedback_loop_detectors_reliability_resolution_tracker_py["(原型态 / prototype) Resolution Tracker — v0.12.0 R165<br/>文件: resolution_tracker.py"]
        src_zephyr_feedback_loop_detectors_reliability_runbook_executor_py["(原型态 / prototype) Runbook Executor — v0.13.0 R186a<br/>文件: runbook_executor.py"]
        src_zephyr_feedback_loop_detectors_reliability_version_migrator_py["(原型态 / prototype) Version Migrator — v0.12.0 R169<br/>文件: version_migrator.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py["(原型态 / prototype) Adaptive Parameter Tuning — v0.37.0 R452<br/>文件: adaptive_param_tuning.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py["(原型态 / prototype) Cognitive Load Estimator — v0.6.0 R68<br/>文件: cognitive_load.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py["(原型态 / prototype) Cognitive Load Budget — v0.16.0 R223<br/>文件: cognitive_load_budget.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py["(原型态 / prototype) Collaborative Learning — v0.7.0 R82<br/>文件: collaborative_learning.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py["(原型态 / prototype) Confidence Decomposer — v0.7.0 R83<br/>文件: confidence_decomposer.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py["(原型态 / prototype) Gamification — v0.8.0 R101<br/>文件: gamification.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py["(原型态 / prototype) R516: MetaGuardLatencyBudget<br/>文件: meta_guard_latency_budget.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py["(原型态 / prototype) Socratic Questions — v0.7.0 R81<br/>文件: socratic_questions.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py["(原型态 / prototype) Tone Adapter — v0.9.0 R127<br/>文件: tone_adapter.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py["(原型态 / prototype) Tone Adapter v2 — v0.10.0 R141<br/>文件: tone_adapter_v2.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py["(原型态 / prototype) Auto Diagnosis — v0.3.0 R16<br/>文件: auto_diagnosis.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py["(原型态 / prototype) Causal Inference Engine — v0.3.0 R5-R7<br/>文件: causal_inference_engine.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py["(原型态 / prototype) Counterfactual Engine — v0.6.0 R60<br/>文件: counterfactual.py"]
    end
    src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_detectors_reliability_autoscale_remediation_py,src_zephyr_feedback_loop_detectors_reliability_blast_radius_py,src_zephyr_feedback_loop_detectors_reliability_blast_radius_budget_py,src_zephyr_feedback_loop_detectors_reliability_capacity_forecast_py,src_zephyr_feedback_loop_detectors_reliability_chaos_engineering_py,src_zephyr_feedback_loop_detectors_reliability_ebpf_monitor_py,src_zephyr_feedback_loop_detectors_reliability_flag_lifecycle_py,src_zephyr_feedback_loop_detectors_reliability_maintenance_coordinator_py,src_zephyr_feedback_loop_detectors_reliability_metric_cardinality_guard_py,src_zephyr_feedback_loop_detectors_reliability_openfeature_py,src_zephyr_feedback_loop_detectors_reliability_otel_adapter_py,src_zephyr_feedback_loop_detectors_reliability_regulatory_audit_py,src_zephyr_feedback_loop_detectors_reliability_resolution_tracker_py,src_zephyr_feedback_loop_detectors_reliability_runbook_executor_py,src_zephyr_feedback_loop_detectors_reliability_version_migrator_py,src_zephyr_feedback_loop_diagnosers_cognitive_init_py,src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py,src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py,src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py,src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py,src_zephyr_feedback_loop_diagnosers_diagnosis_init_py,src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py design
    class D_GOVERNANCE external_prod
```

#### 第 5 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py["(原型态 / prototype) diagnosis_engine.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py["(原型态 / prototype) Diagnosis KPI — v0.9.0 R116<br/>文件: diagnosis_kpi.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py["(原型态 / prototype) Impact Predictor — v0.9.0 R121<br/>文件: impact_predictor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py["(原型态 / prototype) R504: IncidentKnowledgeInjector<br/>文件: incident_knowledge_injector.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py["(原型态 / prototype) Interactive Diagnosis — v0.7.0 R80<br/>文件: interactive_diagnosis.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py["(原型态 / prototype) Knowledge Bus Factor Monitor — v0.38.0 R481<br/>文件: knowledge_bus_factor_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py["(原型态 / prototype) Knowledge Market — v0.9.0 R126<br/>文件: knowledge_market.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py["(原型态 / prototype) MTTI Tracker — v0.16.0 R221<br/>文件: mtti_tracker.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py["(原型态 / prototype) Nonstationary Effectiveness — v0.37.0 R455<br/>文件: nonstationary_effectiveness.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py["(原型态 / prototype) Statistical Hygiene Auditor — v0.38.0 R476<br/>文件: statistical_hygiene_auditor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py["(原型态 / prototype) Vertical Self Assessment — v0.10.0 R137<br/>文件: vertical_self_assessment.py"]
        src_zephyr_feedback_loop_diagnosers_health_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py["(原型态 / prototype) R511: ActionCompositionHealthMonitor<br/>文件: action_composition_health_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py["(原型态 / prototype) DR Resilience Metrics — v0.17.0+ R231-R236<br/>文件: dr_resilience_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py["(原型态 / prototype) E2E Integration Health Monitor — v0.39.0 R489<br/>文件: e2e_integration_health.py"]
        src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py["(原型态 / prototype) FLE Dogfood Monitor — v0.38.0 R480<br/>文件: fle_dogfood_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py["(原型态 / prototype) FLE Self SLO Metrics — v0.17.0+ R249-R254<br/>文件: fle_self_slo_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_health_global_health_map_py["(原型态 / prototype) Global Health Map — v0.8.0 R103<br/>文件: global_health_map.py"]
        src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py["(原型态 / prototype) Memory Self Check — v0.8.0 R105<br/>文件: memory_self_check.py"]
        src_zephyr_feedback_loop_diagnosers_health_model_health_py["(原型态 / prototype) Model Health Monitor — v0.5.0 R40<br/>文件: model_health.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py["(原型态 / prototype) Self Benchmark — v0.9.0 R115<br/>文件: self_benchmark.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py["(原型态 / prototype) Self-Bottleneck Detector — v0.38.0 R479<br/>文件: self_bottleneck_detector.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py["(原型态 / prototype) Self Health Monitor — v0.4.0 R29<br/>文件: self_health_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py["(原型态 / prototype) Self LLM Observability — v0.12.0 R160<br/>文件: self_llm_observability.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py["(原型态 / prototype) Amplification Guard — v0.10.0 R134<br/>文件: amplification_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py["(原型态 / prototype) API Dependency Metrics — v0.17.0+ R237-R242<br/>文件: api_dependency_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py["(原型态 / prototype) Burn Rate Alerter — v0.14.0 R200<br/>文件: burn_rate_alerter.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py["(原型态 / prototype) Burnout Alarm — v0.8.0 R100<br/>文件: burnout_alarm.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py["(原型态 / prototype) Capacity Aware Repair — v0.9.0 R120<br/>文件: capacity_aware_repair.py"]
    end
    src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_global_health_map_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_model_health_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py,src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py,src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py,src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py,src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py,src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py,src_zephyr_feedback_loop_diagnosers_health_init_py,src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py,src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py,src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py,src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py,src_zephyr_feedback_loop_diagnosers_health_global_health_map_py,src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py,src_zephyr_feedback_loop_diagnosers_health_model_health_py,src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py,src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py,src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py,src_zephyr_feedback_loop_diagnosers_reliability_init_py,src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py,src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py,src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py design
    class D_GOVERNANCE external_prod
```

#### 第 6 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py["(原型态 / prototype) R509: ColdStartConservativeMode<br/>文件: cold_start_conservative_mode.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py["(原型态 / prototype) Context Truncation Detector — v0.9.0 R122<br/>文件: context_truncation.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py["(原型态 / prototype) R506: ContextWindowPressureManager<br/>文件: context_window_pressure_manager.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py["(原型态 / prototype) R513: CrossGuardConflictDetector<br/>文件: cross_guard_conflict_detector.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py["(原型态 / prototype) R510: CrossSessionConsistencyValidator<br/>文件: cross_session_consistency_validator.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py["(原型态 / prototype) Data Volume Growth Monitor — v0.39.0 R492<br/>文件: data_volume_growth_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py["(原型态 / prototype) Feedback Delay Compensator — v0.38.0 R477<br/>文件: feedback_delay_compensator.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py["(原型态 / prototype) R518: GuardInteractionTopologyMapper<br/>文件: guard_interaction_topology_mapper.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py["(原型态 / prototype) R512: GuardSelfConsistencyAuditor<br/>文件: guard_self_consistency_auditor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py["(原型态 / prototype) Human Anomaly Flood Detector — v0.40.0 R500<br/>文件: human_anomaly_flood_detector.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py["(原型态 / prototype) Latency SLO Monitor — v0.14.0 R192<br/>文件: latency_slo.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py["(原型态 / prototype) LLM Provider Integrity — v0.15.0 R217<br/>文件: llm_provider_integrity.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py["(原型态 / prototype) LLM Quality Regression — v0.12.0 R161<br/>文件: llm_quality_regression.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py["(原型态 / prototype) Model Rotation — v0.9.0 R125<br/>文件: model_rotation.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py["(原型态 / prototype) Model Rotation v2 — v0.10.0 R140<br/>文件: model_rotation_v2.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py["(原型态 / prototype) Model Version Semantic Drift Monitor — v0.39.0...<br/>文件: model_version_semantic_drift.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py["(原型态 / prototype) Numerical Stability Guard — v0.38.0 R475<br/>文件: numerical_stability_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py["(原型态 / prototype) Operational Seasonality — v0.16.0 R228<br/>文件: operational_seasonality.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py["(原型态 / prototype) Prompt Fingerprint — v0.3.0 R14<br/>文件: prompt_fingerprint.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py["(原型态 / prototype) Prompt Sanitizer — v0.10.0 R133<br/>文件: prompt_sanitizer.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py["(原型态 / prototype) Recovery Time Statistics — v0.37.0 R454<br/>文件: recovery_time_stats.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py["(原型态 / prototype) Regime Gain Scheduling — v0.37.0 R453<br/>文件: regime_gain_scheduling.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py["(原型态 / prototype) Retirement Planner — v0.10.0 R139<br/>文件: retirement_planner.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py["(原型态 / prototype) SLO Capacity Metrics — v0.17.0+ R243-R248<br/>文件: slo_capacity_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py["(原型态 / prototype) R527: SystemEntropyMonitor<br/>文件: system_entropy_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py["(原型态 / prototype) Temporal Integrity Guard — v0.38.0 R478<br/>文件: temporal_integrity_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py["(原型态 / prototype) Timezone Semantic Reasoner — v0.37.0 R456<br/>文件: timezone_semantic_reasoner.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py["(原型态 / prototype) Toil Quantification — v0.37.0 R457<br/>文件: toil_quantification.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py["(原型态 / prototype) Value Added Baseline — v0.10.0 R138<br/>文件: value_added_baseline.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py["(原型态 / prototype) Zombie FLE Detector — v0.16.0 R222<br/>文件: zombie_fle_detector.py"]
    end
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py -.->|导入依赖 / import_depends| D_SHARED
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py,src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py,src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py,src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py,src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py,src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py,src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py,src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py,src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py,src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py,src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py,src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py,src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py,src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py,src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py,src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py design
    class D_SHARED external_prod
```

#### 第 7 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        src_zephyr_feedback_loop_docs_cold_start_manual_py["(生产态 / production) cold_start_manual.py"]
        src_zephyr_feedback_loop_error_budget_py["(生产态 / production) Error Budget 状态机——monthly budget + burn_ra...<br/>文件: error_budget.py"]
        src_zephyr_feedback_loop_eval_harness_py["(生产态 / production) eval_harness.py"]
        src_zephyr_feedback_loop_evolution_auto_reward_py["(生产态 / production) Auto Reward — v0.7.0 R76<br/>文件: auto_reward.py"]
        src_zephyr_feedback_loop_evolution_conformal_prediction_py["(生产态 / production) Conformal Prediction — v0.7.0 R74<br/>文件: conformal_prediction.py"]
        src_zephyr_feedback_loop_evolution_cross_gen_validation_py["(生产态 / production) Cross-Gen Validation — v0.7.0 R78<br/>文件: cross_gen_validation.py"]
        src_zephyr_feedback_loop_evolution_dynamic_threshold_py["(生产态 / production) Dynamic Threshold — v0.7.0 R71<br/>文件: dynamic_threshold.py"]
        src_zephyr_feedback_loop_evolution_ewc_kb_review_py["(生产态 / production) EWC KB Review — v0.6.0 R51<br/>文件: ewc_kb_review.py"]
        src_zephyr_feedback_loop_evolution_failure_replay_py["(生产态 / production) Failure Replay — v0.7.0 R77<br/>文件: failure_replay.py"]
        src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py["(生产态 / production) Graduated Activation Protocol — v0.38.0 R485<br/>文件: graduated_activation_protocol.py"]
        src_zephyr_feedback_loop_evolution_hypernetwork_py["(生产态 / production) HyperNetwork — v0.7.0 R72<br/>文件: hypernetwork.py"]
        src_zephyr_feedback_loop_evolution_knowledge_distillation_py["(生产态 / production) Knowledge Distillation — v0.6.0 R52<br/>文件: knowledge_distillation.py"]
        src_zephyr_feedback_loop_evolution_online_feature_importance_py["(生产态 / production) Online Feature Importance — v0.7.0 R73<br/>文件: online_feature_importance.py"]
        src_zephyr_feedback_loop_evolution_prompt_factory_governance_py["(生产态 / production) Prompt Factory Governance — v0.16.0 R224<br/>文件: prompt_factory_governance.py"]
        src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py["(生产态 / production) R514: PromptOptimizationRegressionDetector<br/>文件: prompt_optimization_regression_detector.py"]
        src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py["(生产态 / production) R502: PromptSelfOptimizationLoop<br/>文件: prompt_self_optimization_loop.py"]
        src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py["(生产态 / production) R522: SelfModificationRateLimiter<br/>文件: self_modification_rate_limiter.py"]
        src_zephyr_feedback_loop_evolution_self_reflection_py["(生产态 / production) Self Reflection — v0.7.0 R75<br/>文件: self_reflection.py"]
        src_zephyr_feedback_loop_evolution_self_upgrade_canary_py["(生产态 / production) Self Upgrade Canary — v0.14.0 R194<br/>文件: self_upgrade_canary.py"]
        src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py["(生产态 / production) R505: SemanticIntentPreservationGuard<br/>文件: semantic_intent_preservation_guard.py"]
        src_zephyr_feedback_loop_evolution_teacher_transfer_py["(生产态 / production) Teacher Transfer — v0.6.0 R53<br/>文件: teacher_transfer.py"]
        src_zephyr_feedback_loop_evolution_training_data_gov_py["(生产态 / production) Training Data Governance — v0.14.0 R191<br/>文件: training_data_gov.py"]
        src_zephyr_feedback_loop_evolution_engine_py["(生产态 / production) evolution_engine.py"]
        src_zephyr_feedback_loop_exceptions_py["(生产态 / production) exceptions.py"]
        src_zephyr_feedback_loop_feedback_collector_py["(生产态 / production) FeedbackCollector: collect task execution feedback<br/>文件: feedback_collector.py"]
        src_zephyr_feedback_loop_fitness_functions_py["(生产态 / production) fitness_functions.py"]
        src_zephyr_feedback_loop_forensic_architectural_sod_py["(生产态 / production) Architectural SoD — v0.15.0 R205<br/>文件: architectural_sod.py"]
        src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py["(生产态 / production) Automated RCA Postmortem Generator — v0.38.0 R486<br/>文件: automated_rca_postmortem_generator.py"]
        src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py["(生产态 / production) Boot Integrity Attestation — v0.38.0 R487<br/>文件: boot_integrity_attestation.py"]
        src_zephyr_feedback_loop_forensic_crypto_bootstrap_py["(生产态 / production) Cryptographic Bootstrap — v0.15.0 R204<br/>文件: crypto_bootstrap.py"]
    end
    D_SHARED["(原型态 / prototype) D_SHARED"]
    src_zephyr_feedback_loop_evolution_engine_py -.->|导入依赖 / import_depends| D_SHARED
    D_SECURITY["(生产态 / production) D_SECURITY"]
    src_zephyr_feedback_loop_evolution_engine_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_feedback_loop_feedback_collector_py -->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    src_zephyr_feedback_loop_feedback_collector_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_feedback_loop_feedback_collector_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_fitness_functions_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_docs_cold_start_manual_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_auto_reward_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_conformal_prediction_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_cross_gen_validation_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_dynamic_threshold_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_ewc_kb_review_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_failure_replay_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_hypernetwork_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_knowledge_distillation_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_online_feature_importance_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_factory_governance_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_docs_cold_start_manual_py,src_zephyr_feedback_loop_error_budget_py,src_zephyr_feedback_loop_eval_harness_py,src_zephyr_feedback_loop_evolution_auto_reward_py,src_zephyr_feedback_loop_evolution_conformal_prediction_py,src_zephyr_feedback_loop_evolution_cross_gen_validation_py,src_zephyr_feedback_loop_evolution_dynamic_threshold_py,src_zephyr_feedback_loop_evolution_ewc_kb_review_py,src_zephyr_feedback_loop_evolution_failure_replay_py,src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py,src_zephyr_feedback_loop_evolution_hypernetwork_py,src_zephyr_feedback_loop_evolution_knowledge_distillation_py,src_zephyr_feedback_loop_evolution_online_feature_importance_py,src_zephyr_feedback_loop_evolution_prompt_factory_governance_py,src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py,src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py,src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py,src_zephyr_feedback_loop_evolution_self_reflection_py,src_zephyr_feedback_loop_evolution_self_upgrade_canary_py,src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py,src_zephyr_feedback_loop_evolution_teacher_transfer_py,src_zephyr_feedback_loop_evolution_training_data_gov_py,src_zephyr_feedback_loop_evolution_engine_py,src_zephyr_feedback_loop_exceptions_py,src_zephyr_feedback_loop_feedback_collector_py,src_zephyr_feedback_loop_fitness_functions_py,src_zephyr_feedback_loop_forensic_architectural_sod_py,src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py,src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py,src_zephyr_feedback_loop_forensic_crypto_bootstrap_py production
    class D_SECURITY,D_INTEGRATION,D_GOVERNANCE external_prod
    class D_SHARED external_design
```

#### 第 8 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        src_zephyr_feedback_loop_forensic_deterministic_replay_py["(生产态 / production) Deterministic Replay — v0.15.0 R206<br/>文件: deterministic_replay.py"]
        src_zephyr_feedback_loop_forensic_external_verifier_py["(生产态 / production) External Verifier — v0.15.0 R203<br/>文件: external_verifier.py"]
        src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py["(生产态 / production) R529: FLEUpgradeSafetyValidator<br/>文件: fle_upgrade_safety_validator.py"]
        src_zephyr_feedback_loop_forensic_guard_complexity_budget_py["(生产态 / production) R523: GuardComplexityBudget<br/>文件: guard_complexity_budget.py"]
        src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py["(生产态 / production) R521: GuardConfigurationDriftMonitor<br/>文件: guard_configuration_drift_monitor.py"]
        src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py["(生产态 / production) R531: InterruptCoherenceValidator<br/>文件: interrupt_coherence_validator.py"]
        src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py["(生产态 / production) R515: KnowledgeInjectionPreFlightVerifier<br/>文件: knowledge_injection_pre_flight_verifier.py"]
        src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py["(生产态 / production) Point-in-Time Reconstructor — v0.37.0 R465<br/>文件: point_in_time_reconstructor.py"]
        src_zephyr_feedback_loop_forensic_self_modification_audit_py["(生产态 / production) Self-Modification Audit — v0.15.0 R218<br/>文件: self_modification_audit.py"]
        src_zephyr_feedback_loop_forensic_serialization_format_tracker_py["(生产态 / production) Serialization Format Tracker — v0.39.0 R488<br/>文件: serialization_format_tracker.py"]
        src_zephyr_feedback_loop_forensic_state_migration_validator_py["(生产态 / production) State Migration Validator — v0.40.0 R497<br/>文件: state_migration_validator.py"]
        src_zephyr_feedback_loop_forensic_sub_agent_collusion_py["(生产态 / production) Sub-Agent Collusion Detector — v0.15.0 R213<br/>文件: sub_agent_collusion.py"]
        src_zephyr_feedback_loop_forensic_toctou_guard_py["(原型态 / prototype) TOCTOU Guard — v0.15.0 R207<br/>文件: toctou_guard.py"]
        src_zephyr_feedback_loop_forensic_worm_write_integrity_py["(生产态 / production) WORM Write Integrity — v0.15.0 R216<br/>文件: worm_write_integrity.py"]
        src_zephyr_feedback_loop_generator_py["(生产态 / production) generator.py"]
        src_zephyr_feedback_loop_metrics_collector_py["(生产态 / production) MetricsCollector: append-only metrics recording.<br/>文件: metrics_collector.py"]
        src_zephyr_feedback_loop_protocols_py["(生产态 / production) protocols.py"]
        src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py["(生产态 / production) Config Hot-Reload Guard — v0.40.0 R498<br/>文件: config_hot_reload_guard.py"]
        src_zephyr_feedback_loop_resilience_deadman_switch_py["(生产态 / production) Deadman Switch — v0.15.0 R212<br/>文件: deadman_switch.py"]
        src_zephyr_feedback_loop_resilience_dr_automation_py["(生产态 / production) DR Automation — v0.14.0 R187<br/>文件: dr_automation.py"]
        src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py["(生产态 / production) Graceful Degradation Planner — v0.40.0 R496<br/>文件: graceful_degradation_planner.py"]
        src_zephyr_feedback_loop_resilience_multi_instance_coord_py["(生产态 / production) Multi-Instance Coordinator — v0.14.0 R199<br/>文件: multi_instance_coord.py"]
        src_zephyr_feedback_loop_resilience_oscillation_damping_py["(生产态 / production) Oscillation Damping — v0.37.0 R450<br/>文件: oscillation_damping.py"]
        src_zephyr_feedback_loop_resilience_resource_starvation_aware_py["(生产态 / production) Resource Starvation Aware — v0.15.0 R209<br/>文件: resource_starvation_aware.py"]
        src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py["(生产态 / production) Self API Throttle Defense — v0.39.0 R491<br/>文件: self_api_throttle_defense.py"]
        src_zephyr_feedback_loop_resilience_split_brain_quorum_py["(生产态 / production) Split-Brain Quorum — v0.37.0 R451<br/>文件: split_brain_quorum.py"]
        src_zephyr_feedback_loop_scheduler_py["(生产态 / production) FLE 全链路调度器 —— collect->detect->diagnose...<br/>文件: scheduler.py"]
        src_zephyr_feedback_loop_scheduler_act_py["(生产态 / production) scheduler_act.py"]
        src_zephyr_feedback_loop_scheduler_collect_detect_py["(生产态 / production) scheduler_collect_detect.py"]
        src_zephyr_feedback_loop_scheduler_health_py["(生产态 / production) scheduler_health.py"]
    end
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_act_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_collect_detect_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_health_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_oscillation_damping_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_complexity_budget_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    D_SHARED["(原型态 / prototype) D_SHARED"]
    src_zephyr_feedback_loop_metrics_collector_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_feedback_loop_metrics_collector_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_scheduler_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_FBL_VERIFICATION["(生产态 / production) D_FBL_VERIFICATION"]
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    D_GOV_DRIFT["(生产态 / production) D_GOV_DRIFT"]
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_feedback_loop_scheduler_py -.->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_SHARED
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE"]
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_AUTONOMY_CORE
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_deterministic_replay_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_external_verifier_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_complexity_budget_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_self_modification_audit_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_serialization_format_tracker_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_state_migration_validator_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_sub_agent_collusion_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_toctou_guard_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_worm_write_integrity_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_forensic_deterministic_replay_py,src_zephyr_feedback_loop_forensic_external_verifier_py,src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py,src_zephyr_feedback_loop_forensic_guard_complexity_budget_py,src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py,src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py,src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py,src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py,src_zephyr_feedback_loop_forensic_self_modification_audit_py,src_zephyr_feedback_loop_forensic_serialization_format_tracker_py,src_zephyr_feedback_loop_forensic_state_migration_validator_py,src_zephyr_feedback_loop_forensic_sub_agent_collusion_py,src_zephyr_feedback_loop_forensic_worm_write_integrity_py,src_zephyr_feedback_loop_generator_py,src_zephyr_feedback_loop_metrics_collector_py,src_zephyr_feedback_loop_protocols_py,src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py,src_zephyr_feedback_loop_resilience_deadman_switch_py,src_zephyr_feedback_loop_resilience_dr_automation_py,src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py,src_zephyr_feedback_loop_resilience_multi_instance_coord_py,src_zephyr_feedback_loop_resilience_oscillation_damping_py,src_zephyr_feedback_loop_resilience_resource_starvation_aware_py,src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py,src_zephyr_feedback_loop_resilience_split_brain_quorum_py,src_zephyr_feedback_loop_scheduler_py,src_zephyr_feedback_loop_scheduler_act_py,src_zephyr_feedback_loop_scheduler_collect_detect_py,src_zephyr_feedback_loop_scheduler_health_py production
    class src_zephyr_feedback_loop_forensic_toctou_guard_py design
    class D_GOVERNANCE,D_FBL_VERIFICATION,D_GOV_DRIFT,D_INFRA_RUNTIME,D_AUTONOMY_CORE,D_INTEGRATION external_prod
    class D_SHARED external_design
```

#### 第 9 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        src_zephyr_feedback_loop_scheduler_safety_py["(生产态 / production) scheduler_safety.py"]
        src_zephyr_feedback_loop_security_agent_skill_guard_py["(生产态 / production) Agent Skill Guard — v0.14.0 R201<br/>文件: agent_skill_guard.py"]
        src_zephyr_feedback_loop_security_dep_cve_correlator_py["(生产态 / production) Dependency CVE Correlator — v0.14.0 R196<br/>文件: dep_cve_correlator.py"]
        src_zephyr_feedback_loop_security_metric_prompt_scanner_py["(生产态 / production) Metric-Prompt Scanner — v0.15.0 R215<br/>文件: metric_prompt_scanner.py"]
        src_zephyr_feedback_loop_security_remote_attestation_py["(生产态 / production) Remote Attestation — v0.15.0 R211<br/>文件: remote_attestation.py"]
        src_zephyr_feedback_loop_security_secret_rotation_py["(生产态 / production) Secret Rotation — v0.14.0 R189<br/>文件: secret_rotation.py"]
        src_zephyr_feedback_loop_security_wireheading_prevention_py["(生产态 / production) Wireheading Prevention — v0.37.0 R486<br/>文件: wireheading_prevention.py"]
        src_zephyr_feedback_loop_self_diagnosis_py["(生产态 / production) self_diagnosis.py — 自我诊断 (DD120, TASK-020)<br/>文件: self_diagnosis.py"]
        src_zephyr_feedback_loop_session_learner_py["(生产态 / production) session_learner.py — 在线学习 (DD114, TASK-020)<br/>文件: session_learner.py"]
        src_zephyr_feedback_loop_slo_manager_py["(生产态 / production) slo_manager.py"]
        src_zephyr_feedback_loop_template_py["(生产态 / production) template.py"]
        src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py["(生产态 / production) E2E Integration Test Pipeline — TASK-MOD-FEEDB...<br/>文件: integration_test_pipeline.py"]
        src_zephyr_feedback_loop_validator_py["(生产态 / production) validator.py"]
        tests_feedback_test_actors_init_py["(原型态 / prototype) test_actors_init.py"]
        tests_feedback_test_adaptive_param_tuning_py["(原型态 / prototype) test_adaptive_param_tuning.py"]
        tests_feedback_test_alert_desensitization_curve_py["(原型态 / prototype) test_alert_desensitization_curve.py"]
        tests_feedback_test_anomaly_clustering_py["(原型态 / prototype) test_anomaly_clustering.py"]
        tests_feedback_test_architectural_sod_py["(原型态 / prototype) test_architectural_sod.py"]
        tests_feedback_test_automated_rca_postmortem_generator_py["(原型态 / prototype) test_automated_rca_postmortem_generator.py"]
        tests_feedback_test_autoscale_remediation_py["(原型态 / prototype) test_autoscale_remediation.py"]
        tests_feedback_test_backpressure_bridge_root_py["(原型态 / prototype) test_backpressure_bridge_root.py"]
        tests_feedback_test_blast_radius_budget_py["(原型态 / prototype) test_blast_radius_budget.py"]
        tests_feedback_test_boot_integrity_attestation_py["(原型态 / prototype) test_boot_integrity_attestation.py"]
        tests_feedback_test_cascading_rollback_analyzer_py["(原型态 / prototype) test_cascading_rollback_analyzer.py"]
        tests_feedback_test_cognitive_load_py["(原型态 / prototype) test_cognitive_load.py"]
        tests_feedback_test_collaborative_learning_py["(原型态 / prototype) test_collaborative_learning.py"]
        tests_feedback_test_collectors_py["(原型态 / prototype) test_collectors.py"]
        tests_feedback_test_confidence_decomposer_py["(原型态 / prototype) test_confidence_decomposer.py"]
        tests_feedback_test_config_feedback_loop_py["(原型态 / prototype) test_config_feedback_loop.py"]
        tests_feedback_test_conformal_prediction_py["(原型态 / prototype) test_conformal_prediction.py"]
    end
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_wireheading_prevention_py
    src_zephyr_feedback_loop_validator_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_template_py
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_FBL_VERIFICATION["(生产态 / production) D_FBL_VERIFICATION"]
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    src_zephyr_feedback_loop_security_secret_rotation_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    tests_feedback_test_actors_init_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_anomaly_clustering_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_alert_desensitization_curve_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_adaptive_param_tuning_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_autoscale_remediation_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_cognitive_load_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_INFRA_RUNTIME["(原型态 / prototype) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_secret_rotation_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_agent_skill_guard_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_dep_cve_correlator_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_metric_prompt_scanner_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_remote_attestation_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_secret_rotation_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_wireheading_prevention_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py
    D_SHARED -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_secret_rotation_py
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_security_agent_skill_guard_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_scheduler_safety_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_slo_manager_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_template_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_validator_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_template_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_scheduler_safety_py,src_zephyr_feedback_loop_security_agent_skill_guard_py,src_zephyr_feedback_loop_security_dep_cve_correlator_py,src_zephyr_feedback_loop_security_metric_prompt_scanner_py,src_zephyr_feedback_loop_security_remote_attestation_py,src_zephyr_feedback_loop_security_secret_rotation_py,src_zephyr_feedback_loop_security_wireheading_prevention_py,src_zephyr_feedback_loop_self_diagnosis_py,src_zephyr_feedback_loop_session_learner_py,src_zephyr_feedback_loop_slo_manager_py,src_zephyr_feedback_loop_template_py,src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py,src_zephyr_feedback_loop_validator_py production
    class tests_feedback_test_actors_init_py,tests_feedback_test_adaptive_param_tuning_py,tests_feedback_test_alert_desensitization_curve_py,tests_feedback_test_anomaly_clustering_py,tests_feedback_test_architectural_sod_py,tests_feedback_test_automated_rca_postmortem_generator_py,tests_feedback_test_autoscale_remediation_py,tests_feedback_test_backpressure_bridge_root_py,tests_feedback_test_blast_radius_budget_py,tests_feedback_test_boot_integrity_attestation_py,tests_feedback_test_cascading_rollback_analyzer_py,tests_feedback_test_cognitive_load_py,tests_feedback_test_collaborative_learning_py,tests_feedback_test_collectors_py,tests_feedback_test_confidence_decomposer_py,tests_feedback_test_config_feedback_loop_py,tests_feedback_test_conformal_prediction_py design
    class D_GOVERNANCE,D_FBL_VERIFICATION,D_SHARED external_prod
    class D_INFRA_RUNTIME,D_AUTONOMY_CORE external_design
```

#### 第 10 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        tests_feedback_test_counterfactual_py["(原型态 / prototype) test_counterfactual.py"]
        tests_feedback_test_deadman_switch_py["(原型态 / prototype) test_deadman_switch.py"]
        tests_feedback_test_diagnosers_py["(原型态 / prototype) test_diagnosers.py"]
        tests_feedback_test_diagnosis_engine_py["(原型态 / prototype) test_diagnosis_engine.py"]
        tests_feedback_test_digital_twin_sandbox_py["(原型态 / prototype) test_digital_twin_sandbox.py"]
        tests_feedback_test_diminishing_returns_detector_py["(原型态 / prototype) test_diminishing_returns_detector.py"]
        tests_feedback_test_docs_init_py["(原型态 / prototype) test_docs_init.py"]
        tests_feedback_test_dr_automation_py["(原型态 / prototype) test_dr_automation.py"]
        tests_feedback_test_dr_resilience_metrics_py["(原型态 / prototype) test_dr_resilience_metrics.py"]
        tests_feedback_test_dry_run_sandbox_py["(原型态 / prototype) test_dry_run_sandbox.py"]
        tests_feedback_test_dynamic_threshold_py["(原型态 / prototype) test_dynamic_threshold.py"]
        tests_feedback_test_e2e_integration_health_py["(原型态 / prototype) test_e2e_integration_health.py"]
        tests_feedback_test_ebpf_monitor_py["(原型态 / prototype) test_ebpf_monitor.py"]
        tests_feedback_test_ensemble_detector_py["(原型态 / prototype) test_ensemble_detector.py"]
        tests_feedback_test_ensemble_drift_py["(原型态 / prototype) test_ensemble_drift.py"]
        tests_feedback_test_eval_harness_root_py["(原型态 / prototype) test_eval_harness_root.py"]
        tests_feedback_test_evolution_engine_root_py["(原型态 / prototype) test_evolution_engine_root.py"]
        tests_feedback_test_evolution_init_py["(原型态 / prototype) test_evolution_init.py"]
        tests_feedback_test_ewc_kb_review_py["(原型态 / prototype) test_ewc_kb_review.py"]
        tests_feedback_test_exceptions_feedback_loop_py["(原型态 / prototype) test_exceptions_feedback_loop.py"]
        tests_feedback_test_failure_replay_py["(原型态 / prototype) test_failure_replay.py"]
        tests_feedback_test_federated_protocol_py["(原型态 / prototype) test_federated_protocol.py"]
        tests_feedback_test_feedback_bridge_py["(原型态 / prototype) test_feedback_bridge.py"]
        tests_feedback_test_feedback_collector_root_py["(原型态 / prototype) test_feedback_collector_root.py"]
        tests_feedback_test_feedback_core_py["(原型态 / prototype) Test suite: feedback-loop core (FeedbackCollect...<br/>文件: test_feedback_core.py"]
        tests_feedback_test_feedback_delay_compensator_py["(原型态 / prototype) test_feedback_delay_compensator.py"]
        tests_feedback_test_feedback_loop_py["(原型态 / prototype) test_feedback_loop.py"]
        tests_feedback_test_feedback_policy_py["(原型态 / prototype) test_feedback_policy.py"]
        tests_feedback_test_feedback_self_audit_py["(原型态 / prototype) test_feedback_self_audit.py"]
        tests_feedback_test_flapping_detector_py["(原型态 / prototype) test_flapping_detector.py"]
    end
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    tests_feedback_test_diagnosers_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_counterfactual_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_diagnosis_engine_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_docs_init_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_diminishing_returns_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_FBL_VERIFICATION["(生产态 / production) D_FBL_VERIFICATION"]
    tests_feedback_test_digital_twin_sandbox_py -.->|测试依赖 / test_depends| D_FBL_VERIFICATION
    tests_feedback_test_dry_run_sandbox_py -.->|测试依赖 / test_depends| D_FBL_VERIFICATION
    tests_feedback_test_dr_resilience_metrics_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_e2e_integration_health_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_ebpf_monitor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_ensemble_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_ensemble_drift_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_federated_protocol_py -.->|测试依赖 / test_depends| D_FBL_VERIFICATION
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    tests_feedback_test_feedback_bridge_py -.->|测试依赖 / test_depends| D_GOV_AUDIT
    tests_feedback_test_feedback_policy_py -.->|测试依赖 / test_depends| D_GOV_AUDIT
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_feedback_test_counterfactual_py,tests_feedback_test_deadman_switch_py,tests_feedback_test_diagnosers_py,tests_feedback_test_diagnosis_engine_py,tests_feedback_test_digital_twin_sandbox_py,tests_feedback_test_diminishing_returns_detector_py,tests_feedback_test_docs_init_py,tests_feedback_test_dr_automation_py,tests_feedback_test_dr_resilience_metrics_py,tests_feedback_test_dry_run_sandbox_py,tests_feedback_test_dynamic_threshold_py,tests_feedback_test_e2e_integration_health_py,tests_feedback_test_ebpf_monitor_py,tests_feedback_test_ensemble_detector_py,tests_feedback_test_ensemble_drift_py,tests_feedback_test_eval_harness_root_py,tests_feedback_test_evolution_engine_root_py,tests_feedback_test_evolution_init_py,tests_feedback_test_ewc_kb_review_py,tests_feedback_test_exceptions_feedback_loop_py,tests_feedback_test_failure_replay_py,tests_feedback_test_federated_protocol_py,tests_feedback_test_feedback_bridge_py,tests_feedback_test_feedback_collector_root_py,tests_feedback_test_feedback_core_py,tests_feedback_test_feedback_delay_compensator_py,tests_feedback_test_feedback_loop_py,tests_feedback_test_feedback_policy_py,tests_feedback_test_feedback_self_audit_py,tests_feedback_test_flapping_detector_py design
    class D_GOVERNANCE,D_FBL_VERIFICATION,D_GOV_AUDIT external_prod
```

#### 第 11 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        tests_feedback_test_gamification_py["(原型态 / prototype) test_gamification.py"]
        tests_feedback_test_global_action_scheduler_py["(原型态 / prototype) test_global_action_scheduler.py"]
        tests_feedback_test_golden_test_external_py["(原型态 / prototype) test_golden_test_external.py"]
        tests_feedback_test_gradual_poisoning_detector_py["(原型态 / prototype) test_gradual_poisoning_detector.py"]
        tests_feedback_test_graduated_activation_protocol_py["(原型态 / prototype) test_graduated_activation_protocol.py"]
        tests_feedback_test_heisenbug_detector_py["(原型态 / prototype) test_heisenbug_detector.py"]
        tests_feedback_test_hypernetwork_py["(原型态 / prototype) test_hypernetwork.py"]
        tests_feedback_test_impact_predictor_py["(原型态 / prototype) test_impact_predictor.py"]
        tests_feedback_test_incident_knowledge_injector_py["(原型态 / prototype) test_incident_knowledge_injector.py"]
        tests_feedback_test_infinite_loop_detector_py["(原型态 / prototype) test_infinite_loop_detector.py"]
        tests_feedback_test_interrupt_coherence_validator_py["(原型态 / prototype) test_interrupt_coherence_validator.py"]
        tests_feedback_test_known_unknown_registry_py["(原型态 / prototype) test_known_unknown_registry.py"]
        tests_feedback_test_log_anomaly_py["(原型态 / prototype) test_log_anomaly.py"]
        tests_feedback_test_maintenance_coordinator_py["(原型态 / prototype) test_maintenance_coordinator.py"]
        tests_feedback_test_market_calendar_py["(原型态 / prototype) test_market_calendar.py"]
        tests_feedback_test_market_event_integrator_py["(原型态 / prototype) test_market_event_integrator.py"]
        tests_feedback_test_meta_guard_latency_budget_py["(原型态 / prototype) test_meta_guard_latency_budget.py"]
        tests_feedback_test_metric_cardinality_guard_py["(原型态 / prototype) test_metric_cardinality_guard.py"]
        tests_feedback_test_metrics_collector_py["(原型态 / prototype) test_metrics_collector.py"]
        tests_feedback_test_no_llm_degradation_py["(原型态 / prototype) test_no_llm_degradation.py"]
        tests_feedback_test_nonstationary_effectiveness_py["(原型态 / prototype) test_nonstationary_effectiveness.py"]
        tests_feedback_test_notification_feedback_py["(原型态 / prototype) test_notification_feedback.py"]
        tests_feedback_test_notification_personalizer_py["(原型态 / prototype) test_notification_personalizer.py"]
        tests_feedback_test_numerical_stability_guard_py["(原型态 / prototype) test_numerical_stability_guard.py"]
        tests_feedback_test_online_feature_importance_py["(原型态 / prototype) test_online_feature_importance.py"]
        tests_feedback_test_operational_seasonality_py["(原型态 / prototype) test_operational_seasonality.py"]
        tests_feedback_test_oscillation_damping_py["(原型态 / prototype) test_oscillation_damping.py"]
        tests_feedback_test_otel_adapter_py["(原型态 / prototype) test_otel_adapter.py"]
        tests_feedback_test_placebo_action_detector_py["(原型态 / prototype) test_placebo_action_detector.py"]
        tests_feedback_test_positive_feedback_defense_py["(原型态 / prototype) test_positive_feedback_defense.py"]
    end
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    tests_feedback_test_gamification_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_FBL_VERIFICATION["(生产态 / production) D_FBL_VERIFICATION"]
    tests_feedback_test_golden_test_external_py -.->|测试依赖 / test_depends| D_FBL_VERIFICATION
    tests_feedback_test_gradual_poisoning_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_heisenbug_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_impact_predictor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_infinite_loop_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_incident_knowledge_injector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_log_anomaly_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_maintenance_coordinator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_meta_guard_latency_budget_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_nonstationary_effectiveness_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_metric_cardinality_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_no_llm_degradation_py -.->|测试依赖 / test_depends| D_FBL_VERIFICATION
    tests_feedback_test_numerical_stability_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_operational_seasonality_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_feedback_test_gamification_py,tests_feedback_test_global_action_scheduler_py,tests_feedback_test_golden_test_external_py,tests_feedback_test_gradual_poisoning_detector_py,tests_feedback_test_graduated_activation_protocol_py,tests_feedback_test_heisenbug_detector_py,tests_feedback_test_hypernetwork_py,tests_feedback_test_impact_predictor_py,tests_feedback_test_incident_knowledge_injector_py,tests_feedback_test_infinite_loop_detector_py,tests_feedback_test_interrupt_coherence_validator_py,tests_feedback_test_known_unknown_registry_py,tests_feedback_test_log_anomaly_py,tests_feedback_test_maintenance_coordinator_py,tests_feedback_test_market_calendar_py,tests_feedback_test_market_event_integrator_py,tests_feedback_test_meta_guard_latency_budget_py,tests_feedback_test_metric_cardinality_guard_py,tests_feedback_test_metrics_collector_py,tests_feedback_test_no_llm_degradation_py,tests_feedback_test_nonstationary_effectiveness_py,tests_feedback_test_notification_feedback_py,tests_feedback_test_notification_personalizer_py,tests_feedback_test_numerical_stability_guard_py,tests_feedback_test_online_feature_importance_py,tests_feedback_test_operational_seasonality_py,tests_feedback_test_oscillation_damping_py,tests_feedback_test_otel_adapter_py,tests_feedback_test_placebo_action_detector_py,tests_feedback_test_positive_feedback_defense_py design
    class D_GOVERNANCE,D_FBL_VERIFICATION external_prod
```

#### 第 12 页 / 共 12 页

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        tests_feedback_test_protocols_py["(原型态 / prototype) test_protocols.py"]
        tests_feedback_test_recovery_time_stats_py["(原型态 / prototype) test_recovery_time_stats.py"]
        tests_feedback_test_recursive_diagnosis_trust_evaluator_py["(原型态 / prototype) test_recursive_diagnosis_trust_evaluator.py"]
        tests_feedback_test_regulatory_audit_py["(原型态 / prototype) test_regulatory_audit.py"]
        tests_feedback_test_resolution_tracker_py["(原型态 / prototype) test_resolution_tracker.py"]
        tests_feedback_test_retirement_planner_py["(原型态 / prototype) test_retirement_planner.py"]
        tests_feedback_test_rumor_noise_filter_py["(原型态 / prototype) test_rumor_noise_filter.py"]
        tests_feedback_test_runbook_executor_py["(原型态 / prototype) test_runbook_executor.py"]
        tests_feedback_test_scheduler_collect_detect_py["(原型态 / prototype) test_scheduler_collect_detect.py"]
        tests_feedback_test_scheduler_health_py["(原型态 / prototype) test_scheduler_health.py"]
        tests_feedback_test_scheduler_integration_py["(原型态 / prototype) Integration tests: FeedbackLoopScheduler start/...<br/>文件: test_scheduler_integration.py"]
        tests_feedback_test_secondary_alert_channel_py["(原型态 / prototype) test_secondary_alert_channel.py"]
        tests_feedback_test_silent_corruption_detector_py["(原型态 / prototype) test_silent_corruption_detector.py"]
        tests_feedback_test_slo_capacity_metrics_py["(原型态 / prototype) test_slo_capacity_metrics.py"]
        tests_feedback_test_slo_manager_root_py["(原型态 / prototype) test_slo_manager_root.py"]
        tests_feedback_test_state_migration_validator_py["(原型态 / prototype) test_state_migration_validator.py"]
        tests_feedback_test_stochastic_diagnosis_verifier_py["(原型态 / prototype) test_stochastic_diagnosis_verifier.py"]
        tests_feedback_test_stochastic_diagnosis_verifier_v2_py["(原型态 / prototype) test_stochastic_diagnosis_verifier_v2.py"]
        tests_feedback_test_synthetic_anomaly_generator_py["(原型态 / prototype) test_synthetic_anomaly_generator.py"]
        tests_feedback_test_system_entropy_monitor_py["(原型态 / prototype) test_system_entropy_monitor.py"]
        tests_feedback_test_teacher_transfer_py["(原型态 / prototype) test_teacher_transfer.py"]
        tests_feedback_test_timezone_semantic_reasoner_py["(原型态 / prototype) test_timezone_semantic_reasoner.py"]
        tests_feedback_test_token_finops_py["(原型态 / prototype) test_token_finops.py"]
        tests_feedback_test_training_data_gov_py["(原型态 / prototype) test_training_data_gov.py"]
        tests_feedback_test_trend_cycle_separator_py["(原型态 / prototype) test_trend_cycle_separator.py"]
        tests_feedback_test_validator_py["(原型态 / prototype) test_validator.py"]
        tests_feedback_test_vertical_self_assessment_py["(原型态 / prototype) test_vertical_self_assessment.py"]
        tests_feedback_test_worm_write_integrity_py["(原型态 / prototype) test_worm_write_integrity.py"]
    end
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    tests_feedback_test_recovery_time_stats_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_recursive_diagnosis_trust_evaluator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_resolution_tracker_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_regulatory_audit_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_retirement_planner_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_runbook_executor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_rumor_noise_filter_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_scheduler_collect_detect_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_scheduler_collect_detect_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_slo_capacity_metrics_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_silent_corruption_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_FBL_VERIFICATION["(生产态 / production) D_FBL_VERIFICATION"]
    tests_feedback_test_stochastic_diagnosis_verifier_py -.->|测试依赖 / test_depends| D_FBL_VERIFICATION
    tests_feedback_test_stochastic_diagnosis_verifier_v2_py -.->|测试依赖 / test_depends| D_FBL_VERIFICATION
    tests_feedback_test_system_entropy_monitor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_synthetic_anomaly_generator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_feedback_test_protocols_py,tests_feedback_test_recovery_time_stats_py,tests_feedback_test_recursive_diagnosis_trust_evaluator_py,tests_feedback_test_regulatory_audit_py,tests_feedback_test_resolution_tracker_py,tests_feedback_test_retirement_planner_py,tests_feedback_test_rumor_noise_filter_py,tests_feedback_test_runbook_executor_py,tests_feedback_test_scheduler_collect_detect_py,tests_feedback_test_scheduler_health_py,tests_feedback_test_scheduler_integration_py,tests_feedback_test_secondary_alert_channel_py,tests_feedback_test_silent_corruption_detector_py,tests_feedback_test_slo_capacity_metrics_py,tests_feedback_test_slo_manager_root_py,tests_feedback_test_state_migration_validator_py,tests_feedback_test_stochastic_diagnosis_verifier_py,tests_feedback_test_stochastic_diagnosis_verifier_v2_py,tests_feedback_test_synthetic_anomaly_generator_py,tests_feedback_test_system_entropy_monitor_py,tests_feedback_test_teacher_transfer_py,tests_feedback_test_timezone_semantic_reasoner_py,tests_feedback_test_token_finops_py,tests_feedback_test_training_data_gov_py,tests_feedback_test_trend_cycle_separator_py,tests_feedback_test_validator_py,tests_feedback_test_vertical_self_assessment_py,tests_feedback_test_worm_write_integrity_py design
    class D_GOVERNANCE,D_FBL_VERIFICATION external_prod
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 107 个，24 条域内依赖）。

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        src_zephyr_feedback_loop_init_py["(生产态 / production) Feedback Loop Engine — MOD-FEEDBACK_LOOP.<br/>文件: __init__.py"]
        src_zephyr_feedback_loop_gen_inherited_py["(生产态 / production) _gen_inherited.py"]
        src_zephyr_feedback_loop_actors_action_selector_py["(生产态 / production) action_selector.py"]
        src_zephyr_feedback_loop_actors_agent_lifecycle_py["(生产态 / production) Agent Lifecycle Manager — v0.12.0 R159c<br/>文件: agent_lifecycle.py"]
        src_zephyr_feedback_loop_actors_api_version_contract_py["(生产态 / production) API Version Contract — v0.14.0 R188<br/>文件: api_version_contract.py"]
        src_zephyr_feedback_loop_actors_global_action_scheduler_py["(生产态 / production) Global Action Scheduler — v0.16.0 R226<br/>文件: global_action_scheduler.py"]
        src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py["(生产态 / production) Incident Priority Triage Automator — v0.37.0 R463<br/>文件: incident_priority_triage_automator.py"]
        src_zephyr_feedback_loop_actors_intent_driven_ops_py["(生产态 / production) Intent-Driven Ops — v0.12.0 R159<br/>文件: intent_driven_ops.py"]
        src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py["(生产态 / production) Multi-Agent Orchestrator — v0.12.0 R159b<br/>文件: multi_agent_orchestrator.py"]
        src_zephyr_feedback_loop_actors_notification_personalizer_py["(生产态 / production) Notification Personalizer — v0.6.0 R67<br/>文件: notification_personalizer.py"]
        src_zephyr_feedback_loop_actors_owner_absence_escalation_py["(生产态 / production) Owner Absence Escalation — v0.37.0 R462<br/>文件: owner_absence_escalation.py"]
        src_zephyr_feedback_loop_actors_secondary_alert_channel_py["(生产态 / production) Secondary Alert Channel — v0.37.0 R461<br/>文件: secondary_alert_channel.py"]
        src_zephyr_feedback_loop_auto_evolution_py["(生产态 / production) auto_evolution.py"]
        src_zephyr_feedback_loop_backpressure_bridge_py["(生产态 / production) FLE -> Pipeline 背压桥接（CTR-BP-001~003）<br/>文件: backpressure_bridge.py"]
        src_zephyr_feedback_loop_collectors_calendar_adapter_py["(生产态 / production) Calendar Adapter — v0.8.0 R102b<br/>文件: calendar_adapter.py"]
        src_zephyr_feedback_loop_collectors_config_timeline_py["(生产态 / production) Config Timeline — v0.8.0 R99<br/>文件: config_timeline.py"]
        src_zephyr_feedback_loop_collectors_data_quality_validator_py["(生产态 / production) Data Quality Validator — v0.9.0 R110<br/>文件: data_quality_validator.py"]
        src_zephyr_feedback_loop_collectors_financial_stratification_py["(生产态 / production) Financial Stratification — v0.5.0 R50<br/>文件: financial_stratification.py"]
        src_zephyr_feedback_loop_collectors_kb_provenance_py["(生产态 / production) KB Provenance — v0.10.0 R136<br/>文件: kb_provenance.py"]
        src_zephyr_feedback_loop_collectors_knowledge_capture_py["(生产态 / production) Knowledge Capture — v0.4.0 R30<br/>文件: knowledge_capture.py"]
        src_zephyr_feedback_loop_collectors_knowledge_freshness_py["(生产态 / production) Knowledge Freshness — v0.5.0 R47<br/>文件: knowledge_freshness.py"]
        src_zephyr_feedback_loop_collectors_knowledge_injection_py["(生产态 / production) Knowledge Injection — v0.8.0 R102<br/>文件: knowledge_injection.py"]
        src_zephyr_feedback_loop_collectors_knowledge_packaging_py["(生产态 / production) Knowledge Packaging — v0.9.0 R123<br/>文件: knowledge_packaging.py"]
        src_zephyr_feedback_loop_collectors_known_unknown_registry_py["(生产态 / production) Known-Unknown Registry — v0.16.0 R229<br/>文件: known_unknown_registry.py"]
        src_zephyr_feedback_loop_collectors_llm_cost_accounting_py["(生产态 / production) LLM Cost Accounting — v0.4.0 R35<br/>文件: llm_cost_accounting.py"]
        src_zephyr_feedback_loop_collectors_market_calendar_py["(生产态 / production) Market Calendar — v0.5.0 R48<br/>文件: market_calendar.py"]
        src_zephyr_feedback_loop_collectors_market_event_integrator_py["(生产态 / production) Market Event Integrator — v0.14.0 R197<br/>文件: market_event_integrator.py"]
        src_zephyr_feedback_loop_collectors_notification_feedback_py["(生产态 / production) Notification Feedback — v0.9.0 R118<br/>文件: notification_feedback.py"]
        src_zephyr_feedback_loop_collectors_schema_evolution_py["(生产态 / production) Schema Evolution — v0.9.0 R111<br/>文件: schema_evolution.py"]
        src_zephyr_feedback_loop_collectors_schema_migration_py["(生产态 / production) Schema Migration — v0.14.0 R190<br/>文件: schema_migration.py"]
        src_zephyr_feedback_loop_collectors_temporal_event_store_py["(生产态 / production) Temporal Event Store — v0.3.0 R9<br/>文件: temporal_event_store.py"]
        src_zephyr_feedback_loop_collectors_token_finops_py["(生产态 / production) Token FinOps — v0.12.0 R162<br/>文件: token_finops.py"]
        src_zephyr_feedback_loop_config_py["(生产态 / production) config.py"]
        src_zephyr_feedback_loop_db_bridge_py["(生产态 / production) FLE DB契约适配器 — 通过规范zephyr.governance.s...<br/>文件: db_bridge.py"]
        src_zephyr_feedback_loop_decision_engine_py["(生产态 / production) Feedback Loop Decision Engine<br/>文件: decision_engine.py"]
        src_zephyr_feedback_loop_docs_cold_start_manual_py["(生产态 / production) cold_start_manual.py"]
        src_zephyr_feedback_loop_error_budget_py["(生产态 / production) Error Budget 状态机——monthly budget + burn_ra...<br/>文件: error_budget.py"]
        src_zephyr_feedback_loop_eval_harness_py["(生产态 / production) eval_harness.py"]
        src_zephyr_feedback_loop_evolution_auto_reward_py["(生产态 / production) Auto Reward — v0.7.0 R76<br/>文件: auto_reward.py"]
        src_zephyr_feedback_loop_evolution_conformal_prediction_py["(生产态 / production) Conformal Prediction — v0.7.0 R74<br/>文件: conformal_prediction.py"]
        src_zephyr_feedback_loop_evolution_cross_gen_validation_py["(生产态 / production) Cross-Gen Validation — v0.7.0 R78<br/>文件: cross_gen_validation.py"]
        src_zephyr_feedback_loop_evolution_dynamic_threshold_py["(生产态 / production) Dynamic Threshold — v0.7.0 R71<br/>文件: dynamic_threshold.py"]
        src_zephyr_feedback_loop_evolution_ewc_kb_review_py["(生产态 / production) EWC KB Review — v0.6.0 R51<br/>文件: ewc_kb_review.py"]
        src_zephyr_feedback_loop_evolution_failure_replay_py["(生产态 / production) Failure Replay — v0.7.0 R77<br/>文件: failure_replay.py"]
        src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py["(生产态 / production) Graduated Activation Protocol — v0.38.0 R485<br/>文件: graduated_activation_protocol.py"]
        src_zephyr_feedback_loop_evolution_hypernetwork_py["(生产态 / production) HyperNetwork — v0.7.0 R72<br/>文件: hypernetwork.py"]
        src_zephyr_feedback_loop_evolution_knowledge_distillation_py["(生产态 / production) Knowledge Distillation — v0.6.0 R52<br/>文件: knowledge_distillation.py"]
        src_zephyr_feedback_loop_evolution_online_feature_importance_py["(生产态 / production) Online Feature Importance — v0.7.0 R73<br/>文件: online_feature_importance.py"]
        src_zephyr_feedback_loop_evolution_prompt_factory_governance_py["(生产态 / production) Prompt Factory Governance — v0.16.0 R224<br/>文件: prompt_factory_governance.py"]
        src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py["(生产态 / production) R514: PromptOptimizationRegressionDetector<br/>文件: prompt_optimization_regression_detector.py"]
        src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py["(生产态 / production) R502: PromptSelfOptimizationLoop<br/>文件: prompt_self_optimization_loop.py"]
        src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py["(生产态 / production) R522: SelfModificationRateLimiter<br/>文件: self_modification_rate_limiter.py"]
        src_zephyr_feedback_loop_evolution_self_reflection_py["(生产态 / production) Self Reflection — v0.7.0 R75<br/>文件: self_reflection.py"]
        src_zephyr_feedback_loop_evolution_self_upgrade_canary_py["(生产态 / production) Self Upgrade Canary — v0.14.0 R194<br/>文件: self_upgrade_canary.py"]
        src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py["(生产态 / production) R505: SemanticIntentPreservationGuard<br/>文件: semantic_intent_preservation_guard.py"]
        src_zephyr_feedback_loop_evolution_teacher_transfer_py["(生产态 / production) Teacher Transfer — v0.6.0 R53<br/>文件: teacher_transfer.py"]
        src_zephyr_feedback_loop_evolution_training_data_gov_py["(生产态 / production) Training Data Governance — v0.14.0 R191<br/>文件: training_data_gov.py"]
        src_zephyr_feedback_loop_evolution_engine_py["(生产态 / production) evolution_engine.py"]
        src_zephyr_feedback_loop_exceptions_py["(生产态 / production) exceptions.py"]
        src_zephyr_feedback_loop_feedback_collector_py["(生产态 / production) FeedbackCollector: collect task execution feedback<br/>文件: feedback_collector.py"]
        src_zephyr_feedback_loop_fitness_functions_py["(生产态 / production) fitness_functions.py"]
        src_zephyr_feedback_loop_forensic_architectural_sod_py["(生产态 / production) Architectural SoD — v0.15.0 R205<br/>文件: architectural_sod.py"]
        src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py["(生产态 / production) Automated RCA Postmortem Generator — v0.38.0 R486<br/>文件: automated_rca_postmortem_generator.py"]
        src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py["(生产态 / production) Boot Integrity Attestation — v0.38.0 R487<br/>文件: boot_integrity_attestation.py"]
        src_zephyr_feedback_loop_forensic_crypto_bootstrap_py["(生产态 / production) Cryptographic Bootstrap — v0.15.0 R204<br/>文件: crypto_bootstrap.py"]
        src_zephyr_feedback_loop_forensic_deterministic_replay_py["(生产态 / production) Deterministic Replay — v0.15.0 R206<br/>文件: deterministic_replay.py"]
        src_zephyr_feedback_loop_forensic_external_verifier_py["(生产态 / production) External Verifier — v0.15.0 R203<br/>文件: external_verifier.py"]
        src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py["(生产态 / production) R529: FLEUpgradeSafetyValidator<br/>文件: fle_upgrade_safety_validator.py"]
        src_zephyr_feedback_loop_forensic_guard_complexity_budget_py["(生产态 / production) R523: GuardComplexityBudget<br/>文件: guard_complexity_budget.py"]
        src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py["(生产态 / production) R521: GuardConfigurationDriftMonitor<br/>文件: guard_configuration_drift_monitor.py"]
        src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py["(生产态 / production) R531: InterruptCoherenceValidator<br/>文件: interrupt_coherence_validator.py"]
        src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py["(生产态 / production) R515: KnowledgeInjectionPreFlightVerifier<br/>文件: knowledge_injection_pre_flight_verifier.py"]
        src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py["(生产态 / production) Point-in-Time Reconstructor — v0.37.0 R465<br/>文件: point_in_time_reconstructor.py"]
        src_zephyr_feedback_loop_forensic_self_modification_audit_py["(生产态 / production) Self-Modification Audit — v0.15.0 R218<br/>文件: self_modification_audit.py"]
        src_zephyr_feedback_loop_forensic_serialization_format_tracker_py["(生产态 / production) Serialization Format Tracker — v0.39.0 R488<br/>文件: serialization_format_tracker.py"]
        src_zephyr_feedback_loop_forensic_state_migration_validator_py["(生产态 / production) State Migration Validator — v0.40.0 R497<br/>文件: state_migration_validator.py"]
        src_zephyr_feedback_loop_forensic_sub_agent_collusion_py["(生产态 / production) Sub-Agent Collusion Detector — v0.15.0 R213<br/>文件: sub_agent_collusion.py"]
        src_zephyr_feedback_loop_forensic_worm_write_integrity_py["(生产态 / production) WORM Write Integrity — v0.15.0 R216<br/>文件: worm_write_integrity.py"]
        src_zephyr_feedback_loop_generator_py["(生产态 / production) generator.py"]
        src_zephyr_feedback_loop_metrics_collector_py["(生产态 / production) MetricsCollector: append-only metrics recording.<br/>文件: metrics_collector.py"]
        src_zephyr_feedback_loop_protocols_py["(生产态 / production) protocols.py"]
        src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py["(生产态 / production) Config Hot-Reload Guard — v0.40.0 R498<br/>文件: config_hot_reload_guard.py"]
        src_zephyr_feedback_loop_resilience_deadman_switch_py["(生产态 / production) Deadman Switch — v0.15.0 R212<br/>文件: deadman_switch.py"]
        src_zephyr_feedback_loop_resilience_dr_automation_py["(生产态 / production) DR Automation — v0.14.0 R187<br/>文件: dr_automation.py"]
        src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py["(生产态 / production) Graceful Degradation Planner — v0.40.0 R496<br/>文件: graceful_degradation_planner.py"]
        src_zephyr_feedback_loop_resilience_multi_instance_coord_py["(生产态 / production) Multi-Instance Coordinator — v0.14.0 R199<br/>文件: multi_instance_coord.py"]
        src_zephyr_feedback_loop_resilience_oscillation_damping_py["(生产态 / production) Oscillation Damping — v0.37.0 R450<br/>文件: oscillation_damping.py"]
        src_zephyr_feedback_loop_resilience_resource_starvation_aware_py["(生产态 / production) Resource Starvation Aware — v0.15.0 R209<br/>文件: resource_starvation_aware.py"]
        src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py["(生产态 / production) Self API Throttle Defense — v0.39.0 R491<br/>文件: self_api_throttle_defense.py"]
        src_zephyr_feedback_loop_resilience_split_brain_quorum_py["(生产态 / production) Split-Brain Quorum — v0.37.0 R451<br/>文件: split_brain_quorum.py"]
        src_zephyr_feedback_loop_scheduler_py["(生产态 / production) FLE 全链路调度器 —— collect->detect->diagnose...<br/>文件: scheduler.py"]
        src_zephyr_feedback_loop_scheduler_act_py["(生产态 / production) scheduler_act.py"]
        src_zephyr_feedback_loop_scheduler_collect_detect_py["(生产态 / production) scheduler_collect_detect.py"]
        src_zephyr_feedback_loop_scheduler_health_py["(生产态 / production) scheduler_health.py"]
        src_zephyr_feedback_loop_scheduler_safety_py["(生产态 / production) scheduler_safety.py"]
        src_zephyr_feedback_loop_security_agent_skill_guard_py["(生产态 / production) Agent Skill Guard — v0.14.0 R201<br/>文件: agent_skill_guard.py"]
        src_zephyr_feedback_loop_security_dep_cve_correlator_py["(生产态 / production) Dependency CVE Correlator — v0.14.0 R196<br/>文件: dep_cve_correlator.py"]
        src_zephyr_feedback_loop_security_metric_prompt_scanner_py["(生产态 / production) Metric-Prompt Scanner — v0.15.0 R215<br/>文件: metric_prompt_scanner.py"]
        src_zephyr_feedback_loop_security_remote_attestation_py["(生产态 / production) Remote Attestation — v0.15.0 R211<br/>文件: remote_attestation.py"]
        src_zephyr_feedback_loop_security_secret_rotation_py["(生产态 / production) Secret Rotation — v0.14.0 R189<br/>文件: secret_rotation.py"]
        src_zephyr_feedback_loop_security_wireheading_prevention_py["(生产态 / production) Wireheading Prevention — v0.37.0 R486<br/>文件: wireheading_prevention.py"]
        src_zephyr_feedback_loop_self_diagnosis_py["(生产态 / production) self_diagnosis.py — 自我诊断 (DD120, TASK-020)<br/>文件: self_diagnosis.py"]
        src_zephyr_feedback_loop_session_learner_py["(生产态 / production) session_learner.py — 在线学习 (DD114, TASK-020)<br/>文件: session_learner.py"]
        src_zephyr_feedback_loop_slo_manager_py["(生产态 / production) slo_manager.py"]
        src_zephyr_feedback_loop_template_py["(生产态 / production) template.py"]
        src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py["(生产态 / production) E2E Integration Test Pipeline — TASK-MOD-FEEDB...<br/>文件: integration_test_pipeline.py"]
        src_zephyr_feedback_loop_validator_py["(生产态 / production) validator.py"]
    end
    src_zephyr_feedback_loop_auto_evolution_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_backpressure_bridge_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_decision_engine_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_generator_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_template_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_act_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_safety_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_collect_detect_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_health_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_oscillation_damping_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_wireheading_prevention_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_complexity_budget_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_validator_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_template_py
    src_zephyr_feedback_loop_actors_action_selector_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    src_zephyr_feedback_loop_backpressure_bridge_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_feedback_loop_db_bridge_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_SHARED["(原型态 / prototype) D_SHARED"]
    src_zephyr_feedback_loop_evolution_engine_py -.->|导入依赖 / import_depends| D_SHARED
    D_SECURITY["(生产态 / production) D_SECURITY"]
    src_zephyr_feedback_loop_evolution_engine_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_feedback_loop_feedback_collector_py -->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    src_zephyr_feedback_loop_feedback_collector_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_feedback_loop_feedback_collector_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_fitness_functions_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_metrics_collector_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_metrics_collector_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_scheduler_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_FBL_VERIFICATION["(生产态 / production) D_FBL_VERIFICATION"]
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    D_INFRA_RUNTIME -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_secret_rotation_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_agent_lifecycle_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_api_version_contract_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_global_action_scheduler_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_intent_driven_ops_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_notification_personalizer_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_owner_absence_escalation_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_secondary_alert_channel_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_calendar_adapter_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_config_timeline_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_data_quality_validator_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_financial_stratification_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_init_py,src_zephyr_feedback_loop_gen_inherited_py,src_zephyr_feedback_loop_actors_action_selector_py,src_zephyr_feedback_loop_actors_agent_lifecycle_py,src_zephyr_feedback_loop_actors_api_version_contract_py,src_zephyr_feedback_loop_actors_global_action_scheduler_py,src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py,src_zephyr_feedback_loop_actors_intent_driven_ops_py,src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py,src_zephyr_feedback_loop_actors_notification_personalizer_py,src_zephyr_feedback_loop_actors_owner_absence_escalation_py,src_zephyr_feedback_loop_actors_secondary_alert_channel_py,src_zephyr_feedback_loop_auto_evolution_py,src_zephyr_feedback_loop_backpressure_bridge_py,src_zephyr_feedback_loop_collectors_calendar_adapter_py,src_zephyr_feedback_loop_collectors_config_timeline_py,src_zephyr_feedback_loop_collectors_data_quality_validator_py,src_zephyr_feedback_loop_collectors_financial_stratification_py,src_zephyr_feedback_loop_collectors_kb_provenance_py,src_zephyr_feedback_loop_collectors_knowledge_capture_py,src_zephyr_feedback_loop_collectors_knowledge_freshness_py,src_zephyr_feedback_loop_collectors_knowledge_injection_py,src_zephyr_feedback_loop_collectors_knowledge_packaging_py,src_zephyr_feedback_loop_collectors_known_unknown_registry_py,src_zephyr_feedback_loop_collectors_llm_cost_accounting_py,src_zephyr_feedback_loop_collectors_market_calendar_py,src_zephyr_feedback_loop_collectors_market_event_integrator_py,src_zephyr_feedback_loop_collectors_notification_feedback_py,src_zephyr_feedback_loop_collectors_schema_evolution_py,src_zephyr_feedback_loop_collectors_schema_migration_py,src_zephyr_feedback_loop_collectors_temporal_event_store_py,src_zephyr_feedback_loop_collectors_token_finops_py,src_zephyr_feedback_loop_config_py,src_zephyr_feedback_loop_db_bridge_py,src_zephyr_feedback_loop_decision_engine_py,src_zephyr_feedback_loop_docs_cold_start_manual_py,src_zephyr_feedback_loop_error_budget_py,src_zephyr_feedback_loop_eval_harness_py,src_zephyr_feedback_loop_evolution_auto_reward_py,src_zephyr_feedback_loop_evolution_conformal_prediction_py,src_zephyr_feedback_loop_evolution_cross_gen_validation_py,src_zephyr_feedback_loop_evolution_dynamic_threshold_py,src_zephyr_feedback_loop_evolution_ewc_kb_review_py,src_zephyr_feedback_loop_evolution_failure_replay_py,src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py,src_zephyr_feedback_loop_evolution_hypernetwork_py,src_zephyr_feedback_loop_evolution_knowledge_distillation_py,src_zephyr_feedback_loop_evolution_online_feature_importance_py,src_zephyr_feedback_loop_evolution_prompt_factory_governance_py,src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py,src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py,src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py,src_zephyr_feedback_loop_evolution_self_reflection_py,src_zephyr_feedback_loop_evolution_self_upgrade_canary_py,src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py,src_zephyr_feedback_loop_evolution_teacher_transfer_py,src_zephyr_feedback_loop_evolution_training_data_gov_py,src_zephyr_feedback_loop_evolution_engine_py,src_zephyr_feedback_loop_exceptions_py,src_zephyr_feedback_loop_feedback_collector_py,src_zephyr_feedback_loop_fitness_functions_py,src_zephyr_feedback_loop_forensic_architectural_sod_py,src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py,src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py,src_zephyr_feedback_loop_forensic_crypto_bootstrap_py,src_zephyr_feedback_loop_forensic_deterministic_replay_py,src_zephyr_feedback_loop_forensic_external_verifier_py,src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py,src_zephyr_feedback_loop_forensic_guard_complexity_budget_py,src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py,src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py,src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py,src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py,src_zephyr_feedback_loop_forensic_self_modification_audit_py,src_zephyr_feedback_loop_forensic_serialization_format_tracker_py,src_zephyr_feedback_loop_forensic_state_migration_validator_py,src_zephyr_feedback_loop_forensic_sub_agent_collusion_py,src_zephyr_feedback_loop_forensic_worm_write_integrity_py,src_zephyr_feedback_loop_generator_py,src_zephyr_feedback_loop_metrics_collector_py,src_zephyr_feedback_loop_protocols_py,src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py,src_zephyr_feedback_loop_resilience_deadman_switch_py,src_zephyr_feedback_loop_resilience_dr_automation_py,src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py,src_zephyr_feedback_loop_resilience_multi_instance_coord_py,src_zephyr_feedback_loop_resilience_oscillation_damping_py,src_zephyr_feedback_loop_resilience_resource_starvation_aware_py,src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py,src_zephyr_feedback_loop_resilience_split_brain_quorum_py,src_zephyr_feedback_loop_scheduler_py,src_zephyr_feedback_loop_scheduler_act_py,src_zephyr_feedback_loop_scheduler_collect_detect_py,src_zephyr_feedback_loop_scheduler_health_py,src_zephyr_feedback_loop_scheduler_safety_py,src_zephyr_feedback_loop_security_agent_skill_guard_py,src_zephyr_feedback_loop_security_dep_cve_correlator_py,src_zephyr_feedback_loop_security_metric_prompt_scanner_py,src_zephyr_feedback_loop_security_remote_attestation_py,src_zephyr_feedback_loop_security_secret_rotation_py,src_zephyr_feedback_loop_security_wireheading_prevention_py,src_zephyr_feedback_loop_self_diagnosis_py,src_zephyr_feedback_loop_session_learner_py,src_zephyr_feedback_loop_slo_manager_py,src_zephyr_feedback_loop_template_py,src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py,src_zephyr_feedback_loop_validator_py production
    class D_INFRA_RUNTIME,D_GOVERNANCE,D_SECURITY,D_INTEGRATION,D_FBL_VERIFICATION external_prod
    class D_SHARED external_design
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 251 个，130 条域内依赖）。

```mermaid
graph TD
    subgraph D_FEEDBACK_LOOP["D_FEEDBACK_LOOP 反馈循环引擎"]
        src_zephyr_feedback_loop_actors_saga_compensator_py["(原型态 / prototype) Saga Compensator — v0.3.0 R19b<br/>文件: saga_compensator.py"]
        src_zephyr_feedback_loop_alert_dispatcher_py["(原型态 / prototype) FLE->Orc 告警分派器 — dispatch() 生产者<br/>文件: alert_dispatcher.py"]
        src_zephyr_feedback_loop_collectors_feedback_collector_py["(原型态 / prototype) feedback_collector.py"]
        src_zephyr_feedback_loop_collectors_metrics_collector_py["(原型态 / prototype) metrics_collector.py"]
        src_zephyr_feedback_loop_core_py["(原型态 / prototype) FeedbackLoop core — 反馈闭环核心类。<br/>文件: core.py"]
        src_zephyr_feedback_loop_db_writer_py["(原型态 / prototype) FLE 持久化写入器 — 写 metrics/alerts/dispatch_...<br/>文件: db_writer.py"]
        src_zephyr_feedback_loop_detectors_anomaly_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_detectors_anomaly_anomaly_clustering_py["(原型态 / prototype) Anomaly Clustering — v0.9.0 R119<br/>文件: anomaly_clustering.py"]
        src_zephyr_feedback_loop_detectors_anomaly_anomaly_detector_py["(原型态 / prototype) anomaly_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_emergent_behavior_detector_py["(原型态 / prototype) Emergent Behavior Detector — v0.38.0 R473<br/>文件: emergent_behavior_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_flapping_detector_py["(原型态 / prototype) Flapping Detector — v0.40.0 R494<br/>文件: flapping_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_heisenbug_detector_py["(原型态 / prototype) Heisenbug Detector — v0.38.0 R470<br/>文件: heisenbug_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_infinite_loop_detector_py["(原型态 / prototype) Infinite Loop Detector — v0.15.0 R219<br/>文件: infinite_loop_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_intermittent_failure_pattern_py["(原型态 / prototype) Intermittent Failure Pattern Detector — v0.40....<br/>文件: intermittent_failure_pattern.py"]
        src_zephyr_feedback_loop_detectors_anomaly_log_anomaly_py["(原型态 / prototype) Log Anomaly Detector — v0.6.0 R61<br/>文件: log_anomaly.py"]
        src_zephyr_feedback_loop_detectors_anomaly_silent_corruption_detector_py["(原型态 / prototype) Silent Corruption Detector — v0.40.0 R499<br/>文件: silent_corruption_detector.py"]
        src_zephyr_feedback_loop_detectors_anomaly_synthetic_anomaly_generator_py["(原型态 / prototype) Synthetic Anomaly Generator — v0.9.0 R112<br/>文件: synthetic_anomaly_generator.py"]
        src_zephyr_feedback_loop_detectors_anomaly_temporal_pattern_py["(原型态 / prototype) Temporal Pattern Detector — v0.12.0 R164<br/>文件: temporal_pattern.py"]
        src_zephyr_feedback_loop_detectors_correlation_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_detectors_correlation_action_efficacy_decay_detector_py["(原型态 / prototype) R507: ActionEfficacyDecayDetector<br/>文件: action_efficacy_decay_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_action_interaction_detector_py["(原型态 / prototype) Action Interaction Detector — v0.38.0 R472<br/>文件: action_interaction_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_action_side_effect_cumulative_detector_py["(原型态 / prototype) R526: ActionSideEffectCumulativeDetector<br/>文件: action_side_effect_cumulative_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_agent_trajectory_anomaly_detector_py["(原型态 / prototype) R503: AgentTrajectoryAnomalyDetector<br/>文件: agent_trajectory_anomaly_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_cross_signal_validator_py["(原型态 / prototype) Cross-Signal Validator — v0.6.0 R63<br/>文件: cross_signal_validator.py"]
        src_zephyr_feedback_loop_detectors_correlation_cross_system_correlator_py["(原型态 / prototype) Cross-System Correlator — v0.13.0 R185<br/>文件: cross_system_correlator.py"]
        src_zephyr_feedback_loop_detectors_correlation_decision_provenance_py["(原型态 / prototype) Decision Provenance — v0.12.0 R166<br/>文件: decision_provenance.py"]
        src_zephyr_feedback_loop_detectors_correlation_dependency_freshness_monitor_py["(原型态 / prototype) Dependency Freshness Monitor — v0.38.0 R474<br/>文件: dependency_freshness_monitor.py"]
        src_zephyr_feedback_loop_detectors_correlation_ensemble_detector_py["(原型态 / prototype) Ensemble Detector — v0.4.0 R21<br/>文件: ensemble_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_external_health_py["(原型态 / prototype) External Health Monitor — v0.14.0 R193<br/>文件: external_health.py"]
        src_zephyr_feedback_loop_detectors_correlation_external_validation_checkpoint_py["(原型态 / prototype) R524: ExternalValidationCheckpoint<br/>文件: external_validation_checkpoint.py"]
        src_zephyr_feedback_loop_detectors_correlation_fle_performance_regression_detector_py["(原型态 / prototype) R532: FLEPerformanceRegressionDetector<br/>文件: fle_performance_regression_detector.py"]
        src_zephyr_feedback_loop_detectors_correlation_multi_signal_correlator_py["(原型态 / prototype) Multi-Signal Correlator — v0.4.0 R22<br/>文件: multi_signal_correlator.py"]
        src_zephyr_feedback_loop_detectors_correlation_rumor_noise_filter_py["(原型态 / prototype) Rumor Noise Filter — v0.37.0 R460<br/>文件: rumor_noise_filter.py"]
        src_zephyr_feedback_loop_detectors_correlation_trace_causal_bridge_py["(原型态 / prototype) Trace Causal Bridge — v0.6.0 R62<br/>文件: trace_causal_bridge.py"]
        src_zephyr_feedback_loop_detectors_correlation_traffic_replay_validator_py["(原型态 / prototype) Traffic Replay Validator — v0.14.0 R202<br/>文件: traffic_replay_validator.py"]
        src_zephyr_feedback_loop_detectors_drift_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_detectors_drift_concept_drift_py["(原型态 / prototype) Concept Drift Detector — v0.5.0 R42<br/>文件: concept_drift.py"]
        src_zephyr_feedback_loop_detectors_drift_config_drift_py["(原型态 / prototype) Config Drift Detector — v0.13.0 R182<br/>文件: config_drift.py"]
        src_zephyr_feedback_loop_detectors_drift_context_window_contamination_detector_py["(原型态 / prototype) Context Window Contamination Detector — v0.38....<br/>文件: context_window_contamination_detector.py"]
        src_zephyr_feedback_loop_detectors_drift_diminishing_returns_detector_py["(原型态 / prototype) R528: DiminishingReturnsDetector<br/>文件: diminishing_returns_detector.py"]
        src_zephyr_feedback_loop_detectors_drift_ensemble_drift_py["(原型态 / prototype) Ensemble Drift — v0.5.0 R43<br/>文件: ensemble_drift.py"]
        src_zephyr_feedback_loop_detectors_drift_gradual_poisoning_detector_py["(原型态 / prototype) Gradual Poisoning Detector — v0.15.0 R210<br/>文件: gradual_poisoning_detector.py"]
        src_zephyr_feedback_loop_detectors_drift_trend_cycle_separator_py["(原型态 / prototype) Trend-Cycle Separator — v0.9.0 R113<br/>文件: trend_cycle_separator.py"]
        src_zephyr_feedback_loop_detectors_guard_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_detectors_guard_alert_desensitization_curve_py["(原型态 / prototype) Alert Desensitization Curve — v0.37.0 R492<br/>文件: alert_desensitization_curve.py"]
        src_zephyr_feedback_loop_detectors_guard_guard_cascade_detector_py["(原型态 / prototype) R520: GuardCascadeDetector<br/>文件: guard_cascade_detector.py"]
        src_zephyr_feedback_loop_detectors_guard_guard_oscillation_detector_py["(原型态 / prototype) R519: GuardOscillationDetector<br/>文件: guard_oscillation_detector.py"]
        src_zephyr_feedback_loop_detectors_guard_placebo_action_detector_py["(原型态 / prototype) R508: PlaceboActionDetector<br/>文件: placebo_action_detector.py"]
        src_zephyr_feedback_loop_detectors_guard_positive_feedback_defense_py["(原型态 / prototype) Positive Feedback Defense — v0.4.0 R28<br/>文件: positive_feedback_defense.py"]
        src_zephyr_feedback_loop_detectors_guard_recursive_diagnosis_trust_evaluator_py["(原型态 / prototype) R517: RecursiveDiagnosisTrustEvaluator<br/>文件: recursive_diagnosis_trust_evaluator.py"]
        src_zephyr_feedback_loop_detectors_guard_self_audit_py["(原型态 / prototype) Self Audit — v0.13.0 R183<br/>文件: self_audit.py"]
        src_zephyr_feedback_loop_detectors_guard_self_diagnosis_data_leak_detector_py["(原型态 / prototype) R530: SelfDiagnosisDataLeakDetector<br/>文件: self_diagnosis_data_leak_detector.py"]
        src_zephyr_feedback_loop_detectors_guard_self_ha_py["(原型态 / prototype) Self HA — v0.13.0 R173<br/>文件: self_ha.py"]
        src_zephyr_feedback_loop_detectors_guard_temporal_coherence_of_self_model_py["(原型态 / prototype) R525: TemporalCoherenceOfSelfModel<br/>文件: temporal_coherence_of_self_model.py"]
        src_zephyr_feedback_loop_detectors_reliability_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_detectors_reliability_autoscale_remediation_py["(原型态 / prototype) Autoscale Remediation — v0.13.0 R174<br/>文件: autoscale_remediation.py"]
        src_zephyr_feedback_loop_detectors_reliability_blast_radius_py["(原型态 / prototype) Blast Radius Detector — v0.12.0 R167<br/>文件: blast_radius.py"]
        src_zephyr_feedback_loop_detectors_reliability_blast_radius_budget_py["(原型态 / prototype) Blast Radius Budget — v0.13.0 R178<br/>文件: blast_radius_budget.py"]
        src_zephyr_feedback_loop_detectors_reliability_capacity_forecast_py["(原型态 / prototype) Capacity Forecast — v0.13.0 R186b<br/>文件: capacity_forecast.py"]
        src_zephyr_feedback_loop_detectors_reliability_chaos_engineering_py["(原型态 / prototype) Chaos Engineering — v0.13.0 R172<br/>文件: chaos_engineering.py"]
        src_zephyr_feedback_loop_detectors_reliability_ebpf_monitor_py["(原型态 / prototype) eBPF Monitor — v0.6.0 R64<br/>文件: ebpf_monitor.py"]
        src_zephyr_feedback_loop_detectors_reliability_flag_lifecycle_py["(原型态 / prototype) Flag Lifecycle Detector — v0.13.0 R180<br/>文件: flag_lifecycle.py"]
        src_zephyr_feedback_loop_detectors_reliability_maintenance_coordinator_py["(原型态 / prototype) Maintenance Coordinator — v0.12.0 R168<br/>文件: maintenance_coordinator.py"]
        src_zephyr_feedback_loop_detectors_reliability_metric_cardinality_guard_py["(原型态 / prototype) Metric Cardinality Guard — v0.40.0 R495<br/>文件: metric_cardinality_guard.py"]
        src_zephyr_feedback_loop_detectors_reliability_openfeature_py["(原型态 / prototype) OpenFeature Integration — v0.13.0 R181<br/>文件: openfeature.py"]
        src_zephyr_feedback_loop_detectors_reliability_otel_adapter_py["(原型态 / prototype) OTel Adapter — v0.12.0 R170<br/>文件: otel_adapter.py"]
        src_zephyr_feedback_loop_detectors_reliability_regulatory_audit_py["(原型态 / prototype) Regulatory Audit Detector — v0.13.0 R184<br/>文件: regulatory_audit.py"]
        src_zephyr_feedback_loop_detectors_reliability_resolution_tracker_py["(原型态 / prototype) Resolution Tracker — v0.12.0 R165<br/>文件: resolution_tracker.py"]
        src_zephyr_feedback_loop_detectors_reliability_runbook_executor_py["(原型态 / prototype) Runbook Executor — v0.13.0 R186a<br/>文件: runbook_executor.py"]
        src_zephyr_feedback_loop_detectors_reliability_version_migrator_py["(原型态 / prototype) Version Migrator — v0.12.0 R169<br/>文件: version_migrator.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py["(原型态 / prototype) Adaptive Parameter Tuning — v0.37.0 R452<br/>文件: adaptive_param_tuning.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py["(原型态 / prototype) Cognitive Load Estimator — v0.6.0 R68<br/>文件: cognitive_load.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py["(原型态 / prototype) Cognitive Load Budget — v0.16.0 R223<br/>文件: cognitive_load_budget.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py["(原型态 / prototype) Collaborative Learning — v0.7.0 R82<br/>文件: collaborative_learning.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py["(原型态 / prototype) Confidence Decomposer — v0.7.0 R83<br/>文件: confidence_decomposer.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py["(原型态 / prototype) Gamification — v0.8.0 R101<br/>文件: gamification.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py["(原型态 / prototype) R516: MetaGuardLatencyBudget<br/>文件: meta_guard_latency_budget.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py["(原型态 / prototype) Socratic Questions — v0.7.0 R81<br/>文件: socratic_questions.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py["(原型态 / prototype) Tone Adapter — v0.9.0 R127<br/>文件: tone_adapter.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py["(原型态 / prototype) Tone Adapter v2 — v0.10.0 R141<br/>文件: tone_adapter_v2.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py["(原型态 / prototype) Auto Diagnosis — v0.3.0 R16<br/>文件: auto_diagnosis.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py["(原型态 / prototype) Causal Inference Engine — v0.3.0 R5-R7<br/>文件: causal_inference_engine.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py["(原型态 / prototype) Counterfactual Engine — v0.6.0 R60<br/>文件: counterfactual.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py["(原型态 / prototype) diagnosis_engine.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py["(原型态 / prototype) Diagnosis KPI — v0.9.0 R116<br/>文件: diagnosis_kpi.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py["(原型态 / prototype) Impact Predictor — v0.9.0 R121<br/>文件: impact_predictor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py["(原型态 / prototype) R504: IncidentKnowledgeInjector<br/>文件: incident_knowledge_injector.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py["(原型态 / prototype) Interactive Diagnosis — v0.7.0 R80<br/>文件: interactive_diagnosis.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py["(原型态 / prototype) Knowledge Bus Factor Monitor — v0.38.0 R481<br/>文件: knowledge_bus_factor_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py["(原型态 / prototype) Knowledge Market — v0.9.0 R126<br/>文件: knowledge_market.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py["(原型态 / prototype) MTTI Tracker — v0.16.0 R221<br/>文件: mtti_tracker.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py["(原型态 / prototype) Nonstationary Effectiveness — v0.37.0 R455<br/>文件: nonstationary_effectiveness.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py["(原型态 / prototype) Statistical Hygiene Auditor — v0.38.0 R476<br/>文件: statistical_hygiene_auditor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py["(原型态 / prototype) Vertical Self Assessment — v0.10.0 R137<br/>文件: vertical_self_assessment.py"]
        src_zephyr_feedback_loop_diagnosers_health_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py["(原型态 / prototype) R511: ActionCompositionHealthMonitor<br/>文件: action_composition_health_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py["(原型态 / prototype) DR Resilience Metrics — v0.17.0+ R231-R236<br/>文件: dr_resilience_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py["(原型态 / prototype) E2E Integration Health Monitor — v0.39.0 R489<br/>文件: e2e_integration_health.py"]
        src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py["(原型态 / prototype) FLE Dogfood Monitor — v0.38.0 R480<br/>文件: fle_dogfood_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py["(原型态 / prototype) FLE Self SLO Metrics — v0.17.0+ R249-R254<br/>文件: fle_self_slo_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_health_global_health_map_py["(原型态 / prototype) Global Health Map — v0.8.0 R103<br/>文件: global_health_map.py"]
        src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py["(原型态 / prototype) Memory Self Check — v0.8.0 R105<br/>文件: memory_self_check.py"]
        src_zephyr_feedback_loop_diagnosers_health_model_health_py["(原型态 / prototype) Model Health Monitor — v0.5.0 R40<br/>文件: model_health.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py["(原型态 / prototype) Self Benchmark — v0.9.0 R115<br/>文件: self_benchmark.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py["(原型态 / prototype) Self-Bottleneck Detector — v0.38.0 R479<br/>文件: self_bottleneck_detector.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py["(原型态 / prototype) Self Health Monitor — v0.4.0 R29<br/>文件: self_health_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py["(原型态 / prototype) Self LLM Observability — v0.12.0 R160<br/>文件: self_llm_observability.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py["(原型态 / prototype) Amplification Guard — v0.10.0 R134<br/>文件: amplification_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py["(原型态 / prototype) API Dependency Metrics — v0.17.0+ R237-R242<br/>文件: api_dependency_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py["(原型态 / prototype) Burn Rate Alerter — v0.14.0 R200<br/>文件: burn_rate_alerter.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py["(原型态 / prototype) Burnout Alarm — v0.8.0 R100<br/>文件: burnout_alarm.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py["(原型态 / prototype) Capacity Aware Repair — v0.9.0 R120<br/>文件: capacity_aware_repair.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py["(原型态 / prototype) R509: ColdStartConservativeMode<br/>文件: cold_start_conservative_mode.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py["(原型态 / prototype) Context Truncation Detector — v0.9.0 R122<br/>文件: context_truncation.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py["(原型态 / prototype) R506: ContextWindowPressureManager<br/>文件: context_window_pressure_manager.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py["(原型态 / prototype) R513: CrossGuardConflictDetector<br/>文件: cross_guard_conflict_detector.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py["(原型态 / prototype) R510: CrossSessionConsistencyValidator<br/>文件: cross_session_consistency_validator.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py["(原型态 / prototype) Data Volume Growth Monitor — v0.39.0 R492<br/>文件: data_volume_growth_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py["(原型态 / prototype) Feedback Delay Compensator — v0.38.0 R477<br/>文件: feedback_delay_compensator.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py["(原型态 / prototype) R518: GuardInteractionTopologyMapper<br/>文件: guard_interaction_topology_mapper.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py["(原型态 / prototype) R512: GuardSelfConsistencyAuditor<br/>文件: guard_self_consistency_auditor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py["(原型态 / prototype) Human Anomaly Flood Detector — v0.40.0 R500<br/>文件: human_anomaly_flood_detector.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py["(原型态 / prototype) Latency SLO Monitor — v0.14.0 R192<br/>文件: latency_slo.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py["(原型态 / prototype) LLM Provider Integrity — v0.15.0 R217<br/>文件: llm_provider_integrity.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py["(原型态 / prototype) LLM Quality Regression — v0.12.0 R161<br/>文件: llm_quality_regression.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py["(原型态 / prototype) Model Rotation — v0.9.0 R125<br/>文件: model_rotation.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py["(原型态 / prototype) Model Rotation v2 — v0.10.0 R140<br/>文件: model_rotation_v2.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py["(原型态 / prototype) Model Version Semantic Drift Monitor — v0.39.0...<br/>文件: model_version_semantic_drift.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py["(原型态 / prototype) Numerical Stability Guard — v0.38.0 R475<br/>文件: numerical_stability_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py["(原型态 / prototype) Operational Seasonality — v0.16.0 R228<br/>文件: operational_seasonality.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py["(原型态 / prototype) Prompt Fingerprint — v0.3.0 R14<br/>文件: prompt_fingerprint.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py["(原型态 / prototype) Prompt Sanitizer — v0.10.0 R133<br/>文件: prompt_sanitizer.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py["(原型态 / prototype) Recovery Time Statistics — v0.37.0 R454<br/>文件: recovery_time_stats.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py["(原型态 / prototype) Regime Gain Scheduling — v0.37.0 R453<br/>文件: regime_gain_scheduling.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py["(原型态 / prototype) Retirement Planner — v0.10.0 R139<br/>文件: retirement_planner.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py["(原型态 / prototype) SLO Capacity Metrics — v0.17.0+ R243-R248<br/>文件: slo_capacity_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py["(原型态 / prototype) R527: SystemEntropyMonitor<br/>文件: system_entropy_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py["(原型态 / prototype) Temporal Integrity Guard — v0.38.0 R478<br/>文件: temporal_integrity_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py["(原型态 / prototype) Timezone Semantic Reasoner — v0.37.0 R456<br/>文件: timezone_semantic_reasoner.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py["(原型态 / prototype) Toil Quantification — v0.37.0 R457<br/>文件: toil_quantification.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py["(原型态 / prototype) Value Added Baseline — v0.10.0 R138<br/>文件: value_added_baseline.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py["(原型态 / prototype) Zombie FLE Detector — v0.16.0 R222<br/>文件: zombie_fle_detector.py"]
        src_zephyr_feedback_loop_forensic_toctou_guard_py["(原型态 / prototype) TOCTOU Guard — v0.15.0 R207<br/>文件: toctou_guard.py"]
        tests_feedback_test_actors_init_py["(原型态 / prototype) test_actors_init.py"]
        tests_feedback_test_adaptive_param_tuning_py["(原型态 / prototype) test_adaptive_param_tuning.py"]
        tests_feedback_test_alert_desensitization_curve_py["(原型态 / prototype) test_alert_desensitization_curve.py"]
        tests_feedback_test_anomaly_clustering_py["(原型态 / prototype) test_anomaly_clustering.py"]
        tests_feedback_test_architectural_sod_py["(原型态 / prototype) test_architectural_sod.py"]
        tests_feedback_test_automated_rca_postmortem_generator_py["(原型态 / prototype) test_automated_rca_postmortem_generator.py"]
        tests_feedback_test_autoscale_remediation_py["(原型态 / prototype) test_autoscale_remediation.py"]
        tests_feedback_test_backpressure_bridge_root_py["(原型态 / prototype) test_backpressure_bridge_root.py"]
        tests_feedback_test_blast_radius_budget_py["(原型态 / prototype) test_blast_radius_budget.py"]
        tests_feedback_test_boot_integrity_attestation_py["(原型态 / prototype) test_boot_integrity_attestation.py"]
        tests_feedback_test_cascading_rollback_analyzer_py["(原型态 / prototype) test_cascading_rollback_analyzer.py"]
        tests_feedback_test_cognitive_load_py["(原型态 / prototype) test_cognitive_load.py"]
        tests_feedback_test_collaborative_learning_py["(原型态 / prototype) test_collaborative_learning.py"]
        tests_feedback_test_collectors_py["(原型态 / prototype) test_collectors.py"]
        tests_feedback_test_confidence_decomposer_py["(原型态 / prototype) test_confidence_decomposer.py"]
        tests_feedback_test_config_feedback_loop_py["(原型态 / prototype) test_config_feedback_loop.py"]
        tests_feedback_test_conformal_prediction_py["(原型态 / prototype) test_conformal_prediction.py"]
        tests_feedback_test_counterfactual_py["(原型态 / prototype) test_counterfactual.py"]
        tests_feedback_test_deadman_switch_py["(原型态 / prototype) test_deadman_switch.py"]
        tests_feedback_test_diagnosers_py["(原型态 / prototype) test_diagnosers.py"]
        tests_feedback_test_diagnosis_engine_py["(原型态 / prototype) test_diagnosis_engine.py"]
        tests_feedback_test_digital_twin_sandbox_py["(原型态 / prototype) test_digital_twin_sandbox.py"]
        tests_feedback_test_diminishing_returns_detector_py["(原型态 / prototype) test_diminishing_returns_detector.py"]
        tests_feedback_test_docs_init_py["(原型态 / prototype) test_docs_init.py"]
        tests_feedback_test_dr_automation_py["(原型态 / prototype) test_dr_automation.py"]
        tests_feedback_test_dr_resilience_metrics_py["(原型态 / prototype) test_dr_resilience_metrics.py"]
        tests_feedback_test_dry_run_sandbox_py["(原型态 / prototype) test_dry_run_sandbox.py"]
        tests_feedback_test_dynamic_threshold_py["(原型态 / prototype) test_dynamic_threshold.py"]
        tests_feedback_test_e2e_integration_health_py["(原型态 / prototype) test_e2e_integration_health.py"]
        tests_feedback_test_ebpf_monitor_py["(原型态 / prototype) test_ebpf_monitor.py"]
        tests_feedback_test_ensemble_detector_py["(原型态 / prototype) test_ensemble_detector.py"]
        tests_feedback_test_ensemble_drift_py["(原型态 / prototype) test_ensemble_drift.py"]
        tests_feedback_test_eval_harness_root_py["(原型态 / prototype) test_eval_harness_root.py"]
        tests_feedback_test_evolution_engine_root_py["(原型态 / prototype) test_evolution_engine_root.py"]
        tests_feedback_test_evolution_init_py["(原型态 / prototype) test_evolution_init.py"]
        tests_feedback_test_ewc_kb_review_py["(原型态 / prototype) test_ewc_kb_review.py"]
        tests_feedback_test_exceptions_feedback_loop_py["(原型态 / prototype) test_exceptions_feedback_loop.py"]
        tests_feedback_test_failure_replay_py["(原型态 / prototype) test_failure_replay.py"]
        tests_feedback_test_federated_protocol_py["(原型态 / prototype) test_federated_protocol.py"]
        tests_feedback_test_feedback_bridge_py["(原型态 / prototype) test_feedback_bridge.py"]
        tests_feedback_test_feedback_collector_root_py["(原型态 / prototype) test_feedback_collector_root.py"]
        tests_feedback_test_feedback_core_py["(原型态 / prototype) Test suite: feedback-loop core (FeedbackCollect...<br/>文件: test_feedback_core.py"]
        tests_feedback_test_feedback_delay_compensator_py["(原型态 / prototype) test_feedback_delay_compensator.py"]
        tests_feedback_test_feedback_loop_py["(原型态 / prototype) test_feedback_loop.py"]
        tests_feedback_test_feedback_policy_py["(原型态 / prototype) test_feedback_policy.py"]
        tests_feedback_test_feedback_self_audit_py["(原型态 / prototype) test_feedback_self_audit.py"]
        tests_feedback_test_flapping_detector_py["(原型态 / prototype) test_flapping_detector.py"]
        tests_feedback_test_gamification_py["(原型态 / prototype) test_gamification.py"]
        tests_feedback_test_global_action_scheduler_py["(原型态 / prototype) test_global_action_scheduler.py"]
        tests_feedback_test_golden_test_external_py["(原型态 / prototype) test_golden_test_external.py"]
        tests_feedback_test_gradual_poisoning_detector_py["(原型态 / prototype) test_gradual_poisoning_detector.py"]
        tests_feedback_test_graduated_activation_protocol_py["(原型态 / prototype) test_graduated_activation_protocol.py"]
        tests_feedback_test_heisenbug_detector_py["(原型态 / prototype) test_heisenbug_detector.py"]
        tests_feedback_test_hypernetwork_py["(原型态 / prototype) test_hypernetwork.py"]
        tests_feedback_test_impact_predictor_py["(原型态 / prototype) test_impact_predictor.py"]
        tests_feedback_test_incident_knowledge_injector_py["(原型态 / prototype) test_incident_knowledge_injector.py"]
        tests_feedback_test_infinite_loop_detector_py["(原型态 / prototype) test_infinite_loop_detector.py"]
        tests_feedback_test_interrupt_coherence_validator_py["(原型态 / prototype) test_interrupt_coherence_validator.py"]
        tests_feedback_test_known_unknown_registry_py["(原型态 / prototype) test_known_unknown_registry.py"]
        tests_feedback_test_log_anomaly_py["(原型态 / prototype) test_log_anomaly.py"]
        tests_feedback_test_maintenance_coordinator_py["(原型态 / prototype) test_maintenance_coordinator.py"]
        tests_feedback_test_market_calendar_py["(原型态 / prototype) test_market_calendar.py"]
        tests_feedback_test_market_event_integrator_py["(原型态 / prototype) test_market_event_integrator.py"]
        tests_feedback_test_meta_guard_latency_budget_py["(原型态 / prototype) test_meta_guard_latency_budget.py"]
        tests_feedback_test_metric_cardinality_guard_py["(原型态 / prototype) test_metric_cardinality_guard.py"]
        tests_feedback_test_metrics_collector_py["(原型态 / prototype) test_metrics_collector.py"]
        tests_feedback_test_no_llm_degradation_py["(原型态 / prototype) test_no_llm_degradation.py"]
        tests_feedback_test_nonstationary_effectiveness_py["(原型态 / prototype) test_nonstationary_effectiveness.py"]
        tests_feedback_test_notification_feedback_py["(原型态 / prototype) test_notification_feedback.py"]
        tests_feedback_test_notification_personalizer_py["(原型态 / prototype) test_notification_personalizer.py"]
        tests_feedback_test_numerical_stability_guard_py["(原型态 / prototype) test_numerical_stability_guard.py"]
        tests_feedback_test_online_feature_importance_py["(原型态 / prototype) test_online_feature_importance.py"]
        tests_feedback_test_operational_seasonality_py["(原型态 / prototype) test_operational_seasonality.py"]
        tests_feedback_test_oscillation_damping_py["(原型态 / prototype) test_oscillation_damping.py"]
        tests_feedback_test_otel_adapter_py["(原型态 / prototype) test_otel_adapter.py"]
        tests_feedback_test_placebo_action_detector_py["(原型态 / prototype) test_placebo_action_detector.py"]
        tests_feedback_test_positive_feedback_defense_py["(原型态 / prototype) test_positive_feedback_defense.py"]
        tests_feedback_test_protocols_py["(原型态 / prototype) test_protocols.py"]
        tests_feedback_test_recovery_time_stats_py["(原型态 / prototype) test_recovery_time_stats.py"]
        tests_feedback_test_recursive_diagnosis_trust_evaluator_py["(原型态 / prototype) test_recursive_diagnosis_trust_evaluator.py"]
        tests_feedback_test_regulatory_audit_py["(原型态 / prototype) test_regulatory_audit.py"]
        tests_feedback_test_resolution_tracker_py["(原型态 / prototype) test_resolution_tracker.py"]
        tests_feedback_test_retirement_planner_py["(原型态 / prototype) test_retirement_planner.py"]
        tests_feedback_test_rumor_noise_filter_py["(原型态 / prototype) test_rumor_noise_filter.py"]
        tests_feedback_test_runbook_executor_py["(原型态 / prototype) test_runbook_executor.py"]
        tests_feedback_test_scheduler_collect_detect_py["(原型态 / prototype) test_scheduler_collect_detect.py"]
        tests_feedback_test_scheduler_health_py["(原型态 / prototype) test_scheduler_health.py"]
        tests_feedback_test_scheduler_integration_py["(原型态 / prototype) Integration tests: FeedbackLoopScheduler start/...<br/>文件: test_scheduler_integration.py"]
        tests_feedback_test_secondary_alert_channel_py["(原型态 / prototype) test_secondary_alert_channel.py"]
        tests_feedback_test_silent_corruption_detector_py["(原型态 / prototype) test_silent_corruption_detector.py"]
        tests_feedback_test_slo_capacity_metrics_py["(原型态 / prototype) test_slo_capacity_metrics.py"]
        tests_feedback_test_slo_manager_root_py["(原型态 / prototype) test_slo_manager_root.py"]
        tests_feedback_test_state_migration_validator_py["(原型态 / prototype) test_state_migration_validator.py"]
        tests_feedback_test_stochastic_diagnosis_verifier_py["(原型态 / prototype) test_stochastic_diagnosis_verifier.py"]
        tests_feedback_test_stochastic_diagnosis_verifier_v2_py["(原型态 / prototype) test_stochastic_diagnosis_verifier_v2.py"]
        tests_feedback_test_synthetic_anomaly_generator_py["(原型态 / prototype) test_synthetic_anomaly_generator.py"]
        tests_feedback_test_system_entropy_monitor_py["(原型态 / prototype) test_system_entropy_monitor.py"]
        tests_feedback_test_teacher_transfer_py["(原型态 / prototype) test_teacher_transfer.py"]
        tests_feedback_test_timezone_semantic_reasoner_py["(原型态 / prototype) test_timezone_semantic_reasoner.py"]
        tests_feedback_test_token_finops_py["(原型态 / prototype) test_token_finops.py"]
        tests_feedback_test_training_data_gov_py["(原型态 / prototype) test_training_data_gov.py"]
        tests_feedback_test_trend_cycle_separator_py["(原型态 / prototype) test_trend_cycle_separator.py"]
        tests_feedback_test_validator_py["(原型态 / prototype) test_validator.py"]
        tests_feedback_test_vertical_self_assessment_py["(原型态 / prototype) test_vertical_self_assessment.py"]
        tests_feedback_test_worm_write_integrity_py["(原型态 / prototype) test_worm_write_integrity.py"]
    end
    src_zephyr_feedback_loop_db_writer_py -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_alert_dispatcher_py
    src_zephyr_feedback_loop_detectors_anomaly_anomaly_detector_py -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_detectors_anomaly_anomaly_detector_py -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_detectors_anomaly_anomaly_clustering_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_emergent_behavior_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_flapping_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_infinite_loop_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_heisenbug_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_intermittent_failure_pattern_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_temporal_pattern_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_silent_corruption_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_correlation_action_interaction_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_anomaly_synthetic_anomaly_generator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_anomaly_log_anomaly_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    src_zephyr_feedback_loop_detectors_correlation_action_efficacy_decay_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_action_side_effect_cumulative_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_agent_trajectory_anomaly_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_cross_signal_validator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_cross_system_correlator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_decision_provenance_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_dependency_freshness_monitor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_external_health_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_ensemble_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_fle_performance_regression_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_external_validation_checkpoint_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_multi_signal_correlator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_traffic_replay_validator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_trace_causal_bridge_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_correlation_rumor_noise_filter_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    src_zephyr_feedback_loop_detectors_drift_concept_drift_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_drift_config_drift_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_drift_context_window_contamination_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_drift_diminishing_returns_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_drift_trend_cycle_separator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_drift_gradual_poisoning_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_guard_alert_desensitization_curve_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_guard_cascade_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_drift_ensemble_drift_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    src_zephyr_feedback_loop_detectors_guard_guard_oscillation_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_placebo_action_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_positive_feedback_defense_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_recursive_diagnosis_trust_evaluator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_self_audit_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_self_diagnosis_data_leak_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_self_ha_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_guard_temporal_coherence_of_self_model_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    src_zephyr_feedback_loop_detectors_reliability_autoscale_remediation_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_blast_radius_budget_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_blast_radius_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_ebpf_monitor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_capacity_forecast_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_maintenance_coordinator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_flag_lifecycle_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_chaos_engineering_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_metric_cardinality_guard_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_otel_adapter_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_openfeature_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_resolution_tracker_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_regulatory_audit_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_version_migrator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_detectors_reliability_runbook_executor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_global_health_map_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_model_health_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py -.->|config_depends / config_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    D_ORCHESTRATOR["(原型态 / prototype) D_ORCHESTRATOR"]
    src_zephyr_feedback_loop_alert_dispatcher_py -.->|导入依赖 / import_depends| D_ORCHESTRATOR
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_feedback_loop_alert_dispatcher_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_feedback_loop_core_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_core_py -.->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    src_zephyr_feedback_loop_core_py -.->|导入依赖 / import_depends| D_INTEGRATION
    D_INFRA_RUNTIME["(原型态 / prototype) D_INFRA_RUNTIME"]
    src_zephyr_feedback_loop_db_writer_py -.->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_feedback_loop_db_writer_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py -.->|导入依赖 / import_depends| D_SHARED
    tests_feedback_test_actors_init_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_anomaly_clustering_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_alert_desensitization_curve_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_adaptive_param_tuning_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_autoscale_remediation_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_cognitive_load_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_blast_radius_budget_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_saga_compensator_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_detectors_anomaly_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_detectors_correlation_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_detectors_drift_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_detectors_guard_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_detectors_reliability_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_toctou_guard_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_actors_saga_compensator_py,src_zephyr_feedback_loop_alert_dispatcher_py,src_zephyr_feedback_loop_collectors_feedback_collector_py,src_zephyr_feedback_loop_collectors_metrics_collector_py,src_zephyr_feedback_loop_core_py,src_zephyr_feedback_loop_db_writer_py,src_zephyr_feedback_loop_detectors_anomaly_init_py,src_zephyr_feedback_loop_detectors_anomaly_anomaly_clustering_py,src_zephyr_feedback_loop_detectors_anomaly_anomaly_detector_py,src_zephyr_feedback_loop_detectors_anomaly_emergent_behavior_detector_py,src_zephyr_feedback_loop_detectors_anomaly_flapping_detector_py,src_zephyr_feedback_loop_detectors_anomaly_heisenbug_detector_py,src_zephyr_feedback_loop_detectors_anomaly_infinite_loop_detector_py,src_zephyr_feedback_loop_detectors_anomaly_intermittent_failure_pattern_py,src_zephyr_feedback_loop_detectors_anomaly_log_anomaly_py,src_zephyr_feedback_loop_detectors_anomaly_silent_corruption_detector_py,src_zephyr_feedback_loop_detectors_anomaly_synthetic_anomaly_generator_py,src_zephyr_feedback_loop_detectors_anomaly_temporal_pattern_py,src_zephyr_feedback_loop_detectors_correlation_init_py,src_zephyr_feedback_loop_detectors_correlation_action_efficacy_decay_detector_py,src_zephyr_feedback_loop_detectors_correlation_action_interaction_detector_py,src_zephyr_feedback_loop_detectors_correlation_action_side_effect_cumulative_detector_py,src_zephyr_feedback_loop_detectors_correlation_agent_trajectory_anomaly_detector_py,src_zephyr_feedback_loop_detectors_correlation_cross_signal_validator_py,src_zephyr_feedback_loop_detectors_correlation_cross_system_correlator_py,src_zephyr_feedback_loop_detectors_correlation_decision_provenance_py,src_zephyr_feedback_loop_detectors_correlation_dependency_freshness_monitor_py,src_zephyr_feedback_loop_detectors_correlation_ensemble_detector_py,src_zephyr_feedback_loop_detectors_correlation_external_health_py,src_zephyr_feedback_loop_detectors_correlation_external_validation_checkpoint_py,src_zephyr_feedback_loop_detectors_correlation_fle_performance_regression_detector_py,src_zephyr_feedback_loop_detectors_correlation_multi_signal_correlator_py,src_zephyr_feedback_loop_detectors_correlation_rumor_noise_filter_py,src_zephyr_feedback_loop_detectors_correlation_trace_causal_bridge_py,src_zephyr_feedback_loop_detectors_correlation_traffic_replay_validator_py,src_zephyr_feedback_loop_detectors_drift_init_py,src_zephyr_feedback_loop_detectors_drift_concept_drift_py,src_zephyr_feedback_loop_detectors_drift_config_drift_py,src_zephyr_feedback_loop_detectors_drift_context_window_contamination_detector_py,src_zephyr_feedback_loop_detectors_drift_diminishing_returns_detector_py,src_zephyr_feedback_loop_detectors_drift_ensemble_drift_py,src_zephyr_feedback_loop_detectors_drift_gradual_poisoning_detector_py,src_zephyr_feedback_loop_detectors_drift_trend_cycle_separator_py,src_zephyr_feedback_loop_detectors_guard_init_py,src_zephyr_feedback_loop_detectors_guard_alert_desensitization_curve_py,src_zephyr_feedback_loop_detectors_guard_guard_cascade_detector_py,src_zephyr_feedback_loop_detectors_guard_guard_oscillation_detector_py,src_zephyr_feedback_loop_detectors_guard_placebo_action_detector_py,src_zephyr_feedback_loop_detectors_guard_positive_feedback_defense_py,src_zephyr_feedback_loop_detectors_guard_recursive_diagnosis_trust_evaluator_py,src_zephyr_feedback_loop_detectors_guard_self_audit_py,src_zephyr_feedback_loop_detectors_guard_self_diagnosis_data_leak_detector_py,src_zephyr_feedback_loop_detectors_guard_self_ha_py,src_zephyr_feedback_loop_detectors_guard_temporal_coherence_of_self_model_py,src_zephyr_feedback_loop_detectors_reliability_init_py,src_zephyr_feedback_loop_detectors_reliability_autoscale_remediation_py,src_zephyr_feedback_loop_detectors_reliability_blast_radius_py,src_zephyr_feedback_loop_detectors_reliability_blast_radius_budget_py,src_zephyr_feedback_loop_detectors_reliability_capacity_forecast_py,src_zephyr_feedback_loop_detectors_reliability_chaos_engineering_py,src_zephyr_feedback_loop_detectors_reliability_ebpf_monitor_py,src_zephyr_feedback_loop_detectors_reliability_flag_lifecycle_py,src_zephyr_feedback_loop_detectors_reliability_maintenance_coordinator_py,src_zephyr_feedback_loop_detectors_reliability_metric_cardinality_guard_py,src_zephyr_feedback_loop_detectors_reliability_openfeature_py,src_zephyr_feedback_loop_detectors_reliability_otel_adapter_py,src_zephyr_feedback_loop_detectors_reliability_regulatory_audit_py,src_zephyr_feedback_loop_detectors_reliability_resolution_tracker_py,src_zephyr_feedback_loop_detectors_reliability_runbook_executor_py,src_zephyr_feedback_loop_detectors_reliability_version_migrator_py,src_zephyr_feedback_loop_diagnosers_cognitive_init_py,src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py,src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py,src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py,src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py,src_zephyr_feedback_loop_diagnosers_diagnosis_init_py,src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py,src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py,src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py,src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py,src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py,src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py,src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py,src_zephyr_feedback_loop_diagnosers_health_init_py,src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py,src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py,src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py,src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py,src_zephyr_feedback_loop_diagnosers_health_global_health_map_py,src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py,src_zephyr_feedback_loop_diagnosers_health_model_health_py,src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py,src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py,src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py,src_zephyr_feedback_loop_diagnosers_reliability_init_py,src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py,src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py,src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py,src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py,src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py,src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py,src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py,src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py,src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py,src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py,src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py,src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py,src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py,src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py,src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py,src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py,src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py,src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py,src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py,src_zephyr_feedback_loop_forensic_toctou_guard_py,tests_feedback_test_actors_init_py,tests_feedback_test_adaptive_param_tuning_py,tests_feedback_test_alert_desensitization_curve_py,tests_feedback_test_anomaly_clustering_py,tests_feedback_test_architectural_sod_py,tests_feedback_test_automated_rca_postmortem_generator_py,tests_feedback_test_autoscale_remediation_py,tests_feedback_test_backpressure_bridge_root_py,tests_feedback_test_blast_radius_budget_py,tests_feedback_test_boot_integrity_attestation_py,tests_feedback_test_cascading_rollback_analyzer_py,tests_feedback_test_cognitive_load_py,tests_feedback_test_collaborative_learning_py,tests_feedback_test_collectors_py,tests_feedback_test_confidence_decomposer_py,tests_feedback_test_config_feedback_loop_py,tests_feedback_test_conformal_prediction_py,tests_feedback_test_counterfactual_py,tests_feedback_test_deadman_switch_py,tests_feedback_test_diagnosers_py,tests_feedback_test_diagnosis_engine_py,tests_feedback_test_digital_twin_sandbox_py,tests_feedback_test_diminishing_returns_detector_py,tests_feedback_test_docs_init_py,tests_feedback_test_dr_automation_py,tests_feedback_test_dr_resilience_metrics_py,tests_feedback_test_dry_run_sandbox_py,tests_feedback_test_dynamic_threshold_py,tests_feedback_test_e2e_integration_health_py,tests_feedback_test_ebpf_monitor_py,tests_feedback_test_ensemble_detector_py,tests_feedback_test_ensemble_drift_py,tests_feedback_test_eval_harness_root_py,tests_feedback_test_evolution_engine_root_py,tests_feedback_test_evolution_init_py,tests_feedback_test_ewc_kb_review_py,tests_feedback_test_exceptions_feedback_loop_py,tests_feedback_test_failure_replay_py,tests_feedback_test_federated_protocol_py,tests_feedback_test_feedback_bridge_py,tests_feedback_test_feedback_collector_root_py,tests_feedback_test_feedback_core_py,tests_feedback_test_feedback_delay_compensator_py,tests_feedback_test_feedback_loop_py,tests_feedback_test_feedback_policy_py,tests_feedback_test_feedback_self_audit_py,tests_feedback_test_flapping_detector_py,tests_feedback_test_gamification_py,tests_feedback_test_global_action_scheduler_py,tests_feedback_test_golden_test_external_py,tests_feedback_test_gradual_poisoning_detector_py,tests_feedback_test_graduated_activation_protocol_py,tests_feedback_test_heisenbug_detector_py,tests_feedback_test_hypernetwork_py,tests_feedback_test_impact_predictor_py,tests_feedback_test_incident_knowledge_injector_py,tests_feedback_test_infinite_loop_detector_py,tests_feedback_test_interrupt_coherence_validator_py,tests_feedback_test_known_unknown_registry_py,tests_feedback_test_log_anomaly_py,tests_feedback_test_maintenance_coordinator_py,tests_feedback_test_market_calendar_py,tests_feedback_test_market_event_integrator_py,tests_feedback_test_meta_guard_latency_budget_py,tests_feedback_test_metric_cardinality_guard_py,tests_feedback_test_metrics_collector_py,tests_feedback_test_no_llm_degradation_py,tests_feedback_test_nonstationary_effectiveness_py,tests_feedback_test_notification_feedback_py,tests_feedback_test_notification_personalizer_py,tests_feedback_test_numerical_stability_guard_py,tests_feedback_test_online_feature_importance_py,tests_feedback_test_operational_seasonality_py,tests_feedback_test_oscillation_damping_py,tests_feedback_test_otel_adapter_py,tests_feedback_test_placebo_action_detector_py,tests_feedback_test_positive_feedback_defense_py,tests_feedback_test_protocols_py,tests_feedback_test_recovery_time_stats_py,tests_feedback_test_recursive_diagnosis_trust_evaluator_py,tests_feedback_test_regulatory_audit_py,tests_feedback_test_resolution_tracker_py,tests_feedback_test_retirement_planner_py,tests_feedback_test_rumor_noise_filter_py,tests_feedback_test_runbook_executor_py,tests_feedback_test_scheduler_collect_detect_py,tests_feedback_test_scheduler_health_py,tests_feedback_test_scheduler_integration_py,tests_feedback_test_secondary_alert_channel_py,tests_feedback_test_silent_corruption_detector_py,tests_feedback_test_slo_capacity_metrics_py,tests_feedback_test_slo_manager_root_py,tests_feedback_test_state_migration_validator_py,tests_feedback_test_stochastic_diagnosis_verifier_py,tests_feedback_test_stochastic_diagnosis_verifier_v2_py,tests_feedback_test_synthetic_anomaly_generator_py,tests_feedback_test_system_entropy_monitor_py,tests_feedback_test_teacher_transfer_py,tests_feedback_test_timezone_semantic_reasoner_py,tests_feedback_test_token_finops_py,tests_feedback_test_training_data_gov_py,tests_feedback_test_trend_cycle_separator_py,tests_feedback_test_validator_py,tests_feedback_test_vertical_self_assessment_py,tests_feedback_test_worm_write_integrity_py design
    class D_GOVERNANCE,D_SHARED,D_INTEGRATION external_prod
    class D_ORCHESTRATOR,D_INFRA_RUNTIME external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_AUTONOMY_CORE 自治核心: VectorBridge — CE↔VMS 检索桥接 (Connect CT-CE... | 导入依赖 / import_depends |
| 2 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_FBL_VERIFICATION 反馈验证: verification_engine.py | 导入依赖 / import_depends |
| 3 | scheduler_act.py | → | D_FBL_VERIFICATION 反馈验证: Cascading Rollback Analyzer — v0.38.0 R482 (ca... | 导入依赖 / import_depends |
| 4 | scheduler_act.py | → | D_FBL_VERIFICATION 反馈验证: Stochastic Diagnosis Verifier — v0.38.0 R483 (... | 导入依赖 / import_depends |
| 5 | scheduler_act.py | → | D_FBL_VERIFICATION 反馈验证: verification_engine.py | 导入依赖 / import_depends |
| 6 | scheduler_safety.py | → | D_FBL_VERIFICATION 反馈验证: Deployment Suppression — v0.37.0 R464 (deploym... | 导入依赖 / import_depends |
| 7 | scheduler_safety.py | → | D_FBL_VERIFICATION 反馈验证: Safety Gates L1-L27 — Unified Pipeline (MOD-FE... | 导入依赖 / import_depends |
| 8 | E2E Integration Test Pipeline — TASK-MOD-FEEDB... | → | D_FBL_VERIFICATION 反馈验证: Safety Gates L1-L27 — Unified Pipeline (MOD-FE... | 导入依赖 / import_depends |
| 9 | test_cascading_rollback_analyzer.py | → | D_FBL_VERIFICATION 反馈验证: Cascading Rollback Analyzer — v0.38.0 R482 (ca... | 测试依赖 / test_depends |
| 10 | test_digital_twin_sandbox.py | → | D_FBL_VERIFICATION 反馈验证: Digital Twin Sandbox — v0.6.0 R55 (digital_twi... | 测试依赖 / test_depends |
| 11 | test_dry_run_sandbox.py | → | D_FBL_VERIFICATION 反馈验证: Dry Run Sandbox — v0.3.0 R19 (dry_run_sandbox.py) | 测试依赖 / test_depends |
| 12 | test_federated_protocol.py | → | D_FBL_VERIFICATION 反馈验证: Federated Protocol — v0.10.0 R129 (federated_p... | 测试依赖 / test_depends |
| 13 | test_golden_test_external.py | → | D_FBL_VERIFICATION 反馈验证: Golden Test External — v0.15.0 R214 (golden_te... | 测试依赖 / test_depends |
| 14 | test_no_llm_degradation.py | → | D_FBL_VERIFICATION 反馈验证: No-LLM Degradation Mode — v0.8.0 R94 (no_llm_d... | 测试依赖 / test_depends |
| 15 | test_stochastic_diagnosis_verifier.py | → | D_FBL_VERIFICATION 反馈验证: Stochastic Diagnosis Verifier — v0.38.0 R483 (... | 测试依赖 / test_depends |
| 16 | test_stochastic_diagnosis_verifier_v2.py | → | D_FBL_VERIFICATION 反馈验证: Stochastic Diagnosis Verifier — v0.38.0 R483 (... | 测试依赖 / test_depends |
| 17 | FLE->Orc 告警分派器 — dispatch() 生产者 (alert... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-... | 导入依赖 / import_depends |
| 18 | FLE DB契约适配器 — 通过规范zephyr.governance.s... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-... | 导入依赖 / import_depends |
| 19 | FLE 持久化写入器 — 写 metrics/alerts/dispatch_... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-... | 导入依赖 / import_depends |
| 20 | MetricsCollector: append-only metrics recording... | → | D_GOVERNANCE 生命周期管理: SQLite 元数据层 Schema DDL + 版本化迁移框架（T-... | 导入依赖 / import_depends |
| 21 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 导入依赖 / import_depends |
| 22 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 23 | scheduler_act.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 导入依赖 / import_depends |
| 24 | scheduler_act.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 25 | scheduler_collect_detect.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 导入依赖 / import_depends |
| 26 | scheduler_collect_detect.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 27 | scheduler_health.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 导入依赖 / import_depends |
| 28 | scheduler_health.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 29 | scheduler_safety.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 30 | E2E Integration Test Pipeline — TASK-MOD-FEEDB... | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 导入依赖 / import_depends |
| 31 | E2E Integration Test Pipeline — TASK-MOD-FEEDB... | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 32 | test_actors_init.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | 测试依赖 / test_depends |
| 33 | test_adaptive_param_tuning.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 34 | test_alert_desensitization_curve.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 35 | test_anomaly_clustering.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 36 | test_autoscale_remediation.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 37 | test_blast_radius_budget.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 38 | test_cognitive_load.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 39 | test_collaborative_learning.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 40 | test_confidence_decomposer.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 41 | test_counterfactual.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 42 | test_diagnosers.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 43 | test_diagnosis_engine.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 44 | test_diminishing_returns_detector.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 45 | test_docs_init.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.docs — auto-generated package in... | 测试依赖 / test_depends |
| 46 | test_dr_resilience_metrics.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 47 | test_e2e_integration_health.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 48 | test_ebpf_monitor.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 49 | test_ensemble_detector.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 50 | test_ensemble_drift.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 51 | test_feedback_delay_compensator.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 52 | test_flapping_detector.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 53 | test_gamification.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 54 | test_gradual_poisoning_detector.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 55 | test_heisenbug_detector.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 56 | test_impact_predictor.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 57 | test_incident_knowledge_injector.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 58 | test_infinite_loop_detector.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 59 | test_log_anomaly.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 60 | test_maintenance_coordinator.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 61 | test_meta_guard_latency_budget.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 62 | test_metric_cardinality_guard.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 63 | test_nonstationary_effectiveness.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 64 | test_numerical_stability_guard.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 65 | test_operational_seasonality.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 66 | test_otel_adapter.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 67 | test_placebo_action_detector.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 68 | test_positive_feedback_defense.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 69 | test_recovery_time_stats.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 70 | test_recursive_diagnosis_trust_evaluator.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 71 | test_regulatory_audit.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 72 | test_resolution_tracker.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 73 | test_retirement_planner.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 74 | test_rumor_noise_filter.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 75 | test_runbook_executor.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 76 | test_scheduler_collect_detect.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 77 | test_scheduler_collect_detect.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 78 | test_silent_corruption_detector.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 79 | test_slo_capacity_metrics.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 80 | test_synthetic_anomaly_generator.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 81 | test_system_entropy_monitor.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 82 | test_timezone_semantic_reasoner.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 83 | test_trend_cycle_separator.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | 测试依赖 / test_depends |
| 84 | test_vertical_self_assessment.py | → | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 测试依赖 / test_depends |
| 85 | test_feedback_bridge.py | → | D_GOV_AUDIT 审计追踪: feedback_bridge.py | 测试依赖 / test_depends |
| 86 | test_feedback_policy.py | → | D_GOV_AUDIT 审计追踪: feedback_policy.py | 测试依赖 / test_depends |
| 87 | test_feedback_self_audit.py | → | D_GOV_AUDIT 审计追踪: audit-trail.feedback_self_audit — MOD-INF-020 ... | 测试依赖 / test_depends |
| 88 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_GOV_DRIFT 漂移检测: Drift Engine — 编排器核心 (SRC-0030 精简后) (d... | 导入依赖 / import_depends |
| 89 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_GOV_DRIFT 漂移检测: integrity.py | 导入依赖 / import_depends |
| 90 | scheduler_act.py | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Escalation Engine — MOD-INF-022 (escalation_en... | 导入依赖 / import_depends |
| 91 | scheduler_act.py | → | D_GOV_OPS_RESILIENCE 运维弹性治理: Escalation Protocol data models — MOD-INF-022 ... | 导入依赖 / import_depends |
| 92 | scheduler_act.py | → | D_INFRA_RECOVERY 回滚恢复: RollbackExecutor — 回滚执行器核心封装。 (rollb... | 导入依赖 / import_depends |
| 93 | FLE -> Pipeline 背压桥接（CTR-BP-001~003） (bac... | → | D_INFRA_RUNTIME 运行时集成: Pipeline — Backpressure Manager (backpressure_... | 导入依赖 / import_depends |
| 94 | FLE 持久化写入器 — 写 metrics/alerts/dispatch_... | → | D_INFRA_RUNTIME 运行时集成: TELE->FLE 指标桥接 — emit_metrics() 生产者 (me... | 导入依赖 / import_depends |
| 95 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_INFRA_RUNTIME 运行时集成: __init__.py | 导入依赖 / import_depends |
| 96 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_INFRA_RUNTIME 运行时集成: TELE->FLE 指标桥接 — emit_metrics() 生产者 (me... | 导入依赖 / import_depends |
| 97 | FeedbackLoop core — 反馈闭环核心类。 (core.py) | → | D_INTEGRATION 管线路由: schemas.py | 导入依赖 / import_depends |
| 98 | FeedbackCollector: collect task execution feedb... | → | D_INTEGRATION 管线路由: schemas.py | 导入依赖 / import_depends |
| 99 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_INTEGRATION 管线路由: InProcessVectorMemory — MOD-INF-011 VMS 统一入... | 导入依赖 / import_depends |
| 100 | FLE->Orc 告警分派器 — dispatch() 生产者 (alert... | → | D_ORCHESTRATOR 代理编排器: Orc 告警接收器 — handle_alert() 消费者 (alert_... | 导入依赖 / import_depends |
| 101 | evolution_engine.py | → | D_SECURITY 对抗验证: gateway.py | 导入依赖 / import_depends |
| 102 | API Version Contract — v0.14.0 R188 (api_versi... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 103 | FeedbackLoop core — 反馈闭环核心类。 (core.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 104 | FeedbackLoop core — 反馈闭环核心类。 (core.py) | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 105 | Operational Seasonality — v0.16.0 R228 (operat... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 106 | evolution_engine.py | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 .... | 导入依赖 / import_depends |
| 107 | FeedbackCollector: collect task execution feedb... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 108 | FeedbackCollector: collect task execution feedb... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 109 | fitness_functions.py | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 110 | Self-Modification Audit — v0.15.0 R218 (self_m... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 111 | MetricsCollector: append-only metrics recording... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (sqlite_factory.py) | 导入依赖 / import_depends |
| 112 | Config Hot-Reload Guard — v0.40.0 R498 (config... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 113 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (event... | 导入依赖 / import_depends |
| 114 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 115 | FLE 全链路调度器 —— collect->detect->diagnose... | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 .... | 导入依赖 / import_depends |
| 116 | scheduler_act.py | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (event... | 导入依赖 / import_depends |
| 117 | scheduler_safety.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 118 | Secret Rotation — v0.14.0 R189 (secret_rotatio... | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 ... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: test_action_selector.py | → | action_selector.py | 测试依赖 / test_depends |
| 2 | D_AUTONOMY_CORE 自治核心: test_action_selector.py | → | protocols.py | 测试依赖 / test_depends |
| 3 | D_AUTONOMY_CORE 自治核心: test_agent_lifecycle.py | → | Agent Lifecycle Manager — v0.12.0 R159c (agent... | 测试依赖 / test_depends |
| 4 | D_AUTONOMY_CORE 自治核心: test_agent_skill_guard.py | → | Agent Skill Guard — v0.14.0 R201 (agent_skill_... | 测试依赖 / test_depends |
| 5 | D_AUTONOMY_CORE 自治核心: test_auto_evolution_root.py | → | auto_evolution.py | 测试依赖 / test_depends |
| 6 | D_AUTONOMY_CORE 自治核心: test_auto_evolution_root.py | → | evolution_engine.py | 测试依赖 / test_depends |
| 7 | D_AUTONOMY_CORE 自治核心: test_auto_reward.py | → | Auto Reward — v0.7.0 R76 (auto_reward.py) | 测试依赖 / test_depends |
| 8 | D_AUTONOMY_CORE 自治核心: AutoRuntimeCore → FeedbackLoopScheduler 自动启... | → | FLE 全链路调度器 —— collect->detect->diagnose... | 测试依赖 / test_depends |
| 9 | D_AUTONOMY_CORE 自治核心: test_incident_priority_triage_automator.py | → | Incident Priority Triage Automator — v0.37.0 R... | 测试依赖 / test_depends |
| 10 | D_AUTONOMY_CORE 自治核心: test_owner_absence_escalation.py | → | Owner Absence Escalation — v0.37.0 R462 (owner... | 测试依赖 / test_depends |
| 11 | D_AUTONOMY_CORE 自治核心: test_fl_action_selector.py | → | action_selector.py | 测试依赖 / test_depends |
| 12 | D_AUTONOMY_CORE 自治核心: test_fl_action_selector.py | → | protocols.py | 测试依赖 / test_depends |
| 13 | D_AUTONOMY_CORE 自治核心: test_fl_agent_lifecycle.py | → | Agent Lifecycle Manager — v0.12.0 R159c (agent... | 测试依赖 / test_depends |
| 14 | D_AUTONOMY_CORE 自治核心: test_fl_anomaly_detector.py | → | FeedbackCollector: collect task execution feedb... | 测试依赖 / test_depends |
| 15 | D_AUTONOMY_CORE 自治核心: test_fl_anomaly_detector.py | → | MetricsCollector: append-only metrics recording... | 测试依赖 / test_depends |
| 16 | D_AUTONOMY_CORE 自治核心: test_fl_anomaly_detector.py | → | protocols.py | 测试依赖 / test_depends |
| 17 | D_AUTONOMY_CORE 自治核心: test_fl_api_version_contract.py | → | API Version Contract — v0.14.0 R188 (api_versi... | 测试依赖 / test_depends |
| 18 | D_AUTONOMY_CORE 自治核心: test_fl_auto_evolution.py | → | auto_evolution.py | 测试依赖 / test_depends |
| 19 | D_AUTONOMY_CORE 自治核心: test_fl_auto_evolution.py | → | evolution_engine.py | 测试依赖 / test_depends |
| 20 | D_AUTONOMY_CORE 自治核心: test_fl_backpressure_bridge.py | → | FLE -> Pipeline 背压桥接（CTR-BP-001~003） (bac... | 测试依赖 / test_depends |
| 21 | D_AUTONOMY_CORE 自治核心: test_fl_backpressure_bridge.py | → | evolution_engine.py | 测试依赖 / test_depends |
| 22 | D_AUTONOMY_CORE 自治核心: test_fl_calendar_adapter.py | → | Calendar Adapter — v0.8.0 R102b (calendar_adap... | 测试依赖 / test_depends |
| 23 | D_AUTONOMY_CORE 自治核心: test_fl_config.py | → | config.py | 测试依赖 / test_depends |
| 24 | D_AUTONOMY_CORE 自治核心: test_fl_config_timeline.py | → | Config Timeline — v0.8.0 R99 (config_timeline.py) | 测试依赖 / test_depends |
| 25 | D_AUTONOMY_CORE 自治核心: test_fl_data_quality_validator.py | → | Data Quality Validator — v0.9.0 R110 (data_qua... | 测试依赖 / test_depends |
| 26 | D_AUTONOMY_CORE 自治核心: test_fl_db_bridge.py | → | FLE DB契约适配器 — 通过规范zephyr.governance.s... | 测试依赖 / test_depends |
| 27 | D_AUTONOMY_CORE 自治核心: test_fl_decision_engine.py | → | Feedback Loop Decision Engine (decision_engine.py) | 测试依赖 / test_depends |
| 28 | D_AUTONOMY_CORE 自治核心: test_fl_decision_engine.py | → | protocols.py | 测试依赖 / test_depends |
| 29 | D_AUTONOMY_CORE 自治核心: test_fl_error_budget.py | → | Error Budget 状态机——monthly budget + burn_ra... | 测试依赖 / test_depends |
| 30 | D_AUTONOMY_CORE 自治核心: test_fl_eval_harness.py | → | eval_harness.py | 测试依赖 / test_depends |
| 31 | D_AUTONOMY_CORE 自治核心: test_fl_evolution_engine.py | → | evolution_engine.py | 测试依赖 / test_depends |
| 32 | D_AUTONOMY_CORE 自治核心: test_fl_exceptions.py | → | exceptions.py | 测试依赖 / test_depends |
| 33 | D_AUTONOMY_CORE 自治核心: test_fl_financial_stratification.py | → | Financial Stratification — v0.5.0 R50 (financi... | 测试依赖 / test_depends |
| 34 | D_AUTONOMY_CORE 自治核心: test_fl_fitness_functions.py | → | fitness_functions.py | 测试依赖 / test_depends |
| 35 | D_AUTONOMY_CORE 自治核心: test_fl_generator.py | → | generator.py | 测试依赖 / test_depends |
| 36 | D_AUTONOMY_CORE 自治核心: test_fl_global_action_scheduler.py | → | Global Action Scheduler — v0.16.0 R226 (global... | 测试依赖 / test_depends |
| 37 | D_AUTONOMY_CORE 自治核心: test_fl_incident_priority_triage_automator.py | → | Incident Priority Triage Automator — v0.37.0 R... | 测试依赖 / test_depends |
| 38 | D_AUTONOMY_CORE 自治核心: test_fl_intent_driven_ops.py | → | Intent-Driven Ops — v0.12.0 R159 (intent_drive... | 测试依赖 / test_depends |
| 39 | D_AUTONOMY_CORE 自治核心: test_fl_kb_provenance.py | → | KB Provenance — v0.10.0 R136 (kb_provenance.py) | 测试依赖 / test_depends |
| 40 | D_AUTONOMY_CORE 自治核心: test_fl_multi_agent_orchestrator.py | → | Multi-Agent Orchestrator — v0.12.0 R159b (mult... | 测试依赖 / test_depends |
| 41 | D_AUTONOMY_CORE 自治核心: test_fl_notification_personalizer.py | → | Notification Personalizer — v0.6.0 R67 (notifi... | 测试依赖 / test_depends |
| 42 | D_AUTONOMY_CORE 自治核心: test_fl_owner_absence_escalation.py | → | Owner Absence Escalation — v0.37.0 R462 (owner... | 测试依赖 / test_depends |
| 43 | D_AUTONOMY_CORE 自治核心: test_fl_protocols.py | → | protocols.py | 测试依赖 / test_depends |
| 44 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler.py | → | FLE 全链路调度器 —— collect->detect->diagnose... | 测试依赖 / test_depends |
| 45 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_act.py | → | R522: SelfModificationRateLimiter (self_modific... | 测试依赖 / test_depends |
| 46 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_act.py | → | Graceful Degradation Planner — v0.40.0 R496 (g... | 测试依赖 / test_depends |
| 47 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_act.py | → | Self API Throttle Defense — v0.39.0 R491 (self... | 测试依赖 / test_depends |
| 48 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_act.py | → | scheduler_act.py | 测试依赖 / test_depends |
| 49 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_collect_detect.py | → | FeedbackCollector: collect task execution feedb... | 测试依赖 / test_depends |
| 50 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_collect_detect.py | → | MetricsCollector: append-only metrics recording... | 测试依赖 / test_depends |
| 51 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_collect_detect.py | → | scheduler_collect_detect.py | 测试依赖 / test_depends |
| 52 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_health.py | → | scheduler_health.py | 测试依赖 / test_depends |
| 53 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_safety.py | → | scheduler_safety.py | 测试依赖 / test_depends |
| 54 | D_AUTONOMY_CORE 自治核心: test_fl_slo_manager.py | → | slo_manager.py | 测试依赖 / test_depends |
| 55 | D_AUTONOMY_CORE 自治核心: test_fl_template.py | → | template.py | 测试依赖 / test_depends |
| 56 | D_AUTONOMY_CORE 自治核心: test_fl_validator.py | → | template.py | 测试依赖 / test_depends |
| 57 | D_AUTONOMY_CORE 自治核心: test_fl_validator.py | → | validator.py | 测试依赖 / test_depends |
| 58 | D_AUTONOMY_CORE 自治核心: test_intent_driven_ops.py | → | Intent-Driven Ops — v0.12.0 R159 (intent_drive... | 测试依赖 / test_depends |
| 59 | D_AUTONOMY_CORE 自治核心: test_prompt_factory_governance.py | → | Prompt Factory Governance — v0.16.0 R224 (prom... | 测试依赖 / test_depends |
| 60 | D_AUTONOMY_CORE 自治核心: test_prompt_optimization_regression_detector.py | → | R514: PromptOptimizationRegressionDetector (pro... | 测试依赖 / test_depends |
| 61 | D_AUTONOMY_CORE 自治核心: test_prompt_self_optimization_loop.py | → | R502: PromptSelfOptimizationLoop (prompt_self_o... | 测试依赖 / test_depends |
| 62 | D_AUTONOMY_CORE 自治核心: test_session_learner.py | → | session_learner.py — 在线学习 (DD114, TASK-020... | 测试依赖 / test_depends |
| 63 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 (... | → | Error Budget 状态机——monthly budget + burn_ra... | 测试依赖 / test_depends |
| 64 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 (... | → | FLE 全链路调度器 —— collect->detect->diagnose... | 测试依赖 / test_depends |
| 65 | D_DATA: Tests for zephyr.trading.feedback_loop.db_bridg... | → | FLE DB契约适配器 — 通过规范zephyr.governance.s... | 测试依赖 / test_depends |
| 66 | D_FRONTEND 前端: fitness_functions · Fitness Functions 仪表盘组... | → | fitness_functions.py | 导入依赖 / import_depends |
| 67 | D_FRONTEND 前端: test_fle_anomaly_detector.py | → | FeedbackCollector: collect task execution feedb... | 测试依赖 / test_depends |
| 68 | D_FRONTEND 前端: test_fle_anomaly_detector.py | → | MetricsCollector: append-only metrics recording... | 测试依赖 / test_depends |
| 69 | D_FRONTEND 前端: test_fle_anomaly_detector.py | → | protocols.py | 测试依赖 / test_depends |
| 70 | D_FRONTEND 前端: test_fle_config.py | → | config.py | 测试依赖 / test_depends |
| 71 | D_FRONTEND 前端: test_fle_exceptions.py | → | exceptions.py | 测试依赖 / test_depends |
| 72 | D_FRONTEND 前端: test_fle_feedback_collector.py | → | FeedbackCollector: collect task execution feedb... | 测试依赖 / test_depends |
| 73 | D_FRONTEND 前端: test_fle_generator.py | → | generator.py | 测试依赖 / test_depends |
| 74 | D_FRONTEND 前端: test_fle_metrics_collector.py | → | MetricsCollector: append-only metrics recording... | 测试依赖 / test_depends |
| 75 | D_FRONTEND 前端: test_fle_protocols.py | → | protocols.py | 测试依赖 / test_depends |
| 76 | D_FRONTEND 前端: test_fle_template.py | → | template.py | 测试依赖 / test_depends |
| 77 | D_FRONTEND 前端: test_fle_upgrade_safety_validator.py | → | R529: FLEUpgradeSafetyValidator (fle_upgrade_sa... | 测试依赖 / test_depends |
| 78 | D_FRONTEND 前端: test_fle_validator.py | → | template.py | 测试依赖 / test_depends |
| 79 | D_FRONTEND 前端: test_fle_validator.py | → | validator.py | 测试依赖 / test_depends |
| 80 | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | → | action_selector.py | 导入依赖 / import_depends |
| 81 | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | → | Agent Lifecycle Manager — v0.12.0 R159c (agent... | 导入依赖 / import_depends |
| 82 | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | → | API Version Contract — v0.14.0 R188 (api_versi... | 导入依赖 / import_depends |
| 83 | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | → | Global Action Scheduler — v0.16.0 R226 (global... | 导入依赖 / import_depends |
| 84 | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | → | Incident Priority Triage Automator — v0.37.0 R... | 导入依赖 / import_depends |
| 85 | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | → | Intent-Driven Ops — v0.12.0 R159 (intent_drive... | 导入依赖 / import_depends |
| 86 | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | → | Multi-Agent Orchestrator — v0.12.0 R159b (mult... | 导入依赖 / import_depends |
| 87 | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | → | Notification Personalizer — v0.6.0 R67 (notifi... | 导入依赖 / import_depends |
| 88 | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | → | Owner Absence Escalation — v0.37.0 R462 (owner... | 导入依赖 / import_depends |
| 89 | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | → | Saga Compensator — v0.3.0 R19b (saga_compensat... | 导入依赖 / import_depends |
| 90 | D_GOVERNANCE 生命周期管理: feedback-loop.actors — auto-generated package ... | → | Secondary Alert Channel — v0.37.0 R461 (second... | 导入依赖 / import_depends |
| 91 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Calendar Adapter — v0.8.0 R102b (calendar_adap... | 导入依赖 / import_depends |
| 92 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Config Timeline — v0.8.0 R99 (config_timeline.py) | 导入依赖 / import_depends |
| 93 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Data Quality Validator — v0.9.0 R110 (data_qua... | 导入依赖 / import_depends |
| 94 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | feedback_collector.py | 导入依赖 / import_depends |
| 95 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Financial Stratification — v0.5.0 R50 (financi... | 导入依赖 / import_depends |
| 96 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | KB Provenance — v0.10.0 R136 (kb_provenance.py) | 导入依赖 / import_depends |
| 97 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Knowledge Capture — v0.4.0 R30 (knowledge_capt... | 导入依赖 / import_depends |
| 98 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Knowledge Freshness — v0.5.0 R47 (knowledge_fr... | 导入依赖 / import_depends |
| 99 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Knowledge Injection — v0.8.0 R102 (knowledge_i... | 导入依赖 / import_depends |
| 100 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Knowledge Packaging — v0.9.0 R123 (knowledge_p... | 导入依赖 / import_depends |
| 101 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Known-Unknown Registry — v0.16.0 R229 (known_u... | 导入依赖 / import_depends |
| 102 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | LLM Cost Accounting — v0.4.0 R35 (llm_cost_acc... | 导入依赖 / import_depends |
| 103 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Market Calendar — v0.5.0 R48 (market_calendar.py) | 导入依赖 / import_depends |
| 104 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Market Event Integrator — v0.14.0 R197 (market... | 导入依赖 / import_depends |
| 105 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | metrics_collector.py | 导入依赖 / import_depends |
| 106 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Notification Feedback — v0.9.0 R118 (notificat... | 导入依赖 / import_depends |
| 107 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Schema Evolution — v0.9.0 R111 (schema_evoluti... | 导入依赖 / import_depends |
| 108 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Schema Migration — v0.14.0 R190 (schema_migrat... | 导入依赖 / import_depends |
| 109 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Temporal Event Store — v0.3.0 R9 (temporal_eve... | 导入依赖 / import_depends |
| 110 | D_GOVERNANCE 生命周期管理: feedback-loop.collectors — auto-generated pack... | → | Token FinOps — v0.12.0 R162 (token_finops.py) | 导入依赖 / import_depends |
| 111 | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | → | __init__.py | 导入依赖 / import_depends |
| 112 | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | → | __init__.py | 导入依赖 / import_depends |
| 113 | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | → | __init__.py | 导入依赖 / import_depends |
| 114 | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | → | __init__.py | 导入依赖 / import_depends |
| 115 | D_GOVERNANCE 生命周期管理: feedback-loop.detectors — GOV-DOC-018: 60个叶.... | → | __init__.py | 导入依赖 / import_depends |
| 116 | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | → | __init__.py | 导入依赖 / import_depends |
| 117 | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | → | __init__.py | 导入依赖 / import_depends |
| 118 | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | → | __init__.py | 导入依赖 / import_depends |
| 119 | D_GOVERNANCE 生命周期管理: feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | → | __init__.py | 导入依赖 / import_depends |
| 120 | D_GOVERNANCE 生命周期管理: feedback-loop.docs — auto-generated package in... | → | cold_start_manual.py | 导入依赖 / import_depends |
| 121 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Auto Reward — v0.7.0 R76 (auto_reward.py) | 导入依赖 / import_depends |
| 122 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Conformal Prediction — v0.7.0 R74 (conformal_p... | 导入依赖 / import_depends |
| 123 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Cross-Gen Validation — v0.7.0 R78 (cross_gen_v... | 导入依赖 / import_depends |
| 124 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Dynamic Threshold — v0.7.0 R71 (dynamic_thresh... | 导入依赖 / import_depends |
| 125 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | EWC KB Review — v0.6.0 R51 (ewc_kb_review.py) | 导入依赖 / import_depends |
| 126 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Failure Replay — v0.7.0 R77 (failure_replay.py) | 导入依赖 / import_depends |
| 127 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Graduated Activation Protocol — v0.38.0 R485 (... | 导入依赖 / import_depends |
| 128 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | HyperNetwork — v0.7.0 R72 (hypernetwork.py) | 导入依赖 / import_depends |
| 129 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Knowledge Distillation — v0.6.0 R52 (knowledge... | 导入依赖 / import_depends |
| 130 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Online Feature Importance — v0.7.0 R73 (online... | 导入依赖 / import_depends |
| 131 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Prompt Factory Governance — v0.16.0 R224 (prom... | 导入依赖 / import_depends |
| 132 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | R514: PromptOptimizationRegressionDetector (pro... | 导入依赖 / import_depends |
| 133 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | R502: PromptSelfOptimizationLoop (prompt_self_o... | 导入依赖 / import_depends |
| 134 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | R522: SelfModificationRateLimiter (self_modific... | 导入依赖 / import_depends |
| 135 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Self Reflection — v0.7.0 R75 (self_reflection.py) | 导入依赖 / import_depends |
| 136 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Self Upgrade Canary — v0.14.0 R194 (self_upgra... | 导入依赖 / import_depends |
| 137 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | R505: SemanticIntentPreservationGuard (semantic... | 导入依赖 / import_depends |
| 138 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Teacher Transfer — v0.6.0 R53 (teacher_transfe... | 导入依赖 / import_depends |
| 139 | D_GOVERNANCE 生命周期管理: feedback-loop.evolution — auto-generated packa... | → | Training Data Governance — v0.14.0 R191 (train... | 导入依赖 / import_depends |
| 140 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | Architectural SoD — v0.15.0 R205 (architectura... | 导入依赖 / import_depends |
| 141 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | Automated RCA Postmortem Generator — v0.38.0 R... | 导入依赖 / import_depends |
| 142 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | Boot Integrity Attestation — v0.38.0 R487 (boo... | 导入依赖 / import_depends |
| 143 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | Cryptographic Bootstrap — v0.15.0 R204 (crypto... | 导入依赖 / import_depends |
| 144 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | Deterministic Replay — v0.15.0 R206 (determini... | 导入依赖 / import_depends |
| 145 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | External Verifier — v0.15.0 R203 (external_ver... | 导入依赖 / import_depends |
| 146 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | R529: FLEUpgradeSafetyValidator (fle_upgrade_sa... | 导入依赖 / import_depends |
| 147 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | R523: GuardComplexityBudget (guard_complexity_b... | 导入依赖 / import_depends |
| 148 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | R521: GuardConfigurationDriftMonitor (guard_con... | 导入依赖 / import_depends |
| 149 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | R531: InterruptCoherenceValidator (interrupt_co... | 导入依赖 / import_depends |
| 150 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | R515: KnowledgeInjectionPreFlightVerifier (know... | 导入依赖 / import_depends |
| 151 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | Point-in-Time Reconstructor — v0.37.0 R465 (po... | 导入依赖 / import_depends |
| 152 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | Self-Modification Audit — v0.15.0 R218 (self_m... | 导入依赖 / import_depends |
| 153 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | Serialization Format Tracker — v0.39.0 R488 (s... | 导入依赖 / import_depends |
| 154 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | State Migration Validator — v0.40.0 R497 (stat... | 导入依赖 / import_depends |
| 155 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | Sub-Agent Collusion Detector — v0.15.0 R213 (s... | 导入依赖 / import_depends |
| 156 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | TOCTOU Guard — v0.15.0 R207 (toctou_guard.py) | 导入依赖 / import_depends |
| 157 | D_GOVERNANCE 生命周期管理: feedback-loop.forensic — auto-generated packag... | → | WORM Write Integrity — v0.15.0 R216 (worm_writ... | 导入依赖 / import_depends |
| 158 | D_GOVERNANCE 生命周期管理: feedback-loop.resilience — auto-generated pack... | → | Config Hot-Reload Guard — v0.40.0 R498 (config... | 导入依赖 / import_depends |
| 159 | D_GOVERNANCE 生命周期管理: feedback-loop.resilience — auto-generated pack... | → | Deadman Switch — v0.15.0 R212 (deadman_switch.py) | 导入依赖 / import_depends |
| 160 | D_GOVERNANCE 生命周期管理: feedback-loop.resilience — auto-generated pack... | → | DR Automation — v0.14.0 R187 (dr_automation.py) | 导入依赖 / import_depends |
| 161 | D_GOVERNANCE 生命周期管理: feedback-loop.resilience — auto-generated pack... | → | Graceful Degradation Planner — v0.40.0 R496 (g... | 导入依赖 / import_depends |
| 162 | D_GOVERNANCE 生命周期管理: feedback-loop.resilience — auto-generated pack... | → | Multi-Instance Coordinator — v0.14.0 R199 (mul... | 导入依赖 / import_depends |
| 163 | D_GOVERNANCE 生命周期管理: feedback-loop.resilience — auto-generated pack... | → | Oscillation Damping — v0.37.0 R450 (oscillatio... | 导入依赖 / import_depends |
| 164 | D_GOVERNANCE 生命周期管理: feedback-loop.resilience — auto-generated pack... | → | Resource Starvation Aware — v0.15.0 R209 (reso... | 导入依赖 / import_depends |
| 165 | D_GOVERNANCE 生命周期管理: feedback-loop.resilience — auto-generated pack... | → | Self API Throttle Defense — v0.39.0 R491 (self... | 导入依赖 / import_depends |
| 166 | D_GOVERNANCE 生命周期管理: feedback-loop.resilience — auto-generated pack... | → | Split-Brain Quorum — v0.37.0 R451 (split_brain... | 导入依赖 / import_depends |
| 167 | D_GOVERNANCE 生命周期管理: feedback-loop.security — auto-generated packag... | → | Agent Skill Guard — v0.14.0 R201 (agent_skill_... | 导入依赖 / import_depends |
| 168 | D_GOVERNANCE 生命周期管理: feedback-loop.security — auto-generated packag... | → | Dependency CVE Correlator — v0.14.0 R196 (dep_... | 导入依赖 / import_depends |
| 169 | D_GOVERNANCE 生命周期管理: feedback-loop.security — auto-generated packag... | → | Metric-Prompt Scanner — v0.15.0 R215 (metric_p... | 导入依赖 / import_depends |
| 170 | D_GOVERNANCE 生命周期管理: feedback-loop.security — auto-generated packag... | → | Remote Attestation — v0.15.0 R211 (remote_atte... | 导入依赖 / import_depends |
| 171 | D_GOVERNANCE 生命周期管理: feedback-loop.security — auto-generated packag... | → | Secret Rotation — v0.14.0 R189 (secret_rotatio... | 导入依赖 / import_depends |
| 172 | D_GOVERNANCE 生命周期管理: feedback-loop.security — auto-generated packag... | → | Wireheading Prevention — v0.37.0 R486 (wirehea... | 导入依赖 / import_depends |
| 173 | D_GOVERNANCE 生命周期管理: feedback-loop.tests.e2e — auto-generated packa... | → | E2E Integration Test Pipeline — TASK-MOD-FEEDB... | 导入依赖 / import_depends |
| 174 | D_GOVERNANCE 生命周期管理: test_spec_auditor.py | → | protocols.py | 测试依赖 / test_depends |
| 175 | D_GOV_AUDIT 审计追踪: feedback_bridge.py | → | Feedback Loop Engine — MOD-FEEDBACK_LOOP. (__i... | 导入依赖 / import_depends |
| 176 | D_GOV_AUDIT 审计追踪: test_audit_spec_auditor.py | → | protocols.py | 测试依赖 / test_depends |
| 177 | D_GOV_AUDIT 审计追踪: test_crypto_bootstrap.py | → | Cryptographic Bootstrap — v0.15.0 R204 (crypto... | 测试依赖 / test_depends |
| 178 | D_GOV_AUDIT 审计追踪: test_deterministic_replay.py | → | Deterministic Replay — v0.15.0 R206 (determini... | 测试依赖 / test_depends |
| 179 | D_GOV_AUDIT 审计追踪: test_point_in_time_reconstructor.py | → | Point-in-Time Reconstructor — v0.37.0 R465 (po... | 测试依赖 / test_depends |
| 180 | D_GOV_AUDIT 审计追踪: test_serialization_format_tracker.py | → | Serialization Format Tracker — v0.39.0 R488 (s... | 测试依赖 / test_depends |
| 181 | D_GOV_AUDIT 审计追踪: test_sub_agent_collusion.py | → | Sub-Agent Collusion Detector — v0.15.0 R213 (s... | 测试依赖 / test_depends |
| 182 | D_GOV_AUDIT 审计追踪: test_schema_evolution_root.py | → | Schema Evolution — v0.9.0 R111 (schema_evoluti... | 测试依赖 / test_depends |
| 183 | D_GOV_AUDIT 审计追踪: test_self_api_throttle_defense.py | → | Self API Throttle Defense — v0.39.0 R491 (self... | 测试依赖 / test_depends |
| 184 | D_GOV_AUDIT 审计追踪: test_self_diagnosis.py | → | self_diagnosis.py — 自我诊断 (DD120, TASK-020)... | 测试依赖 / test_depends |
| 185 | D_GOV_AUDIT 审计追踪: test_self_modification_audit.py | → | Self-Modification Audit — v0.15.0 R218 (self_m... | 测试依赖 / test_depends |
| 186 | D_GOV_AUDIT 审计追踪: test_self_modification_rate_limiter.py | → | R522: SelfModificationRateLimiter (self_modific... | 测试依赖 / test_depends |
| 187 | D_GOV_AUDIT 审计追踪: test_self_reflection.py | → | Self Reflection — v0.7.0 R75 (self_reflection.py) | 测试依赖 / test_depends |
| 188 | D_GOV_AUDIT 审计追踪: test_self_upgrade_canary.py | → | Self Upgrade Canary — v0.14.0 R194 (self_upgra... | 测试依赖 / test_depends |
| 189 | D_GOV_AUDIT 审计追踪: test_semantic_intent_preservation_guard.py | → | R505: SemanticIntentPreservationGuard (semantic... | 测试依赖 / test_depends |
| 190 | D_GOV_ENFORCEMENT 规则执行: test_guard_complexity_budget.py | → | R523: GuardComplexityBudget (guard_complexity_b... | 测试依赖 / test_depends |
| 191 | D_GOV_ENFORCEMENT 规则执行: test_guard_configuration_drift_monitor.py | → | R521: GuardConfigurationDriftMonitor (guard_con... | 测试依赖 / test_depends |
| 192 | D_GOV_SCRIPTS 脚本治理: test_gen_inherited.py | → | _gen_inherited.py | 测试依赖 / test_depends |
| 193 | D_INFRASTRUCTURE: test_config_hot_reload_guard.py | → | Config Hot-Reload Guard — v0.40.0 R498 (config... | 测试依赖 / test_depends |
| 194 | D_INFRASTRUCTURE: test_api_version_contract.py | → | API Version Contract — v0.14.0 R188 (api_versi... | 测试依赖 / test_depends |
| 195 | D_INFRA_A2A A2A通信: test_bridges_spec_auditor.py | → | protocols.py | 测试依赖 / test_depends |
| 196 | D_INFRA_RUNTIME 运行时集成: ZephyrAlpha 核心包索引 + 模块懒加载器 (M-04) (_... | → | Secret Rotation — v0.14.0 R189 (secret_rotatio... | 导入依赖 / import_depends |
| 197 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | Feedback Loop Engine — MOD-FEEDBACK_LOOP. (__i... | 导入依赖 / import_depends |
| 198 | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | → | FLE 全链路调度器 —— collect->detect->diagnose... | 导入依赖 / import_depends |
| 199 | D_INFRA_RUNTIME 运行时集成: lifecycle_manager.py | → | Feedback Loop Engine — MOD-FEEDBACK_LOOP. (__i... | 导入依赖 / import_depends |
| 200 | D_INFRA_RUNTIME 运行时集成: test_graceful_degradation_planner.py | → | Graceful Degradation Planner — v0.40.0 R496 (g... | 测试依赖 / test_depends |
| 201 | D_INFRA_RUNTIME 运行时集成: test_split_brain_quorum.py | → | Split-Brain Quorum — v0.37.0 R451 (split_brain... | 测试依赖 / test_depends |
| 202 | D_INFRA_RUNTIME 运行时集成: test_resource_starvation_aware.py | → | Resource Starvation Aware — v0.15.0 R209 (reso... | 测试依赖 / test_depends |
| 203 | D_INFRA_RUNTIME 运行时集成: test_temporal_event_store.py | → | Temporal Event Store — v0.3.0 R9 (temporal_eve... | 测试依赖 / test_depends |
| 204 | D_INTEGRATION 管线路由: test_external_verifier.py | → | External Verifier — v0.15.0 R203 (external_ver... | 测试依赖 / test_depends |
| 205 | D_INTELLIGENCE 上下文管理: test_error_budget.py | → | Error Budget 状态机——monthly budget + burn_ra... | 测试依赖 / test_depends |
| 206 | D_INTELLIGENCE 上下文管理: test_decision_engine.py | → | Feedback Loop Decision Engine (decision_engine.py) | 测试依赖 / test_depends |
| 207 | D_INTELLIGENCE 上下文管理: test_decision_engine.py | → | protocols.py | 测试依赖 / test_depends |
| 208 | D_INTELLIGENCE 上下文管理: test_integration_test_pipeline.py | → | E2E Integration Test Pipeline — TASK-MOD-FEEDB... | 测试依赖 / test_depends |
| 209 | D_KNOWLEDGE 知识管理: test_knowledge_capture.py | → | Knowledge Capture — v0.4.0 R30 (knowledge_capt... | 测试依赖 / test_depends |
| 210 | D_KNOWLEDGE 知识管理: test_knowledge_distillation.py | → | Knowledge Distillation — v0.6.0 R52 (knowledge... | 测试依赖 / test_depends |
| 211 | D_KNOWLEDGE 知识管理: test_knowledge_injection.py | → | Knowledge Injection — v0.8.0 R102 (knowledge_i... | 测试依赖 / test_depends |
| 212 | D_KNOWLEDGE 知识管理: test_knowledge_injection_pre_flight_verifier.py | → | R515: KnowledgeInjectionPreFlightVerifier (know... | 测试依赖 / test_depends |
| 213 | D_KNOWLEDGE 知识管理: test_knowledge_packaging.py | → | Knowledge Packaging — v0.9.0 R123 (knowledge_p... | 测试依赖 / test_depends |
| 214 | D_ORCHESTRATOR 代理编排器: TriggerRouter — RI-03 触发路由器（M3 跨模块触.... | → | Feedback Loop Decision Engine (decision_engine.py) | 导入依赖 / import_depends |
| 215 | D_SECURITY 对抗验证: feedback_bridge.py | → | Feedback Loop Engine — MOD-FEEDBACK_LOOP. (__i... | 导入依赖 / import_depends |
| 216 | D_SECURITY 对抗验证: test_scheduler_safety.py | → | scheduler_safety.py | 测试依赖 / test_depends |
| 217 | D_SECURITY_LLM LLM防御: test_dep_cve_correlator.py | → | Dependency CVE Correlator — v0.14.0 R196 (dep_... | 测试依赖 / test_depends |
| 218 | D_SECURITY_LLM LLM防御: test_llm_cost_accounting.py | → | LLM Cost Accounting — v0.4.0 R35 (llm_cost_acc... | 测试依赖 / test_depends |
| 219 | D_SECURITY_LLM LLM防御: test_metric_prompt_scanner.py | → | Metric-Prompt Scanner — v0.15.0 R215 (metric_p... | 测试依赖 / test_depends |
| 220 | D_SECURITY_LLM LLM防御: test_remote_attestation.py | → | Remote Attestation — v0.15.0 R211 (remote_atte... | 测试依赖 / test_depends |
| 221 | D_SECURITY_LLM LLM防御: test_secret_rotation.py | → | Secret Rotation — v0.14.0 R189 (secret_rotatio... | 测试依赖 / test_depends |
| 222 | D_SECURITY_LLM LLM防御: test_security.py | → | Agent Skill Guard — v0.14.0 R201 (agent_skill_... | 测试依赖 / test_depends |
| 223 | D_SECURITY_LLM LLM防御: test_security.py | → | Dependency CVE Correlator — v0.14.0 R196 (dep_... | 测试依赖 / test_depends |
| 224 | D_SECURITY_LLM LLM防御: test_security.py | → | Metric-Prompt Scanner — v0.15.0 R215 (metric_p... | 测试依赖 / test_depends |
| 225 | D_SECURITY_LLM LLM防御: test_security.py | → | Remote Attestation — v0.15.0 R211 (remote_atte... | 测试依赖 / test_depends |
| 226 | D_SECURITY_LLM LLM防御: test_security.py | → | Secret Rotation — v0.14.0 R189 (secret_rotatio... | 测试依赖 / test_depends |
| 227 | D_SECURITY_LLM LLM防御: test_security.py | → | Wireheading Prevention — v0.37.0 R486 (wirehea... | 测试依赖 / test_depends |
| 228 | D_SECURITY_LLM LLM防御: test_wireheading_prevention.py | → | Wireheading Prevention — v0.37.0 R486 (wirehea... | 测试依赖 / test_depends |
| 229 | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 ... | → | Secret Rotation — v0.14.0 R189 (secret_rotatio... | 导入依赖 / import_depends |
| 230 | D_SHARED 共享服务: test_cross_gen_validation.py | → | Cross-Gen Validation — v0.7.0 R78 (cross_gen_v... | 测试依赖 / test_depends |
| 231 | D_SHARED 共享服务: test_multi_agent_orchestrator.py | → | Multi-Agent Orchestrator — v0.12.0 R159b (mult... | 测试依赖 / test_depends |
| 232 | D_SHARED 共享服务: test_multi_instance_coord.py | → | Multi-Instance Coordinator — v0.14.0 R199 (mul... | 测试依赖 / test_depends |
| 233 | D_TRADING 交易运营: test_lifecycle_manager.py | → | Feedback Loop Engine — MOD-FEEDBACK_LOOP. (__i... | 测试依赖 / test_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 22 个外部域直接连接（出边 119 条 + 入边 233 条 = 352 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_FBL_VERIFICATION["D_FBL_VERIFICATION<br/>反馈验证"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_FRONTEND["D_FRONTEND<br/>前端"]
    D_SECURITY_LLM["D_SECURITY_LLM<br/>LLM防御"]
    D_KNOWLEDGE["D_KNOWLEDGE<br/>知识管理"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_INFRASTRUCTURE["D_INFRASTRUCTURE"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_INFRA_A2A["D_INFRA_A2A<br/>A2A通信"]
    D_DATA["D_DATA"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_FEEDBACK_LOOP -->|68条 导入依赖 / import_depends, 测试依赖 / test_depends| D_GOVERNANCE
    D_FEEDBACK_LOOP -->|17条 导入依赖 / import_depends| D_SHARED
    D_FEEDBACK_LOOP -->|16条 导入依赖 / import_depends, 测试依赖 / test_depends| D_FBL_VERIFICATION
    D_FEEDBACK_LOOP -->|4条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_FEEDBACK_LOOP -->|3条 导入依赖 / import_depends| D_INTEGRATION
    D_FEEDBACK_LOOP -->|3条 测试依赖 / test_depends| D_GOV_AUDIT
    D_FEEDBACK_LOOP -->|2条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_FEEDBACK_LOOP -->|2条 导入依赖 / import_depends| D_GOV_DRIFT
    D_FEEDBACK_LOOP -->|1条 导入依赖 / import_depends| D_INFRA_RECOVERY
    D_FEEDBACK_LOOP -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_FEEDBACK_LOOP -->|1条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_FEEDBACK_LOOP -->|1条 导入依赖 / import_depends| D_SECURITY
    D_GOVERNANCE -->|95条 导入依赖 / import_depends, 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_AUTONOMY_CORE -->|64条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_GOV_AUDIT -->|15条 导入依赖 / import_depends, 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_FRONTEND -->|14条 导入依赖 / import_depends, 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_SECURITY_LLM -->|12条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_INFRA_RUNTIME -->|8条 导入依赖 / import_depends, 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_KNOWLEDGE -->|5条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_SHARED -->|4条 导入依赖 / import_depends, 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_INTELLIGENCE -->|4条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_GOV_ENFORCEMENT -->|2条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_SECURITY -->|2条 导入依赖 / import_depends, 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_INFRASTRUCTURE -->|2条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_TRADING -->|1条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_INFRA_A2A -->|1条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_INTEGRATION -->|1条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_ORCHESTRATOR -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_DATA -->|1条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_GOV_SCRIPTS -->|1条 测试依赖 / test_depends| D_FEEDBACK_LOOP
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
