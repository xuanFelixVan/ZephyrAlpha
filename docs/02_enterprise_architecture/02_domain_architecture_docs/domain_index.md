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
| 模块总数 | 2683 |
| 生产态模块 | 1567 |
| 设计态模块 | 62 |
| 原型态模块 | 1054 |

## 域清单（按架构层分组）

### L0 基础设施层 / L0 Infrastructure (5 个域 / 5 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_INFRA_A2A | A2A通信 / A2A Communication | 72 | 28 | 0 | 44 | 72/150 (OK) | [📄 01_d_infra_a2a.md](01_d_infra_a2a.md) |
| D_INFRA_OPS | 基础设施运维 / Asset Inventory | 2 | 0 | 2 | 0 | 2/150 (OK) | [📄 02_d_infra_ops.md](02_d_infra_ops.md) |
| D_INFRA_RECOVERY | 回滚恢复 / Rollback Recovery | 54 | 48 | 0 | 6 | 54/150 (OK) | [📄 03_d_infra_recovery.md](03_d_infra_recovery.md) |
| D_INFRA_RUNTIME | 运行时集成 / Runtime Integration | 160 | 118 | 1 | 41 | 160/150 (超容) | [📄 04_d_infra_runtime.md](04_d_infra_runtime.md) |
| D_INFRA_TELEMETRY | 可观测性 / Observability | 0 | 0 | 0 | 0 | 0/150 (OK) | [📄 05_d_infra_telemetry.md](05_d_infra_telemetry.md) |

### L1 基础平台层 / L1 Foundation (21 个域 / 21 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_ALT_DATA | 另类数据 / Alternative Data | 7 | 0 | 0 | 7 | 7/150 (OK) | [📄 06_d_alt_data.md](06_d_alt_data.md) |
| D_AUTONOMY_CORE | 自治核心 / Autonomy Core | 137 | 132 | 0 | 5 | 137/150 (OK) | [📄 07_d_autonomy_core.md](07_d_autonomy_core.md) |
| D_DATA_ENG | 数据工程 / Data Engineering | 7 | 0 | 0 | 7 | 7/150 (OK) | [📄 08_d_data_eng.md](08_d_data_eng.md) |
| D_DATA_GOV | 数据治理 / Data Governance | 7 | 0 | 0 | 7 | 7/150 (OK) | [📄 09_d_data_gov.md](09_d_data_gov.md) |
| D_DATA_SEC | 数据安全与契约 / Data Security & Contracts | 7 | 0 | 0 | 7 | 7/150 (OK) | [📄 10_d_data_sec.md](10_d_data_sec.md) |
| D_FBL_DETECTORS | 反馈检测器 / Feedback Detectors | 65 | 59 | 0 | 6 | 65/150 (OK) | [📄 11_d_fbl_detectors.md](11_d_fbl_detectors.md) |
| D_FBL_DIAGNOSERS | 反馈诊断器 / Feedback Diagnosers | 76 | 71 | 0 | 5 | 76/150 (OK) | [📄 12_d_fbl_diagnosers.md](12_d_fbl_diagnosers.md) |
| D_FBL_VERIFICATION | 反馈验证 / Feedback Verification | 71 | 67 | 0 | 4 | 71/150 (OK) | [📄 13_d_fbl_verification.md](13_d_fbl_verification.md) |
| D_FEEDBACK_LOOP | 反馈循环引擎 / Feedback Loop Engine | 124 | 112 | 0 | 12 | 124/150 (OK) | [📄 14_d_feedback_loop.md](14_d_feedback_loop.md) |
| D_FRONTEND | 前端 / Frontend | 18 | 9 | 6 | 3 | 18/150 (OK) | [📄 15_d_frontend.md](15_d_frontend.md) |
| D_GOV_CODE_QUALITY | 代码质量治理 / Code Quality Governance | 134 | 114 | 0 | 20 | 134/150 (OK) | [📄 16_d_gov_code_quality.md](16_d_gov_code_quality.md) |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 / Ops Resilience Governance | 90 | 81 | 0 | 9 | 90/150 (OK) | [📄 17_d_gov_ops_resilience.md](17_d_gov_ops_resilience.md) |
| D_INTEGRATION | 管线路由 / Pipeline Routing | 73 | 45 | 0 | 28 | 73/150 (OK) | [📄 18_d_integration.md](18_d_integration.md) |
| D_INTEGRATION_GATEWAY | 集成网关 / Integration Gateway | 0 | 0 | 0 | 0 | 0/150 (OK) | [📄 19_d_integration_gateway.md](19_d_integration_gateway.md) |
| D_MKT_DATA | 行情数据 / Market Data | 10 | 0 | 3 | 7 | 10/150 (OK) | [📄 20_d_mkt_data.md](20_d_mkt_data.md) |
| D_OPS | 反馈循环 / Feedback Loop | 9 | 8 | 0 | 1 | 9/150 (OK) | [📄 21_d_ops.md](21_d_ops.md) |
| D_ORCHESTRATOR | 代理编排器 / Agent Orchestrator | 72 | 58 | 0 | 14 | 72/150 (OK) | [📄 22_d_orchestrator.md](22_d_orchestrator.md) |
| D_REPORTING | 报告 / Reporting | 3 | 1 | 0 | 2 | 3/150 (OK) | [📄 23_d_reporting.md](23_d_reporting.md) |
| D_SECURITY | 对抗验证 / Adversarial Validation | 165 | 99 | 0 | 66 | 165/150 (超容) | [📄 24_d_security.md](24_d_security.md) |
| D_SECURITY_LLM | LLM防御 / LLM Defense | 0 | 0 | 0 | 0 | 0/150 (OK) | [📄 25_d_security_llm.md](25_d_security_llm.md) |
| D_SHARED | 共享服务 / Shared Services | 184 | 115 | 0 | 69 | 184/150 (超容) | [📄 26_d_shared.md](26_d_shared.md) |

