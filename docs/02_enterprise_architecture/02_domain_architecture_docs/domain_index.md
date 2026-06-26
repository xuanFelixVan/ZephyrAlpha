---
doc_type: domain_index
title: 域总览索引
version: "1.0"
status: active
date: 2026-06-26
owner: auto-generator
ttl: permanent
---

# 域总览索引

> **文档作用 / Purpose**: 列出所有功能域的编号、ID、名称、层级、模块数等基本信息，是域架构文档的入口索引。

> 本文档由 generate_domain_index.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-26 18:50:47
> 数据源: depgraph.db domains表 + nodes表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 53 |
| 模块总数 | 6501 |
| 生产态模块 | 1404 |
| 设计态模块 | 89 |
| 原型态模块 | 5008 |

## 域清单（按架构层分组）

### L0_infrastructure (5 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-INFRA_A2A | a2a_communication | 114 | 114 | 0 | 0 | 114/150 (OK) | [d_infra_a2a.md](domains/d_infra_a2a.md) |
| D-INFRA_OPS | 基础设施运维 | 34 | 7 | 1 | 26 | 34/150 (OK) | [d_infra_ops.md](domains/d_infra_ops.md) |
| D-INFRA_RECOVERY | rollback_recovery | 107 | 107 | 0 | 0 | 107/150 (OK) | [d_infra_recovery.md](domains/d_infra_recovery.md) |
| D-INFRA_RUNTIME | 运行时集成 | 145 | 139 | 0 | 6 | 145/150 (OK) | [d_infra_runtime.md](domains/d_infra_runtime.md) |
| D-INFRA_TELEMETRY | observability_profiling | 51 | 51 | 0 | 0 | 51/150 (OK) | [d_infra_telemetry.md](domains/d_infra_telemetry.md) |

### L1_foundation (15 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-ALT_DATA | 另类数据 | 8 | 1 | 0 | 7 | 8/150 (OK) | [d_alt_data.md](domains/d_alt_data.md) |
| D-AUTONOMY_CORE | 自治核心 | 176 | 2 | 0 | 174 | 176/150 (超容) | [d_autonomy_core.md](domains/d_autonomy_core.md) |
| D-BEHAVIORAL_AUDIT | 行为审计 | 79 | 79 | 0 | 0 | 79/150 (OK) | [d_behavioral_audit.md](domains/d_behavioral_audit.md) |
| D-DATA_ENG | 数据工程 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_data_eng.md](domains/d_data_eng.md) |
| D-DATA_GOV | 数据治理 | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_data_gov.md](domains/d_data_gov.md) |
| D-DATA_SEC | 数据安全与契约 | 10 | 0 | 0 | 10 | 10/150 (OK) | [d_data_sec.md](domains/d_data_sec.md) |
| D-FRONTEND | 前端 | 23 | 7 | 0 | 16 | 23/150 (OK) | [d_frontend.md](domains/d_frontend.md) |
| D-INTEGRATION | 管线路由 | 296 | 70 | 0 | 226 | 296/150 (超容) | [d_integration.md](domains/d_integration.md) |
| D-INTEGRATION_GATEWAY | mcp_servers | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_integration_gateway.md](domains/d_integration_gateway.md) |
| D-MKT_DATA | 行情数据 | 9 | 1 | 0 | 8 | 9/150 (OK) | [d_mkt_data.md](domains/d_mkt_data.md) |
| D-OPS | 反馈循环 | 433 | 24 | 1 | 408 | 433/150 (超容) | [d_ops.md](domains/d_ops.md) |
| D-REPORTING | 报告 | 15 | 1 | 0 | 14 | 15/150 (OK) | [d_reporting.md](domains/d_reporting.md) |
| D-SECURITY | 对抗验证 | 244 | 132 | 0 | 112 | 244/150 (超容) | [d_security.md](domains/d_security.md) |
| D-SECURITY_LLM | llm_defense | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_security_llm.md](domains/d_security_llm.md) |
| D-SHARED | 共享服务 | 296 | 93 | 0 | 203 | 296/150 (超容) | [d_shared.md](domains/d_shared.md) |

