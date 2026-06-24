---
doc_type: capability_heatmap
title: 能力热力图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 能力热力图 / Capability Heatmap

> **文档作用 / Purpose**: 以矩阵形式展示43个架构域在10个能力域上的成熟度分布，用于识别能力短板和过度建设。

> 本文档由 generate_capability_heatmap.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 23:01:39
> 数据源: depgraph.db domains表 + nodes表 (注: arch_domain_capacity表不存在，v6已合并入domains表)

## 统计概览 / Statistics Overview

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 / Total Domains | 48 |
| 能力域数 / Capability Domains | 10 |
| L0 缺失 / Missing | 5 |
| L1 设计中 / Designing | 17 |
| L2 可用未验证 / Usable | 26 |
| L3 生产已验证 / Verified | 0 |
| ✅ 完全覆盖 / Full Coverage (L3) | 0 |
| 🟡 部分覆盖 / Partial Coverage (L1-L2) | 43 |
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
| C2 | 因子研究 | Factor & Signal | 业务 | 5 | D-FACTOR, D-SIGNAL, D-SIGNAL_FUNDAMENTAL, D-SIGNAL_ASHARE, D-SIGNAL_QUALITY |
| C3 | 风险控制 | Risk Control | 业务 | 2 | D-RISK, D-COMPLIANCE |
| C4 | 策略决策 | Strategy Decision | 业务 | 4 | D-PF_CORE, D-PF_ALLOC, D-SELL_DECISION, D-CROSS_ASSET |
| C5 | 执行交易 | Execution & Trading | 业务 | 4 | D-EX_CORE, D-EX_SOR, D-TRADING, D-POSITION |
| C6 | ML平台 | ML Platform | 业务 | 2 | D-ML_TRAIN, D-ML_SERVE |
| C7 | 回测仿真 | Backtest & Simulation | 业务 | 4 | D-BACKTEST, D-SIMULATION, D-EXEC_SIM, D-DIGITAL_TWIN |
| CC1 | 治理合规 | Governance & Compliance | 横切 | 7 | D-GOVERNANCE, D-GOV_RULE, D-GOV_AUDIT, D-GOV_DRIFT, D-GOV_ENFORCEMENT, D-GOV_REPAIR, D-GOV_SCRIPTS |
| CC2 | 安全防护 | Security | 横切 | 5 | D-SECURITY, D-SECURITY-LLM, D-BEHAVIORAL_AUDIT, D-DATA_SEC, D-AUTONOMY_PERM |
| CC3 | 基础设施 | Infrastructure | 横切 | 11 | D-INFRA_OPS, D-INFRA_RUNTIME, D-INTEGRATION, D-INTEGRATION-GATEWAY, D-SHARED, D-FRONTEND, D-REPORTING, D-KNOWLEDGE, D-INTELLIGENCE, D-AUTONOMY_CORE, D-OPS |

## 能力热力图矩阵 / Capability Heatmap Matrix

> 行：架构域（43域） | 列：能力域（10能力域）
> Rows: Architecture Domains (43) | Columns: Capability Domains (10)
> 单元格：成熟度符号（属于该能力域时显示，否则显示 —）
> Cell: Maturity symbol (shown when domain belongs to capability, otherwise —)

