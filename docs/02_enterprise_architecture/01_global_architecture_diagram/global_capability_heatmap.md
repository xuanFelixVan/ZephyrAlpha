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

> **文档作用 / Purpose**: 以矩阵形式展示59个架构域在10个能力域上的成熟度分布，用于识别能力短板和过度建设。

> 本文档由 generate_capability_heatmap.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) domains表 + nodes表 (注: arch_domain_capacity表不存在，v6已合并入domains表)

## 统计概览 / Statistics Overview

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 / Total Domains | 59 |
| 能力域数 / Capability Domains | 10 |
| L0 缺失 / Missing | 1 |
| L1 设计中 / Designing | 18 |
| L2 可用未验证 / Usable | 37 |
| L3 生产已验证 / Verified | 3 |
| ✅ 完全覆盖 / Full Coverage (L3) | 3 |
| 🟡 部分覆盖 / Partial Coverage (L1-L2) | 55 |
| ❌ 无覆盖 / No Coverage (L0) | 1 |

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

> 行：架构域（59域） | 列：能力域（10能力域）
> Rows: Architecture Domains (59) | Columns: Capability Domains (10)
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
| D_SIGLEGACY | signal_legacy | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D_SIGQC | signal_quality | — | 🔵 | — | — | — | — | — | — | — | — | L1 |
| D_COMPLIANCE | compliance_gate | — | — | 🔵 | — | — | — | — | — | — | — | L1 |
| D_RISK | 风控 | — | — | 🟡 | — | — | — | — | — | — | — | L2 |
| D_CROSS_ASSET | 跨资产 | — | — | — | 🟡 | — | — | — | — | — | — | L2 |
| D_PF_ALLOC | 组合分配 | — | — | — | 🟡 | — | — | — | — | — | — | L2 |
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
| D_GOV_AUDIT | audit_orchestration | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D_GOV_DRIFT | drift_detection | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D_GOV_ENFORCEMENT | rule_enforcement | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_GOV_REPAIR | rollback | — | — | — | — | — | — | — | ⚪ | — | — | L0 |
| D_GOV_RULE | rule_governance | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D_AUTONOMY_PERM | budget_enforcement | — | — | — | — | — | — | — | — | 🔵 | — | L1 |
| D_BEHAVIORAL_AUDIT | drift_detector_core | — | — | — | — | — | — | — | — | 🔵 | — | L1 |
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
| D_DATA | data_source_integrator | — | — | — | — | — | — | — | — | — | — | L2 |
| D_DATA_GOV | 数据治理 | — | — | — | — | — | — | — | — | — | — | L1 |
| D_FBL_VERIFICATION | feedback_verification | — | — | — | — | — | — | — | — | — | — | L2 |
| D_FEEDBACK_LOOP | feedback_loop_engine | — | — | — | — | — | — | — | — | — | — | L2 |
| D_GOV_CODE_QUALITY | code_quality_governance | — | — | — | — | — | — | — | — | — | — | L2 |
| D_GOV_DOCS | architecture_docs | — | — | — | — | — | — | — | — | — | — | L2 |
| D_GOV_KB | knowledge_base_governance | — | — | — | — | — | — | — | — | — | — | L2 |
| D_GOV_OPS_RESILIENCE | ops_resilience_governance | — | — | — | — | — | — | — | — | — | — | L2 |
| D_INFRASTRUCTURE | shared_contracts | — | — | — | — | — | — | — | — | — | — | L2 |
| D_INFRA_A2A | a2a_communication | — | — | — | — | — | — | — | — | — | — | L2 |
| D_INFRA_RECOVERY | rollback_recovery | — | — | — | — | — | — | — | — | — | — | L2 |
| D_INFRA_TELEMETRY | observability_profiling | — | — | — | — | — | — | — | — | — | — | L2 |
| D_ORCHESTRATOR | agent_orchestrator | — | — | — | — | — | — | — | — | — | — | L2 |

## 能力域成熟度汇总 / Capability Domain Maturity Summary

