---
doc_type: architecture_view
title: D_FBL_DIAGNOSERS feedback_diagnosers架构文档
version: "1.0"
status: active
date: 2026-07-14
owner: auto-generator
ttl: permanent
---

# 12_d_fbl_diagnosers / feedback_diagnosers / feedback_diagnosers / Feedback Diagnosers

> **功能简介 / Overview**: 反馈诊断器，负责异常根因诊断、模型健康监控、可靠性诊断和上下文窗口压力管理

> **文档作用 / Purpose**: 展示 feedback_diagnosers（D_FBL_DIAGNOSERS）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-14 17:48:37
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 12 | Number | 12 |
| 域ID | D_FBL_DIAGNOSERS | Domain ID | D_FBL_DIAGNOSERS |
| 域名称 | feedback_diagnosers | Domain Name | Feedback Diagnosers |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 76 | Module Count | 76 |
| 域内依赖 | 4 | Internal Dependencies | 4 |
| 跨域入边 | 113 | Cross-domain Incoming | 113 |
| 跨域出边 | 1 | Cross-domain Outgoing | 1 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 5 | Prototype Modules | 5 |
| 生产态模块 | 71 | Production Modules | 71 |
| 容量 | 71/150 (正常) | Capacity | 71/150 (正常) |
| 描述 | 反馈循环诊断(feedback_loop/diagnosers)——根因诊断、健康评估、认知诊断 | Description | 反馈循环诊断(feedback_loop/diagnosers)——根因诊断、健康评估、认知诊断 |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 76 个模块 / 76 modules）。

### L1 基础层 / Foundation Layer (76 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/feedback_loop/diagnosers/__init__.py | feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 2 | src/zephyr/feedback_loop/diagnosers/cognitive/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 3 | src/zephyr/feedback_loop/diagnosers/cognitive/adaptive_pa... | Adaptive Parameter Tuning — v0.37.0 R452 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 4 | src/zephyr/feedback_loop/diagnosers/cognitive/cognitive_l... | Cognitive Load Estimator — v0.6.0 R68 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 5 | src/zephyr/feedback_loop/diagnosers/cognitive/cognitive_l... | Cognitive Load Budget — v0.16.0 R223 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 6 | src/zephyr/feedback_loop/diagnosers/cognitive/collaborati... | Collaborative Learning — v0.7.0 R82 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 7 | src/zephyr/feedback_loop/diagnosers/cognitive/confidence_... | Confidence Decomposer — v0.7.0 R83 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 8 | src/zephyr/feedback_loop/diagnosers/cognitive/gamificatio... | Gamification — v0.8.0 R101 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 9 | src/zephyr/feedback_loop/diagnosers/cognitive/meta_guard_... | R516: MetaGuardLatencyBudget | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 10 | src/zephyr/feedback_loop/diagnosers/cognitive/socratic_qu... | Socratic Questions — v0.7.0 R81 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 11 | src/zephyr/feedback_loop/diagnosers/cognitive/tone_adapte... | Tone Adapter — v0.9.0 R127 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 12 | src/zephyr/feedback_loop/diagnosers/cognitive/tone_adapte... | Tone Adapter v2 — v0.10.0 R141 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 13 | src/zephyr/feedback_loop/diagnosers/diagnosis/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 14 | src/zephyr/feedback_loop/diagnosers/diagnosis/auto_diagno... | Auto Diagnosis — v0.3.0 R16 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 15 | src/zephyr/feedback_loop/diagnosers/diagnosis/causal_infe... | Causal Inference Engine — v0.3.0 R5-R7 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 16 | src/zephyr/feedback_loop/diagnosers/diagnosis/counterfact... | Counterfactual Engine — v0.6.0 R60 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 17 | src/zephyr/feedback_loop/diagnosers/diagnosis/diagnosis_e... | diagnosis_engine.py | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 18 | src/zephyr/feedback_loop/diagnosers/diagnosis/diagnosis_k... | Diagnosis KPI — v0.9.0 R116 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 19 | src/zephyr/feedback_loop/diagnosers/diagnosis/impact_pred... | Impact Predictor — v0.9.0 R121 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 20 | src/zephyr/feedback_loop/diagnosers/diagnosis/incident_kn... | R504: IncidentKnowledgeInjector | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 21 | src/zephyr/feedback_loop/diagnosers/diagnosis/interactive... | Interactive Diagnosis — v0.7.0 R80 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 22 | src/zephyr/feedback_loop/diagnosers/diagnosis/knowledge_b... | Knowledge Bus Factor Monitor — v0.38.0 R481 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 23 | src/zephyr/feedback_loop/diagnosers/diagnosis/knowledge_m... | Knowledge Market — v0.9.0 R126 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 24 | src/zephyr/feedback_loop/diagnosers/diagnosis/mtti_tracke... | MTTI Tracker — v0.16.0 R221 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 25 | src/zephyr/feedback_loop/diagnosers/diagnosis/nonstationa... | Nonstationary Effectiveness — v0.37.0 R455 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 26 | src/zephyr/feedback_loop/diagnosers/diagnosis/statistical... | Statistical Hygiene Auditor — v0.38.0 R476 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 27 | src/zephyr/feedback_loop/diagnosers/diagnosis/vertical_se... | Vertical Self Assessment — v0.10.0 R137 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 28 | src/zephyr/feedback_loop/diagnosers/health/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 29 | src/zephyr/feedback_loop/diagnosers/health/action_composi... | R511: ActionCompositionHealthMonitor | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 30 | src/zephyr/feedback_loop/diagnosers/health/dr_resilience_... | DR Resilience Metrics — v0.17.0+ R231-R236 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 31 | src/zephyr/feedback_loop/diagnosers/health/e2e_integratio... | E2E Integration Health Monitor — v0.39.0 R489 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 32 | src/zephyr/feedback_loop/diagnosers/health/fle_dogfood_mo... | FLE Dogfood Monitor — v0.38.0 R480 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 33 | src/zephyr/feedback_loop/diagnosers/health/fle_self_slo_m... | FLE Self SLO Metrics — v0.17.0+ R249-R254 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 34 | src/zephyr/feedback_loop/diagnosers/health/global_health_... | Global Health Map — v0.8.0 R103 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 35 | src/zephyr/feedback_loop/diagnosers/health/memory_self_ch... | Memory Self Check — v0.8.0 R105 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 36 | src/zephyr/feedback_loop/diagnosers/health/model_health.py | Model Health Monitor — v0.5.0 R40 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 37 | src/zephyr/feedback_loop/diagnosers/health/self_benchmark.py | Self Benchmark — v0.9.0 R115 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 38 | src/zephyr/feedback_loop/diagnosers/health/self_bottlenec... | Self-Bottleneck Detector — v0.38.0 R479 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 39 | src/zephyr/feedback_loop/diagnosers/health/self_health_mo... | Self Health Monitor — v0.4.0 R29 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 40 | src/zephyr/feedback_loop/diagnosers/health/self_llm_obser... | Self LLM Observability — v0.12.0 R160 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 41 | src/zephyr/feedback_loop/diagnosers/reliability/__init__.py | __init__.py | 原型态 / prototype | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 42 | src/zephyr/feedback_loop/diagnosers/reliability/amplifica... | Amplification Guard — v0.10.0 R134 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 43 | src/zephyr/feedback_loop/diagnosers/reliability/api_depen... | API Dependency Metrics — v0.17.0+ R237-R242 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 44 | src/zephyr/feedback_loop/diagnosers/reliability/burn_rate... | Burn Rate Alerter — v0.14.0 R200 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 45 | src/zephyr/feedback_loop/diagnosers/reliability/burnout_a... | Burnout Alarm — v0.8.0 R100 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 46 | src/zephyr/feedback_loop/diagnosers/reliability/capacity_... | Capacity Aware Repair — v0.9.0 R120 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 47 | src/zephyr/feedback_loop/diagnosers/reliability/cold_star... | R509: ColdStartConservativeMode | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 48 | src/zephyr/feedback_loop/diagnosers/reliability/context_t... | Context Truncation Detector — v0.9.0 R122 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 49 | src/zephyr/feedback_loop/diagnosers/reliability/context_w... | R506: ContextWindowPressureManager | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 50 | src/zephyr/feedback_loop/diagnosers/reliability/cross_gua... | R513: CrossGuardConflictDetector | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 51 | src/zephyr/feedback_loop/diagnosers/reliability/cross_ses... | R510: CrossSessionConsistencyValidator | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 52 | src/zephyr/feedback_loop/diagnosers/reliability/data_volu... | Data Volume Growth Monitor — v0.39.0 R492 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 53 | src/zephyr/feedback_loop/diagnosers/reliability/feedback_... | Feedback Delay Compensator — v0.38.0 R477 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 54 | src/zephyr/feedback_loop/diagnosers/reliability/guard_int... | R518: GuardInteractionTopologyMapper | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 55 | src/zephyr/feedback_loop/diagnosers/reliability/guard_sel... | R512: GuardSelfConsistencyAuditor | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 56 | src/zephyr/feedback_loop/diagnosers/reliability/human_ano... | Human Anomaly Flood Detector — v0.40.0 R500 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 57 | src/zephyr/feedback_loop/diagnosers/reliability/latency_s... | Latency SLO Monitor — v0.14.0 R192 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 58 | src/zephyr/feedback_loop/diagnosers/reliability/llm_provi... | LLM Provider Integrity — v0.15.0 R217 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 59 | src/zephyr/feedback_loop/diagnosers/reliability/llm_quali... | LLM Quality Regression — v0.12.0 R161 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 60 | src/zephyr/feedback_loop/diagnosers/reliability/model_rot... | Model Rotation — v0.9.0 R125 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 61 | src/zephyr/feedback_loop/diagnosers/reliability/model_rot... | Model Rotation v2 — v0.10.0 R140 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 62 | src/zephyr/feedback_loop/diagnosers/reliability/model_ver... | Model Version Semantic Drift Monitor — v0.39.0... | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 63 | src/zephyr/feedback_loop/diagnosers/reliability/numerical... | Numerical Stability Guard — v0.38.0 R475 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 64 | src/zephyr/feedback_loop/diagnosers/reliability/operation... | Operational Seasonality — v0.16.0 R228 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 65 | src/zephyr/feedback_loop/diagnosers/reliability/prompt_fi... | Prompt Fingerprint — v0.3.0 R14 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 66 | src/zephyr/feedback_loop/diagnosers/reliability/prompt_sa... | Prompt Sanitizer — v0.10.0 R133 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 67 | src/zephyr/feedback_loop/diagnosers/reliability/recovery_... | Recovery Time Statistics — v0.37.0 R454 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 68 | src/zephyr/feedback_loop/diagnosers/reliability/regime_ga... | Regime Gain Scheduling — v0.37.0 R453 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 69 | src/zephyr/feedback_loop/diagnosers/reliability/retiremen... | Retirement Planner — v0.10.0 R139 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 70 | src/zephyr/feedback_loop/diagnosers/reliability/slo_capac... | SLO Capacity Metrics — v0.17.0+ R243-R248 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 71 | src/zephyr/feedback_loop/diagnosers/reliability/system_en... | R527: SystemEntropyMonitor | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 72 | src/zephyr/feedback_loop/diagnosers/reliability/temporal_... | Temporal Integrity Guard — v0.38.0 R478 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 73 | src/zephyr/feedback_loop/diagnosers/reliability/timezone_... | Timezone Semantic Reasoner — v0.37.0 R456 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 74 | src/zephyr/feedback_loop/diagnosers/reliability/toil_quan... | Toil Quantification — v0.37.0 R457 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 75 | src/zephyr/feedback_loop/diagnosers/reliability/value_add... | Value Added Baseline — v0.10.0 R138 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |
| 76 | src/zephyr/feedback_loop/diagnosers/reliability/zombie_fl... | Zombie FLE Detector — v0.16.0 R222 | 生产态 / production | [MOD-FEEDBACK_LOOP](../../03_modules/_cross_layer/feedback_loop/blueprint.md) |

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

