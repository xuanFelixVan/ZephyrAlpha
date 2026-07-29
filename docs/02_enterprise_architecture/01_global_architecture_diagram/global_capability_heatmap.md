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

> **文档作用 / Purpose**: 以矩阵形式展示70个架构域在10个能力域上的成熟度分布，用于识别能力短板和过度建设。

> 本文档由 generate_capability_heatmap.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) domains表 + nodes表 (注: arch_domain_capacity表不存在，v6已合并入domains表)

## 统计概览 / Statistics Overview

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 / Total Domains | 70 |
| 能力域数 / Capability Domains | 10 |
| L0 缺失 / Missing | 17 |
| L1 设计中 / Designing | 2 |
| L2 可用未验证 / Usable | 15 |
| L3 生产已验证 / Verified | 36 |
| ✅ 完全覆盖 / Full Coverage (L3) | 36 |
| 🟡 部分覆盖 / Partial Coverage (L1-L2) | 17 |
| ❌ 无覆盖 / No Coverage (L0) | 17 |

## 成熟度图例 / Maturity Legend

| 等级 / Level | 符号 / Symbol | 覆盖度 / Coverage | 中文名 / Chinese | 英文名 / English | 定义 / Definition |
|:---:|:---:|:---:|--------|--------|------|
| L0 | ⚪ | ❌ | 缺失 | Missing | 能力完全不存在，无设计无代码 / No nodes in domain |
| L1 | 🔵 | 🟡 | 设计中 | Designing | 有设计文档，未集成 / design_maturity=design |
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

> 行：架构域（70域） | 列：能力域（10能力域）
> Rows: Architecture Domains (70) | Columns: Capability Domains (10)
> 单元格：成熟度符号（属于该能力域时显示，否则显示 —）
> Cell: Maturity symbol (shown when domain belongs to capability, otherwise —)

| 架构域 / Architecture Domain | 域名称 / Domain Name | C1 | C2 | C3 | C4 | C5 | C6 | C7 | CC1 | CC2 | CC3 | 成熟度 / Maturity |
|--------|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 🟡 | — | — | — | — | — | — | — | — | — | L2 |
| D_DATA | 数据接入层 | 🟢 | — | — | — | — | — | — | — | — | — | L3 |
| D_DATA_ENG | 数据工程 | 🟡 | — | — | — | — | — | — | — | — | — | L2 |
| D_MKT_DATA | 行情数据 | 🟡 | — | — | — | — | — | — | — | — | — | L2 |
| D_ASHARE_SIGNAL | A股特色信号 | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D_FACTOR | 因子 | — | 🟢 | — | — | — | — | — | — | — | — | L3 |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | — | 🟢 | — | — | — | — | — | — | — | — | L3 |
| D_SIGLEGACY | 信号遗留设计态 | — | ⚪ | — | — | — | — | — | — | — | — | L0 |
| D_SIGQC | 信号质量控制 | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D_COMPLIANCE | 合规 | — | — | 🟡 | — | — | — | — | — | — | — | L2 |
| D_RISK | 风控 | — | — | 🟢 | — | — | — | — | — | — | — | L3 |
| D_CROSS_ASSET | 跨资产 | — | — | — | 🟡 | — | — | — | — | — | — | L2 |
| D_PF_ALLOC | 组合分配 | — | — | — | 🟢 | — | — | — | — | — | — | L3 |
| D_PF_CORE | 组合核心 | — | — | — | 🟡 | — | — | — | — | — | — | L2 |
| D_SELL_DECISION | 卖出决策 | — | — | — | 🟡 | — | — | — | — | — | — | L2 |
| D_EX_CORE | 执行核心 | — | — | — | — | 🟢 | — | — | — | — | — | L3 |
| D_EX_SOR | 执行路由 | — | — | — | — | 🟡 | — | — | — | — | — | L2 |
| D_POSITION | 仓位管理 | — | — | — | — | 🟢 | — | — | — | — | — | L3 |
| D_TRADING | 交易运营 | — | — | — | — | 🟢 | — | — | — | — | — | L3 |
| D_ML_SERVE | 推理 | — | — | — | — | — | 🟡 | — | — | — | — | L2 |
| D_ML_TRAIN | 训练 | — | — | — | — | — | 🟡 | — | — | — | — | L2 |
| D_BACKTEST | 回测 | — | — | — | — | — | — | 🟢 | — | — | — | L3 |
| D_DIGITAL_TWIN | 数字孪生 | — | — | — | — | — | — | 🟡 | — | — | — | L2 |
| D_EXEC_SIM | 执行仿真 | — | — | — | — | — | — | 🟡 | — | — | — | L2 |
| D_SIMULATION | 仿真 | — | — | — | — | — | — | 🟢 | — | — | — | L3 |
| D_DATA_GOV | 数据治理 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
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
| D_DATA_SEC | 数据安全与契约 | — | — | — | — | — | — | — | — | 🟡 | — | L2 |
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
| D_ARCHIVE_SCRIPTS | Archived Scripts | — | — | — | — | — | — | — | — | — | — | L0 |
| D_ARCH_GUARD | 架构守护脚本 | — | — | — | — | — | — | — | — | — | — | L0 |
| D_ARCH_SCRIPTS | 架构治理脚本 | — | — | — | — | — | — | — | — | — | — | L0 |
| D_CODE_SCRIPTS | 代码质量脚本 | — | — | — | — | — | — | — | — | — | — | L0 |
| D_COMPLIANCE_SCRIPTS | 合规治理脚本 | — | — | — | — | — | — | — | — | — | — | L0 |
| D_CONTRACTS | 共享契约 | — | — | — | — | — | — | — | — | — | — | L0 |
| D_DATA_SCRIPTS | 数据治理脚本 | — | — | — | — | — | — | — | — | — | — | L0 |
| D_META_SCRIPTS | 元治理脚本 | — | — | — | — | — | — | — | — | — | — | L0 |
| D_SEC_SCRIPTS | 安全治理脚本 | — | — | — | — | — | — | — | — | — | — | L0 |
| D_STRUCT_SCRIPTS | 结构治理脚本 | — | — | — | — | — | — | — | — | — | — | L0 |

