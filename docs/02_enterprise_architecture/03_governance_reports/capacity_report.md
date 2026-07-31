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
| 域总数 | 72 |
| 超容域 | 7 |
| 接近超容域（>80%） | 3 |
| 空域（0模块） | 17 |

## 超容域清单（需拆分）

| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 超出 / Over |
|------|--------|:---:|:---:|:---:|
| D_DATA | 数据接入层 | 162 | 150 | +12 |
| D_GOVERNANCE | 生命周期管理 | 220 | 150 | +70 |
| D_GOV_CODE_QUALITY | 代码质量治理 | 169 | 150 | +19 |
| D_GOV_SCRIPTS | 脚本治理 | 381 | 150 | +231 |
| D_INFRA_RUNTIME | 运行时集成 | 160 | 150 | +10 |
| D_SECURITY | 对抗验证 | 166 | 150 | +16 |
| D_SHARED | 共享服务 | 184 | 150 | +34 |

## 接近超容域清单（>80%，需关注）

| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage |
|------|--------|:---:|:---:|:---:|
| D_AUTONOMY_CORE | 自治核心 | 130 | 150 | 86.7% |
| D_FEEDBACK_LOOP | 反馈循环引擎 | 125 | 150 | 83.3% |
| D_GOV_AUDIT | 审计追踪 | 121 | 150 | 80.7% |

## 空域清单（0模块，待开发）

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 上限 / Max |
|------|--------|--------|:---:|
| D_ARCHIVE_SCRIPTS | Archived Scripts | L2_domain | 150 |
| D_ARCH_GUARD | 架构守护脚本 | L2_domain | 150 |
| D_ARCH_SCRIPTS | 架构治理脚本 | L2_domain | 150 |
| D_BEHAVIORAL_AUDIT | 行为审计 | L2_domain | 150 |
| D_CODE_SCRIPTS | 代码质量脚本 | L2_domain | 150 |
| D_COMPLIANCE_SCRIPTS | 合规治理脚本 | L2_domain | 150 |
| D_CONTRACTS | 共享契约 | L0_infrastructure | 150 |
| D_DATA_SCRIPTS | 数据治理脚本 | L2_domain | 150 |
| D_INFRA_OPS | 基础设施运维 | L0_infrastructure | 150 |
| D_INFRA_TELEMETRY | 可观测性 | L0_infrastructure | 150 |
| D_INTEGRATION_GATEWAY | 集成网关 | L1_foundation | 150 |
| D_KNOWLEDGE | 知识管理 | L2_domain | 150 |
| D_META_SCRIPTS | 元治理脚本 | L2_domain | 150 |
| D_SECURITY_LLM | LLM防御 | L1_foundation | 150 |
| D_SEC_SCRIPTS | 安全治理脚本 | L2_domain | 150 |
| D_SIGLEGACY | 信号遗留设计态 | L2_domain | 150 |
| D_STRUCT_SCRIPTS | 结构治理脚本 | L2_domain | 150 |

