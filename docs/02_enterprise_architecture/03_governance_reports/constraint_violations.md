---
doc_type: audit_report
title: 架构约束违规报告
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 架构约束违规报告

> **文档作用 / Purpose**: 展示架构约束违规情况，包括跨层依赖、循环依赖、命名违规等，为架构治理提供修复清单。

> 本文档由 generate_constraint_violations.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) arch_constraints表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 约束总数 | 58 |
| Open（未解决） | 58 |
| Resolved（已解决） | 0 |
| 其他状态 | 0 |

## 按严重程度分组

| 严重程度 / Severity | 数量 / Count |
|---------|:---:|
| error | 1 |
| hard | 57 |

## 按约束类型分组

| 约束类型 / Constraint Type | 数量 / Count |
|---------|:---:|
| architecture_contract | 1 |
| capacity_limit | 33 |
| stability | 24 |

## Open 违规清单（需处理）

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 执行方式 / Enforcement | 描述 / Description |
|--------|------|------|------|--------|---------|---------|------|
| CONSTRAINT_D-DATA-CAPACITY_ASSURANCE | capacity_assurance稳定性约束 | stability | D_DATA_ENG |  | hard | gate | 稳定性约束：capacity_assurance |
| CONSTRAINT_D-DATA-KNOWLEDGE_MANAGEMENT | knowledge_management稳定性约束 | stability | D_DATA_ENG |  | hard | gate | 稳定性约束：knowledge_management |
| CONSTRAINT_D-DATA-PERSISTENCE | persistence稳定性约束 | stability | D_DATA_ENG |  | hard | gate | 稳定性约束：persistence |
| CONSTRAINT_D-DATA-VECTOR_STORAGE | vector_storage稳定性约束 | stability | D_DATA_ENG |  | hard | gate | 稳定性约束：vector_storage |
| CONSTRAINT_D-GOV-DRIFT_DETECTION | drift_detection稳定性约束 | stability | D_GOVERNANCE |  | hard | gate | 稳定性约束：drift_detection |
| CONSTRAINT_D-GOV-REGISTRY_MANAGEMENT | registry_management稳定性约束 | stability | D_GOVERNANCE |  | hard | gate | 稳定性约束：registry_management |
| CONSTRAINT_D-GOV-RULE_ENFORCEMENT | rule_enforcement稳定性约束 | stability | D_GOVERNANCE |  | hard | gate | 稳定性约束：rule_enforcement |
| CONSTRAINT_D-GOV-SCRIPT_GOVERNANCE | script_governance稳定性约束 | stability | D_GOVERNANCE |  | hard | gate | 稳定性约束：script_governance |
| CONSTRAINT_D-GOV-SEMANTIC_AUDIT | semantic_audit稳定性约束 | stability | D_GOVERNANCE |  | hard | gate | 稳定性约束：semantic_audit |
| CONSTRAINT_D-INFRA-LIFECYCLE_MANAGEMENT | lifecycle_management稳定性约束 | stability | D_INFRA_RUNTIME |  | hard | gate | 稳定性约束：lifecycle_management |
| CONSTRAINT_D-INFRA-RESOURCE_OPTIMIZATION | resource_optimization稳定性约束 | stability | D_INFRA_RUNTIME |  | hard | gate | 稳定性约束：resource_optimization |
| CONSTRAINT_D-INFRA-RUNTIME_INTEGRATION | runtime_integration稳定性约束 | stability | D_INFRA_RUNTIME |  | hard | gate | 稳定性约束：runtime_integration |
| CONSTRAINT_D-INFRA-SHARED_SERVICES | shared_services稳定性约束 | stability | D_INFRA_RUNTIME |  | hard | gate | 稳定性约束：shared_services |
| CONSTRAINT_D-INTEL-MODEL_PROFILING | model_profiling稳定性约束 | stability | D_INTELLIGENCE |  | hard | gate | 稳定性约束：model_profiling |
| CONSTRAINT_D-OBS-AUDIT_TRAIL | audit_trail稳定性约束 | stability | D_OPS |  | hard | gate | 稳定性约束：audit_trail |
| CONSTRAINT_D-OBS-TELEMETRY | telemetry稳定性约束 | stability | D_OPS |  | hard | gate | 稳定性约束：telemetry |
| CONSTRAINT_D-ORCH-AGENT_LIFECYCLE | agent_lifecycle稳定性约束 | stability | D_AUTONOMY_CORE |  | hard | gate | 稳定性约束：agent_lifecycle |
| CONSTRAINT_D-ORCH-RUNTIME_CORE | runtime_core稳定性约束 | stability | D_AUTONOMY_CORE |  | hard | gate | 稳定性约束：runtime_core |
| CONSTRAINT_D-RES-ESCALATION | escalation稳定性约束 | stability | D_OPS |  | hard | gate | 稳定性约束：escalation |
| CONSTRAINT_D-RES-ROLLBACK | rollback稳定性约束 | stability | D_OPS |  | hard | gate | 稳定性约束：rollback |
| CONSTRAINT_D-SEC-ACCESS_CONTROL | access_control稳定性约束 | stability | D_SECURITY |  | hard | gate | 稳定性约束：access_control |
| CONSTRAINT_D-SEC-ADVERSARIAL_VALIDATION | adversarial_validation稳定性约束 | stability | D_SECURITY |  | hard | gate | 稳定性约束：adversarial_validation |
| CONSTRAINT_D-SEC-LLM_DEFENSE | llm_defense稳定性约束 | stability | D_SECURITY |  | hard | gate | 稳定性约束：llm_defense |
| CONSTRAINT_D-TEST-CODE_DEDUP | code_dedup稳定性约束 | stability | D_GOVERNANCE |  | hard | gate | 稳定性约束：code_dedup |
| F1-CAPACITY-D-ALT_DATA | 容量超限告警: D-ALT_DATA | capacity_limit | D_ALT_DATA |  | hard | gate | 域D-ALT_DATA(另类数据)当前117模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-AUTONOMY_CORE | 容量超限告警: D-AUTONOMY_CORE | capacity_limit | D_AUTONOMY_CORE |  | hard | gate | 域D-AUTONOMY_CORE(自治核心)当前225模块超过上限180，需拆分或提升上限 |
| F1-CAPACITY-D-AUTONOMY_PERM | 容量超限告警: D-AUTONOMY_PERM | capacity_limit | D_AUTONOMY_PERM |  | hard | gate | 域D-AUTONOMY_PERM(自治保护)当前236模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-COMPLIANCE | 容量超限告警: D-COMPLIANCE | capacity_limit | D_COMPLIANCE |  | hard | gate | 域D-COMPLIANCE(合规)当前972模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-CROSS_ASSET | 容量超限告警: D-CROSS_ASSET | capacity_limit | D_CROSS_ASSET |  | hard | gate | 域D-CROSS_ASSET(跨资产)当前82模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-DATA_ENG | 容量超限告警: D-DATA_ENG | capacity_limit | D_DATA_ENG |  | hard | gate | 域D-DATA_ENG(数据工程(增值+融合+知识))当前201模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-DATA_GOV | 容量超限告警: D-DATA_GOV | capacity_limit | D_DATA_GOV |  | hard | gate | 域D-DATA_GOV(数据治理(质量+血缘+参考))当前62模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-EX_CORE | 容量超限告警: D-EX_CORE | capacity_limit | D_EX_CORE |  | hard | gate | 域D-EX_CORE(执行核心)当前186模块超过上限80，需拆分或提升上限 |
| F1-CAPACITY-D-EX_SOR | 容量超限告警: D-EX_SOR | capacity_limit | D_EX_SOR |  | hard | gate | 域D-EX_SOR(执行路由)当前168模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-FACTOR | 容量超限告警: D-FACTOR | capacity_limit | D_FACTOR |  | hard | gate | 域D-FACTOR(因子)当前104模块超过上限80，需拆分或提升上限 |
| F1-CAPACITY-D-FRONTEND | 容量超限告警: D-FRONTEND | capacity_limit | D_FRONTEND |  | hard | gate | 域D-FRONTEND(前端)当前278模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-GOVERNANCE | 容量超限告警: D-GOVERNANCE | capacity_limit | D_GOVERNANCE |  | hard | gate | 域D-GOVERNANCE(治理)当前2881模块超过上限750，需拆分或提升上限 |
| F1-CAPACITY-D-GOV_SCRIPTS | 容量超限告警: D-GOV_SCRIPTS | capacity_limit | D_GOVERNANCE |  | hard | gate | 域D-GOV_SCRIPTS(治理脚本)当前359模块超过上限340，需拆分或提升上限 |
| F1-CAPACITY-D-INFRA_OPS | 容量超限告警: D-INFRA_OPS | capacity_limit | D_INFRA_OPS |  | hard | gate | 域D-INFRA_OPS(基础设施运维)当前409模块超过上限40，需拆分或提升上限 |
| F1-CAPACITY-D-INFRA_RUNTIME | 容量超限告警: D-INFRA_RUNTIME | capacity_limit | D_INFRA_RUNTIME |  | hard | gate | 域D-INFRA_RUNTIME(运行时基础设施)当前892模块超过上限480，需拆分或提升上限 |
| F1-CAPACITY-D-INTEGRATION | 容量超限告警: D-INTEGRATION | capacity_limit | D_INTEGRATION |  | hard | gate | 域D-INTEGRATION(集成)当前314模块超过上限220，需拆分或提升上限 |
| F1-CAPACITY-D-INTELLIGENCE | 容量超限告警: D-INTELLIGENCE | capacity_limit | D_INTELLIGENCE |  | hard | gate | 域D-INTELLIGENCE(智能)当前322模块超过上限80，需拆分或提升上限 |
| F1-CAPACITY-D-KNOWLEDGE | 容量超限告警: D-KNOWLEDGE | capacity_limit | D_KNOWLEDGE |  | hard | gate | 域D-KNOWLEDGE(知识)当前209模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-MKT_DATA | 容量超限告警: D-MKT_DATA | capacity_limit | D_MKT_DATA |  | hard | gate | 域D-MKT_DATA(行情数据(接入+存储))当前109模块超过上限80，需拆分或提升上限 |
| F1-CAPACITY-D-ML_SERVE | 容量超限告警: D-ML_SERVE | capacity_limit | D_ML_SERVE |  | hard | gate | 域D-ML_SERVE(推理)当前77模块超过上限40，需拆分或提升上限 |
| F1-CAPACITY-D-ML_TRAIN | 容量超限告警: D-ML_TRAIN | capacity_limit | D_ML_TRAIN |  | hard | gate | 域D-ML_TRAIN(训练)当前166模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-OPS | 容量超限告警: D-OPS | capacity_limit | D_OPS |  | hard | gate | 域D-OPS(运维)当前453模块超过上限380，需拆分或提升上限 |
| F1-CAPACITY-D-PF_ALLOC | 容量超限告警: D-PF_ALLOC | capacity_limit | D_PF_ALLOC |  | hard | gate | 域D-PF_ALLOC(组合分配)当前120模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-PF_CORE | 容量超限告警: D-PF_CORE | capacity_limit | D_PF_CORE |  | hard | gate | 域D-PF_CORE(组合核心)当前246模块超过上限80，需拆分或提升上限 |
| F1-CAPACITY-D-POSITION | 容量超限告警: D-POSITION | capacity_limit | D_POSITION |  | hard | gate | 域D-POSITION(仓位管理)当前127模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-REPORTING | 容量超限告警: D-REPORTING | capacity_limit | D_REPORTING |  | hard | gate | 域D-REPORTING(报告)当前170模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-RISK | 容量超限告警: D-RISK | capacity_limit | D_RISK |  | hard | gate | 域D-RISK(风控)当前150模块超过上限100，需拆分或提升上限 |
| F1-CAPACITY-D-SECURITY | 容量超限告警: D-SECURITY | capacity_limit | D_SECURITY |  | hard | gate | 域D-SECURITY(安全)当前341模块超过上限320，需拆分或提升上限 |
| F1-CAPACITY-D-SELL_DECISION | 容量超限告警: D-SELL_DECISION | capacity_limit | D_SELL_DECISION |  | hard | gate | 域D-SELL_DECISION(卖出决策)当前94模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-SHARED | 容量超限告警: D-SHARED | capacity_limit | D_SHARED |  | hard | gate | 域D-SHARED(共享)当前275模块超过上限210，需拆分或提升上限 |
| F1-CAPACITY-D-SIGLEGACY | 容量超限告警: D-SIGLEGACY | capacity_limit | D_SIGLEGACY |  | hard | gate | 域D-SIGLEGACY(信号(技术+通用))当前135模块超过上限80，需拆分或提升上限 |
| F1-CAPACITY-D-SIMULATION | 容量超限告警: D-SIMULATION | capacity_limit | D_SIMULATION |  | hard | gate | 域D-SIMULATION(仿真)当前92模块超过上限60，需拆分或提升上限 |
| F1-CAPACITY-D-TRADING | 容量超限告警: D-TRADING | capacity_limit | D_TRADING |  | hard | gate | 域D-TRADING(交易运营)当前163模块超过上限140，需拆分或提升上限 |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | code |  |