| 架构域 / Architecture Domain | 域名称 / Domain Name | C1 | C2 | C3 | C4 | C5 | C6 | C7 | CC1 | CC2 | CC3 | 成熟度 / Maturity |
|--------|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | 🔵 | — | — | — | — | — | — | — | — | — | L1 |
| D-DATA_ENG | 数据工程 | 🔵 | — | — | — | — | — | — | — | — | — | L1 |
| D-MKT_DATA | 行情数据 | 🟡 | — | — | — | — | — | — | — | — | — | L2 |
| D-FACTOR | 因子 | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D-SIGNAL | 信号 | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D-SIGNAL_ASHARE | A股特色信号 | — | 🔵 | — | — | — | — | — | — | — | — | L1 |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D-SIGNAL_QUALITY | 信号质量 | — | 🔵 | — | — | — | — | — | — | — | — | L1 |
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
| D-GOV-ENFORCEMENT | rule_enforcement | — | — | — | — | — | — | — | ⚪ | — | — | L0 |
| D-GOV-REPAIR | rollback | — | — | — | — | — | — | — | ⚪ | — | — | L0 |
| D-GOV-SCRIPTS | code_dedup | — | — | — | — | — | — | — | ⚪ | — | — | L0 |
| D-GOVERNANCE | 生命周期管理 | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D-GOV_AUDIT | 审计追踪 | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D-GOV_DRIFT | 漂移检测 | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D-GOV_RULE | 规则治理 | — | — | — | — | — | — | — | 🟡 | — | — | L2 |
| D-AUTONOMY_PERM | 自治保护 | — | — | — | — | — | — | — | — | 🟡 | — | L2 |
| D-BEHAVIORAL_AUDIT | 行为审计 | — | — | — | — | — | — | — | — | 🟡 | — | L2 |
| D-DATA_SEC | 数据安全与契约 | — | — | — | — | — | — | — | — | 🔵 | — | L1 |
| D-SECURITY | 对抗验证 | — | — | — | — | — | — | — | — | 🟡 | — | L2 |
| D-SECURITY-LLM | llm_defense | — | — | — | — | — | — | — | — | ⚪ | — | L0 |
| D-AUTONOMY_CORE | 自治核心 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-FRONTEND | 前端 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-INFRA_OPS | 基础设施运维 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-INFRA_RUNTIME | 运行时集成 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-INTEGRATION | 管线路由 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-INTEGRATION-GATEWAY | mcp_servers | — | — | — | — | — | — | — | — | — | ⚪ | L0 |
| D-INTELLIGENCE | 上下文管理 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-KNOWLEDGE | 知识管理 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-OPS | 反馈循环 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-REPORTING | 报告 | — | — | — | — | — | — | — | — | — | 🔵 | L1 |
| D-SHARED | 共享服务 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-DATA_GOV | 数据治理 | — | — | — | — | — | — | — | — | — | — | L1 |

## 能力域成熟度汇总 / Capability Domain Maturity Summary

| 能力域 / Capability | 中文名 / Chinese | 域数量 / Domain Count | 总节点 / Total Nodes | production | design | prototype | 平均成熟度 / Avg Maturity | 覆盖度 / Coverage |
|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 | 数据接入 | 3 | 463 | 1 | 458 | 4 | 1.33 | 🟡 部分覆盖 / Partial |
| C2 | 因子研究 | 5 | 840 | 6 | 807 | 27 | 1.60 | 🟡 部分覆盖 / Partial |
| C3 | 风险控制 | 2 | 1679 | 9 | 1640 | 30 | 1.50 | 🟡 部分覆盖 / Partial |
| C4 | 策略决策 | 4 | 432 | 7 | 410 | 15 | 1.50 | 🟡 部分覆盖 / Partial |
| C5 | 执行交易 | 4 | 568 | 20 | 402 | 146 | 1.50 | 🟡 部分覆盖 / Partial |
| C6 | ML平台 | 2 | 176 | 0 | 170 | 6 | 1.00 | 🟡 部分覆盖 / Partial |
| C7 | 回测仿真 | 4 | 134 | 4 | 119 | 11 | 1.25 | 🟡 部分覆盖 / Partial |
| CC1 | 治理合规 | 7 | 4282 | 400 | 598 | 3284 | 1.14 | 🟡 部分覆盖 / Partial |
| CC2 | 安全防护 | 5 | 1191 | 198 | 820 | 173 | 1.40 | 🟡 部分覆盖 / Partial |
| CC3 | 基础设施 | 11 | 4250 | 587 | 2565 | 1098 | 1.73 | 🟡 部分覆盖 / Partial |

