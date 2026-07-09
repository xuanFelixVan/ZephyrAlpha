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
| 域总数 | 50 |
| 模块总数 | 5023 |
| 生产态模块 | 1621 |
| 设计态模块 | 54 |
| 原型态模块 | 3348 |

## 域清单（按架构层分组）

### L0 基础设施层 / L0 Infrastructure (5 个域 / 5 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_INFRA_A2A | a2a_communication / A2A Communication | 89 | 32 | 0 | 57 | 89/150 (OK) | [01_d_infra_a2a.md](01_d_infra_a2a.md) |
| D_INFRA_OPS | asset-inventory / Asset Inventory | 1 | 0 | 1 | 0 | 1/150 (OK) | [02_d_infra_ops.md](02_d_infra_ops.md) |
| D_INFRA_RECOVERY | rollback_recovery / Rollback Recovery | 54 | 48 | 0 | 6 | 54/150 (OK) | [03_d_infra_recovery.md](03_d_infra_recovery.md) |
| D_INFRA_RUNTIME | runtime_core / Runtime Integration | 132 | 87 | 0 | 45 | 132/150 (OK) | [04_d_infra_runtime.md](04_d_infra_runtime.md) |
| D_INFRA_TELEMETRY | observability_profiling / Observability | 25 | 13 | 0 | 12 | 25/150 (OK) | [05_d_infra_telemetry.md](05_d_infra_telemetry.md) |

### L1 基础平台层 / L1 Foundation (14 个域 / 14 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_ALT_DATA | 另类数据 / Alternative Data | 7 | 0 | 0 | 7 | 7/150 (OK) | [06_d_alt_data.md](06_d_alt_data.md) |
| D_AUTONOMY_CORE | agent_lifecycle / Autonomy Core | 114 | 111 | 0 | 3 | 114/150 (OK) | [07_d_autonomy_core.md](07_d_autonomy_core.md) |
| D_DATA_ENG | 数据工程 / Data Engineering | 7 | 0 | 0 | 7 | 7/150 (OK) | [08_d_data_eng.md](08_d_data_eng.md) |
| D_DATA_GOV | 数据治理 / Data Governance | 7 | 0 | 0 | 7 | 7/150 (OK) | [09_d_data_gov.md](09_d_data_gov.md) |
| D_DATA_SEC | 数据安全与契约 / Data Security & Contracts | 7 | 0 | 0 | 7 | 7/150 (OK) | [10_d_data_sec.md](10_d_data_sec.md) |
| D_FRONTEND | 前端 / Frontend | 30 | 13 | 6 | 11 | 30/150 (OK) | [11_d_frontend.md](11_d_frontend.md) |
| D_INTEGRATION | pipeline_routing / Pipeline Routing | 72 | 33 | 0 | 39 | 72/150 (OK) | [12_d_integration.md](12_d_integration.md) |
| D_INTEGRATION_GATEWAY | mcp_servers / Integration Gateway | 20 | 14 | 0 | 6 | 20/150 (OK) | [13_d_integration_gateway.md](13_d_integration_gateway.md) |
| D_MKT_DATA | 行情数据 / Market Data | 7 | 0 | 0 | 7 | 7/150 (OK) | [14_d_mkt_data.md](14_d_mkt_data.md) |
| D_OPS | telemetry / Feedback Loop | 3 | 3 | 0 | 0 | 3/150 (OK) | [15_d_ops.md](15_d_ops.md) |
| D_REPORTING | 报告 / Reporting | 10 | 1 | 0 | 9 | 10/150 (OK) | [16_d_reporting.md](16_d_reporting.md) |
| D_SECURITY | orphan_judge / Adversarial Validation | 147 | 80 | 0 | 67 | 147/150 (OK) | [17_d_security.md](17_d_security.md) |
| D_SECURITY_LLM | llm_defense / LLM Defense | 44 | 33 | 0 | 11 | 44/150 (OK) | [18_d_security_llm.md](18_d_security_llm.md) |
| D_SHARED | shared_services / Shared Services | 225 | 94 | 0 | 131 | 225/150 (超容) | [19_d_shared.md](19_d_shared.md) |

