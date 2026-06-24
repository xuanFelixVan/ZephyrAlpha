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

> 本文档由 generate_capability_heatmap.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:29:59
> 数据源: depgraph.db domains表 + nodes表 (注: arch_domain_capacity表不存在，v6已合并入domains表)

## 统计概览 / Statistics Overview

| 指标 | 值 |
|------|-----|
| 域总数 / Total Domains | 43 |
| 能力域数 / Capability Domains | 10 |
| ✅ 完全覆盖 / Full Coverage (L3+) | 26 |
| 🟡 部分覆盖 / Partial Coverage (L1-L2) | 17 |
| ❌ 无覆盖 / No Coverage (L0) | 0 |

## 成熟度图例 / Maturity Legend

| 等级 | 符号 | 覆盖度 | 中文名 | 英文名 | 定义 |
|:---:|:---:|:---:|--------|--------|------|
| L0 | ⚪ | ❌ | 缺失 | Missing | 能力完全不存在，无设计无代码 / No nodes in domain |
| L1 | 🔵 | 🟡 | 设计 | Designed | 仅有设计文档/蓝图，无代码 / design_maturity=design only |
| L2 | 🟡 | 🟡 | 草稿 | Drafted | 有原型代码，未集成 / design_maturity=prototype |
| L3 | 🟢 | ✅ | 可用 | Usable | 代码可用但未生产验证 / design_maturity=production, build_status!=active |
| L4 | 🟣 | ✅ | 生产级 | Production | 生产环境稳定运行 / design_maturity=production, build_status=active |
| L5 | 🔴 | ✅ | 顶级对标 | Leading | 达到Goldman/BlackRock水平 / Leading (manual assessment) |

## 能力域定义 / Capability Domain Definitions

| 能力域ID | 中文名 | 英文名 | 类型 | 包含域数 | 包含域 |
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
> 单元格：成熟度符号（属于该能力域时显示，否则显示 —）

| 架构域 | 域名称 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | CC1 | CC2 | CC3 | 成熟度 |
|--------|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | 🟡 | — | — | — | — | — | — | — | — | — | L2 |
| D-DATA_ENG | 数据工程(增值+融合+知识) | 🟡 | — | — | — | — | — | — | — | — | — | L2 |
| D-MKT_DATA | 行情数据(接入+存储) | 🟢 | — | — | — | — | — | — | — | — | — | L3 |
| D-FACTOR | 因子 | — | 🟢 | — | — | — | — | — | — | — | — | L3 |
| D-SIGNAL | 信号 | — | 🟢 | — | — | — | — | — | — | — | — | L3 |
| D-SIGNAL_ASHARE | A股特色信号 | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | — | 🟢 | — | — | — | — | — | — | — | — | L3 |
| D-SIGNAL_QUALITY | 信号质量 | — | 🟡 | — | — | — | — | — | — | — | — | L2 |
| D-COMPLIANCE | 合规 | — | — | 🟡 | — | — | — | — | — | — | — | L2 |
| D-RISK | 风控 | — | — | 🟢 | — | — | — | — | — | — | — | L3 |
| D-CROSS_ASSET | 跨资产 | — | — | — | 🟢 | — | — | — | — | — | — | L3 |
| D-PF_ALLOC | 组合分配 | — | — | — | 🟡 | — | — | — | — | — | — | L2 |
| D-PF_CORE | 组合核心 | — | — | — | 🟢 | — | — | — | — | — | — | L3 |
| D-SELL_DECISION | 卖出决策 | — | — | — | 🟡 | — | — | — | — | — | — | L2 |
| D-EX_CORE | 执行核心 | — | — | — | — | 🟢 | — | — | — | — | — | L3 |
| D-EX_SOR | 执行路由 | — | — | — | — | 🟡 | — | — | — | — | — | L2 |
| D-POSITION | 仓位管理 | — | — | — | — | 🟡 | — | — | — | — | — | L2 |
| D-TRADING | 交易运营 | — | — | — | — | 🟢 | — | — | — | — | — | L3 |
| D-ML_SERVE | 推理 | — | — | — | — | — | 🟡 | — | — | — | — | L2 |
| D-ML_TRAIN | 训练 | — | — | — | — | — | 🟡 | — | — | — | — | L2 |
| D-BACKTEST | 回测 | — | — | — | — | — | — | 🟡 | — | — | — | L2 |
| D-DIGITAL_TWIN | 数字孪生 | — | — | — | — | — | — | 🟡 | — | — | — | L2 |
| D-EXEC_SIM | 执行仿真 | — | — | — | — | — | — | 🟡 | — | — | — | L2 |
| D-SIMULATION | 仿真 | — | — | — | — | — | — | 🟢 | — | — | — | L3 |
| D-GOVERNANCE | lifecycle_management | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D-GOV_AUDIT | audit-trail | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D-GOV_DRIFT | drift_detection | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D-GOV_RULE | 规则治理 | — | — | — | — | — | — | — | 🟢 | — | — | L3 |
| D-AUTONOMY_PERM | 自治保护 | — | — | — | — | — | — | — | — | 🟢 | — | L3 |
| D-BEHAVIORAL_AUDIT | 行为审计 | — | — | — | — | — | — | — | — | 🟢 | — | L3 |
| D-DATA_SEC | 数据安全与契约 | — | — | — | — | — | — | — | — | 🟡 | — | L2 |
| D-SECURITY | adversarial_validation | — | — | — | — | — | — | — | — | 🟢 | — | L3 |
| D-AUTONOMY_CORE | 自治核心 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D-FRONTEND | 前端 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D-INFRA_OPS | 基础设施运维 | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D-INFRA_RUNTIME | runtime_integration | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D-INTEGRATION | pipeline_routing | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D-INTELLIGENCE | context_management | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D-KNOWLEDGE | knowledge_management | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D-OPS | feedback-loop | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D-REPORTING | 报告 | — | — | — | — | — | — | — | — | — | 🟡 | L2 |
| D-SHARED | shared_services | — | — | — | — | — | — | — | — | — | 🟢 | L3 |
| D-DATA_GOV | 数据治理(质量+血缘+参考) | — | — | — | — | — | — | — | — | — | — | L1 |

