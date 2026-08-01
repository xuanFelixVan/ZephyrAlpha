---
doc_type: architecture_view
title: D_FEEDBACK_LOOP 反馈循环引擎架构文档
version: "1.0"
status: active
date: 2026-08-01
owner: auto-generator
ttl: permanent
---

# 18_d_feedback_loop / 反馈循环引擎域 / Feedback Loop Engine

> **功能简介 / Overview**: 反馈循环引擎，负责系统自我改进闭环：异常检测、根因诊断、自动修复和自我进化

> **文档作用 / Purpose**: 展示 反馈循环引擎（D_FEEDBACK_LOOP）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/18_d_feedback_loop.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 18 | Number | 18 |
| 域ID | D_FEEDBACK_LOOP | Domain ID | D_FEEDBACK_LOOP |
| 域名称 | 反馈循环引擎 | Domain Name | Feedback Loop Engine |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 125 | Module Count | 125 |
| 域内依赖 | 122 | Internal Dependencies | 122 |
| 跨域入边 | 13 | Cross-domain Incoming | 13 |
| 跨域出边 | 87 | Cross-domain Outgoing | 87 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 125 | Production Modules | 125 |
| 容量 | 125/150 (正常) | Capacity | 125/150 (正常) |
| 描述 | 反馈收集器(collectors) | Description | 反馈收集器(collectors) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。全景图用颜色区分运营态/设计态，不再分页/拆子图。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景依赖图（全部模块，颜色区分运营态/设计态）