### L2 业务域层 / L2 Domain (31 个域 / 31 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_ASHARE_SIGNAL | ashare_signal / A-Share Signal | 7 | 0 | 0 | 7 | 7/150 (OK) | [20_d_ashare_signal.md](20_d_ashare_signal.md) |
| D_AUDITTEST | audit_test_suite / Audit Test Suite | 1752 | 49 | 0 | 1703 | 1752/150 (超容) | [21_d_audittest.md](21_d_audittest.md) |
| D_AUTONOMY_PERM | budget_enforcement / Autonomy Protection | 14 | 0 | 0 | 14 | 14/150 (OK) | [22_d_autonomy_perm.md](22_d_autonomy_perm.md) |
| D_BACKTEST | 回测 / Backtest | 33 | 9 | 8 | 16 | 33/150 (OK) | [23_d_backtest.md](23_d_backtest.md) |
| D_CROSS_ASSET | 跨资产 / Cross Asset | 8 | 1 | 1 | 6 | 8/150 (OK) | [24_d_cross_asset.md](24_d_cross_asset.md) |
| D_DIGITAL_TWIN | 数字孪生 / Digital Twin | 8 | 0 | 1 | 7 | 8/150 (OK) | [25_d_digital_twin.md](25_d_digital_twin.md) |
| D_EXEC_SIM | 执行仿真 / Execution Simulation | 7 | 0 | 0 | 7 | 7/150 (OK) | [26_d_exec_sim.md](26_d_exec_sim.md) |
| D_EX_CORE | 执行核心 / Execution Core | 15 | 5 | 1 | 9 | 15/150 (OK) | [27_d_ex_core.md](27_d_ex_core.md) |
| D_EX_SOR | 执行路由 / Execution Routing | 7 | 0 | 0 | 7 | 7/150 (OK) | [28_d_ex_sor.md](28_d_ex_sor.md) |
| D_FACTOR | 因子 / Factor | 14 | 4 | 0 | 10 | 14/150 (OK) | [29_d_factor.md](29_d_factor.md) |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal / Fundamental Signal | 25 | 4 | 0 | 21 | 25/150 (OK) | [30_d_fundamental_signal.md](30_d_fundamental_signal.md) |
| D_GOVERNANCE | registry_management / Lifecycle Management | 860 | 503 | 28 | 329 | 860/150 (超容) | [31_d_governance.md](31_d_governance.md) |
| D_GOV_AUDIT | audit_orchestration / Audit Trail | 2 | 0 | 2 | 0 | 2/150 (OK) | [32_d_gov_audit.md](32_d_gov_audit.md) |
| D_GOV_DOCS | architecture_docs / Architecture Docs Governance | 2 | 2 | 0 | 0 | 2/150 (OK) | [33_d_gov_docs.md](33_d_gov_docs.md) |
| D_GOV_DRIFT | drift_detection / Drift Detection | 1 | 0 | 1 | 0 | 1/150 (OK) | [34_d_gov_drift.md](34_d_gov_drift.md) |
| D_GOV_ENFORCEMENT | rule_enforcement / Rule Enforcement | 201 | 133 | 0 | 68 | 201/150 (超容) | [35_d_gov_enforcement.md](35_d_gov_enforcement.md) |
| D_GOV_REPAIR | rollback / Governance Repair | 0 | 0 | 0 | 0 | 0/200 (OK) | [36_d_gov_repair.md](36_d_gov_repair.md) |
| D_GOV_RULE | rule_governance / Rule Governance | 0 | 0 | 0 | 0 | 0/200 (OK) | [37_d_gov_rule.md](37_d_gov_rule.md) |
| D_GOV_SCRIPTS | script_governance / Script Governance | 438 | 32 | 0 | 406 | 438/150 (超容) | [38_d_gov_scripts.md](38_d_gov_scripts.md) |
| D_INTELLIGENCE | context_management / Context Management | 43 | 21 | 0 | 22 | 43/150 (OK) | [39_d_intelligence.md](39_d_intelligence.md) |
| D_KNOWLEDGE | vector_storage / Knowledge Management | 9 | 0 | 2 | 7 | 9/150 (OK) | [40_d_knowledge.md](40_d_knowledge.md) |
| D_ML_SERVE | 推理 / Inference | 7 | 0 | 0 | 7 | 7/150 (OK) | [41_d_ml_serve.md](41_d_ml_serve.md) |
| D_ML_TRAIN | model_evaluation / Training | 12 | 0 | 1 | 11 | 12/150 (OK) | [42_d_ml_train.md](42_d_ml_train.md) |
| D_PF_ALLOC | 组合分配 / Portfolio Allocation | 8 | 0 | 1 | 7 | 8/150 (OK) | [43_d_pf_alloc.md](43_d_pf_alloc.md) |
| D_PF_CORE | 组合核心 / Portfolio Core | 14 | 4 | 0 | 10 | 14/150 (OK) | [44_d_pf_core.md](44_d_pf_core.md) |
| D_POSITION | 仓位管理 / Position Management | 8 | 1 | 0 | 7 | 8/150 (OK) | [45_d_position.md](45_d_position.md) |
| D_RISK | 风控 / Risk Control | 20 | 9 | 0 | 11 | 20/150 (OK) | [46_d_risk.md](46_d_risk.md) |
| D_SELL_DECISION | 卖出决策 / Sell Decision | 7 | 0 | 0 | 7 | 7/150 (OK) | [47_d_sell_decision.md](47_d_sell_decision.md) |
| D_SIGQC | signal_quality / Signal Quality Control | 8 | 0 | 0 | 8 | 8/150 (OK) | [48_d_sigqc.md](48_d_sigqc.md) |
| D_SIMULATION | 仿真 / Simulation | 11 | 2 | 1 | 8 | 11/150 (OK) | [49_d_simulation.md](49_d_simulation.md) |
| D_TRADING | 交易运营 / Trading Operations | 481 | 280 | 0 | 201 | 481/150 (超容) | [50_d_trading.md](50_d_trading.md) |