| 能力域 / Capability | 中文名 / Chinese | 域数量 / Domain Count | 总节点 / Total Nodes | production | design | prototype | 平均成熟度 / Avg Maturity | 覆盖度 / Coverage |
|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 | 数据接入 | 3 | 24 | 0 | 3 | 21 | 1.00 | 🟡 部分覆盖 / Partial |
| C2 | 因子研究 | 5 | 54 | 8 | 0 | 46 | 1.60 | 🟡 部分覆盖 / Partial |
| C3 | 风险控制 | 2 | 44 | 9 | 0 | 35 | 1.50 | 🟡 部分覆盖 / Partial |
| C4 | 策略决策 | 4 | 37 | 5 | 2 | 30 | 1.75 | 🟡 部分覆盖 / Partial |
| C5 | 执行交易 | 4 | 74 | 26 | 1 | 47 | 1.75 | 🟡 部分覆盖 / Partial |
| C6 | ML平台 | 2 | 12 | 0 | 1 | 11 | 1.00 | 🟡 部分覆盖 / Partial |
| C7 | 回测仿真 | 4 | 59 | 11 | 10 | 38 | 1.50 | 🟡 部分覆盖 / Partial |
| CC1 | 治理合规 | 6 | 538 | 389 | 6 | 143 | 2.00 | 🟡 部分覆盖 / Partial |
| CC2 | 安全防护 | 5 | 215 | 106 | 0 | 109 | 1.40 | 🟡 部分覆盖 / Partial |
| CC3 | 基础设施 | 11 | 766 | 489 | 13 | 264 | 1.91 | 🟡 部分覆盖 / Partial |

