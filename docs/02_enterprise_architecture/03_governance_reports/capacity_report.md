---
doc_type: audit_report
title: 域容量报告
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 域容量报告

> **文档作用 / Purpose**: 展示各功能域的模块数量与容量上限对比，识别超容域和接近超容域，为域拆分决策提供依据。

> 本文档由 generate_capacity_report.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) domains表 + nodes表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 62 |
| 超容域 | 0 |
| 接近超容域（>80%） | 1 |
| 空域（0模块） | 25 |

## 接近超容域清单（>80%，需关注）

| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage |
|------|--------|:---:|:---:|:---:|
| D_AUTONOMY_CORE | 自治核心 | 126 | 150 | 84.0% |

## 空域清单（0模块，待开发）

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 上限 / Max |
|------|--------|--------|:---:|
| D_ALT_DATA | 另类数据 | L1_foundation | 150 |
| D_ASHARE_SIGNAL | A股特色信号 | L2_domain | 150 |
| D_AUTONOMY_PERM | 自治保护 | L2_domain | 150 |
| D_BEHAVIORAL_AUDIT | 行为审计 |  | 150 |
| D_COMPLIANCE | 合规 |  | 150 |
| D_CROSS_ASSET | 跨资产 | L2_domain | 150 |
| D_DATA_ENG | 数据工程 | L1_foundation | 150 |
| D_DATA_GOV | 数据治理 | L1_foundation | 150 |
| D_DATA_SEC | 数据安全与契约 | L1_foundation | 150 |
| D_DIGITAL_TWIN | 数字孪生 | L2_domain | 150 |
| D_EXEC_SIM | 执行仿真 | L2_domain | 150 |
| D_EX_SOR | 执行路由 | L2_domain | 150 |
| D_GOV_DOCS | 架构文档治理 | L2_domain | 150 |
| D_INFRA_OPS | 基础设施运维 | L0_infrastructure | 150 |
| D_INFRA_TELEMETRY | 可观测性 | L0_infrastructure | 150 |
| D_INTEGRATION_GATEWAY | 集成网关 | L1_foundation | 150 |
| D_KNOWLEDGE | 知识管理 | L2_domain | 150 |
| D_MKT_DATA | 行情数据 | L1_foundation | 150 |
| D_ML_SERVE | 推理 | L2_domain | 150 |
| D_ML_TRAIN | 训练 | L2_domain | 150 |
| D_PF_CORE | 组合核心 | L2_domain | 150 |
| D_SECURITY_LLM | LLM防御 | L1_foundation | 150 |
| D_SELL_DECISION | 卖出决策 | L2_domain | 150 |
| D_SIGLEGACY | 信号遗留设计态 |  | 150 |
| D_SIGQC | 信号质量控制 | L2_domain | 150 |

