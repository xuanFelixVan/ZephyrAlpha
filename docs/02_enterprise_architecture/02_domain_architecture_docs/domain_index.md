---
doc_type: domain_index
title: 域总览索引
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 域总览索引

> **文档作用 / Purpose**: 列出所有功能域的编号、ID、名称、层级、模块数等基本信息，是域架构文档的入口索引。

> 本文档由 generate_domain_index.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-25 20:00:20
> 数据源: depgraph.db domains表 + nodes表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 53 |
| 模块总数 | 6841 |
| 生产态模块 | 1428 |
| 设计态模块 | 403 |
| 原型态模块 | 5010 |

## 域清单（按架构层分组）

### L0_infrastructure (5 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-INFRA_A2A | a2a_communication | 114 | 114 | 0 | 0 | 114/150 (OK) | [d_infra_a2a.md](domains/d_infra_a2a.md) |
| D-INFRA_OPS | 基础设施运维 | 46 | 7 | 13 | 26 | 46/150 (OK) | [d_infra_ops.md](domains/d_infra_ops.md) |
| D-INFRA_RECOVERY | rollback_recovery | 107 | 107 | 0 | 0 | 107/150 (OK) | [d_infra_recovery.md](domains/d_infra_recovery.md) |
| D-INFRA_RUNTIME | 运行时集成 | 148 | 139 | 3 | 6 | 148/150 (OK) | [d_infra_runtime.md](domains/d_infra_runtime.md) |
| D-INFRA_TELEMETRY | observability_profiling | 51 | 51 | 0 | 0 | 51/150 (OK) | [d_infra_telemetry.md](domains/d_infra_telemetry.md) |

### L1_foundation (15 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-ALT_DATA | 另类数据 | 8 | 1 | 0 | 7 | 8/150 (OK) | [d_alt_data.md](domains/d_alt_data.md) |
| D-AUTONOMY_CORE | 自治核心 | 181 | 2 | 5 | 174 | 181/150 (超容) | [d_autonomy_core.md](domains/d_autonomy_core.md) |
| D-BEHAVIORAL_AUDIT | 行为审计 | 79 | 79 | 0 | 0 | 79/150 (OK) | [d_behavioral_audit.md](domains/d_behavioral_audit.md) |
| D-DATA_ENG | 数据工程 | 11 | 0 | 4 | 7 | 11/150 (OK) | [d_data_eng.md](domains/d_data_eng.md) |
| D-DATA_GOV | 数据治理 | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_data_gov.md](domains/d_data_gov.md) |
| D-DATA_SEC | 数据安全与契约 | 10 | 0 | 0 | 10 | 10/150 (OK) | [d_data_sec.md](domains/d_data_sec.md) |
| D-FRONTEND | 前端 | 33 | 7 | 10 | 16 | 33/150 (OK) | [d_frontend.md](domains/d_frontend.md) |
| D-INTEGRATION | 管线路由 | 314 | 71 | 17 | 226 | 314/150 (超容) | [d_integration.md](domains/d_integration.md) |
| D-INTEGRATION-GATEWAY | mcp_servers | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_integration_gateway.md](domains/d_integration_gateway.md) |
| D-MKT_DATA | 行情数据 | 10 | 1 | 1 | 8 | 10/150 (OK) | [d_mkt_data.md](domains/d_mkt_data.md) |
| D-OPS | 反馈循环 | 445 | 24 | 13 | 408 | 445/150 (超容) | [d_ops.md](domains/d_ops.md) |
| D-REPORTING | 报告 | 19 | 1 | 4 | 14 | 19/150 (OK) | [d_reporting.md](domains/d_reporting.md) |
| D-SECURITY | 对抗验证 | 276 | 132 | 32 | 112 | 276/150 (超容) | [d_security.md](domains/d_security.md) |
| D-SECURITY-LLM | llm_defense | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_security_llm.md](domains/d_security_llm.md) |
| D-SHARED | 共享服务 | 303 | 94 | 6 | 203 | 303/150 (超容) | [d_shared.md](domains/d_shared.md) |