## 能力域成熟度汇总 / Capability Domain Maturity Summary

| 能力域 / Capability | 中文名 / Chinese | 域数量 / Domain Count | 总节点 / Total Nodes | production | design | 平均成熟度 / Avg Maturity | 覆盖度 / Coverage |
|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 | 数据接入 | 4 | 184 | 162 | 22 | 2.25 | 🟡 部分覆盖 / Partial |
| C2 | 因子研究 | 5 | 106 | 56 | 50 | 2.00 | 🟡 部分覆盖 / Partial |
| C3 | 风险控制 | 2 | 13 | 13 | 0 | 2.50 | 🟡 部分覆盖 / Partial |
| C4 | 策略决策 | 4 | 17 | 17 | 0 | 2.25 | 🟡 部分覆盖 / Partial |
| C5 | 执行交易 | 4 | 52 | 52 | 0 | 2.75 | 🟡 部分覆盖 / Partial |
| C6 | ML平台 | 2 | 11 | 10 | 1 | 2.00 | 🟡 部分覆盖 / Partial |
| C7 | 回测仿真 | 4 | 43 | 34 | 9 | 2.50 | 🟡 部分覆盖 / Partial |
| CC1 | 治理合规 | 14 | 1004 | 975 | 29 | 2.86 | 🟡 部分覆盖 / Partial |
| CC2 | 安全防护 | 5 | 173 | 173 | 0 | 1.00 | 🟡 部分覆盖 / Partial |
| CC3 | 基础设施 | 16 | 814 | 812 | 2 | 2.31 | 🟡 部分覆盖 / Partial |

