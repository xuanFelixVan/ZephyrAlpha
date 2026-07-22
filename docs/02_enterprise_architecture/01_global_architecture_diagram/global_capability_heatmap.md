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

> **文档作用 / Purpose**: 以矩阵形式展示61个架构域在10个能力域上的成熟度分布，用于识别能力短板和过度建设。

> 本文档由 generate_capability_heatmap.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) domains表 + nodes表 (注: arch_domain_capacity表不存在，v6已合并入domains表)

## 统计概览 / Statistics Overview

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 / Total Domains | 61 |
| 能力域数 / Capability Domains | 10 |
| L0 缺失 / Missing | 8 |
| L1 设计中 / Designing | 18 |
| L2 可用未验证 / Usable | 0 |
| L3 生产已验证 / Verified | 35 |
| ✅ 完全覆盖 / Full Coverage (L3) | 35 |
| 🟡 部分覆盖 / Partial Coverage (L1-L2) | 18 |
| ❌ 无覆盖 / No Coverage (L0) | 8 |

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
| C1 | 数据接入 | Data Ingestion | 业务 | 4 | D_MKT_DATA, D_ALT_DATA, D_DATA_ENG, D_DATA |
| C2 | 因子研究 | Factor & Signal | 业务 | 5 | D_FACTOR, D_SIGLEGACY, D_FUNDAMENTAL_SIGNAL, D_ASHARE_SIGNAL, D_SIGQC |
| C3 | 风险控制 | Risk Control | 业务 | 2 | D_RISK, D_COMPLIANCE |
| C4 | 策略决策 | Strategy Decision | 业务 | 4 | D_PF_CORE, D_PF_ALLOC, D_SELL_DECISION, D_CROSS_ASSET |
| C5 | 执行交易 | Execution & Trading | 业务 | 4 | D_EX_CORE, D_EX_SOR, D_TRADING, D_POSITION |
| C6 | ML平台 | ML Platform | 业务 | 2 | D_ML_TRAIN, D_ML_SERVE |
| C7 | 回测仿真 | Backtest & Simulation | 业务 | 4 | D_BACKTEST, D_SIMULATION, D_EXEC_SIM, D_DIGITAL_TWIN |
| CC1 | 治理合规 | Governance & Compliance | 横切 | 14 | D_GOVERNANCE, D_GOV_RULE, D_GOV_AUDIT, D_GOV_DRIFT, D_GOV_ENFORCEMENT, D_GOV_REPAIR, D_GOV_CODE_QUALITY, D_GOV_DOCS, D_GOV_OPS_RESILIENCE, D_DATA_GOV, D_FEEDBACK_LOOP, D_FBL_DIAGNOSERS, D_FBL_DETECTORS, D_FBL_VERIFICATION |
| CC2 | 安全防护 | Security | 横切 | 5 | D_SECURITY, D_SECURITY_LLM, D_BEHAVIORAL_AUDIT, D_DATA_SEC, D_AUTONOMY_PERM |
| CC3 | 基础设施 | Infrastructure | 横切 | 16 | D_INFRA_OPS, D_INFRA_RUNTIME, D_INFRASTRUCTURE, D_INFRA_A2A, D_INFRA_RECOVERY, D_INFRA_TELEMETRY, D_INTEGRATION, D_INTEGRATION_GATEWAY, D_SHARED, D_FRONTEND, D_REPORTING, D_KNOWLEDGE, D_INTELLIGENCE, D_AUTONOMY_CORE, D_OPS, D_ORCHESTRATOR |

## 能力热力图矩阵 / Capability Heatmap Matrix

> 行：架构域（61域） | 列：能力域（10能力域）
> Rows: Architecture Domains (61) | Columns: Capability Domains (10)
> 单元格：成熟度符号（属于该能力域时显示，否则显示 —）
> Cell: Maturity symbol (shown when domain belongs to capability, otherwise —)