## 能力域成熟度汇总 / Capability Domain Maturity Summary

| 能力域 | 中文名 | 域数量 | 总节点 | production | design | prototype | 平均成熟度 | 覆盖度 |
|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 | 数据接入 | 3 | 463 | 1 | 458 | 4 | 2.33 | 🟡 部分覆盖 |
| C2 | 因子研究 | 5 | 841 | 6 | 808 | 27 | 2.60 | 🟡 部分覆盖 |
| C3 | 风险控制 | 2 | 1679 | 9 | 1640 | 30 | 2.50 | 🟡 部分覆盖 |
| C4 | 策略决策 | 4 | 435 | 7 | 410 | 18 | 2.50 | 🟡 部分覆盖 |
| C5 | 执行交易 | 4 | 568 | 20 | 402 | 146 | 2.50 | 🟡 部分覆盖 |
| C6 | ML平台 | 2 | 176 | 0 | 170 | 6 | 2.00 | 🟡 部分覆盖 |
| C7 | 回测仿真 | 4 | 134 | 4 | 119 | 11 | 2.25 | 🟡 部分覆盖 |
| CC1 | 治理合规 | 4 | 4381 | 400 | 598 | 3383 | 3.00 | ✅ 完全覆盖 |
| CC2 | 安全防护 | 4 | 1191 | 198 | 820 | 173 | 2.75 | 🟡 部分覆盖 |
| CC3 | 基础设施 | 10 | 4271 | 587 | 2565 | 1119 | 2.90 | 🟡 部分覆盖 |

## 域成熟度明细 / Domain Maturity Detail