## 域成熟度明细 / Domain Maturity Detail

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 架构层 / Layer | 节点数 / Nodes | production | design | active | 成熟度 / Maturity | 覆盖度 / Coverage |
|--------|--------|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | C1 | L1_foundation | 8 | 7 | 1 | 0 | L2 🟡 | 🟡 |
| D_DATA | 数据接入层 | C1 | L1_foundation | 147 | 139 | 8 | 17 | L3 🟢 | ✅ |
| D_DATA_ENG | 数据工程 | C1 | L1_foundation | 20 | 7 | 13 | 0 | L2 🟡 | 🟡 |
| D_MKT_DATA | 行情数据 | C1 | L1_foundation | 9 | 9 | 0 | 0 | L2 🟡 | 🟡 |
| D_ASHARE_SIGNAL | A股特色信号 | C2 | L2_domain | 8 | 7 | 1 | 0 | L2 🟡 | 🟡 |
| D_FACTOR | 因子 | C2 | L2_domain | 86 | 37 | 49 | 17 | L3 🟢 | ✅ |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | C2 | L2_domain | 10 | 10 | 0 | 4 | L3 🟢 | ✅ |
| D_SIGLEGACY | 信号遗留设计态 | C2 | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_SIGQC | 信号质量控制 | C2 | L2_domain | 2 | 2 | 0 | 0 | L2 🟡 | 🟡 |
| D_COMPLIANCE | 合规 | C3 | L2_domain | 2 | 2 | 0 | 0 | L2 🟡 | 🟡 |
| D_RISK | 风控 | C3 | L2_domain | 11 | 11 | 0 | 9 | L3 🟢 | ✅ |
| D_CROSS_ASSET | 跨资产 | C4 | L2_domain | 7 | 7 | 0 | 0 | L2 🟡 | 🟡 |
| D_PF_ALLOC | 组合分配 | C4 | L2_domain | 2 | 2 | 0 | 1 | L3 🟢 | ✅ |
| D_PF_CORE | 组合核心 | C4 | L2_domain | 1 | 1 | 0 | 0 | L2 🟡 | 🟡 |
| D_SELL_DECISION | 卖出决策 | C4 | L2_domain | 7 | 7 | 0 | 0 | L2 🟡 | 🟡 |
| D_EX_CORE | 执行核心 | C5 | L2_domain | 7 | 7 | 0 | 4 | L3 🟢 | ✅ |
| D_EX_SOR | 执行路由 | C5 | L2_domain | 7 | 7 | 0 | 0 | L2 🟡 | 🟡 |
| D_POSITION | 仓位管理 | C5 | L2_domain | 1 | 1 | 0 | 1 | L3 🟢 | ✅ |
| D_TRADING | 交易运营 | C5 | L2_domain | 37 | 37 | 0 | 20 | L3 🟢 | ✅ |
| D_ML_SERVE | 推理 | C6 | L2_domain | 7 | 7 | 0 | 0 | L2 🟡 | 🟡 |
| D_ML_TRAIN | 训练 | C6 | L2_domain | 4 | 3 | 1 | 0 | L2 🟡 | 🟡 |
| D_BACKTEST | 回测 | C7 | L2_domain | 27 | 18 | 9 | 10 | L3 🟢 | ✅ |
| D_DIGITAL_TWIN | 数字孪生 | C7 | L2_domain | 7 | 7 | 0 | 0 | L2 🟡 | 🟡 |
| D_EXEC_SIM | 执行仿真 | C7 | L2_domain | 7 | 7 | 0 | 0 | L2 🟡 | 🟡 |
| D_SIMULATION | 仿真 | C7 | L2_domain | 2 | 2 | 0 | 2 | L3 🟢 | ✅ |
| D_DATA_GOV | 数据治理 | CC1 | L1_foundation | 10 | 10 | 0 | 3 | L3 🟢 | ✅ |
| D_FBL_DETECTORS | 反馈检测器 | CC1 | L1_foundation | 65 | 65 | 0 | 59 | L3 🟢 | ✅ |
| D_FBL_DIAGNOSERS | 反馈诊断器 | CC1 | L1_foundation | 76 | 76 | 0 | 69 | L3 🟢 | ✅ |
| D_FBL_VERIFICATION | 反馈验证 | CC1 | L1_foundation | 71 | 71 | 0 | 67 | L3 🟢 | ✅ |
| D_FEEDBACK_LOOP | 反馈循环引擎 | CC1 | L1_foundation | 125 | 125 | 0 | 111 | L3 🟢 | ✅ |
| D_GOVERNANCE | 生命周期管理 | CC1 | L2_domain | 134 | 134 | 0 | 96 | L3 🟢 | ✅ |
| D_GOV_AUDIT | 审计追踪 | CC1 | L2_domain | 113 | 110 | 3 | 75 | L3 🟢 | ✅ |
| D_GOV_CODE_QUALITY | 代码质量治理 | CC1 | L1_foundation | 156 | 156 | 0 | 139 | L3 🟢 | ✅ |
| D_GOV_DOCS | 架构文档治理 | CC1 | L2_domain | 24 | 0 | 24 | 0 | L1 🔵 | 🟡 |
| D_GOV_DRIFT | 漂移检测 | CC1 | L2_domain | 71 | 70 | 1 | 65 | L3 🟢 | ✅ |
| D_GOV_ENFORCEMENT | 规则执行 | CC1 | L2_domain | 33 | 32 | 1 | 18 | L3 🟢 | ✅ |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 | CC1 | L1_foundation | 91 | 91 | 0 | 81 | L3 🟢 | ✅ |
| D_GOV_REPAIR | 治理修复 | CC1 | L2_domain | 1 | 1 | 0 | 1 | L3 🟢 | ✅ |
| D_GOV_RULE | 规则治理 | CC1 | L2_domain | 34 | 34 | 0 | 31 | L3 🟢 | ✅ |
| D_AUTONOMY_PERM | 自治保护 | CC2 | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_BEHAVIORAL_AUDIT | 行为审计 | CC2 | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_DATA_SEC | 数据安全与契约 | CC2 | L1_foundation | 7 | 7 | 0 | 0 | L2 🟡 | 🟡 |
| D_SECURITY | 对抗验证 | CC2 | L1_foundation | 166 | 166 | 0 | 100 | L3 🟢 | ✅ |
| D_SECURITY_LLM | LLM防御 | CC2 | L1_foundation | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_AUTONOMY_CORE | 自治核心 | CC3 | L1_foundation | 126 | 126 | 0 | 125 | L3 🟢 | ✅ |
| D_FRONTEND | 前端 | CC3 | L2_domain | 11 | 11 | 0 | 9 | L3 🟢 | ✅ |
| D_INFRASTRUCTURE | 跨层契约基础设施 | CC3 | L0_infrastructure | 24 | 24 | 0 | 12 | L3 🟢 | ✅ |
| D_INFRA_A2A | A2A通信 | CC3 | L0_infrastructure | 72 | 72 | 0 | 28 | L3 🟢 | ✅ |
| D_INFRA_OPS | 基础设施运维 | CC3 | L0_infrastructure | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_INFRA_RECOVERY | 回滚恢复 | CC3 | L0_infrastructure | 54 | 54 | 0 | 48 | L3 🟢 | ✅ |
| D_INFRA_RUNTIME | 运行时集成 | CC3 | L0_infrastructure | 161 | 160 | 1 | 119 | L3 🟢 | ✅ |
| D_INFRA_TELEMETRY | 可观测性 | CC3 | L0_infrastructure | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_INTEGRATION | 管线路由 | CC3 | L1_foundation | 71 | 71 | 0 | 39 | L3 🟢 | ✅ |
| D_INTEGRATION_GATEWAY | 集成网关 | CC3 | L1_foundation | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_INTELLIGENCE | 上下文管理 | CC3 | L2_domain | 29 | 29 | 0 | 19 | L3 🟢 | ✅ |
| D_KNOWLEDGE | 知识管理 | CC3 | L2_domain | 1 | 0 | 1 | 0 | L1 🔵 | 🟡 |
| D_OPS | 反馈循环 | CC3 | L1_foundation | 9 | 9 | 0 | 8 | L3 🟢 | ✅ |
| D_ORCHESTRATOR | 代理编排器 | CC3 | L1_foundation | 70 | 70 | 0 | 54 | L3 🟢 | ✅ |
| D_REPORTING | 报告 | CC3 | L1_foundation | 3 | 3 | 0 | 1 | L3 🟢 | ✅ |
| D_SHARED | 共享服务 | CC3 | L0_infrastructure | 183 | 183 | 0 | 118 | L3 🟢 | ✅ |
| D_ARCHIVE_SCRIPTS | Archived Scripts | — | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_ARCH_GUARD | 架构守护脚本 | — | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_ARCH_SCRIPTS | 架构治理脚本 | — | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_CODE_SCRIPTS | 代码质量脚本 | — | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_COMPLIANCE_SCRIPTS | 合规治理脚本 | — | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_CONTRACTS | 共享契约 | — | L0_infrastructure | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_DATA_SCRIPTS | 数据治理脚本 | — | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_META_SCRIPTS | 元治理脚本 | — | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_SEC_SCRIPTS | 安全治理脚本 | — | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |
| D_STRUCT_SCRIPTS | 结构治理脚本 | — | L2_domain | 0 | 0 | 0 | 0 | L0 ⚪ | ❌ |