## 域成熟度明细 / Domain Maturity Detail

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 架构层 / Layer | 节点数 / Nodes | production | design | prototype | active | 成熟度 / Maturity | 覆盖度 / Coverage |
|--------|--------|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | C1 | L1_foundation | 62 | 0 | 61 | 1 | 0 | L1 🔵 | 🟡 |
| D-DATA_ENG | 数据工程 | C1 | L1_foundation | 141 | 0 | 140 | 1 | 0 | L1 🔵 | 🟡 |
| D-MKT_DATA | 行情数据 | C1 | L1_foundation | 260 | 1 | 257 | 2 | 0 | L2 🟡 | 🟡 |
| D-FACTOR | 因子 | C2 | L2_domain | 313 | 2 | 301 | 10 | 0 | L2 🟡 | 🟡 |
| D-SIGNAL | 信号 | C2 | L2_domain | 476 | 1 | 474 | 1 | 0 | L2 🟡 | 🟡 |
| D-SIGNAL_ASHARE | A股特色信号 | C2 | L2_domain | 21 | 0 | 20 | 1 | 0 | L1 🔵 | 🟡 |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | C2 | L2_domain | 18 | 3 | 1 | 14 | 0 | L2 🟡 | 🟡 |
| D-SIGNAL_QUALITY | 信号质量 | C2 | L2_domain | 12 | 0 | 11 | 1 | 0 | L1 🔵 | 🟡 |
| D-COMPLIANCE | 合规 | C3 | L2_domain | 910 | 0 | 891 | 19 | 0 | L1 🔵 | 🟡 |
| D-RISK | 风控 | C3 | L2_domain | 769 | 9 | 749 | 11 | 0 | L2 🟡 | 🟡 |
| D-CROSS_ASSET | 跨资产 | C4 | L2_domain | 70 | 1 | 66 | 3 | 0 | L2 🟡 | 🟡 |
| D-PF_ALLOC | 组合分配 | C4 | L2_domain | 108 | 0 | 104 | 4 | 0 | L1 🔵 | 🟡 |
| D-PF_CORE | 组合核心 | C4 | L2_domain | 196 | 6 | 183 | 7 | 0 | L2 🟡 | 🟡 |
| D-SELL_DECISION | 卖出决策 | C4 | L2_domain | 58 | 0 | 57 | 1 | 0 | L1 🔵 | 🟡 |
| D-EX_CORE | 执行核心 | C5 | L2_domain | 129 | 3 | 120 | 6 | 0 | L2 🟡 | 🟡 |
| D-EX_SOR | 执行路由 | C5 | L2_domain | 125 | 0 | 124 | 1 | 0 | L1 🔵 | 🟡 |
| D-POSITION | 仓位管理 | C5 | L2_domain | 71 | 0 | 69 | 2 | 0 | L1 🔵 | 🟡 |
| D-TRADING | 交易运营 | C5 | L2_domain | 243 | 17 | 89 | 137 | 0 | L2 🟡 | 🟡 |
| D-ML_SERVE | 推理 | C6 | L2_domain | 63 | 0 | 62 | 1 | 0 | L1 🔵 | 🟡 |
| D-ML_TRAIN | 训练 | C6 | L2_domain | 113 | 0 | 108 | 5 | 0 | L1 🔵 | 🟡 |
| D-BACKTEST | 回测 | C7 | L2_domain | 3 | 0 | 2 | 1 | 0 | L1 🔵 | 🟡 |
| D-DIGITAL_TWIN | 数字孪生 | C7 | L2_domain | 7 | 0 | 6 | 1 | 0 | L1 🔵 | 🟡 |
| D-EXEC_SIM | 执行仿真 | C7 | L2_domain | 2 | 0 | 1 | 1 | 0 | L1 🔵 | 🟡 |
| D-SIMULATION | 仿真 | C7 | L2_domain | 122 | 4 | 110 | 8 | 0 | L2 🟡 | 🟡 |
| D-GOV-ENFORCEMENT | rule_enforcement | CC1 |  | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D-GOV-REPAIR | rollback | CC1 |  | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D-GOV-SCRIPTS | code_dedup | CC1 |  | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D-GOVERNANCE | 生命周期管理 | CC1 | L2_domain | 3849 | 132 | 591 | 3126 | 0 | L2 🟡 | 🟡 |
| D-GOV_AUDIT | 审计追踪 | CC1 | L2_domain | 217 | 69 | 6 | 142 | 0 | L2 🟡 | 🟡 |
| D-GOV_DRIFT | 漂移检测 | CC1 | L2_domain | 38 | 22 | 1 | 15 | 0 | L2 🟡 | 🟡 |
| D-GOV_RULE | 规则治理 | CC1 | L2_domain | 178 | 177 | 0 | 1 | 0 | L2 🟡 | 🟡 |
| D-AUTONOMY_PERM | 自治保护 | CC2 | L2_domain | 264 | 4 | 197 | 63 | 0 | L2 🟡 | 🟡 |
| D-BEHAVIORAL_AUDIT | 行为审计 | CC2 | L1_foundation | 60 | 60 | 0 | 0 | 0 | L2 🟡 | 🟡 |
| D-DATA_SEC | 数据安全与契约 | CC2 | L1_foundation | 24 | 0 | 20 | 4 | 0 | L1 🔵 | 🟡 |
| D-SECURITY | 对抗验证 | CC2 | L1_platform | 843 | 134 | 603 | 106 | 0 | L2 🟡 | 🟡 |
| D-SECURITY-LLM | llm_defense | CC2 |  | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D-AUTONOMY_CORE | 自治核心 | CC3 | L1_platform | 644 | 1 | 475 | 168 | 0 | L2 🟡 | 🟡 |
| D-FRONTEND | 前端 | CC3 | L1_platform | 230 | 7 | 213 | 10 | 0 | L2 🟡 | 🟡 |
| D-INFRA_OPS | 基础设施运维 | CC3 | L0_infrastructure | 412 | 3 | 389 | 20 | 0 | L2 🟡 | 🟡 |
| D-INFRA_RUNTIME | 运行时集成 | CC3 | L0_infrastructure | 721 | 410 | 311 | 0 | 0 | L2 🟡 | 🟡 |
| D-INTEGRATION | 管线路由 | CC3 | L1_platform | 700 | 63 | 416 | 221 | 0 | L2 🟡 | 🟡 |
| D-INTEGRATION-GATEWAY | mcp_servers | CC3 |  | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D-INTELLIGENCE | 上下文管理 | CC3 | L2_domain | 267 | 18 | 217 | 32 | 0 | L2 🟡 | 🟡 |
| D-KNOWLEDGE | 知识管理 | CC3 | L2_domain | 188 | 1 | 155 | 32 | 0 | L2 🟡 | 🟡 |
| D-OPS | 反馈循环 | CC3 | L1_platform | 673 | 5 | 264 | 404 | 0 | L2 🟡 | 🟡 |
| D-REPORTING | 报告 | CC3 | L1_platform | 126 | 0 | 118 | 8 | 0 | L1 🔵 | 🟡 |
| D-SHARED | 共享服务 | CC3 | L1_platform | 289 | 79 | 7 | 203 | 0 | L2 🟡 | 🟡 |
| D-DATA_GOV | 数据治理 | — | L1_foundation | 38 | 0 | 38 | 0 | 0 | L1 🔵 | 🟡 |