> 展示全部 76 个模块（生产态 71 + 设计态 0 + 原型态 5），标签标注成熟度。

#### 第 1 页 / 共 3 页

```mermaid
graph TD
    subgraph D_FBL_DIAGNOSERS["D_FBL_DIAGNOSERS feedback_diagnosers"]
        src_zephyr_feedback_loop_diagnosers_init_py["(原型态 / prototype) feedback-loop.diagnosers — GOV-DOC-018: 71个叶...<br/>文件: __init__.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py["(生产态 / production) Adaptive Parameter Tuning — v0.37.0 R452<br/>文件: adaptive_param_tuning.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py["(生产态 / production) Cognitive Load Estimator — v0.6.0 R68<br/>文件: cognitive_load.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py["(生产态 / production) Cognitive Load Budget — v0.16.0 R223<br/>文件: cognitive_load_budget.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py["(生产态 / production) Collaborative Learning — v0.7.0 R82<br/>文件: collaborative_learning.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py["(生产态 / production) Confidence Decomposer — v0.7.0 R83<br/>文件: confidence_decomposer.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py["(生产态 / production) Gamification — v0.8.0 R101<br/>文件: gamification.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py["(生产态 / production) R516: MetaGuardLatencyBudget<br/>文件: meta_guard_latency_budget.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py["(生产态 / production) Socratic Questions — v0.7.0 R81<br/>文件: socratic_questions.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py["(生产态 / production) Tone Adapter — v0.9.0 R127<br/>文件: tone_adapter.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py["(生产态 / production) Tone Adapter v2 — v0.10.0 R141<br/>文件: tone_adapter_v2.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py["(生产态 / production) Auto Diagnosis — v0.3.0 R16<br/>文件: auto_diagnosis.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py["(生产态 / production) Causal Inference Engine — v0.3.0 R5-R7<br/>文件: causal_inference_engine.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py["(生产态 / production) Counterfactual Engine — v0.6.0 R60<br/>文件: counterfactual.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py["(生产态 / production) diagnosis_engine.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py["(生产态 / production) Diagnosis KPI — v0.9.0 R116<br/>文件: diagnosis_kpi.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py["(生产态 / production) Impact Predictor — v0.9.0 R121<br/>文件: impact_predictor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py["(生产态 / production) R504: IncidentKnowledgeInjector<br/>文件: incident_knowledge_injector.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py["(生产态 / production) Interactive Diagnosis — v0.7.0 R80<br/>文件: interactive_diagnosis.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py["(生产态 / production) Knowledge Bus Factor Monitor — v0.38.0 R481<br/>文件: knowledge_bus_factor_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py["(生产态 / production) Knowledge Market — v0.9.0 R126<br/>文件: knowledge_market.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py["(生产态 / production) MTTI Tracker — v0.16.0 R221<br/>文件: mtti_tracker.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py["(生产态 / production) Nonstationary Effectiveness — v0.37.0 R455<br/>文件: nonstationary_effectiveness.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py["(生产态 / production) Statistical Hygiene Auditor — v0.38.0 R476<br/>文件: statistical_hygiene_auditor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py["(生产态 / production) Vertical Self Assessment — v0.10.0 R137<br/>文件: vertical_self_assessment.py"]
        src_zephyr_feedback_loop_diagnosers_health_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py["(生产态 / production) R511: ActionCompositionHealthMonitor<br/>文件: action_composition_health_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py["(生产态 / production) DR Resilience Metrics — v0.17.0+ R231-R236<br/>文件: dr_resilience_metrics.py"]
    end
    src_zephyr_feedback_loop_diagnosers_init_py -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    D_FEEDBACK_LOOP["(原型态 / prototype) D_FEEDBACK_LOOP"]
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py
    D_KNOWLEDGE["(原型态 / prototype) D_KNOWLEDGE"]
    D_KNOWLEDGE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py
    D_FEEDBACK_LOOP -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py
    D_GOV_AUDIT["(原型态 / prototype) D_GOV_AUDIT"]
    D_GOV_AUDIT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py,src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py,src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py,src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py,src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py,src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py,src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py,src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py,src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py,src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py,src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py,src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py production
    class src_zephyr_feedback_loop_diagnosers_init_py,src_zephyr_feedback_loop_diagnosers_cognitive_init_py,src_zephyr_feedback_loop_diagnosers_diagnosis_init_py,src_zephyr_feedback_loop_diagnosers_health_init_py design
    class D_FEEDBACK_LOOP,D_AUTONOMY_CORE,D_KNOWLEDGE,D_GOV_AUDIT external_design
```

