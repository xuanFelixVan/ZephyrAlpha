---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.feedback_loop（227 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.feedback_loop（227 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：wired=142，wired_by_header=85；初判汇总：mount=227

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/feedback_loop/actors/alert_router.py` | alert_router.py — Severity-based alert channel router. | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/actors/api_version_contract.py` | API Version Contract — v0.14.0 R188 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/actors/global_action_scheduler.py` | Global Action Scheduler — v0.16.0 R226 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/actors/incident_priority_triage_automator.py` | Incident Priority Triage Automator — v0.37.0 R463 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/actors/intent_driven_ops.py` | Intent-Driven Ops — v0.12.0 R159 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/actors/multi_agent_orchestrator.py` | Multi-Agent Orchestrator — v0.12.0 R159b | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/actors/notification_personalizer.py` | Notification Personalizer — v0.6.0 R67 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/actors/owner_absence_escalation.py` | Owner Absence Escalation — v0.37.0 R462 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/actors/saga_compensator.py` | Saga Compensator — v0.3.0 R19b | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/actors/secondary_alert_channel.py` | Secondary Alert Channel — v0.37.0 R461 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/__init__.py` | feedback-loop.collectors — auto-generated package init. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/calendar_adapter.py` | Calendar Adapter — v0.8.0 R102b | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/config_timeline.py` | Config Timeline — v0.8.0 R99 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/data_quality_validator.py` | Data Quality Validator — v0.9.0 R110 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/feedback_collector.py` | Feedback Collector — FLE 动作结果与负责人应答的滑动窗口采集与比率统计。 | 2026-09-16（18天） | in=5/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/financial_stratification.py` | Financial Stratification — v0.5.0 R50 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/kb_provenance.py` | KB Provenance — v0.10.0 R136 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/knowledge_capture.py` | Knowledge Capture — v0.4.0 R30 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/knowledge_freshness.py` | Knowledge Freshness — v0.5.0 R47 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/knowledge_injection.py` | Knowledge Injection — v0.8.0 R102 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/knowledge_packaging.py` | Knowledge Packaging — v0.9.0 R123 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/known_unknown_registry.py` | Known-Unknown Registry — v0.16.0 R229 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/llm_cost_accounting.py` | LLM Cost Accounting — v0.4.0 R35 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/market_calendar.py` | Market Calendar — v0.5.0 R48 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/market_event_integrator.py` | Market Event Integrator — v0.14.0 R197 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/metrics_collector.py` | （无文档头，按文件名语义：metrics_collector） | 2026-09-16（18天） | in=5/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/notification_feedback.py` | Notification Feedback — v0.9.0 R118 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/schema_evolution.py` | Schema Evolution — v0.9.0 R111 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/schema_migration.py` | Schema Migration — v0.14.0 R190 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/temporal_event_store.py` | Temporal Event Store — v0.3.0 R9 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/collectors/token_finops.py` | Token FinOps — v0.12.0 R162 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/config.py` | （无文档头，按文件名语义：config） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/db_bridge.py` | FLE DB契约适配器 — 通过规范zephyr.governance.sqlite_schema连接写入fle_metrics | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/anomaly/__init__.py` | [GOV-DOC-018] 子包anomaly: 异常检测族（DW-244分类，原_anomaly.py聚合迁移而来） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/anomaly/anomaly_clustering.py` | Anomaly Clustering — v0.9.0 R119 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/anomaly/emergent_behavior_detector.py` | Emergent Behavior Detector — v0.38.0 R473 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/anomaly/flapping_detector.py` | Flapping Detector — v0.40.0 R494 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/anomaly/heisenbug_detector.py` | Heisenbug Detector — v0.38.0 R470 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/anomaly/infinite_loop_detector.py` | Infinite Loop Detector — v0.15.0 R219 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/anomaly/intermittent_failure_pattern.py` | Intermittent Failure Pattern Detector — v0.40.0 R501 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/anomaly/log_anomaly.py` | Log Anomaly Detector — v0.6.0 R61 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/anomaly/silent_corruption_detector.py` | Silent Corruption Detector — v0.40.0 R499 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/anomaly/synthetic_anomaly_generator.py` | Synthetic Anomaly Generator — v0.9.0 R112 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/anomaly/temporal_pattern.py` | Temporal Pattern Detector — v0.12.0 R164 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/__init__.py` | [GOV-DOC-018] 子包correlation: 跨信号/系统关联与因果族（DW-244分类，原_correlation.py聚合迁移而来） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/action_efficacy_decay_detector.py` | R507: ActionEfficacyDecayDetector | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/action_interaction_detector.py` | Action Interaction Detector — v0.38.0 R472 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/action_side_effect_cumulative_detector.py` | R526: ActionSideEffectCumulativeDetector | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/agent_trajectory_anomaly_detector.py` | R503: AgentTrajectoryAnomalyDetector | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/cross_signal_validator.py` | Cross-Signal Validator — v0.6.0 R63 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/cross_system_correlator.py` | Cross-System Correlator — v0.13.0 R185 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/decision_provenance.py` | Decision Provenance — v0.12.0 R166 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/ensemble_detector.py` | Ensemble Detector — v0.4.0 R21 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/external_validation_checkpoint.py` | R524: ExternalValidationCheckpoint | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/fle_performance_regression_detector.py` | R532: FLEPerformanceRegressionDetector | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/multi_signal_correlator.py` | Multi-Signal Correlator — v0.4.0 R22 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/rumor_noise_filter.py` | Rumor Noise Filter — v0.37.0 R460 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/trace_causal_bridge.py` | Trace Causal Bridge — v0.6.0 R62 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/correlation/traffic_replay_validator.py` | Traffic Replay Validator — v0.14.0 R202 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/drift/concept_drift.py` | Concept Drift Detector — v0.5.0 R42 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/drift/config_drift.py` | Config Drift Detector — v0.13.0 R182 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/drift/context_window_contamination_detector.py` | Context Window Contamination Detector — v0.38.0 R471 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/drift/diminishing_returns_detector.py` | R528: DiminishingReturnsDetector | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/drift/ensemble_drift.py` | Ensemble Drift — v0.5.0 R43 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/drift/gradual_poisoning_detector.py` | Gradual Poisoning Detector — v0.15.0 R210 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/drift/trend_cycle_separator.py` | Trend-Cycle Separator — v0.9.0 R113 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/guard/__init__.py` | [GOV-DOC-018] 子包guard: 守卫/自审计/反馈防御族（DW-244分类，原_guard.py聚合迁移而来） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/guard/alert_desensitization_curve.py` | Alert Desensitization Curve — v0.37.0 R492 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/guard/guard_cascade_detector.py` | R520: GuardCascadeDetector | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/guard/guard_oscillation_detector.py` | R519: GuardOscillationDetector | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/guard/placebo_action_detector.py` | R508: PlaceboActionDetector | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/guard/positive_feedback_defense.py` | Positive Feedback Defense — v0.4.0 R28 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/guard/recursive_diagnosis_trust_evaluator.py` | R517: RecursiveDiagnosisTrustEvaluator | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/guard/self_audit.py` | Self Audit — v0.13.0 R183 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/guard/self_diagnosis_data_leak_detector.py` | R530: SelfDiagnosisDataLeakDetector | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/guard/self_ha.py` | Self HA — v0.13.0 R173 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/guard/temporal_coherence_of_self_model.py` | R525: TemporalCoherenceOfSelfModel | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/__init__.py` | [GOV-DOC-018] 子包reliability: 可靠性/容量/混沌/运维族（DW-244分类，原_reliability.py聚合迁移而来） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/autoscale_remediation.py` | Autoscale Remediation — v0.13.0 R174 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/blast_radius.py` | Blast Radius Detector — v0.12.0 R167 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/capacity_forecast.py` | Capacity Forecast — v0.13.0 R186b | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/chaos_engineering.py` | Chaos Engineering — v0.13.0 R172 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/maintenance_coordinator.py` | Maintenance Coordinator — v0.12.0 R168 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/metric_cardinality_guard.py` | Metric Cardinality Guard — v0.40.0 R495 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/openfeature.py` | OpenFeature Integration — v0.13.0 R181 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/otel_adapter.py` | OTel Adapter — v0.12.0 R170 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/regulatory_audit.py` | Regulatory Audit Detector — v0.13.0 R184 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/resolution_tracker.py` | Resolution Tracker — v0.12.0 R165 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/runbook_executor.py` | Runbook Executor — v0.13.0 R186a | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/detectors/reliability/version_migrator.py` | Version Migrator — v0.12.0 R169 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/cognitive/__init__.py` | [GOV-DOC-018] 子包cognitive: 认知/调优族（DW-242分类，原_cognitive.py聚合迁移而来） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/cognitive/adaptive_param_tuning.py` | Adaptive Parameter Tuning — v0.37.0 R452 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/cognitive/cognitive_load.py` | Cognitive Load Estimator — v0.6.0 R68 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/cognitive/collaborative_learning.py` | Collaborative Learning — v0.7.0 R82 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/cognitive/confidence_decomposer.py` | Confidence Decomposer — v0.7.0 R83 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/cognitive/gamification.py` | Gamification — v0.8.0 R101 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/cognitive/socratic_questions.py` | Socratic Questions — v0.7.0 R81 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/cognitive/tone_adapter.py` | Tone Adapter — v0.9.0 R127 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/cognitive/tone_adapter_v2.py` | Tone Adapter v2 — v0.10.0 R141 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/__init__.py` | [GOV-DOC-018] 子包diagnosis: 诊断引擎族（DW-242分类，原_diagnosis.py聚合迁移而来） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/auto_diagnosis.py` | Auto Diagnosis — v0.3.0 R16 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/causal_inference_engine.py` | Causal Inference Engine — v0.3.0 R5-R7 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/counterfactual.py` | Counterfactual Engine — v0.6.0 R60 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/diagnosis_engine.py` | （无文档头，按文件名语义：diagnosis_engine） | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/diagnosis_kpi.py` | Diagnosis KPI — v0.9.0 R116 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/impact_predictor.py` | Impact Predictor — v0.9.0 R121 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/incident_knowledge_injector.py` | R504: IncidentKnowledgeInjector | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/interactive_diagnosis.py` | Interactive Diagnosis — v0.7.0 R80 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/knowledge_market.py` | Knowledge Market — v0.9.0 R126 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/mtti_tracker.py` | MTTI Tracker — v0.16.0 R221 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/nonstationary_effectiveness.py` | Nonstationary Effectiveness — v0.37.0 R455 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/statistical_hygiene_auditor.py` | Statistical Hygiene Auditor — v0.38.0 R476 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/diagnosis/vertical_self_assessment.py` | Vertical Self Assessment — v0.10.0 R137 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/__init__.py` | [GOV-DOC-018] 子包reliability: 可靠性/守卫族（DW-242分类，原_reliability.py聚合迁移而来） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/amplification_guard.py` | Amplification Guard — v0.10.0 R134 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/api_dependency_metrics.py` | API Dependency Metrics — v0.17.0+ R237-R242 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/burn_rate_alerter.py` | Burn Rate Alerter — v0.14.0 R200 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/burnout_alarm.py` | Burnout Alarm — v0.8.0 R100 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/cold_start_conservative_mode.py` | R509: ColdStartConservativeMode | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/context_truncation.py` | Context Truncation Detector — v0.9.0 R122 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/context_window_pressure_manager.py` | R506: ContextWindowPressureManager | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/cross_guard_conflict_detector.py` | R513: CrossGuardConflictDetector | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/cross_session_consistency_validator.py` | R510: CrossSessionConsistencyValidator | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/feedback_delay_compensator.py` | Feedback Delay Compensator — v0.38.0 R477 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/guard_interaction_topology_mapper.py` | R518: GuardInteractionTopologyMapper | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/guard_self_consistency_auditor.py` | R512: GuardSelfConsistencyAuditor | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/human_anomaly_flood_detector.py` | Human Anomaly Flood Detector — v0.40.0 R500 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/latency_slo.py` | Latency SLO Monitor — v0.14.0 R192 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/llm_provider_integrity.py` | LLM Provider Integrity — v0.15.0 R217 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/llm_quality_regression.py` | LLM Quality Regression — v0.12.0 R161 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/model_rotation.py` | Model Rotation — v0.9.0 R125 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/model_rotation_v2.py` | Model Rotation v2 — v0.10.0 R140 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/model_version_semantic_drift.py` | Model Version Semantic Drift Monitor — v0.39.0 R493 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/numerical_stability_guard.py` | Numerical Stability Guard — v0.38.0 R475 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/operational_seasonality.py` | Operational Seasonality — v0.16.0 R228 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/prompt_fingerprint.py` | Prompt Fingerprint — v0.3.0 R14 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/prompt_sanitizer.py` | Prompt Sanitizer — v0.10.0 R133 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/recovery_time_stats.py` | Recovery Time Statistics — v0.37.0 R454 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/regime_gain_scheduling.py` | Regime Gain Scheduling — v0.37.0 R453 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/retirement_planner.py` | Retirement Planner — v0.10.0 R139 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/slo_capacity_metrics.py` | SLO Capacity Metrics — v0.17.0+ R243-R248 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/temporal_integrity_guard.py` | Temporal Integrity Guard — v0.38.0 R478 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/timezone_semantic_reasoner.py` | Timezone Semantic Reasoner — v0.37.0 R456 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/toil_quantification.py` | Toil Quantification — v0.37.0 R457 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/diagnosers/reliability/value_added_baseline.py` | Value Added Baseline — v0.10.0 R138 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/docs/__init__.py` | feedback-loop.docs — auto-generated package init. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/docs/cold_start_manual.py` | （无文档头，按文件名语义：cold_start_manual） | 2026-09-19（15天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/eval_harness.py` | （无文档头，按文件名语义：eval_harness） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/__init__.py` | feedback-loop.evolution — auto-generated package init. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/auto_reward.py` | Auto Reward — v0.7.0 R76 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/conformal_prediction.py` | Conformal Prediction — v0.7.0 R74 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/cross_gen_validation.py` | Cross-Gen Validation — v0.7.0 R78 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/dynamic_threshold.py` | Dynamic Threshold — v0.7.0 R71 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/ewc_kb_review.py` | EWC KB Review — v0.6.0 R51 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/failure_replay.py` | Failure Replay — v0.7.0 R77 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/graduated_activation_protocol.py` | Graduated Activation Protocol — v0.38.0 R485 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/hypernetwork.py` | HyperNetwork — v0.7.0 R72 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/knowledge_distillation.py` | Knowledge Distillation — v0.6.0 R52 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/online_feature_importance.py` | Online Feature Importance — v0.7.0 R73 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/prompt_factory_governance.py` | Prompt Factory Governance — v0.16.0 R224 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/prompt_optimization_regression_detector.py` | R514: PromptOptimizationRegressionDetector | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/prompt_self_optimization_loop.py` | R502: PromptSelfOptimizationLoop | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/self_modification_rate_limiter.py` | R522: SelfModificationRateLimiter | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/self_reflection.py` | Self Reflection — v0.7.0 R75 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/self_upgrade_canary.py` | Self Upgrade Canary — v0.14.0 R194 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/semantic_intent_preservation_guard.py` | R505: SemanticIntentPreservationGuard | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/teacher_transfer.py` | Teacher Transfer — v0.6.0 R53 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/evolution/training_data_gov.py` | Training Data Governance — v0.14.0 R191 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/exceptions.py` | （无文档头，按文件名语义：exceptions） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/feedback_collector.py` | FeedbackCollector: collect task execution feedback | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/fitness_functions.py` | ----- measure_module_coupling ----- | 2026-09-19（15天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/architectural_sod.py` | Architectural SoD — v0.15.0 R205 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/automated_rca_postmortem_generator.py` | Automated RCA Postmortem Generator — v0.38.0 R486 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/boot_integrity_attestation.py` | Boot Integrity Attestation — v0.38.0 R487 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/deterministic_replay.py` | Deterministic Replay — v0.15.0 R206 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/external_verifier.py` | External Verifier — v0.15.0 R203 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/fle_upgrade_safety_validator.py` | R529: FLEUpgradeSafetyValidator | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/interrupt_coherence_validator.py` | R531: InterruptCoherenceValidator | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/knowledge_injection_pre_flight_verifier.py` | R515: KnowledgeInjectionPreFlightVerifier | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/point_in_time_reconstructor.py` | Point-in-Time Reconstructor — v0.37.0 R465 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/self_modification_audit.py` | Self-Modification Audit — v0.15.0 R218 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/serialization_format_tracker.py` | Serialization Format Tracker — v0.39.0 R488 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/state_migration_validator.py` | State Migration Validator — v0.40.0 R497 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/sub_agent_collusion.py` | Sub-Agent Collusion Detector — v0.15.0 R213 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/toctou_guard.py` | TOCTOU Guard — v0.15.0 R207 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/forensic/worm_write_integrity.py` | WORM Write Integrity — v0.15.0 R216 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/generator.py` | SRC-0068a: 从 _gen_inherited.py 拆分 - 代码生成执行器 | 2026-09-19（15天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/metrics_collector.py` | MetricsCollector: append-only metrics recording. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/module_matcher.py` | ModuleMatcher — 模块匹配器（MOD-FBL-002）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/resilience/config_hot_reload_guard.py` | Config Hot-Reload Guard — v0.40.0 R498 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/resilience/dr_automation.py` | DR Automation — v0.14.0 R187 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/resilience/graceful_degradation_planner.py` | Graceful Degradation Planner — v0.40.0 R496 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/resilience/multi_instance_coord.py` | Multi-Instance Coordinator — v0.14.0 R199 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/resilience/oscillation_damping.py` | Oscillation Damping — v0.37.0 R450 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/resilience/resource_starvation_aware.py` | Resource Starvation Aware — v0.15.0 R209 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/resilience/self_api_throttle_defense.py` | Self API Throttle Defense — v0.39.0 R491 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/resilience/split_brain_quorum.py` | Split-Brain Quorum — v0.37.0 R451 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/security/agent_skill_guard.py` | Agent Skill Guard — v0.14.0 R201 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/security/dep_cve_correlator.py` | Dependency CVE Correlator — v0.14.0 R196 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/security/metric_prompt_scanner.py` | Metric-Prompt Scanner — v0.15.0 R215 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/security/remote_attestation.py` | Remote Attestation — v0.15.0 R211 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/security/wireheading_prevention.py` | Wireheading Prevention — v0.37.0 R486 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/self_diagnosis.py` | self_diagnosis.py — 自我诊断 (DD120, TASK-020) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/session_learner.py` | session_learner.py — 在线学习 (DD114, TASK-020) | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/template.py` | SRC-0068a: 从 _gen_inherited.py 拆分 — 骨骼模板数据 | 2026-09-19（15天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/validator.py` | SRC-0068a: 从 _gen_inherited.py 拆分 - 骨骼文件验证器 | 2026-09-19（15天） | in=0/out=0·wired_by_header | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/ab_test.py` | A/B Test Verifier — v0.9.0 R117 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/action_explainability.py` | Action Explainability — v0.3.0 R15 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/ai_comment_veracity.py` | AI Comment Veracity — v0.37.0 R459 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/attack_simulator.py` | Attack Simulator — v0.6.0 R57 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/auto_rollback.py` | Auto Rollback — v0.8.0 R93 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/build_reproducibility_verifier.py` | Build Reproducibility Verifier — v0.38.0 R484 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/cascading_rollback_analyzer.py` | Cascading Rollback Analyzer — v0.38.0 R482 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/cross_blueprint_contract_drift.py` | Cross-Blueprint Contract Drift Monitor — v0.39.0 R490 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/cross_module_integration.py` | Cross-Module Integration Verifier — v0.5.0 R39 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/cross_session_knowledge_integrity.py` | Cross-Session Knowledge Integrity — v0.16.0 R225 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/digital_twin_sandbox.py` | Digital Twin Sandbox — v0.6.0 R55 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/dry_run_sandbox.py` | Dry Run Sandbox — v0.3.0 R19 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/federated_protocol.py` | Federated Protocol — v0.10.0 R129 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/golden_test_external.py` | Golden Test External — v0.15.0 R214 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/no_llm_degradation.py` | No-LLM Degradation Mode — v0.8.0 R94 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/pre_flight_simulator.py` | Pre-Flight Simulator — v0.12.0 R169b | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/rollback_integrity.py` | Rollback Integrity — v0.3.0 R18b | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/sim2real_calibration.py` | Sim2Real Calibration — v0.6.0 R56 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/stochastic_diagnosis_verifier.py` | Stochastic Diagnosis Verifier — v0.38.0 R483 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/toctou_revalidation.py` | TOCTOU Revalidation — v0.37.0 R458 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
| `src/zephyr/feedback_loop/verifiers/verification_engine.py` | （无文档头，按文件名语义：verification_engine） | 2026-09-16（18天） | in=3/out=0·wired | **mount**→GOMAP（反馈回路域）/图13 备选（活线在身未挂线） |
