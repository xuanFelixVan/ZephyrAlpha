---
doc_type: architecture_view
title: 能力热力图
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 能力热力图 / Capability Heatmap

> **文档作用 / Purpose**: 以矩阵形式展示48个架构域在10个能力域上的成熟度分布，用于识别能力短板和过度建设。

> 本文档由 generate_capability_heatmap.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) domains表 + nodes表 (注: arch_domain_capacity表不存在，v6已合并入domains表)

## 统计概览 / Statistics Overview

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 / Total Domains | 48 |
| 能力域数 / Capability Domains | 10 |
| L0 缺失 / Missing | 2 |
| L1 设计中 / Designing | 19 |
| L2 可用未验证 / Usable | 24 |
| L3 生产已验证 / Verified | 3 |
| ✅ 完全覆盖 / Full Coverage (L3) | 3 |
| 🟡 部分覆盖 / Partial Coverage (L1-L2) | 43 |
| ❌ 无覆盖 / No Coverage (L0) | 2 |

## 成熟度图例 / Maturity Legend

| 等级 / Level | 符号 / Symbol | 覆盖度 / Coverage | 中文名 / Chinese | 英文名 / English | 定义 / Definition |
|:---:|:---:|:---:|--------|--------|------|
| L0 | ⚪ | ❌ | 缺失 | Missing | 能力完全不存在，无设计无代码 / No nodes in domain |
| L1 | 🔵 | 🟡 | 设计中 | Designing | 有设计文档或原型代码，未集成 / design_maturity=design or prototype |
| L2 | 🟡 | 🟡 | 可用未验证 | Usable | 代码可用但未生产验证 / design_maturity=production, build_status NOT IN (active, stable) |
| L3 | 🟢 | ✅ | 生产已验证 | Verified | 生产环境稳定运行 / design_maturity=production, build_status IN (active, stable) |

## 能力域定义 / Capability Domain Definitions

| 能力域ID / Capability ID | 中文名 / Chinese | 英文名 / English | 类型 / Type | 包含域数 / Domain Count | 包含域 / Included Domains |
|:---:|--------|--------|:---:|:---:|--------|
| C1 | 数据接入 | Data Ingestion | 业务 | 3 | D_MKT_DATA, D_ALT_DATA, D_DATA_ENG |
| C2 | 因子研究 | Factor & Signal | 业务 | 5 | D_FACTOR, D_SIGLEGACY, D_FUNDAMENTAL_SIGNAL, D_ASHARE_SIGNAL, D_SIGQC |
| C3 | 风险控制 | Risk Control | 业务 | 2 | D_RISK, D_COMPLIANCE |
| C4 | 策略决策 | Strategy Decision | 业务 | 4 | D_PF_CORE, D_PF_ALLOC, D_SELL_DECISION, D_CROSS_ASSET |
| C5 | 执行交易 | Execution & Trading | 业务 | 4 | D_EX_CORE, D_EX_SOR, D_TRADING, D_POSITION |
| C6 | ML平台 | ML Platform | 业务 | 2 | D_ML_TRAIN, D_ML_SERVE |
| C7 | 回测仿真 | Backtest & Simulation | 业务 | 4 | D_BACKTEST, D_SIMULATION, D_EXEC_SIM, D_DIGITAL_TWIN |
| CC1 | 治理合规 | Governance & Compliance | 横切 | 7 | D_GOVERNANCE, D_GOV_RULE, D_GOV_AUDIT, D_GOV_DRIFT, D_GOV_ENFORCEMENT, D_GOV_REPAIR, D_GOV_SCRIPTS |
| CC2 | 安全防护 | Security | 横切 | 5 | D_SECURITY, D_SECURITY_LLM, D_BEHAVIORAL_AUDIT, D_DATA_SEC, D_AUTONOMY_PERM |
| CC3 | 基础设施 | Infrastructure | 横切 | 11 | D_INFRA_OPS, D_INFRA_RUNTIME, D_INTEGRATION, D_INTEGRATION_GATEWAY, D_SHARED, D_FRONTEND, D_REPORTING, D_KNOWLEDGE, D_INTELLIGENCE, D_AUTONOMY_CORE, D_OPS |

## 能力热力图矩阵 / Capability Heatmap Matrix

> 行：架构域（48域） | 列：能力域（10能力域）
> Rows: Architecture Domains (48) | Columns: Capability Domains (10)
> 单元格：成熟度符号（属于该能力域时显示，否则显示 —）
> Cell: Maturity symbol (shown when domain belongs to capability, otherwise —)