#### 第 2 页 / 共 3 页

```mermaid
graph TD
    subgraph D_FBL_DIAGNOSERS["D_FBL_DIAGNOSERS feedback_diagnosers"]
        src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py["(生产态 / production) E2E Integration Health Monitor — v0.39.0 R489<br/>文件: e2e_integration_health.py"]
        src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py["(生产态 / production) FLE Dogfood Monitor — v0.38.0 R480<br/>文件: fle_dogfood_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py["(生产态 / production) FLE Self SLO Metrics — v0.17.0+ R249-R254<br/>文件: fle_self_slo_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_health_global_health_map_py["(生产态 / production) Global Health Map — v0.8.0 R103<br/>文件: global_health_map.py"]
        src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py["(生产态 / production) Memory Self Check — v0.8.0 R105<br/>文件: memory_self_check.py"]
        src_zephyr_feedback_loop_diagnosers_health_model_health_py["(生产态 / production) Model Health Monitor — v0.5.0 R40<br/>文件: model_health.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py["(生产态 / production) Self Benchmark — v0.9.0 R115<br/>文件: self_benchmark.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py["(生产态 / production) Self-Bottleneck Detector — v0.38.0 R479<br/>文件: self_bottleneck_detector.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py["(生产态 / production) Self Health Monitor — v0.4.0 R29<br/>文件: self_health_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py["(生产态 / production) Self LLM Observability — v0.12.0 R160<br/>文件: self_llm_observability.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py["(生产态 / production) Amplification Guard — v0.10.0 R134<br/>文件: amplification_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py["(生产态 / production) API Dependency Metrics — v0.17.0+ R237-R242<br/>文件: api_dependency_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py["(生产态 / production) Burn Rate Alerter — v0.14.0 R200<br/>文件: burn_rate_alerter.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py["(生产态 / production) Burnout Alarm — v0.8.0 R100<br/>文件: burnout_alarm.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py["(生产态 / production) Capacity Aware Repair — v0.9.0 R120<br/>文件: capacity_aware_repair.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py["(生产态 / production) R509: ColdStartConservativeMode<br/>文件: cold_start_conservative_mode.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py["(生产态 / production) Context Truncation Detector — v0.9.0 R122<br/>文件: context_truncation.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py["(生产态 / production) R506: ContextWindowPressureManager<br/>文件: context_window_pressure_manager.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py["(生产态 / production) R513: CrossGuardConflictDetector<br/>文件: cross_guard_conflict_detector.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py["(生产态 / production) R510: CrossSessionConsistencyValidator<br/>文件: cross_session_consistency_validator.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py["(生产态 / production) Data Volume Growth Monitor — v0.39.0 R492<br/>文件: data_volume_growth_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py["(生产态 / production) Feedback Delay Compensator — v0.38.0 R477<br/>文件: feedback_delay_compensator.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py["(生产态 / production) R518: GuardInteractionTopologyMapper<br/>文件: guard_interaction_topology_mapper.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py["(生产态 / production) R512: GuardSelfConsistencyAuditor<br/>文件: guard_self_consistency_auditor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py["(生产态 / production) Human Anomaly Flood Detector — v0.40.0 R500<br/>文件: human_anomaly_flood_detector.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py["(生产态 / production) Latency SLO Monitor — v0.14.0 R192<br/>文件: latency_slo.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py["(生产态 / production) LLM Provider Integrity — v0.15.0 R217<br/>文件: llm_provider_integrity.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py["(生产态 / production) LLM Quality Regression — v0.12.0 R161<br/>文件: llm_quality_regression.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py["(生产态 / production) Model Rotation — v0.9.0 R125<br/>文件: model_rotation.py"]
    end
    D_FEEDBACK_LOOP["(原型态 / prototype) D_FEEDBACK_LOOP"]
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py
    D_INTELLIGENCE["(原型态 / prototype) D_INTELLIGENCE"]
    D_INTELLIGENCE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_model_health_py
    D_FRONTEND["(原型态 / prototype) D_FRONTEND"]
    D_FRONTEND -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py
    D_GOV_AUDIT["(原型态 / prototype) D_GOV_AUDIT"]
    D_GOV_AUDIT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py
    D_GOV_AUDIT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py
    D_GOV_AUDIT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py
    D_GOV_ENFORCEMENT["(原型态 / prototype) D_GOV_ENFORCEMENT"]
    D_GOV_ENFORCEMENT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py
    D_GOV_AUDIT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py
    D_GOV_ENFORCEMENT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py,src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py,src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py,src_zephyr_feedback_loop_diagnosers_health_global_health_map_py,src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py,src_zephyr_feedback_loop_diagnosers_health_model_health_py,src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py,src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py,src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py,src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py,src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py,src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py,src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py,src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py,src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py,src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py,src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py,src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py production
    class src_zephyr_feedback_loop_diagnosers_reliability_init_py design
    class D_FEEDBACK_LOOP,D_INTELLIGENCE,D_FRONTEND,D_AUTONOMY_CORE,D_GOV_AUDIT,D_GOV_ENFORCEMENT external_design
```

#### 第 3 页 / 共 3 页

