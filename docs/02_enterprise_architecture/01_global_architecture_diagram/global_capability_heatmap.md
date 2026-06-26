---
doc_type: architecture_view
title: 能力热力图
version: "1.0"
status: active
date: 2026-06-26
owner: auto-generator
ttl: permanent
---

# 能力热力图 / Capability Heatmap

> **文档作用 / Purpose**: 以矩阵形式展示43个架构域在10个能力域上的成熟度分布，用于识别能力短板和过度建设。

> 本文档由 generate_capability_heatmap.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-26 18:51:27
> 数据源: depgraph.db domains表 + nodes表 (注: arch_domain_capacity表不存在，v6已合并入domains表)

## 统计概览 / Statistics Overview

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 / Total Domains | 53 |
| 能力域数 / Capability Domains | 10 |
| L0 缺失 / Missing | 5 |
| L1 设计中 / Designing | 14 |
| L2 可用未验证 / Usable | 34 |
| L3 生产已验证 / Verified | 0 |
| ✅ 完全覆盖 / Full Coverage (L3) | 0 |
| 🟡 部分覆盖 / Partial Coverage (L1-L2) | 48 |
| ❌ 无覆盖 / No Coverage (L0) | 5 |

## 成熟度图例 / Maturity Legend

| 等级 / Level | 符号 / Symbol | 覆盖度 / Coverage | 中文名 / Chinese | 英文名 / English | 定义 / Definition |
|:---:|:---:|:---:|--------|--------|------|
| L0 | ⚪ | ❌ | 缺失 | Missing | 能力完全不存在，无设计无代码 / No nodes in domain |
| L1 | 🔵 | 🟡 | 设计中 | Designing | 有设计文档或原型代码，未集成 / design_maturity=design or prototype |
| L2 | 🟡 | 🟡 | 可用未验证 | Usable | 代码可用但未生产验证 / design_maturity=production, build_status!=active |
| L3 | 🟢 | ✅ | 生产已验证 | Verified | 生产环境稳定运行 / design_maturity=production, build_status=active |

## 能力域定义 / Capability Domain Definitions

| 能力域ID / Capability ID | 中文名 / Chinese | 英文名 / English | 类型 / Type | 包含域数 / Domain Count | 包含域 / Included Domains |
|:---:|--------|--------|:---:|:---:|--------|
| C1 | 数据接入 | Data Ingestion | 业务 | 3 | D-MKT_DATA, D-ALT_DATA, D-DATA_ENG |
| C2 | 因子研究 | Factor & Signal | 业务 | 5 | D-FACTOR, D-SIGLEGACY, D-FUNDAMENTAL_SIGNAL, D-ASHARE_SIGNAL, D-SIGQC |
| C3 | 风险控制 | Risk Control | 业务 | 2 | D-RISK, D-COMPLIANCE |
| C4 | 策略决策 | Strategy Decision | 业务 | 4 | D-PF_CORE, D-PF_ALLOC, D-SELL_DECISION, D-CROSS_ASSET |
| C5 | 执行交易 | Execution & Trading | 业务 | 4 | D-EX_CORE, D-EX_SOR, D-TRADING, D-POSITION |
| C6 | ML平台 | ML Platform | 业务 | 2 | D-ML_TRAIN, D-ML_SERVE |
| C7 | 回测仿真 | Backtest & Simulation | 业务 | 4 | D-BACKTEST, D-SIMULATION, D-EXEC_SIM, D-DIGITAL_TWIN |
| CC1 | 治理合规 | Governance & Compliance | 横切 | 7 | D-GOVERNANCE, D-GOV_RULE, D-GOV_AUDIT, D-GOV_DRIFT, D-GOV_ENFORCEMENT, D-GOV_REPAIR, D-GOV_SCRIPTS |
| CC2 | 安全防护 | Security | 横切 | 5 | D-SECURITY, D-SECURITY_LLM, D-BEHAVIORAL_AUDIT, D-DATA_SEC, D-AUTONOMY_PERM |
| CC3 | 基础设施 | Infrastructure | 横切 | 11 | D-INFRA_OPS, D-INFRA_RUNTIME, D-INTEGRATION, D-INTEGRATION_GATEWAY, D-SHARED, D-FRONTEND, D-REPORTING, D-KNOWLEDGE, D-INTELLIGENCE, D-AUTONOMY_CORE, D-OPS |

