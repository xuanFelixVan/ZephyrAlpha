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
| 域总数 | 50 |
| 超容域 | 2 |
| 接近超容域（>80%） | 1 |
| 空域（0模块） | 21 |

## 超容域清单（需拆分）

| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 超出 / Over |
|------|--------|:---:|:---:|:---:|
| D_GOVERNANCE | registry_management | 483 | 150 | +333 |
| D_TRADING | 交易运营 | 280 | 150 | +130 |

## 接近超容域清单（>80%，需关注）

| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage |
|------|--------|:---:|:---:|:---:|
| D_GOV_ENFORCEMENT | rule_enforcement | 133 | 150 | 88.7% |

## 空域清单（0模块，待开发）

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 上限 / Max |
|------|--------|--------|:---:|
| D_ALT_DATA | 另类数据 | L1_foundation | 150 |
| D_ASHARE_SIGNAL | ashare_signal | L2_domain | 150 |
| D_AUTONOMY_PERM | budget_enforcement | L2_domain | 150 |
| D_DATA_ENG | 数据工程 | L1_foundation | 150 |
| D_DATA_GOV | 数据治理 | L1_foundation | 150 |
| D_DATA_SEC | 数据安全与契约 | L1_foundation | 150 |
| D_DIGITAL_TWIN | 数字孪生 | L2_domain | 150 |
| D_EXEC_SIM | 执行仿真 | L2_domain | 150 |
| D_EX_SOR | 执行路由 | L2_domain | 150 |
| D_GOV_AUDIT | audit_orchestration | L2_domain | 150 |
| D_GOV_DRIFT | drift_detection | L2_domain | 150 |
| D_GOV_REPAIR | rollback | L2_domain | 150 |
| D_GOV_RULE | rule_governance | L2_domain | 150 |
| D_INFRA_OPS | asset-inventory | L0_infrastructure | 150 |
| D_KNOWLEDGE | vector_storage | L2_domain | 150 |
| D_MKT_DATA | 行情数据 | L1_foundation | 150 |
| D_ML_SERVE | 推理 | L2_domain | 150 |
| D_ML_TRAIN | model_evaluation | L2_domain | 150 |
| D_PF_ALLOC | 组合分配 | L2_domain | 150 |
| D_SELL_DECISION | 卖出决策 | L2_domain | 150 |
| D_SIGQC | signal_quality | L2_domain | 150 |

## 完整域容量清单

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage | 状态 / Status |
|------|--------|--------|:---:|:---:|:---:|------|
| D_ALT_DATA | 另类数据 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_ASHARE_SIGNAL | ashare_signal | L2_domain | 0 | 150 | 0.0% | 空 |
| D_AUDITTEST | audit_test_suite | L2_domain | 49 | 150 | 32.7% | 正常 |
| D_AUTONOMY_CORE | agent_lifecycle | L1_foundation | 111 | 150 | 74.0% | 正常 |
| D_AUTONOMY_PERM | budget_enforcement | L2_domain | 0 | 150 | 0.0% | 空 |
| D_BACKTEST | 回测 | L2_domain | 9 | 150 | 6.0% | 正常 |
| D_CROSS_ASSET | 跨资产 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_DATA_ENG | 数据工程 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_DATA_GOV | 数据治理 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_DATA_SEC | 数据安全与契约 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_DIGITAL_TWIN | 数字孪生 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_EXEC_SIM | 执行仿真 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_EX_CORE | 执行核心 | L2_domain | 5 | 150 | 3.3% | 正常 |
| D_EX_SOR | 执行路由 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_FACTOR | 因子 | L2_domain | 4 | 150 | 2.7% | 正常 |
| D_FRONTEND | 前端 | L1_foundation | 13 | 150 | 8.7% | 正常 |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal | L2_domain | 4 | 150 | 2.7% | 正常 |
| D_GOVERNANCE | registry_management | L2_domain | 483 | 150 | 322.0% | 超容 |
| D_GOV_AUDIT | audit_orchestration | L2_domain | 0 | 150 | 0.0% | 空 |
| D_GOV_DOCS | architecture_docs | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_GOV_DRIFT | drift_detection | L2_domain | 0 | 150 | 0.0% | 空 |
| D_GOV_ENFORCEMENT | rule_enforcement | L2_domain | 133 | 150 | 88.7% | 接近超容 |
| D_GOV_REPAIR | rollback | L2_domain | 0 | 150 | 0.0% | 空 |
| D_GOV_RULE | rule_governance | L2_domain | 0 | 150 | 0.0% | 空 |
| D_GOV_SCRIPTS | script_governance | L2_domain | 32 | 150 | 21.3% | 正常 |
| D_INFRA_A2A | a2a_communication | L0_infrastructure | 32 | 150 | 21.3% | 正常 |
| D_INFRA_OPS | asset-inventory | L0_infrastructure | 0 | 150 | 0.0% | 空 |
| D_INFRA_RECOVERY | rollback_recovery | L0_infrastructure | 48 | 150 | 32.0% | 正常 |
| D_INFRA_RUNTIME | runtime_core | L0_infrastructure | 87 | 150 | 58.0% | 正常 |
| D_INFRA_TELEMETRY | observability_profiling | L0_infrastructure | 13 | 150 | 8.7% | 正常 |
| D_INTEGRATION | pipeline_routing | L1_foundation | 30 | 150 | 20.0% | 正常 |
| D_INTEGRATION_GATEWAY | mcp_servers | L1_foundation | 14 | 150 | 9.3% | 正常 |
| D_INTELLIGENCE | context_management | L2_domain | 21 | 150 | 14.0% | 正常 |
| D_KNOWLEDGE | vector_storage | L2_domain | 0 | 150 | 0.0% | 空 |
| D_MKT_DATA | 行情数据 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_ML_SERVE | 推理 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_ML_TRAIN | model_evaluation | L2_domain | 0 | 150 | 0.0% | 空 |
| D_OPS | telemetry | L1_foundation | 3 | 150 | 2.0% | 正常 |
| D_PF_ALLOC | 组合分配 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_PF_CORE | 组合核心 | L2_domain | 4 | 150 | 2.7% | 正常 |
| D_POSITION | 仓位管理 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_REPORTING | 报告 | L1_foundation | 1 | 150 | 0.7% | 正常 |
| D_RISK | 风控 | L2_domain | 9 | 150 | 6.0% | 正常 |
| D_SECURITY | orphan_judge | L1_foundation | 80 | 150 | 53.3% | 正常 |
| D_SECURITY_LLM | llm_defense | L1_foundation | 33 | 150 | 22.0% | 正常 |
| D_SELL_DECISION | 卖出决策 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_SHARED | shared_services | L1_foundation | 94 | 150 | 62.7% | 正常 |
| D_SIGQC | signal_quality | L2_domain | 0 | 150 | 0.0% | 空 |
| D_SIMULATION | 仿真 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_TRADING | 交易运营 | L2_domain | 280 | 150 | 186.7% | 超容 |