| 架构域 / Architecture Domain | 域名称 / Domain Name | C1 | C2 | C3 | C4 | C5 | C6 | C7 | CC1 | CC2 | CC3 | 成熟度 / Maturity |
|--------|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 🔵 | — | — | — | — | — | — | — | — | — | L1 |
| D_DATA | 数据接入层 | 🟢 | — | — | — | — | — | — | — | — | — | L3 |
| D_DATA_ENG | 数据工程 | 🔵 | — | — | — | — | — | — | — | — | — | L1 |
| D_MKT_DATA | 行情数据 | 🔵 | — | — | — | — | — | — | — | — | — | L1 |
| D_ASHARE_SIGNAL | A股特色信号 | — | 🔵 | — | — | — | — | — | — | — | — | L1 |
| D_FACTOR | 因子 | — | 🟢 | — | — | — | — | — | — | — | — | L3 |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | — | 🟢 | — | — | — | — | — | — | — | — | L3 |
| D_SIGLEGACY | 信号遗留设计态 | — | ⚪ | — | — | — | — | — | — | — | — | L0 |
| D_SIGQC | 信号质量控制 | — | 🔵 | — | — | — | — | — | — | — | — | L1 |
| D_COMPLIANCE | 合规 | — | — | 🔵 | — | — | — | — | — | — | — | L1 |
| D_RISK | 风控 | — | — | 🟢 | — | — | — | — | — | — | — | L3 |
| D_CROSS_ASSET | 跨资产 | — | — | — | 🔵 | — | — | — | — | — | — | L1 |
| D_PF_ALLOC | 组合分配 | — | — | — | 🟢 | — | — | — | — | — | — | L3 |
| D_PF_CORE | 组合核心 | — | — | — | 🔵 | — | — | — | — | — | — | L1 |
| D_SELL_DECISION | 卖出决策 | — | — | — | 🔵 | — | — | — | — | — | — | L1 |
| D_EX_CORE | 执行核心 | — | — | — | — | 🟢 | — | — | — | — | — | L3 |
| D_EX_SOR | 执行路由 | — | — | — | — | 🔵 | — | — | — | — | — | L1 |
| D_POSITION | 仓位管理 | — | — | — | — | 🟢 | — | — | — | — | — | L3 |
| D_TRADING | 交易运营 | — | — | — | — | 🟢 | — | — | — | — | — | L3 |
| D_ML_SERVE | 推理 | — | — | — | — | — | 🔵 | — | — | — | — | L1 |
| D_ML_TRAIN | 训练 | — | — | — | — | — | 🔵 | — | — | — | — | L1 |
| D_BACKTEST | 回测 | — | — | — | — | — | — | 🟢 | — | — | — | L3 |
| D_DIGITAL_TWIN | 数字孪生 | — | — | — | — | — | — | 🔵 | — | — | — | L1 |
| D_EXEC_SIM | 执行仿真 | — | — | — | — | — | — | 🔵 | — | — | — | L1 |
| D_SIMULATION | 仿真 | — | — | — | — | — | — | 🟢 | — | — | — | L3 |
| D_DATA_GOV | 数据治理 | — | — | — | — | — | — | — | 🔵 | — | — | L1 |
| D_FBL_DETECTORS | 反馈检测器 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_FBL_DIAGNOSERS | 反馈诊断器 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_FBL_VERIFICATION | 反馈验证 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_FEEDBACK_LOOP | 反馈循环引擎 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_GOVERNANCE | 生命周期管理 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_GOV_AUDIT | 审计追踪 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_GOV_CODE_QUALITY | 代码质量治理 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_GOV_DOCS | 架构文档治理 | — | — | — | — | — | — | — | 🔵 | — | — | L1 |
| D_GOV_DRIFT | 漂移检测 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_GOV_ENFORCEMENT | 规则执行 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_GOV_REPAIR | 治理修复 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_GOV_RULE | 规则治理 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D_AUTONOMY_PERM | 自治保护 | — | — | — | — | — | — | — | — | ⚪ | — | L0 |
| D_BEHAVIORAL_AUDIT | 行为审计 | — | — | — | — | — | — | — | — | ⚪ | — | L0 |
| D_DATA_SEC | 数据安全与契约 | — | — | — | — | — | — | — | — | 🔵 | — | L1 |
| D_SECURITY | 对抗验证 | — | — | — | — | — | — | — | — | 🟢 | — | L3 |
| D_SECURITY_LLM | LLM防御 | — | — | — | — | — | — | — | — | ⚪ | — | L0 |
| D_AUTONOMY_CORE | 自治核心 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_FRONTEND | 前端 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_INFRASTRUCTURE | 跨层契约基础设施 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_INFRA_A2A | A2A通信 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_INFRA_OPS | 基础设施运维 | — | — | — | — | — | — | — | — | — | ⚪ | L0 |
| D_INFRA_RECOVERY | 回滚恢复 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_INFRA_RUNTIME | 运行时集成 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_INFRA_TELEMETRY | 可观测性 | — | — | — | — | — | — | — | — | — | ⚪ | L0 |
| D_INTEGRATION | 管线路由 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_INTEGRATION_GATEWAY | 集成网关 | — | — | — | — | — | — | — | — | — | ⚪ | L0 |
| D_INTELLIGENCE | 上下文管理 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_KNOWLEDGE | 知识管理 | — | — | — | — | — | — | — | — | — | 🔵 | L1 |
| D_OPS | 反馈循环 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_ORCHESTRATOR | 代理编排器 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_REPORTING | 报告 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_SHARED | 共享服务 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D_GOV_KB | Governance Knowledge Base | — | — | — | — | — | — | — | — | — | — | L0 |