## 能力热力图矩阵 / Capability Heatmap Matrix

> 行：架构域（43域） | 列：能力域（10能力域）
> Rows: Architecture Domains (43) | Columns: Capability Domains (10)
> 单元格：成熟度符号（属于该能力域时显示，否则显示 —）
> Cell: Maturity symbol (shown when domain belongs to capability, otherwise —)

| 架构域 / Architecture Domain | 域名称 / Domain Name | C1 | C2 | C3 | C4 | C5 | C6 | C7 | CC1 | CC2 | CC3 | 成熟度 / Maturity |
|--------|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | 🟡 | — | — | — | — | — | — | — | — | — | L2 |
| D-DATA_ENG | 数据工程 | 🔵 | — | — | — | — | — | — | — | — | — | L1 |
| D-MKT_DATA | 行情数据 | 🟡 | — | — | — | — | — | — | — | — | — | L2 |
| D-ASHARE_SIGNAL | A股特色信号 | — | 🔵 | — | — | — | — | — | — | — | — | L1 |
| D-FACTOR | 因子 | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D-FUNDAMENTAL_SIGNAL | 基本面信号 | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D-SIGLEGACY | 信号遗留设计态 | — | ⚪ | — | — | — | — | — | — | — | — | L0 |
| D-SIGQC | 信号质量控制 | — | 🔵 | — | — | — | — | — | — | — | — | L1 |
| D-COMPLIANCE | 合规 | — | — | 🔵 | — | — | — | — | — | — | — | L1 |
| D-RISK | 风控 | — | — | 🟡 | — | — | — | — | — | — | — | L2 |
| D-CROSS_ASSET | 跨资产 | — | — | — | 🟡 | — | — | — | — | — | — | L2 |
| D-PF_ALLOC | 组合分配 | — | — | — | 🔵 | — | — | — | — | — | — | L1 |
| D-PF_CORE | 组合核心 | — | — | — | 🟡 | — | — | — | — | — | — | L2 |
| D-SELL_DECISION | 卖出决策 | — | — | — | 🔵 | — | — | — | — | — | — | L1 |
| D-EX_CORE | 执行核心 | — | — | — | — | 🟡 | — | — | — | — | — | L2 |
| D-EX_SOR | 执行路由 | — | — | — | — | 🔵 | — | — | — | — | — | L1 |
| D-POSITION | 仓位管理 | — | — | — | — | 🔵 | — | — | — | — | — | L1 |
| D-TRADING | 交易运营 | — | — | — | — | 🟡 | — | — | — | — | — | L2 |
| D-ML_SERVE | 推理 | — | — | — | — | — | 🔵 | — | — | — | — | L1 |
| D-ML_TRAIN | 训练 | — | — | — | — | — | 🔵 | — | — | — | — | L1 |
| D-BACKTEST | 回测 | — | — | — | — | — | — | 🔵 | — | — | — | L1 |
| D-DIGITAL_TWIN | 数字孪生 | — | — | — | — | — | — | 🔵 | — | — | — | L1 |
| D-EXEC_SIM | 执行仿真 | — | — | — | — | — | — | 🔵 | — | — | — | L1 |
| D-SIMULATION | 仿真 | — | — | — | — | — | — | 🟡 | — | — | — | L2 |
| D-GOV-REPAIR | rollback | — | — | — | — | — | — | — | ⚪ | — | — | L0 |
| D-GOVERNANCE | 生命周期管理 | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D-GOV_AUDIT | 审计追踪 | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D-GOV_DRIFT | 漂移检测 | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D-GOV_ENFORCEMENT | rule_enforcement | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D-GOV_RULE | 规则治理 | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D-GOV_SCRIPTS | code_dedup | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D-AUTONOMY_PERM | 自治保护 | — | — | — | — | — | — | — | — | 🟡 | — | L2 |
| D-BEHAVIORAL_AUDIT | 行为审计 | — | — | — | — | — | — | — | — | 🟡 | — | L2 |
| D-DATA_SEC | 数据安全与契约 | — | — | — | — | — | — | — | — | 🔵 | — | L1 |
| D-SECURITY | 对抗验证 | — | — | — | — | — | — | — | — | 🟡 | — | L2 |
| D-SECURITY_LLM | llm_defense | — | — | — | — | — | — | — | — | ⚪ | — | L0 |
| D-AUTONOMY_CORE | 自治核心 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-FRONTEND | 前端 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-INFRA_OPS | 基础设施运维 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-INFRA_RUNTIME | 运行时集成 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-INTEGRATION | 管线路由 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-INTEGRATION_GATEWAY | mcp_servers | — | — | — | — | — | — | — | — | — | ⚪ | L0 |
| D-INTELLIGENCE | 上下文管理 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-KNOWLEDGE | 知识管理 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-OPS | 反馈循环 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-REPORTING | 报告 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-SHARED | 共享服务 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-AUDITTEST | audit_test_suite | — | — | — | — | — | — | — | — | — | — | L2 |
| D-DATA_GOV | 数据治理 | — | — | — | — | — | — | — | — | — | — | L0 |
| D-GOV_DOCS | architecture_docs | — | — | — | — | — | — | — | — | — | — | L2 |
| D-INFRA_A2A | a2a_communication | — | — | — | — | — | — | — | — | — | — | L2 |
| D-INFRA_RECOVERY | rollback_recovery | — | — | — | — | — | — | — | — | — | — | L2 |
| D-INFRA_TELEMETRY | observability_profiling | — | — | — | — | — | — | — | — | — | — | L2 |