> 展示全部 125 个模块（生产态 125 + 设计态 0），节点含成熟度+中英文名+大白话+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_feedback_loop_init_py["(生产态 / production) 反馈循环域包 / Feedback Loop Domain Package<br/>反馈循环域的文件夹入口，标记该域的代码边界。本身不含业务逻辑，给域内模块一个稳定归属。<br/>文件: feedback_loop/__init__.py"]
    src_zephyr_feedback_loop_gen_inherited_py["(生产态 / production) 生成继承 / Gen Inherited<br/>生成继承模块。<br/>文件: feedback_loop/_gen_inherited.py"]
    src_zephyr_feedback_loop_actors_init_py["(生产态 / production) 反馈循环Actors包 / Feedback Loop Actors Package<br/>反馈循环域下 actors 子包，归集该方向的模块。本身不含业务逻辑，只是组织归属。<br/>文件: actors/__init__.py"]
    src_zephyr_feedback_loop_auto_evolution_py["(生产态 / production) 自动进化 / Auto Evolution<br/>定义 AutoTriggerType、AutoTrigger、AutoEvolutionConfig 等类型。<br/>文件: feedback_loop/auto_evolution.py"]
    src_zephyr_feedback_loop_backpressure_bridge_py["(生产态 / production) backpressure桥接 / Backpressure Bridge<br/>FLE -> Pipeline 背压桥接（CTR-BP-001~003）<br/>文件: feedback_loop/backpressure_bridge.py"]
    src_zephyr_feedback_loop_collectors_init_py["(生产态 / production) 反馈循环Collectors包 / Feedback Loop Collectors Package<br/>反馈循环域下 collectors 子包，归集该方向的模块。本身不含业务逻辑，只是组织归属。<br/>文件: collectors/__init__.py"]
    src_zephyr_feedback_loop_config_py["(生产态 / production) 配置 / Config<br/>定义 FLEConfig 等类型。<br/>文件: feedback_loop/config.py"]
    src_zephyr_feedback_loop_db_bridge_py["(生产态 / production) 数据库桥接 / DB Bridge<br/>FLE DB契约适配器 — 通过规范zephyr.governance.sqlite_schema连接写入fle_metrics<br/>文件: feedback_loop/db_bridge.py"]
    src_zephyr_feedback_loop_decision_engine_py["(生产态 / production) 决策引擎 / Decision Engine<br/>Feedback Loop Decision Engine<br/>文件: feedback_loop/decision_engine.py"]
    src_zephyr_feedback_loop_docs_init_py["(生产态 / production) 反馈循环Docs包 / Feedback Loop Docs Package<br/>反馈循环域下 docs 子包，归集该方向的模块。本身不含业务逻辑，只是组织归属。<br/>文件: docs/__init__.py"]
    src_zephyr_feedback_loop_error_budget_py["(生产态 / production) 错误预算 / Error Budget<br/>Error Budget 状态机——monthly budget + burn_rate + exhaust_policy。<br/>文件: feedback_loop/error_budget.py"]
    src_zephyr_feedback_loop_eval_harness_py["(生产态 / production) 评估套件 / Eval Harness<br/>定义 EvalCase、EvalOutcome、EvalCaseResult 等类型。<br/>文件: feedback_loop/eval_harness.py"]
    src_zephyr_feedback_loop_evolution_init_py["(生产态 / production) 反馈循环Evolution包 / Feedback Loop Evolution Package<br/>反馈循环域下 evolution 子包，归集该方向的模块。本身不含业务逻辑，只是组织归属。<br/>文件: evolution/__init__.py"]
    src_zephyr_feedback_loop_exceptions_py["(生产态 / production) 异常 / Exceptions<br/>定义 ForensicContext、FLEBaseException、DiagnosisError 等类型。<br/>文件: feedback_loop/exceptions.py"]
    src_zephyr_feedback_loop_feedback_collector_py["(生产态 / production) 反馈收集器 / Feedback Collector<br/>FeedbackCollector: collect task execution feedback<br/>文件: feedback_loop/feedback_collector.py"]
    src_zephyr_feedback_loop_fitness_functions_py["(生产态 / production) 适应度函数 / Fitness Functions<br/>定义 MetricStatus、FitnessThresholds、FitnessInputs 等类型。<br/>文件: feedback_loop/fitness_functions.py"]
    src_zephyr_feedback_loop_forensic_init_py["(生产态 / production) 反馈循环Forensic包 / Feedback Loop Forensic Package<br/>反馈循环域下 forensic 子包，归集该方向的模块。本身不含业务逻辑，只是组织归属。<br/>文件: forensic/__init__.py"]
    src_zephyr_feedback_loop_gates_init_py["(生产态 / production) 反馈循环Gates包 / Feedback Loop Gates Package<br/>反馈循环域下 gates 子包，归集该方向的模块。本身不含业务逻辑，只是组织归属。<br/>文件: gates/__init__.py"]
    src_zephyr_feedback_loop_generator_py["(生产态 / production) 生成器 / Generator<br/>执行骨骼代码生成. 返回 (created, skipped, errors).<br/>文件: feedback_loop/generator.py"]
    src_zephyr_feedback_loop_metrics_collector_py["(生产态 / production) 指标收集器 / Metrics Collector<br/>MetricsCollector: append-only metrics recording.<br/>文件: feedback_loop/metrics_collector.py"]
    src_zephyr_feedback_loop_resilience_init_py["(生产态 / production) 反馈循环Resilience包 / Feedback Loop Resilience Package<br/>反馈循环域下 resilience 子包，归集该方向的模块。本身不含业务逻辑，只是组织归属。<br/>文件: resilience/__init__.py"]
    src_zephyr_feedback_loop_scheduler_py["(生产态 / production) 调度器 / Scheduler<br/>FLE 全链路调度器 —— collect->detect->diagnose->act->verify 闭环。<br/>文件: feedback_loop/scheduler.py"]
    src_zephyr_feedback_loop_security_init_py["(生产态 / production) 反馈循环Security包 / Feedback Loop Security Package<br/>反馈循环域下 security 子包，归集该方向的模块。本身不含业务逻辑，只是组织归属。<br/>文件: security/__init__.py"]
    src_zephyr_feedback_loop_self_diagnosis_py["(生产态 / production) 自我诊断 / Self Diagnosis<br/>self_diagnosis.py — 自我诊断 (DD120, TASK-020)<br/>文件: feedback_loop/self_diagnosis.py"]
    src_zephyr_feedback_loop_session_learner_py["(生产态 / production) 会话learner / Session Learner<br/>session_learner.py — 在线学习 (DD114, TASK-020)<br/>文件: feedback_loop/session_learner.py"]
    src_zephyr_feedback_loop_slo_manager_py["(生产态 / production) SLO管理器 / SLO Manager<br/>5.39.6: SLOManager 进程级单例（boot_hooks 启动时实例化）。<br/>文件: feedback_loop/slo_manager.py"]
    src_zephyr_feedback_loop_tests_e2e_init_py["(生产态 / production) 反馈循环E2e包 / Feedback Loop E2e Package<br/>反馈循环域下 e2e 子包，归集该方向的模块。本身不含业务逻辑，只是组织归属。<br/>文件: e2e/__init__.py"]
    src_zephyr_feedback_loop_validator_py["(生产态 / production) 校验器 / Validator<br/>返回尚未生成的骨骼文件列表.<br/>文件: feedback_loop/validator.py"]
    src_zephyr_feedback_loop_verifiers_init_py["(生产态 / production) 反馈验证域包 / Verifiers Domain Package<br/>反馈验证域的文件夹入口，标记该域的代码边界。本身不含业务逻辑，给域内模块一个稳定归属。<br/>文件: verifiers/__init__.py"]
    src_zephyr_feedback_loop_init_py ~~~ src_zephyr_feedback_loop_gen_inherited_py
    src_zephyr_feedback_loop_gen_inherited_py ~~~ src_zephyr_feedback_loop_actors_init_py
    src_zephyr_feedback_loop_actors_init_py ~~~ src_zephyr_feedback_loop_auto_evolution_py
    src_zephyr_feedback_loop_auto_evolution_py ~~~ src_zephyr_feedback_loop_backpressure_bridge_py
    src_zephyr_feedback_loop_backpressure_bridge_py ~~~ src_zephyr_feedback_loop_collectors_init_py
    src_zephyr_feedback_loop_collectors_init_py ~~~ src_zephyr_feedback_loop_config_py
    src_zephyr_feedback_loop_config_py ~~~ src_zephyr_feedback_loop_db_bridge_py
    src_zephyr_feedback_loop_db_bridge_py ~~~ src_zephyr_feedback_loop_decision_engine_py
    src_zephyr_feedback_loop_decision_engine_py ~~~ src_zephyr_feedback_loop_docs_init_py
    src_zephyr_feedback_loop_docs_init_py ~~~ src_zephyr_feedback_loop_error_budget_py
    src_zephyr_feedback_loop_error_budget_py ~~~ src_zephyr_feedback_loop_eval_harness_py
    src_zephyr_feedback_loop_eval_harness_py ~~~ src_zephyr_feedback_loop_evolution_init_py
    src_zephyr_feedback_loop_evolution_init_py ~~~ src_zephyr_feedback_loop_exceptions_py
    src_zephyr_feedback_loop_exceptions_py ~~~ src_zephyr_feedback_loop_feedback_collector_py
    src_zephyr_feedback_loop_feedback_collector_py ~~~ src_zephyr_feedback_loop_fitness_functions_py
    src_zephyr_feedback_loop_fitness_functions_py ~~~ src_zephyr_feedback_loop_forensic_init_py
    src_zephyr_feedback_loop_forensic_init_py ~~~ src_zephyr_feedback_loop_gates_init_py
    src_zephyr_feedback_loop_gates_init_py ~~~ src_zephyr_feedback_loop_generator_py
    src_zephyr_feedback_loop_generator_py ~~~ src_zephyr_feedback_loop_metrics_collector_py
    src_zephyr_feedback_loop_metrics_collector_py ~~~ src_zephyr_feedback_loop_resilience_init_py
    src_zephyr_feedback_loop_resilience_init_py ~~~ src_zephyr_feedback_loop_scheduler_py
    src_zephyr_feedback_loop_scheduler_py ~~~ src_zephyr_feedback_loop_security_init_py
    src_zephyr_feedback_loop_security_init_py ~~~ src_zephyr_feedback_loop_self_diagnosis_py
    src_zephyr_feedback_loop_self_diagnosis_py ~~~ src_zephyr_feedback_loop_session_learner_py
    src_zephyr_feedback_loop_session_learner_py ~~~ src_zephyr_feedback_loop_slo_manager_py
    src_zephyr_feedback_loop_slo_manager_py ~~~ src_zephyr_feedback_loop_tests_e2e_init_py
    src_zephyr_feedback_loop_tests_e2e_init_py ~~~ src_zephyr_feedback_loop_validator_py
    src_zephyr_feedback_loop_validator_py ~~~ src_zephyr_feedback_loop_verifiers_init_py
    src_zephyr_feedback_loop_actors_agent_lifecycle_py["(生产态 / production) 代理生命周期 / Agent Lifecycle<br/>Agent Lifecycle Manager — v0.12.0 R159c<br/>文件: actors/agent_lifecycle.py"]
    src_zephyr_feedback_loop_actors_api_version_contract_py["(生产态 / production) API版本contract / API Version Contract<br/>API Version Contract — v0.14.0 R188<br/>文件: actors/api_version_contract.py"]
    src_zephyr_feedback_loop_actors_global_action_scheduler_py["(生产态 / production) global动作调度器 / Global Action Scheduler<br/>Global Action Scheduler — v0.16.0 R226<br/>文件: actors/global_action_scheduler.py"]
    src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py["(生产态 / production) 事件prioritytriageautomator / Incident Priority Triage Automator<br/>Incident Priority Triage Automator — v0.37.0 R463<br/>文件: actors/incident_priority_triage_automator.py"]
    src_zephyr_feedback_loop_actors_intent_driven_ops_py["(生产态 / production) intentdriven运维 / Intent Driven Ops<br/>Intent-Driven Ops — v0.12.0 R159<br/>文件: actors/intent_driven_ops.py"]
    src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py["(生产态 / production) 多代理orchestrator / Multi Agent Orchestrator<br/>Multi-Agent Orchestrator — v0.12.0 R159b<br/>文件: actors/multi_agent_orchestrator.py"]
    src_zephyr_feedback_loop_actors_notification_personalizer_py["(生产态 / production) notificationpersonalizer / Notification Personalizer<br/>Notification Personalizer — v0.6.0 R67<br/>文件: actors/notification_personalizer.py"]
    src_zephyr_feedback_loop_actors_owner_absence_escalation_py["(生产态 / production) 所有者absence升级 / Owner Absence Escalation<br/>Owner Absence Escalation — v0.37.0 R462<br/>文件: actors/owner_absence_escalation.py"]
    src_zephyr_feedback_loop_actors_saga_compensator_py["(生产态 / production) sagacompensator / Saga Compensator<br/>Saga Compensator — v0.3.0 R19b<br/>文件: actors/saga_compensator.py"]
    src_zephyr_feedback_loop_actors_secondary_alert_channel_py["(生产态 / production) secondary告警通道 / Secondary Alert Channel<br/>Secondary Alert Channel — v0.37.0 R461<br/>文件: actors/secondary_alert_channel.py"]
    src_zephyr_feedback_loop_collectors_calendar_adapter_py["(生产态 / production) calendar适配器 / Calendar Adapter<br/>Calendar Adapter — v0.8.0 R102b<br/>文件: collectors/calendar_adapter.py"]
    src_zephyr_feedback_loop_collectors_config_timeline_py["(生产态 / production) 配置timeline / Config Timeline<br/>Config Timeline — v0.8.0 R99<br/>文件: collectors/config_timeline.py"]
    src_zephyr_feedback_loop_collectors_data_quality_validator_py["(生产态 / production) 数据质量校验器 / Data Quality Validator<br/>Data Quality Validator — v0.9.0 R110<br/>文件: collectors/data_quality_validator.py"]
    src_zephyr_feedback_loop_collectors_financial_stratification_py["(生产态 / production) 金融stratification / Financial Stratification<br/>Financial Stratification — v0.5.0 R50<br/>文件: collectors/financial_stratification.py"]
    src_zephyr_feedback_loop_collectors_kb_provenance_py["(生产态 / production) 知识库溯源 / KB Provenance<br/>KB Provenance — v0.10.0 R136<br/>文件: collectors/kb_provenance.py"]
    src_zephyr_feedback_loop_collectors_knowledge_capture_py["(生产态 / production) knowledgecapture / Knowledge Capture<br/>Knowledge Capture — v0.4.0 R30<br/>文件: collectors/knowledge_capture.py"]
    src_zephyr_feedback_loop_collectors_knowledge_freshness_py["(生产态 / production) knowledgefreshness / Knowledge Freshness<br/>Knowledge Freshness — v0.5.0 R47<br/>文件: collectors/knowledge_freshness.py"]
    src_zephyr_feedback_loop_collectors_knowledge_injection_py["(生产态 / production) knowledge注入 / Knowledge Injection<br/>Knowledge Injection — v0.8.0 R102<br/>文件: collectors/knowledge_injection.py"]
    src_zephyr_feedback_loop_collectors_knowledge_packaging_py["(生产态 / production) knowledgepackaging / Knowledge Packaging<br/>Knowledge Packaging — v0.9.0 R123<br/>文件: collectors/knowledge_packaging.py"]
    src_zephyr_feedback_loop_collectors_known_unknown_registry_py["(生产态 / production) knownunknown注册表 / Known Unknown Registry<br/>Known-Unknown Registry — v0.16.0 R229<br/>文件: collectors/known_unknown_registry.py"]
    src_zephyr_feedback_loop_collectors_llm_cost_accounting_py["(生产态 / production) LLM成本accounting / LLM Cost Accounting<br/>LLM Cost Accounting — v0.4.0 R35<br/>文件: collectors/llm_cost_accounting.py"]
    src_zephyr_feedback_loop_collectors_market_calendar_py["(生产态 / production) marketcalendar / Market Calendar<br/>Market Calendar — v0.5.0 R48<br/>文件: collectors/market_calendar.py"]
    src_zephyr_feedback_loop_collectors_market_event_integrator_py["(生产态 / production) market事件integrator / Market Event Integrator<br/>Market Event Integrator — v0.14.0 R197<br/>文件: collectors/market_event_integrator.py"]
    src_zephyr_feedback_loop_collectors_notification_feedback_py["(生产态 / production) notification反馈 / Notification Feedback<br/>Notification Feedback — v0.9.0 R118<br/>文件: collectors/notification_feedback.py"]
    src_zephyr_feedback_loop_collectors_schema_evolution_py["(生产态 / production) schema进化 / Schema Evolution<br/>Schema Evolution — v0.9.0 R111<br/>文件: collectors/schema_evolution.py"]
    src_zephyr_feedback_loop_collectors_schema_migration_py["(生产态 / production) schema迁移 / Schema Migration<br/>Schema Migration — v0.14.0 R190<br/>文件: collectors/schema_migration.py"]
    src_zephyr_feedback_loop_collectors_temporal_event_store_py["(生产态 / production) temporal事件store / Temporal Event Store<br/>Temporal Event Store — v0.3.0 R9<br/>文件: collectors/temporal_event_store.py"]
    src_zephyr_feedback_loop_collectors_token_finops_py["(生产态 / production) tokenfinops / Token Finops<br/>Token FinOps — v0.12.0 R162<br/>文件: collectors/token_finops.py"]
    src_zephyr_feedback_loop_core_py["(生产态 / production) 核心 / Core<br/>FeedbackLoop core — 反馈闭环核心类。<br/>文件: feedback_loop/core.py"]
    src_zephyr_feedback_loop_db_writer_py["(生产态 / production) 数据库writer / DB Writer<br/>FLE 持久化写入器 — 写 metrics/alerts/dispatch_log 到 SQLite<br/>文件: feedback_loop/db_writer.py"]
    src_zephyr_feedback_loop_docs_cold_start_manual_py["(生产态 / production) 冷启动手册 / Cold Start Manual<br/>冷启动手册模块。<br/>文件: docs/cold_start_manual.py"]
    src_zephyr_feedback_loop_evolution_auto_reward_py["(生产态 / production) 自动reward / Auto Reward<br/>Auto Reward — v0.7.0 R76<br/>文件: evolution/auto_reward.py"]
    src_zephyr_feedback_loop_evolution_conformal_prediction_py["(生产态 / production) conformalprediction / Conformal Prediction<br/>Conformal Prediction — v0.7.0 R74<br/>文件: evolution/conformal_prediction.py"]
    src_zephyr_feedback_loop_evolution_cross_gen_validation_py["(生产态 / production) 跨生成validation / Cross Gen Validation<br/>Cross-Gen Validation — v0.7.0 R78<br/>文件: evolution/cross_gen_validation.py"]
    src_zephyr_feedback_loop_evolution_dynamic_threshold_py["(生产态 / production) dynamicthreshold / Dynamic Threshold<br/>Dynamic Threshold — v0.7.0 R71<br/>文件: evolution/dynamic_threshold.py"]
    src_zephyr_feedback_loop_evolution_ewc_kb_review_py["(生产态 / production) ewc知识库审查 / Ewc KB Review<br/>EWC KB Review — v0.6.0 R51<br/>文件: evolution/ewc_kb_review.py"]
    src_zephyr_feedback_loop_evolution_failure_replay_py["(生产态 / production) failurereplay / Failure Replay<br/>Failure Replay — v0.7.0 R77<br/>文件: evolution/failure_replay.py"]
    src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py["(生产态 / production) graduatedactivation协议 / Graduated Activation Protocol<br/>Graduated Activation Protocol — v0.38.0 R485<br/>文件: evolution/graduated_activation_protocol.py"]
    src_zephyr_feedback_loop_evolution_hypernetwork_py["(生产态 / production) hypernetwork / Hypernetwork<br/>HyperNetwork — v0.7.0 R72<br/>文件: evolution/hypernetwork.py"]
    src_zephyr_feedback_loop_evolution_knowledge_distillation_py["(生产态 / production) knowledgedistillation / Knowledge Distillation<br/>Knowledge Distillation — v0.6.0 R52<br/>文件: evolution/knowledge_distillation.py"]
    src_zephyr_feedback_loop_evolution_online_feature_importance_py["(生产态 / production) onlinefeatureimportance / Online Feature Importance<br/>Online Feature Importance — v0.7.0 R73<br/>文件: evolution/online_feature_importance.py"]
    src_zephyr_feedback_loop_evolution_prompt_factory_governance_py["(生产态 / production) 提示词工厂治理 / Prompt Factory Governance<br/>Prompt Factory Governance — v0.16.0 R224<br/>文件: evolution/prompt_factory_governance.py"]
    src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py["(生产态 / production) 提示词optimizationregression检测器 / Prompt Optimization Regression Detector<br/>R514: PromptOptimizationRegressionDetector<br/>文件: evolution/prompt_optimization_regression_detector.py"]
    src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py["(生产态 / production) 提示词自我optimization环路 / Prompt Self Optimization Loop<br/>R502: PromptSelfOptimizationLoop<br/>文件: evolution/prompt_self_optimization_loop.py"]
    src_zephyr_feedback_loop_evolution_self_reflection_py["(生产态 / production) 自我reflection / Self Reflection<br/>Self Reflection — v0.7.0 R75<br/>文件: evolution/self_reflection.py"]
    src_zephyr_feedback_loop_evolution_self_upgrade_canary_py["(生产态 / production) 自我upgradecanary / Self Upgrade Canary<br/>Self Upgrade Canary — v0.14.0 R194<br/>文件: evolution/self_upgrade_canary.py"]
    src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py["(生产态 / production) 语义intentpreservation守卫 / Semantic Intent Preservation Guard<br/>R505: SemanticIntentPreservationGuard<br/>文件: evolution/semantic_intent_preservation_guard.py"]
    src_zephyr_feedback_loop_evolution_teacher_transfer_py["(生产态 / production) teachertransfer / Teacher Transfer<br/>Teacher Transfer — v0.6.0 R53<br/>文件: evolution/teacher_transfer.py"]
    src_zephyr_feedback_loop_evolution_training_data_gov_py["(生产态 / production) training数据gov / Training Data Gov<br/>Training Data Governance — v0.14.0 R191<br/>文件: evolution/training_data_gov.py"]
    src_zephyr_feedback_loop_evolution_engine_py["(生产态 / production) 进化引擎 / Evolution Engine<br/>定义 Severity、FeedbackLayer、EvolutionSignal 等类型。<br/>文件: feedback_loop/evolution_engine.py"]
    src_zephyr_feedback_loop_forensic_architectural_sod_py["(生产态 / production) architecturalsod / Architectural Sod<br/>Architectural SoD — v0.15.0 R205<br/>文件: forensic/architectural_sod.py"]
    src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py["(生产态 / production) automatedrcapostmortem生成器 / Automated Rca Postmortem Generator<br/>Automated RCA Postmortem Generator — v0.38.0 R486<br/>文件: forensic/automated_rca_postmortem_generator.py"]
    src_zephyr_feedback_loop_forensic_crypto_bootstrap_py["(生产态 / production) cryptobootstrap / Crypto Bootstrap<br/>Cryptographic Bootstrap — v0.15.0 R204<br/>文件: forensic/crypto_bootstrap.py"]
    src_zephyr_feedback_loop_forensic_deterministic_replay_py["(生产态 / production) deterministicreplay / Deterministic Replay<br/>Deterministic Replay — v0.15.0 R206<br/>文件: forensic/deterministic_replay.py"]
    src_zephyr_feedback_loop_forensic_external_verifier_py["(生产态 / production) external验证器 / External Verifier<br/>External Verifier — v0.15.0 R203<br/>文件: forensic/external_verifier.py"]
    src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py["(生产态 / production) fleupgrade安全校验器 / Fle Upgrade Safety Validator<br/>R529: FLEUpgradeSafetyValidator<br/>文件: forensic/fle_upgrade_safety_validator.py"]
    src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py["(生产态 / production) 守卫配置漂移监控器 / Guard Configuration Drift Monitor<br/>R521: GuardConfigurationDriftMonitor<br/>文件: forensic/guard_configuration_drift_monitor.py"]
    src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py["(生产态 / production) 中断coherence校验器 / Interrupt Coherence Validator<br/>R531: InterruptCoherenceValidator<br/>文件: forensic/interrupt_coherence_validator.py"]
    src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py["(生产态 / production) knowledge注入预飞行验证器 / Knowledge Injection Pre Flight Verifier<br/>R515: KnowledgeInjectionPreFlightVerifier<br/>文件: forensic/knowledge_injection_pre_flight_verifier.py"]
    src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py["(生产态 / production) pointin时间reconstructor / Point In Time Reconstructor<br/>Point-in-Time Reconstructor — v0.37.0 R465<br/>文件: forensic/point_in_time_reconstructor.py"]
    src_zephyr_feedback_loop_forensic_self_modification_audit_py["(生产态 / production) 自我modification审计 / Self Modification Audit<br/>Self-Modification Audit — v0.15.0 R218<br/>文件: forensic/self_modification_audit.py"]
    src_zephyr_feedback_loop_forensic_serialization_format_tracker_py["(生产态 / production) serializationformat追踪器 / Serialization Format Tracker<br/>Serialization Format Tracker — v0.39.0 R488<br/>文件: forensic/serialization_format_tracker.py"]
    src_zephyr_feedback_loop_forensic_state_migration_validator_py["(生产态 / production) 状态迁移校验器 / State Migration Validator<br/>State Migration Validator — v0.40.0 R497<br/>文件: forensic/state_migration_validator.py"]
    src_zephyr_feedback_loop_forensic_sub_agent_collusion_py["(生产态 / production) sub代理collusion / Sub Agent Collusion<br/>Sub-Agent Collusion Detector — v0.15.0 R213<br/>文件: forensic/sub_agent_collusion.py"]
    src_zephyr_feedback_loop_forensic_toctou_guard_py["(生产态 / production) toctou守卫 / Toctou Guard<br/>TOCTOU Guard — v0.15.0 R207<br/>文件: forensic/toctou_guard.py"]
    src_zephyr_feedback_loop_forensic_worm_write_integrity_py["(生产态 / production) wormwrite完整性 / Worm Write Integrity<br/>WORM Write Integrity — v0.15.0 R216<br/>文件: forensic/worm_write_integrity.py"]
    src_zephyr_feedback_loop_resilience_deadman_switch_py["(生产态 / production) deadmanswitch / Deadman Switch<br/>Deadman Switch — v0.15.0 R212<br/>文件: resilience/deadman_switch.py"]
    src_zephyr_feedback_loop_resilience_dr_automation_py["(生产态 / production) drautomation / Dr Automation<br/>DR Automation — v0.14.0 R187<br/>文件: resilience/dr_automation.py"]
    src_zephyr_feedback_loop_resilience_multi_instance_coord_py["(生产态 / production) 多instancecoord / Multi Instance Coord<br/>Multi-Instance Coordinator — v0.14.0 R199<br/>文件: resilience/multi_instance_coord.py"]
    src_zephyr_feedback_loop_resilience_resource_starvation_aware_py["(生产态 / production) 资源starvation感知 / Resource Starvation Aware<br/>Resource Starvation Aware — v0.15.0 R209<br/>文件: resilience/resource_starvation_aware.py"]
    src_zephyr_feedback_loop_resilience_split_brain_quorum_py["(生产态 / production) splitbrainquorum / Split Brain Quorum<br/>Split-Brain Quorum — v0.37.0 R451<br/>文件: resilience/split_brain_quorum.py"]
    src_zephyr_feedback_loop_scheduler_act_py["(生产态 / production) 调度器执行 / Scheduler Act<br/>_escalate_on_failure 不抛异常; _auto_rollback_on_escalation 不抛异常; run_act...<br/>文件: feedback_loop/scheduler_act.py"]
    src_zephyr_feedback_loop_scheduler_collect_detect_py["(生产态 / production) 调度器收集检测 / Scheduler Collect Detect<br/>定义 CollectDetectHandler 等类型。<br/>文件: feedback_loop/scheduler_collect_detect.py"]
    src_zephyr_feedback_loop_scheduler_health_py["(生产态 / production) 调度器健康 / Scheduler Health<br/>定义 HealthReporter 等类型。<br/>文件: feedback_loop/scheduler_health.py"]
    src_zephyr_feedback_loop_scheduler_safety_py["(生产态 / production) 调度器安全 / Scheduler Safety<br/>定义 SafetyGateManager 等类型。<br/>文件: feedback_loop/scheduler_safety.py"]
    src_zephyr_feedback_loop_security_agent_skill_guard_py["(生产态 / production) 代理技能守卫 / Agent Skill Guard<br/>Agent Skill Guard — v0.14.0 R201<br/>文件: security/agent_skill_guard.py"]
    src_zephyr_feedback_loop_security_dep_cve_correlator_py["(生产态 / production) depcvecorrelator / Dep Cve Correlator<br/>Dependency CVE Correlator — v0.14.0 R196<br/>文件: security/dep_cve_correlator.py"]
    src_zephyr_feedback_loop_security_metric_prompt_scanner_py["(生产态 / production) metric提示词scanner / Metric Prompt Scanner<br/>Metric-Prompt Scanner — v0.15.0 R215<br/>文件: security/metric_prompt_scanner.py"]
    src_zephyr_feedback_loop_security_remote_attestation_py["(生产态 / production) remoteattestation / Remote Attestation<br/>Remote Attestation — v0.15.0 R211<br/>文件: security/remote_attestation.py"]
    src_zephyr_feedback_loop_security_secret_rotation_py["(生产态 / production) secretrotation / Secret Rotation<br/>Secret Rotation — v0.14.0 R189<br/>文件: security/secret_rotation.py"]
    src_zephyr_feedback_loop_template_py["(生产态 / production) 模板 / Template<br/>FeedbackLoopError<br/>文件: feedback_loop/template.py"]
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py["(生产态 / production) 集成测试流水线 / Integration Test Pipeline<br/>E2E Integration Test Pipeline — TASK-MOD-FEEDBACK_LOOP-0028 (Phase43-87)<br/>文件: e2e/integration_test_pipeline.py"]
    src_zephyr_feedback_loop_actors_agent_lifecycle_py ~~~ src_zephyr_feedback_loop_actors_api_version_contract_py
    src_zephyr_feedback_loop_actors_api_version_contract_py ~~~ src_zephyr_feedback_loop_actors_global_action_scheduler_py
    src_zephyr_feedback_loop_actors_global_action_scheduler_py ~~~ src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py
    src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py ~~~ src_zephyr_feedback_loop_actors_intent_driven_ops_py
    src_zephyr_feedback_loop_actors_intent_driven_ops_py ~~~ src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py
    src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py ~~~ src_zephyr_feedback_loop_actors_notification_personalizer_py
    src_zephyr_feedback_loop_actors_notification_personalizer_py ~~~ src_zephyr_feedback_loop_actors_owner_absence_escalation_py
    src_zephyr_feedback_loop_actors_owner_absence_escalation_py ~~~ src_zephyr_feedback_loop_actors_saga_compensator_py
    src_zephyr_feedback_loop_actors_saga_compensator_py ~~~ src_zephyr_feedback_loop_actors_secondary_alert_channel_py
    src_zephyr_feedback_loop_actors_secondary_alert_channel_py ~~~ src_zephyr_feedback_loop_collectors_calendar_adapter_py
    src_zephyr_feedback_loop_collectors_calendar_adapter_py ~~~ src_zephyr_feedback_loop_collectors_config_timeline_py
    src_zephyr_feedback_loop_collectors_config_timeline_py ~~~ src_zephyr_feedback_loop_collectors_data_quality_validator_py
    src_zephyr_feedback_loop_collectors_data_quality_validator_py ~~~ src_zephyr_feedback_loop_collectors_financial_stratification_py
    src_zephyr_feedback_loop_collectors_financial_stratification_py ~~~ src_zephyr_feedback_loop_collectors_kb_provenance_py
    src_zephyr_feedback_loop_collectors_kb_provenance_py ~~~ src_zephyr_feedback_loop_collectors_knowledge_capture_py
    src_zephyr_feedback_loop_collectors_knowledge_capture_py ~~~ src_zephyr_feedback_loop_collectors_knowledge_freshness_py
    src_zephyr_feedback_loop_collectors_knowledge_freshness_py ~~~ src_zephyr_feedback_loop_collectors_knowledge_injection_py
    src_zephyr_feedback_loop_collectors_knowledge_injection_py ~~~ src_zephyr_feedback_loop_collectors_knowledge_packaging_py
    src_zephyr_feedback_loop_collectors_knowledge_packaging_py ~~~ src_zephyr_feedback_loop_collectors_known_unknown_registry_py
    src_zephyr_feedback_loop_collectors_known_unknown_registry_py ~~~ src_zephyr_feedback_loop_collectors_llm_cost_accounting_py
    src_zephyr_feedback_loop_collectors_llm_cost_accounting_py ~~~ src_zephyr_feedback_loop_collectors_market_calendar_py
    src_zephyr_feedback_loop_collectors_market_calendar_py ~~~ src_zephyr_feedback_loop_collectors_market_event_integrator_py
    src_zephyr_feedback_loop_collectors_market_event_integrator_py ~~~ src_zephyr_feedback_loop_collectors_notification_feedback_py
    src_zephyr_feedback_loop_collectors_notification_feedback_py ~~~ src_zephyr_feedback_loop_collectors_schema_evolution_py
    src_zephyr_feedback_loop_collectors_schema_evolution_py ~~~ src_zephyr_feedback_loop_collectors_schema_migration_py
    src_zephyr_feedback_loop_collectors_schema_migration_py ~~~ src_zephyr_feedback_loop_collectors_temporal_event_store_py
    src_zephyr_feedback_loop_collectors_temporal_event_store_py ~~~ src_zephyr_feedback_loop_collectors_token_finops_py
    src_zephyr_feedback_loop_collectors_token_finops_py ~~~ src_zephyr_feedback_loop_core_py
    src_zephyr_feedback_loop_core_py ~~~ src_zephyr_feedback_loop_db_writer_py
    src_zephyr_feedback_loop_db_writer_py ~~~ src_zephyr_feedback_loop_docs_cold_start_manual_py
    src_zephyr_feedback_loop_docs_cold_start_manual_py ~~~ src_zephyr_feedback_loop_evolution_auto_reward_py
    src_zephyr_feedback_loop_evolution_auto_reward_py ~~~ src_zephyr_feedback_loop_evolution_conformal_prediction_py
    src_zephyr_feedback_loop_evolution_conformal_prediction_py ~~~ src_zephyr_feedback_loop_evolution_cross_gen_validation_py
    src_zephyr_feedback_loop_evolution_cross_gen_validation_py ~~~ src_zephyr_feedback_loop_evolution_dynamic_threshold_py
    src_zephyr_feedback_loop_evolution_dynamic_threshold_py ~~~ src_zephyr_feedback_loop_evolution_ewc_kb_review_py
    src_zephyr_feedback_loop_evolution_ewc_kb_review_py ~~~ src_zephyr_feedback_loop_evolution_failure_replay_py
    src_zephyr_feedback_loop_evolution_failure_replay_py ~~~ src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py
    src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py ~~~ src_zephyr_feedback_loop_evolution_hypernetwork_py
    src_zephyr_feedback_loop_evolution_hypernetwork_py ~~~ src_zephyr_feedback_loop_evolution_knowledge_distillation_py
    src_zephyr_feedback_loop_evolution_knowledge_distillation_py ~~~ src_zephyr_feedback_loop_evolution_online_feature_importance_py
    src_zephyr_feedback_loop_evolution_online_feature_importance_py ~~~ src_zephyr_feedback_loop_evolution_prompt_factory_governance_py
    src_zephyr_feedback_loop_evolution_prompt_factory_governance_py ~~~ src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py
    src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py ~~~ src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py
    src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py ~~~ src_zephyr_feedback_loop_evolution_self_reflection_py
    src_zephyr_feedback_loop_evolution_self_reflection_py ~~~ src_zephyr_feedback_loop_evolution_self_upgrade_canary_py
    src_zephyr_feedback_loop_evolution_self_upgrade_canary_py ~~~ src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py
    src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py ~~~ src_zephyr_feedback_loop_evolution_teacher_transfer_py
    src_zephyr_feedback_loop_evolution_teacher_transfer_py ~~~ src_zephyr_feedback_loop_evolution_training_data_gov_py
    src_zephyr_feedback_loop_evolution_training_data_gov_py ~~~ src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_evolution_engine_py ~~~ src_zephyr_feedback_loop_forensic_architectural_sod_py
    src_zephyr_feedback_loop_forensic_architectural_sod_py ~~~ src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py
    src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py ~~~ src_zephyr_feedback_loop_forensic_crypto_bootstrap_py
    src_zephyr_feedback_loop_forensic_crypto_bootstrap_py ~~~ src_zephyr_feedback_loop_forensic_deterministic_replay_py
    src_zephyr_feedback_loop_forensic_deterministic_replay_py ~~~ src_zephyr_feedback_loop_forensic_external_verifier_py
    src_zephyr_feedback_loop_forensic_external_verifier_py ~~~ src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py
    src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py ~~~ src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py
    src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py ~~~ src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py
    src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py ~~~ src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py
    src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py ~~~ src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py
    src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py ~~~ src_zephyr_feedback_loop_forensic_self_modification_audit_py
    src_zephyr_feedback_loop_forensic_self_modification_audit_py ~~~ src_zephyr_feedback_loop_forensic_serialization_format_tracker_py
    src_zephyr_feedback_loop_forensic_serialization_format_tracker_py ~~~ src_zephyr_feedback_loop_forensic_state_migration_validator_py
    src_zephyr_feedback_loop_forensic_state_migration_validator_py ~~~ src_zephyr_feedback_loop_forensic_sub_agent_collusion_py
    src_zephyr_feedback_loop_forensic_sub_agent_collusion_py ~~~ src_zephyr_feedback_loop_forensic_toctou_guard_py
    src_zephyr_feedback_loop_forensic_toctou_guard_py ~~~ src_zephyr_feedback_loop_forensic_worm_write_integrity_py
    src_zephyr_feedback_loop_forensic_worm_write_integrity_py ~~~ src_zephyr_feedback_loop_resilience_deadman_switch_py
    src_zephyr_feedback_loop_resilience_deadman_switch_py ~~~ src_zephyr_feedback_loop_resilience_dr_automation_py
    src_zephyr_feedback_loop_resilience_dr_automation_py ~~~ src_zephyr_feedback_loop_resilience_multi_instance_coord_py
    src_zephyr_feedback_loop_resilience_multi_instance_coord_py ~~~ src_zephyr_feedback_loop_resilience_resource_starvation_aware_py
    src_zephyr_feedback_loop_resilience_resource_starvation_aware_py ~~~ src_zephyr_feedback_loop_resilience_split_brain_quorum_py
    src_zephyr_feedback_loop_resilience_split_brain_quorum_py ~~~ src_zephyr_feedback_loop_scheduler_act_py
    src_zephyr_feedback_loop_scheduler_act_py ~~~ src_zephyr_feedback_loop_scheduler_collect_detect_py
    src_zephyr_feedback_loop_scheduler_collect_detect_py ~~~ src_zephyr_feedback_loop_scheduler_health_py
    src_zephyr_feedback_loop_scheduler_health_py ~~~ src_zephyr_feedback_loop_scheduler_safety_py
    src_zephyr_feedback_loop_scheduler_safety_py ~~~ src_zephyr_feedback_loop_security_agent_skill_guard_py
    src_zephyr_feedback_loop_security_agent_skill_guard_py ~~~ src_zephyr_feedback_loop_security_dep_cve_correlator_py
    src_zephyr_feedback_loop_security_dep_cve_correlator_py ~~~ src_zephyr_feedback_loop_security_metric_prompt_scanner_py
    src_zephyr_feedback_loop_security_metric_prompt_scanner_py ~~~ src_zephyr_feedback_loop_security_remote_attestation_py
    src_zephyr_feedback_loop_security_remote_attestation_py ~~~ src_zephyr_feedback_loop_security_secret_rotation_py
    src_zephyr_feedback_loop_security_secret_rotation_py ~~~ src_zephyr_feedback_loop_template_py
    src_zephyr_feedback_loop_template_py ~~~ src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py
    src_zephyr_feedback_loop_actors_action_selector_py["(生产态 / production) 动作选择器 / Action Selector<br/>定义 ActionRecord、ActionSelector 等类型。<br/>文件: actors/action_selector.py"]
    src_zephyr_feedback_loop_alert_dispatcher_py["(生产态 / production) 告警dispatcher / Alert Dispatcher<br/>FLE->Orc 告警分派器 — dispatch() 生产者<br/>文件: feedback_loop/alert_dispatcher.py"]
    src_zephyr_feedback_loop_collectors_feedback_collector_py["(生产态 / production) 反馈收集器 / Feedback Collector<br/>定义 FeedbackChannel、OwnerResponse、ActionResult 等类型。<br/>文件: collectors/feedback_collector.py"]
    src_zephyr_feedback_loop_collectors_metrics_collector_py["(生产态 / production) 指标收集器 / Metrics Collector<br/>定义 MetricSnapshot、EMABaseline、MetricsCollector 等类型。<br/>文件: collectors/metrics_collector.py"]
    src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py["(生产态 / production) 自我modificationratelimiter / Self Modification Rate Limiter<br/>R522: SelfModificationRateLimiter<br/>文件: evolution/self_modification_rate_limiter.py"]
    src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py["(生产态 / production) boot完整性attestation / Boot Integrity Attestation<br/>Boot Integrity Attestation — v0.38.0 R487<br/>文件: forensic/boot_integrity_attestation.py"]
    src_zephyr_feedback_loop_forensic_guard_complexity_budget_py["(生产态 / production) 守卫complexity预算 / Guard Complexity Budget<br/>R523: GuardComplexityBudget<br/>文件: forensic/guard_complexity_budget.py"]
    src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py["(生产态 / production) 配置hotreload守卫 / Config Hot Reload Guard<br/>Config Hot-Reload Guard — v0.40.0 R498<br/>文件: resilience/config_hot_reload_guard.py"]
    src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py["(生产态 / production) graceful降级planner / Graceful Degradation Planner<br/>Graceful Degradation Planner — v0.40.0 R496<br/>文件: resilience/graceful_degradation_planner.py"]
    src_zephyr_feedback_loop_resilience_oscillation_damping_py["(生产态 / production) oscillationdamping / Oscillation Damping<br/>Oscillation Damping — v0.37.0 R450<br/>文件: resilience/oscillation_damping.py"]
    src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py["(生产态 / production) 自我APIthrottle防御 / Self API Throttle Defense<br/>Self API Throttle Defense — v0.39.0 R491<br/>文件: resilience/self_api_throttle_defense.py"]
    src_zephyr_feedback_loop_security_wireheading_prevention_py["(生产态 / production) wireheadingprevention / Wireheading Prevention<br/>Wireheading Prevention — v0.37.0 R486<br/>文件: security/wireheading_prevention.py"]
    src_zephyr_feedback_loop_actors_action_selector_py ~~~ src_zephyr_feedback_loop_alert_dispatcher_py
    src_zephyr_feedback_loop_alert_dispatcher_py ~~~ src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_collectors_feedback_collector_py ~~~ src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_collectors_metrics_collector_py ~~~ src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py ~~~ src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py
    src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py ~~~ src_zephyr_feedback_loop_forensic_guard_complexity_budget_py
    src_zephyr_feedback_loop_forensic_guard_complexity_budget_py ~~~ src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py
    src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py ~~~ src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py ~~~ src_zephyr_feedback_loop_resilience_oscillation_damping_py
    src_zephyr_feedback_loop_resilience_oscillation_damping_py ~~~ src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py ~~~ src_zephyr_feedback_loop_security_wireheading_prevention_py
    src_zephyr_feedback_loop_actors_alert_router_py["(生产态 / production) 告警路由器 / Alert Router<br/>alert_router.py — Severity-based alert channel router.<br/>文件: actors/alert_router.py"]
    src_zephyr_feedback_loop_protocols_py["(生产态 / production) 协议 / Protocols<br/>定义 ActionType、FeedbackProtocolAdapter 等类型。<br/>文件: feedback_loop/protocols.py"]
    src_zephyr_feedback_loop_actors_alert_router_py ~~~ src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_backpressure_bridge_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_auto_evolution_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_db_writer_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_alert_dispatcher_py
    src_zephyr_feedback_loop_alert_dispatcher_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_alert_router_py
    src_zephyr_feedback_loop_decision_engine_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_generator_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_template_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_oscillation_damping_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_complexity_budget_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_db_writer_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_alert_dispatcher_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_act_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_health_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_collect_detect_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_safety_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_scheduler_collect_detect_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_scheduler_collect_detect_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_wireheading_prevention_py
    src_zephyr_feedback_loop_validator_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_template_py
    src_zephyr_feedback_loop_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_core_py
    src_zephyr_feedback_loop_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_actors_action_selector_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_agent_lifecycle_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_api_version_contract_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_global_action_scheduler_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_alert_router_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_saga_compensator_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_owner_absence_escalation_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_intent_driven_ops_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_notification_personalizer_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_secondary_alert_channel_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_config_timeline_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_calendar_adapter_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_data_quality_validator_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_financial_stratification_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_capture_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_injection_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_known_unknown_registry_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_kb_provenance_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_market_event_integrator_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_market_calendar_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_packaging_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_freshness_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_llm_cost_accounting_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_notification_feedback_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_schema_evolution_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_temporal_event_store_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_token_finops_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_schema_migration_py
    src_zephyr_feedback_loop_docs_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_docs_cold_start_manual_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_conformal_prediction_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_auto_reward_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_failure_replay_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_ewc_kb_review_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_cross_gen_validation_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_dynamic_threshold_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_knowledge_distillation_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_online_feature_importance_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_hypernetwork_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_reflection_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_upgrade_canary_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_teacher_transfer_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_factory_governance_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_training_data_gov_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_architectural_sod_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_crypto_bootstrap_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_deterministic_replay_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_external_verifier_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_complexity_budget_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_serialization_format_tracker_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_sub_agent_collusion_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_state_migration_validator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_toctou_guard_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_worm_write_integrity_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_self_modification_audit_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_deadman_switch_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_dr_automation_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_multi_instance_coord_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_oscillation_damping_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_split_brain_quorum_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_resource_starvation_aware_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_dep_cve_correlator_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_metric_prompt_scanner_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_remote_attestation_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_secret_rotation_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_agent_skill_guard_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_wireheading_prevention_py
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_tests_e2e_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py
    D_GOVERNANCE["(生产态 / production) 生命周期管理 / Lifecycle Management<br/>生命周期管理，负责蓝图/模块/任务的声明周期管理和元数据治理<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_db_bridge_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_FBL_DIAGNOSERS["(生产态 / production) 反馈诊断器 / Feedback Diagnosers<br/>反馈诊断器，负责异常根因诊断、模型健康监控、可靠性诊断和上下文窗口压力管理<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_scheduler_collect_detect_py -->|导入依赖 / import_depends| D_FBL_DIAGNOSERS
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_metrics_collector_py -->|导入依赖 / import_depends| D_SHARED
    D_FBL_VERIFICATION["(生产态 / production) 反馈验证 / Feedback Verification<br/>反馈验证，负责反馈循环门禁拦截、结果验证器执行和反馈质量检查<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    D_INFRA_RUNTIME["(生产态 / production) 运行时集成 / Runtime Integration<br/>运行时集成，负责组件生命周期编排、启动钩子和运行时上下文管理<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_feedback_loop_verifiers_init_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    src_zephyr_feedback_loop_gates_init_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    src_zephyr_feedback_loop_metrics_collector_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_GOV_DRIFT["(生产态 / production) 漂移检测 / Drift Detection<br/>漂移检测，负责架构漂移检测和漂移告警<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_feedback_loop_gates_init_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    src_zephyr_feedback_loop_slo_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_db_writer_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_feedback_loop_verifiers_init_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    D_FBL_DETECTORS["(生产态 / production) 反馈检测器 / Feedback Detectors<br/>反馈检测器，负责异常检测、漂移检测、反馈信号检测和可靠性监控<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_scheduler_collect_detect_py -->|导入依赖 / import_depends| D_FBL_DETECTORS
    D_FBL_DETECTORS -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_feedback_loop_init_py
    D_SHARED -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_secret_rotation_py
    D_FRONTEND["(生产态 / production) 前端 / Frontend<br/>前端，负责用户界面展示、交互可视化和前端状态管理<br/>跨域节点 / cross-domain"]
    D_FRONTEND -->|导入依赖 / import_depends| src_zephyr_feedback_loop_fitness_functions_py
    D_AUTONOMY_CORE["(生产态 / production) 自治核心 / Autonomy Core<br/>自治核心，负责 AI 自治决策、目标分解和执行编排<br/>跨域节点 / cross-domain"]
    D_AUTONOMY_CORE -->|测试依赖 / test_depends| src_zephyr_feedback_loop_scheduler_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_feedback_loop_init_py
    D_FBL_DETECTORS -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    D_FBL_DETECTORS -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    D_ORCHESTRATOR["(生产态 / production) 代理编排器 / Agent Orchestrator<br/>代理编排器，负责 Agent 任务全生命周期：任务入队、调度、沙箱执行、幻觉检测和收尾归档<br/>跨域节点 / cross-domain"]
    D_ORCHESTRATOR -->|导入依赖 / import_depends| src_zephyr_feedback_loop_decision_engine_py
    D_GOV_AUDIT["(生产态 / production) 审计追踪 / Audit Trail<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>跨域节点 / cross-domain"]
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_feedback_loop_init_py
    D_SECURITY["(生产态 / production) 对抗验证 / Adversarial Validation<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验证<br/>跨域节点 / cross-domain"]
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_feedback_loop_init_py
    D_AUTONOMY_CORE -->|测试依赖 / test_depends| src_zephyr_feedback_loop_error_budget_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_init_py,src_zephyr_feedback_loop_gen_inherited_py,src_zephyr_feedback_loop_actors_init_py,src_zephyr_feedback_loop_actors_action_selector_py,src_zephyr_feedback_loop_actors_agent_lifecycle_py,src_zephyr_feedback_loop_actors_alert_router_py,src_zephyr_feedback_loop_actors_api_version_contract_py,src_zephyr_feedback_loop_actors_global_action_scheduler_py,src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py,src_zephyr_feedback_loop_actors_intent_driven_ops_py,src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py,src_zephyr_feedback_loop_actors_notification_personalizer_py,src_zephyr_feedback_loop_actors_owner_absence_escalation_py,src_zephyr_feedback_loop_actors_saga_compensator_py,src_zephyr_feedback_loop_actors_secondary_alert_channel_py,src_zephyr_feedback_loop_alert_dispatcher_py,src_zephyr_feedback_loop_auto_evolution_py,src_zephyr_feedback_loop_backpressure_bridge_py,src_zephyr_feedback_loop_collectors_init_py,src_zephyr_feedback_loop_collectors_calendar_adapter_py,src_zephyr_feedback_loop_collectors_config_timeline_py,src_zephyr_feedback_loop_collectors_data_quality_validator_py,src_zephyr_feedback_loop_collectors_feedback_collector_py,src_zephyr_feedback_loop_collectors_financial_stratification_py,src_zephyr_feedback_loop_collectors_kb_provenance_py,src_zephyr_feedback_loop_collectors_knowledge_capture_py,src_zephyr_feedback_loop_collectors_knowledge_freshness_py,src_zephyr_feedback_loop_collectors_knowledge_injection_py,src_zephyr_feedback_loop_collectors_knowledge_packaging_py,src_zephyr_feedback_loop_collectors_known_unknown_registry_py,src_zephyr_feedback_loop_collectors_llm_cost_accounting_py,src_zephyr_feedback_loop_collectors_market_calendar_py,src_zephyr_feedback_loop_collectors_market_event_integrator_py,src_zephyr_feedback_loop_collectors_metrics_collector_py,src_zephyr_feedback_loop_collectors_notification_feedback_py,src_zephyr_feedback_loop_collectors_schema_evolution_py,src_zephyr_feedback_loop_collectors_schema_migration_py,src_zephyr_feedback_loop_collectors_temporal_event_store_py,src_zephyr_feedback_loop_collectors_token_finops_py,src_zephyr_feedback_loop_config_py,src_zephyr_feedback_loop_core_py,src_zephyr_feedback_loop_db_bridge_py,src_zephyr_feedback_loop_db_writer_py,src_zephyr_feedback_loop_decision_engine_py,src_zephyr_feedback_loop_docs_init_py,src_zephyr_feedback_loop_docs_cold_start_manual_py,src_zephyr_feedback_loop_error_budget_py,src_zephyr_feedback_loop_eval_harness_py,src_zephyr_feedback_loop_evolution_init_py,src_zephyr_feedback_loop_evolution_auto_reward_py,src_zephyr_feedback_loop_evolution_conformal_prediction_py,src_zephyr_feedback_loop_evolution_cross_gen_validation_py,src_zephyr_feedback_loop_evolution_dynamic_threshold_py,src_zephyr_feedback_loop_evolution_ewc_kb_review_py,src_zephyr_feedback_loop_evolution_failure_replay_py,src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py,src_zephyr_feedback_loop_evolution_hypernetwork_py,src_zephyr_feedback_loop_evolution_knowledge_distillation_py,src_zephyr_feedback_loop_evolution_online_feature_importance_py,src_zephyr_feedback_loop_evolution_prompt_factory_governance_py,src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py,src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py,src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py,src_zephyr_feedback_loop_evolution_self_reflection_py,src_zephyr_feedback_loop_evolution_self_upgrade_canary_py,src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py,src_zephyr_feedback_loop_evolution_teacher_transfer_py,src_zephyr_feedback_loop_evolution_training_data_gov_py,src_zephyr_feedback_loop_evolution_engine_py,src_zephyr_feedback_loop_exceptions_py,src_zephyr_feedback_loop_feedback_collector_py,src_zephyr_feedback_loop_fitness_functions_py,src_zephyr_feedback_loop_forensic_init_py,src_zephyr_feedback_loop_forensic_architectural_sod_py,src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py,src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py,src_zephyr_feedback_loop_forensic_crypto_bootstrap_py,src_zephyr_feedback_loop_forensic_deterministic_replay_py,src_zephyr_feedback_loop_forensic_external_verifier_py,src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py,src_zephyr_feedback_loop_forensic_guard_complexity_budget_py,src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py,src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py,src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py,src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py,src_zephyr_feedback_loop_forensic_self_modification_audit_py,src_zephyr_feedback_loop_forensic_serialization_format_tracker_py,src_zephyr_feedback_loop_forensic_state_migration_validator_py,src_zephyr_feedback_loop_forensic_sub_agent_collusion_py,src_zephyr_feedback_loop_forensic_toctou_guard_py,src_zephyr_feedback_loop_forensic_worm_write_integrity_py,src_zephyr_feedback_loop_gates_init_py,src_zephyr_feedback_loop_generator_py,src_zephyr_feedback_loop_metrics_collector_py,src_zephyr_feedback_loop_protocols_py,src_zephyr_feedback_loop_resilience_init_py,src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py,src_zephyr_feedback_loop_resilience_deadman_switch_py,src_zephyr_feedback_loop_resilience_dr_automation_py,src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py,src_zephyr_feedback_loop_resilience_multi_instance_coord_py,src_zephyr_feedback_loop_resilience_oscillation_damping_py,src_zephyr_feedback_loop_resilience_resource_starvation_aware_py,src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py,src_zephyr_feedback_loop_resilience_split_brain_quorum_py,src_zephyr_feedback_loop_scheduler_py,src_zephyr_feedback_loop_scheduler_act_py,src_zephyr_feedback_loop_scheduler_collect_detect_py,src_zephyr_feedback_loop_scheduler_health_py,src_zephyr_feedback_loop_scheduler_safety_py,src_zephyr_feedback_loop_security_init_py,src_zephyr_feedback_loop_security_agent_skill_guard_py,src_zephyr_feedback_loop_security_dep_cve_correlator_py,src_zephyr_feedback_loop_security_metric_prompt_scanner_py,src_zephyr_feedback_loop_security_remote_attestation_py,src_zephyr_feedback_loop_security_secret_rotation_py,src_zephyr_feedback_loop_security_wireheading_prevention_py,src_zephyr_feedback_loop_self_diagnosis_py,src_zephyr_feedback_loop_session_learner_py,src_zephyr_feedback_loop_slo_manager_py,src_zephyr_feedback_loop_template_py,src_zephyr_feedback_loop_tests_e2e_init_py,src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py,src_zephyr_feedback_loop_validator_py,src_zephyr_feedback_loop_verifiers_init_py production
    class D_GOVERNANCE,D_FBL_DIAGNOSERS,D_SHARED,D_FBL_VERIFICATION,D_INFRA_RUNTIME,D_GOV_DRIFT,D_FBL_DETECTORS,D_FRONTEND,D_AUTONOMY_CORE,D_ORCHESTRATOR,D_GOV_AUDIT,D_SECURITY external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_AUTONOMY_CORE 自治核心: vector桥接 / Vector Bridge (context/vector_bridge.py) | 导入依赖 / import_depends |
| 2 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_FBL_DETECTORS 反馈检测器: 反馈检测器域包 / Detectors Domain Package (detectors/__in... | 导入依赖 / import_depends |
| 3 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_FBL_DETECTORS 反馈检测器: 异常检测器 / Anomaly Detector (anomaly/anomaly_detector.py) | 导入依赖 / import_depends |
| 4 | 调度器执行 / Scheduler Act (feedback_loop/scheduler_act.py) | → | D_FBL_DETECTORS 反馈检测器: 反馈检测器域包 / Detectors Domain Package (detectors/__in... | 导入依赖 / import_depends |
| 5 | 调度器收集检测 / Scheduler Collect Detect (feedback_loop/... | → | D_FBL_DETECTORS 反馈检测器: 反馈检测器域包 / Detectors Domain Package (detectors/__in... | 导入依赖 / import_depends |
| 6 | 调度器健康 / Scheduler Health (feedback_loop/scheduler_he... | → | D_FBL_DETECTORS 反馈检测器: 反馈检测器域包 / Detectors Domain Package (detectors/__in... | 导入依赖 / import_depends |
| 7 | 集成测试流水线 / Integration Test Pipeline (e2e/integrati... | → | D_FBL_DETECTORS 反馈检测器: 反馈检测器域包 / Detectors Domain Package (detectors/__in... | 导入依赖 / import_depends |
| 8 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_FBL_DIAGNOSERS 反馈诊断器: 反馈诊断器域包 / Diagnosers Domain Package (diagnosers/__... | 导入依赖 / import_depends |
| 9 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_FBL_DIAGNOSERS 反馈诊断器: 诊断引擎 / Diagnosis Engine (diagnosis/diagnosis_engine.py) | 导入依赖 / import_depends |
| 10 | 调度器执行 / Scheduler Act (feedback_loop/scheduler_act.py) | → | D_FBL_DIAGNOSERS 反馈诊断器: 反馈诊断器域包 / Diagnosers Domain Package (diagnosers/__... | 导入依赖 / import_depends |
| 11 | 调度器收集检测 / Scheduler Collect Detect (feedback_loop/... | → | D_FBL_DIAGNOSERS 反馈诊断器: 反馈诊断器域包 / Diagnosers Domain Package (diagnosers/__... | 导入依赖 / import_depends |
| 12 | 调度器健康 / Scheduler Health (feedback_loop/scheduler_he... | → | D_FBL_DIAGNOSERS 反馈诊断器: 反馈诊断器域包 / Diagnosers Domain Package (diagnosers/__... | 导入依赖 / import_depends |
| 13 | 调度器安全 / Scheduler Safety (feedback_loop/scheduler_sa... | → | D_FBL_DIAGNOSERS 反馈诊断器: 反馈诊断器域包 / Diagnosers Domain Package (diagnosers/__... | 导入依赖 / import_depends |
| 14 | 集成测试流水线 / Integration Test Pipeline (e2e/integrati... | → | D_FBL_DIAGNOSERS 反馈诊断器: 反馈诊断器域包 / Diagnosers Domain Package (diagnosers/__... | 导入依赖 / import_depends |
| 15 | 反馈循环Gates包 / Feedback Loop Gates Package (gates/__in... | → | D_FBL_VERIFICATION 反馈验证: 治理门禁 / Governance Gates (gates/_governance_gates.py) | 导入依赖 / import_depends |
| 16 | 反馈循环Gates包 / Feedback Loop Gates Package (gates/__in... | → | D_FBL_VERIFICATION 反馈验证: 运营门禁 / Operational Gates (gates/_operational_gates.py) | 导入依赖 / import_depends |
| 17 | 反馈循环Gates包 / Feedback Loop Gates Package (gates/__in... | → | D_FBL_VERIFICATION 反馈验证: 安全门禁 / Safety Gates (gates/_safety_gates.py) | 导入依赖 / import_depends |
| 18 | 反馈循环Gates包 / Feedback Loop Gates Package (gates/__in... | → | D_FBL_VERIFICATION 反馈验证: 安全门禁 / Security Gates (gates/_security_gates.py) | 导入依赖 / import_depends |
| 19 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_FBL_VERIFICATION 反馈验证: 验证引擎 / Verification Engine (verifiers/verification_en... | 导入依赖 / import_depends |
| 20 | 调度器执行 / Scheduler Act (feedback_loop/scheduler_act.py) | → | D_FBL_VERIFICATION 反馈验证: cascadingrollback分析器 / Cascading Rollback Analyzer (ve... | 导入依赖 / import_depends |
| 21 | 调度器执行 / Scheduler Act (feedback_loop/scheduler_act.py) | → | D_FBL_VERIFICATION 反馈验证: stochastic诊断验证器 / Stochastic Diagnosis Verifier (ver... | 导入依赖 / import_depends |
| 22 | 调度器执行 / Scheduler Act (feedback_loop/scheduler_act.py) | → | D_FBL_VERIFICATION 反馈验证: 验证引擎 / Verification Engine (verifiers/verification_en... | 导入依赖 / import_depends |
| 23 | 调度器安全 / Scheduler Safety (feedback_loop/scheduler_sa... | → | D_FBL_VERIFICATION 反馈验证: deploymentsuppression / Deployment Suppression (gates/dep... | 导入依赖 / import_depends |
| 24 | 调度器安全 / Scheduler Safety (feedback_loop/scheduler_sa... | → | D_FBL_VERIFICATION 反馈验证: 安全门禁l1l27 / Safety Gate L1 L27 (gates/safety_gate_l1_... | 导入依赖 / import_depends |
| 25 | 集成测试流水线 / Integration Test Pipeline (e2e/integrati... | → | D_FBL_VERIFICATION 反馈验证: 安全门禁l1l27 / Safety Gate L1 L27 (gates/safety_gate_l1_... | 导入依赖 / import_depends |
| 26 | 集成测试流水线 / Integration Test Pipeline (e2e/integrati... | → | D_FBL_VERIFICATION 反馈验证: 安全门禁l66l67 / Safety Gate L66 L67 (gates/safety_gate_l... | 导入依赖 / import_depends |
| 27 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: ab测试 / Ab Test (verifiers/ab_test.py) | 导入依赖 / import_depends |
| 28 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: 动作explainability / Action Explainability (verifiers/act... | 导入依赖 / import_depends |
| 29 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: AIcommentveracity / AI Comment Veracity (verifiers/ai_com... | 导入依赖 / import_depends |
| 30 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: 攻击simulator / Attack Simulator (verifiers/attack_simula... | 导入依赖 / import_depends |
| 31 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: 自动rollback / Auto Rollback (verifiers/auto_rollback.py) | 导入依赖 / import_depends |
| 32 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: buildreproducibility验证器 / Build Reproducibility Verifi... | 导入依赖 / import_depends |
| 33 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: canaryrepair / Canary Repair (verifiers/canary_repair.py) | 导入依赖 / import_depends |
| 34 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: cascadingrollback分析器 / Cascading Rollback Analyzer (ve... | 导入依赖 / import_depends |
| 35 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: 跨蓝图contract漂移 / Cross Blueprint Contract Drift (veri... | 导入依赖 / import_depends |
| 36 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: 跨模块集成 / Cross Module Integration (verifiers/cross_mo... | 导入依赖 / import_depends |
| 37 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: 跨会话knowledge完整性 / Cross Session Knowledge Integrity... | 导入依赖 / import_depends |
| 38 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: 数字孪生沙箱 / Digital Twin Sandbox (verifiers/digital_tw... | 导入依赖 / import_depends |
| 39 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: dryrun沙箱 / Dry Run Sandbox (verifiers/dry_run_sandbox.py) | 导入依赖 / import_depends |
| 40 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: federated协议 / Federated Protocol (verifiers/federated_p... | 导入依赖 / import_depends |
| 41 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: golden测试external / Golden Test External (verifiers/gold... | 导入依赖 / import_depends |
| 42 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: noLLM降级 / No LLM Degradation (verifiers/no_llm_degradat... | 导入依赖 / import_depends |
| 43 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: 预飞行simulator / Pre Flight Simulator (verifiers/pre_fli... | 导入依赖 / import_depends |
| 44 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: preventiverepair / Preventive Repair (verifiers/preventiv... | 导入依赖 / import_depends |
| 45 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: rollback完整性 / Rollback Integrity (verifiers/rollback_i... | 导入依赖 / import_depends |
| 46 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: sim2realcalibration / Sim2real Calibration (verifiers/sim... | 导入依赖 / import_depends |
| 47 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: stochastic诊断验证器 / Stochastic Diagnosis Verifier (ver... | 导入依赖 / import_depends |
| 48 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: toctourevalidation / Toctou Revalidation (verifiers/tocto... | 导入依赖 / import_depends |
| 49 | 反馈验证域包 / Verifiers Domain Package (verifiers/__init... | → | D_FBL_VERIFICATION 反馈验证: 验证引擎 / Verification Engine (verifiers/verification_en... | 导入依赖 / import_depends |
| 50 | 告警dispatcher / Alert Dispatcher (feedback_loop/alert_di... | → | D_GOVERNANCE 生命周期管理: sqliteschema / Sqlite Schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 51 | 数据库桥接 / DB Bridge (feedback_loop/db_bridge.py) | → | D_GOVERNANCE 生命周期管理: sqliteschema / Sqlite Schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 52 | 数据库writer / DB Writer (feedback_loop/db_writer.py) | → | D_GOVERNANCE 生命周期管理: sqliteschema / Sqlite Schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 53 | 指标收集器 / Metrics Collector (feedback_loop/metrics_col... | → | D_GOVERNANCE 生命周期管理: sqliteschema / Sqlite Schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 54 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_GOV_DRIFT 漂移检测: 漂移引擎 / Drift Engine (gov_drift/drift_engine.py) | 导入依赖 / import_depends |
| 55 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_GOV_DRIFT 漂移检测: 完整性 / Integrity (governance/integrity.py) | 导入依赖 / import_depends |
| 56 | 调度器执行 / Scheduler Act (feedback_loop/scheduler_act.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级引擎 / Escalation Engine (escalation/escalation_engin... | 导入依赖 / import_depends |
| 57 | 调度器执行 / Scheduler Act (feedback_loop/scheduler_act.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级模型 / Escalation Models (escalation/escalation_model... | 导入依赖 / import_depends |
| 58 | 调度器执行 / Scheduler Act (feedback_loop/scheduler_act.py) | → | D_INFRA_RECOVERY 回滚恢复: rollbackexecutor / Rollback Executor (rollback/rollback_e... | 导入依赖 / import_depends |
| 59 | backpressure桥接 / Backpressure Bridge (feedback_loop/bac... | → | D_INFRA_RUNTIME 运行时集成: backpressure管理器 / Backpressure Manager (pipeline/backp... | 导入依赖 / import_depends |
| 60 | 数据库writer / DB Writer (feedback_loop/db_writer.py) | → | D_INFRA_RUNTIME 运行时集成: 指标桥接 / Metrics Bridge (system_telemetry/metrics_bridg... | 导入依赖 / import_depends |
| 61 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_INFRA_RUNTIME 运行时集成: 指标桥接 / Metrics Bridge (system_telemetry/metrics_bridg... | 导入依赖 / import_depends |
| 62 | 协议 / Protocols (feedback_loop/protocols.py) | → | D_INTEGRATION 管线路由: 协议 / Protocols (contracts/protocols.py) | 导入依赖 / import_depends |
| 63 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_INTEGRATION 管线路由: inprocessvectormemory / In Process Vector Memory (vector_... | 导入依赖 / import_depends |
| 64 | 告警dispatcher / Alert Dispatcher (feedback_loop/alert_di... | → | D_ORCHESTRATOR 代理编排器: 告警handler / Alert Handler (contracts/alert_handler.py) | 导入依赖 / import_depends |
| 65 | 进化引擎 / Evolution Engine (feedback_loop/evolution_engi... | → | D_SECURITY 对抗验证: gateway / Gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 66 | API版本contract / API Version Contract (actors/api_versio... | → | D_SHARED 共享服务: 时间utils / Time Utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 67 | 核心 / Core (feedback_loop/core.py) | → | D_SHARED 共享服务: serialization / Serialization (io/serialization.py) | 导入依赖 / import_depends |
| 68 | 核心 / Core (feedback_loop/core.py) | → | D_SHARED 共享服务: 模式 / Schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 69 | 核心 / Core (feedback_loop/core.py) | → | D_SHARED 共享服务: 时间utils / Time Utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 70 | 数据库桥接 / DB Bridge (feedback_loop/db_bridge.py) | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 71 | 进化引擎 / Evolution Engine (feedback_loop/evolution_engi... | → | D_SHARED 共享服务: 异步utils / Async Utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 72 | 反馈收集器 / Feedback Collector (feedback_loop/feedback_c... | → | D_SHARED 共享服务: serialization / Serialization (io/serialization.py) | 导入依赖 / import_depends |
| 73 | 反馈收集器 / Feedback Collector (feedback_loop/feedback_c... | → | D_SHARED 共享服务: 模式 / Schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 74 | 反馈收集器 / Feedback Collector (feedback_loop/feedback_c... | → | D_SHARED 共享服务: 时间utils / Time Utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 75 | 适应度函数 / Fitness Functions (feedback_loop/fitness_fun... | → | D_SHARED 共享服务: serialization / Serialization (io/serialization.py) | 导入依赖 / import_depends |
| 76 | 自我modification审计 / Self Modification Audit (forensic/... | → | D_SHARED 共享服务: 时间utils / Time Utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 77 | 指标收集器 / Metrics Collector (feedback_loop/metrics_col... | → | D_SHARED 共享服务: sqlite工厂 / Sqlite Factory (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 78 | 配置hotreload守卫 / Config Hot Reload Guard (resilience/c... | → | D_SHARED 共享服务: serialization / Serialization (io/serialization.py) | 导入依赖 / import_depends |
| 79 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_SHARED 共享服务: 事件总线 / Event Bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 80 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 81 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_SHARED 共享服务: ports / Ports (protocols/ports.py) | 导入依赖 / import_depends |
| 82 | 调度器 / Scheduler (feedback_loop/scheduler.py) | → | D_SHARED 共享服务: 异步utils / Async Utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 83 | 调度器执行 / Scheduler Act (feedback_loop/scheduler_act.py) | → | D_SHARED 共享服务: 事件总线 / Event Bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 84 | 调度器安全 / Scheduler Safety (feedback_loop/scheduler_sa... | → | D_SHARED 共享服务: paths / Paths (io/paths.py) | 导入依赖 / import_depends |
| 85 | secretrotation / Secret Rotation (security/secret_rotatio... | → | D_SHARED 共享服务: 密钥 / Secrets (security/secrets.py) | 导入依赖 / import_depends |
| 86 | SLO管理器 / SLO Manager (feedback_loop/slo_manager.py) | → | D_SHARED 共享服务: 事件总线 / Event Bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 87 | SLO管理器 / SLO Manager (feedback_loop/slo_manager.py) | → | D_SHARED 共享服务: 指标 / Metrics (observability/metrics.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: 测试f14流水线extreme / Test F14 Pipeline Extreme (extreme... | → | 错误预算 / Error Budget (feedback_loop/error_budget.py) | 测试依赖 / test_depends |
| 2 | D_AUTONOMY_CORE 自治核心: 测试f14流水线extreme / Test F14 Pipeline Extreme (extreme... | → | 调度器 / Scheduler (feedback_loop/scheduler.py) | 测试依赖 / test_depends |
| 3 | D_FBL_DETECTORS 反馈检测器: 异常检测器 / Anomaly Detector (anomaly/anomaly_detector.py) | → | 反馈收集器 / Feedback Collector (collectors/feedback_coll... | 导入依赖 / import_depends |
| 4 | D_FBL_DETECTORS 反馈检测器: 异常检测器 / Anomaly Detector (anomaly/anomaly_detector.py) | → | 指标收集器 / Metrics Collector (collectors/metrics_collec... | 导入依赖 / import_depends |
| 5 | D_FBL_DETECTORS 反馈检测器: 异常检测器 / Anomaly Detector (anomaly/anomaly_detector.py) | → | 协议 / Protocols (feedback_loop/protocols.py) | 导入依赖 / import_depends |
| 6 | D_FRONTEND 前端: 适应度函数 / Fitness Functions (components/fitness_functi... | → | 适应度函数 / Fitness Functions (feedback_loop/fitness_fun... | 导入依赖 / import_depends |
| 7 | D_GOV_AUDIT 审计追踪: 反馈桥接 / Feedback Bridge (gov_audit/feedback_bridge.py) | → | 反馈循环域包 / Feedback Loop Domain Package (feedback_loo... | 导入依赖 / import_depends |
| 8 | D_INFRA_RUNTIME 运行时集成: 自动运行时核心 / Auto Runtime Core (trading/auto_runtime_... | → | 反馈循环域包 / Feedback Loop Domain Package (feedback_loo... | 导入依赖 / import_depends |
| 9 | D_INFRA_RUNTIME 运行时集成: 自动运行时核心 / Auto Runtime Core (trading/auto_runtime_... | → | 调度器 / Scheduler (feedback_loop/scheduler.py) | 导入依赖 / import_depends |
| 10 | D_INFRA_RUNTIME 运行时集成: 生命周期管理器 / Lifecycle Manager (trading/lifecycle_man... | → | 反馈循环域包 / Feedback Loop Domain Package (feedback_loo... | 导入依赖 / import_depends |
| 11 | D_ORCHESTRATOR 代理编排器: 触发器路由器 / Trigger Router (execution/trigger_router.py) | → | 决策引擎 / Decision Engine (feedback_loop/decision_engine... | 导入依赖 / import_depends |
| 12 | D_SECURITY 对抗验证: 反馈桥接 / Feedback Bridge (orphan_judge/feedback_bridge.py) | → | 反馈循环域包 / Feedback Loop Domain Package (feedback_loo... | 导入依赖 / import_depends |
| 13 | D_SHARED 共享服务: 密钥 / Secrets (security/secrets.py) | → | secretrotation / Secret Rotation (security/secret_rotatio... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 15 个外部域直接连接（出边 87 条 + 入边 13 条 = 100 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_FBL_VERIFICATION["D_FBL_VERIFICATION<br/>反馈验证"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_FBL_DIAGNOSERS["D_FBL_DIAGNOSERS<br/>反馈诊断器"]
    D_FBL_DETECTORS["D_FBL_DETECTORS<br/>反馈检测器"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_GOV_OPS_RESILIENCE["D_GOV_OPS_RESILIENCE<br/>运维弹性治理"]
    D_GOV_DRIFT["D_GOV_DRIFT<br/>漂移检测"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_INFRA_RECOVERY["D_INFRA_RECOVERY<br/>回滚恢复"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_FRONTEND["D_FRONTEND<br/>前端"]
    D_FEEDBACK_LOOP -->|35条 导入依赖 / import_depends| D_FBL_VERIFICATION
    D_FEEDBACK_LOOP -->|22条 导入依赖 / import_depends| D_SHARED
    D_FEEDBACK_LOOP -->|7条 导入依赖 / import_depends| D_FBL_DIAGNOSERS
    D_FEEDBACK_LOOP -->|6条 导入依赖 / import_depends| D_FBL_DETECTORS
    D_FEEDBACK_LOOP -->|4条 导入依赖 / import_depends| D_GOVERNANCE
    D_FEEDBACK_LOOP -->|3条 导入依赖 / import_depends| D_INFRA_RUNTIME
    D_FEEDBACK_LOOP -->|2条 导入依赖 / import_depends| D_GOV_OPS_RESILIENCE
    D_FEEDBACK_LOOP -->|2条 导入依赖 / import_depends| D_GOV_DRIFT
    D_FEEDBACK_LOOP -->|2条 导入依赖 / import_depends| D_INTEGRATION
    D_FEEDBACK_LOOP -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_FEEDBACK_LOOP -->|1条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_FEEDBACK_LOOP -->|1条 导入依赖 / import_depends| D_SECURITY
    D_FEEDBACK_LOOP -->|1条 导入依赖 / import_depends| D_INFRA_RECOVERY
    D_INFRA_RUNTIME -->|3条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_FBL_DETECTORS -->|3条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_AUTONOMY_CORE -->|2条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_GOV_AUDIT -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_FRONTEND -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_ORCHESTRATOR -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_SECURITY -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
    D_SHARED -->|1条 导入依赖 / import_depends| D_FEEDBACK_LOOP
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