## 完整域容量清单

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage | 状态 / Status |
|------|--------|--------|:---:|:---:|:---:|------|
| D_ALT_DATA | 另类数据 | L1_foundation | 7 | 150 | 4.7% | 正常 |
| D_ARCHIVE_SCRIPTS | Archived Scripts | L2_domain | 0 | 150 | 0.0% | 空 |
| D_ARCH_GUARD | 架构守护脚本 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_ARCH_SCRIPTS | 架构治理脚本 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_ASHARE_SIGNAL | A股特色信号 | L2_domain | 7 | 150 | 4.7% | 正常 |
| D_AUDITTEST | 审计测试套件 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_AUTONOMY_CORE | 自治核心 | L1_foundation | 130 | 150 | 86.7% | 接近超容 |
| D_AUTONOMY_PERM | 自治保护 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_BACKTEST | 回测 | L2_domain | 18 | 150 | 12.0% | 正常 |
| D_BEHAVIORAL_AUDIT | 行为审计 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_CODE_SCRIPTS | 代码质量脚本 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_COMPLIANCE | 合规 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_COMPLIANCE_SCRIPTS | 合规治理脚本 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_CONTRACTS | 共享契约 | L0_infrastructure | 0 | 150 | 0.0% | 空 |
| D_CROSS_ASSET | 跨资产 | L2_domain | 7 | 150 | 4.7% | 正常 |
| D_DATA | 数据接入层 | L1_foundation | 162 | 150 | 108.0% | 超容 |
| D_DATA_ENG | 数据工程 | L1_foundation | 7 | 150 | 4.7% | 正常 |
| D_DATA_GOV | 数据治理 | L1_foundation | 10 | 150 | 6.7% | 正常 |
| D_DATA_SCRIPTS | 数据治理脚本 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_DATA_SEC | 数据安全与契约 | L1_foundation | 7 | 150 | 4.7% | 正常 |
| D_DIGITAL_TWIN | 数字孪生 | L2_domain | 7 | 150 | 4.7% | 正常 |
| D_EXEC_SIM | 执行仿真 | L2_domain | 7 | 150 | 4.7% | 正常 |
| D_EX_CORE | 执行核心 | L2_domain | 8 | 150 | 5.3% | 正常 |
| D_EX_SOR | 执行路由 | L2_domain | 7 | 150 | 4.7% | 正常 |
| D_FACTOR | 因子 | L2_domain | 37 | 150 | 24.7% | 正常 |
| D_FBL_DETECTORS | 反馈检测器 | L1_foundation | 65 | 150 | 43.3% | 正常 |
| D_FBL_DIAGNOSERS | 反馈诊断器 | L1_foundation | 76 | 150 | 50.7% | 正常 |
| D_FBL_VERIFICATION | 反馈验证 | L1_foundation | 71 | 150 | 47.3% | 正常 |
| D_FEEDBACK_LOOP | 反馈循环引擎 | L1_foundation | 125 | 150 | 83.3% | 接近超容 |
| D_FRONTEND | 前端 | L2_domain | 12 | 150 | 8.0% | 正常 |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | L2_domain | 10 | 150 | 6.7% | 正常 |
| D_GOVERNANCE | 生命周期管理 | L2_domain | 220 | 150 | 146.7% | 超容 |
| D_GOV_AUDIT | 审计追踪 | L2_domain | 121 | 150 | 80.7% | 接近超容 |
| D_GOV_CODE_QUALITY | 代码质量治理 | L1_foundation | 169 | 150 | 112.7% | 超容 |
| D_GOV_DOCS | 架构文档治理 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_GOV_DRIFT | 漂移检测 | L2_domain | 74 | 150 | 49.3% | 正常 |
| D_GOV_ENFORCEMENT | 规则执行 | L2_domain | 40 | 150 | 26.7% | 正常 |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 | L1_foundation | 91 | 150 | 60.7% | 正常 |
| D_GOV_REPAIR | 治理修复 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_GOV_RULE | 规则治理 | L2_domain | 35 | 150 | 23.3% | 正常 |
| D_GOV_SCRIPTS | 脚本治理 | L2_domain | 381 | 150 | 254.0% | 超容 |
| D_INFRASTRUCTURE | 跨层契约基础设施 | L0_infrastructure | 25 | 150 | 16.7% | 正常 |
| D_INFRA_A2A | A2A通信 | L0_infrastructure | 72 | 150 | 48.0% | 正常 |
| D_INFRA_OPS | 基础设施运维 | L0_infrastructure | 0 | 150 | 0.0% | 空 |
| D_INFRA_RECOVERY | 回滚恢复 | L0_infrastructure | 55 | 150 | 36.7% | 正常 |
| D_INFRA_RUNTIME | 运行时集成 | L0_infrastructure | 160 | 150 | 106.7% | 超容 |
| D_INFRA_TELEMETRY | 可观测性 | L0_infrastructure | 0 | 150 | 0.0% | 空 |
| D_INTEGRATION | 管线路由 | L1_foundation | 71 | 150 | 47.3% | 正常 |
| D_INTEGRATION_GATEWAY | 集成网关 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_INTELLIGENCE | 上下文管理 | L2_domain | 31 | 150 | 20.7% | 正常 |
| D_KNOWLEDGE | 知识管理 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_META_SCRIPTS | 元治理脚本 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_MKT_DATA | 行情数据 | L1_foundation | 9 | 150 | 6.0% | 正常 |
| D_ML_SERVE | 推理 | L2_domain | 7 | 150 | 4.7% | 正常 |
| D_ML_TRAIN | 训练 | L2_domain | 3 | 150 | 2.0% | 正常 |
| D_OPS | 反馈循环 | L1_foundation | 11 | 150 | 7.3% | 正常 |
| D_ORCHESTRATOR | 代理编排器 | L1_foundation | 70 | 150 | 46.7% | 正常 |
| D_PF_ALLOC | 组合分配 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_PF_CORE | 组合核心 | L2_domain | 6 | 150 | 4.0% | 正常 |
| D_POSITION | 仓位管理 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_REPORTING | 报告 | L1_foundation | 3 | 150 | 2.0% | 正常 |
| D_RISK | 风控 | L2_domain | 11 | 150 | 7.3% | 正常 |
| D_SECURITY | 对抗验证 | L1_foundation | 166 | 150 | 110.7% | 超容 |
| D_SECURITY_LLM | LLM防御 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_SEC_SCRIPTS | 安全治理脚本 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_SELL_DECISION | 卖出决策 | L2_domain | 7 | 150 | 4.7% | 正常 |
| D_SHARED | 共享服务 | L0_infrastructure | 184 | 150 | 122.7% | 超容 |
| D_SIGLEGACY | 信号遗留设计态 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_SIGQC | 信号质量控制 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_SIMULATION | 仿真 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_STRUCT_SCRIPTS | 结构治理脚本 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_TRADING | 交易运营 | L2_domain | 37 | 150 | 24.7% | 正常 |