### L2_domain (32 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-ASHARE_SIGNAL | A股特色信号 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_ashare_signal.md](domains/d_ashare_signal.md) |
| D-AUDITTEST | audit_test_suite | 152 | 142 | 0 | 10 | 152/150 (超容) | [d_audittest.md](domains/d_audittest.md) |
| D-AUTONOMY_PERM | 自治保护 | 70 | 2 | 1 | 67 | 70/150 (OK) | [d_autonomy_perm.md](domains/d_autonomy_perm.md) |
| D-BACKTEST | 回测 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_backtest.md](domains/d_backtest.md) |
| D-COMPLIANCE | 合规 | 25 | 0 | 0 | 25 | 25/150 (OK) | [d_compliance.md](domains/d_compliance.md) |
| D-CROSS_ASSET | 跨资产 | 11 | 1 | 1 | 9 | 11/150 (OK) | [d_cross_asset.md](domains/d_cross_asset.md) |
| D-DIGITAL_TWIN | 数字孪生 | 8 | 0 | 1 | 7 | 8/150 (OK) | [d_digital_twin.md](domains/d_digital_twin.md) |
| D-EXEC_SIM | 执行仿真 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_exec_sim.md](domains/d_exec_sim.md) |
| D-EX_CORE | 执行核心 | 14 | 3 | 0 | 11 | 14/150 (OK) | [d_ex_core.md](domains/d_ex_core.md) |
| D-EX_SOR | 执行路由 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_ex_sor.md](domains/d_ex_sor.md) |
| D-FACTOR | 因子 | 17 | 2 | 0 | 15 | 17/150 (OK) | [d_factor.md](domains/d_factor.md) |
| D-FUNDAMENTAL_SIGNAL | 基本面信号 | 25 | 4 | 0 | 21 | 25/150 (OK) | [d_fundamental_signal.md](domains/d_fundamental_signal.md) |
| D-GOVERNANCE | 生命周期管理 | 2831 | 117 | 50 | 2664 | 2831/150 (超容) | [d_governance.md](domains/d_governance.md) |
| D-GOV_AUDIT | 审计追踪 | 188 | 54 | 2 | 132 | 188/150 (超容) | [d_gov_audit.md](domains/d_gov_audit.md) |
| D-GOV_DOCS | architecture_docs | 127 | 78 | 0 | 49 | 127/150 (OK) | [d_gov_docs.md](domains/d_gov_docs.md) |
| D-GOV_DRIFT | 漂移检测 | 24 | 9 | 1 | 14 | 24/150 (OK) | [d_gov_drift.md](domains/d_gov_drift.md) |
| D-GOV_ENFORCEMENT | rule_enforcement | 107 | 69 | 0 | 38 | 107/150 (OK) | [d_gov_enforcement.md](domains/d_gov_enforcement.md) |
| D-GOV_RULE | 规则治理 | 11 | 11 | 0 | 0 | 11/150 (OK) | [d_gov_rule.md](domains/d_gov_rule.md) |
| D-GOV_SCRIPTS | code_dedup | 416 | 26 | 0 | 390 | 416/150 (超容) | [d_gov_scripts.md](domains/d_gov_scripts.md) |
| D-INTELLIGENCE | 上下文管理 | 56 | 18 | 0 | 38 | 56/150 (OK) | [d_intelligence.md](domains/d_intelligence.md) |
| D-KNOWLEDGE | 知识管理 | 41 | 1 | 2 | 38 | 41/150 (OK) | [d_knowledge.md](domains/d_knowledge.md) |
| D-ML_SERVE | 推理 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_ml_serve.md](domains/d_ml_serve.md) |
| D-ML_TRAIN | 训练 | 12 | 0 | 1 | 11 | 12/150 (OK) | [d_ml_train.md](domains/d_ml_train.md) |
| D-PF_ALLOC | 组合分配 | 11 | 0 | 1 | 10 | 11/150 (OK) | [d_pf_alloc.md](domains/d_pf_alloc.md) |
| D-PF_CORE | 组合核心 | 44 | 6 | 26 | 12 | 44/150 (OK) | [d_pf_core.md](domains/d_pf_core.md) |
| D-POSITION | 仓位管理 | 8 | 0 | 0 | 8 | 8/150 (OK) | [d_position.md](domains/d_position.md) |
| D-RISK | 风控 | 25 | 9 | 0 | 16 | 25/150 (OK) | [d_risk.md](domains/d_risk.md) |
| D-SELL_DECISION | 卖出决策 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_sell_decision.md](domains/d_sell_decision.md) |
| D-SIGLEGACY | 信号遗留设计态 | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_siglegacy.md](domains/d_siglegacy.md) |
| D-SIGQC | 信号质量控制 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_sigqc.md](domains/d_sigqc.md) |
| D-SIMULATION | 仿真 | 19 | 4 | 1 | 14 | 19/150 (OK) | [d_simulation.md](domains/d_simulation.md) |
| D-TRADING | 交易运营 | 163 | 20 | 0 | 143 | 163/150 (超容) | [d_trading.md](domains/d_trading.md) |

### 未分类 (1 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-GOV-REPAIR | rollback | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_gov_repair.md](domains/d_gov_repair.md) |