## 域成熟度明细 / Domain Maturity Detail

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 架构层 / Layer | 节点数 / Nodes | production | design | prototype | active | 成熟度 / Maturity | 覆盖度 / Coverage |
|--------|--------|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | C1 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_DATA_ENG | 数据工程 | C1 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_MKT_DATA | 行情数据 | C1 | L1_foundation | 10 | 0 | 3 | 7 | 0 | L1 🔵 | 🟡 |
| D_ASHARE_SIGNAL | ashare_signal | C2 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_FACTOR | 因子 | C2 | L2_domain | 14 | 4 | 0 | 10 | 0 | L2 🟡 | 🟡 |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal | C2 | L2_domain | 9 | 3 | 0 | 6 | 0 | L2 🟡 | 🟡 |
| D_SIGLEGACY | signal_legacy | C2 |  | 16 | 1 | 0 | 15 | 0 | L2 🟡 | 🟡 |
| D_SIGQC | signal_quality | C2 | L2_domain | 8 | 0 | 0 | 8 | 0 | L1 🔵 | 🟡 |
| D_COMPLIANCE | compliance_gate | C3 |  | 24 | 0 | 0 | 24 | 0 | L1 🔵 | 🟡 |
| D_RISK | 风控 | C3 | L2_domain | 20 | 9 | 0 | 11 | 0 | L2 🟡 | 🟡 |
| D_CROSS_ASSET | 跨资产 | C4 | L2_domain | 8 | 1 | 1 | 6 | 0 | L2 🟡 | 🟡 |
| D_PF_ALLOC | 组合分配 | C4 | L2_domain | 9 | 1 | 1 | 7 | 0 | L2 🟡 | 🟡 |
| D_PF_CORE | 组合核心 | C4 | L2_domain | 13 | 3 | 0 | 10 | 0 | L2 🟡 | 🟡 |
| D_SELL_DECISION | 卖出决策 | C4 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_EX_CORE | 执行核心 | C5 | L2_domain | 16 | 6 | 1 | 9 | 0 | L2 🟡 | 🟡 |
| D_EX_SOR | 执行路由 | C5 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_POSITION | 仓位管理 | C5 | L2_domain | 8 | 1 | 0 | 7 | 0 | L2 🟡 | 🟡 |
| D_TRADING | 交易运营 | C5 | L2_domain | 43 | 19 | 0 | 24 | 0 | L2 🟡 | 🟡 |
| D_ML_SERVE | 推理 | C6 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_ML_TRAIN | model_evaluation | C6 | L2_domain | 5 | 0 | 1 | 4 | 0 | L1 🔵 | 🟡 |
| D_BACKTEST | 回测 | C7 | L2_domain | 33 | 9 | 8 | 16 | 0 | L2 🟡 | 🟡 |
| D_DIGITAL_TWIN | 数字孪生 | C7 | L2_domain | 8 | 0 | 1 | 7 | 0 | L1 🔵 | 🟡 |
| D_EXEC_SIM | 执行仿真 | C7 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_SIMULATION | 仿真 | C7 | L2_domain | 11 | 2 | 1 | 8 | 0 | L2 🟡 | 🟡 |
| D_GOVERNANCE | registry_management | CC1 | L2_domain | 199 | 126 | 3 | 70 | 1 | L3 🟢 | ✅ |
| D_GOV_AUDIT | audit_orchestration | CC1 | L2_domain | 119 | 66 | 2 | 51 | 0 | L2 🟡 | 🟡 |
| D_GOV_DRIFT | drift_detection | CC1 | L2_domain | 72 | 67 | 1 | 4 | 0 | L2 🟡 | 🟡 |
| D_GOV_ENFORCEMENT | rule_enforcement | CC1 | L2_domain | 116 | 100 | 0 | 16 | 1 | L3 🟢 | ✅ |
| D_GOV_REPAIR | rollback | CC1 | L2_domain | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_GOV_RULE | rule_governance | CC1 | L2_domain | 32 | 30 | 0 | 2 | 0 | L2 🟡 | 🟡 |
| D_AUTONOMY_PERM | budget_enforcement | CC2 | L2_domain | 14 | 0 | 0 | 14 | 0 | L1 🔵 | 🟡 |
| D_BEHAVIORAL_AUDIT | drift_detector_core | CC2 |  | 1 | 0 | 0 | 1 | 0 | L1 🔵 | 🟡 |
| D_DATA_SEC | 数据安全与契约 | CC2 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_SECURITY | orphan_judge | CC2 | L1_foundation | 180 | 101 | 0 | 79 | 0 | L2 🟡 | 🟡 |
| D_SECURITY_LLM | llm_defense | CC2 | L1_foundation | 13 | 5 | 0 | 8 | 0 | L2 🟡 | 🟡 |
| D_AUTONOMY_CORE | agent_lifecycle | CC3 | L1_foundation | 137 | 133 | 0 | 4 | 0 | L2 🟡 | 🟡 |
| D_FRONTEND | 前端 | CC3 | L1_foundation | 30 | 13 | 6 | 11 | 0 | L2 🟡 | 🟡 |
| D_INFRA_OPS | asset-inventory | CC3 | L0_infrastructure | 2 | 0 | 2 | 0 | 0 | L1 🔵 | 🟡 |
| D_INFRA_RUNTIME | runtime_core | CC3 | L0_infrastructure | 219 | 135 | 3 | 81 | 4 | L3 🟢 | ✅ |
| D_INTEGRATION | pipeline_routing | CC3 | L1_foundation | 87 | 46 | 0 | 41 | 0 | L2 🟡 | 🟡 |
| D_INTEGRATION_GATEWAY | mcp_servers | CC3 | L1_foundation | 2 | 1 | 0 | 1 | 0 | L2 🟡 | 🟡 |
| D_INTELLIGENCE | context_management | CC3 | L2_domain | 50 | 21 | 0 | 29 | 0 | L2 🟡 | 🟡 |
| D_KNOWLEDGE | vector_storage | CC3 | L2_domain | 9 | 0 | 2 | 7 | 0 | L1 🔵 | 🟡 |
| D_OPS | telemetry | CC3 | L1_foundation | 8 | 7 | 0 | 1 | 0 | L2 🟡 | 🟡 |
| D_REPORTING | 报告 | CC3 | L1_foundation | 10 | 1 | 0 | 9 | 0 | L2 🟡 | 🟡 |
| D_SHARED | shared_services | CC3 | L1_foundation | 212 | 132 | 0 | 80 | 0 | L2 🟡 | 🟡 |
| D_DATA | data_source_integrator | — |  | 29 | 6 | 0 | 23 | 0 | L2 🟡 | 🟡 |
| D_DATA_GOV | 数据治理 | — | L1_foundation | 30 | 0 | 0 | 30 | 0 | L1 🔵 | 🟡 |
| D_FBL_VERIFICATION | feedback_verification | — | L1_foundation | 71 | 67 | 0 | 4 | 0 | L2 🟡 | 🟡 |
| D_FEEDBACK_LOOP | feedback_loop_engine | — | L1_foundation | 253 | 107 | 0 | 146 | 0 | L2 🟡 | 🟡 |
| D_GOV_CODE_QUALITY | code_quality_governance | — | L1_foundation | 107 | 100 | 0 | 7 | 0 | L2 🟡 | 🟡 |
| D_GOV_DOCS | architecture_docs | — | L2_domain | 96 | 68 | 28 | 0 | 0 | L2 🟡 | 🟡 |
| D_GOV_KB | knowledge_base_governance | — | L2_domain | 30 | 16 | 0 | 14 | 0 | L2 🟡 | 🟡 |
| D_GOV_OPS_RESILIENCE | ops_resilience_governance | — | L1_foundation | 79 | 76 | 0 | 3 | 0 | L2 🟡 | 🟡 |
| D_INFRASTRUCTURE | shared_contracts | — |  | 37 | 9 | 0 | 28 | 0 | L2 🟡 | 🟡 |
| D_INFRA_A2A | a2a_communication | — | L0_infrastructure | 77 | 29 | 0 | 48 | 0 | L2 🟡 | 🟡 |
| D_INFRA_RECOVERY | rollback_recovery | — | L0_infrastructure | 54 | 48 | 0 | 6 | 0 | L2 🟡 | 🟡 |
| D_INFRA_TELEMETRY | observability_profiling | — | L0_infrastructure | 10 | 8 | 0 | 2 | 0 | L2 🟡 | 🟡 |
| D_ORCHESTRATOR | agent_orchestrator | — | L1_foundation | 70 | 58 | 0 | 12 | 0 | L2 🟡 | 🟡 |