## 能力域成熟度汇总 / Capability Domain Maturity Summary

| 能力域 / Capability | 中文名 / Chinese | 域数量 / Domain Count | 总节点 / Total Nodes | production | design | prototype | 平均成熟度 / Avg Maturity | 覆盖度 / Coverage |
|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 | 数据接入 | 4 | 76 | 14 | 3 | 59 | 1.50 | 🟡 部分覆盖 / Partial |
| C2 | 因子研究 | 5 | 24 | 6 | 0 | 18 | 1.60 | 🟡 部分覆盖 / Partial |
| C3 | 风险控制 | 2 | 13 | 9 | 0 | 4 | 2.00 | 🟡 部分覆盖 / Partial |
| C4 | 策略决策 | 4 | 17 | 1 | 0 | 16 | 1.50 | 🟡 部分覆盖 / Partial |
| C5 | 执行交易 | 4 | 52 | 25 | 0 | 27 | 2.50 | 🟡 部分覆盖 / Partial |
| C6 | ML平台 | 2 | 11 | 0 | 1 | 10 | 1.00 | 🟡 部分覆盖 / Partial |
| C7 | 回测仿真 | 4 | 33 | 11 | 0 | 22 | 2.00 | 🟡 部分覆盖 / Partial |
| CC1 | 治理合规 | 14 | 994 | 798 | 41 | 155 | 2.71 | 🟡 部分覆盖 / Partial |
| CC2 | 安全防护 | 5 | 172 | 100 | 0 | 72 | 0.80 | 🟡 部分覆盖 / Partial |
| CC3 | 基础设施 | 16 | 815 | 576 | 3 | 236 | 2.31 | 🟡 部分覆盖 / Partial |