## 完整约束清单

| 约束ID / Constraint ID | 名称 / Name | 类型 / Type | 源域 / From Domain | 目标域 / To Domain | 严重程度 / Severity | 状态 / Status |
|--------|------|------|------|--------|---------|------|
| CONSTRAINT_D-DATA-CAPACITY_ASSURANCE | capacity_assurance稳定性约束 | stability | D_DATA_ENG |  | hard | open |
| CONSTRAINT_D-DATA-KNOWLEDGE_MANAGEMENT | knowledge_management稳定性约束 | stability | D_DATA_ENG |  | hard | open |
| CONSTRAINT_D-DATA-PERSISTENCE | persistence稳定性约束 | stability | D_DATA_ENG |  | hard | open |
| CONSTRAINT_D-DATA-VECTOR_STORAGE | vector_storage稳定性约束 | stability | D_DATA_ENG |  | hard | open |
| CONSTRAINT_D-GOV-DRIFT_DETECTION | drift_detection稳定性约束 | stability | D_GOVERNANCE |  | hard | open |
| CONSTRAINT_D-GOV-REGISTRY_MANAGEMENT | registry_management稳定性约束 | stability | D_GOVERNANCE |  | hard | open |
| CONSTRAINT_D-GOV-RULE_ENFORCEMENT | rule_enforcement稳定性约束 | stability | D_GOVERNANCE |  | hard | open |
| CONSTRAINT_D-GOV-SCRIPT_GOVERNANCE | script_governance稳定性约束 | stability | D_GOVERNANCE |  | hard | open |
| CONSTRAINT_D-GOV-SEMANTIC_AUDIT | semantic_audit稳定性约束 | stability | D_GOVERNANCE |  | hard | open |
| CONSTRAINT_D-INFRA-LIFECYCLE_MANAGEMENT | lifecycle_management稳定性约束 | stability | D_INFRA_RUNTIME |  | hard | open |
| CONSTRAINT_D-INFRA-RESOURCE_OPTIMIZATION | resource_optimization稳定性约束 | stability | D_INFRA_RUNTIME |  | hard | open |
| CONSTRAINT_D-INFRA-RUNTIME_INTEGRATION | runtime_integration稳定性约束 | stability | D_INFRA_RUNTIME |  | hard | open |
| CONSTRAINT_D-INFRA-SHARED_SERVICES | shared_services稳定性约束 | stability | D_INFRA_RUNTIME |  | hard | open |
| CONSTRAINT_D-INTEL-MODEL_PROFILING | model_profiling稳定性约束 | stability | D_INTELLIGENCE |  | hard | open |
| CONSTRAINT_D-OBS-AUDIT_TRAIL | audit_trail稳定性约束 | stability | D_OPS |  | hard | open |
| CONSTRAINT_D-OBS-TELEMETRY | telemetry稳定性约束 | stability | D_OPS |  | hard | open |
| CONSTRAINT_D-ORCH-AGENT_LIFECYCLE | agent_lifecycle稳定性约束 | stability | D_AUTONOMY_CORE |  | hard | open |
| CONSTRAINT_D-ORCH-RUNTIME_CORE | runtime_core稳定性约束 | stability | D_AUTONOMY_CORE |  | hard | open |
| CONSTRAINT_D-RES-ESCALATION | escalation稳定性约束 | stability | D_OPS |  | hard | open |
| CONSTRAINT_D-RES-ROLLBACK | rollback稳定性约束 | stability | D_OPS |  | hard | open |
| CONSTRAINT_D-SEC-ACCESS_CONTROL | access_control稳定性约束 | stability | D_SECURITY |  | hard | open |
| CONSTRAINT_D-SEC-ADVERSARIAL_VALIDATION | adversarial_validation稳定性约束 | stability | D_SECURITY |  | hard | open |
| CONSTRAINT_D-SEC-LLM_DEFENSE | llm_defense稳定性约束 | stability | D_SECURITY |  | hard | open |
| CONSTRAINT_D-TEST-CODE_DEDUP | code_dedup稳定性约束 | stability | D_GOVERNANCE |  | hard | open |
| F1-CAPACITY-D-ALT_DATA | 容量超限告警: D-ALT_DATA | capacity_limit | D_ALT_DATA |  | hard | open |
| F1-CAPACITY-D-AUTONOMY_CORE | 容量超限告警: D-AUTONOMY_CORE | capacity_limit | D_AUTONOMY_CORE |  | hard | open |
| F1-CAPACITY-D-AUTONOMY_PERM | 容量超限告警: D-AUTONOMY_PERM | capacity_limit | D_AUTONOMY_PERM |  | hard | open |
| F1-CAPACITY-D-COMPLIANCE | 容量超限告警: D-COMPLIANCE | capacity_limit | D_COMPLIANCE |  | hard | open |
| F1-CAPACITY-D-CROSS_ASSET | 容量超限告警: D-CROSS_ASSET | capacity_limit | D_CROSS_ASSET |  | hard | open |
| F1-CAPACITY-D-DATA_ENG | 容量超限告警: D-DATA_ENG | capacity_limit | D_DATA_ENG |  | hard | open |
| F1-CAPACITY-D-DATA_GOV | 容量超限告警: D-DATA_GOV | capacity_limit | D_DATA_GOV |  | hard | open |
| F1-CAPACITY-D-EX_CORE | 容量超限告警: D-EX_CORE | capacity_limit | D_EX_CORE |  | hard | open |
| F1-CAPACITY-D-EX_SOR | 容量超限告警: D-EX_SOR | capacity_limit | D_EX_SOR |  | hard | open |
| F1-CAPACITY-D-FACTOR | 容量超限告警: D-FACTOR | capacity_limit | D_FACTOR |  | hard | open |
| F1-CAPACITY-D-FRONTEND | 容量超限告警: D-FRONTEND | capacity_limit | D_FRONTEND |  | hard | open |
| F1-CAPACITY-D-GOVERNANCE | 容量超限告警: D-GOVERNANCE | capacity_limit | D_GOVERNANCE |  | hard | open |
| F1-CAPACITY-D-GOV_SCRIPTS | 容量超限告警: D-GOV_SCRIPTS | capacity_limit | D_GOVERNANCE |  | hard | open |
| F1-CAPACITY-D-INFRA_OPS | 容量超限告警: D-INFRA_OPS | capacity_limit | D_INFRA_OPS |  | hard | open |
| F1-CAPACITY-D-INFRA_RUNTIME | 容量超限告警: D-INFRA_RUNTIME | capacity_limit | D_INFRA_RUNTIME |  | hard | open |
| F1-CAPACITY-D-INTEGRATION | 容量超限告警: D-INTEGRATION | capacity_limit | D_INTEGRATION |  | hard | open |
| F1-CAPACITY-D-INTELLIGENCE | 容量超限告警: D-INTELLIGENCE | capacity_limit | D_INTELLIGENCE |  | hard | open |
| F1-CAPACITY-D-KNOWLEDGE | 容量超限告警: D-KNOWLEDGE | capacity_limit | D_KNOWLEDGE |  | hard | open |
| F1-CAPACITY-D-MKT_DATA | 容量超限告警: D-MKT_DATA | capacity_limit | D_MKT_DATA |  | hard | open |
| F1-CAPACITY-D-ML_SERVE | 容量超限告警: D-ML_SERVE | capacity_limit | D_ML_SERVE |  | hard | open |
| F1-CAPACITY-D-ML_TRAIN | 容量超限告警: D-ML_TRAIN | capacity_limit | D_ML_TRAIN |  | hard | open |
| F1-CAPACITY-D-OPS | 容量超限告警: D-OPS | capacity_limit | D_OPS |  | hard | open |
| F1-CAPACITY-D-PF_ALLOC | 容量超限告警: D-PF_ALLOC | capacity_limit | D_PF_ALLOC |  | hard | open |
| F1-CAPACITY-D-PF_CORE | 容量超限告警: D-PF_CORE | capacity_limit | D_PF_CORE |  | hard | open |
| F1-CAPACITY-D-POSITION | 容量超限告警: D-POSITION | capacity_limit | D_POSITION |  | hard | open |
| F1-CAPACITY-D-REPORTING | 容量超限告警: D-REPORTING | capacity_limit | D_REPORTING |  | hard | open |
| F1-CAPACITY-D-RISK | 容量超限告警: D-RISK | capacity_limit | D_RISK |  | hard | open |
| F1-CAPACITY-D-SECURITY | 容量超限告警: D-SECURITY | capacity_limit | D_SECURITY |  | hard | open |
| F1-CAPACITY-D-SELL_DECISION | 容量超限告警: D-SELL_DECISION | capacity_limit | D_SELL_DECISION |  | hard | open |
| F1-CAPACITY-D-SHARED | 容量超限告警: D-SHARED | capacity_limit | D_SHARED |  | hard | open |
| F1-CAPACITY-D-SIGLEGACY | 容量超限告警: D-SIGLEGACY | capacity_limit | D_SIGLEGACY |  | hard | open |
| F1-CAPACITY-D-SIMULATION | 容量超限告警: D-SIMULATION | capacity_limit | D_SIMULATION |  | hard | open |
| F1-CAPACITY-D-TRADING | 容量超限告警: D-TRADING | capacity_limit | D_TRADING |  | hard | open |
|  | procedural policy 必须可验证（不能是 inspection） | architecture_contract |  |  | error | open |