| 架构域 / Architecture Domain | 域名称 / Domain Name | C1 | C2 | C3 | C4 | C5 | C6 | C7 | CC1 | CC2 | CC3 | 成熟度 / Maturity |
|--------|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 🔵 | — | — | — | — | — | — | — | — | — | L1 |
| D_DATA_ENG | 数据工程 | 🔵 | — | — | — | — | — | — | — | — | — | L1 |
| D_MKT_DATA | 行情数据 | 🔵 | — | — | — | — | — | — | — | — | — | L1 |
| D_ASHARE_SIGNAL | ashare_signal | — | 🔵 | — | — | — | — | — | — | — | — | L1 |
| D_FACTOR | 因子 | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D_SIGQC | signal_quality | — | 🔵 | — | — | — | — | — | — | — | — | L1 |
| D_RISK | 风控 | — | — | 🟡 | — | — | — | — | — | — | — | L2 |
| D_CROSS_ASSET | 跨资产 | — | — | — | 🟡 | — | — | — | — | — | — | L2 |
| D_PF_ALLOC | 组合分配 | — | — | — | 🔵 | — | — | — | — | — | — | L1 |
| D_PF_CORE | 组合核心 | — | — | — | 🟡 | — | — | — | — | — | — | L2 |
| D_SELL_DECISION | 卖出决策 | — | — | — | 🔵 | — | — | — | — | — | — | L1 |
| D_EX_CORE | 执行核心 | — | — | — | — | 🟡 | — | — | — | — | — | L2 |
| D_EX_SOR | 执行路由 | — | — | — | — | 🔵 | — | — | — | — | — | L1 |
| D_POSITION | 仓位管理 | — | — | — | — | 🟡 | — | — | — | — | — | L2 |
| D_TRADING | 交易运营 | — | — | — | — | 🟡 | — | — | — | — | — | L2 |
| D_ML_SERVE | 推理 | — | — | — | — | — | 🔵 | — | — | — | — | L1 |
| D_ML_TRAIN | model_evaluation | — | — | — | — | — | 🔵 | — | — | — | — | L1 |
| D_BACKTEST | 回测 | — | — | — | — | — | — | 🟡 | — | — | — | L2 |
| D_DIGITAL_TWIN | 数字孪生 | — | — | — | — | — | — | 🔵 | — | — | — | L1 |
| D_EXEC_SIM | 执行仿真 | — | — | — | — | — | — | 🔵 | — | — | — | L1 |
| D_SIMULATION | 仿真 | — | — | — | — | — | — | 🟡 | — | — | — | L2 |
| D_GOVERNANCE | registry_management | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_GOV_AUDIT | audit_orchestration | — | — | — | — | — | — | — | 🔵 | — | — | L1 |
| D_GOV_DRIFT | drift_detection | — | — | — | — | — | — | — | 🔵 | — | — | L1 |
| D_GOV_ENFORCEMENT | rule_enforcement | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_GOV_REPAIR | rollback | — | — | — | — | — | — | — | ⚪ | — | — | L0 |
| D_GOV_RULE | rule_governance | — | — | — | — | — | — | — | ⚪ | — | — | L0 |
| D_AUTONOMY_PERM | budget_enforcement | — | — | — | — | — | — | — | — | 🔵 | — | L1 |
| D_DATA_SEC | 数据安全与契约 | — | — | — | — | — | — | — | — | 🔵 | — | L1 |
| D_SECURITY | orphan_judge | — | — | — | — | — | — | — | — | 🟡 | — | L2 |
| D_SECURITY_LLM | llm_defense | — | — | — | — | — | — | — | — | 🟡 | — | L2 |
| D_AUTONOMY_CORE | agent_lifecycle | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D_FRONTEND | 前端 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D_INFRA_OPS | asset-inventory | — | — | — | — | — | — | — | — | — | 🔵 | L1 |
| D_INFRA_RUNTIME | runtime_core | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_INTEGRATION | pipeline_routing | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D_INTEGRATION_GATEWAY | mcp_servers | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D_INTELLIGENCE | context_management | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D_KNOWLEDGE | vector_storage | — | — | — | — | — | — | — | — | — | 🔵 | L1 |
| D_OPS | telemetry | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D_REPORTING | 报告 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D_SHARED | shared_services | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D_DATA_GOV | 数据治理 | — | — | — | — | — | — | — | — | — | — | L1 |
| D_GOV_DOCS | architecture_docs | — | — | — | — | — | — | — | — | — | — | L2 |
| D_INFRA_A2A | a2a_communication | — | — | — | — | — | — | — | — | — | — | L2 |
| D_INFRA_RECOVERY | rollback_recovery | — | — | — | — | — | — | — | — | — | — | L2 |
| D_INFRA_TELEMETRY | observability_profiling | — | — | — | — | — | — | — | — | — | — | L2 |