## 差距分析 / Gap Analysis

### P0 短板（L0-L1，需优先补齐）/ P0 Gaps (L0-L1, priority)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | C1 | L1 | 7 |
| D_DATA_ENG | 数据工程 | C1 | L1 | 7 |
| D_MKT_DATA | 行情数据 | C1 | L1 | 10 |
| D_ASHARE_SIGNAL | ashare_signal | C2 | L1 | 7 |
| D_SIGQC | signal_quality | C2 | L1 | 8 |
| D_COMPLIANCE | compliance_gate | C3 | L1 | 24 |
| D_SELL_DECISION | 卖出决策 | C4 | L1 | 7 |
| D_EX_SOR | 执行路由 | C5 | L1 | 7 |
| D_ML_SERVE | 推理 | C6 | L1 | 7 |
| D_ML_TRAIN | model_evaluation | C6 | L1 | 5 |
| D_DIGITAL_TWIN | 数字孪生 | C7 | L1 | 8 |
| D_EXEC_SIM | 执行仿真 | C7 | L1 | 7 |
| D_GOV_REPAIR | rollback | CC1 | L0 | 0 |
| D_AUTONOMY_PERM | budget_enforcement | CC2 | L1 | 14 |
| D_BEHAVIORAL_AUDIT | drift_detector_core | CC2 | L1 | 1 |
| D_DATA_SEC | 数据安全与契约 | CC2 | L1 | 7 |
| D_INFRA_OPS | asset-inventory | CC3 | L1 | 2 |
| D_KNOWLEDGE | vector_storage | CC3 | L1 | 9 |
| D_DATA_GOV | 数据治理 | — | L1 | 30 |