## 差距分析 / Gap Analysis

### P0 短板（L0-L1，需优先补齐）/ P0 Gaps (L0-L1, priority)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D_SIGLEGACY | 信号遗留设计态 | C2 | L0 | 0 |
| D_GOV_DOCS | 架构文档治理 | CC1 | L1 | 24 |
| D_AUTONOMY_PERM | 自治保护 | CC2 | L0 | 0 |
| D_BEHAVIORAL_AUDIT | 行为审计 | CC2 | L0 | 0 |
| D_SECURITY_LLM | LLM防御 | CC2 | L0 | 0 |
| D_INFRA_OPS | 基础设施运维 | CC3 | L0 | 0 |
| D_INFRA_TELEMETRY | 可观测性 | CC3 | L0 | 0 |
| D_INTEGRATION_GATEWAY | 集成网关 | CC3 | L0 | 0 |
| D_KNOWLEDGE | 知识管理 | CC3 | L1 | 1 |
| D_ARCHIVE_SCRIPTS | Archived Scripts | — | L0 | 0 |
| D_ARCH_GUARD | 架构守护脚本 | — | L0 | 0 |
| D_ARCH_SCRIPTS | 架构治理脚本 | — | L0 | 0 |
| D_CODE_SCRIPTS | 代码质量脚本 | — | L0 | 0 |
| D_COMPLIANCE_SCRIPTS | 合规治理脚本 | — | L0 | 0 |
| D_CONTRACTS | 共享契约 | — | L0 | 0 |
| D_DATA_SCRIPTS | 数据治理脚本 | — | L0 | 0 |
| D_META_SCRIPTS | 元治理脚本 | — | L0 | 0 |
| D_SEC_SCRIPTS | 安全治理脚本 | — | L0 | 0 |
| D_STRUCT_SCRIPTS | 结构治理脚本 | — | L0 | 0 |