### L2 业务域层 / L2 Domain (32 个域 / 32 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_ASHARE_SIGNAL | A股特色信号 / A-Share Signal | 7 | 0 | 0 | 7 | 7/150 (OK) | [📄 27_d_ashare_signal.md](27_d_ashare_signal.md) |
| D_AUDITTEST | 审计测试套件 / Audit Test Suite | 1 | 1 | 0 | 0 | 1/150 (OK) | [📄 28_d_audittest.md](28_d_audittest.md) |
| D_AUTONOMY_PERM | 自治保护 / Autonomy Protection | 2 | 0 | 0 | 2 | 2/150 (OK) | [📄 29_d_autonomy_perm.md](29_d_autonomy_perm.md) |
| D_BACKTEST | 回测 / Backtest | 25 | 9 | 8 | 8 | 25/150 (OK) | [📄 30_d_backtest.md](30_d_backtest.md) |
| D_CROSS_ASSET | 跨资产 / Cross Asset | 8 | 0 | 1 | 7 | 8/150 (OK) | [📄 31_d_cross_asset.md](31_d_cross_asset.md) |
| D_DIGITAL_TWIN | 数字孪生 / Digital Twin | 8 | 0 | 1 | 7 | 8/150 (OK) | [📄 32_d_digital_twin.md](32_d_digital_twin.md) |
| D_EXEC_SIM | 执行仿真 / Execution Simulation | 7 | 0 | 0 | 7 | 7/150 (OK) | [📄 33_d_exec_sim.md](33_d_exec_sim.md) |
| D_EX_CORE | 执行核心 / Execution Core | 8 | 4 | 1 | 3 | 8/150 (OK) | [📄 34_d_ex_core.md](34_d_ex_core.md) |
| D_EX_SOR | 执行路由 / Execution Routing | 7 | 0 | 0 | 7 | 7/150 (OK) | [📄 35_d_ex_sor.md](35_d_ex_sor.md) |
| D_FACTOR | 因子 / Factor | 5 | 2 | 0 | 3 | 5/150 (OK) | [📄 36_d_factor.md](36_d_factor.md) |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 / Fundamental Signal | 10 | 4 | 0 | 6 | 10/150 (OK) | [📄 37_d_fundamental_signal.md](37_d_fundamental_signal.md) |
| D_GOVERNANCE | 生命周期管理 / Lifecycle Management | 213 | 96 | 1 | 116 | 213/150 (超容) | [📄 38_d_governance.md](38_d_governance.md) |
| D_GOV_AUDIT | 审计追踪 / Audit Trail | 102 | 67 | 2 | 33 | 102/150 (OK) | [📄 39_d_gov_audit.md](39_d_gov_audit.md) |
| D_GOV_DOCS | 架构文档治理 / Architecture Docs Governance | 28 | 0 | 28 | 0 | 28/150 (OK) | [📄 40_d_gov_docs.md](40_d_gov_docs.md) |
| D_GOV_DRIFT | 漂移检测 / Drift Detection | 74 | 70 | 1 | 3 | 74/150 (OK) | [📄 41_d_gov_drift.md](41_d_gov_drift.md) |
| D_GOV_ENFORCEMENT | 规则执行 / Rule Enforcement | 32 | 15 | 0 | 17 | 32/150 (OK) | [📄 42_d_gov_enforcement.md](42_d_gov_enforcement.md) |
| D_GOV_KB | 知识库治理 / Knowledge Base Governance | 26 | 16 | 0 | 10 | 26/150 (OK) | [📄 43_d_gov_kb.md](43_d_gov_kb.md) |
| D_GOV_REPAIR | 治理修复 / Governance Repair | 1 | 1 | 0 | 0 | 1/200 (OK) | [📄 44_d_gov_repair.md](44_d_gov_repair.md) |
| D_GOV_RULE | 规则治理 / Rule Governance | 35 | 31 | 0 | 4 | 35/200 (OK) | [📄 45_d_gov_rule.md](45_d_gov_rule.md) |
| D_GOV_SCRIPTS | 脚本治理 / Script Governance | 359 | 10 | 2 | 347 | 359/150 (超容) | [📄 46_d_gov_scripts.md](46_d_gov_scripts.md) |
| D_INTELLIGENCE | 上下文管理 / Context Management | 31 | 21 | 0 | 10 | 31/150 (OK) | [📄 47_d_intelligence.md](47_d_intelligence.md) |
| D_KNOWLEDGE | 知识管理 / Knowledge Management | 4 | 0 | 2 | 2 | 4/150 (OK) | [📄 48_d_knowledge.md](48_d_knowledge.md) |
| D_ML_SERVE | 推理 / Inference | 7 | 0 | 0 | 7 | 7/150 (OK) | [📄 49_d_ml_serve.md](49_d_ml_serve.md) |
| D_ML_TRAIN | 训练 / Training | 4 | 0 | 1 | 3 | 4/150 (OK) | [📄 50_d_ml_train.md](50_d_ml_train.md) |
| D_PF_ALLOC | 组合分配 / Portfolio Allocation | 3 | 1 | 1 | 1 | 3/150 (OK) | [📄 51_d_pf_alloc.md](51_d_pf_alloc.md) |
| D_PF_CORE | 组合核心 / Portfolio Core | 1 | 0 | 0 | 1 | 1/150 (OK) | [📄 52_d_pf_core.md](52_d_pf_core.md) |
| D_POSITION | 仓位管理 / Position Management | 1 | 1 | 0 | 0 | 1/150 (OK) | [📄 53_d_position.md](53_d_position.md) |
| D_RISK | 风控 / Risk Control | 11 | 9 | 0 | 2 | 11/150 (OK) | [📄 54_d_risk.md](54_d_risk.md) |
| D_SELL_DECISION | 卖出决策 / Sell Decision | 7 | 0 | 0 | 7 | 7/150 (OK) | [📄 55_d_sell_decision.md](55_d_sell_decision.md) |
| D_SIGQC | 信号质量控制 / Signal Quality Control | 2 | 0 | 0 | 2 | 2/150 (OK) | [📄 56_d_sigqc.md](56_d_sigqc.md) |
| D_SIMULATION | 仿真 / Simulation | 3 | 2 | 1 | 0 | 3/150 (OK) | [📄 57_d_simulation.md](57_d_simulation.md) |
| D_TRADING | 交易运营 / Trading Operations | 32 | 21 | 0 | 11 | 32/150 (OK) | [📄 58_d_trading.md](58_d_trading.md) |

### 未分类 / 未分类 (5 个域 / 5 domains)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_BEHAVIORAL_AUDIT | 行为审计 / Behavioral Audit | 0 | 0 | 0 | 0 | 0/200 (OK) | [📄 59_d_behavioral_audit.md](59_d_behavioral_audit.md) |
| D_COMPLIANCE | 合规 / Compliance | 4 | 0 | 0 | 4 | 4/200 (OK) | [📄 60_d_compliance.md](60_d_compliance.md) |
| D_DATA | 数据接入层 / Data Access Layer | 42 | 9 | 0 | 33 | 42/200 (OK) | [📄 61_d_data.md](61_d_data.md) |
| D_INFRASTRUCTURE | 跨层契约基础设施 / Cross-Layer Contract Infrastructure | 26 | 12 | 0 | 14 | 26/200 (OK) | [📄 62_d_infrastructure.md](62_d_infrastructure.md) |
| D_SIGLEGACY | 信号遗留设计态 / Signal Legacy (Design) | 0 | 0 | 0 | 0 | 0/200 (OK) | [📄 63_d_siglegacy.md](63_d_siglegacy.md) |