## 完整域容量清单

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage | 状态 / Status |
|------|--------|--------|:---:|:---:|:---:|------|
| D_ALT_DATA | 另类数据 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_ASHARE_SIGNAL | A股特色信号 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_AUDITTEST | 审计测试套件 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_AUTONOMY_CORE | 自治核心 | L1_foundation | 126 | 150 | 84.0% | 接近超容 |
| D_AUTONOMY_PERM | 自治保护 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_BACKTEST | 回测 | L2_domain | 9 | 150 | 6.0% | 正常 |
| D_BEHAVIORAL_AUDIT | 行为审计 |  | 0 | 150 | 0.0% | 空 |
| D_COMPLIANCE | 合规 |  | 0 | 150 | 0.0% | 空 |
| D_CROSS_ASSET | 跨资产 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_DATA | 数据接入层 |  | 9 | 150 | 6.0% | 正常 |
| D_DATA_ENG | 数据工程 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_DATA_GOV | 数据治理 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_DATA_SEC | 数据安全与契约 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_DIGITAL_TWIN | 数字孪生 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_EXEC_SIM | 执行仿真 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_EX_CORE | 执行核心 | L2_domain | 4 | 150 | 2.7% | 正常 |
| D_EX_SOR | 执行路由 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_FACTOR | 因子 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_FBL_DETECTORS | 反馈检测器 | L1_foundation | 59 | 150 | 39.3% | 正常 |
| D_FBL_DIAGNOSERS | 反馈诊断器 | L1_foundation | 69 | 150 | 46.0% | 正常 |
| D_FBL_VERIFICATION | 反馈验证 | L1_foundation | 67 | 150 | 44.7% | 正常 |
| D_FEEDBACK_LOOP | 反馈循环引擎 | L1_foundation | 110 | 150 | 73.3% | 正常 |
| D_FRONTEND | 前端 | L1_foundation | 9 | 150 | 6.0% | 正常 |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | L2_domain | 4 | 150 | 2.7% | 正常 |
| D_GOVERNANCE | 生命周期管理 | L2_domain | 96 | 150 | 64.0% | 正常 |
| D_GOV_AUDIT | 审计追踪 | L2_domain | 66 | 150 | 44.0% | 正常 |
| D_GOV_CODE_QUALITY | 代码质量治理 | L1_foundation | 115 | 150 | 76.7% | 正常 |
| D_GOV_DOCS | 架构文档治理 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_GOV_DRIFT | 漂移检测 | L2_domain | 69 | 150 | 46.0% | 正常 |
| D_GOV_ENFORCEMENT | 规则执行 | L2_domain | 15 | 150 | 10.0% | 正常 |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 | L1_foundation | 81 | 150 | 54.0% | 正常 |
| D_GOV_REPAIR | 治理修复 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_GOV_RULE | 规则治理 | L2_domain | 31 | 150 | 20.7% | 正常 |
| D_GOV_SCRIPTS | 脚本治理 | L2_domain | 10 | 150 | 6.7% | 正常 |
| D_INFRASTRUCTURE | 跨层契约基础设施 |  | 12 | 150 | 8.0% | 正常 |
| D_INFRA_A2A | A2A通信 | L0_infrastructure | 28 | 150 | 18.7% | 正常 |
| D_INFRA_OPS | 基础设施运维 | L0_infrastructure | 0 | 150 | 0.0% | 空 |
| D_INFRA_RECOVERY | 回滚恢复 | L0_infrastructure | 48 | 150 | 32.0% | 正常 |
| D_INFRA_RUNTIME | 运行时集成 | L0_infrastructure | 114 | 150 | 76.0% | 正常 |
| D_INFRA_TELEMETRY | 可观测性 | L0_infrastructure | 0 | 150 | 0.0% | 空 |
| D_INTEGRATION | 管线路由 | L1_foundation | 40 | 150 | 26.7% | 正常 |
| D_INTEGRATION_GATEWAY | 集成网关 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_INTELLIGENCE | 上下文管理 | L2_domain | 19 | 150 | 12.7% | 正常 |
| D_KNOWLEDGE | 知识管理 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_MKT_DATA | 行情数据 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_ML_SERVE | 推理 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_ML_TRAIN | 训练 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_OPS | 反馈循环 | L1_foundation | 8 | 150 | 5.3% | 正常 |
| D_ORCHESTRATOR | 代理编排器 | L1_foundation | 56 | 150 | 37.3% | 正常 |
| D_PF_ALLOC | 组合分配 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_PF_CORE | 组合核心 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_POSITION | 仓位管理 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_REPORTING | 报告 | L1_foundation | 1 | 150 | 0.7% | 正常 |
| D_RISK | 风控 | L2_domain | 9 | 150 | 6.0% | 正常 |
| D_SECURITY | 对抗验证 | L1_foundation | 99 | 150 | 66.0% | 正常 |
| D_SECURITY_LLM | LLM防御 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_SELL_DECISION | 卖出决策 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_SHARED | 共享服务 | L1_foundation | 112 | 150 | 74.7% | 正常 |
| D_SIGLEGACY | 信号遗留设计态 |  | 0 | 150 | 0.0% | 空 |
| D_SIGQC | 信号质量控制 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_SIMULATION | 仿真 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_TRADING | 交易运营 | L2_domain | 21 | 150 | 14.0% | 正常 |