## 差距分析 / Gap Analysis

### P0 短板（L0-L1，需优先补齐）/ P0 Gaps (L0-L1, priority)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | C1 | L1 | 62 |
| D-DATA_ENG | 数据工程 | C1 | L1 | 141 |
| D-SIGNAL_ASHARE | A股特色信号 | C2 | L1 | 21 |
| D-SIGNAL_QUALITY | 信号质量 | C2 | L1 | 12 |
| D-COMPLIANCE | 合规 | C3 | L1 | 910 |
| D-PF_ALLOC | 组合分配 | C4 | L1 | 108 |
| D-SELL_DECISION | 卖出决策 | C4 | L1 | 58 |
| D-EX_SOR | 执行路由 | C5 | L1 | 125 |
| D-POSITION | 仓位管理 | C5 | L1 | 71 |
| D-ML_SERVE | 推理 | C6 | L1 | 63 |
| D-ML_TRAIN | 训练 | C6 | L1 | 113 |
| D-BACKTEST | 回测 | C7 | L1 | 3 |
| D-DIGITAL_TWIN | 数字孪生 | C7 | L1 | 7 |
| D-EXEC_SIM | 执行仿真 | C7 | L1 | 2 |
| D-GOV-ENFORCEMENT | rule_enforcement | CC1 | L0 | 0 |
| D-GOV-REPAIR | rollback | CC1 | L0 | 0 |
| D-GOV-SCRIPTS | code_dedup | CC1 | L0 | 0 |
| D-DATA_SEC | 数据安全与契约 | CC2 | L1 | 24 |
| D-SECURITY-LLM | llm_defense | CC2 | L0 | 0 |
| D-INTEGRATION-GATEWAY | mcp_servers | CC3 | L0 | 0 |
| D-REPORTING | 报告 | CC3 | L1 | 126 |
| D-DATA_GOV | 数据治理 | — | L1 | 38 |