## 能力域成熟度汇总 / Capability Domain Maturity Summary

| 能力域 / Capability | 中文名 / Chinese | 域数量 / Domain Count | 总节点 / Total Nodes | production | design | prototype | 平均成熟度 / Avg Maturity | 覆盖度 / Coverage |
|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 | 数据接入 | 3 | 24 | 2 | 0 | 22 | 1.67 | 🟡 部分覆盖 / Partial |
| C2 | 因子研究 | 5 | 56 | 6 | 0 | 50 | 1.20 | 🟡 部分覆盖 / Partial |
| C3 | 风险控制 | 2 | 50 | 9 | 0 | 41 | 1.50 | 🟡 部分覆盖 / Partial |
| C4 | 策略决策 | 4 | 73 | 7 | 28 | 38 | 1.50 | 🟡 部分覆盖 / Partial |
| C5 | 执行交易 | 4 | 192 | 23 | 0 | 169 | 1.50 | 🟡 部分覆盖 / Partial |
| C6 | ML平台 | 2 | 19 | 0 | 1 | 18 | 1.00 | 🟡 部分覆盖 / Partial |
| C7 | 回测仿真 | 4 | 41 | 4 | 2 | 35 | 1.25 | 🟡 部分覆盖 / Partial |
| CC1 | 治理合规 | 7 | 3577 | 286 | 53 | 3238 | 1.71 | 🟡 部分覆盖 / Partial |
| CC2 | 安全防护 | 5 | 403 | 213 | 1 | 189 | 1.40 | 🟡 部分覆盖 / Partial |
| CC3 | 基础设施 | 11 | 1515 | 362 | 4 | 1149 | 1.82 | 🟡 部分覆盖 / Partial |

