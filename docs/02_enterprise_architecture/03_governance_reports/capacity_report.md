---
doc_type: audit_report
title: 域容量报告
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: task_bound
---

# 域容量报告

> **文档作用 / Purpose**: 展示各功能域的模块数量与容量上限对比，识别超容域和接近超容域，为域拆分决策提供依据。

> 本文档由 generate_capacity_report.py 从 depgraph.db 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph.db domains表 + nodes表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 53 |
| 超容域 | 0 |
| 接近超容域（>80%） | 3 |
| 空域（0模块） | 19 |

## 接近超容域清单（>80%，需关注）

| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage |
|------|--------|:---:|:---:|:---:|
| D-AUDITTEST | audit_test_suite | 142 | 150 | 94.7% |
| D_INFRA_RUNTIME | 运行时集成 | 139 | 150 | 92.7% |
| D-SECURITY | 对抗验证 | 132 | 150 | 88.0% |

## 空域清单（0模块，待开发）

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 上限 / Max |
|------|--------|--------|:---:|
| D-ASHARE_SIGNAL | A股特色信号 | L2_domain | 150 |
| D-BACKTEST | 回测 | L2_domain | 150 |
| D-COMPLIANCE | 合规 | L2_domain | 150 |
| D-DATA_ENG | 数据工程 | L1_foundation | 150 |
| D-DATA_GOV | 数据治理 | L1_foundation | 150 |
| D-DATA_SEC | 数据安全与契约 | L1_foundation | 150 |
| D-DIGITAL_TWIN | 数字孪生 | L2_domain | 150 |
| D-EXEC_SIM | 执行仿真 | L2_domain | 150 |
| D-EX_SOR | 执行路由 | L2_domain | 150 |
| D-GOV-REPAIR | rollback |  | 150 |
| D-INTEGRATION_GATEWAY | mcp_servers | L1_foundation | 150 |
| D-ML_SERVE | 推理 | L2_domain | 150 |
| D-ML_TRAIN | 训练 | L2_domain | 150 |
| D-PF_ALLOC | 组合分配 | L2_domain | 150 |
| D-POSITION | 仓位管理 | L2_domain | 150 |
| D-SECURITY_LLM | llm_defense | L1_foundation | 150 |
| D-SELL_DECISION | 卖出决策 | L2_domain | 150 |
| D-SIGLEGACY | 信号遗留设计态 | L2_domain | 150 |
| D-SIGQC | 信号质量控制 | L2_domain | 150 |

## 完整域容量清单

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage | 状态 / Status |
|------|--------|--------|:---:|:---:|:---:|------|
| D-ALT_DATA | 另类数据 | L1_foundation | 1 | 150 | 0.7% | 正常 |
| D-ASHARE_SIGNAL | A股特色信号 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-AUDITTEST | audit_test_suite | L2_domain | 142 | 150 | 94.7% | 接近超容 |
| D-AUTONOMY_CORE | 自治核心 | L1_foundation | 2 | 150 | 1.3% | 正常 |
| D-AUTONOMY_PERM | 自治保护 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D-BACKTEST | 回测 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-BEHAVIORAL_AUDIT | 行为审计 | L1_foundation | 79 | 150 | 52.7% | 正常 |
| D-COMPLIANCE | 合规 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-CROSS_ASSET | 跨资产 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D-DATA_ENG | 数据工程 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D-DATA_GOV | 数据治理 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D-DATA_SEC | 数据安全与契约 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D-DIGITAL_TWIN | 数字孪生 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-EXEC_SIM | 执行仿真 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-EX_CORE | 执行核心 | L2_domain | 3 | 150 | 2.0% | 正常 |
| D-EX_SOR | 执行路由 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-FACTOR | 因子 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D-FRONTEND | 前端 | L1_foundation | 7 | 150 | 4.7% | 正常 |
| D-FUNDAMENTAL_SIGNAL | 基本面信号 | L2_domain | 4 | 150 | 2.7% | 正常 |
| D-GOV-REPAIR | rollback |  | 0 | 150 | 0.0% | 空 |
| D-GOVERNANCE | 生命周期管理 | L2_domain | 117 | 150 | 78.0% | 正常 |
| D-GOV_AUDIT | 审计追踪 | L2_domain | 54 | 150 | 36.0% | 正常 |
| D-GOV_DOCS | architecture_docs | L2_domain | 100 | 150 | 66.7% | 正常 |
| D-GOV_DRIFT | 漂移检测 | L2_domain | 9 | 150 | 6.0% | 正常 |
| D-GOV_ENFORCEMENT | rule_enforcement | L2_domain | 69 | 150 | 46.0% | 正常 |
| D-GOV_RULE | 规则治理 | L2_domain | 11 | 150 | 7.3% | 正常 |
| D-GOV_SCRIPTS | code_dedup | L2_domain | 26 | 150 | 17.3% | 正常 |
| D_INFRA_A2A | a2a_communication | L0_infrastructure | 114 | 150 | 76.0% | 正常 |
| D_INFRA_OPS | 基础设施运维 | L0_infrastructure | 7 | 150 | 4.7% | 正常 |
| D_INFRA_RECOVERY | rollback_recovery | L0_infrastructure | 107 | 150 | 71.3% | 正常 |
| D_INFRA_RUNTIME | 运行时集成 | L0_infrastructure | 139 | 150 | 92.7% | 接近超容 |
| D_INFRA_TELEMETRY | observability_profiling | L0_infrastructure | 51 | 150 | 34.0% | 正常 |
| D-INTEGRATION | 管线路由 | L1_foundation | 71 | 150 | 47.3% | 正常 |
| D-INTEGRATION_GATEWAY | mcp_servers | L1_foundation | 0 | 150 | 0.0% | 空 |
| D-INTELLIGENCE | 上下文管理 | L2_domain | 18 | 150 | 12.0% | 正常 |
| D-KNOWLEDGE | 知识管理 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D-MKT_DATA | 行情数据 | L1_foundation | 1 | 150 | 0.7% | 正常 |
| D-ML_SERVE | 推理 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-ML_TRAIN | 训练 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-OPS | 反馈循环 | L1_foundation | 24 | 150 | 16.0% | 正常 |
| D-PF_ALLOC | 组合分配 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-PF_CORE | 组合核心 | L2_domain | 6 | 150 | 4.0% | 正常 |
| D-POSITION | 仓位管理 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-REPORTING | 报告 | L1_foundation | 1 | 150 | 0.7% | 正常 |
| D-RISK | 风控 | L2_domain | 9 | 150 | 6.0% | 正常 |
| D-SECURITY | 对抗验证 | L1_foundation | 132 | 150 | 88.0% | 接近超容 |
| D-SECURITY_LLM | llm_defense | L1_foundation | 0 | 150 | 0.0% | 空 |
| D-SELL_DECISION | 卖出决策 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-SHARED | 共享服务 | L1_foundation | 94 | 150 | 62.7% | 正常 |
| D-SIGLEGACY | 信号遗留设计态 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-SIGQC | 信号质量控制 | L2_domain | 0 | 150 | 0.0% | 空 |
| D-SIMULATION | 仿真 | L2_domain | 4 | 150 | 2.7% | 正常 |
| D-TRADING | 交易运营 | L2_domain | 20 | 150 | 13.3% | 正常 |