### P1 关注（L2，可用未验证）/ P1 Watch (L2, usable unverified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D_FACTOR | 因子 | C2 | L2 | 14 |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal | C2 | L2 | 9 |
| D_SIGLEGACY | signal_legacy | C2 | L2 | 16 |
| D_RISK | 风控 | C3 | L2 | 20 |
| D_CROSS_ASSET | 跨资产 | C4 | L2 | 8 |
| D_PF_ALLOC | 组合分配 | C4 | L2 | 9 |
| D_PF_CORE | 组合核心 | C4 | L2 | 13 |
| D_EX_CORE | 执行核心 | C5 | L2 | 16 |
| D_POSITION | 仓位管理 | C5 | L2 | 8 |
| D_TRADING | 交易运营 | C5 | L2 | 43 |
| D_BACKTEST | 回测 | C7 | L2 | 33 |
| D_SIMULATION | 仿真 | C7 | L2 | 11 |
| D_GOV_AUDIT | audit_orchestration | CC1 | L2 | 119 |
| D_GOV_DRIFT | drift_detection | CC1 | L2 | 72 |
| D_GOV_RULE | rule_governance | CC1 | L2 | 32 |
| D_SECURITY | orphan_judge | CC2 | L2 | 180 |
| D_SECURITY_LLM | llm_defense | CC2 | L2 | 13 |
| D_AUTONOMY_CORE | agent_lifecycle | CC3 | L2 | 137 |
| D_FRONTEND | 前端 | CC3 | L2 | 30 |
| D_INTEGRATION | pipeline_routing | CC3 | L2 | 87 |
| D_INTEGRATION_GATEWAY | mcp_servers | CC3 | L2 | 2 |
| D_INTELLIGENCE | context_management | CC3 | L2 | 50 |
| D_OPS | telemetry | CC3 | L2 | 8 |
| D_REPORTING | 报告 | CC3 | L2 | 10 |
| D_SHARED | shared_services | CC3 | L2 | 212 |
| D_DATA | data_source_integrator | — | L2 | 29 |
| D_FBL_VERIFICATION | feedback_verification | — | L2 | 71 |
| D_FEEDBACK_LOOP | feedback_loop_engine | — | L2 | 253 |
| D_GOV_CODE_QUALITY | code_quality_governance | — | L2 | 107 |
| D_GOV_DOCS | architecture_docs | — | L2 | 96 |
| D_GOV_KB | knowledge_base_governance | — | L2 | 30 |
| D_GOV_OPS_RESILIENCE | ops_resilience_governance | — | L2 | 79 |
| D_INFRASTRUCTURE | shared_contracts | — | L2 | 37 |
| D_INFRA_A2A | a2a_communication | — | L2 | 77 |
| D_INFRA_RECOVERY | rollback_recovery | — | L2 | 54 |
| D_INFRA_TELEMETRY | observability_profiling | — | L2 | 10 |
| D_ORCHESTRATOR | agent_orchestrator | — | L2 | 70 |

### 已就绪（L3，生产已验证）/ Ready (L3, verified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D_GOVERNANCE | registry_management | CC1 | L3 | 199 |
| D_GOV_ENFORCEMENT | rule_enforcement | CC1 | L3 | 116 |
| D_INFRA_RUNTIME | runtime_core | CC3 | L3 | 219 |

## 未映射域 / Unmapped Domains

> 以下域未归属任何能力域，可能需要更新能力域定义
> The following domains are not mapped to any capability domain; capability definitions may need updating

| 架构域 / Architecture Domain | 域名称 / Domain Name | 架构层 / Layer | 节点数 / Nodes | 成熟度 / Maturity |
|--------|--------|--------|:---:|:---:|
| D_DATA | data_source_integrator |  | 29 | L2 |
| D_DATA_GOV | 数据治理 | L1_foundation | 30 | L1 |
| D_FBL_VERIFICATION | feedback_verification | L1_foundation | 71 | L2 |
| D_FEEDBACK_LOOP | feedback_loop_engine | L1_foundation | 253 | L2 |
| D_GOV_CODE_QUALITY | code_quality_governance | L1_foundation | 107 | L2 |
| D_GOV_DOCS | architecture_docs | L2_domain | 96 | L2 |
| D_GOV_KB | knowledge_base_governance | L2_domain | 30 | L2 |
| D_GOV_OPS_RESILIENCE | ops_resilience_governance | L1_foundation | 79 | L2 |
| D_INFRASTRUCTURE | shared_contracts |  | 37 | L2 |
| D_INFRA_A2A | a2a_communication | L0_infrastructure | 77 | L2 |
| D_INFRA_RECOVERY | rollback_recovery | L0_infrastructure | 54 | L2 |
| D_INFRA_TELEMETRY | observability_profiling | L0_infrastructure | 10 | L2 |
| D_ORCHESTRATOR | agent_orchestrator | L1_foundation | 70 | L2 |