## 域成熟度明细 / Domain Maturity Detail

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 架构层 / Layer | 节点数 / Nodes | production | design | prototype | active | 成熟度 / Maturity | 覆盖度 / Coverage |
|--------|--------|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | C1 | L1_foundation | 8 | 1 | 0 | 7 | 0 | L2 🟡 | 🟡 |
| D-DATA_ENG | 数据工程 | C1 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D-MKT_DATA | 行情数据 | C1 | L1_foundation | 9 | 1 | 0 | 8 | 0 | L2 🟡 | 🟡 |
| D-ASHARE_SIGNAL | A股特色信号 | C2 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D-FACTOR | 因子 | C2 | L2_domain | 17 | 2 | 0 | 15 | 0 | L2 🟡 | 🟡 |
| D-FUNDAMENTAL_SIGNAL | 基本面信号 | C2 | L2_domain | 25 | 4 | 0 | 21 | 0 | L2 🟡 | 🟡 |
| D-SIGLEGACY | 信号遗留设计态 | C2 | L2_domain | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D-SIGQC | 信号质量控制 | C2 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D-COMPLIANCE | 合规 | C3 | L2_domain | 25 | 0 | 0 | 25 | 0 | L1 🔵 | 🟡 |
| D-RISK | 风控 | C3 | L2_domain | 25 | 9 | 0 | 16 | 0 | L2 🟡 | 🟡 |
| D-CROSS_ASSET | 跨资产 | C4 | L2_domain | 11 | 1 | 1 | 9 | 0 | L2 🟡 | 🟡 |
| D-PF_ALLOC | 组合分配 | C4 | L2_domain | 11 | 0 | 1 | 10 | 0 | L1 🔵 | 🟡 |
| D-PF_CORE | 组合核心 | C4 | L2_domain | 44 | 6 | 26 | 12 | 0 | L2 🟡 | 🟡 |
| D-SELL_DECISION | 卖出决策 | C4 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D-EX_CORE | 执行核心 | C5 | L2_domain | 14 | 3 | 0 | 11 | 0 | L2 🟡 | 🟡 |
| D-EX_SOR | 执行路由 | C5 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D-POSITION | 仓位管理 | C5 | L2_domain | 8 | 0 | 0 | 8 | 0 | L1 🔵 | 🟡 |
| D-TRADING | 交易运营 | C5 | L2_domain | 163 | 20 | 0 | 143 | 0 | L2 🟡 | 🟡 |
| D-ML_SERVE | 推理 | C6 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D-ML_TRAIN | 训练 | C6 | L2_domain | 12 | 0 | 1 | 11 | 0 | L1 🔵 | 🟡 |
| D-BACKTEST | 回测 | C7 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D-DIGITAL_TWIN | 数字孪生 | C7 | L2_domain | 8 | 0 | 1 | 7 | 0 | L1 🔵 | 🟡 |
| D-EXEC_SIM | 执行仿真 | C7 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D-SIMULATION | 仿真 | C7 | L2_domain | 19 | 4 | 1 | 14 | 0 | L2 🟡 | 🟡 |
| D-GOV-REPAIR | rollback | CC1 |  | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D-GOVERNANCE | 生命周期管理 | CC1 | L2_domain | 2831 | 117 | 50 | 2664 | 0 | L2 🟡 | 🟡 |
| D-GOV_AUDIT | 审计追踪 | CC1 | L2_domain | 188 | 54 | 2 | 132 | 0 | L2 🟡 | 🟡 |
| D-GOV_DRIFT | 漂移检测 | CC1 | L2_domain | 24 | 9 | 1 | 14 | 0 | L2 🟡 | 🟡 |
| D-GOV_ENFORCEMENT | rule_enforcement | CC1 | L2_domain | 107 | 69 | 0 | 38 | 0 | L2 🟡 | 🟡 |
| D-GOV_RULE | 规则治理 | CC1 | L2_domain | 11 | 11 | 0 | 0 | 0 | L2 🟡 | 🟡 |
| D-GOV_SCRIPTS | code_dedup | CC1 | L2_domain | 416 | 26 | 0 | 390 | 0 | L2 🟡 | 🟡 |
| D-AUTONOMY_PERM | 自治保护 | CC2 | L2_domain | 70 | 2 | 1 | 67 | 0 | L2 🟡 | 🟡 |
| D-BEHAVIORAL_AUDIT | 行为审计 | CC2 | L1_foundation | 79 | 79 | 0 | 0 | 0 | L2 🟡 | 🟡 |
| D-DATA_SEC | 数据安全与契约 | CC2 | L1_foundation | 10 | 0 | 0 | 10 | 0 | L1 🔵 | 🟡 |
| D-SECURITY | 对抗验证 | CC2 | L1_foundation | 244 | 132 | 0 | 112 | 0 | L2 🟡 | 🟡 |
| D-SECURITY_LLM | llm_defense | CC2 | L1_foundation | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D-AUTONOMY_CORE | 自治核心 | CC3 | L1_foundation | 176 | 2 | 0 | 174 | 0 | L2 🟡 | 🟡 |
| D-FRONTEND | 前端 | CC3 | L1_foundation | 23 | 7 | 0 | 16 | 0 | L2 🟡 | 🟡 |
| D-INFRA_OPS | 基础设施运维 | CC3 | L0_infrastructure | 34 | 7 | 1 | 26 | 0 | L2 🟡 | 🟡 |
| D-INFRA_RUNTIME | 运行时集成 | CC3 | L0_infrastructure | 145 | 139 | 0 | 6 | 0 | L2 🟡 | 🟡 |
| D-INTEGRATION | 管线路由 | CC3 | L1_foundation | 296 | 70 | 0 | 226 | 0 | L2 🟡 | 🟡 |
| D-INTEGRATION_GATEWAY | mcp_servers | CC3 | L1_foundation | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D-INTELLIGENCE | 上下文管理 | CC3 | L2_domain | 56 | 18 | 0 | 38 | 0 | L2 🟡 | 🟡 |
| D-KNOWLEDGE | 知识管理 | CC3 | L2_domain | 41 | 1 | 2 | 38 | 0 | L2 🟡 | 🟡 |
| D-OPS | 反馈循环 | CC3 | L1_foundation | 433 | 24 | 1 | 408 | 0 | L2 🟡 | 🟡 |
| D-REPORTING | 报告 | CC3 | L1_foundation | 15 | 1 | 0 | 14 | 0 | L2 🟡 | 🟡 |
| D-SHARED | 共享服务 | CC3 | L1_foundation | 296 | 93 | 0 | 203 | 0 | L2 🟡 | 🟡 |
| D-AUDITTEST | audit_test_suite | — | L2_domain | 152 | 142 | 0 | 10 | 0 | L2 🟡 | 🟡 |
| D-DATA_GOV | 数据治理 | — | L1_foundation | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D-GOV_DOCS | architecture_docs | — | L2_domain | 127 | 78 | 0 | 49 | 0 | L2 🟡 | 🟡 |
| D-INFRA_A2A | a2a_communication | — | L0_infrastructure | 114 | 114 | 0 | 0 | 0 | L2 🟡 | 🟡 |
| D-INFRA_RECOVERY | rollback_recovery | — | L0_infrastructure | 107 | 107 | 0 | 0 | 0 | L2 🟡 | 🟡 |
| D-INFRA_TELEMETRY | observability_profiling | — | L0_infrastructure | 51 | 51 | 0 | 0 | 0 | L2 🟡 | 🟡 |