### P1 关注（L2，可用未验证）/ P1 Watch (L2, usable unverified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | C1 | L2 | 8 |
| D_DATA_ENG | 数据工程 | C1 | L2 | 20 |
| D_MKT_DATA | 行情数据 | C1 | L2 | 9 |
| D_ASHARE_SIGNAL | A股特色信号 | C2 | L2 | 8 |
| D_SIGQC | 信号质量控制 | C2 | L2 | 2 |
| D_COMPLIANCE | 合规 | C3 | L2 | 2 |
| D_CROSS_ASSET | 跨资产 | C4 | L2 | 7 |
| D_PF_CORE | 组合核心 | C4 | L2 | 1 |
| D_SELL_DECISION | 卖出决策 | C4 | L2 | 7 |
| D_EX_SOR | 执行路由 | C5 | L2 | 7 |
| D_ML_SERVE | 推理 | C6 | L2 | 7 |
| D_ML_TRAIN | 训练 | C6 | L2 | 4 |
| D_DIGITAL_TWIN | 数字孪生 | C7 | L2 | 7 |
| D_EXEC_SIM | 执行仿真 | C7 | L2 | 7 |
| D_DATA_SEC | 数据安全与契约 | CC2 | L2 | 7 |

### 已就绪（L3，生产已验证）/ Ready (L3, verified)

