---
doc_type: architecture_view
title: D_GOV_DOCS 架构文档治理架构文档
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 51_d_gov_docs / 架构文档治理域 / Architecture Docs Governance

> **功能简介 / Overview**: 架构文档治理，负责架构文档生成、一致性和版本管理

> **文档作用 / Purpose**: 展示 架构文档治理（D_GOV_DOCS）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

> **[可缩放 HTML 版 / Zoomable HTML](http://localhost:8765/docs/02_enterprise_architecture/02_domain_architecture_docs/_zoomable_html/51_d_gov_docs.html)** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 51 | Number | 51 |
| 域ID | D_GOV_DOCS | Domain ID | D_GOV_DOCS |
| 域名称 | 架构文档治理 | Domain Name | Architecture Docs Governance |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 25 | Module Count | 25 |
| 域内依赖 | 0 | Internal Dependencies | 0 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 2 | Cross-domain Outgoing | 2 |
| 设计态模块 | 23 | Design Modules | 23 |
| 生产态模块 | 2 | Production Modules | 2 |
| 容量 | 2/150 (正常) | Capacity | 2/150 (正常) |
| 描述 | 架构模型文档(architecture_model) | Description | 架构模型文档(architecture_model) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。
>
> **图例说明 / Legend**：
> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 全景图（全部模块，颜色区分运营态/设计态）

> 展示全部 25 个模块（生产态 2 + 设计态 23），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_03_modules_cross_layer_auto_fix_engine_blueprint_md["蓝图<br/>自动修复引擎的模块<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: auto_fix_engine/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_auto_runtime_core_blueprint_md["蓝图<br/>自动运行时核心蓝图，定义 MAPE-K<br/>调和循环的大脑主控，协调监控-分析-规划-执行四阶<br/>段自洽循环。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: auto_runtime_core/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_behavioral_auditor_blueprint_md["蓝图<br/>AI 行为边界审计引擎蓝图，定义 agent<br/>行为合规性审计的主控类与审计规则。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: behavioral_auditor/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_context_engine_blueprint_md["蓝图<br/>上下文引擎集成蓝图，定义上下文注入管道<br/>（build→compress→validate→inject）与 Token<br/>预算管控。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: context_engine/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_database_blueprint_md["蓝图<br/>数据库层蓝图，定义数据持久化的分层架构与访问契约<br/>。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: database/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_database_business_data_architecture_md["业务数据架构文档<br/>描述系统各业务数据的分层结构和跨层关系，是数据架<br/>构设计的顶层参考。<br/>文件: database/business_data_architecture.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_feedback_loop_blueprint_md["蓝图<br/>反馈循环蓝图，定义反馈采集-分析-提案-应用的自强<br/>化学习闭环。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: feedback_loop/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_gate_engine_blueprint_md["蓝图<br/>门禁引擎蓝图，定义门禁检查的注册、执行与阻断机制<br/>。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: gate_engine/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_model_capability_exam_blueprint_md["蓝图<br/>模型能力考试蓝图，定义五轴入职考试主控，评估模型<br/>是否具备上岗能力。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: model_capability_exam/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_orphan_judge_blueprint_md["蓝图<br/>孤儿判定引擎蓝图，定义五层判定→决策路由→安全围栏<br/>→处置建议的孤儿文件判定主控。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: orphan_judge/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_pipeline_blueprint_md["蓝图<br/>管线协调器蓝图，定义 M1-M11<br/>双管线调度核心，协调数据与执行两条管线的流转。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: pipeline/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_red_blue_validator_blueprint_md["蓝图<br/>红蓝对抗验证器蓝图，定义红队攻击与蓝队防御的对抗<br/>验证框架。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: red_blue_validator/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_resource_optimization_engine_blueprint_md["资源优化引擎蓝图<br/>定义 MAPE-K<br/>循环驱动的资源监控、分析、优化与自愈主控<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: resource_optimization_engine/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_semantic_auditor_blueprint_md["蓝图<br/>语义审计器蓝图，定义 2 类纯语义触发与 9<br/>阶段管道的语义审计主控。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: semantic_auditor/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_shared_core_blueprint_md["蓝图<br/>共享核心蓝图，定义跨域共享的基础数据结构与工具契<br/>约。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: shared_core/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_autonomy_core_agent_spec_blueprint_md["蓝图<br/>Agent 规格蓝图，定义蓝图→Skill 升级引擎，把<br/>agent 规格声明转为可执行技能。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: agent_spec/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_autonomy_core_rollback_system_blueprint_md["蓝图<br/>回滚系统蓝图，定义回滚执行器，管理回滚生命周期与<br/>变更撤销。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: rollback_system/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_autonomy_perm_budget_enforcer_blueprint_md["蓝图<br/>预算执行器蓝图，定义预算限额的检查、消耗与熔断机<br/>制。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: budget_enforcer/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_autonomy_perm_escalation_protocol_blueprint_md["蓝图<br/>升级协议蓝图，定义规则匹配→级别判定→经济护栏检查<br/>→返回 EscalationEvent 的升级流程。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: escalation_protocol/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_governance_blueprint_md["蓝图<br/>治理域蓝图，定义治理域的总体架构与各治理子域的协<br/>调关系。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: _domain_governance/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_governance_code_dedup_engine_blueprint_md["蓝图<br/>代码去重引擎蓝图，定义全生命周期七维去重的主控，<br/>检测并合并重复代码。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: code_dedup_engine/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_governance_governance_automation_blueprint_md["脚本系统蓝图 — 第三条生产线的自动化审计与门禁<br/>治理自动化蓝图，定义运行全维度或指定维度审计扫描<br/>的自动化主控。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: governance_automation/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_governance_registry_governance_blueprint_md["注册表治理<br/>蓝图，定义功能域注册表的加载、查询、重叠检测与注<br/>册管理<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: registry_governance/blueprint.md<br/>(设计态 / design)"]
    tests_governance_d8_doc_sync_test_guc_trigger_fix_py["测试guc触发器fix.py — GUC 触发器缺陷修复的端到<br/>GUC 触发器缺陷修复的端到端 smoke test<br/>（#ARCH-GUC-TRIGGER-FIX-001）<br/>test_guc_trigger_fix<br/>文件: d8_doc_sync/test_guc_trigger_fix.py<br/>(生产态 / production)"]
    tests_governance_d8_doc_sync_test_sync_savepoint_isolation_py["测试syncsavepointisolation<br/>() 级联失败隔离验证（#ARCH-GUC-TRIGGER-FIX-001<br/>裁定 B / P1）<br/>test_sync_savepoint_isolation<br/>文件: d8_doc_sync<br/>/test_sync_savepoint_isolation.py<br/>(生产态 / production)"]
    docs_03_modules_cross_layer_auto_fix_engine_blueprint_md ~~~ docs_03_modules_cross_layer_auto_runtime_core_blueprint_md
    docs_03_modules_cross_layer_auto_runtime_core_blueprint_md ~~~ docs_03_modules_cross_layer_behavioral_auditor_blueprint_md
    docs_03_modules_cross_layer_behavioral_auditor_blueprint_md ~~~ docs_03_modules_cross_layer_context_engine_blueprint_md
    docs_03_modules_cross_layer_context_engine_blueprint_md ~~~ docs_03_modules_cross_layer_database_blueprint_md
    docs_03_modules_cross_layer_database_blueprint_md ~~~ docs_03_modules_cross_layer_database_business_data_architecture_md
    docs_03_modules_cross_layer_database_business_data_architecture_md ~~~ docs_03_modules_cross_layer_feedback_loop_blueprint_md
    docs_03_modules_cross_layer_feedback_loop_blueprint_md ~~~ docs_03_modules_cross_layer_gate_engine_blueprint_md
    docs_03_modules_cross_layer_gate_engine_blueprint_md ~~~ docs_03_modules_cross_layer_model_capability_exam_blueprint_md
    docs_03_modules_cross_layer_model_capability_exam_blueprint_md ~~~ docs_03_modules_cross_layer_orphan_judge_blueprint_md
    docs_03_modules_cross_layer_orphan_judge_blueprint_md ~~~ docs_03_modules_cross_layer_pipeline_blueprint_md
    docs_03_modules_cross_layer_pipeline_blueprint_md ~~~ docs_03_modules_cross_layer_red_blue_validator_blueprint_md
    docs_03_modules_cross_layer_red_blue_validator_blueprint_md ~~~ docs_03_modules_cross_layer_resource_optimization_engine_blueprint_md
    docs_03_modules_cross_layer_resource_optimization_engine_blueprint_md ~~~ docs_03_modules_cross_layer_semantic_auditor_blueprint_md
    docs_03_modules_cross_layer_semantic_auditor_blueprint_md ~~~ docs_03_modules_cross_layer_shared_core_blueprint_md
    docs_03_modules_cross_layer_shared_core_blueprint_md ~~~ docs_03_modules_domain_autonomy_core_agent_spec_blueprint_md
    docs_03_modules_domain_autonomy_core_agent_spec_blueprint_md ~~~ docs_03_modules_domain_autonomy_core_rollback_system_blueprint_md
    docs_03_modules_domain_autonomy_core_rollback_system_blueprint_md ~~~ docs_03_modules_domain_autonomy_perm_budget_enforcer_blueprint_md
    docs_03_modules_domain_autonomy_perm_budget_enforcer_blueprint_md ~~~ docs_03_modules_domain_autonomy_perm_escalation_protocol_blueprint_md
    docs_03_modules_domain_autonomy_perm_escalation_protocol_blueprint_md ~~~ docs_03_modules_domain_governance_blueprint_md
    docs_03_modules_domain_governance_blueprint_md ~~~ docs_03_modules_domain_governance_code_dedup_engine_blueprint_md
    docs_03_modules_domain_governance_code_dedup_engine_blueprint_md ~~~ docs_03_modules_domain_governance_governance_automation_blueprint_md
    docs_03_modules_domain_governance_governance_automation_blueprint_md ~~~ docs_03_modules_domain_governance_registry_governance_blueprint_md
    docs_03_modules_domain_governance_registry_governance_blueprint_md ~~~ tests_governance_d8_doc_sync_test_guc_trigger_fix_py
    tests_governance_d8_doc_sync_test_guc_trigger_fix_py ~~~ tests_governance_d8_doc_sync_test_sync_savepoint_isolation_py
    D_GOV_SCRIPTS["脚本治理<br/>脚本治理，负责脚本生命周期管理和脚本质量门禁<br/>Script Governance<br/>跨域节点 / cross-domain<br/>(生产态 / production)"]
    tests_governance_d8_doc_sync_test_guc_trigger_fix_py -->|测试依赖 / test_depends| D_GOV_SCRIPTS
    tests_governance_d8_doc_sync_test_sync_savepoint_isolation_py -->|测试依赖 / test_depends| D_GOV_SCRIPTS
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_governance_d8_doc_sync_test_guc_trigger_fix_py,tests_governance_d8_doc_sync_test_sync_savepoint_isolation_py production
    class docs_03_modules_cross_layer_auto_fix_engine_blueprint_md,docs_03_modules_cross_layer_auto_runtime_core_blueprint_md,docs_03_modules_cross_layer_behavioral_auditor_blueprint_md,docs_03_modules_cross_layer_context_engine_blueprint_md,docs_03_modules_cross_layer_database_blueprint_md,docs_03_modules_cross_layer_database_business_data_architecture_md,docs_03_modules_cross_layer_feedback_loop_blueprint_md,docs_03_modules_cross_layer_gate_engine_blueprint_md,docs_03_modules_cross_layer_model_capability_exam_blueprint_md,docs_03_modules_cross_layer_orphan_judge_blueprint_md,docs_03_modules_cross_layer_pipeline_blueprint_md,docs_03_modules_cross_layer_red_blue_validator_blueprint_md,docs_03_modules_cross_layer_resource_optimization_engine_blueprint_md,docs_03_modules_cross_layer_semantic_auditor_blueprint_md,docs_03_modules_cross_layer_shared_core_blueprint_md,docs_03_modules_domain_autonomy_core_agent_spec_blueprint_md,docs_03_modules_domain_autonomy_core_rollback_system_blueprint_md,docs_03_modules_domain_autonomy_perm_budget_enforcer_blueprint_md,docs_03_modules_domain_autonomy_perm_escalation_protocol_blueprint_md,docs_03_modules_domain_governance_blueprint_md,docs_03_modules_domain_governance_code_dedup_engine_blueprint_md,docs_03_modules_domain_governance_governance_automation_blueprint_md,docs_03_modules_domain_governance_registry_governance_blueprint_md design
    class D_GOV_SCRIPTS external_prod
```

### 运营态的图（仅 design_maturity=production 的模块和域内依赖）

> 仅展示已上线运行的模块（共 2 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    tests_governance_d8_doc_sync_test_guc_trigger_fix_py["测试guc触发器fix.py — GUC 触发器缺陷修复的端到<br/>GUC 触发器缺陷修复的端到端 smoke test<br/>（#ARCH-GUC-TRIGGER-FIX-001）<br/>test_guc_trigger_fix<br/>文件: d8_doc_sync/test_guc_trigger_fix.py<br/>(生产态 / production)"]
    tests_governance_d8_doc_sync_test_sync_savepoint_isolation_py["测试syncsavepointisolation<br/>() 级联失败隔离验证（#ARCH-GUC-TRIGGER-FIX-001<br/>裁定 B / P1）<br/>test_sync_savepoint_isolation<br/>文件: d8_doc_sync<br/>/test_sync_savepoint_isolation.py<br/>(生产态 / production)"]
    tests_governance_d8_doc_sync_test_guc_trigger_fix_py ~~~ tests_governance_d8_doc_sync_test_sync_savepoint_isolation_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_governance_d8_doc_sync_test_guc_trigger_fix_py,tests_governance_d8_doc_sync_test_sync_savepoint_isolation_py production
```

### 设计态的图（仅 design_maturity=design 的模块和域内依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 23 个），不含跨域外部节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    docs_03_modules_cross_layer_auto_fix_engine_blueprint_md["蓝图<br/>自动修复引擎的模块<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: auto_fix_engine/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_auto_runtime_core_blueprint_md["蓝图<br/>自动运行时核心蓝图，定义 MAPE-K<br/>调和循环的大脑主控，协调监控-分析-规划-执行四阶<br/>段自洽循环。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: auto_runtime_core/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_behavioral_auditor_blueprint_md["蓝图<br/>AI 行为边界审计引擎蓝图，定义 agent<br/>行为合规性审计的主控类与审计规则。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: behavioral_auditor/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_context_engine_blueprint_md["蓝图<br/>上下文引擎集成蓝图，定义上下文注入管道<br/>（build→compress→validate→inject）与 Token<br/>预算管控。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: context_engine/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_database_blueprint_md["蓝图<br/>数据库层蓝图，定义数据持久化的分层架构与访问契约<br/>。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: database/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_database_business_data_architecture_md["业务数据架构文档<br/>描述系统各业务数据的分层结构和跨层关系，是数据架<br/>构设计的顶层参考。<br/>文件: database/business_data_architecture.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_feedback_loop_blueprint_md["蓝图<br/>反馈循环蓝图，定义反馈采集-分析-提案-应用的自强<br/>化学习闭环。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: feedback_loop/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_gate_engine_blueprint_md["蓝图<br/>门禁引擎蓝图，定义门禁检查的注册、执行与阻断机制<br/>。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: gate_engine/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_model_capability_exam_blueprint_md["蓝图<br/>模型能力考试蓝图，定义五轴入职考试主控，评估模型<br/>是否具备上岗能力。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: model_capability_exam/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_orphan_judge_blueprint_md["蓝图<br/>孤儿判定引擎蓝图，定义五层判定→决策路由→安全围栏<br/>→处置建议的孤儿文件判定主控。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: orphan_judge/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_pipeline_blueprint_md["蓝图<br/>管线协调器蓝图，定义 M1-M11<br/>双管线调度核心，协调数据与执行两条管线的流转。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: pipeline/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_red_blue_validator_blueprint_md["蓝图<br/>红蓝对抗验证器蓝图，定义红队攻击与蓝队防御的对抗<br/>验证框架。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: red_blue_validator/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_resource_optimization_engine_blueprint_md["资源优化引擎蓝图<br/>定义 MAPE-K<br/>循环驱动的资源监控、分析、优化与自愈主控<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: resource_optimization_engine/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_semantic_auditor_blueprint_md["蓝图<br/>语义审计器蓝图，定义 2 类纯语义触发与 9<br/>阶段管道的语义审计主控。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: semantic_auditor/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_shared_core_blueprint_md["蓝图<br/>共享核心蓝图，定义跨域共享的基础数据结构与工具契<br/>约。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: shared_core/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_autonomy_core_agent_spec_blueprint_md["蓝图<br/>Agent 规格蓝图，定义蓝图→Skill 升级引擎，把<br/>agent 规格声明转为可执行技能。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: agent_spec/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_autonomy_core_rollback_system_blueprint_md["蓝图<br/>回滚系统蓝图，定义回滚执行器，管理回滚生命周期与<br/>变更撤销。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: rollback_system/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_autonomy_perm_budget_enforcer_blueprint_md["蓝图<br/>预算执行器蓝图，定义预算限额的检查、消耗与熔断机<br/>制。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: budget_enforcer/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_autonomy_perm_escalation_protocol_blueprint_md["蓝图<br/>升级协议蓝图，定义规则匹配→级别判定→经济护栏检查<br/>→返回 EscalationEvent 的升级流程。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: escalation_protocol/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_governance_blueprint_md["蓝图<br/>治理域蓝图，定义治理域的总体架构与各治理子域的协<br/>调关系。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: _domain_governance/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_governance_code_dedup_engine_blueprint_md["蓝图<br/>代码去重引擎蓝图，定义全生命周期七维去重的主控，<br/>检测并合并重复代码。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: code_dedup_engine/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_governance_governance_automation_blueprint_md["脚本系统蓝图 — 第三条生产线的自动化审计与门禁<br/>治理自动化蓝图，定义运行全维度或指定维度审计扫描<br/>的自动化主控。<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: governance_automation/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_domain_governance_registry_governance_blueprint_md["注册表治理<br/>蓝图，定义功能域注册表的加载、查询、重叠检测与注<br/>册管理<br/>⛔ 治理文档域，设计已就绪，等待开发排期<br/>blueprint<br/>文件: registry_governance/blueprint.md<br/>(设计态 / design)"]
    docs_03_modules_cross_layer_auto_fix_engine_blueprint_md ~~~ docs_03_modules_cross_layer_auto_runtime_core_blueprint_md
    docs_03_modules_cross_layer_auto_runtime_core_blueprint_md ~~~ docs_03_modules_cross_layer_behavioral_auditor_blueprint_md
    docs_03_modules_cross_layer_behavioral_auditor_blueprint_md ~~~ docs_03_modules_cross_layer_context_engine_blueprint_md
    docs_03_modules_cross_layer_context_engine_blueprint_md ~~~ docs_03_modules_cross_layer_database_blueprint_md
    docs_03_modules_cross_layer_database_blueprint_md ~~~ docs_03_modules_cross_layer_database_business_data_architecture_md
    docs_03_modules_cross_layer_database_business_data_architecture_md ~~~ docs_03_modules_cross_layer_feedback_loop_blueprint_md
    docs_03_modules_cross_layer_feedback_loop_blueprint_md ~~~ docs_03_modules_cross_layer_gate_engine_blueprint_md
    docs_03_modules_cross_layer_gate_engine_blueprint_md ~~~ docs_03_modules_cross_layer_model_capability_exam_blueprint_md
    docs_03_modules_cross_layer_model_capability_exam_blueprint_md ~~~ docs_03_modules_cross_layer_orphan_judge_blueprint_md
    docs_03_modules_cross_layer_orphan_judge_blueprint_md ~~~ docs_03_modules_cross_layer_pipeline_blueprint_md
    docs_03_modules_cross_layer_pipeline_blueprint_md ~~~ docs_03_modules_cross_layer_red_blue_validator_blueprint_md
    docs_03_modules_cross_layer_red_blue_validator_blueprint_md ~~~ docs_03_modules_cross_layer_resource_optimization_engine_blueprint_md
    docs_03_modules_cross_layer_resource_optimization_engine_blueprint_md ~~~ docs_03_modules_cross_layer_semantic_auditor_blueprint_md
    docs_03_modules_cross_layer_semantic_auditor_blueprint_md ~~~ docs_03_modules_cross_layer_shared_core_blueprint_md
    docs_03_modules_cross_layer_shared_core_blueprint_md ~~~ docs_03_modules_domain_autonomy_core_agent_spec_blueprint_md
    docs_03_modules_domain_autonomy_core_agent_spec_blueprint_md ~~~ docs_03_modules_domain_autonomy_core_rollback_system_blueprint_md
    docs_03_modules_domain_autonomy_core_rollback_system_blueprint_md ~~~ docs_03_modules_domain_autonomy_perm_budget_enforcer_blueprint_md
    docs_03_modules_domain_autonomy_perm_budget_enforcer_blueprint_md ~~~ docs_03_modules_domain_autonomy_perm_escalation_protocol_blueprint_md
    docs_03_modules_domain_autonomy_perm_escalation_protocol_blueprint_md ~~~ docs_03_modules_domain_governance_blueprint_md
    docs_03_modules_domain_governance_blueprint_md ~~~ docs_03_modules_domain_governance_code_dedup_engine_blueprint_md
    docs_03_modules_domain_governance_code_dedup_engine_blueprint_md ~~~ docs_03_modules_domain_governance_governance_automation_blueprint_md
    docs_03_modules_domain_governance_governance_automation_blueprint_md ~~~ docs_03_modules_domain_governance_registry_governance_blueprint_md
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000
    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_03_modules_cross_layer_auto_fix_engine_blueprint_md,docs_03_modules_cross_layer_auto_runtime_core_blueprint_md,docs_03_modules_cross_layer_behavioral_auditor_blueprint_md,docs_03_modules_cross_layer_context_engine_blueprint_md,docs_03_modules_cross_layer_database_blueprint_md,docs_03_modules_cross_layer_database_business_data_architecture_md,docs_03_modules_cross_layer_feedback_loop_blueprint_md,docs_03_modules_cross_layer_gate_engine_blueprint_md,docs_03_modules_cross_layer_model_capability_exam_blueprint_md,docs_03_modules_cross_layer_orphan_judge_blueprint_md,docs_03_modules_cross_layer_pipeline_blueprint_md,docs_03_modules_cross_layer_red_blue_validator_blueprint_md,docs_03_modules_cross_layer_resource_optimization_engine_blueprint_md,docs_03_modules_cross_layer_semantic_auditor_blueprint_md,docs_03_modules_cross_layer_shared_core_blueprint_md,docs_03_modules_domain_autonomy_core_agent_spec_blueprint_md,docs_03_modules_domain_autonomy_core_rollback_system_blueprint_md,docs_03_modules_domain_autonomy_perm_budget_enforcer_blueprint_md,docs_03_modules_domain_autonomy_perm_escalation_protocol_blueprint_md,docs_03_modules_domain_governance_blueprint_md,docs_03_modules_domain_governance_code_dedup_engine_blueprint_md,docs_03_modules_domain_governance_governance_automation_blueprint_md,docs_03_modules_domain_governance_registry_governance_blueprint_md design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | 测试guc触发器fix.py — GUC 触发器缺陷修复的端到 / test_gu... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 测试依赖 / test_depends |
| 2 | 测试syncsavepointisolation / test_sync_savepoint_isolatio... | → | D_GOV_SCRIPTS 脚本治理: 常量 / constants (_shared/constants.py) | 测试依赖 / test_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 1 个外部域直接连接（出边 2 条 + 入边 0 条 = 2 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_GOV_DOCS["D_GOV_DOCS<br/>架构文档治理"]
    D_GOV_SCRIPTS["D_GOV_SCRIPTS<br/>脚本治理"]
    D_GOV_DOCS -->|2条 测试依赖 / test_depends| D_GOV_SCRIPTS
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