## 能力域成熟度汇总 / Capability Domain Maturity Summary

| 能力域 / Capability | 中文名 / Chinese | 域数量 / Domain Count | 总节点 / Total Nodes | production | design | prototype | 平均成熟度 / Avg Maturity | 覆盖度 / Coverage |
|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 | 数据接入 | 3 | 21 | 0 | 0 | 21 | 1.00 | 🟡 部分覆盖 / Partial |
| C2 | 因子研究 | 4 | 54 | 8 | 0 | 46 | 1.50 | 🟡 部分覆盖 / Partial |
| C3 | 风险控制 | 1 | 20 | 9 | 0 | 11 | 2.00 | 🟡 部分覆盖 / Partial |
| C4 | 策略决策 | 4 | 37 | 5 | 2 | 30 | 1.50 | 🟡 部分覆盖 / Partial |
| C5 | 执行交易 | 4 | 511 | 286 | 1 | 224 | 1.75 | 🟡 部分覆盖 / Partial |
| C6 | ML平台 | 2 | 19 | 0 | 1 | 18 | 1.00 | 🟡 部分覆盖 / Partial |
| C7 | 回测仿真 | 4 | 59 | 11 | 10 | 38 | 1.50 | 🟡 部分覆盖 / Partial |
| CC1 | 治理合规 | 6 | 836 | 549 | 31 | 256 | 1.33 | 🟡 部分覆盖 / Partial |
| CC2 | 安全防护 | 4 | 212 | 113 | 0 | 99 | 1.50 | 🟡 部分覆盖 / Partial |
| CC3 | 基础设施 | 11 | 660 | 377 | 9 | 274 | 1.91 | 🟡 部分覆盖 / Partial |