| 架构域 | 域名称 | 能力域 | 架构层 | 节点数 | production | design | prototype | active | 成熟度 | 覆盖度 |
|--------|--------|:---:|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | C1 | L1_foundation | 62 | 0 | 61 | 1 | 0 | L2 🟡 | 🟡 |
| D-DATA_ENG | 数据工程(增值+融合+知识) | C1 | L1_foundation | 141 | 0 | 140 | 1 | 0 | L2 🟡 | 🟡 |
| D-MKT_DATA | 行情数据(接入+存储) | C1 | L1_foundation | 260 | 1 | 257 | 2 | 0 | L3 🟢 | ✅ |
| D-FACTOR | 因子 | C2 | L2_domain | 314 | 2 | 302 | 10 | 0 | L3 🟢 | ✅ |
| D-SIGNAL | 信号 | C2 | L2_domain | 476 | 1 | 474 | 1 | 0 | L3 🟢 | ✅ |
| D-SIGNAL_ASHARE | A股特色信号 | C2 | L2_domain | 21 | 0 | 20 | 1 | 0 | L2 🟡 | 🟡 |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | C2 | L2_domain | 18 | 3 | 1 | 14 | 0 | L3 🟢 | ✅ |
| D-SIGNAL_QUALITY | 信号质量 | C2 | L2_domain | 12 | 0 | 11 | 1 | 0 | L2 🟡 | 🟡 |
| D-COMPLIANCE | 合规 | C3 | L2_domain | 910 | 0 | 891 | 19 | 0 | L2 🟡 | 🟡 |
| D-RISK | 风控 | C3 | L2_domain | 769 | 9 | 749 | 11 | 0 | L3 🟢 | ✅ |
| D-CROSS_ASSET | 跨资产 | C4 | L2_domain | 73 | 1 | 66 | 6 | 0 | L3 🟢 | ✅ |
| D-PF_ALLOC | 组合分配 | C4 | L2_domain | 108 | 0 | 104 | 4 | 0 | L2 🟡 | 🟡 |
| D-PF_CORE | 组合核心 | C4 | L2_domain | 196 | 6 | 183 | 7 | 0 | L3 🟢 | ✅ |
| D-SELL_DECISION | 卖出决策 | C4 | L2_domain | 58 | 0 | 57 | 1 | 0 | L2 🟡 | 🟡 |
| D-EX_CORE | 执行核心 | C5 | L2_domain | 129 | 3 | 120 | 6 | 0 | L3 🟢 | ✅ |
| D-EX_SOR | 执行路由 | C5 | L2_domain | 125 | 0 | 124 | 1 | 0 | L2 🟡 | 🟡 |
| D-POSITION | 仓位管理 | C5 | L2_domain | 71 | 0 | 69 | 2 | 0 | L2 🟡 | 🟡 |
| D-TRADING | 交易运营 | C5 | L2_domain | 243 | 17 | 89 | 137 | 0 | L3 🟢 | ✅ |
| D-ML_SERVE | 推理 | C6 | L2_domain | 63 | 0 | 62 | 1 | 0 | L2 🟡 | 🟡 |
| D-ML_TRAIN | 训练 | C6 | L2_domain | 113 | 0 | 108 | 5 | 0 | L2 🟡 | 🟡 |
| D-BACKTEST | 回测 | C7 | L2_domain | 3 | 0 | 2 | 1 | 0 | L2 🟡 | 🟡 |
| D-DIGITAL_TWIN | 数字孪生 | C7 | L2_domain | 7 | 0 | 6 | 1 | 0 | L2 🟡 | 🟡 |
| D-EXEC_SIM | 执行仿真 | C7 | L2_domain | 2 | 0 | 1 | 1 | 0 | L2 🟡 | 🟡 |
| D-SIMULATION | 仿真 | C7 | L2_domain | 122 | 4 | 110 | 8 | 0 | L3 🟢 | ✅ |
| D-GOVERNANCE | lifecycle_management | CC1 | L2_domain | 3897 | 132 | 591 | 3174 | 0 | L3 🟢 | ✅ |
| D-GOV_AUDIT | audit-trail | CC1 | L2_domain | 268 | 69 | 6 | 193 | 0 | L3 🟢 | ✅ |
| D-GOV_DRIFT | drift_detection | CC1 | L2_domain | 38 | 22 | 1 | 15 | 0 | L3 🟢 | ✅ |
| D-GOV_RULE | 规则治理 | CC1 | L2_domain | 178 | 177 | 0 | 1 | 0 | L3 🟢 | ✅ |
| D-AUTONOMY_PERM | 自治保护 | CC2 | L2_domain | 264 | 4 | 197 | 63 | 0 | L3 🟢 | ✅ |
| D-BEHAVIORAL_AUDIT | 行为审计 | CC2 | L1_foundation | 60 | 60 | 0 | 0 | 0 | L3 🟢 | ✅ |
| D-DATA_SEC | 数据安全与契约 | CC2 | L1_foundation | 24 | 0 | 20 | 4 | 0 | L2 🟡 | 🟡 |
| D-SECURITY | adversarial_validation | CC2 | L1_platform | 843 | 134 | 603 | 106 | 0 | L3 🟢 | ✅ |
| D-AUTONOMY_CORE | 自治核心 | CC3 | L1_platform | 644 | 1 | 475 | 168 | 0 | L3 🟢 | ✅ |
| D-FRONTEND | 前端 | CC3 | L1_platform | 231 | 7 | 213 | 11 | 0 | L3 🟢 | ✅ |
| D-INFRA_OPS | 基础设施运维 | CC3 | L0_infrastructure | 412 | 3 | 389 | 20 | 0 | L3 🟢 | ✅ |
| D-INFRA_RUNTIME | runtime_integration | CC3 | L0_infrastructure | 721 | 410 | 311 | 0 | 0 | L3 🟢 | ✅ |
| D-INTEGRATION | pipeline_routing | CC3 | L1_platform | 701 | 63 | 416 | 222 | 0 | L3 🟢 | ✅ |
| D-INTELLIGENCE | context_management | CC3 | L2_domain | 267 | 18 | 217 | 32 | 0 | L3 🟢 | ✅ |
| D-KNOWLEDGE | knowledge_management | CC3 | L2_domain | 188 | 1 | 155 | 32 | 0 | L3 🟢 | ✅ |
| D-OPS | feedback-loop | CC3 | L1_platform | 691 | 5 | 264 | 422 | 0 | L3 🟢 | ✅ |
| D-REPORTING | 报告 | CC3 | L1_platform | 126 | 0 | 118 | 8 | 0 | L2 🟡 | 🟡 |
| D-SHARED | shared_services | CC3 | L1_platform | 290 | 79 | 7 | 204 | 0 | L3 🟢 | ✅ |
| D-DATA_GOV | 数据治理(质量+血缘+参考) | — | L1_foundation | 38 | 0 | 38 | 0 | 0 | L1 🔵 | 🟡 |