### P1 关注（L2，可用未验证）/ P1 Watch (L2, usable unverified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D-MKT_DATA | 行情数据 | C1 | L2 | 260 |
| D-FACTOR | 因子 | C2 | L2 | 313 |
| D-SIGNAL | 信号 | C2 | L2 | 476 |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | C2 | L2 | 18 |
| D-RISK | 风控 | C3 | L2 | 769 |
| D-CROSS_ASSET | 跨资产 | C4 | L2 | 70 |
| D-PF_CORE | 组合核心 | C4 | L2 | 196 |
| D-EX_CORE | 执行核心 | C5 | L2 | 129 |
| D-TRADING | 交易运营 | C5 | L2 | 243 |
| D-SIMULATION | 仿真 | C7 | L2 | 122 |
| D-GOVERNANCE | 生命周期管理 | CC1 | L2 | 3849 |
| D-GOV_AUDIT | 审计追踪 | CC1 | L2 | 217 |
| D-GOV_DRIFT | 漂移检测 | CC1 | L2 | 38 |
| D-GOV_RULE | 规则治理 | CC1 | L2 | 178 |
| D-AUTONOMY_PERM | 自治保护 | CC2 | L2 | 264 |
| D-BEHAVIORAL_AUDIT | 行为审计 | CC2 | L2 | 60 |
| D-SECURITY | 对抗验证 | CC2 | L2 | 843 |
| D-AUTONOMY_CORE | 自治核心 | CC3 | L2 | 644 |
| D-FRONTEND | 前端 | CC3 | L2 | 230 |
| D-INFRA_OPS | 基础设施运维 | CC3 | L2 | 412 |
| D-INFRA_RUNTIME | 运行时集成 | CC3 | L2 | 721 |
| D-INTEGRATION | 管线路由 | CC3 | L2 | 700 |
| D-INTELLIGENCE | 上下文管理 | CC3 | L2 | 267 |
| D-KNOWLEDGE | 知识管理 | CC3 | L2 | 188 |
| D-OPS | 反馈循环 | CC3 | L2 | 673 |
| D-SHARED | 共享服务 | CC3 | L2 | 289 |

### 已就绪（L3，生产已验证）/ Ready (L3, verified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| — | 无L3域 / No L3 domains | — | — | — |

## 未映射域 / Unmapped Domains

> 以下域未归属任何能力域，可能需要更新能力域定义
> The following domains are not mapped to any capability domain; capability definitions may need updating

| 架构域 / Architecture Domain | 域名称 / Domain Name | 架构层 / Layer | 节点数 / Nodes | 成熟度 / Maturity |
|--------|--------|--------|:---:|:---:|
| D-DATA_GOV | 数据治理 | L1_foundation | 38 | L1 |