## 域成熟度明细 / Domain Maturity Detail

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 架构层 / Layer | 节点数 / Nodes | production | design | prototype | active | 成熟度 / Maturity | 覆盖度 / Coverage |
|--------|--------|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | C1 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_DATA_ENG | 数据工程 | C1 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_MKT_DATA | 行情数据 | C1 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_ASHARE_SIGNAL | ashare_signal | C2 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_FACTOR | 因子 | C2 | L2_domain | 14 | 4 | 0 | 10 | 0 | L2 🟡 | 🟡 |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal | C2 | L2_domain | 25 | 4 | 0 | 21 | 0 | L2 🟡 | 🟡 |
| D_SIGQC | signal_quality | C2 | L2_domain | 8 | 0 | 0 | 8 | 0 | L1 🔵 | 🟡 |
| D_RISK | 风控 | C3 | L2_domain | 20 | 9 | 0 | 11 | 0 | L2 🟡 | 🟡 |
| D_CROSS_ASSET | 跨资产 | C4 | L2_domain | 8 | 1 | 1 | 6 | 0 | L2 🟡 | 🟡 |
| D_PF_ALLOC | 组合分配 | C4 | L2_domain | 8 | 0 | 1 | 7 | 0 | L1 🔵 | 🟡 |
| D_PF_CORE | 组合核心 | C4 | L2_domain | 14 | 4 | 0 | 10 | 0 | L2 🟡 | 🟡 |
| D_SELL_DECISION | 卖出决策 | C4 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_EX_CORE | 执行核心 | C5 | L2_domain | 15 | 5 | 1 | 9 | 0 | L2 🟡 | 🟡 |
| D_EX_SOR | 执行路由 | C5 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_POSITION | 仓位管理 | C5 | L2_domain | 8 | 1 | 0 | 7 | 0 | L2 🟡 | 🟡 |
| D_TRADING | 交易运营 | C5 | L2_domain | 481 | 280 | 0 | 201 | 0 | L2 🟡 | 🟡 |
| D_ML_SERVE | 推理 | C6 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_ML_TRAIN | model_evaluation | C6 | L2_domain | 12 | 0 | 1 | 11 | 0 | L1 🔵 | 🟡 |
| D_BACKTEST | 回测 | C7 | L2_domain | 33 | 9 | 8 | 16 | 0 | L2 🟡 | 🟡 |
| D_DIGITAL_TWIN | 数字孪生 | C7 | L2_domain | 8 | 0 | 1 | 7 | 0 | L1 🔵 | 🟡 |
| D_EXEC_SIM | 执行仿真 | C7 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_SIMULATION | 仿真 | C7 | L2_domain | 11 | 2 | 1 | 8 | 0 | L2 🟡 | 🟡 |
| D_GOVERNANCE | registry_management | CC1 | L2_domain | 716 | 500 | 28 | 188 | 1 | L3 🟢 | ✅ |
| D_GOV_AUDIT | audit_orchestration | CC1 | L2_domain | 2 | 0 | 2 | 0 | 0 | L1 🔵 | 🟡 |
| D_GOV_DRIFT | drift_detection | CC1 | L2_domain | 1 | 0 | 1 | 0 | 0 | L1 🔵 | 🟡 |
| D_GOV_ENFORCEMENT | rule_enforcement | CC1 | L2_domain | 117 | 49 | 0 | 68 | 1 | L3 🟢 | ✅ |
| D_GOV_REPAIR | rollback | CC1 | L2_domain | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_GOV_RULE | rule_governance | CC1 | L2_domain | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_AUTONOMY_PERM | budget_enforcement | CC2 | L2_domain | 14 | 0 | 0 | 14 | 0 | L1 🔵 | 🟡 |
| D_DATA_SEC | 数据安全与契约 | CC2 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_SECURITY | orphan_judge | CC2 | L1_foundation | 147 | 80 | 0 | 67 | 0 | L2 🟡 | 🟡 |
| D_SECURITY_LLM | llm_defense | CC2 | L1_foundation | 44 | 33 | 0 | 11 | 0 | L2 🟡 | 🟡 |
| D_AUTONOMY_CORE | agent_lifecycle | CC3 | L1_foundation | 114 | 111 | 0 | 3 | 0 | L2 🟡 | 🟡 |
| D_FRONTEND | 前端 | CC3 | L1_foundation | 30 | 13 | 6 | 11 | 0 | L2 🟡 | 🟡 |
| D_INFRA_OPS | asset-inventory | CC3 | L0_infrastructure | 1 | 0 | 1 | 0 | 0 | L1 🔵 | 🟡 |
| D_INFRA_RUNTIME | runtime_core | CC3 | L0_infrastructure | 133 | 87 | 0 | 46 | 4 | L3 🟢 | ✅ |
| D_INTEGRATION | pipeline_routing | CC3 | L1_foundation | 72 | 33 | 0 | 39 | 0 | L2 🟡 | 🟡 |
| D_INTEGRATION_GATEWAY | mcp_servers | CC3 | L1_foundation | 20 | 14 | 0 | 6 | 0 | L2 🟡 | 🟡 |
| D_INTELLIGENCE | context_management | CC3 | L2_domain | 43 | 21 | 0 | 22 | 0 | L2 🟡 | 🟡 |
| D_KNOWLEDGE | vector_storage | CC3 | L2_domain | 9 | 0 | 2 | 7 | 0 | L1 🔵 | 🟡 |
| D_OPS | telemetry | CC3 | L1_foundation | 3 | 3 | 0 | 0 | 0 | L2 🟡 | 🟡 |
| D_REPORTING | 报告 | CC3 | L1_foundation | 10 | 1 | 0 | 9 | 0 | L2 🟡 | 🟡 |
| D_SHARED | shared_services | CC3 | L1_foundation | 225 | 94 | 0 | 131 | 0 | L2 🟡 | 🟡 |
| D_DATA_GOV | 数据治理 | — | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_GOV_DOCS | architecture_docs | — | L2_domain | 2 | 2 | 0 | 0 | 0 | L2 🟡 | 🟡 |
| D_INFRA_A2A | a2a_communication | — | L0_infrastructure | 89 | 32 | 0 | 57 | 0 | L2 🟡 | 🟡 |
| D_INFRA_RECOVERY | rollback_recovery | — | L0_infrastructure | 54 | 48 | 0 | 6 | 0 | L2 🟡 | 🟡 |
| D_INFRA_TELEMETRY | observability_profiling | — | L0_infrastructure | 25 | 13 | 0 | 12 | 0 | L2 🟡 | 🟡 |

## 差距分析 / Gap Analysis