## 差距分析 / Gap Analysis

### P0 短板（L0-L1，需优先补齐）/ P0 Gaps (L0-L1, priority)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D-DATA_ENG | 数据工程 | C1 | L1 | 7 |
| D-ASHARE_SIGNAL | A股特色信号 | C2 | L1 | 7 |
| D-SIGLEGACY | 信号遗留设计态 | C2 | L0 | 0 |
| D-SIGQC | 信号质量控制 | C2 | L1 | 7 |
| D-COMPLIANCE | 合规 | C3 | L1 | 25 |
| D-PF_ALLOC | 组合分配 | C4 | L1 | 11 |
| D-SELL_DECISION | 卖出决策 | C4 | L1 | 7 |
| D-EX_SOR | 执行路由 | C5 | L1 | 7 |
| D-POSITION | 仓位管理 | C5 | L1 | 8 |
| D-ML_SERVE | 推理 | C6 | L1 | 7 |
| D-ML_TRAIN | 训练 | C6 | L1 | 12 |
| D-BACKTEST | 回测 | C7 | L1 | 7 |
| D-DIGITAL_TWIN | 数字孪生 | C7 | L1 | 8 |
| D-EXEC_SIM | 执行仿真 | C7 | L1 | 7 |
| D-GOV-REPAIR | rollback | CC1 | L0 | 0 |
| D-DATA_SEC | 数据安全与契约 | CC2 | L1 | 10 |
| D-SECURITY_LLM | llm_defense | CC2 | L0 | 0 |
| D-INTEGRATION_GATEWAY | mcp_servers | CC3 | L0 | 0 |
| D-DATA_GOV | 数据治理 | — | L0 | 0 |