### L2_domain (32 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-ASHARE_SIGNAL | A股特色信号 | 27 | 0 | 20 | 7 | 27/150 (OK) | [d_ashare_signal.md](domains/d_ashare_signal.md) |
| D-AUTONOMY_PERM | 自治保护 | 88 | 2 | 19 | 67 | 88/150 (OK) | [d_autonomy_perm.md](domains/d_autonomy_perm.md) |
| D-BACKTEST | 回测 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_backtest.md](domains/d_backtest.md) |
| D-COMPLIANCE | 合规 | 30 | 0 | 5 | 25 | 30/150 (OK) | [d_compliance.md](domains/d_compliance.md) |
| D-CROSS_ASSET | 跨资产 | 15 | 1 | 5 | 9 | 15/150 (OK) | [d_cross_asset.md](domains/d_cross_asset.md) |
| D-DIGITAL_TWIN | 数字孪生 | 12 | 0 | 5 | 7 | 12/150 (OK) | [d_digital_twin.md](domains/d_digital_twin.md) |
| D-EXEC_SIM | 执行仿真 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_exec_sim.md](domains/d_exec_sim.md) |
| D-EX_CORE | 执行核心 | 14 | 3 | 0 | 11 | 14/150 (OK) | [d_ex_core.md](domains/d_ex_core.md) |
| D-EX_SOR | 执行路由 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_ex_sor.md](domains/d_ex_sor.md) |
| D-FACTOR | 因子 | 17 | 2 | 0 | 15 | 17/150 (OK) | [d_factor.md](domains/d_factor.md) |
| D-FUNDAMENTAL_SIGNAL | 基本面信号 | 25 | 4 | 0 | 21 | 25/150 (OK) | [d_fundamental_signal.md](domains/d_fundamental_signal.md) |
| D-GOV-DOCS | architecture_docs | 151 | 100 | 0 | 51 | 151/150 (超容) | [d_gov_docs.md](domains/d_gov_docs.md) |
| D-GOV-ENFORCEMENT | rule_enforcement | 107 | 69 | 0 | 38 | 107/150 (OK) | [d_gov_enforcement.md](domains/d_gov_enforcement.md) |
| D-GOV-SCRIPTS | code_dedup | 416 | 26 | 0 | 390 | 416/150 (超容) | [d_gov_scripts.md](domains/d_gov_scripts.md) |
| D-GOVERNANCE | 生命周期管理 | 2843 | 117 | 62 | 2664 | 2843/150 (超容) | [d_governance.md](domains/d_governance.md) |
| D-GOV_AUDIT | 审计追踪 | 189 | 54 | 3 | 132 | 189/150 (超容) | [d_gov_audit.md](domains/d_gov_audit.md) |
| D-GOV_AUDIT_TESTS | audit_test_suite | 152 | 142 | 0 | 10 | 152/150 (超容) | [d_gov_audit_tests.md](domains/d_gov_audit_tests.md) |
| D-GOV_DRIFT | 漂移检测 | 25 | 9 | 2 | 14 | 25/150 (OK) | [d_gov_drift.md](domains/d_gov_drift.md) |
| D-GOV_RULE | 规则治理 | 12 | 11 | 1 | 0 | 12/150 (OK) | [d_gov_rule.md](domains/d_gov_rule.md) |
| D-INTELLIGENCE | 上下文管理 | 57 | 18 | 1 | 38 | 57/150 (OK) | [d_intelligence.md](domains/d_intelligence.md) |
| D-KNOWLEDGE | 知识管理 | 50 | 1 | 11 | 38 | 50/150 (OK) | [d_knowledge.md](domains/d_knowledge.md) |
| D-ML_SERVE | 推理 | 8 | 0 | 1 | 7 | 8/150 (OK) | [d_ml_serve.md](domains/d_ml_serve.md) |
| D-ML_TRAIN | 训练 | 13 | 0 | 2 | 11 | 13/150 (OK) | [d_ml_train.md](domains/d_ml_train.md) |
| D-PF_ALLOC | 组合分配 | 15 | 0 | 5 | 10 | 15/150 (OK) | [d_pf_alloc.md](domains/d_pf_alloc.md) |
| D-PF_CORE | 组合核心 | 48 | 6 | 30 | 12 | 48/150 (OK) | [d_pf_core.md](domains/d_pf_core.md) |
| D-POSITION | 仓位管理 | 8 | 0 | 0 | 8 | 8/150 (OK) | [d_position.md](domains/d_position.md) |
| D-RISK | 风控 | 82 | 9 | 57 | 16 | 82/150 (OK) | [d_risk.md](domains/d_risk.md) |
| D-SELL_DECISION | 卖出决策 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_sell_decision.md](domains/d_sell_decision.md) |
| D-SIGLEGACY | 信号遗留设计态 | 45 | 0 | 45 | 0 | 45/150 (OK) | [d_siglegacy.md](domains/d_siglegacy.md) |
| D-SIGQC | 信号质量控制 | 17 | 0 | 10 | 7 | 17/150 (OK) | [d_sigqc.md](domains/d_sigqc.md) |
| D-SIMULATION | 仿真 | 23 | 4 | 5 | 14 | 23/150 (OK) | [d_simulation.md](domains/d_simulation.md) |
| D-TRADING | 交易运营 | 169 | 20 | 6 | 143 | 169/150 (超容) | [d_trading.md](domains/d_trading.md) |

### 未分类 (1 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-GOV-REPAIR | rollback | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_gov_repair.md](domains/d_gov_repair.md) |