## 域成熟度明细 / Domain Maturity Detail

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 架构层 / Layer | 节点数 / Nodes | production | design | prototype | active | 成熟度 / Maturity | 覆盖度 / Coverage |
|--------|--------|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | C1 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_DATA | 数据接入层 | C1 |  | 55 | 14 | 3 | 38 | 11 | L3 🟢 | ✅ |
| D_DATA_ENG | 数据工程 | C1 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_MKT_DATA | 行情数据 | C1 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_ASHARE_SIGNAL | A股特色信号 | C2 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_FACTOR | 因子 | C2 | L2_domain | 5 | 2 | 0 | 3 | 2 | L3 🟢 | ✅ |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | C2 | L2_domain | 10 | 4 | 0 | 6 | 4 | L3 🟢 | ✅ |
| D_SIGLEGACY | 信号遗留设计态 | C2 |  | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_SIGQC | 信号质量控制 | C2 | L2_domain | 2 | 0 | 0 | 2 | 0 | L1 🔵 | 🟡 |
| D_COMPLIANCE | 合规 | C3 |  | 2 | 0 | 0 | 2 | 0 | L1 🔵 | 🟡 |
| D_RISK | 风控 | C3 | L2_domain | 11 | 9 | 0 | 2 | 9 | L3 🟢 | ✅ |
| D_CROSS_ASSET | 跨资产 | C4 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_PF_ALLOC | 组合分配 | C4 | L2_domain | 2 | 1 | 0 | 1 | 1 | L3 🟢 | ✅ |
| D_PF_CORE | 组合核心 | C4 | L2_domain | 1 | 0 | 0 | 1 | 0 | L1 🔵 | 🟡 |
| D_SELL_DECISION | 卖出决策 | C4 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_EX_CORE | 执行核心 | C5 | L2_domain | 7 | 4 | 0 | 3 | 4 | L3 🟢 | ✅ |
| D_EX_SOR | 执行路由 | C5 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_POSITION | 仓位管理 | C5 | L2_domain | 1 | 1 | 0 | 0 | 1 | L3 🟢 | ✅ |
| D_TRADING | 交易运营 | C5 | L2_domain | 37 | 20 | 0 | 17 | 20 | L3 🟢 | ✅ |
| D_ML_SERVE | 推理 | C6 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_ML_TRAIN | 训练 | C6 | L2_domain | 4 | 0 | 1 | 3 | 0 | L1 🔵 | 🟡 |
| D_BACKTEST | 回测 | C7 | L2_domain | 17 | 9 | 0 | 8 | 9 | L3 🟢 | ✅ |
| D_DIGITAL_TWIN | 数字孪生 | C7 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_EXEC_SIM | 执行仿真 | C7 | L2_domain | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_SIMULATION | 仿真 | C7 | L2_domain | 2 | 2 | 0 | 0 | 2 | L3 🟢 | ✅ |
| D_DATA_GOV | 数据治理 | CC1 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_FBL_DETECTORS | 反馈检测器 | CC1 | L1_foundation | 65 | 59 | 0 | 6 | 59 | L3 🟢 | ✅ |
| D_FBL_DIAGNOSERS | 反馈诊断器 | CC1 | L1_foundation | 76 | 69 | 0 | 7 | 69 | L3 🟢 | ✅ |
| D_FBL_VERIFICATION | 反馈验证 | CC1 | L1_foundation | 71 | 67 | 0 | 4 | 67 | L3 🟢 | ✅ |
| D_FEEDBACK_LOOP | 反馈循环引擎 | CC1 | L1_foundation | 125 | 111 | 0 | 14 | 111 | L3 🟢 | ✅ |
| D_GOVERNANCE | 生命周期管理 | CC1 | L2_domain | 133 | 95 | 1 | 37 | 95 | L3 🟢 | ✅ |
| D_GOV_AUDIT | 审计追踪 | CC1 | L2_domain | 113 | 72 | 8 | 33 | 72 | L3 🟢 | ✅ |
| D_GOV_CODE_QUALITY | 代码质量治理 | CC1 | L1_foundation | 151 | 132 | 5 | 14 | 132 | L3 🟢 | ✅ |
| D_GOV_DOCS | 架构文档治理 | CC1 | L2_domain | 24 | 0 | 24 | 0 | 0 | L1 🔵 | 🟡 |
| D_GOV_DRIFT | 漂移检测 | CC1 | L2_domain | 71 | 65 | 1 | 5 | 65 | L3 🟢 | ✅ |
| D_GOV_ENFORCEMENT | 规则执行 | CC1 | L2_domain | 32 | 15 | 2 | 15 | 15 | L3 🟢 | ✅ |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 | CC1 | L1_foundation | 91 | 81 | 0 | 10 | 81 | L3 🟢 | ✅ |
| D_GOV_REPAIR | 治理修复 | CC1 | L2_domain | 1 | 1 | 0 | 0 | 1 | L3 🟢 | ✅ |
| D_GOV_RULE | 规则治理 | CC1 | L2_domain | 34 | 31 | 0 | 3 | 31 | L3 🟢 | ✅ |
| D_AUTONOMY_PERM | 自治保护 | CC2 | L2_domain | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_BEHAVIORAL_AUDIT | 行为审计 | CC2 |  | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_DATA_SEC | 数据安全与契约 | CC2 | L1_foundation | 7 | 0 | 0 | 7 | 0 | L1 🔵 | 🟡 |
| D_SECURITY | 对抗验证 | CC2 | L1_foundation | 165 | 100 | 0 | 65 | 100 | L3 🟢 | ✅ |
| D_SECURITY_LLM | LLM防御 | CC2 | L1_foundation | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_AUTONOMY_CORE | 自治核心 | CC3 | L1_foundation | 126 | 125 | 0 | 1 | 125 | L3 🟢 | ✅ |
| D_FRONTEND | 前端 | CC3 | L1_foundation | 11 | 9 | 0 | 2 | 9 | L3 🟢 | ✅ |
| D_INFRASTRUCTURE | 跨层契约基础设施 | CC3 |  | 24 | 12 | 0 | 12 | 12 | L3 🟢 | ✅ |
| D_INFRA_A2A | A2A通信 | CC3 | L0_infrastructure | 72 | 28 | 0 | 44 | 28 | L3 🟢 | ✅ |
| D_INFRA_OPS | 基础设施运维 | CC3 | L0_infrastructure | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_INFRA_RECOVERY | 回滚恢复 | CC3 | L0_infrastructure | 54 | 48 | 0 | 6 | 48 | L3 🟢 | ✅ |
| D_INFRA_RUNTIME | 运行时集成 | CC3 | L0_infrastructure | 162 | 119 | 1 | 42 | 119 | L3 🟢 | ✅ |
| D_INFRA_TELEMETRY | 可观测性 | CC3 | L0_infrastructure | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_INTEGRATION | 管线路由 | CC3 | L1_foundation | 72 | 39 | 0 | 33 | 39 | L3 🟢 | ✅ |
| D_INTEGRATION_GATEWAY | 集成网关 | CC3 | L1_foundation | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_INTELLIGENCE | 上下文管理 | CC3 | L2_domain | 29 | 18 | 0 | 11 | 18 | L3 🟢 | ✅ |
| D_KNOWLEDGE | 知识管理 | CC3 | L2_domain | 1 | 0 | 1 | 0 | 0 | L1 🔵 | 🟡 |
| D_OPS | 反馈循环 | CC3 | L1_foundation | 9 | 8 | 0 | 1 | 8 | L3 🟢 | ✅ |
| D_ORCHESTRATOR | 代理编排器 | CC3 | L1_foundation | 70 | 54 | 0 | 16 | 54 | L3 🟢 | ✅ |
| D_REPORTING | 报告 | CC3 | L1_foundation | 3 | 1 | 0 | 2 | 1 | L3 🟢 | ✅ |
| D_SHARED | 共享服务 | CC3 | L1_foundation | 182 | 115 | 1 | 66 | 115 | L3 🟢 | ✅ |
| D_GOV_KB | Governance Knowledge Base | — | L2_domain | 0 | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |

