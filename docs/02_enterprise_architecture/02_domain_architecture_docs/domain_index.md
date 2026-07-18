---
doc_type: index
title: 域总览索引
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 域总览索引

> **文档作用 / Purpose**: 列出所有功能域的编号、ID、名称、层级、模块数等基本信息，是域架构文档的入口索引。

> 本文档由 generate_domain_index.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) domains表 + nodes表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 63 |
| 模块总数 | 2673 |
| 生产态模块 | 1566 |
| 设计态模块 | 62 |
| 原型态模块 | 1045 |

## 域清单（按架构层分组）

### L0 基础设施层 / L0 Infrastructure (5 个域 / 5 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_INFRA_A2A | a2a_communication / A2A Communication | 72 | 28 | 0 | 44 | 72/150 (OK) | [01_d_infra_a2a.md](01_d_infra_a2a.md) |
| D_INFRA_OPS | asset-inventory / Asset Inventory | 2 | 0 | 2 | 0 | 2/150 (OK) | [02_d_infra_ops.md](02_d_infra_ops.md) |
| D_INFRA_RECOVERY | rollback_recovery / Rollback Recovery | 54 | 48 | 0 | 6 | 54/150 (OK) | [03_d_infra_recovery.md](03_d_infra_recovery.md) |
| D_INFRA_RUNTIME | runtime_core / Runtime Integration | 159 | 118 | 1 | 40 | 159/150 (超容) | [04_d_infra_runtime.md](04_d_infra_runtime.md) |
| D_INFRA_TELEMETRY | observability_profiling / Observability | 0 | 0 | 0 | 0 | 0/150 (OK) | [05_d_infra_telemetry.md](05_d_infra_telemetry.md) |

### L1 基础平台层 / L1 Foundation (21 个域 / 21 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_ALT_DATA | 另类数据 / Alternative Data | 7 | 0 | 0 | 7 | 7/150 (OK) | [06_d_alt_data.md](06_d_alt_data.md) |
| D_AUTONOMY_CORE | agent_lifecycle / Autonomy Core | 137 | 131 | 0 | 6 | 137/150 (OK) | [07_d_autonomy_core.md](07_d_autonomy_core.md) |
| D_DATA_ENG | 数据工程 / Data Engineering | 7 | 0 | 0 | 7 | 7/150 (OK) | [08_d_data_eng.md](08_d_data_eng.md) |
| D_DATA_GOV | 数据治理 / Data Governance | 7 | 0 | 0 | 7 | 7/150 (OK) | [09_d_data_gov.md](09_d_data_gov.md) |
| D_DATA_SEC | 数据安全与契约 / Data Security & Contracts | 7 | 0 | 0 | 7 | 7/150 (OK) | [10_d_data_sec.md](10_d_data_sec.md) |
| D_FBL_DETECTORS | feedback_detectors / Feedback Detectors | 65 | 59 | 0 | 6 | 65/150 (OK) | [11_d_fbl_detectors.md](11_d_fbl_detectors.md) |
| D_FBL_DIAGNOSERS | feedback_diagnosers / Feedback Diagnosers | 76 | 71 | 0 | 5 | 76/150 (OK) | [12_d_fbl_diagnosers.md](12_d_fbl_diagnosers.md) |
| D_FBL_VERIFICATION | feedback_verification / Feedback Verification | 71 | 67 | 0 | 4 | 71/150 (OK) | [13_d_fbl_verification.md](13_d_fbl_verification.md) |
| D_FEEDBACK_LOOP | feedback_loop_engine / Feedback Loop Engine | 124 | 112 | 0 | 12 | 124/150 (OK) | [14_d_feedback_loop.md](14_d_feedback_loop.md) |
| D_FRONTEND | 前端 / Frontend | 18 | 9 | 6 | 3 | 18/150 (OK) | [15_d_frontend.md](15_d_frontend.md) |
| D_GOV_CODE_QUALITY | code_quality_governance / Code Quality Governance | 128 | 112 | 0 | 16 | 128/150 (OK) | [16_d_gov_code_quality.md](16_d_gov_code_quality.md) |
| D_GOV_OPS_RESILIENCE | ops_resilience_governance / Ops Resilience Governance | 90 | 81 | 0 | 9 | 90/150 (OK) | [17_d_gov_ops_resilience.md](17_d_gov_ops_resilience.md) |
| D_INTEGRATION | pipeline_routing / Pipeline Routing | 72 | 45 | 0 | 27 | 72/150 (OK) | [18_d_integration.md](18_d_integration.md) |
| D_INTEGRATION_GATEWAY | mcp_servers / Integration Gateway | 0 | 0 | 0 | 0 | 0/150 (OK) | [19_d_integration_gateway.md](19_d_integration_gateway.md) |
| D_MKT_DATA | 行情数据 / Market Data | 10 | 0 | 3 | 7 | 10/150 (OK) | [20_d_mkt_data.md](20_d_mkt_data.md) |
| D_OPS | telemetry / Feedback Loop | 9 | 8 | 0 | 1 | 9/150 (OK) | [21_d_ops.md](21_d_ops.md) |
| D_ORCHESTRATOR | agent_orchestrator / Agent Orchestrator | 72 | 58 | 0 | 14 | 72/150 (OK) | [22_d_orchestrator.md](22_d_orchestrator.md) |
| D_REPORTING | 报告 / Reporting | 3 | 1 | 0 | 2 | 3/150 (OK) | [23_d_reporting.md](23_d_reporting.md) |
| D_SECURITY | orphan_judge / Adversarial Validation | 165 | 99 | 0 | 66 | 165/150 (超容) | [24_d_security.md](24_d_security.md) |
| D_SECURITY_LLM | llm_defense / LLM Defense | 0 | 0 | 0 | 0 | 0/150 (OK) | [25_d_security_llm.md](25_d_security_llm.md) |
| D_SHARED | shared_services / Shared Services | 184 | 115 | 0 | 69 | 184/150 (超容) | [26_d_shared.md](26_d_shared.md) |