## 差距分析 / Gap Analysis

### P0 短板（L0-L1，需优先补齐）

| 架构域 | 域名称 | 能力域 | 当前成熟度 | 节点数 |
|--------|--------|:---:|:---:|:---:|
| D-DATA_GOV | 数据治理(质量+血缘+参考) | — | L1 | 38 |

### P1 关注（L2，有原型待集成）

| 架构域 | 域名称 | 能力域 | 当前成熟度 | 节点数 |
|--------|--------|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | C1 | L2 | 62 |
| D-DATA_ENG | 数据工程(增值+融合+知识) | C1 | L2 | 141 |
| D-SIGNAL_ASHARE | A股特色信号 | C2 | L2 | 21 |
| D-SIGNAL_QUALITY | 信号质量 | C2 | L2 | 12 |
| D-COMPLIANCE | 合规 | C3 | L2 | 910 |
| D-PF_ALLOC | 组合分配 | C4 | L2 | 108 |
| D-SELL_DECISION | 卖出决策 | C4 | L2 | 58 |
| D-EX_SOR | 执行路由 | C5 | L2 | 125 |
| D-POSITION | 仓位管理 | C5 | L2 | 71 |
| D-ML_SERVE | 推理 | C6 | L2 | 63 |
| D-ML_TRAIN | 训练 | C6 | L2 | 113 |
| D-BACKTEST | 回测 | C7 | L2 | 3 |
| D-DIGITAL_TWIN | 数字孪生 | C7 | L2 | 7 |
| D-EXEC_SIM | 执行仿真 | C7 | L2 | 2 |
| D-DATA_SEC | 数据安全与契约 | CC2 | L2 | 24 |
| D-REPORTING | 报告 | CC3 | L2 | 126 |

### 已就绪（L3+，可用/生产级）

| 架构域 | 域名称 | 能力域 | 当前成熟度 | 节点数 |
|--------|--------|:---:|:---:|:---:|
| D-MKT_DATA | 行情数据(接入+存储) | C1 | L3 | 260 |
| D-FACTOR | 因子 | C2 | L3 | 314 |
| D-SIGNAL | 信号 | C2 | L3 | 476 |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | C2 | L3 | 18 |
| D-RISK | 风控 | C3 | L3 | 769 |
| D-CROSS_ASSET | 跨资产 | C4 | L3 | 73 |
| D-PF_CORE | 组合核心 | C4 | L3 | 196 |
| D-EX_CORE | 执行核心 | C5 | L3 | 129 |
| D-TRADING | 交易运营 | C5 | L3 | 243 |
| D-SIMULATION | 仿真 | C7 | L3 | 122 |
| D-GOVERNANCE | lifecycle_management | CC1 | L3 | 3897 |
| D-GOV_AUDIT | audit-trail | CC1 | L3 | 268 |
| D-GOV_DRIFT | drift_detection | CC1 | L3 | 38 |
| D-GOV_RULE | 规则治理 | CC1 | L3 | 178 |
| D-AUTONOMY_PERM | 自治保护 | CC2 | L3 | 264 |
| D-BEHAVIORAL_AUDIT | 行为审计 | CC2 | L3 | 60 |
| D-SECURITY | adversarial_validation | CC2 | L3 | 843 |
| D-AUTONOMY_CORE | 自治核心 | CC3 | L3 | 644 |
| D-FRONTEND | 前端 | CC3 | L3 | 231 |
| D-INFRA_OPS | 基础设施运维 | CC3 | L3 | 412 |
| D-INFRA_RUNTIME | runtime_integration | CC3 | L3 | 721 |
| D-INTEGRATION | pipeline_routing | CC3 | L3 | 701 |
| D-INTELLIGENCE | context_management | CC3 | L3 | 267 |
| D-KNOWLEDGE | knowledge_management | CC3 | L3 | 188 |
| D-OPS | feedback-loop | CC3 | L3 | 691 |
| D-SHARED | shared_services | CC3 | L3 | 290 |

## 未映射域 / Unmapped Domains

> 以下域未归属任何能力域，可能需要更新能力域定义

| 架构域 | 域名称 | 架构层 | 节点数 | 成熟度 |
|--------|--------|--------|:---:|:---:|
| D-DATA_GOV | 数据治理(质量+血缘+参考) | L1_foundation | 38 | L1 |