## 差距分析 / Gap Analysis

### P0 短板（L0-L1，需优先补齐）/ P0 Gaps (L0-L1, priority)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | C1 | L1 | 7 |
| D_DATA_ENG | 数据工程 | C1 | L1 | 7 |
| D_MKT_DATA | 行情数据 | C1 | L1 | 7 |
| D_ASHARE_SIGNAL | A股特色信号 | C2 | L1 | 7 |
| D_SIGLEGACY | 信号遗留设计态 | C2 | L0 | 0 |
| D_SIGQC | 信号质量控制 | C2 | L1 | 2 |
| D_COMPLIANCE | 合规 | C3 | L1 | 2 |
| D_CROSS_ASSET | 跨资产 | C4 | L1 | 7 |
| D_PF_CORE | 组合核心 | C4 | L1 | 1 |
| D_SELL_DECISION | 卖出决策 | C4 | L1 | 7 |
| D_EX_SOR | 执行路由 | C5 | L1 | 7 |
| D_ML_SERVE | 推理 | C6 | L1 | 7 |
| D_ML_TRAIN | 训练 | C6 | L1 | 4 |
| D_DIGITAL_TWIN | 数字孪生 | C7 | L1 | 7 |
| D_EXEC_SIM | 执行仿真 | C7 | L1 | 7 |
| D_DATA_GOV | 数据治理 | CC1 | L1 | 7 |
| D_GOV_DOCS | 架构文档治理 | CC1 | L1 | 24 |
| D_AUTONOMY_PERM | 自治保护 | CC2 | L0 | 0 |
| D_BEHAVIORAL_AUDIT | 行为审计 | CC2 | L0 | 0 |
| D_DATA_SEC | 数据安全与契约 | CC2 | L1 | 7 |
| D_SECURITY_LLM | LLM防御 | CC2 | L0 | 0 |
| D_INFRA_OPS | 基础设施运维 | CC3 | L0 | 0 |
| D_INFRA_TELEMETRY | 可观测性 | CC3 | L0 | 0 |
| D_INTEGRATION_GATEWAY | 集成网关 | CC3 | L0 | 0 |
| D_KNOWLEDGE | 知识管理 | CC3 | L1 | 1 |
| D_GOV_KB | Governance Knowledge Base | — | L0 | 0 |