### L2 业务域层 / L2 Domain (32 个域 / 32 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_ASHARE_SIGNAL | ashare_signal / A-Share Signal | 7 | 0 | 0 | 7 | 7/150 (OK) | [27_d_ashare_signal.md](27_d_ashare_signal.md) |
| D_AUDITTEST | audit_test_suite / Audit Test Suite | 1 | 1 | 0 | 0 | 1/150 (OK) | [28_d_audittest.md](28_d_audittest.md) |
| D_AUTONOMY_PERM | budget_enforcement / Autonomy Protection | 2 | 0 | 0 | 2 | 2/150 (OK) | [29_d_autonomy_perm.md](29_d_autonomy_perm.md) |
| D_BACKTEST | 回测 / Backtest | 25 | 9 | 8 | 8 | 25/150 (OK) | [30_d_backtest.md](30_d_backtest.md) |
| D_CROSS_ASSET | 跨资产 / Cross Asset | 8 | 0 | 1 | 7 | 8/150 (OK) | [31_d_cross_asset.md](31_d_cross_asset.md) |
| D_DIGITAL_TWIN | 数字孪生 / Digital Twin | 8 | 0 | 1 | 7 | 8/150 (OK) | [32_d_digital_twin.md](32_d_digital_twin.md) |
| D_EXEC_SIM | 执行仿真 / Execution Simulation | 7 | 0 | 0 | 7 | 7/150 (OK) | [33_d_exec_sim.md](33_d_exec_sim.md) |
| D_EX_CORE | 执行核心 / Execution Core | 8 | 4 | 1 | 3 | 8/150 (OK) | [34_d_ex_core.md](34_d_ex_core.md) |
| D_EX_SOR | 执行路由 / Execution Routing | 7 | 0 | 0 | 7 | 7/150 (OK) | [35_d_ex_sor.md](35_d_ex_sor.md) |
| D_FACTOR | 因子 / Factor | 5 | 2 | 0 | 3 | 5/150 (OK) | [36_d_factor.md](36_d_factor.md) |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal / Fundamental Signal | 10 | 4 | 0 | 6 | 10/150 (OK) | [37_d_fundamental_signal.md](37_d_fundamental_signal.md) |
| D_GOVERNANCE | registry_management / Lifecycle Management | 213 | 96 | 1 | 116 | 213/150 (超容) | [38_d_governance.md](38_d_governance.md) |
| D_GOV_AUDIT | audit_orchestration / Audit Trail | 100 | 67 | 2 | 31 | 100/150 (OK) | [39_d_gov_audit.md](39_d_gov_audit.md) |
| D_GOV_DOCS | architecture_docs / Architecture Docs Governance | 28 | 0 | 28 | 0 | 28/150 (OK) | [40_d_gov_docs.md](40_d_gov_docs.md) |
| D_GOV_DRIFT | drift_detection / Drift Detection | 74 | 70 | 1 | 3 | 74/150 (OK) | [41_d_gov_drift.md](41_d_gov_drift.md) |
| D_GOV_ENFORCEMENT | rule_enforcement / Rule Enforcement | 31 | 15 | 0 | 16 | 31/150 (OK) | [42_d_gov_enforcement.md](42_d_gov_enforcement.md) |
| D_GOV_KB | knowledge_base_governance / Knowledge Base Governance | 31 | 18 | 0 | 13 | 31/150 (OK) | [43_d_gov_kb.md](43_d_gov_kb.md) |
| D_GOV_REPAIR | rollback / Governance Repair | 1 | 1 | 0 | 0 | 1/200 (OK) | [44_d_gov_repair.md](44_d_gov_repair.md) |
| D_GOV_RULE | rule_governance / Rule Governance | 35 | 31 | 0 | 4 | 35/200 (OK) | [45_d_gov_rule.md](45_d_gov_rule.md) |
| D_GOV_SCRIPTS | script_governance / Script Governance | 356 | 10 | 2 | 344 | 356/150 (超容) | [46_d_gov_scripts.md](46_d_gov_scripts.md) |
| D_INTELLIGENCE | context_management / Context Management | 30 | 21 | 0 | 9 | 30/150 (OK) | [47_d_intelligence.md](47_d_intelligence.md) |
| D_KNOWLEDGE | vector_storage / Knowledge Management | 4 | 0 | 2 | 2 | 4/150 (OK) | [48_d_knowledge.md](48_d_knowledge.md) |
| D_ML_SERVE | 推理 / Inference | 7 | 0 | 0 | 7 | 7/150 (OK) | [49_d_ml_serve.md](49_d_ml_serve.md) |
| D_ML_TRAIN | model_evaluation / Training | 4 | 0 | 1 | 3 | 4/150 (OK) | [50_d_ml_train.md](50_d_ml_train.md) |
| D_PF_ALLOC | 组合分配 / Portfolio Allocation | 3 | 1 | 1 | 1 | 3/150 (OK) | [51_d_pf_alloc.md](51_d_pf_alloc.md) |
| D_PF_CORE | 组合核心 / Portfolio Core | 1 | 0 | 0 | 1 | 1/150 (OK) | [52_d_pf_core.md](52_d_pf_core.md) |
| D_POSITION | 仓位管理 / Position Management | 1 | 1 | 0 | 0 | 1/150 (OK) | [53_d_position.md](53_d_position.md) |
| D_RISK | 风控 / Risk Control | 11 | 9 | 0 | 2 | 11/150 (OK) | [54_d_risk.md](54_d_risk.md) |
| D_SELL_DECISION | 卖出决策 / Sell Decision | 7 | 0 | 0 | 7 | 7/150 (OK) | [55_d_sell_decision.md](55_d_sell_decision.md) |
| D_SIGQC | signal_quality / Signal Quality Control | 2 | 0 | 0 | 2 | 2/150 (OK) | [56_d_sigqc.md](56_d_sigqc.md) |
| D_SIMULATION | 仿真 / Simulation | 3 | 2 | 1 | 0 | 3/150 (OK) | [57_d_simulation.md](57_d_simulation.md) |
| D_TRADING | 交易运营 / Trading Operations | 32 | 21 | 0 | 11 | 32/150 (OK) | [58_d_trading.md](58_d_trading.md) |

### 未分类 / 未分类 (5 个域 / 5 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_BEHAVIORAL_AUDIT | drift_detector_core / Behavioral Audit | 0 | 0 | 0 | 0 | 0/200 (OK) | [59_d_behavioral_audit.md](59_d_behavioral_audit.md) |
| D_COMPLIANCE | compliance_gate / Compliance | 4 | 0 | 0 | 4 | 4/200 (OK) | [60_d_compliance.md](60_d_compliance.md) |
| D_DATA | data_source_integrator / D_DATA | 42 | 9 | 0 | 33 | 42/200 (OK) | [61_d_data.md](61_d_data.md) |
| D_INFRASTRUCTURE | shared_contracts / D_INFRASTRUCTURE | 26 | 12 | 0 | 14 | 26/200 (OK) | [62_d_infrastructure.md](62_d_infrastructure.md) |
| D_SIGLEGACY | signal_legacy / Signal Legacy (Design) | 0 | 0 | 0 | 0 | 0/200 (OK) | [63_d_siglegacy.md](63_d_siglegacy.md) |
