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
| 域总数 | 53 |
| 模块总数 | 5048 |
| 生产态模块 | 1740 |
| 设计态模块 | 36 |
| 原型态模块 | 3272 |

## 域清单（按架构层分组）

### L0_infrastructure (5 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_INFRA_A2A | A2A通信 | 93 | 83 | 0 | 10 | 93/150 (OK) | [d_infra_a2a.md](domains/d_infra_a2a.md) |
| D_INFRA_OPS | 基础设施运维 | 10 | 0 | 1 | 9 | 10/150 (OK) | [d_infra_ops.md](domains/d_infra_ops.md) |
| D_INFRA_RECOVERY | 回滚恢复 | 74 | 73 | 0 | 1 | 74/150 (OK) | [d_infra_recovery.md](domains/d_infra_recovery.md) |
| D_INFRA_RUNTIME | 运行时集成 | 149 | 140 | 0 | 9 | 149/150 (OK) | [d_infra_runtime.md](domains/d_infra_runtime.md) |
| D_INFRA_TELEMETRY | 可观测性 | 25 | 25 | 0 | 0 | 25/150 (OK) | [d_infra_telemetry.md](domains/d_infra_telemetry.md) |

### L1_foundation (15 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_ALT_DATA | 另类数据 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_alt_data.md](domains/d_alt_data.md) |
| D_AUTONOMY_CORE | 自治核心 | 114 | 111 | 0 | 3 | 114/150 (OK) | [d_autonomy_core.md](domains/d_autonomy_core.md) |
| D_BEHAVIORAL_AUDIT | 行为审计 | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_behavioral_audit.md](domains/d_behavioral_audit.md) |
| D_DATA_ENG | 数据工程 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_data_eng.md](domains/d_data_eng.md) |
| D_DATA_GOV | 数据治理 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_data_gov.md](domains/d_data_gov.md) |
| D_DATA_SEC | 数据安全与契约 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_data_sec.md](domains/d_data_sec.md) |
| D_FRONTEND | 前端 | 16 | 7 | 0 | 9 | 16/150 (OK) | [d_frontend.md](domains/d_frontend.md) |
| D_INTEGRATION | 管线路由 | 89 | 49 | 0 | 40 | 89/150 (OK) | [d_integration.md](domains/d_integration.md) |
| D_INTEGRATION_GATEWAY | 集成网关 | 20 | 1 | 0 | 19 | 20/150 (OK) | [d_integration_gateway.md](domains/d_integration_gateway.md) |
| D_MKT_DATA | 行情数据 | 8 | 1 | 0 | 7 | 8/150 (OK) | [d_mkt_data.md](domains/d_mkt_data.md) |
| D_OPS | 反馈循环 | 3 | 3 | 0 | 0 | 3/150 (OK) | [d_ops.md](domains/d_ops.md) |
| D_REPORTING | 报告 | 10 | 1 | 0 | 9 | 10/150 (OK) | [d_reporting.md](domains/d_reporting.md) |
| D_SECURITY | 对抗验证 | 147 | 93 | 0 | 54 | 147/150 (OK) | [d_security.md](domains/d_security.md) |
| D_SECURITY_LLM | LLM防御 | 44 | 32 | 0 | 12 | 44/150 (OK) | [d_security_llm.md](domains/d_security_llm.md) |
| D_SHARED | 共享服务 | 227 | 98 | 0 | 129 | 227/150 (超容) | [d_shared.md](domains/d_shared.md) |