| 架构域 / Architecture Domain | 域名称 / Domain Name | 能力域 / Capability | 当前成熟度 / Current Maturity | 节点数 / Nodes |
|--------|--------|:---:|:---:|:---:|
| D_DATA | 数据接入层 | C1 | L3 | 147 |
| D_FACTOR | 因子 | C2 | L3 | 86 |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | C2 | L3 | 10 |
| D_RISK | 风控 | C3 | L3 | 11 |
| D_PF_ALLOC | 组合分配 | C4 | L3 | 2 |
| D_EX_CORE | 执行核心 | C5 | L3 | 7 |
| D_POSITION | 仓位管理 | C5 | L3 | 1 |
| D_TRADING | 交易运营 | C5 | L3 | 37 |
| D_BACKTEST | 回测 | C7 | L3 | 27 |
| D_SIMULATION | 仿真 | C7 | L3 | 2 |
| D_DATA_GOV | 数据治理 | CC1 | L3 | 10 |
| D_FBL_DETECTORS | 反馈检测器 | CC1 | L3 | 65 |
| D_FBL_DIAGNOSERS | 反馈诊断器 | CC1 | L3 | 76 |
| D_FBL_VERIFICATION | 反馈验证 | CC1 | L3 | 71 |
| D_FEEDBACK_LOOP | 反馈循环引擎 | CC1 | L3 | 125 |
| D_GOVERNANCE | 生命周期管理 | CC1 | L3 | 134 |
| D_GOV_AUDIT | 审计追踪 | CC1 | L3 | 113 |
| D_GOV_CODE_QUALITY | 代码质量治理 | CC1 | L3 | 156 |
| D_GOV_DRIFT | 漂移检测 | CC1 | L3 | 71 |
| D_GOV_ENFORCEMENT | 规则执行 | CC1 | L3 | 33 |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 | CC1 | L3 | 91 |
| D_GOV_REPAIR | 治理修复 | CC1 | L3 | 1 |
| D_GOV_RULE | 规则治理 | CC1 | L3 | 34 |
| D_SECURITY | 对抗验证 | CC2 | L3 | 166 |
| D_AUTONOMY_CORE | 自治核心 | CC3 | L3 | 126 |
| D_FRONTEND | 前端 | CC3 | L3 | 11 |
| D_INFRASTRUCTURE | 跨层契约基础设施 | CC3 | L3 | 24 |
| D_INFRA_A2A | A2A通信 | CC3 | L3 | 72 |
| D_INFRA_RECOVERY | 回滚恢复 | CC3 | L3 | 54 |
| D_INFRA_RUNTIME | 运行时集成 | CC3 | L3 | 161 |
| D_INTEGRATION | 管线路由 | CC3 | L3 | 71 |
| D_INTELLIGENCE | 上下文管理 | CC3 | L3 | 29 |
| D_OPS | 反馈循环 | CC3 | L3 | 9 |
| D_ORCHESTRATOR | 代理编排器 | CC3 | L3 | 70 |
| D_REPORTING | 报告 | CC3 | L3 | 3 |
| D_SHARED | 共享服务 | CC3 | L3 | 183 |

## 未映射域 / Unmapped Domains

> 以下域未归属任何能力域，可能需要更新能力域定义
> The following domains are not mapped to any capability domain; capability definitions may need updating

| 架构域 / Architecture Domain | 域名称 / Domain Name | 架构层 / Layer | 节点数 / Nodes | 成熟度 / Maturity |
|--------|--------|--------|:---:|:---:|
| D_ARCHIVE_SCRIPTS | Archived Scripts | L2_domain | 0 | L0 |
| D_ARCH_GUARD | 架构守护脚本 | L2_domain | 0 | L0 |
| D_ARCH_SCRIPTS | 架构治理脚本 | L2_domain | 0 | L0 |
| D_CODE_SCRIPTS | 代码质量脚本 | L2_domain | 0 | L0 |
| D_COMPLIANCE_SCRIPTS | 合规治理脚本 | L2_domain | 0 | L0 |
| D_CONTRACTS | 共享契约 | L0_infrastructure | 0 | L0 |
| D_DATA_SCRIPTS | 数据治理脚本 | L2_domain | 0 | L0 |
| D_META_SCRIPTS | 元治理脚本 | L2_domain | 0 | L0 |
| D_SEC_SCRIPTS | 安全治理脚本 | L2_domain | 0 | L0 |
| D_STRUCT_SCRIPTS | 结构治理脚本 | L2_domain | 0 | L0 |