### P1 关注（L2，可用未验证）/ P1 Watch (L2, usable unverified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| — | 无P1关注 / No P1 watch | — | — | — |

### 已就绪（L3，生产已验证）/ Ready (L3, verified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D_DATA | 数据接入层 | C1 | L3 | 55 |
| D_FACTOR | 因子 | C2 | L3 | 5 |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | C2 | L3 | 10 |
| D_RISK | 风控 | C3 | L3 | 11 |
| D_PF_ALLOC | 组合分配 | C4 | L3 | 2 |
| D_EX_CORE | 执行核心 | C5 | L3 | 7 |
| D_POSITION | 仓位管理 | C5 | L3 | 1 |
| D_TRADING | 交易运营 | C5 | L3 | 37 |
| D_BACKTEST | 回测 | C7 | L3 | 17 |
| D_SIMULATION | 仿真 | C7 | L3 | 2 |
| D_FBL_DETECTORS | 反馈检测器 | CC1 | L3 | 65 |
| D_FBL_DIAGNOSERS | 反馈诊断器 | CC1 | L3 | 76 |
| D_FBL_VERIFICATION | 反馈验证 | CC1 | L3 | 71 |
| D_FEEDBACK_LOOP | 反馈循环引擎 | CC1 | L3 | 125 |
| D_GOVERNANCE | 生命周期管理 | CC1 | L3 | 133 |
| D_GOV_AUDIT | 审计追踪 | CC1 | L3 | 113 |
| D_GOV_CODE_QUALITY | 代码质量治理 | CC1 | L3 | 151 |
| D_GOV_DRIFT | 漂移检测 | CC1 | L3 | 71 |
| D_GOV_ENFORCEMENT | 规则执行 | CC1 | L3 | 32 |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 | CC1 | L3 | 91 |
| D_GOV_REPAIR | 治理修复 | CC1 | L3 | 1 |
| D_GOV_RULE | 规则治理 | CC1 | L3 | 34 |
| D_SECURITY | 对抗验证 | CC2 | L3 | 165 |
| D_AUTONOMY_CORE | 自治核心 | CC3 | L3 | 126 |
| D_FRONTEND | 前端 | CC3 | L3 | 11 |
| D_INFRASTRUCTURE | 跨层契约基础设施 | CC3 | L3 | 24 |
| D_INFRA_A2A | A2A通信 | CC3 | L3 | 72 |
| D_INFRA_RECOVERY | 回滚恢复 | CC3 | L3 | 54 |
| D_INFRA_RUNTIME | 运行时集成 | CC3 | L3 | 162 |
| D_INTEGRATION | 管线路由 | CC3 | L3 | 72 |
| D_INTELLIGENCE | 上下文管理 | CC3 | L3 | 29 |
| D_OPS | 反馈循环 | CC3 | L3 | 9 |
| D_ORCHESTRATOR | 代理编排器 | CC3 | L3 | 70 |
| D_REPORTING | 报告 | CC3 | L3 | 3 |
| D_SHARED | 共享服务 | CC3 | L3 | 182 |

## 未映射域 / Unmapped Domains

> 以下域未归属任何能力域，可能需要更新能力域定义
> The following domains are not mapped to any capability domain; capability definitions may need updating

| 架构域 / Architecture Domain | 域名称 / Domain Name | 架构层 / Layer | 节点数 / Nodes | 成熟度 / Maturity |
|--------|--------|--------|:---:|:---:|
| D_GOV_KB | Governance Knowledge Base | L2_domain | 0 | L0 |