### P0 短板（L0-L1，需优先补齐）/ P0 Gaps (L0-L1, priority)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | C1 | L1 | 7 |
| D_DATA_ENG | 数据工程 | C1 | L1 | 7 |
| D_MKT_DATA | 行情数据 | C1 | L1 | 7 |
| D_ASHARE_SIGNAL | ashare_signal | C2 | L1 | 7 |
| D_SIGQC | signal_quality | C2 | L1 | 8 |
| D_PF_ALLOC | 组合分配 | C4 | L1 | 8 |
| D_SELL_DECISION | 卖出决策 | C4 | L1 | 7 |
| D_EX_SOR | 执行路由 | C5 | L1 | 7 |
| D_ML_SERVE | 推理 | C6 | L1 | 7 |
| D_ML_TRAIN | model_evaluation | C6 | L1 | 12 |
| D_DIGITAL_TWIN | 数字孪生 | C7 | L1 | 8 |
| D_EXEC_SIM | 执行仿真 | C7 | L1 | 7 |
| D_GOV_AUDIT | audit_orchestration | CC1 | L1 | 2 |
| D_GOV_DRIFT | drift_detection | CC1 | L1 | 1 |
| D_GOV_REPAIR | rollback | CC1 | L0 | 0 |
| D_GOV_RULE | rule_governance | CC1 | L0 | 0 |
| D_AUTONOMY_PERM | budget_enforcement | CC2 | L1 | 14 |
| D_DATA_SEC | 数据安全与契约 | CC2 | L1 | 7 |
| D_INFRA_OPS | asset-inventory | CC3 | L1 | 1 |
| D_KNOWLEDGE | vector_storage | CC3 | L1 | 9 |
| D_DATA_GOV | 数据治理 | — | L1 | 7 |

### P1 关注（L2，可用未验证）/ P1 Watch (L2, usable unverified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D_FACTOR | 因子 | C2 | L2 | 14 |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal | C2 | L2 | 25 |
| D_RISK | 风控 | C3 | L2 | 20 |
| D_CROSS_ASSET | 跨资产 | C4 | L2 | 8 |
| D_PF_CORE | 组合核心 | C4 | L2 | 14 |
| D_EX_CORE | 执行核心 | C5 | L2 | 15 |
| D_POSITION | 仓位管理 | C5 | L2 | 8 |
| D_TRADING | 交易运营 | C5 | L2 | 481 |
| D_BACKTEST | 回测 | C7 | L2 | 33 |
| D_SIMULATION | 仿真 | C7 | L2 | 11 |
| D_SECURITY | orphan_judge | CC2 | L2 | 147 |
| D_SECURITY_LLM | llm_defense | CC2 | L2 | 44 |
| D_AUTONOMY_CORE | agent_lifecycle | CC3 | L2 | 114 |
| D_FRONTEND | 前端 | CC3 | L2 | 30 |
| D_INTEGRATION | pipeline_routing | CC3 | L2 | 72 |
| D_INTEGRATION_GATEWAY | mcp_servers | CC3 | L2 | 20 |
| D_INTELLIGENCE | context_management | CC3 | L2 | 43 |
| D_OPS | telemetry | CC3 | L2 | 3 |
| D_REPORTING | 报告 | CC3 | L2 | 10 |
| D_SHARED | shared_services | CC3 | L2 | 225 |
| D_GOV_DOCS | architecture_docs | — | L2 | 2 |
| D_INFRA_A2A | a2a_communication | — | L2 | 89 |
| D_INFRA_RECOVERY | rollback_recovery | — | L2 | 54 |
| D_INFRA_TELEMETRY | observability_profiling | — | L2 | 25 |

### 已就绪（L3，生产已验证）/ Ready (L3, verified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D_GOVERNANCE | registry_management | CC1 | L3 | 716 |
| D_GOV_ENFORCEMENT | rule_enforcement | CC1 | L3 | 117 |
| D_INFRA_RUNTIME | runtime_core | CC3 | L3 | 133 |

## 未映射域 / Unmapped Domains

> 以下域未归属任何能力域，可能需要更新能力域定义
> The following domains are not mapped to any capability domain; capability definitions may need updating

| 架构域 / Architecture Domain | 域名称 / Domain Name | 架构层 / Layer | 节点数 / Nodes | 成熟度 / Maturity |
|--------|--------|--------|:---:|:---:|
| D_DATA_GOV | 数据治理 | L1_foundation | 7 | L1 |
| D_GOV_DOCS | architecture_docs | L2_domain | 2 | L2 |
| D_INFRA_A2A | a2a_communication | L0_infrastructure | 89 | L2 |
| D_INFRA_RECOVERY | rollback_recovery | L0_infrastructure | 54 | L2 |
| D_INFRA_TELEMETRY | observability_profiling | L0_infrastructure | 25 | L2 |