### L2_domain (32 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_ASHARE_SIGNAL | A股特色信号 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_ashare_signal.md](domains/d_ashare_signal.md) |
| D_AUDITTEST | 审计测试套件 | 1738 | 49 | 0 | 1689 | 1738/150 (超容) | [d_audittest.md](domains/d_audittest.md) |
| D_AUTONOMY_PERM | 自治保护 | 14 | 0 | 0 | 14 | 14/150 (OK) | [d_autonomy_perm.md](domains/d_autonomy_perm.md) |
| D_BACKTEST | 回测 | 10 | 3 | 0 | 7 | 10/150 (OK) | [d_backtest.md](domains/d_backtest.md) |
| D_COMPLIANCE | 合规 | 25 | 0 | 0 | 25 | 25/150 (OK) | [d_compliance.md](domains/d_compliance.md) |
| D_CROSS_ASSET | 跨资产 | 8 | 1 | 1 | 6 | 8/150 (OK) | [d_cross_asset.md](domains/d_cross_asset.md) |
| D_DIGITAL_TWIN | 数字孪生 | 8 | 0 | 1 | 7 | 8/150 (OK) | [d_digital_twin.md](domains/d_digital_twin.md) |
| D_EXEC_SIM | 执行仿真 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_exec_sim.md](domains/d_exec_sim.md) |
| D_EX_CORE | 执行核心 | 13 | 5 | 0 | 8 | 13/150 (OK) | [d_ex_core.md](domains/d_ex_core.md) |
| D_EX_SOR | 执行路由 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_ex_sor.md](domains/d_ex_sor.md) |
| D_FACTOR | 因子 | 14 | 4 | 0 | 10 | 14/150 (OK) | [d_factor.md](domains/d_factor.md) |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | 25 | 4 | 0 | 21 | 25/150 (OK) | [d_fundamental_signal.md](domains/d_fundamental_signal.md) |
| D_GOVERNANCE | 生命周期管理 | 878 | 465 | 25 | 388 | 878/150 (超容) | [d_governance.md](domains/d_governance.md) |
| D_GOV_AUDIT | 审计追踪 | 2 | 0 | 2 | 0 | 2/150 (OK) | [d_gov_audit.md](domains/d_gov_audit.md) |
| D_GOV_DOCS | 架构文档治理 | 1 | 1 | 0 | 0 | 1/150 (OK) | [d_gov_docs.md](domains/d_gov_docs.md) |
| D_GOV_DRIFT | 漂移检测 | 1 | 0 | 1 | 0 | 1/150 (OK) | [d_gov_drift.md](domains/d_gov_drift.md) |
| D_GOV_ENFORCEMENT | 规则执行 | 173 | 132 | 0 | 41 | 173/150 (超容) | [d_gov_enforcement.md](domains/d_gov_enforcement.md) |
| D_GOV_RULE | 规则治理 | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_gov_rule.md](domains/d_gov_rule.md) |
| D_GOV_SCRIPTS | 脚本治理 | 422 | 38 | 0 | 384 | 422/150 (超容) | [d_gov_scripts.md](domains/d_gov_scripts.md) |
| D_INTELLIGENCE | 上下文管理 | 45 | 21 | 0 | 24 | 45/150 (OK) | [d_intelligence.md](domains/d_intelligence.md) |
| D_KNOWLEDGE | 知识管理 | 9 | 0 | 2 | 7 | 9/150 (OK) | [d_knowledge.md](domains/d_knowledge.md) |
| D_ML_SERVE | 推理 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_ml_serve.md](domains/d_ml_serve.md) |
| D_ML_TRAIN | 训练 | 12 | 0 | 1 | 11 | 12/150 (OK) | [d_ml_train.md](domains/d_ml_train.md) |
| D_PF_ALLOC | 组合分配 | 8 | 0 | 1 | 7 | 8/150 (OK) | [d_pf_alloc.md](domains/d_pf_alloc.md) |
| D_PF_CORE | 组合核心 | 14 | 4 | 0 | 10 | 14/150 (OK) | [d_pf_core.md](domains/d_pf_core.md) |
| D_POSITION | 仓位管理 | 8 | 1 | 0 | 7 | 8/150 (OK) | [d_position.md](domains/d_position.md) |
| D_RISK | 风控 | 22 | 10 | 0 | 12 | 22/150 (OK) | [d_risk.md](domains/d_risk.md) |
| D_SELL_DECISION | 卖出决策 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_sell_decision.md](domains/d_sell_decision.md) |
| D_SIGLEGACY | 信号遗留设计态 | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_siglegacy.md](domains/d_siglegacy.md) |
| D_SIGQC | 信号质量控制 | 7 | 0 | 0 | 7 | 7/150 (OK) | [d_sigqc.md](domains/d_sigqc.md) |
| D_SIMULATION | 仿真 | 11 | 2 | 1 | 8 | 11/150 (OK) | [d_simulation.md](domains/d_simulation.md) |
| D_TRADING | 交易运营 | 488 | 283 | 0 | 205 | 488/150 (超容) | [d_trading.md](domains/d_trading.md) |

### 未分类 (1 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D_GOV_REPAIR | 治理修复 | 0 | 0 | 0 | 0 | 0/150 (OK) | [d_gov_repair.md](domains/d_gov_repair.md) |