```mermaid
graph TD
    subgraph D_FBL_DIAGNOSERS["D_FBL_DIAGNOSERS feedback_diagnosers"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py["(生产态 / production) Model Rotation v2 — v0.10.0 R140<br/>文件: model_rotation_v2.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py["(生产态 / production) Model Version Semantic Drift Monitor — v0.39.0...<br/>文件: model_version_semantic_drift.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py["(生产态 / production) Numerical Stability Guard — v0.38.0 R475<br/>文件: numerical_stability_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py["(生产态 / production) Operational Seasonality — v0.16.0 R228<br/>文件: operational_seasonality.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py["(生产态 / production) Prompt Fingerprint — v0.3.0 R14<br/>文件: prompt_fingerprint.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py["(生产态 / production) Prompt Sanitizer — v0.10.0 R133<br/>文件: prompt_sanitizer.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py["(生产态 / production) Recovery Time Statistics — v0.37.0 R454<br/>文件: recovery_time_stats.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py["(生产态 / production) Regime Gain Scheduling — v0.37.0 R453<br/>文件: regime_gain_scheduling.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py["(生产态 / production) Retirement Planner — v0.10.0 R139<br/>文件: retirement_planner.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py["(生产态 / production) SLO Capacity Metrics — v0.17.0+ R243-R248<br/>文件: slo_capacity_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py["(生产态 / production) R527: SystemEntropyMonitor<br/>文件: system_entropy_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py["(生产态 / production) Temporal Integrity Guard — v0.38.0 R478<br/>文件: temporal_integrity_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py["(生产态 / production) Timezone Semantic Reasoner — v0.37.0 R456<br/>文件: timezone_semantic_reasoner.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py["(生产态 / production) Toil Quantification — v0.37.0 R457<br/>文件: toil_quantification.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py["(生产态 / production) Value Added Baseline — v0.10.0 R138<br/>文件: value_added_baseline.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py["(生产态 / production) Zombie FLE Detector — v0.16.0 R222<br/>文件: zombie_fle_detector.py"]
    end
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py -->|导入依赖 / import_depends| D_SHARED
    D_INTELLIGENCE["(原型态 / prototype) D_INTELLIGENCE"]
    D_INTELLIGENCE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py
    D_INTELLIGENCE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py
    D_FEEDBACK_LOOP["(原型态 / prototype) D_FEEDBACK_LOOP"]
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py
    D_GOV_AUDIT["(原型态 / prototype) D_GOV_AUDIT"]
    D_GOV_AUDIT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py
    D_INFRA_RUNTIME["(原型态 / prototype) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py
    D_GOV_AUDIT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py,src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py,src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py,src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py,src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py,src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py,src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py,src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py,src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py,src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py production
    class D_SHARED external_prod
    class D_INTELLIGENCE,D_FEEDBACK_LOOP,D_AUTONOMY_CORE,D_GOV_AUDIT,D_INFRA_RUNTIME external_design
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 71 个，0 条域内依赖）。

```mermaid
graph TD
    subgraph D_FBL_DIAGNOSERS["D_FBL_DIAGNOSERS feedback_diagnosers"]
        src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py["(生产态 / production) Adaptive Parameter Tuning — v0.37.0 R452<br/>文件: adaptive_param_tuning.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py["(生产态 / production) Cognitive Load Estimator — v0.6.0 R68<br/>文件: cognitive_load.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py["(生产态 / production) Cognitive Load Budget — v0.16.0 R223<br/>文件: cognitive_load_budget.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py["(生产态 / production) Collaborative Learning — v0.7.0 R82<br/>文件: collaborative_learning.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py["(生产态 / production) Confidence Decomposer — v0.7.0 R83<br/>文件: confidence_decomposer.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py["(生产态 / production) Gamification — v0.8.0 R101<br/>文件: gamification.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py["(生产态 / production) R516: MetaGuardLatencyBudget<br/>文件: meta_guard_latency_budget.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py["(生产态 / production) Socratic Questions — v0.7.0 R81<br/>文件: socratic_questions.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py["(生产态 / production) Tone Adapter — v0.9.0 R127<br/>文件: tone_adapter.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py["(生产态 / production) Tone Adapter v2 — v0.10.0 R141<br/>文件: tone_adapter_v2.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py["(生产态 / production) Auto Diagnosis — v0.3.0 R16<br/>文件: auto_diagnosis.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py["(生产态 / production) Causal Inference Engine — v0.3.0 R5-R7<br/>文件: causal_inference_engine.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py["(生产态 / production) Counterfactual Engine — v0.6.0 R60<br/>文件: counterfactual.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py["(生产态 / production) diagnosis_engine.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py["(生产态 / production) Diagnosis KPI — v0.9.0 R116<br/>文件: diagnosis_kpi.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py["(生产态 / production) Impact Predictor — v0.9.0 R121<br/>文件: impact_predictor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py["(生产态 / production) R504: IncidentKnowledgeInjector<br/>文件: incident_knowledge_injector.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py["(生产态 / production) Interactive Diagnosis — v0.7.0 R80<br/>文件: interactive_diagnosis.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py["(生产态 / production) Knowledge Bus Factor Monitor — v0.38.0 R481<br/>文件: knowledge_bus_factor_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py["(生产态 / production) Knowledge Market — v0.9.0 R126<br/>文件: knowledge_market.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py["(生产态 / production) MTTI Tracker — v0.16.0 R221<br/>文件: mtti_tracker.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py["(生产态 / production) Nonstationary Effectiveness — v0.37.0 R455<br/>文件: nonstationary_effectiveness.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py["(生产态 / production) Statistical Hygiene Auditor — v0.38.0 R476<br/>文件: statistical_hygiene_auditor.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py["(生产态 / production) Vertical Self Assessment — v0.10.0 R137<br/>文件: vertical_self_assessment.py"]
        src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py["(生产态 / production) R511: ActionCompositionHealthMonitor<br/>文件: action_composition_health_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py["(生产态 / production) DR Resilience Metrics — v0.17.0+ R231-R236<br/>文件: dr_resilience_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py["(生产态 / production) E2E Integration Health Monitor — v0.39.0 R489<br/>文件: e2e_integration_health.py"]
        src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py["(生产态 / production) FLE Dogfood Monitor — v0.38.0 R480<br/>文件: fle_dogfood_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py["(生产态 / production) FLE Self SLO Metrics — v0.17.0+ R249-R254<br/>文件: fle_self_slo_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_health_global_health_map_py["(生产态 / production) Global Health Map — v0.8.0 R103<br/>文件: global_health_map.py"]
        src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py["(生产态 / production) Memory Self Check — v0.8.0 R105<br/>文件: memory_self_check.py"]
        src_zephyr_feedback_loop_diagnosers_health_model_health_py["(生产态 / production) Model Health Monitor — v0.5.0 R40<br/>文件: model_health.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py["(生产态 / production) Self Benchmark — v0.9.0 R115<br/>文件: self_benchmark.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py["(生产态 / production) Self-Bottleneck Detector — v0.38.0 R479<br/>文件: self_bottleneck_detector.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py["(生产态 / production) Self Health Monitor — v0.4.0 R29<br/>文件: self_health_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py["(生产态 / production) Self LLM Observability — v0.12.0 R160<br/>文件: self_llm_observability.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py["(生产态 / production) Amplification Guard — v0.10.0 R134<br/>文件: amplification_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py["(生产态 / production) API Dependency Metrics — v0.17.0+ R237-R242<br/>文件: api_dependency_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py["(生产态 / production) Burn Rate Alerter — v0.14.0 R200<br/>文件: burn_rate_alerter.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py["(生产态 / production) Burnout Alarm — v0.8.0 R100<br/>文件: burnout_alarm.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py["(生产态 / production) Capacity Aware Repair — v0.9.0 R120<br/>文件: capacity_aware_repair.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py["(生产态 / production) R509: ColdStartConservativeMode<br/>文件: cold_start_conservative_mode.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py["(生产态 / production) Context Truncation Detector — v0.9.0 R122<br/>文件: context_truncation.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py["(生产态 / production) R506: ContextWindowPressureManager<br/>文件: context_window_pressure_manager.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py["(生产态 / production) R513: CrossGuardConflictDetector<br/>文件: cross_guard_conflict_detector.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py["(生产态 / production) R510: CrossSessionConsistencyValidator<br/>文件: cross_session_consistency_validator.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py["(生产态 / production) Data Volume Growth Monitor — v0.39.0 R492<br/>文件: data_volume_growth_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py["(生产态 / production) Feedback Delay Compensator — v0.38.0 R477<br/>文件: feedback_delay_compensator.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py["(生产态 / production) R518: GuardInteractionTopologyMapper<br/>文件: guard_interaction_topology_mapper.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py["(生产态 / production) R512: GuardSelfConsistencyAuditor<br/>文件: guard_self_consistency_auditor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py["(生产态 / production) Human Anomaly Flood Detector — v0.40.0 R500<br/>文件: human_anomaly_flood_detector.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py["(生产态 / production) Latency SLO Monitor — v0.14.0 R192<br/>文件: latency_slo.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py["(生产态 / production) LLM Provider Integrity — v0.15.0 R217<br/>文件: llm_provider_integrity.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py["(生产态 / production) LLM Quality Regression — v0.12.0 R161<br/>文件: llm_quality_regression.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py["(生产态 / production) Model Rotation — v0.9.0 R125<br/>文件: model_rotation.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py["(生产态 / production) Model Rotation v2 — v0.10.0 R140<br/>文件: model_rotation_v2.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py["(生产态 / production) Model Version Semantic Drift Monitor — v0.39.0...<br/>文件: model_version_semantic_drift.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py["(生产态 / production) Numerical Stability Guard — v0.38.0 R475<br/>文件: numerical_stability_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py["(生产态 / production) Operational Seasonality — v0.16.0 R228<br/>文件: operational_seasonality.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py["(生产态 / production) Prompt Fingerprint — v0.3.0 R14<br/>文件: prompt_fingerprint.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py["(生产态 / production) Prompt Sanitizer — v0.10.0 R133<br/>文件: prompt_sanitizer.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py["(生产态 / production) Recovery Time Statistics — v0.37.0 R454<br/>文件: recovery_time_stats.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py["(生产态 / production) Regime Gain Scheduling — v0.37.0 R453<br/>文件: regime_gain_scheduling.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py["(生产态 / production) Retirement Planner — v0.10.0 R139<br/>文件: retirement_planner.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py["(生产态 / production) SLO Capacity Metrics — v0.17.0+ R243-R248<br/>文件: slo_capacity_metrics.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py["(生产态 / production) R527: SystemEntropyMonitor<br/>文件: system_entropy_monitor.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py["(生产态 / production) Temporal Integrity Guard — v0.38.0 R478<br/>文件: temporal_integrity_guard.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py["(生产态 / production) Timezone Semantic Reasoner — v0.37.0 R456<br/>文件: timezone_semantic_reasoner.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py["(生产态 / production) Toil Quantification — v0.37.0 R457<br/>文件: toil_quantification.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py["(生产态 / production) Value Added Baseline — v0.10.0 R138<br/>文件: value_added_baseline.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py["(生产态 / production) Zombie FLE Detector — v0.16.0 R222<br/>文件: zombie_fle_detector.py"]
    end
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py -->|导入依赖 / import_depends| D_SHARED
    D_FEEDBACK_LOOP["(原型态 / prototype) D_FEEDBACK_LOOP"]
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py
    D_GOV_AUDIT["(原型态 / prototype) D_GOV_AUDIT"]
    D_GOV_AUDIT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py
    D_INTELLIGENCE["(原型态 / prototype) D_INTELLIGENCE"]
    D_INTELLIGENCE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_model_health_py
    D_KNOWLEDGE["(原型态 / prototype) D_KNOWLEDGE"]
    D_KNOWLEDGE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py
    D_FRONTEND["(原型态 / prototype) D_FRONTEND"]
    D_FRONTEND -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py
    D_AUTONOMY_CORE -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py
    D_GOV_AUDIT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py
    D_GOV_AUDIT -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py
    D_FEEDBACK_LOOP -.->|测试依赖 / test_depends| src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_py,src_zephyr_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_collaborative_learning_py,src_zephyr_feedback_loop_diagnosers_cognitive_confidence_decomposer_py,src_zephyr_feedback_loop_diagnosers_cognitive_gamification_py,src_zephyr_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py,src_zephyr_feedback_loop_diagnosers_cognitive_socratic_questions_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_py,src_zephyr_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py,src_zephyr_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_counterfactual_py,src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py,src_zephyr_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py,src_zephyr_feedback_loop_diagnosers_diagnosis_impact_predictor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py,src_zephyr_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_knowledge_market_py,src_zephyr_feedback_loop_diagnosers_diagnosis_mtti_tracker_py,src_zephyr_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py,src_zephyr_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py,src_zephyr_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py,src_zephyr_feedback_loop_diagnosers_health_action_composition_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_dr_resilience_metrics_py,src_zephyr_feedback_loop_diagnosers_health_e2e_integration_health_py,src_zephyr_feedback_loop_diagnosers_health_fle_dogfood_monitor_py,src_zephyr_feedback_loop_diagnosers_health_fle_self_slo_metrics_py,src_zephyr_feedback_loop_diagnosers_health_global_health_map_py,src_zephyr_feedback_loop_diagnosers_health_memory_self_check_py,src_zephyr_feedback_loop_diagnosers_health_model_health_py,src_zephyr_feedback_loop_diagnosers_health_self_benchmark_py,src_zephyr_feedback_loop_diagnosers_health_self_bottleneck_detector_py,src_zephyr_feedback_loop_diagnosers_health_self_health_monitor_py,src_zephyr_feedback_loop_diagnosers_health_self_llm_observability_py,src_zephyr_feedback_loop_diagnosers_reliability_amplification_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_api_dependency_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_burn_rate_alerter_py,src_zephyr_feedback_loop_diagnosers_reliability_burnout_alarm_py,src_zephyr_feedback_loop_diagnosers_reliability_capacity_aware_repair_py,src_zephyr_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py,src_zephyr_feedback_loop_diagnosers_reliability_context_truncation_py,src_zephyr_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py,src_zephyr_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py,src_zephyr_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py,src_zephyr_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py,src_zephyr_feedback_loop_diagnosers_reliability_latency_slo_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_provider_integrity_py,src_zephyr_feedback_loop_diagnosers_reliability_llm_quality_regression_py,src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_py,src_zephyr_feedback_loop_diagnosers_reliability_model_rotation_v2_py,src_zephyr_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py,src_zephyr_feedback_loop_diagnosers_reliability_numerical_stability_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_operational_seasonality_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_fingerprint_py,src_zephyr_feedback_loop_diagnosers_reliability_prompt_sanitizer_py,src_zephyr_feedback_loop_diagnosers_reliability_recovery_time_stats_py,src_zephyr_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py,src_zephyr_feedback_loop_diagnosers_reliability_retirement_planner_py,src_zephyr_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py,src_zephyr_feedback_loop_diagnosers_reliability_system_entropy_monitor_py,src_zephyr_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py,src_zephyr_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py,src_zephyr_feedback_loop_diagnosers_reliability_toil_quantification_py,src_zephyr_feedback_loop_diagnosers_reliability_value_added_baseline_py,src_zephyr_feedback_loop_diagnosers_reliability_zombie_fle_detector_py production
    class D_SHARED external_prod
    class D_FEEDBACK_LOOP,D_AUTONOMY_CORE,D_GOV_AUDIT,D_INTELLIGENCE,D_KNOWLEDGE,D_FRONTEND external_design
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 5 个，4 条域内依赖）。

```mermaid
graph TD
    subgraph D_FBL_DIAGNOSERS["D_FBL_DIAGNOSERS feedback_diagnosers"]
        src_zephyr_feedback_loop_diagnosers_init_py["(原型态 / prototype) feedback-loop.diagnosers — GOV-DOC-018: 71个叶...<br/>文件: __init__.py"]
        src_zephyr_feedback_loop_diagnosers_cognitive_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_diagnosis_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_health_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_feedback_loop_diagnosers_reliability_init_py["(原型态 / prototype) __init__.py"]
    end
    src_zephyr_feedback_loop_diagnosers_init_py -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_health_init_py
    src_zephyr_feedback_loop_diagnosers_init_py -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_reliability_init_py
    D_FEEDBACK_LOOP["(生产态 / production) D_FEEDBACK_LOOP"]
    D_FEEDBACK_LOOP -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    D_FEEDBACK_LOOP -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    D_FEEDBACK_LOOP -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    D_FEEDBACK_LOOP -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    D_FEEDBACK_LOOP -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    D_FEEDBACK_LOOP -.->|导入依赖 / import_depends| src_zephyr_feedback_loop_diagnosers_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_diagnosers_init_py,src_zephyr_feedback_loop_diagnosers_cognitive_init_py,src_zephyr_feedback_loop_diagnosers_diagnosis_init_py,src_zephyr_feedback_loop_diagnosers_health_init_py,src_zephyr_feedback_loop_diagnosers_reliability_init_py design
    class D_FEEDBACK_LOOP external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | Operational Seasonality — v0.16.0 R228 (operat... | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: test_action_composition_health_monitor.py | → | R511: ActionCompositionHealthMonitor (action_co... | 测试依赖 / test_depends |
| 2 | D_AUTONOMY_CORE 自治核心: test_auto_diagnosis.py | → | Auto Diagnosis — v0.3.0 R16 (auto_diagnosis.py) | 测试依赖 / test_depends |
| 3 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_act.py | → | Self-Bottleneck Detector — v0.38.0 R479 (self_... | 测试依赖 / test_depends |
| 4 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_act.py | → | R506: ContextWindowPressureManager (context_win... | 测试依赖 / test_depends |
| 5 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_collect_detect.py | → | Statistical Hygiene Auditor — v0.38.0 R476 (st... | 测试依赖 / test_depends |
| 6 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_collect_detect.py | → | Self-Bottleneck Detector — v0.38.0 R479 (self_... | 测试依赖 / test_depends |
| 7 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_collect_detect.py | → | R509: ColdStartConservativeMode (cold_start_con... | 测试依赖 / test_depends |
| 8 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_collect_detect.py | → | R512: GuardSelfConsistencyAuditor (guard_self_c... | 测试依赖 / test_depends |
| 9 | D_AUTONOMY_CORE 自治核心: test_fl_scheduler_collect_detect.py | → | Numerical Stability Guard — v0.38.0 R475 (nume... | 测试依赖 / test_depends |
| 10 | D_AUTONOMY_CORE 自治核心: test_memory_self_check.py | → | Memory Self Check — v0.8.0 R105 (memory_self_c... | 测试依赖 / test_depends |
| 11 | D_AUTONOMY_CORE 自治核心: test_prompt_fingerprint.py | → | Prompt Fingerprint — v0.3.0 R14 (prompt_finger... | 测试依赖 / test_depends |
| 12 | D_AUTONOMY_CORE 自治核心: test_prompt_sanitizer.py | → | Prompt Sanitizer — v0.10.0 R133 (prompt_saniti... | 测试依赖 / test_depends |
| 13 | D_DATA: test_data_volume_growth_monitor.py | → | Data Volume Growth Monitor — v0.39.0 R492 (dat... | 测试依赖 / test_depends |
| 14 | D_FEEDBACK_LOOP 反馈循环引擎: FLE 全链路调度器 —— collect->detect->diagnose... | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 15 | D_FEEDBACK_LOOP 反馈循环引擎: FLE 全链路调度器 —— collect->detect->diagnose... | → | diagnosis_engine.py | 导入依赖 / import_depends |
| 16 | D_FEEDBACK_LOOP 反馈循环引擎: scheduler_act.py | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 17 | D_FEEDBACK_LOOP 反馈循环引擎: scheduler_collect_detect.py | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 18 | D_FEEDBACK_LOOP 反馈循环引擎: scheduler_health.py | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 19 | D_FEEDBACK_LOOP 反馈循环引擎: scheduler_safety.py | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 20 | D_FEEDBACK_LOOP 反馈循环引擎: E2E Integration Test Pipeline — TASK-MOD-FEEDB... | → | feedback-loop.diagnosers — GOV-DOC-018: 71个叶... | 导入依赖 / import_depends |
| 21 | D_FEEDBACK_LOOP 反馈循环引擎: test_adaptive_param_tuning.py | → | Adaptive Parameter Tuning — v0.37.0 R452 (adap... | 测试依赖 / test_depends |
| 22 | D_FEEDBACK_LOOP 反馈循环引擎: test_cognitive_load.py | → | Cognitive Load Estimator — v0.6.0 R68 (cogniti... | 测试依赖 / test_depends |
| 23 | D_FEEDBACK_LOOP 反馈循环引擎: test_collaborative_learning.py | → | Collaborative Learning — v0.7.0 R82 (collabora... | 测试依赖 / test_depends |
| 24 | D_FEEDBACK_LOOP 反馈循环引擎: test_confidence_decomposer.py | → | Confidence Decomposer — v0.7.0 R83 (confidence... | 测试依赖 / test_depends |
| 25 | D_FEEDBACK_LOOP 反馈循环引擎: test_counterfactual.py | → | Counterfactual Engine — v0.6.0 R60 (counterfac... | 测试依赖 / test_depends |
| 26 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Adaptive Parameter Tuning — v0.37.0 R452 (adap... | 测试依赖 / test_depends |
| 27 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Cognitive Load Estimator — v0.6.0 R68 (cogniti... | 测试依赖 / test_depends |
| 28 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Cognitive Load Budget — v0.16.0 R223 (cognitiv... | 测试依赖 / test_depends |
| 29 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Collaborative Learning — v0.7.0 R82 (collabora... | 测试依赖 / test_depends |
| 30 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Confidence Decomposer — v0.7.0 R83 (confidence... | 测试依赖 / test_depends |
| 31 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Tone Adapter — v0.9.0 R127 (tone_adapter.py) | 测试依赖 / test_depends |
| 32 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Tone Adapter v2 — v0.10.0 R141 (tone_adapter_v... | 测试依赖 / test_depends |
| 33 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Auto Diagnosis — v0.3.0 R16 (auto_diagnosis.py) | 测试依赖 / test_depends |
| 34 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Causal Inference Engine — v0.3.0 R5-R7 (causal... | 测试依赖 / test_depends |
| 35 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Vertical Self Assessment — v0.10.0 R137 (verti... | 测试依赖 / test_depends |
| 36 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | R511: ActionCompositionHealthMonitor (action_co... | 测试依赖 / test_depends |
| 37 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Amplification Guard — v0.10.0 R134 (amplificat... | 测试依赖 / test_depends |
| 38 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | API Dependency Metrics — v0.17.0+ R237-R242 (a... | 测试依赖 / test_depends |
| 39 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Burn Rate Alerter — v0.14.0 R200 (burn_rate_al... | 测试依赖 / test_depends |
| 40 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Burnout Alarm — v0.8.0 R100 (burnout_alarm.py) | 测试依赖 / test_depends |
| 41 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Capacity Aware Repair — v0.9.0 R120 (capacity_... | 测试依赖 / test_depends |
| 42 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | R509: ColdStartConservativeMode (cold_start_con... | 测试依赖 / test_depends |
| 43 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Context Truncation Detector — v0.9.0 R122 (con... | 测试依赖 / test_depends |
| 44 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | R506: ContextWindowPressureManager (context_win... | 测试依赖 / test_depends |
| 45 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Timezone Semantic Reasoner — v0.37.0 R456 (tim... | 测试依赖 / test_depends |
| 46 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Toil Quantification — v0.37.0 R457 (toil_quant... | 测试依赖 / test_depends |
| 47 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Value Added Baseline — v0.10.0 R138 (value_add... | 测试依赖 / test_depends |
| 48 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosers.py | → | Zombie FLE Detector — v0.16.0 R222 (zombie_fle... | 测试依赖 / test_depends |
| 49 | D_FEEDBACK_LOOP 反馈循环引擎: test_diagnosis_engine.py | → | diagnosis_engine.py | 测试依赖 / test_depends |
| 50 | D_FEEDBACK_LOOP 反馈循环引擎: test_dr_resilience_metrics.py | → | DR Resilience Metrics — v0.17.0+ R231-R236 (dr... | 测试依赖 / test_depends |
| 51 | D_FEEDBACK_LOOP 反馈循环引擎: test_e2e_integration_health.py | → | E2E Integration Health Monitor — v0.39.0 R489 ... | 测试依赖 / test_depends |
| 52 | D_FEEDBACK_LOOP 反馈循环引擎: test_feedback_delay_compensator.py | → | Feedback Delay Compensator — v0.38.0 R477 (fee... | 测试依赖 / test_depends |
| 53 | D_FEEDBACK_LOOP 反馈循环引擎: test_gamification.py | → | Gamification — v0.8.0 R101 (gamification.py) | 测试依赖 / test_depends |
| 54 | D_FEEDBACK_LOOP 反馈循环引擎: test_impact_predictor.py | → | Impact Predictor — v0.9.0 R121 (impact_predict... | 测试依赖 / test_depends |
| 55 | D_FEEDBACK_LOOP 反馈循环引擎: test_incident_knowledge_injector.py | → | R504: IncidentKnowledgeInjector (incident_knowl... | 测试依赖 / test_depends |
| 56 | D_FEEDBACK_LOOP 反馈循环引擎: test_meta_guard_latency_budget.py | → | R516: MetaGuardLatencyBudget (meta_guard_latenc... | 测试依赖 / test_depends |
| 57 | D_FEEDBACK_LOOP 反馈循环引擎: test_nonstationary_effectiveness.py | → | Nonstationary Effectiveness — v0.37.0 R455 (no... | 测试依赖 / test_depends |
| 58 | D_FEEDBACK_LOOP 反馈循环引擎: test_numerical_stability_guard.py | → | Numerical Stability Guard — v0.38.0 R475 (nume... | 测试依赖 / test_depends |
| 59 | D_FEEDBACK_LOOP 反馈循环引擎: test_operational_seasonality.py | → | Operational Seasonality — v0.16.0 R228 (operat... | 测试依赖 / test_depends |
| 60 | D_FEEDBACK_LOOP 反馈循环引擎: test_recovery_time_stats.py | → | Recovery Time Statistics — v0.37.0 R454 (recov... | 测试依赖 / test_depends |
| 61 | D_FEEDBACK_LOOP 反馈循环引擎: test_retirement_planner.py | → | Retirement Planner — v0.10.0 R139 (retirement_... | 测试依赖 / test_depends |
| 62 | D_FEEDBACK_LOOP 反馈循环引擎: test_scheduler_collect_detect.py | → | Statistical Hygiene Auditor — v0.38.0 R476 (st... | 测试依赖 / test_depends |
| 63 | D_FEEDBACK_LOOP 反馈循环引擎: test_scheduler_collect_detect.py | → | Self-Bottleneck Detector — v0.38.0 R479 (self_... | 测试依赖 / test_depends |
| 64 | D_FEEDBACK_LOOP 反馈循环引擎: test_scheduler_collect_detect.py | → | R509: ColdStartConservativeMode (cold_start_con... | 测试依赖 / test_depends |
| 65 | D_FEEDBACK_LOOP 反馈循环引擎: test_scheduler_collect_detect.py | → | R512: GuardSelfConsistencyAuditor (guard_self_c... | 测试依赖 / test_depends |
| 66 | D_FEEDBACK_LOOP 反馈循环引擎: test_scheduler_collect_detect.py | → | Numerical Stability Guard — v0.38.0 R475 (nume... | 测试依赖 / test_depends |
| 67 | D_FEEDBACK_LOOP 反馈循环引擎: test_slo_capacity_metrics.py | → | SLO Capacity Metrics — v0.17.0+ R243-R248 (slo... | 测试依赖 / test_depends |
| 68 | D_FEEDBACK_LOOP 反馈循环引擎: test_system_entropy_monitor.py | → | R527: SystemEntropyMonitor (system_entropy_moni... | 测试依赖 / test_depends |
| 69 | D_FEEDBACK_LOOP 反馈循环引擎: test_timezone_semantic_reasoner.py | → | Timezone Semantic Reasoner — v0.37.0 R456 (tim... | 测试依赖 / test_depends |
| 70 | D_FEEDBACK_LOOP 反馈循环引擎: test_vertical_self_assessment.py | → | Vertical Self Assessment — v0.10.0 R137 (verti... | 测试依赖 / test_depends |
| 71 | D_FRONTEND 前端: test_fle_dogfood_monitor.py | → | FLE Dogfood Monitor — v0.38.0 R480 (fle_dogfoo... | 测试依赖 / test_depends |
| 72 | D_FRONTEND 前端: test_fle_self_slo_metrics.py | → | FLE Self SLO Metrics — v0.17.0+ R249-R254 (fle... | 测试依赖 / test_depends |
| 73 | D_GOVERNANCE 生命周期管理: test_context_truncation.py | → | Context Truncation Detector — v0.9.0 R122 (con... | 测试依赖 / test_depends |
| 74 | D_GOVERNANCE 生命周期管理: test_context_window_pressure_manager.py | → | R506: ContextWindowPressureManager (context_win... | 测试依赖 / test_depends |
| 75 | D_GOV_AUDIT 审计追踪: test_amplification_guard.py | → | Amplification Guard — v0.10.0 R134 (amplificat... | 测试依赖 / test_depends |
| 76 | D_GOV_AUDIT 审计追踪: test_api_dependency_metrics.py | → | API Dependency Metrics — v0.17.0+ R237-R242 (a... | 测试依赖 / test_depends |
| 77 | D_GOV_AUDIT 审计追踪: test_burn_rate_alerter.py | → | Burn Rate Alerter — v0.14.0 R200 (burn_rate_al... | 测试依赖 / test_depends |
| 78 | D_GOV_AUDIT 审计追踪: test_burnout_alarm.py | → | Burnout Alarm — v0.8.0 R100 (burnout_alarm.py) | 测试依赖 / test_depends |
| 79 | D_GOV_AUDIT 审计追踪: test_causal_inference_engine.py | → | Causal Inference Engine — v0.3.0 R5-R7 (causal... | 测试依赖 / test_depends |
| 80 | D_GOV_AUDIT 审计追踪: test_cognitive_load_budget.py | → | Cognitive Load Budget — v0.16.0 R223 (cognitiv... | 测试依赖 / test_depends |
| 81 | D_GOV_AUDIT 审计追踪: test_diagnosis_kpi.py | → | Diagnosis KPI — v0.9.0 R116 (diagnosis_kpi.py) | 测试依赖 / test_depends |
| 82 | D_GOV_AUDIT 审计追踪: test_global_health_map.py | → | Global Health Map — v0.8.0 R103 (global_health... | 测试依赖 / test_depends |
| 83 | D_GOV_AUDIT 审计追踪: test_human_anomaly_flood_detector.py | → | Human Anomaly Flood Detector — v0.40.0 R500 (h... | 测试依赖 / test_depends |
| 84 | D_GOV_AUDIT 审计追踪: test_interactive_diagnosis.py | → | Interactive Diagnosis — v0.7.0 R80 (interactiv... | 测试依赖 / test_depends |
| 85 | D_GOV_AUDIT 审计追踪: test_latency_slo.py | → | Latency SLO Monitor — v0.14.0 R192 (latency_sl... | 测试依赖 / test_depends |
| 86 | D_GOV_AUDIT 审计追踪: test_mtti_tracker.py | → | MTTI Tracker — v0.16.0 R221 (mtti_tracker.py) | 测试依赖 / test_depends |
| 87 | D_GOV_AUDIT 审计追踪: test_regime_gain_scheduling.py | → | Regime Gain Scheduling — v0.37.0 R453 (regime_... | 测试依赖 / test_depends |
| 88 | D_GOV_AUDIT 审计追踪: test_socratic_questions.py | → | Socratic Questions — v0.7.0 R81 (socratic_ques... | 测试依赖 / test_depends |
| 89 | D_GOV_AUDIT 审计追踪: test_statistical_hygiene_auditor.py | → | Statistical Hygiene Auditor — v0.38.0 R476 (st... | 测试依赖 / test_depends |
| 90 | D_GOV_AUDIT 审计追踪: test_toil_quantification.py | → | Toil Quantification — v0.37.0 R457 (toil_quant... | 测试依赖 / test_depends |
| 91 | D_GOV_AUDIT 审计追踪: test_tone_adapter.py | → | Tone Adapter — v0.9.0 R127 (tone_adapter.py) | 测试依赖 / test_depends |
| 92 | D_GOV_AUDIT 审计追踪: test_tone_adapter_v2.py | → | Tone Adapter v2 — v0.10.0 R141 (tone_adapter_v... | 测试依赖 / test_depends |
| 93 | D_GOV_AUDIT 审计追踪: test_value_added_baseline.py | → | Value Added Baseline — v0.10.0 R138 (value_add... | 测试依赖 / test_depends |
| 94 | D_GOV_AUDIT 审计追踪: test_zombie_fle_detector.py | → | Zombie FLE Detector — v0.16.0 R222 (zombie_fle... | 测试依赖 / test_depends |
| 95 | D_GOV_AUDIT 审计追踪: test_self_benchmark.py | → | Self Benchmark — v0.9.0 R115 (self_benchmark.py) | 测试依赖 / test_depends |
| 96 | D_GOV_AUDIT 审计追踪: test_self_bottleneck_detector.py | → | Self-Bottleneck Detector — v0.38.0 R479 (self_... | 测试依赖 / test_depends |
| 97 | D_GOV_AUDIT 审计追踪: test_self_health_monitor.py | → | Self Health Monitor — v0.4.0 R29 (self_health_... | 测试依赖 / test_depends |
| 98 | D_GOV_AUDIT 审计追踪: test_self_llm_observability.py | → | Self LLM Observability — v0.12.0 R160 (self_ll... | 测试依赖 / test_depends |
| 99 | D_GOV_ENFORCEMENT 规则执行: test_capacity_aware_repair.py | → | Capacity Aware Repair — v0.9.0 R120 (capacity_... | 测试依赖 / test_depends |
| 100 | D_GOV_ENFORCEMENT 规则执行: test_guard_interaction_topology_mapper.py | → | R518: GuardInteractionTopologyMapper (guard_int... | 测试依赖 / test_depends |
| 101 | D_GOV_ENFORCEMENT 规则执行: test_guard_self_consistency_auditor.py | → | R512: GuardSelfConsistencyAuditor (guard_self_c... | 测试依赖 / test_depends |
| 102 | D_INFRA_RUNTIME 运行时集成: test_cold_start_conservative_mode.py | → | R509: ColdStartConservativeMode (cold_start_con... | 测试依赖 / test_depends |
| 103 | D_INFRA_RUNTIME 运行时集成: test_temporal_integrity_guard.py | → | Temporal Integrity Guard — v0.38.0 R478 (tempo... | 测试依赖 / test_depends |
| 104 | D_INTELLIGENCE 上下文管理: test_model_health.py | → | Model Health Monitor — v0.5.0 R40 (model_healt... | 测试依赖 / test_depends |
| 105 | D_INTELLIGENCE 上下文管理: test_model_rotation.py | → | Model Rotation — v0.9.0 R125 (model_rotation.py) | 测试依赖 / test_depends |
| 106 | D_INTELLIGENCE 上下文管理: test_model_rotation_v2.py | → | Model Rotation v2 — v0.10.0 R140 (model_rotati... | 测试依赖 / test_depends |
| 107 | D_INTELLIGENCE 上下文管理: test_model_version_semantic_drift.py | → | Model Version Semantic Drift Monitor — v0.39.0... | 测试依赖 / test_depends |
| 108 | D_KNOWLEDGE 知识管理: test_knowledge_bus_factor_monitor.py | → | Knowledge Bus Factor Monitor — v0.38.0 R481 (k... | 测试依赖 / test_depends |
| 109 | D_KNOWLEDGE 知识管理: test_knowledge_market.py | → | Knowledge Market — v0.9.0 R126 (knowledge_mark... | 测试依赖 / test_depends |
| 110 | D_SECURITY_LLM LLM防御: test_llm_provider_integrity.py | → | LLM Provider Integrity — v0.15.0 R217 (llm_pro... | 测试依赖 / test_depends |
| 111 | D_SECURITY_LLM LLM防御: test_llm_quality_regression.py | → | LLM Quality Regression — v0.12.0 R161 (llm_qua... | 测试依赖 / test_depends |
| 112 | D_SHARED 共享服务: test_cross_guard_conflict_detector.py | → | R513: CrossGuardConflictDetector (cross_guard_c... | 测试依赖 / test_depends |
| 113 | D_SHARED 共享服务: test_cross_session_consistency_validator.py | → | R510: CrossSessionConsistencyValidator (cross_s... | 测试依赖 / test_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 12 个外部域直接连接（出边 1 条 + 入边 113 条 = 114 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_FBL_DIAGNOSERS["D_FBL_DIAGNOSERS<br/>feedback_diagnosers"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_INTELLIGENCE["D_INTELLIGENCE<br/>上下文管理"]
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT<br/>规则执行"]
    D_FRONTEND["D_FRONTEND<br/>前端"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_KNOWLEDGE["D_KNOWLEDGE<br/>知识管理"]
    D_SECURITY_LLM["D_SECURITY_LLM<br/>LLM防御"]
    D_DATA["D_DATA"]
    D_FBL_DIAGNOSERS -->|1条 导入依赖 / import_depends| D_SHARED
    D_FEEDBACK_LOOP -->|57条 导入依赖 / import_depends, 测试依赖 / test_depends| D_FBL_DIAGNOSERS
    D_GOV_AUDIT -->|24条 测试依赖 / test_depends| D_FBL_DIAGNOSERS
    D_AUTONOMY_CORE -->|12条 测试依赖 / test_depends| D_FBL_DIAGNOSERS
    D_INTELLIGENCE -->|4条 测试依赖 / test_depends| D_FBL_DIAGNOSERS
    D_GOV_ENFORCEMENT -->|3条 测试依赖 / test_depends| D_FBL_DIAGNOSERS
    D_SHARED -->|2条 测试依赖 / test_depends| D_FBL_DIAGNOSERS
    D_FRONTEND -->|2条 测试依赖 / test_depends| D_FBL_DIAGNOSERS
    D_INFRA_RUNTIME -->|2条 测试依赖 / test_depends| D_FBL_DIAGNOSERS
    D_GOVERNANCE -->|2条 测试依赖 / test_depends| D_FBL_DIAGNOSERS
    D_KNOWLEDGE -->|2条 测试依赖 / test_depends| D_FBL_DIAGNOSERS
    D_SECURITY_LLM -->|2条 测试依赖 / test_depends| D_FBL_DIAGNOSERS
    D_DATA -->|1条 测试依赖 / test_depends| D_FBL_DIAGNOSERS
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