### P1 关注（L2，可用未验证）/ P1 Watch (L2, usable unverified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | C1 | L2 | 8 |
| D-MKT_DATA | 行情数据 | C1 | L2 | 9 |
| D-FACTOR | 因子 | C2 | L2 | 17 |
| D-FUNDAMENTAL_SIGNAL | 基本面信号 | C2 | L2 | 25 |
| D-RISK | 风控 | C3 | L2 | 25 |
| D-CROSS_ASSET | 跨资产 | C4 | L2 | 11 |
| D-PF_CORE | 组合核心 | C4 | L2 | 44 |
| D-EX_CORE | 执行核心 | C5 | L2 | 14 |
| D-TRADING | 交易运营 | C5 | L2 | 163 |
| D-SIMULATION | 仿真 | C7 | L2 | 19 |
| D-GOVERNANCE | 生命周期管理 | CC1 | L2 | 2831 |
| D-GOV_AUDIT | 审计追踪 | CC1 | L2 | 188 |
| D-GOV_DRIFT | 漂移检测 | CC1 | L2 | 24 |
| D-GOV_ENFORCEMENT | rule_enforcement | CC1 | L2 | 107 |
| D-GOV_RULE | 规则治理 | CC1 | L2 | 11 |
| D-GOV_SCRIPTS | code_dedup | CC1 | L2 | 416 |
| D-AUTONOMY_PERM | 自治保护 | CC2 | L2 | 70 |
| D-BEHAVIORAL_AUDIT | 行为审计 | CC2 | L2 | 79 |
| D-SECURITY | 对抗验证 | CC2 | L2 | 244 |
| D-AUTONOMY_CORE | 自治核心 | CC3 | L2 | 176 |
| D-FRONTEND | 前端 | CC3 | L2 | 23 |
| D-INFRA_OPS | 基础设施运维 | CC3 | L2 | 34 |
| D-INFRA_RUNTIME | 运行时集成 | CC3 | L2 | 145 |
| D-INTEGRATION | 管线路由 | CC3 | L2 | 296 |
| D-INTELLIGENCE | 上下文管理 | CC3 | L2 | 56 |
| D-KNOWLEDGE | 知识管理 | CC3 | L2 | 41 |
| D-OPS | 反馈循环 | CC3 | L2 | 433 |
| D-REPORTING | 报告 | CC3 | L2 | 15 |
| D-SHARED | 共享服务 | CC3 | L2 | 296 |
| D-AUDITTEST | audit_test_suite | — | L2 | 152 |
| D-GOV_DOCS | architecture_docs | — | L2 | 127 |
| D-INFRA_A2A | a2a_communication | — | L2 | 114 |
| D-INFRA_RECOVERY | rollback_recovery | — | L2 | 107 |
| D-INFRA_TELEMETRY | observability_profiling | — | L2 | 51 |

### 已就绪（L3，生产已验证）/ Ready (L3, verified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| — | 无L3域 / No L3 domains | — | — | — |

## 未映射域 / Unmapped Domains

> 以下域未归属任何能力域，可能需要更新能力域定义
> The following domains are not mapped to any capability domain; capability definitions may need updating

| 架构域 / Architecture Domain | 域名称 / Domain Name | 架构层 / Layer | 节点数 / Nodes | 成熟度 / Maturity |
|--------|--------|--------|:---:|:---:|
| D-AUDITTEST | audit_test_suite | L2_domain | 152 | L2 |
| D-DATA_GOV | 数据治理 | L1_foundation | 0 | L0 |
| D-GOV_DOCS | architecture_docs | L2_domain | 127 | L2 |
| D-INFRA_A2A | a2a_communication | L0_infrastructure | 114 | L2 |
| D-INFRA_RECOVERY | rollback_recovery | L0_infrastructure | 107 | L2 |
| D-INFRA_TELEMETRY | observability_profiling | L0_infrastructure | 51 | L2 |
