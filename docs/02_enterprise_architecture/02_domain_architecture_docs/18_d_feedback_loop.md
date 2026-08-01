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

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 125 个模块（生产态 125 + 设计态 0），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_feedback_loop_init_py["(生产态 / production) 包入口 / Feedback Loop<br/>Engine — MOD-FEEDBACK_LOOP.<br/>包入口。Feedback Loop Engine — MOD-FEEDBACK_<br/>LOOP.<br/>文件: feedback_loop/__init__.py"]
    src_zephyr_feedback_loop_gen_inherited_py["(生产态 / production) 生成inherited / _gen_<br/>inherited<br/>生成inherited，提供包入口和模块加载功能<br/>文件: feedback_loop/_gen_inherited.py"]
    src_zephyr_feedback_loop_actors_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.actors — auto-generated package<br/>init.<br/>包入口。feedback-loop.actors — auto-generated<br/>package init.<br/>文件: actors/__init__.py"]
    src_zephyr_feedback_loop_auto_evolution_py["(生产态 / production) 自动进化 / auto_evolution<br/>自动进化，反馈闭环的核心调度模块，整合包入口、告<br/>警管理器、告警precision追踪器、双通道告警等21个<br/>子模块协同工作。<br/>文件: feedback_loop/auto_evolution.py"]
    src_zephyr_feedback_loop_backpressure_bridge_py["(生产态 / production) 背压桥接 / backpressure_<br/>bridge<br/>FLE -> Pipeline 背压桥接（CTR-BP-001~003）<br/>文件: feedback_loop/backpressure_bridge.py"]
    src_zephyr_feedback_loop_collectors_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.collectors — auto-generated<br/>package init.<br/>包入口。feedback-loop.collectors —<br/>auto-generated package init.<br/>文件: collectors/__init__.py"]
    src_zephyr_feedback_loop_config_py["(生产态 / production) 配置 / config<br/>配置，反馈闭环的配置，管理配置项的读取和校验。<br/>文件: feedback_loop/config.py"]
    src_zephyr_feedback_loop_db_bridge_py["(生产态 / production) 数据库桥接 / db_bridge<br/>FLE DB契约适配器 —<br/>通过规范zephyr.governance.sqlite_<br/>schema连接写入fle_metrics<br/>文件: feedback_loop/db_bridge.py"]
    src_zephyr_feedback_loop_decision_engine_py["(生产态 / production) 决策引擎 / Feedback Loop<br/>Decision Engine<br/>决策引擎。Feedback Loop Decision Engine<br/>文件: feedback_loop/decision_engine.py"]
    src_zephyr_feedback_loop_docs_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.docs — auto-generated package<br/>init.<br/>包入口。feedback-loop.docs — auto-generated<br/>package init.<br/>文件: docs/__init__.py"]
    src_zephyr_feedback_loop_error_budget_py["(生产态 / production) 错误预算 / error_budget<br/>Error Budget 状态机——monthly budget + burn_rate<br/>+ exhaust_policy。<br/>文件: feedback_loop/error_budget.py"]
    src_zephyr_feedback_loop_eval_harness_py["(生产态 / production) 评估harness / eval_harness<br/>评估harness，提供包入口和模块加载功能<br/>文件: feedback_loop/eval_harness.py"]
    src_zephyr_feedback_loop_evolution_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.evolution — auto-generated<br/>package init.<br/>包入口。feedback-loop.evolution —<br/>auto-generated package init.<br/>文件: evolution/__init__.py"]
    src_zephyr_feedback_loop_exceptions_py["(生产态 / production) 异常 / exceptions<br/>异常，提供包入口和模块加载功能<br/>文件: feedback_loop/exceptions.py"]
    src_zephyr_feedback_loop_feedback_collector_py["(生产态 / production) 反馈收集器 /<br/>FeedbackCollector: collect task execution<br/>feedback<br/>反馈收集器。FeedbackCollector: collect task<br/>execution feedback<br/>文件: feedback_loop/feedback_collector.py"]
    src_zephyr_feedback_loop_fitness_functions_py["(生产态 / production) 适应度functions / fitness_<br/>functions<br/>适应度functions，提供包入口和模块加载功能<br/>文件: feedback_loop/fitness_functions.py"]
    src_zephyr_feedback_loop_forensic_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.forensic — auto-generated package<br/>init.<br/>包入口。feedback-loop.forensic — auto-generated<br/>package init.<br/>文件: forensic/__init__.py"]
    src_zephyr_feedback_loop_gates_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.gates — auto-generated package<br/>init.<br/>包入口。feedback-loop.gates — auto-generated<br/>package init.<br/>文件: gates/__init__.py"]
    src_zephyr_feedback_loop_generator_py["(生产态 / production) 生成器 / generator<br/>执行骨骼代码生成. 返回 (created, skipped,<br/>errors).<br/>文件: feedback_loop/generator.py"]
    src_zephyr_feedback_loop_metrics_collector_py["(生产态 / production) 指标收集器 /<br/>MetricsCollector: append-only metrics recording.<br/>指标收集器。MetricsCollector: append-only<br/>metrics recording.<br/>文件: feedback_loop/metrics_collector.py"]
    src_zephyr_feedback_loop_resilience_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.resilience — auto-generated<br/>package init.<br/>包入口。feedback-loop.resilience —<br/>auto-generated package init.<br/>文件: resilience/__init__.py"]
    src_zephyr_feedback_loop_scheduler_py["(生产态 / production) 调度器 / scheduler<br/>FLE 全链路调度器 ——<br/>collect->detect->diagnose->act->verify 闭环。<br/>文件: feedback_loop/scheduler.py"]
    src_zephyr_feedback_loop_security_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.security — auto-generated package<br/>init.<br/>包入口。feedback-loop.security — auto-generated<br/>package init.<br/>文件: security/__init__.py"]
    src_zephyr_feedback_loop_self_diagnosis_py["(生产态 / production) 自诊断 / self_diagnosis<br/>自我诊断<br/>文件: feedback_loop/self_diagnosis.py"]
    src_zephyr_feedback_loop_session_learner_py["(生产态 / production) 会话学习器 / session_<br/>learner<br/>在线学习<br/>文件: feedback_loop/session_learner.py"]
    src_zephyr_feedback_loop_slo_manager_py["(生产态 / production) SLO管理器 / slo_manager<br/>5.39.6: SLOManager 进程级单例（boot_hooks<br/>启动时实例化）。<br/>文件: feedback_loop/slo_manager.py"]
    src_zephyr_feedback_loop_tests_e2e_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.tests.e2e — auto-generated<br/>package init.<br/>包入口。feedback-loop.tests.e2e —<br/>auto-generated package init.<br/>文件: e2e/__init__.py"]
    src_zephyr_feedback_loop_validator_py["(生产态 / production)<br/>返回尚未生成的骨骼文件列表. / validator<br/>返回尚未生成的骨骼文件列表.<br/>文件: feedback_loop/validator.py"]
    src_zephyr_feedback_loop_verifiers_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.verifiers — auto-generated<br/>package init.<br/>包入口。feedback-loop.verifiers —<br/>auto-generated package init.<br/>文件: verifiers/__init__.py"]
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
    src_zephyr_feedback_loop_actors_agent_lifecycle_py["(生产态 / production) 代理生命周期 / Agent<br/>Lifecycle Manager — v0.12.0 R159c<br/>代理生命周期。Agent Lifecycle Manager — v0.12.0<br/>R159c<br/>文件: actors/agent_lifecycle.py"]
    src_zephyr_feedback_loop_actors_api_version_contract_py["(生产态 / production) API版本契约 / API Version<br/>Contract — v0.14.0 R188<br/>API版本契约。API Version Contract — v0.14.0 R188<br/>文件: actors/api_version_contract.py"]
    src_zephyr_feedback_loop_actors_global_action_scheduler_py["(生产态 / production) 全局动作调度器 / Global<br/>Action Scheduler — v0.16.0 R226<br/>全局动作调度器。Global Action Scheduler —<br/>v0.16.0 R226<br/>文件: actors/global_action_scheduler.py"]
    src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py["(生产态 / production)<br/>incident优先级分诊automator / Incident Priority<br/>Triage Automator — v0.37.0 R463<br/>incident优先级triageautomator，执行者的核心类，<br/>封装Severity相关逻辑。<br/>文件: actors/incident_priority_triage_<br/>automator.py"]
    src_zephyr_feedback_loop_actors_intent_driven_ops_py["(生产态 / production) intentdriven运维 /<br/>Intent-Driven Ops — v0.12.0 R159<br/>intentdriven运维。Intent-Driven Ops — v0.12.0<br/>R159<br/>文件: actors/intent_driven_ops.py"]
    src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py["(生产态 / production) 多代理编排器 /<br/>Multi-Agent Orchestrator — v0.12.0 R159b<br/>多代理编排器。Multi-Agent Orchestrator —<br/>v0.12.0 R159b<br/>文件: actors/multi_agent_orchestrator.py"]
    src_zephyr_feedback_loop_actors_notification_personalizer_py["(生产态 / production) 通知personalizer /<br/>Notification Personalizer — v0.6.0 R67<br/>通知personalizer。Notification Personalizer —<br/>v0.6.0 R67<br/>文件: actors/notification_personalizer.py"]
    src_zephyr_feedback_loop_actors_owner_absence_escalation_py["(生产态 / production) ownerabsence升级 / Owner<br/>Absence Escalation — v0.37.0 R462<br/>所有者absenceescalation。Owner Absence<br/>Escalation — v0.37.0 R462<br/>文件: actors/owner_absence_escalation.py"]
    src_zephyr_feedback_loop_actors_saga_compensator_py["(生产态 / production) Saga补偿器 / Saga<br/>Compensator — v0.3.0 R19b<br/>Saga补偿器，执行者的补偿器，对失败操作做补偿。<br/>文件: actors/saga_compensator.py"]
    src_zephyr_feedback_loop_actors_secondary_alert_channel_py["(生产态 / production) secondary告警通道 /<br/>Secondary Alert Channel — v0.37.0 R461<br/>secondary告警通道。Secondary Alert Channel —<br/>v0.37.0 R461<br/>文件: actors/secondary_alert_channel.py"]
    src_zephyr_feedback_loop_collectors_calendar_adapter_py["(生产态 / production) 日历适配器 / Calendar<br/>Adapter — v0.8.0 R102b<br/>calendar适配器。Calendar Adapter — v0.8.0 R102b<br/>文件: collectors/calendar_adapter.py"]
    src_zephyr_feedback_loop_collectors_config_timeline_py["(生产态 / production) 配置timeline / Config<br/>Timeline — v0.8.0 R99<br/>配置timeline。Config Timeline — v0.8.0 R99<br/>文件: collectors/config_timeline.py"]
    src_zephyr_feedback_loop_collectors_data_quality_validator_py["(生产态 / production) 数据质量校验器 / Data<br/>Quality Validator — v0.9.0 R110<br/>数据质量校验器。Data Quality Validator — v0.9.0<br/>R110<br/>文件: collectors/data_quality_validator.py"]
    src_zephyr_feedback_loop_collectors_financial_stratification_py["(生产态 / production) 金融分层 / Financial<br/>Stratification — v0.5.0 R50<br/>金融分层，采集器的核心类，封装FinancialStratific<br/>ation相关逻辑。<br/>文件: collectors/financial_stratification.py"]
    src_zephyr_feedback_loop_collectors_kb_provenance_py["(生产态 / production) 知识库溯源 / KB<br/>Provenance — v0.10.0 R136<br/>知识库溯源，采集器的核心类，封装KBProvenance相关<br/>逻辑。<br/>文件: collectors/kb_provenance.py"]
    src_zephyr_feedback_loop_collectors_knowledge_capture_py["(生产态 / production) 知识capture / Knowledge<br/>Capture — v0.4.0 R30<br/>知识capture。Knowledge Capture — v0.4.0 R30<br/>文件: collectors/knowledge_capture.py"]
    src_zephyr_feedback_loop_collectors_knowledge_freshness_py["(生产态 / production) 知识freshness / Knowledge<br/>Freshness — v0.5.0 R47<br/>知识freshness。Knowledge Freshness — v0.5.0 R47<br/>文件: collectors/knowledge_freshness.py"]
    src_zephyr_feedback_loop_collectors_knowledge_injection_py["(生产态 / production) 知识注入 / Knowledge<br/>Injection — v0.8.0 R102<br/>知识injection。Knowledge Injection — v0.8.0 R102<br/>文件: collectors/knowledge_injection.py"]
    src_zephyr_feedback_loop_collectors_knowledge_packaging_py["(生产态 / production) 知识packaging / Knowledge<br/>Packaging — v0.9.0 R123<br/>知识packaging。Knowledge Packaging — v0.9.0 R123<br/>文件: collectors/knowledge_packaging.py"]
    src_zephyr_feedback_loop_collectors_known_unknown_registry_py["(生产态 / production) knownunknown注册表 /<br/>Known-Unknown Registry — v0.16.0 R229<br/>knownunknown注册表。Known-Unknown Registry —<br/>v0.16.0 R229<br/>文件: collectors/known_unknown_registry.py"]
    src_zephyr_feedback_loop_collectors_llm_cost_accounting_py["(生产态 / production) LLM成本accounting / LLM<br/>Cost Accounting — v0.4.0 R35<br/>llm成本accounting。LLM Cost Accounting — v0.4.0<br/>R35<br/>文件: collectors/llm_cost_accounting.py"]
    src_zephyr_feedback_loop_collectors_market_calendar_py["(生产态 / production) 行情日历 / Market<br/>Calendar — v0.5.0 R48<br/>市场calendar。Market Calendar — v0.5.0 R48<br/>文件: collectors/market_calendar.py"]
    src_zephyr_feedback_loop_collectors_market_event_integrator_py["(生产态 / production) 行情事件integrator /<br/>Market Event Integrator — v0.14.0 R197<br/>市场事件integrator。Market Event Integrator —<br/>v0.14.0 R197<br/>文件: collectors/market_event_integrator.py"]
    src_zephyr_feedback_loop_collectors_notification_feedback_py["(生产态 / production) 通知反馈 / Notification<br/>Feedback — v0.9.0 R118<br/>通知反馈。Notification Feedback — v0.9.0 R118<br/>文件: collectors/notification_feedback.py"]
    src_zephyr_feedback_loop_collectors_schema_evolution_py["(生产态 / production) 模式进化 / Schema<br/>Evolution — v0.9.0 R111<br/>模式进化。Schema Evolution — v0.9.0 R111<br/>文件: collectors/schema_evolution.py"]
    src_zephyr_feedback_loop_collectors_schema_migration_py["(生产态 / production) 模式迁移 / Schema<br/>Migration — v0.14.0 R190<br/>模式迁移。Schema Migration — v0.14.0 R190<br/>文件: collectors/schema_migration.py"]
    src_zephyr_feedback_loop_collectors_temporal_event_store_py["(生产态 / production) temporal事件存储 /<br/>Temporal Event Store — v0.3.0 R9<br/>temporal事件存储。Temporal Event Store — v0.3.0<br/>R9<br/>文件: collectors/temporal_event_store.py"]
    src_zephyr_feedback_loop_collectors_token_finops_py["(生产态 / production) 令牌finops / Token FinOps<br/>— v0.12.0 R162<br/>令牌finops。Token FinOps — v0.12.0 R162<br/>文件: collectors/token_finops.py"]
    src_zephyr_feedback_loop_core_py["(生产态 / production) 核心 / core<br/>FeedbackLoop core — 反馈闭环核心类。<br/>文件: feedback_loop/core.py"]
    src_zephyr_feedback_loop_db_writer_py["(生产态 / production) db写入器 / db_writer<br/>FLE 持久化写入器 — 写 metrics/alerts/dispatch_<br/>log 到 SQLite<br/>文件: feedback_loop/db_writer.py"]
    src_zephyr_feedback_loop_docs_cold_start_manual_py["(生产态 / production) 冷启动手册 / cold_start_<br/>manual<br/>冷启动手册（cold_start_manual.py）<br/>文件: docs/cold_start_manual.py"]
    src_zephyr_feedback_loop_evolution_auto_reward_py["(生产态 / production) 自动奖励 / Auto Reward —<br/>v0.7.0 R76<br/>自动奖励。Auto Reward — v0.7.0 R76<br/>文件: evolution/auto_reward.py"]
    src_zephyr_feedback_loop_evolution_conformal_prediction_py["(生产态 / production) conformal预测 / Conformal<br/>Prediction — v0.7.0 R74<br/>conformal预测。Conformal Prediction — v0.7.0 R74<br/>文件: evolution/conformal_prediction.py"]
    src_zephyr_feedback_loop_evolution_cross_gen_validation_py["(生产态 / production) 跨gen验证 / Cross-Gen<br/>Validation — v0.7.0 R78<br/>跨gen验证。Cross-Gen Validation — v0.7.0 R78<br/>文件: evolution/cross_gen_validation.py"]
    src_zephyr_feedback_loop_evolution_dynamic_threshold_py["(生产态 / production) 动态阈值 / Dynamic<br/>Threshold — v0.7.0 R71<br/>动态阈值。Dynamic Threshold — v0.7.0 R71<br/>文件: evolution/dynamic_threshold.py"]
    src_zephyr_feedback_loop_evolution_ewc_kb_review_py["(生产态 / production) ewc知识库审查 / EWC KB<br/>Review — v0.6.0 R51<br/>ewckb审查。EWC KB Review — v0.6.0 R51<br/>文件: evolution/ewc_kb_review.py"]
    src_zephyr_feedback_loop_evolution_failure_replay_py["(生产态 / production) 故障replay / Failure<br/>Replay — v0.7.0 R77<br/>failure回放，进化的核心类，封装FailureReplay相关<br/>逻辑。<br/>文件: evolution/failure_replay.py"]
    src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py["(生产态 / production) graduatedactivation协议 /<br/>Graduated Activation Protocol — v0.38.0 R485<br/>graduatedactivation协议。Graduated Activation<br/>Protocol — v0.38.0 R485<br/>文件: evolution/graduated_activation_protocol.py"]
    src_zephyr_feedback_loop_evolution_hypernetwork_py["(生产态 / production) 超网络 / HyperNetwork —<br/>v0.7.0 R72<br/>超网络，进化的核心类，封装超网络相关逻辑。<br/>文件: evolution/hypernetwork.py"]
    src_zephyr_feedback_loop_evolution_knowledge_distillation_py["(生产态 / production) 知识distillation /<br/>Knowledge Distillation — v0.6.0 R52<br/>知识distillation。Knowledge Distillation —<br/>v0.6.0 R52<br/>文件: evolution/knowledge_distillation.py"]
    src_zephyr_feedback_loop_evolution_online_feature_importance_py["(生产态 / production) online特征importance /<br/>Online Feature Importance — v0.7.0 R73<br/>online功能importance。Online Feature Importance<br/>— v0.7.0 R73<br/>文件: evolution/online_feature_importance.py"]
    src_zephyr_feedback_loop_evolution_prompt_factory_governance_py["(生产态 / production) 提示工厂治理 / Prompt<br/>Factory Governance — v0.16.0 R224<br/>提示工厂治理。Prompt Factory Governance —<br/>v0.16.0 R224<br/>文件: evolution/prompt_factory_governance.py"]
    src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py["(生产态 / production) 提示优化回归检测器 /<br/>R514: PromptOptimizationRegressionDetector<br/>提示optimization回归检测器。R514:<br/>PromptOptimizationRegressionDetector<br/>文件: evolution/prompt_optimization_regression_<br/>detector.py"]
    src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py["(生产态 / production) 提示自优化循环 / R502:<br/>PromptSelfOptimizationLoop<br/>提示自optimizationloop。R502:<br/>PromptSelfOptimizationLoop<br/>文件: evolution/prompt_self_optimization_loop.py"]
    src_zephyr_feedback_loop_evolution_self_reflection_py["(生产态 / production) 自reflection / Self<br/>Reflection — v0.7.0 R75<br/>自reflection。Self Reflection — v0.7.0 R75<br/>文件: evolution/self_reflection.py"]
    src_zephyr_feedback_loop_evolution_self_upgrade_canary_py["(生产态 / production) selfupgrade金丝雀 / Self<br/>Upgrade Canary — v0.14.0 R194<br/>自upgradecanary。Self Upgrade Canary — v0.14.0<br/>R194<br/>文件: evolution/self_upgrade_canary.py"]
    src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py["(生产态 / production)<br/>semanticintentpreservation守卫 / R505:<br/>SemanticIntentPreservationGuard<br/>semanticintentpreservation守卫。R505:<br/>SemanticIntentPreservationGuard<br/>文件: evolution/semantic_intent_preservation_<br/>guard.py"]
    src_zephyr_feedback_loop_evolution_teacher_transfer_py["(生产态 / production) 教师迁移 / Teacher<br/>Transfer — v0.6.0 R53<br/>教师迁移，进化的核心类，封装TeacherTransfer相关<br/>逻辑。<br/>文件: evolution/teacher_transfer.py"]
    src_zephyr_feedback_loop_evolution_training_data_gov_py["(生产态 / production) training数据治理 /<br/>Training Data Governance — v0.14.0 R191<br/>training数据gov。Training Data Governance —<br/>v0.14.0 R191<br/>文件: evolution/training_data_gov.py"]
    src_zephyr_feedback_loop_evolution_engine_py["(生产态 / production) 进化引擎 / evolution_<br/>engine<br/>进化引擎，依赖网关工作<br/>文件: feedback_loop/evolution_engine.py"]
    src_zephyr_feedback_loop_forensic_architectural_sod_py["(生产态 / production) 架构职责分离 /<br/>Architectural SoD — v0.15.0 R205<br/>架构职责分离，取证的核心类，封装SoDRole相关逻辑<br/>。<br/>文件: forensic/architectural_sod.py"]
    src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py["(生产态 / production)<br/>automatedrcapostmortem生成器 / Automated RCA<br/>Postmortem Generator — v0.38.0 R486<br/>automatedrcapostmortem生成器。Automated RCA<br/>Postmortem Generator — v0.38.0 R486<br/>文件: forensic/automated_rca_postmortem_<br/>generator.py"]
    src_zephyr_feedback_loop_forensic_crypto_bootstrap_py["(生产态 / production) 加密自举 / Cryptographic<br/>Bootstrap — v0.15.0 R204<br/>加密自举，取证的核心类，封装HashLink相关逻辑。<br/>文件: forensic/crypto_bootstrap.py"]
    src_zephyr_feedback_loop_forensic_deterministic_replay_py["(生产态 / production) deterministic回放 /<br/>Deterministic Replay — v0.15.0 R206<br/>deterministic回放，反馈闭环的记录器，把发生的事<br/>件/结果记下来留档。<br/>文件: forensic/deterministic_replay.py"]
    src_zephyr_feedback_loop_forensic_external_verifier_py["(生产态 / production) 外部验证器 / External<br/>Verifier — v0.15.0 R203<br/>外部验证器。External Verifier — v0.15.0 R203<br/>文件: forensic/external_verifier.py"]
    src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py["(生产态 / production) fleupgrade安全校验器 /<br/>R529: FLEUpgradeSafetyValidator<br/>fleupgrade安全校验器。R529:<br/>FLEUpgradeSafetyValidator<br/>文件: forensic/fle_upgrade_safety_validator.py"]
    src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py["(生产态 / production) 守卫配置漂移监控 / R521:<br/>GuardConfigurationDriftMonitor<br/>守卫configuration漂移监控。R521:<br/>GuardConfigurationDriftMonitor<br/>文件: forensic/guard_configuration_drift_<br/>monitor.py"]
    src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py["(生产态 / production) interruptcoherence校验器<br/>/ R531: InterruptCoherenceValidator<br/>中断coherence校验器。R531:<br/>InterruptCoherenceValidator<br/>文件: forensic/interrupt_coherence_validator.py"]
    src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py["(生产态 / production) 知识注入preflight验证器 /<br/>R515: KnowledgeInjectionPreFlightVerifier<br/>知识injection预flight验证器。R515:<br/>KnowledgeInjectionPreFlightVerifier<br/>文件: forensic/knowledge_injection_pre_flight_<br/>verifier.py"]
    src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py["(生产态 / production) 点入时间reconstructor /<br/>Point-in-Time Reconstructor — v0.37.0 R465<br/>点入时间reconstructor。Point-in-Time<br/>Reconstructor — v0.37.0 R465<br/>文件: forensic/point_in_time_reconstructor.py"]
    src_zephyr_feedback_loop_forensic_self_modification_audit_py["(生产态 / production) selfmodification审计 /<br/>Self-Modification Audit — v0.15.0 R218<br/>自modification审计。Self-Modification Audit —<br/>v0.15.0 R218<br/>文件: forensic/self_modification_audit.py"]
    src_zephyr_feedback_loop_forensic_serialization_format_tracker_py["(生产态 / production) serializationformat追踪器<br/>/ Serialization Format Tracker — v0.39.0 R488<br/>serializationformat追踪器。Serialization Format<br/>Tracker — v0.39.0 R488<br/>文件: forensic/serialization_format_tracker.py"]
    src_zephyr_feedback_loop_forensic_state_migration_validator_py["(生产态 / production) 状态迁移校验器 / State<br/>Migration Validator — v0.40.0 R497<br/>状态迁移校验器。State Migration Validator —<br/>v0.40.0 R497<br/>文件: forensic/state_migration_validator.py"]
    src_zephyr_feedback_loop_forensic_sub_agent_collusion_py["(生产态 / production) sub代理collusion /<br/>Sub-Agent Collusion Detector — v0.15.0 R213<br/>子代理collusion。Sub-Agent Collusion Detector —<br/>v0.15.0 R213<br/>文件: forensic/sub_agent_collusion.py"]
    src_zephyr_feedback_loop_forensic_toctou_guard_py["(生产态 / production) TOCTOU守卫 / TOCTOU Guard<br/>— v0.15.0 R207<br/>toctou守卫。TOCTOU Guard — v0.15.0 R207<br/>文件: forensic/toctou_guard.py"]
    src_zephyr_feedback_loop_forensic_worm_write_integrity_py["(生产态 / production) wormwrite完整性 / WORM<br/>Write Integrity — v0.15.0 R216<br/>wormwrite完整性。WORM Write Integrity — v0.15.0<br/>R216<br/>文件: forensic/worm_write_integrity.py"]
    src_zephyr_feedback_loop_resilience_deadman_switch_py["(生产态 / production) deadman开关 / Deadman<br/>Switch — v0.15.0 R212<br/>deadman开关。Deadman Switch — v0.15.0 R212<br/>文件: resilience/deadman_switch.py"]
    src_zephyr_feedback_loop_resilience_dr_automation_py["(生产态 / production) 灾备自动化 / DR<br/>Automation — v0.14.0 R187<br/>灾备自动化，韧性的结果，封装操作结果的数据结构。<br/>文件: resilience/dr_automation.py"]
    src_zephyr_feedback_loop_resilience_multi_instance_coord_py["(生产态 / production) 多instancecoord /<br/>Multi-Instance Coordinator — v0.14.0 R199<br/>多instancecoord。Multi-Instance Coordinator —<br/>v0.14.0 R199<br/>文件: resilience/multi_instance_coord.py"]
    src_zephyr_feedback_loop_resilience_resource_starvation_aware_py["(生产态 / production) 资源starvation感知 /<br/>Resource Starvation Aware — v0.15.0 R209<br/>resourcestarvation感知，韧性的核心类，封装Resour<br/>ceBudget相关逻辑。<br/>文件: resilience/resource_starvation_aware.py"]
    src_zephyr_feedback_loop_resilience_split_brain_quorum_py["(生产态 / production) 拆分brainquorum /<br/>Split-Brain Quorum — v0.37.0 R451<br/>拆分brainquorum。Split-Brain Quorum — v0.37.0<br/>R451<br/>文件: resilience/split_brain_quorum.py"]
    src_zephyr_feedback_loop_scheduler_act_py["(生产态 / production) 调度器act / scheduler_act<br/>调度器act，反馈闭环的结果，封装操作结果的数据结<br/>构。<br/>文件: feedback_loop/scheduler_act.py"]
    src_zephyr_feedback_loop_scheduler_collect_detect_py["(生产态 / production) 调度器collectdetect /<br/>scheduler_collect_detect<br/>调度器collect检测，主要提供运行collect、运行检测<br/>、运行diagnose等功能，供调度器使用<br/>文件: feedback_loop/scheduler_collect_detect.py"]
    src_zephyr_feedback_loop_scheduler_health_py["(生产态 / production) 调度器健康 / scheduler_<br/>health<br/>调度器健康，主要提供报告等功能，供调度器使用<br/>文件: feedback_loop/scheduler_health.py"]
    src_zephyr_feedback_loop_scheduler_safety_py["(生产态 / production) 调度器安全 / scheduler_<br/>safety<br/>调度器安全，主要提供运行安全门禁、fle门禁缓存、f<br/>le门禁缓存等功能，供调度器使用<br/>文件: feedback_loop/scheduler_safety.py"]
    src_zephyr_feedback_loop_security_agent_skill_guard_py["(生产态 / production) 代理技能守卫 / Agent<br/>Skill Guard — v0.14.0 R201<br/>代理技能守卫。Agent Skill Guard — v0.14.0 R201<br/>文件: security/agent_skill_guard.py"]
    src_zephyr_feedback_loop_security_dep_cve_correlator_py["(生产态 / production) 依赖CVE关联器 /<br/>Dependency CVE Correlator — v0.14.0 R196<br/>依赖CVE关联器，安全的关联器，关联匹配相关数据。<br/>文件: security/dep_cve_correlator.py"]
    src_zephyr_feedback_loop_security_metric_prompt_scanner_py["(生产态 / production) 指标提示扫描器 /<br/>Metric-Prompt Scanner — v0.15.0 R215<br/>指标提示扫描器。Metric-Prompt Scanner — v0.15.0<br/>R215<br/>文件: security/metric_prompt_scanner.py"]
    src_zephyr_feedback_loop_security_remote_attestation_py["(生产态 / production) 远程attestation / Remote<br/>Attestation — v0.15.0 R211<br/>远程attestation。Remote Attestation — v0.15.0<br/>R211<br/>文件: security/remote_attestation.py"]
    src_zephyr_feedback_loop_security_secret_rotation_py["(生产态 / production) 密钥rotation / Secret<br/>Rotation — v0.14.0 R189<br/>密钥rotation。Secret Rotation — v0.14.0 R189<br/>文件: security/secret_rotation.py"]
    src_zephyr_feedback_loop_template_py["(生产态 / production) 模板 / template<br/>模板，供blueprint.md §0; zephyr.feedba使用<br/>文件: feedback_loop/template.py"]
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py["(生产态 / production) 集成测试管线 / E2E<br/>Integration Test Pipeline — TASK-MOD-FEEDBACK_<br/>LOOP-0028<br/>集成测试管线。E2E Integration Test Pipeline —<br/>TASK-MOD-FEEDBACK_LOOP-0028 (Phase43-87)<br/>文件: e2e/integration_test_pipeline.py"]
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
    src_zephyr_feedback_loop_actors_action_selector_py["(生产态 / production) 动作选择器 / action_<br/>selector<br/>动作选择器，反馈闭环的记录器，把发生的事件<br/>/结果记下来留档。<br/>文件: actors/action_selector.py"]
    src_zephyr_feedback_loop_alert_dispatcher_py["(生产态 / production) alert分发器 / alert_<br/>dispatcher<br/>FLE->Orc 告警分派器 — dispatch() 生产者<br/>文件: feedback_loop/alert_dispatcher.py"]
    src_zephyr_feedback_loop_collectors_feedback_collector_py["(生产态 / production) 反馈收集器 / feedback_<br/>collector<br/>反馈收集器，反馈闭环的数据库，持久化存取结构化数<br/>据。<br/>文件: collectors/feedback_collector.py"]
    src_zephyr_feedback_loop_collectors_metrics_collector_py["(生产态 / production) 指标收集器 / metrics_<br/>collector<br/>指标收集器，反馈闭环的核心类，封装MetricSnapshot<br/>相关逻辑。<br/>文件: collectors/metrics_collector.py"]
    src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py["(生产态 / production)<br/>selfmodification速率限制器 / R522:<br/>SelfModificationRateLimiter<br/>自modification率限制器。R522:<br/>SelfModificationRateLimiter<br/>文件: evolution/self_modification_rate_<br/>limiter.py"]
    src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py["(生产态 / production) boot完整性attestation /<br/>Boot Integrity Attestation — v0.38.0 R487<br/>启动完整性attestation。Boot Integrity<br/>Attestation — v0.38.0 R487<br/>文件: forensic/boot_integrity_attestation.py"]
    src_zephyr_feedback_loop_forensic_guard_complexity_budget_py["(生产态 / production) 守卫complexity预算 /<br/>R523: GuardComplexityBudget<br/>守卫complexity预算。R523: GuardComplexityBudget<br/>文件: forensic/guard_complexity_budget.py"]
    src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py["(生产态 / production) 配置hotreload守卫 /<br/>Config Hot-Reload Guard — v0.40.0 R498<br/>配置hotreload守卫。Config Hot-Reload Guard —<br/>v0.40.0 R498<br/>文件: resilience/config_hot_reload_guard.py"]
    src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py["(生产态 / production) gracefuldegradation规划器<br/>/ Graceful Degradation Planner — v0.40.0 R496<br/>graceful退化planner。Graceful Degradation<br/>Planner — v0.40.0 R496<br/>文件: resilience/graceful_degradation_planner.py"]
    src_zephyr_feedback_loop_resilience_oscillation_damping_py["(生产态 / production) 振荡阻尼 / Oscillation<br/>Damping — v0.37.0 R450<br/>振荡阻尼，韧性的状态机，管理状态流转。<br/>文件: resilience/oscillation_damping.py"]
    src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py["(生产态 / production) 自API限流器防御 / Self<br/>API Throttle Defense — v0.39.0 R491<br/>自APIthrottle防御。Self API Throttle Defense —<br/>v0.39.0 R491<br/>文件: resilience/self_api_throttle_defense.py"]
    src_zephyr_feedback_loop_security_wireheading_prevention_py["(生产态 / production) 神经劫持防护 /<br/>Wireheading Prevention — v0.37.0 R486<br/>神经劫持防护，安全的状态机，管理状态流转。<br/>文件: security/wireheading_prevention.py"]
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
    src_zephyr_feedback_loop_actors_alert_router_py["(生产态 / production) 告警路由器 / alert_<br/>router.py — Severity-based alert channel router.<br/>告警路由器，执行者的路由器，按规则分发请求到处理<br/>方。<br/>文件: actors/alert_router.py"]
    src_zephyr_feedback_loop_protocols_py["(生产态 / production) 协议 / protocols<br/>协议，反馈闭环的类型，定义数据类型和枚举。<br/>文件: feedback_loop/protocols.py"]
    src_zephyr_feedback_loop_actors_alert_router_py ~~~ src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_backpressure_bridge_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_auto_evolution_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_alert_dispatcher_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_alert_router_py
    src_zephyr_feedback_loop_decision_engine_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_db_writer_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_alert_dispatcher_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_alert_dispatcher_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_db_writer_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_health_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_collect_detect_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_safety_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_act_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_generator_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_template_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_complexity_budget_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_scheduler_collect_detect_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_scheduler_collect_detect_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_wireheading_prevention_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_oscillation_damping_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_core_py
    src_zephyr_feedback_loop_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_validator_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_template_py
    src_zephyr_feedback_loop_actors_action_selector_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_agent_lifecycle_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_alert_router_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_api_version_contract_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_owner_absence_escalation_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_intent_driven_ops_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_secondary_alert_channel_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_global_action_scheduler_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_saga_compensator_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_notification_personalizer_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_config_timeline_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_calendar_adapter_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_data_quality_validator_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_kb_provenance_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_packaging_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_injection_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_financial_stratification_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_capture_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_freshness_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_known_unknown_registry_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_llm_cost_accounting_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_market_event_integrator_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_schema_evolution_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_notification_feedback_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_market_calendar_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_schema_migration_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_temporal_event_store_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_token_finops_py
    src_zephyr_feedback_loop_docs_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_docs_cold_start_manual_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_cross_gen_validation_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_conformal_prediction_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_dynamic_threshold_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_auto_reward_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_hypernetwork_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_online_feature_importance_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_factory_governance_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_failure_replay_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_ewc_kb_review_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_upgrade_canary_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_knowledge_distillation_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_teacher_transfer_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_training_data_gov_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_reflection_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_deterministic_replay_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_architectural_sod_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_crypto_bootstrap_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_external_verifier_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_self_modification_audit_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_complexity_budget_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_serialization_format_tracker_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_state_migration_validator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_toctou_guard_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_worm_write_integrity_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_sub_agent_collusion_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_deadman_switch_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_oscillation_damping_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_resource_starvation_aware_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_split_brain_quorum_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_dr_automation_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_multi_instance_coord_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_agent_skill_guard_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_dep_cve_correlator_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_metric_prompt_scanner_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_secret_rotation_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_remote_attestation_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_wireheading_prevention_py
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_tests_e2e_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py
    D_SHARED["(生产态 / production) 共享服务 / Shared Services<br/>共享服务，负责跨域共享的工具、协议和基础服务<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_metrics_collector_py -->|导入依赖 / import_depends| D_SHARED
    D_FBL_DIAGNOSERS["(生产态 / production) 反馈诊断器 / Feedback<br/>Diagnosers<br/>反馈诊断器，负责异常根因诊断、模型健康监控、可靠<br/>性诊断和上下文窗口压力管理<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_scheduler_collect_detect_py -->|导入依赖 / import_depends| D_FBL_DIAGNOSERS
    D_FBL_VERIFICATION["(生产态 / production) 反馈验证 / Feedback<br/>Verification<br/>反馈验证，负责反馈循环门禁拦截、结果验证器执行和<br/>反馈质量检查<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    D_INFRA_RUNTIME["(生产态 / production) 运行时集成 / Runtime<br/>Integration<br/>运行时集成，负责组件生命周期编排、启动钩子和运行<br/>时上下文管理<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_feedback_loop_gates_init_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    D_GOVERNANCE["(生产态 / production) 生命周期管理 / Lifecycle<br/>Management<br/>生命周期管理，负责蓝图/模块<br/>/任务的声明周期管理和元数据治理<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_metrics_collector_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_feedback_loop_verifiers_init_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    src_zephyr_feedback_loop_verifiers_init_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    src_zephyr_feedback_loop_db_writer_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    D_GOV_DRIFT["(生产态 / production) 漂移检测 / Drift Detection<br/>漂移检测，负责架构漂移检测和漂移告警<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_GOV_DRIFT
    src_zephyr_feedback_loop_slo_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_feedback_loop_verifiers_init_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    src_zephyr_feedback_loop_gates_init_py -->|导入依赖 / import_depends| D_FBL_VERIFICATION
    D_INFRA_RECOVERY["(生产态 / production) 回滚恢复 / Rollback<br/>Recovery<br/>回滚恢复，负责系统故障时的状态回滚、事务补偿和恢<br/>复编排<br/>跨域节点 / cross-domain"]
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| D_INFRA_RECOVERY
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_feedback_loop_init_py
    D_SHARED -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_secret_rotation_py
    D_FRONTEND["(生产态 / production) 前端 / Frontend<br/>前端，负责用户界面展示、交互可视化和前端状态管理<br/>跨域节点 / cross-domain"]
    D_FRONTEND -->|导入依赖 / import_depends| src_zephyr_feedback_loop_fitness_functions_py
    D_FBL_DETECTORS["(生产态 / production) 反馈检测器 / Feedback<br/>Detectors<br/>反馈检测器，负责异常检测、漂移检测、反馈信号检测<br/>和可靠性监控<br/>跨域节点 / cross-domain"]
    D_FBL_DETECTORS -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    D_AUTONOMY_CORE["(生产态 / production) 自治核心 / Autonomy Core<br/>自治核心，负责 AI 自治决策、目标分解和执行编排<br/>跨域节点 / cross-domain"]
    D_AUTONOMY_CORE -->|测试依赖 / test_depends| src_zephyr_feedback_loop_scheduler_py
    D_FBL_DETECTORS -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_feedback_loop_init_py
    D_ORCHESTRATOR["(生产态 / production) 代理编排器 / Agent<br/>Orchestrator<br/>代理编排器，负责 Agent<br/>任务全生命周期：任务入队、调度、沙箱执行、幻觉检<br/>测和收尾归档<br/>跨域节点 / cross-domain"]
    D_ORCHESTRATOR -->|导入依赖 / import_depends| src_zephyr_feedback_loop_decision_engine_py
    D_SECURITY["(生产态 / production) 对抗验证 / Adversarial<br/>Validation<br/>对抗验证，负责系统安全对抗测试、漏洞扫描和攻防验<br/>证<br/>跨域节点 / cross-domain"]
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_feedback_loop_init_py
    D_GOV_AUDIT["(生产态 / production) 审计追踪 / Audit Trail<br/>审计追踪，负责变更审计追踪和操作日志管理<br/>跨域节点 / cross-domain"]
    D_GOV_AUDIT -->|导入依赖 / import_depends| src_zephyr_feedback_loop_init_py
    D_AUTONOMY_CORE -->|测试依赖 / test_depends| src_zephyr_feedback_loop_error_budget_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_py
    D_FBL_DETECTORS -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_init_py,src_zephyr_feedback_loop_gen_inherited_py,src_zephyr_feedback_loop_actors_init_py,src_zephyr_feedback_loop_actors_action_selector_py,src_zephyr_feedback_loop_actors_agent_lifecycle_py,src_zephyr_feedback_loop_actors_alert_router_py,src_zephyr_feedback_loop_actors_api_version_contract_py,src_zephyr_feedback_loop_actors_global_action_scheduler_py,src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py,src_zephyr_feedback_loop_actors_intent_driven_ops_py,src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py,src_zephyr_feedback_loop_actors_notification_personalizer_py,src_zephyr_feedback_loop_actors_owner_absence_escalation_py,src_zephyr_feedback_loop_actors_saga_compensator_py,src_zephyr_feedback_loop_actors_secondary_alert_channel_py,src_zephyr_feedback_loop_alert_dispatcher_py,src_zephyr_feedback_loop_auto_evolution_py,src_zephyr_feedback_loop_backpressure_bridge_py,src_zephyr_feedback_loop_collectors_init_py,src_zephyr_feedback_loop_collectors_calendar_adapter_py,src_zephyr_feedback_loop_collectors_config_timeline_py,src_zephyr_feedback_loop_collectors_data_quality_validator_py,src_zephyr_feedback_loop_collectors_feedback_collector_py,src_zephyr_feedback_loop_collectors_financial_stratification_py,src_zephyr_feedback_loop_collectors_kb_provenance_py,src_zephyr_feedback_loop_collectors_knowledge_capture_py,src_zephyr_feedback_loop_collectors_knowledge_freshness_py,src_zephyr_feedback_loop_collectors_knowledge_injection_py,src_zephyr_feedback_loop_collectors_knowledge_packaging_py,src_zephyr_feedback_loop_collectors_known_unknown_registry_py,src_zephyr_feedback_loop_collectors_llm_cost_accounting_py,src_zephyr_feedback_loop_collectors_market_calendar_py,src_zephyr_feedback_loop_collectors_market_event_integrator_py,src_zephyr_feedback_loop_collectors_metrics_collector_py,src_zephyr_feedback_loop_collectors_notification_feedback_py,src_zephyr_feedback_loop_collectors_schema_evolution_py,src_zephyr_feedback_loop_collectors_schema_migration_py,src_zephyr_feedback_loop_collectors_temporal_event_store_py,src_zephyr_feedback_loop_collectors_token_finops_py,src_zephyr_feedback_loop_config_py,src_zephyr_feedback_loop_core_py,src_zephyr_feedback_loop_db_bridge_py,src_zephyr_feedback_loop_db_writer_py,src_zephyr_feedback_loop_decision_engine_py,src_zephyr_feedback_loop_docs_init_py,src_zephyr_feedback_loop_docs_cold_start_manual_py,src_zephyr_feedback_loop_error_budget_py,src_zephyr_feedback_loop_eval_harness_py,src_zephyr_feedback_loop_evolution_init_py,src_zephyr_feedback_loop_evolution_auto_reward_py,src_zephyr_feedback_loop_evolution_conformal_prediction_py,src_zephyr_feedback_loop_evolution_cross_gen_validation_py,src_zephyr_feedback_loop_evolution_dynamic_threshold_py,src_zephyr_feedback_loop_evolution_ewc_kb_review_py,src_zephyr_feedback_loop_evolution_failure_replay_py,src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py,src_zephyr_feedback_loop_evolution_hypernetwork_py,src_zephyr_feedback_loop_evolution_knowledge_distillation_py,src_zephyr_feedback_loop_evolution_online_feature_importance_py,src_zephyr_feedback_loop_evolution_prompt_factory_governance_py,src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py,src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py,src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py,src_zephyr_feedback_loop_evolution_self_reflection_py,src_zephyr_feedback_loop_evolution_self_upgrade_canary_py,src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py,src_zephyr_feedback_loop_evolution_teacher_transfer_py,src_zephyr_feedback_loop_evolution_training_data_gov_py,src_zephyr_feedback_loop_evolution_engine_py,src_zephyr_feedback_loop_exceptions_py,src_zephyr_feedback_loop_feedback_collector_py,src_zephyr_feedback_loop_fitness_functions_py,src_zephyr_feedback_loop_forensic_init_py,src_zephyr_feedback_loop_forensic_architectural_sod_py,src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py,src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py,src_zephyr_feedback_loop_forensic_crypto_bootstrap_py,src_zephyr_feedback_loop_forensic_deterministic_replay_py,src_zephyr_feedback_loop_forensic_external_verifier_py,src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py,src_zephyr_feedback_loop_forensic_guard_complexity_budget_py,src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py,src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py,src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py,src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py,src_zephyr_feedback_loop_forensic_self_modification_audit_py,src_zephyr_feedback_loop_forensic_serialization_format_tracker_py,src_zephyr_feedback_loop_forensic_state_migration_validator_py,src_zephyr_feedback_loop_forensic_sub_agent_collusion_py,src_zephyr_feedback_loop_forensic_toctou_guard_py,src_zephyr_feedback_loop_forensic_worm_write_integrity_py,src_zephyr_feedback_loop_gates_init_py,src_zephyr_feedback_loop_generator_py,src_zephyr_feedback_loop_metrics_collector_py,src_zephyr_feedback_loop_protocols_py,src_zephyr_feedback_loop_resilience_init_py,src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py,src_zephyr_feedback_loop_resilience_deadman_switch_py,src_zephyr_feedback_loop_resilience_dr_automation_py,src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py,src_zephyr_feedback_loop_resilience_multi_instance_coord_py,src_zephyr_feedback_loop_resilience_oscillation_damping_py,src_zephyr_feedback_loop_resilience_resource_starvation_aware_py,src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py,src_zephyr_feedback_loop_resilience_split_brain_quorum_py,src_zephyr_feedback_loop_scheduler_py,src_zephyr_feedback_loop_scheduler_act_py,src_zephyr_feedback_loop_scheduler_collect_detect_py,src_zephyr_feedback_loop_scheduler_health_py,src_zephyr_feedback_loop_scheduler_safety_py,src_zephyr_feedback_loop_security_init_py,src_zephyr_feedback_loop_security_agent_skill_guard_py,src_zephyr_feedback_loop_security_dep_cve_correlator_py,src_zephyr_feedback_loop_security_metric_prompt_scanner_py,src_zephyr_feedback_loop_security_remote_attestation_py,src_zephyr_feedback_loop_security_secret_rotation_py,src_zephyr_feedback_loop_security_wireheading_prevention_py,src_zephyr_feedback_loop_self_diagnosis_py,src_zephyr_feedback_loop_session_learner_py,src_zephyr_feedback_loop_slo_manager_py,src_zephyr_feedback_loop_template_py,src_zephyr_feedback_loop_tests_e2e_init_py,src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py,src_zephyr_feedback_loop_validator_py,src_zephyr_feedback_loop_verifiers_init_py production
    class D_SHARED,D_FBL_DIAGNOSERS,D_FBL_VERIFICATION,D_INFRA_RUNTIME,D_GOVERNANCE,D_GOV_DRIFT,D_INFRA_RECOVERY,D_FRONTEND,D_FBL_DETECTORS,D_AUTONOMY_CORE,D_ORCHESTRATOR,D_SECURITY,D_GOV_AUDIT external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 125 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_feedback_loop_init_py["(生产态 / production) 包入口 / Feedback Loop<br/>Engine — MOD-FEEDBACK_LOOP.<br/>包入口。Feedback Loop Engine — MOD-FEEDBACK_<br/>LOOP.<br/>文件: feedback_loop/__init__.py"]
    src_zephyr_feedback_loop_gen_inherited_py["(生产态 / production) 生成inherited / _gen_<br/>inherited<br/>生成inherited，提供包入口和模块加载功能<br/>文件: feedback_loop/_gen_inherited.py"]
    src_zephyr_feedback_loop_actors_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.actors — auto-generated package<br/>init.<br/>包入口。feedback-loop.actors — auto-generated<br/>package init.<br/>文件: actors/__init__.py"]
    src_zephyr_feedback_loop_auto_evolution_py["(生产态 / production) 自动进化 / auto_evolution<br/>自动进化，反馈闭环的核心调度模块，整合包入口、告<br/>警管理器、告警precision追踪器、双通道告警等21个<br/>子模块协同工作。<br/>文件: feedback_loop/auto_evolution.py"]
    src_zephyr_feedback_loop_backpressure_bridge_py["(生产态 / production) 背压桥接 / backpressure_<br/>bridge<br/>FLE -> Pipeline 背压桥接（CTR-BP-001~003）<br/>文件: feedback_loop/backpressure_bridge.py"]
    src_zephyr_feedback_loop_collectors_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.collectors — auto-generated<br/>package init.<br/>包入口。feedback-loop.collectors —<br/>auto-generated package init.<br/>文件: collectors/__init__.py"]
    src_zephyr_feedback_loop_config_py["(生产态 / production) 配置 / config<br/>配置，反馈闭环的配置，管理配置项的读取和校验。<br/>文件: feedback_loop/config.py"]
    src_zephyr_feedback_loop_db_bridge_py["(生产态 / production) 数据库桥接 / db_bridge<br/>FLE DB契约适配器 —<br/>通过规范zephyr.governance.sqlite_<br/>schema连接写入fle_metrics<br/>文件: feedback_loop/db_bridge.py"]
    src_zephyr_feedback_loop_decision_engine_py["(生产态 / production) 决策引擎 / Feedback Loop<br/>Decision Engine<br/>决策引擎。Feedback Loop Decision Engine<br/>文件: feedback_loop/decision_engine.py"]
    src_zephyr_feedback_loop_docs_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.docs — auto-generated package<br/>init.<br/>包入口。feedback-loop.docs — auto-generated<br/>package init.<br/>文件: docs/__init__.py"]
    src_zephyr_feedback_loop_error_budget_py["(生产态 / production) 错误预算 / error_budget<br/>Error Budget 状态机——monthly budget + burn_rate<br/>+ exhaust_policy。<br/>文件: feedback_loop/error_budget.py"]
    src_zephyr_feedback_loop_eval_harness_py["(生产态 / production) 评估harness / eval_harness<br/>评估harness，提供包入口和模块加载功能<br/>文件: feedback_loop/eval_harness.py"]
    src_zephyr_feedback_loop_evolution_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.evolution — auto-generated<br/>package init.<br/>包入口。feedback-loop.evolution —<br/>auto-generated package init.<br/>文件: evolution/__init__.py"]
    src_zephyr_feedback_loop_exceptions_py["(生产态 / production) 异常 / exceptions<br/>异常，提供包入口和模块加载功能<br/>文件: feedback_loop/exceptions.py"]
    src_zephyr_feedback_loop_feedback_collector_py["(生产态 / production) 反馈收集器 /<br/>FeedbackCollector: collect task execution<br/>feedback<br/>反馈收集器。FeedbackCollector: collect task<br/>execution feedback<br/>文件: feedback_loop/feedback_collector.py"]
    src_zephyr_feedback_loop_fitness_functions_py["(生产态 / production) 适应度functions / fitness_<br/>functions<br/>适应度functions，提供包入口和模块加载功能<br/>文件: feedback_loop/fitness_functions.py"]
    src_zephyr_feedback_loop_forensic_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.forensic — auto-generated package<br/>init.<br/>包入口。feedback-loop.forensic — auto-generated<br/>package init.<br/>文件: forensic/__init__.py"]
    src_zephyr_feedback_loop_gates_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.gates — auto-generated package<br/>init.<br/>包入口。feedback-loop.gates — auto-generated<br/>package init.<br/>文件: gates/__init__.py"]
    src_zephyr_feedback_loop_generator_py["(生产态 / production) 生成器 / generator<br/>执行骨骼代码生成. 返回 (created, skipped,<br/>errors).<br/>文件: feedback_loop/generator.py"]
    src_zephyr_feedback_loop_metrics_collector_py["(生产态 / production) 指标收集器 /<br/>MetricsCollector: append-only metrics recording.<br/>指标收集器。MetricsCollector: append-only<br/>metrics recording.<br/>文件: feedback_loop/metrics_collector.py"]
    src_zephyr_feedback_loop_resilience_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.resilience — auto-generated<br/>package init.<br/>包入口。feedback-loop.resilience —<br/>auto-generated package init.<br/>文件: resilience/__init__.py"]
    src_zephyr_feedback_loop_scheduler_py["(生产态 / production) 调度器 / scheduler<br/>FLE 全链路调度器 ——<br/>collect->detect->diagnose->act->verify 闭环。<br/>文件: feedback_loop/scheduler.py"]
    src_zephyr_feedback_loop_security_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.security — auto-generated package<br/>init.<br/>包入口。feedback-loop.security — auto-generated<br/>package init.<br/>文件: security/__init__.py"]
    src_zephyr_feedback_loop_self_diagnosis_py["(生产态 / production) 自诊断 / self_diagnosis<br/>自我诊断<br/>文件: feedback_loop/self_diagnosis.py"]
    src_zephyr_feedback_loop_session_learner_py["(生产态 / production) 会话学习器 / session_<br/>learner<br/>在线学习<br/>文件: feedback_loop/session_learner.py"]
    src_zephyr_feedback_loop_slo_manager_py["(生产态 / production) SLO管理器 / slo_manager<br/>5.39.6: SLOManager 进程级单例（boot_hooks<br/>启动时实例化）。<br/>文件: feedback_loop/slo_manager.py"]
    src_zephyr_feedback_loop_tests_e2e_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.tests.e2e — auto-generated<br/>package init.<br/>包入口。feedback-loop.tests.e2e —<br/>auto-generated package init.<br/>文件: e2e/__init__.py"]
    src_zephyr_feedback_loop_validator_py["(生产态 / production)<br/>返回尚未生成的骨骼文件列表. / validator<br/>返回尚未生成的骨骼文件列表.<br/>文件: feedback_loop/validator.py"]
    src_zephyr_feedback_loop_verifiers_init_py["(生产态 / production) 包入口 /<br/>feedback-loop.verifiers — auto-generated<br/>package init.<br/>包入口。feedback-loop.verifiers —<br/>auto-generated package init.<br/>文件: verifiers/__init__.py"]
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
    src_zephyr_feedback_loop_actors_agent_lifecycle_py["(生产态 / production) 代理生命周期 / Agent<br/>Lifecycle Manager — v0.12.0 R159c<br/>代理生命周期。Agent Lifecycle Manager — v0.12.0<br/>R159c<br/>文件: actors/agent_lifecycle.py"]
    src_zephyr_feedback_loop_actors_api_version_contract_py["(生产态 / production) API版本契约 / API Version<br/>Contract — v0.14.0 R188<br/>API版本契约。API Version Contract — v0.14.0 R188<br/>文件: actors/api_version_contract.py"]
    src_zephyr_feedback_loop_actors_global_action_scheduler_py["(生产态 / production) 全局动作调度器 / Global<br/>Action Scheduler — v0.16.0 R226<br/>全局动作调度器。Global Action Scheduler —<br/>v0.16.0 R226<br/>文件: actors/global_action_scheduler.py"]
    src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py["(生产态 / production)<br/>incident优先级分诊automator / Incident Priority<br/>Triage Automator — v0.37.0 R463<br/>incident优先级triageautomator，执行者的核心类，<br/>封装Severity相关逻辑。<br/>文件: actors/incident_priority_triage_<br/>automator.py"]
    src_zephyr_feedback_loop_actors_intent_driven_ops_py["(生产态 / production) intentdriven运维 /<br/>Intent-Driven Ops — v0.12.0 R159<br/>intentdriven运维。Intent-Driven Ops — v0.12.0<br/>R159<br/>文件: actors/intent_driven_ops.py"]
    src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py["(生产态 / production) 多代理编排器 /<br/>Multi-Agent Orchestrator — v0.12.0 R159b<br/>多代理编排器。Multi-Agent Orchestrator —<br/>v0.12.0 R159b<br/>文件: actors/multi_agent_orchestrator.py"]
    src_zephyr_feedback_loop_actors_notification_personalizer_py["(生产态 / production) 通知personalizer /<br/>Notification Personalizer — v0.6.0 R67<br/>通知personalizer。Notification Personalizer —<br/>v0.6.0 R67<br/>文件: actors/notification_personalizer.py"]
    src_zephyr_feedback_loop_actors_owner_absence_escalation_py["(生产态 / production) ownerabsence升级 / Owner<br/>Absence Escalation — v0.37.0 R462<br/>所有者absenceescalation。Owner Absence<br/>Escalation — v0.37.0 R462<br/>文件: actors/owner_absence_escalation.py"]
    src_zephyr_feedback_loop_actors_saga_compensator_py["(生产态 / production) Saga补偿器 / Saga<br/>Compensator — v0.3.0 R19b<br/>Saga补偿器，执行者的补偿器，对失败操作做补偿。<br/>文件: actors/saga_compensator.py"]
    src_zephyr_feedback_loop_actors_secondary_alert_channel_py["(生产态 / production) secondary告警通道 /<br/>Secondary Alert Channel — v0.37.0 R461<br/>secondary告警通道。Secondary Alert Channel —<br/>v0.37.0 R461<br/>文件: actors/secondary_alert_channel.py"]
    src_zephyr_feedback_loop_collectors_calendar_adapter_py["(生产态 / production) 日历适配器 / Calendar<br/>Adapter — v0.8.0 R102b<br/>calendar适配器。Calendar Adapter — v0.8.0 R102b<br/>文件: collectors/calendar_adapter.py"]
    src_zephyr_feedback_loop_collectors_config_timeline_py["(生产态 / production) 配置timeline / Config<br/>Timeline — v0.8.0 R99<br/>配置timeline。Config Timeline — v0.8.0 R99<br/>文件: collectors/config_timeline.py"]
    src_zephyr_feedback_loop_collectors_data_quality_validator_py["(生产态 / production) 数据质量校验器 / Data<br/>Quality Validator — v0.9.0 R110<br/>数据质量校验器。Data Quality Validator — v0.9.0<br/>R110<br/>文件: collectors/data_quality_validator.py"]
    src_zephyr_feedback_loop_collectors_financial_stratification_py["(生产态 / production) 金融分层 / Financial<br/>Stratification — v0.5.0 R50<br/>金融分层，采集器的核心类，封装FinancialStratific<br/>ation相关逻辑。<br/>文件: collectors/financial_stratification.py"]
    src_zephyr_feedback_loop_collectors_kb_provenance_py["(生产态 / production) 知识库溯源 / KB<br/>Provenance — v0.10.0 R136<br/>知识库溯源，采集器的核心类，封装KBProvenance相关<br/>逻辑。<br/>文件: collectors/kb_provenance.py"]
    src_zephyr_feedback_loop_collectors_knowledge_capture_py["(生产态 / production) 知识capture / Knowledge<br/>Capture — v0.4.0 R30<br/>知识capture。Knowledge Capture — v0.4.0 R30<br/>文件: collectors/knowledge_capture.py"]
    src_zephyr_feedback_loop_collectors_knowledge_freshness_py["(生产态 / production) 知识freshness / Knowledge<br/>Freshness — v0.5.0 R47<br/>知识freshness。Knowledge Freshness — v0.5.0 R47<br/>文件: collectors/knowledge_freshness.py"]
    src_zephyr_feedback_loop_collectors_knowledge_injection_py["(生产态 / production) 知识注入 / Knowledge<br/>Injection — v0.8.0 R102<br/>知识injection。Knowledge Injection — v0.8.0 R102<br/>文件: collectors/knowledge_injection.py"]
    src_zephyr_feedback_loop_collectors_knowledge_packaging_py["(生产态 / production) 知识packaging / Knowledge<br/>Packaging — v0.9.0 R123<br/>知识packaging。Knowledge Packaging — v0.9.0 R123<br/>文件: collectors/knowledge_packaging.py"]
    src_zephyr_feedback_loop_collectors_known_unknown_registry_py["(生产态 / production) knownunknown注册表 /<br/>Known-Unknown Registry — v0.16.0 R229<br/>knownunknown注册表。Known-Unknown Registry —<br/>v0.16.0 R229<br/>文件: collectors/known_unknown_registry.py"]
    src_zephyr_feedback_loop_collectors_llm_cost_accounting_py["(生产态 / production) LLM成本accounting / LLM<br/>Cost Accounting — v0.4.0 R35<br/>llm成本accounting。LLM Cost Accounting — v0.4.0<br/>R35<br/>文件: collectors/llm_cost_accounting.py"]
    src_zephyr_feedback_loop_collectors_market_calendar_py["(生产态 / production) 行情日历 / Market<br/>Calendar — v0.5.0 R48<br/>市场calendar。Market Calendar — v0.5.0 R48<br/>文件: collectors/market_calendar.py"]
    src_zephyr_feedback_loop_collectors_market_event_integrator_py["(生产态 / production) 行情事件integrator /<br/>Market Event Integrator — v0.14.0 R197<br/>市场事件integrator。Market Event Integrator —<br/>v0.14.0 R197<br/>文件: collectors/market_event_integrator.py"]
    src_zephyr_feedback_loop_collectors_notification_feedback_py["(生产态 / production) 通知反馈 / Notification<br/>Feedback — v0.9.0 R118<br/>通知反馈。Notification Feedback — v0.9.0 R118<br/>文件: collectors/notification_feedback.py"]
    src_zephyr_feedback_loop_collectors_schema_evolution_py["(生产态 / production) 模式进化 / Schema<br/>Evolution — v0.9.0 R111<br/>模式进化。Schema Evolution — v0.9.0 R111<br/>文件: collectors/schema_evolution.py"]
    src_zephyr_feedback_loop_collectors_schema_migration_py["(生产态 / production) 模式迁移 / Schema<br/>Migration — v0.14.0 R190<br/>模式迁移。Schema Migration — v0.14.0 R190<br/>文件: collectors/schema_migration.py"]
    src_zephyr_feedback_loop_collectors_temporal_event_store_py["(生产态 / production) temporal事件存储 /<br/>Temporal Event Store — v0.3.0 R9<br/>temporal事件存储。Temporal Event Store — v0.3.0<br/>R9<br/>文件: collectors/temporal_event_store.py"]
    src_zephyr_feedback_loop_collectors_token_finops_py["(生产态 / production) 令牌finops / Token FinOps<br/>— v0.12.0 R162<br/>令牌finops。Token FinOps — v0.12.0 R162<br/>文件: collectors/token_finops.py"]
    src_zephyr_feedback_loop_core_py["(生产态 / production) 核心 / core<br/>FeedbackLoop core — 反馈闭环核心类。<br/>文件: feedback_loop/core.py"]
    src_zephyr_feedback_loop_db_writer_py["(生产态 / production) db写入器 / db_writer<br/>FLE 持久化写入器 — 写 metrics/alerts/dispatch_<br/>log 到 SQLite<br/>文件: feedback_loop/db_writer.py"]
    src_zephyr_feedback_loop_docs_cold_start_manual_py["(生产态 / production) 冷启动手册 / cold_start_<br/>manual<br/>冷启动手册（cold_start_manual.py）<br/>文件: docs/cold_start_manual.py"]
    src_zephyr_feedback_loop_evolution_auto_reward_py["(生产态 / production) 自动奖励 / Auto Reward —<br/>v0.7.0 R76<br/>自动奖励。Auto Reward — v0.7.0 R76<br/>文件: evolution/auto_reward.py"]
    src_zephyr_feedback_loop_evolution_conformal_prediction_py["(生产态 / production) conformal预测 / Conformal<br/>Prediction — v0.7.0 R74<br/>conformal预测。Conformal Prediction — v0.7.0 R74<br/>文件: evolution/conformal_prediction.py"]
    src_zephyr_feedback_loop_evolution_cross_gen_validation_py["(生产态 / production) 跨gen验证 / Cross-Gen<br/>Validation — v0.7.0 R78<br/>跨gen验证。Cross-Gen Validation — v0.7.0 R78<br/>文件: evolution/cross_gen_validation.py"]
    src_zephyr_feedback_loop_evolution_dynamic_threshold_py["(生产态 / production) 动态阈值 / Dynamic<br/>Threshold — v0.7.0 R71<br/>动态阈值。Dynamic Threshold — v0.7.0 R71<br/>文件: evolution/dynamic_threshold.py"]
    src_zephyr_feedback_loop_evolution_ewc_kb_review_py["(生产态 / production) ewc知识库审查 / EWC KB<br/>Review — v0.6.0 R51<br/>ewckb审查。EWC KB Review — v0.6.0 R51<br/>文件: evolution/ewc_kb_review.py"]
    src_zephyr_feedback_loop_evolution_failure_replay_py["(生产态 / production) 故障replay / Failure<br/>Replay — v0.7.0 R77<br/>failure回放，进化的核心类，封装FailureReplay相关<br/>逻辑。<br/>文件: evolution/failure_replay.py"]
    src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py["(生产态 / production) graduatedactivation协议 /<br/>Graduated Activation Protocol — v0.38.0 R485<br/>graduatedactivation协议。Graduated Activation<br/>Protocol — v0.38.0 R485<br/>文件: evolution/graduated_activation_protocol.py"]
    src_zephyr_feedback_loop_evolution_hypernetwork_py["(生产态 / production) 超网络 / HyperNetwork —<br/>v0.7.0 R72<br/>超网络，进化的核心类，封装超网络相关逻辑。<br/>文件: evolution/hypernetwork.py"]
    src_zephyr_feedback_loop_evolution_knowledge_distillation_py["(生产态 / production) 知识distillation /<br/>Knowledge Distillation — v0.6.0 R52<br/>知识distillation。Knowledge Distillation —<br/>v0.6.0 R52<br/>文件: evolution/knowledge_distillation.py"]
    src_zephyr_feedback_loop_evolution_online_feature_importance_py["(生产态 / production) online特征importance /<br/>Online Feature Importance — v0.7.0 R73<br/>online功能importance。Online Feature Importance<br/>— v0.7.0 R73<br/>文件: evolution/online_feature_importance.py"]
    src_zephyr_feedback_loop_evolution_prompt_factory_governance_py["(生产态 / production) 提示工厂治理 / Prompt<br/>Factory Governance — v0.16.0 R224<br/>提示工厂治理。Prompt Factory Governance —<br/>v0.16.0 R224<br/>文件: evolution/prompt_factory_governance.py"]
    src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py["(生产态 / production) 提示优化回归检测器 /<br/>R514: PromptOptimizationRegressionDetector<br/>提示optimization回归检测器。R514:<br/>PromptOptimizationRegressionDetector<br/>文件: evolution/prompt_optimization_regression_<br/>detector.py"]
    src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py["(生产态 / production) 提示自优化循环 / R502:<br/>PromptSelfOptimizationLoop<br/>提示自optimizationloop。R502:<br/>PromptSelfOptimizationLoop<br/>文件: evolution/prompt_self_optimization_loop.py"]
    src_zephyr_feedback_loop_evolution_self_reflection_py["(生产态 / production) 自reflection / Self<br/>Reflection — v0.7.0 R75<br/>自reflection。Self Reflection — v0.7.0 R75<br/>文件: evolution/self_reflection.py"]
    src_zephyr_feedback_loop_evolution_self_upgrade_canary_py["(生产态 / production) selfupgrade金丝雀 / Self<br/>Upgrade Canary — v0.14.0 R194<br/>自upgradecanary。Self Upgrade Canary — v0.14.0<br/>R194<br/>文件: evolution/self_upgrade_canary.py"]
    src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py["(生产态 / production)<br/>semanticintentpreservation守卫 / R505:<br/>SemanticIntentPreservationGuard<br/>semanticintentpreservation守卫。R505:<br/>SemanticIntentPreservationGuard<br/>文件: evolution/semantic_intent_preservation_<br/>guard.py"]
    src_zephyr_feedback_loop_evolution_teacher_transfer_py["(生产态 / production) 教师迁移 / Teacher<br/>Transfer — v0.6.0 R53<br/>教师迁移，进化的核心类，封装TeacherTransfer相关<br/>逻辑。<br/>文件: evolution/teacher_transfer.py"]
    src_zephyr_feedback_loop_evolution_training_data_gov_py["(生产态 / production) training数据治理 /<br/>Training Data Governance — v0.14.0 R191<br/>training数据gov。Training Data Governance —<br/>v0.14.0 R191<br/>文件: evolution/training_data_gov.py"]
    src_zephyr_feedback_loop_evolution_engine_py["(生产态 / production) 进化引擎 / evolution_<br/>engine<br/>进化引擎，依赖网关工作<br/>文件: feedback_loop/evolution_engine.py"]
    src_zephyr_feedback_loop_forensic_architectural_sod_py["(生产态 / production) 架构职责分离 /<br/>Architectural SoD — v0.15.0 R205<br/>架构职责分离，取证的核心类，封装SoDRole相关逻辑<br/>。<br/>文件: forensic/architectural_sod.py"]
    src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py["(生产态 / production)<br/>automatedrcapostmortem生成器 / Automated RCA<br/>Postmortem Generator — v0.38.0 R486<br/>automatedrcapostmortem生成器。Automated RCA<br/>Postmortem Generator — v0.38.0 R486<br/>文件: forensic/automated_rca_postmortem_<br/>generator.py"]
    src_zephyr_feedback_loop_forensic_crypto_bootstrap_py["(生产态 / production) 加密自举 / Cryptographic<br/>Bootstrap — v0.15.0 R204<br/>加密自举，取证的核心类，封装HashLink相关逻辑。<br/>文件: forensic/crypto_bootstrap.py"]
    src_zephyr_feedback_loop_forensic_deterministic_replay_py["(生产态 / production) deterministic回放 /<br/>Deterministic Replay — v0.15.0 R206<br/>deterministic回放，反馈闭环的记录器，把发生的事<br/>件/结果记下来留档。<br/>文件: forensic/deterministic_replay.py"]
    src_zephyr_feedback_loop_forensic_external_verifier_py["(生产态 / production) 外部验证器 / External<br/>Verifier — v0.15.0 R203<br/>外部验证器。External Verifier — v0.15.0 R203<br/>文件: forensic/external_verifier.py"]
    src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py["(生产态 / production) fleupgrade安全校验器 /<br/>R529: FLEUpgradeSafetyValidator<br/>fleupgrade安全校验器。R529:<br/>FLEUpgradeSafetyValidator<br/>文件: forensic/fle_upgrade_safety_validator.py"]
    src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py["(生产态 / production) 守卫配置漂移监控 / R521:<br/>GuardConfigurationDriftMonitor<br/>守卫configuration漂移监控。R521:<br/>GuardConfigurationDriftMonitor<br/>文件: forensic/guard_configuration_drift_<br/>monitor.py"]
    src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py["(生产态 / production) interruptcoherence校验器<br/>/ R531: InterruptCoherenceValidator<br/>中断coherence校验器。R531:<br/>InterruptCoherenceValidator<br/>文件: forensic/interrupt_coherence_validator.py"]
    src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py["(生产态 / production) 知识注入preflight验证器 /<br/>R515: KnowledgeInjectionPreFlightVerifier<br/>知识injection预flight验证器。R515:<br/>KnowledgeInjectionPreFlightVerifier<br/>文件: forensic/knowledge_injection_pre_flight_<br/>verifier.py"]
    src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py["(生产态 / production) 点入时间reconstructor /<br/>Point-in-Time Reconstructor — v0.37.0 R465<br/>点入时间reconstructor。Point-in-Time<br/>Reconstructor — v0.37.0 R465<br/>文件: forensic/point_in_time_reconstructor.py"]
    src_zephyr_feedback_loop_forensic_self_modification_audit_py["(生产态 / production) selfmodification审计 /<br/>Self-Modification Audit — v0.15.0 R218<br/>自modification审计。Self-Modification Audit —<br/>v0.15.0 R218<br/>文件: forensic/self_modification_audit.py"]
    src_zephyr_feedback_loop_forensic_serialization_format_tracker_py["(生产态 / production) serializationformat追踪器<br/>/ Serialization Format Tracker — v0.39.0 R488<br/>serializationformat追踪器。Serialization Format<br/>Tracker — v0.39.0 R488<br/>文件: forensic/serialization_format_tracker.py"]
    src_zephyr_feedback_loop_forensic_state_migration_validator_py["(生产态 / production) 状态迁移校验器 / State<br/>Migration Validator — v0.40.0 R497<br/>状态迁移校验器。State Migration Validator —<br/>v0.40.0 R497<br/>文件: forensic/state_migration_validator.py"]
    src_zephyr_feedback_loop_forensic_sub_agent_collusion_py["(生产态 / production) sub代理collusion /<br/>Sub-Agent Collusion Detector — v0.15.0 R213<br/>子代理collusion。Sub-Agent Collusion Detector —<br/>v0.15.0 R213<br/>文件: forensic/sub_agent_collusion.py"]
    src_zephyr_feedback_loop_forensic_toctou_guard_py["(生产态 / production) TOCTOU守卫 / TOCTOU Guard<br/>— v0.15.0 R207<br/>toctou守卫。TOCTOU Guard — v0.15.0 R207<br/>文件: forensic/toctou_guard.py"]
    src_zephyr_feedback_loop_forensic_worm_write_integrity_py["(生产态 / production) wormwrite完整性 / WORM<br/>Write Integrity — v0.15.0 R216<br/>wormwrite完整性。WORM Write Integrity — v0.15.0<br/>R216<br/>文件: forensic/worm_write_integrity.py"]
    src_zephyr_feedback_loop_resilience_deadman_switch_py["(生产态 / production) deadman开关 / Deadman<br/>Switch — v0.15.0 R212<br/>deadman开关。Deadman Switch — v0.15.0 R212<br/>文件: resilience/deadman_switch.py"]
    src_zephyr_feedback_loop_resilience_dr_automation_py["(生产态 / production) 灾备自动化 / DR<br/>Automation — v0.14.0 R187<br/>灾备自动化，韧性的结果，封装操作结果的数据结构。<br/>文件: resilience/dr_automation.py"]
    src_zephyr_feedback_loop_resilience_multi_instance_coord_py["(生产态 / production) 多instancecoord /<br/>Multi-Instance Coordinator — v0.14.0 R199<br/>多instancecoord。Multi-Instance Coordinator —<br/>v0.14.0 R199<br/>文件: resilience/multi_instance_coord.py"]
    src_zephyr_feedback_loop_resilience_resource_starvation_aware_py["(生产态 / production) 资源starvation感知 /<br/>Resource Starvation Aware — v0.15.0 R209<br/>resourcestarvation感知，韧性的核心类，封装Resour<br/>ceBudget相关逻辑。<br/>文件: resilience/resource_starvation_aware.py"]
    src_zephyr_feedback_loop_resilience_split_brain_quorum_py["(生产态 / production) 拆分brainquorum /<br/>Split-Brain Quorum — v0.37.0 R451<br/>拆分brainquorum。Split-Brain Quorum — v0.37.0<br/>R451<br/>文件: resilience/split_brain_quorum.py"]
    src_zephyr_feedback_loop_scheduler_act_py["(生产态 / production) 调度器act / scheduler_act<br/>调度器act，反馈闭环的结果，封装操作结果的数据结<br/>构。<br/>文件: feedback_loop/scheduler_act.py"]
    src_zephyr_feedback_loop_scheduler_collect_detect_py["(生产态 / production) 调度器collectdetect /<br/>scheduler_collect_detect<br/>调度器collect检测，主要提供运行collect、运行检测<br/>、运行diagnose等功能，供调度器使用<br/>文件: feedback_loop/scheduler_collect_detect.py"]
    src_zephyr_feedback_loop_scheduler_health_py["(生产态 / production) 调度器健康 / scheduler_<br/>health<br/>调度器健康，主要提供报告等功能，供调度器使用<br/>文件: feedback_loop/scheduler_health.py"]
    src_zephyr_feedback_loop_scheduler_safety_py["(生产态 / production) 调度器安全 / scheduler_<br/>safety<br/>调度器安全，主要提供运行安全门禁、fle门禁缓存、f<br/>le门禁缓存等功能，供调度器使用<br/>文件: feedback_loop/scheduler_safety.py"]
    src_zephyr_feedback_loop_security_agent_skill_guard_py["(生产态 / production) 代理技能守卫 / Agent<br/>Skill Guard — v0.14.0 R201<br/>代理技能守卫。Agent Skill Guard — v0.14.0 R201<br/>文件: security/agent_skill_guard.py"]
    src_zephyr_feedback_loop_security_dep_cve_correlator_py["(生产态 / production) 依赖CVE关联器 /<br/>Dependency CVE Correlator — v0.14.0 R196<br/>依赖CVE关联器，安全的关联器，关联匹配相关数据。<br/>文件: security/dep_cve_correlator.py"]
    src_zephyr_feedback_loop_security_metric_prompt_scanner_py["(生产态 / production) 指标提示扫描器 /<br/>Metric-Prompt Scanner — v0.15.0 R215<br/>指标提示扫描器。Metric-Prompt Scanner — v0.15.0<br/>R215<br/>文件: security/metric_prompt_scanner.py"]
    src_zephyr_feedback_loop_security_remote_attestation_py["(生产态 / production) 远程attestation / Remote<br/>Attestation — v0.15.0 R211<br/>远程attestation。Remote Attestation — v0.15.0<br/>R211<br/>文件: security/remote_attestation.py"]
    src_zephyr_feedback_loop_security_secret_rotation_py["(生产态 / production) 密钥rotation / Secret<br/>Rotation — v0.14.0 R189<br/>密钥rotation。Secret Rotation — v0.14.0 R189<br/>文件: security/secret_rotation.py"]
    src_zephyr_feedback_loop_template_py["(生产态 / production) 模板 / template<br/>模板，供blueprint.md §0; zephyr.feedba使用<br/>文件: feedback_loop/template.py"]
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py["(生产态 / production) 集成测试管线 / E2E<br/>Integration Test Pipeline — TASK-MOD-FEEDBACK_<br/>LOOP-0028<br/>集成测试管线。E2E Integration Test Pipeline —<br/>TASK-MOD-FEEDBACK_LOOP-0028 (Phase43-87)<br/>文件: e2e/integration_test_pipeline.py"]
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
    src_zephyr_feedback_loop_actors_action_selector_py["(生产态 / production) 动作选择器 / action_<br/>selector<br/>动作选择器，反馈闭环的记录器，把发生的事件<br/>/结果记下来留档。<br/>文件: actors/action_selector.py"]
    src_zephyr_feedback_loop_alert_dispatcher_py["(生产态 / production) alert分发器 / alert_<br/>dispatcher<br/>FLE->Orc 告警分派器 — dispatch() 生产者<br/>文件: feedback_loop/alert_dispatcher.py"]
    src_zephyr_feedback_loop_collectors_feedback_collector_py["(生产态 / production) 反馈收集器 / feedback_<br/>collector<br/>反馈收集器，反馈闭环的数据库，持久化存取结构化数<br/>据。<br/>文件: collectors/feedback_collector.py"]
    src_zephyr_feedback_loop_collectors_metrics_collector_py["(生产态 / production) 指标收集器 / metrics_<br/>collector<br/>指标收集器，反馈闭环的核心类，封装MetricSnapshot<br/>相关逻辑。<br/>文件: collectors/metrics_collector.py"]
    src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py["(生产态 / production)<br/>selfmodification速率限制器 / R522:<br/>SelfModificationRateLimiter<br/>自modification率限制器。R522:<br/>SelfModificationRateLimiter<br/>文件: evolution/self_modification_rate_<br/>limiter.py"]
    src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py["(生产态 / production) boot完整性attestation /<br/>Boot Integrity Attestation — v0.38.0 R487<br/>启动完整性attestation。Boot Integrity<br/>Attestation — v0.38.0 R487<br/>文件: forensic/boot_integrity_attestation.py"]
    src_zephyr_feedback_loop_forensic_guard_complexity_budget_py["(生产态 / production) 守卫complexity预算 /<br/>R523: GuardComplexityBudget<br/>守卫complexity预算。R523: GuardComplexityBudget<br/>文件: forensic/guard_complexity_budget.py"]
    src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py["(生产态 / production) 配置hotreload守卫 /<br/>Config Hot-Reload Guard — v0.40.0 R498<br/>配置hotreload守卫。Config Hot-Reload Guard —<br/>v0.40.0 R498<br/>文件: resilience/config_hot_reload_guard.py"]
    src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py["(生产态 / production) gracefuldegradation规划器<br/>/ Graceful Degradation Planner — v0.40.0 R496<br/>graceful退化planner。Graceful Degradation<br/>Planner — v0.40.0 R496<br/>文件: resilience/graceful_degradation_planner.py"]
    src_zephyr_feedback_loop_resilience_oscillation_damping_py["(生产态 / production) 振荡阻尼 / Oscillation<br/>Damping — v0.37.0 R450<br/>振荡阻尼，韧性的状态机，管理状态流转。<br/>文件: resilience/oscillation_damping.py"]
    src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py["(生产态 / production) 自API限流器防御 / Self<br/>API Throttle Defense — v0.39.0 R491<br/>自APIthrottle防御。Self API Throttle Defense —<br/>v0.39.0 R491<br/>文件: resilience/self_api_throttle_defense.py"]
    src_zephyr_feedback_loop_security_wireheading_prevention_py["(生产态 / production) 神经劫持防护 /<br/>Wireheading Prevention — v0.37.0 R486<br/>神经劫持防护，安全的状态机，管理状态流转。<br/>文件: security/wireheading_prevention.py"]
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
    src_zephyr_feedback_loop_actors_alert_router_py["(生产态 / production) 告警路由器 / alert_<br/>router.py — Severity-based alert channel router.<br/>告警路由器，执行者的路由器，按规则分发请求到处理<br/>方。<br/>文件: actors/alert_router.py"]
    src_zephyr_feedback_loop_protocols_py["(生产态 / production) 协议 / protocols<br/>协议，反馈闭环的类型，定义数据类型和枚举。<br/>文件: feedback_loop/protocols.py"]
    src_zephyr_feedback_loop_actors_alert_router_py ~~~ src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_backpressure_bridge_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_auto_evolution_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_alert_dispatcher_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_alert_router_py
    src_zephyr_feedback_loop_decision_engine_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_db_writer_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_alert_dispatcher_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_alert_dispatcher_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_db_writer_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_health_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_collect_detect_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_safety_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_scheduler_act_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_generator_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_template_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_complexity_budget_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_scheduler_collect_detect_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_scheduler_collect_detect_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py
    src_zephyr_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_wireheading_prevention_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_oscillation_damping_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_core_py
    src_zephyr_feedback_loop_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_engine_py
    src_zephyr_feedback_loop_validator_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_template_py
    src_zephyr_feedback_loop_actors_action_selector_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_protocols_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_agent_lifecycle_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_alert_router_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_api_version_contract_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_owner_absence_escalation_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_action_selector_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_intent_driven_ops_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_secondary_alert_channel_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_global_action_scheduler_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_saga_compensator_py
    src_zephyr_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_actors_notification_personalizer_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_config_timeline_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_calendar_adapter_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_data_quality_validator_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_kb_provenance_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_packaging_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_injection_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_financial_stratification_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_capture_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_knowledge_freshness_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_known_unknown_registry_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_llm_cost_accounting_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_market_event_integrator_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_schema_evolution_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_notification_feedback_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_market_calendar_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_schema_migration_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_temporal_event_store_py
    src_zephyr_feedback_loop_collectors_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_token_finops_py
    src_zephyr_feedback_loop_docs_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_docs_cold_start_manual_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_cross_gen_validation_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_conformal_prediction_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_dynamic_threshold_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_auto_reward_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_hypernetwork_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_online_feature_importance_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_factory_governance_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_failure_replay_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_ewc_kb_review_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_upgrade_canary_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_knowledge_distillation_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_teacher_transfer_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_training_data_gov_py
    src_zephyr_feedback_loop_evolution_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_evolution_self_reflection_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_deterministic_replay_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_architectural_sod_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_crypto_bootstrap_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_external_verifier_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_self_modification_audit_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_guard_complexity_budget_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_serialization_format_tracker_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_state_migration_validator_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_toctou_guard_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_worm_write_integrity_py
    src_zephyr_feedback_loop_forensic_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_forensic_sub_agent_collusion_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_deadman_switch_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_oscillation_damping_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_resource_starvation_aware_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_split_brain_quorum_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_dr_automation_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_multi_instance_coord_py
    src_zephyr_feedback_loop_resilience_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_agent_skill_guard_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_dep_cve_correlator_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_metric_prompt_scanner_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_secret_rotation_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_remote_attestation_py
    src_zephyr_feedback_loop_security_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_security_wireheading_prevention_py
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_feedback_collector_py
    src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_collectors_metrics_collector_py
    src_zephyr_feedback_loop_tests_e2e_init_py -->|导入依赖 / import_depends| src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_feedback_loop_init_py,src_zephyr_feedback_loop_gen_inherited_py,src_zephyr_feedback_loop_actors_init_py,src_zephyr_feedback_loop_actors_action_selector_py,src_zephyr_feedback_loop_actors_agent_lifecycle_py,src_zephyr_feedback_loop_actors_alert_router_py,src_zephyr_feedback_loop_actors_api_version_contract_py,src_zephyr_feedback_loop_actors_global_action_scheduler_py,src_zephyr_feedback_loop_actors_incident_priority_triage_automator_py,src_zephyr_feedback_loop_actors_intent_driven_ops_py,src_zephyr_feedback_loop_actors_multi_agent_orchestrator_py,src_zephyr_feedback_loop_actors_notification_personalizer_py,src_zephyr_feedback_loop_actors_owner_absence_escalation_py,src_zephyr_feedback_loop_actors_saga_compensator_py,src_zephyr_feedback_loop_actors_secondary_alert_channel_py,src_zephyr_feedback_loop_alert_dispatcher_py,src_zephyr_feedback_loop_auto_evolution_py,src_zephyr_feedback_loop_backpressure_bridge_py,src_zephyr_feedback_loop_collectors_init_py,src_zephyr_feedback_loop_collectors_calendar_adapter_py,src_zephyr_feedback_loop_collectors_config_timeline_py,src_zephyr_feedback_loop_collectors_data_quality_validator_py,src_zephyr_feedback_loop_collectors_feedback_collector_py,src_zephyr_feedback_loop_collectors_financial_stratification_py,src_zephyr_feedback_loop_collectors_kb_provenance_py,src_zephyr_feedback_loop_collectors_knowledge_capture_py,src_zephyr_feedback_loop_collectors_knowledge_freshness_py,src_zephyr_feedback_loop_collectors_knowledge_injection_py,src_zephyr_feedback_loop_collectors_knowledge_packaging_py,src_zephyr_feedback_loop_collectors_known_unknown_registry_py,src_zephyr_feedback_loop_collectors_llm_cost_accounting_py,src_zephyr_feedback_loop_collectors_market_calendar_py,src_zephyr_feedback_loop_collectors_market_event_integrator_py,src_zephyr_feedback_loop_collectors_metrics_collector_py,src_zephyr_feedback_loop_collectors_notification_feedback_py,src_zephyr_feedback_loop_collectors_schema_evolution_py,src_zephyr_feedback_loop_collectors_schema_migration_py,src_zephyr_feedback_loop_collectors_temporal_event_store_py,src_zephyr_feedback_loop_collectors_token_finops_py,src_zephyr_feedback_loop_config_py,src_zephyr_feedback_loop_core_py,src_zephyr_feedback_loop_db_bridge_py,src_zephyr_feedback_loop_db_writer_py,src_zephyr_feedback_loop_decision_engine_py,src_zephyr_feedback_loop_docs_init_py,src_zephyr_feedback_loop_docs_cold_start_manual_py,src_zephyr_feedback_loop_error_budget_py,src_zephyr_feedback_loop_eval_harness_py,src_zephyr_feedback_loop_evolution_init_py,src_zephyr_feedback_loop_evolution_auto_reward_py,src_zephyr_feedback_loop_evolution_conformal_prediction_py,src_zephyr_feedback_loop_evolution_cross_gen_validation_py,src_zephyr_feedback_loop_evolution_dynamic_threshold_py,src_zephyr_feedback_loop_evolution_ewc_kb_review_py,src_zephyr_feedback_loop_evolution_failure_replay_py,src_zephyr_feedback_loop_evolution_graduated_activation_protocol_py,src_zephyr_feedback_loop_evolution_hypernetwork_py,src_zephyr_feedback_loop_evolution_knowledge_distillation_py,src_zephyr_feedback_loop_evolution_online_feature_importance_py,src_zephyr_feedback_loop_evolution_prompt_factory_governance_py,src_zephyr_feedback_loop_evolution_prompt_optimization_regression_detector_py,src_zephyr_feedback_loop_evolution_prompt_self_optimization_loop_py,src_zephyr_feedback_loop_evolution_self_modification_rate_limiter_py,src_zephyr_feedback_loop_evolution_self_reflection_py,src_zephyr_feedback_loop_evolution_self_upgrade_canary_py,src_zephyr_feedback_loop_evolution_semantic_intent_preservation_guard_py,src_zephyr_feedback_loop_evolution_teacher_transfer_py,src_zephyr_feedback_loop_evolution_training_data_gov_py,src_zephyr_feedback_loop_evolution_engine_py,src_zephyr_feedback_loop_exceptions_py,src_zephyr_feedback_loop_feedback_collector_py,src_zephyr_feedback_loop_fitness_functions_py,src_zephyr_feedback_loop_forensic_init_py,src_zephyr_feedback_loop_forensic_architectural_sod_py,src_zephyr_feedback_loop_forensic_automated_rca_postmortem_generator_py,src_zephyr_feedback_loop_forensic_boot_integrity_attestation_py,src_zephyr_feedback_loop_forensic_crypto_bootstrap_py,src_zephyr_feedback_loop_forensic_deterministic_replay_py,src_zephyr_feedback_loop_forensic_external_verifier_py,src_zephyr_feedback_loop_forensic_fle_upgrade_safety_validator_py,src_zephyr_feedback_loop_forensic_guard_complexity_budget_py,src_zephyr_feedback_loop_forensic_guard_configuration_drift_monitor_py,src_zephyr_feedback_loop_forensic_interrupt_coherence_validator_py,src_zephyr_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py,src_zephyr_feedback_loop_forensic_point_in_time_reconstructor_py,src_zephyr_feedback_loop_forensic_self_modification_audit_py,src_zephyr_feedback_loop_forensic_serialization_format_tracker_py,src_zephyr_feedback_loop_forensic_state_migration_validator_py,src_zephyr_feedback_loop_forensic_sub_agent_collusion_py,src_zephyr_feedback_loop_forensic_toctou_guard_py,src_zephyr_feedback_loop_forensic_worm_write_integrity_py,src_zephyr_feedback_loop_gates_init_py,src_zephyr_feedback_loop_generator_py,src_zephyr_feedback_loop_metrics_collector_py,src_zephyr_feedback_loop_protocols_py,src_zephyr_feedback_loop_resilience_init_py,src_zephyr_feedback_loop_resilience_config_hot_reload_guard_py,src_zephyr_feedback_loop_resilience_deadman_switch_py,src_zephyr_feedback_loop_resilience_dr_automation_py,src_zephyr_feedback_loop_resilience_graceful_degradation_planner_py,src_zephyr_feedback_loop_resilience_multi_instance_coord_py,src_zephyr_feedback_loop_resilience_oscillation_damping_py,src_zephyr_feedback_loop_resilience_resource_starvation_aware_py,src_zephyr_feedback_loop_resilience_self_api_throttle_defense_py,src_zephyr_feedback_loop_resilience_split_brain_quorum_py,src_zephyr_feedback_loop_scheduler_py,src_zephyr_feedback_loop_scheduler_act_py,src_zephyr_feedback_loop_scheduler_collect_detect_py,src_zephyr_feedback_loop_scheduler_health_py,src_zephyr_feedback_loop_scheduler_safety_py,src_zephyr_feedback_loop_security_init_py,src_zephyr_feedback_loop_security_agent_skill_guard_py,src_zephyr_feedback_loop_security_dep_cve_correlator_py,src_zephyr_feedback_loop_security_metric_prompt_scanner_py,src_zephyr_feedback_loop_security_remote_attestation_py,src_zephyr_feedback_loop_security_secret_rotation_py,src_zephyr_feedback_loop_security_wireheading_prevention_py,src_zephyr_feedback_loop_self_diagnosis_py,src_zephyr_feedback_loop_session_learner_py,src_zephyr_feedback_loop_slo_manager_py,src_zephyr_feedback_loop_template_py,src_zephyr_feedback_loop_tests_e2e_init_py,src_zephyr_feedback_loop_tests_e2e_integration_test_pipeline_py,src_zephyr_feedback_loop_validator_py,src_zephyr_feedback_loop_verifiers_init_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个），不含跨域外部节点。

> （无模块 / No modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_AUTONOMY_CORE 自治核心: 向量桥接 / vector_bridge (context/vector_bridge.py) | 导入依赖 / import_depends |
| 2 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_FBL_DETECTORS 反馈检测器: 包入口 / __init__ (detectors/__init__.py) | 导入依赖 / import_depends |
| 3 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_FBL_DETECTORS 反馈检测器: 异常检测器 / anomaly_detector (anomaly/anomaly_detector.py) | 导入依赖 / import_depends |
| 4 | 调度器act / scheduler_act (feedback_loop/scheduler_act.py) | → | D_FBL_DETECTORS 反馈检测器: 包入口 / __init__ (detectors/__init__.py) | 导入依赖 / import_depends |
| 5 | 调度器collectdetect / scheduler_collect_detect (feedback_... | → | D_FBL_DETECTORS 反馈检测器: 包入口 / __init__ (detectors/__init__.py) | 导入依赖 / import_depends |
| 6 | 调度器健康 / scheduler_health (feedback_loop/scheduler_he... | → | D_FBL_DETECTORS 反馈检测器: 包入口 / __init__ (detectors/__init__.py) | 导入依赖 / import_depends |
| 7 | 集成测试管线 / E2E Integration Test Pipeline — TASK-MOD-... | → | D_FBL_DETECTORS 反馈检测器: 包入口 / __init__ (detectors/__init__.py) | 导入依赖 / import_depends |
| 8 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_FBL_DIAGNOSERS 反馈诊断器: 包入口 / __init__ (diagnosers/__init__.py) | 导入依赖 / import_depends |
| 9 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_FBL_DIAGNOSERS 反馈诊断器: 诊断引擎 / diagnosis_engine (diagnosis/diagnosis_engine.py) | 导入依赖 / import_depends |
| 10 | 调度器act / scheduler_act (feedback_loop/scheduler_act.py) | → | D_FBL_DIAGNOSERS 反馈诊断器: 包入口 / __init__ (diagnosers/__init__.py) | 导入依赖 / import_depends |
| 11 | 调度器collectdetect / scheduler_collect_detect (feedback_... | → | D_FBL_DIAGNOSERS 反馈诊断器: 包入口 / __init__ (diagnosers/__init__.py) | 导入依赖 / import_depends |
| 12 | 调度器健康 / scheduler_health (feedback_loop/scheduler_he... | → | D_FBL_DIAGNOSERS 反馈诊断器: 包入口 / __init__ (diagnosers/__init__.py) | 导入依赖 / import_depends |
| 13 | 调度器安全 / scheduler_safety (feedback_loop/scheduler_sa... | → | D_FBL_DIAGNOSERS 反馈诊断器: 包入口 / __init__ (diagnosers/__init__.py) | 导入依赖 / import_depends |
| 14 | 集成测试管线 / E2E Integration Test Pipeline — TASK-MOD-... | → | D_FBL_DIAGNOSERS 反馈诊断器: 包入口 / __init__ (diagnosers/__init__.py) | 导入依赖 / import_depends |
| 15 | 包入口 / feedback-loop.gates — auto-generated package in... | → | D_FBL_VERIFICATION 反馈验证: 治理门禁 / _governance_gates (gates/_governance_gates.py) | 导入依赖 / import_depends |
| 16 | 包入口 / feedback-loop.gates — auto-generated package in... | → | D_FBL_VERIFICATION 反馈验证: 运营门禁 / _operational_gates (gates/_operational_gates.py) | 导入依赖 / import_depends |
| 17 | 包入口 / feedback-loop.gates — auto-generated package in... | → | D_FBL_VERIFICATION 反馈验证: 安全门禁 / _safety_gates (gates/_safety_gates.py) | 导入依赖 / import_depends |
| 18 | 包入口 / feedback-loop.gates — auto-generated package in... | → | D_FBL_VERIFICATION 反馈验证: 安全门禁 / _security_gates (gates/_security_gates.py) | 导入依赖 / import_depends |
| 19 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_FBL_VERIFICATION 反馈验证: 验证引擎 / verification_engine (verifiers/verification_en... | 导入依赖 / import_depends |
| 20 | 调度器act / scheduler_act (feedback_loop/scheduler_act.py) | → | D_FBL_VERIFICATION 反馈验证: 级联回滚分析器 / Cascading Rollback Analyzer — v0.38.0 R... | 导入依赖 / import_depends |
| 21 | 调度器act / scheduler_act (feedback_loop/scheduler_act.py) | → | D_FBL_VERIFICATION 反馈验证: stochastic诊断验证器 / Stochastic Diagnosis Verifier — v... | 导入依赖 / import_depends |
| 22 | 调度器act / scheduler_act (feedback_loop/scheduler_act.py) | → | D_FBL_VERIFICATION 反馈验证: 验证引擎 / verification_engine (verifiers/verification_en... | 导入依赖 / import_depends |
| 23 | 调度器安全 / scheduler_safety (feedback_loop/scheduler_sa... | → | D_FBL_VERIFICATION 反馈验证: 部署抑制 / Deployment Suppression — v0.37.0 R464 (gates/... | 导入依赖 / import_depends |
| 24 | 调度器安全 / scheduler_safety (feedback_loop/scheduler_sa... | → | D_FBL_VERIFICATION 反馈验证: 安全门禁l1l27 / Safety Gates L1-L27 — Unified Pipeline (... | 导入依赖 / import_depends |
| 25 | 集成测试管线 / E2E Integration Test Pipeline — TASK-MOD-... | → | D_FBL_VERIFICATION 反馈验证: 安全门禁l1l27 / Safety Gates L1-L27 — Unified Pipeline (... | 导入依赖 / import_depends |
| 26 | 集成测试管线 / E2E Integration Test Pipeline — TASK-MOD-... | → | D_FBL_VERIFICATION 反馈验证: 安全门禁l66l67 / Safety Gates L66-L67 — Financial Pruden... | 导入依赖 / import_depends |
| 27 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: ab测试 / A/B Test Verifier — v0.9.0 R117 (verifiers/ab_t... | 导入依赖 / import_depends |
| 28 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 行为explainability / Action Explainability — v0.3.0 R15 ... | 导入依赖 / import_depends |
| 29 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: AI评论真实性 / AI Comment Veracity — v0.37.0 R459 (verif... | 导入依赖 / import_depends |
| 30 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 攻击模拟器 / Attack Simulator — v0.6.0 R57 (verifiers/at... | 导入依赖 / import_depends |
| 31 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 自动回滚 / Auto Rollback — v0.8.0 R93 (verifiers/auto_ro... | 导入依赖 / import_depends |
| 32 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: buildreproducibility验证器 / Build Reproducibility Verifi... | 导入依赖 / import_depends |
| 33 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 金丝雀修复 / Canary Repair — v0.8.0 R104b (verifiers/can... | 导入依赖 / import_depends |
| 34 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 级联回滚分析器 / Cascading Rollback Analyzer — v0.38.0 R... | 导入依赖 / import_depends |
| 35 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 跨蓝图契约漂移 / Cross-Blueprint Contract Drift Monitor ... | 导入依赖 / import_depends |
| 36 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 跨模块集成 / Cross-Module Integration Verifier — v0.5.0 ... | 导入依赖 / import_depends |
| 37 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 跨会话知识完整性 / Cross-Session Knowledge Integrity — v... | 导入依赖 / import_depends |
| 38 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 数字孪生沙箱 / Digital Twin Sandbox — v0.6.0 R55 (verifi... | 导入依赖 / import_depends |
| 39 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: dry运行沙箱 / Dry Run Sandbox — v0.3.0 R19 (verifiers/dr... | 导入依赖 / import_depends |
| 40 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: federated协议 / Federated Protocol — v0.10.0 R129 (verif... | 导入依赖 / import_depends |
| 41 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: golden测试external / Golden Test External — v0.15.0 R214... | 导入依赖 / import_depends |
| 42 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: noLLM退化 / No-LLM Degradation Mode — v0.8.0 R94 (verifi... | 导入依赖 / import_depends |
| 43 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: preflight模拟器 / Pre-Flight Simulator — v0.12.0 R169b (... | 导入依赖 / import_depends |
| 44 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 预防性修复 / Preventive Repair — v0.6.0 R69 (verifiers/p... | 导入依赖 / import_depends |
| 45 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 回滚完整性 / Rollback Integrity — v0.3.0 R18b (verifiers... | 导入依赖 / import_depends |
| 46 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 仿真到实盘校准 / Sim2Real Calibration — v0.6.0 R56 (veri... | 导入依赖 / import_depends |
| 47 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: stochastic诊断验证器 / Stochastic Diagnosis Verifier — v... | 导入依赖 / import_depends |
| 48 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: TOCTOU重新验证 / TOCTOU Revalidation — v0.37.0 R458 (ver... | 导入依赖 / import_depends |
| 49 | 包入口 / feedback-loop.verifiers — auto-generated packag... | → | D_FBL_VERIFICATION 反馈验证: 验证引擎 / verification_engine (verifiers/verification_en... | 导入依赖 / import_depends |
| 50 | alert分发器 / alert_dispatcher (feedback_loop/alert_dispa... | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 51 | 数据库桥接 / db_bridge (feedback_loop/db_bridge.py) | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 52 | db写入器 / db_writer (feedback_loop/db_writer.py) | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 53 | 指标收集器 / MetricsCollector: append-only metrics record... | → | D_GOVERNANCE 生命周期管理: sqlite结构 / sqlite_schema (persistence/sqlite_schema.py) | 导入依赖 / import_depends |
| 54 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_GOV_DRIFT 漂移检测: 漂移引擎 / drift_engine (gov_drift/drift_engine.py) | 导入依赖 / import_depends |
| 55 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_GOV_DRIFT 漂移检测: 完整性 / integrity (governance/integrity.py) | 导入依赖 / import_depends |
| 56 | 调度器act / scheduler_act (feedback_loop/scheduler_act.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级引擎 / Escalation Engine — MOD-INF-022 (escalation/e... | 导入依赖 / import_depends |
| 57 | 调度器act / scheduler_act (feedback_loop/scheduler_act.py) | → | D_GOV_OPS_RESILIENCE 运维弹性治理: 升级模型 / Escalation Protocol data models — MOD-INF-022... | 导入依赖 / import_depends |
| 58 | 调度器act / scheduler_act (feedback_loop/scheduler_act.py) | → | D_INFRA_RECOVERY 回滚恢复: 回滚执行器 / rollback_executor (rollback/rollback_executo... | 导入依赖 / import_depends |
| 59 | 背压桥接 / backpressure_bridge (feedback_loop/backpressur... | → | D_INFRA_RUNTIME 运行时集成: 背压管理器 / Pipeline — Backpressure Manager (pipeline/b... | 导入依赖 / import_depends |
| 60 | db写入器 / db_writer (feedback_loop/db_writer.py) | → | D_INFRA_RUNTIME 运行时集成: 指标桥接 / metrics_bridge (system_telemetry/metrics_bridg... | 导入依赖 / import_depends |
| 61 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_INFRA_RUNTIME 运行时集成: 指标桥接 / metrics_bridge (system_telemetry/metrics_bridg... | 导入依赖 / import_depends |
| 62 | 协议 / protocols (feedback_loop/protocols.py) | → | D_INTEGRATION 管线路由: 协议 / Structural Protocol interfaces for cross-module co... | 导入依赖 / import_depends |
| 63 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_INTEGRATION 管线路由: 入进程向量记忆 / in_process_vector_memory (vector_memory/... | 导入依赖 / import_depends |
| 64 | alert分发器 / alert_dispatcher (feedback_loop/alert_dispa... | → | D_ORCHESTRATOR 代理编排器: 告警处理器 / alert_handler (contracts/alert_handler.py) | 导入依赖 / import_depends |
| 65 | 进化引擎 / evolution_engine (feedback_loop/evolution_engi... | → | D_SECURITY 对抗验证: 网关 / gateway (llm_security/gateway.py) | 导入依赖 / import_depends |
| 66 | API版本契约 / API Version Contract — v0.14.0 R188 (actor... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 67 | 核心 / core (feedback_loop/core.py) | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 68 | 核心 / core (feedback_loop/core.py) | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 69 | 核心 / core (feedback_loop/core.py) | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 70 | 数据库桥接 / db_bridge (feedback_loop/db_bridge.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 71 | 进化引擎 / evolution_engine (feedback_loop/evolution_engi... | → | D_SHARED 共享服务: 异步工具 / async_utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 72 | 反馈收集器 / FeedbackCollector: collect task execution fe... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 73 | 反馈收集器 / FeedbackCollector: collect task execution fe... | → | D_SHARED 共享服务: 模式 / schemas (schema/schemas.py) | 导入依赖 / import_depends |
| 74 | 反馈收集器 / FeedbackCollector: collect task execution fe... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 75 | 适应度functions / fitness_functions (feedback_loop/fitnes... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 76 | selfmodification审计 / Self-Modification Audit — v0.15.0... | → | D_SHARED 共享服务: 时间工具 / time_utils (utils/time_utils.py) | 导入依赖 / import_depends |
| 77 | 指标收集器 / MetricsCollector: append-only metrics record... | → | D_SHARED 共享服务: sqlite工厂 / sqlite_factory (io/sqlite_factory.py) | 导入依赖 / import_depends |
| 78 | 配置hotreload守卫 / Config Hot-Reload Guard — v0.40.0 R4... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设施（Phase ... | 导入依赖 / import_depends |
| 79 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_SHARED 共享服务: 事件总线 / event_bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 80 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 81 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_SHARED 共享服务: 端口 / ports (protocols/ports.py) | 导入依赖 / import_depends |
| 82 | 调度器 / scheduler (feedback_loop/scheduler.py) | → | D_SHARED 共享服务: 异步工具 / async_utils (utils/async_utils.py) | 导入依赖 / import_depends |
| 83 | 调度器act / scheduler_act (feedback_loop/scheduler_act.py) | → | D_SHARED 共享服务: 事件总线 / event_bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 84 | 调度器安全 / scheduler_safety (feedback_loop/scheduler_sa... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of  / paths ... | 导入依赖 / import_depends |
| 85 | 密钥rotation / Secret Rotation — v0.14.0 R189 (security/... | → | D_SHARED 共享服务: 密钥 / secrets (security/secrets.py) | 导入依赖 / import_depends |
| 86 | SLO管理器 / slo_manager (feedback_loop/slo_manager.py) | → | D_SHARED 共享服务: 事件总线 / event_bus (shared/event_bus.py) | 导入依赖 / import_depends |
| 87 | SLO管理器 / slo_manager (feedback_loop/slo_manager.py) | → | D_SHARED 共享服务: 指标 / metrics (observability/metrics.py) | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 / test_f14_... | → | 错误预算 / error_budget (feedback_loop/error_budget.py) | 测试依赖 / test_depends |
| 2 | D_AUTONOMY_CORE 自治核心: F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 / test_f14_... | → | 调度器 / scheduler (feedback_loop/scheduler.py) | 测试依赖 / test_depends |
| 3 | D_FBL_DETECTORS 反馈检测器: 异常检测器 / anomaly_detector (anomaly/anomaly_detector.py) | → | 反馈收集器 / feedback_collector (collectors/feedback_coll... | 导入依赖 / import_depends |
| 4 | D_FBL_DETECTORS 反馈检测器: 异常检测器 / anomaly_detector (anomaly/anomaly_detector.py) | → | 指标收集器 / metrics_collector (collectors/metrics_collec... | 导入依赖 / import_depends |
| 5 | D_FBL_DETECTORS 反馈检测器: 异常检测器 / anomaly_detector (anomaly/anomaly_detector.py) | → | 协议 / protocols (feedback_loop/protocols.py) | 导入依赖 / import_depends |
| 6 | D_FRONTEND 前端: 适应度functions / fitness_functions (components/fitness_f... | → | 适应度functions / fitness_functions (feedback_loop/fitnes... | 导入依赖 / import_depends |
| 7 | D_GOV_AUDIT 审计追踪: 反馈桥接 / feedback_bridge (gov_audit/feedback_bridge.py) | → | 包入口 / Feedback Loop Engine — MOD-FEEDBACK_LOOP. (feed... | 导入依赖 / import_depends |
| 8 | D_INFRA_RUNTIME 运行时集成: 自动运行时核心 / auto_runtime_core (trading/auto_runtime_... | → | 包入口 / Feedback Loop Engine — MOD-FEEDBACK_LOOP. (feed... | 导入依赖 / import_depends |
| 9 | D_INFRA_RUNTIME 运行时集成: 自动运行时核心 / auto_runtime_core (trading/auto_runtime_... | → | 调度器 / scheduler (feedback_loop/scheduler.py) | 导入依赖 / import_depends |
| 10 | D_INFRA_RUNTIME 运行时集成: 生命周期管理器 / lifecycle_manager (trading/lifecycle_man... | → | 包入口 / Feedback Loop Engine — MOD-FEEDBACK_LOOP. (feed... | 导入依赖 / import_depends |
| 11 | D_ORCHESTRATOR 代理编排器: 触发器路由器 / trigger_router (execution/trigger_router.py) | → | 决策引擎 / Feedback Loop Decision Engine (feedback_loop/d... | 导入依赖 / import_depends |
| 12 | D_SECURITY 对抗验证: 反馈桥接 / feedback_bridge (orphan_judge/feedback_bridge.py) | → | 包入口 / Feedback Loop Engine — MOD-FEEDBACK_LOOP. (feed... | 导入依赖 / import_depends |
| 13 | D_SHARED 共享服务: 密钥 / secrets (security/secrets.py) | → | 密钥rotation / Secret Rotation — v0.14.0 R189 (security/... | 导入依赖 / import_depends |

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
