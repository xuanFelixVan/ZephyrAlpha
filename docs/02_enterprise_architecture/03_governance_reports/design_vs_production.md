---
doc_type: audit_report
title: 设计态vs运营态统计报告
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# 设计态vs运营态统计报告

> **文档作用 / Purpose**: 展示各域设计态模块与运营态模块的数量对比和迁移进度，跟踪从设计到落地的完成率。

> 本文档由 generate_design_vs_production.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph (PostgreSQL) nodes表

## 全局统计

| 设计成熟度 / Maturity | 模块数 / Modules | 占比 / Ratio |
|-----------|:---:|:---:|
| production（生产态） | 1598 | 32.0% |
| design（设计态） | 53 | 1.1% |
| prototype（原型态） | 3338 | 66.9% |
| scaffold_placeholder（脚手架） | 0 | 0.0% |
| **总计** | **4989** | **100%** |

## 构建状态统计（build_status）

| 构建状态 / Build Status | 模块数 / Modules | 占比 / Ratio |
|---------|:---:|:---:|
| generated | 4935 | 98.9% |
| planned | 36 | 0.7% |
| stable | 18 | 0.4% |

## 各域设计成熟度统计

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 脚手架 / Scaffold | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_ASHARE_SIGNAL | ashare_signal | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_AUDITTEST | audit_test_suite | 1727 | 49 | 0 | 1678 | 0 | 2.8% |
| D_AUTONOMY_CORE | agent_lifecycle | 114 | 111 | 0 | 3 | 0 | 97.4% |
| D_AUTONOMY_PERM | budget_enforcement | 14 | 0 | 0 | 14 | 0 | 0.0% |
| D_BACKTEST | 回测 | 33 | 9 | 8 | 16 | 0 | 27.3% |
| D_CROSS_ASSET | 跨资产 | 8 | 1 | 1 | 6 | 0 | 12.5% |
| D_DATA_ENG | 数据工程 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DATA_GOV | 数据治理 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DATA_SEC | 数据安全与契约 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DIGITAL_TWIN | 数字孪生 | 8 | 0 | 1 | 7 | 0 | 0.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_EX_CORE | 执行核心 | 15 | 5 | 1 | 9 | 0 | 33.3% |
| D_EX_SOR | 执行路由 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_FACTOR | 因子 | 14 | 4 | 0 | 10 | 0 | 28.6% |
| D_FRONTEND | 前端 | 30 | 13 | 6 | 11 | 0 | 43.3% |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal | 25 | 4 | 0 | 21 | 0 | 16.0% |
| D_GOVERNANCE | registry_management | 854 | 483 | 27 | 344 | 0 | 56.6% |
| D_GOV_AUDIT | audit_orchestration | 2 | 0 | 2 | 0 | 0 | 0.0% |
| D_GOV_DOCS | architecture_docs | 2 | 2 | 0 | 0 | 0 | 100.0% |
| D_GOV_DRIFT | drift_detection | 1 | 0 | 1 | 0 | 0 | 0.0% |
| D_GOV_ENFORCEMENT | rule_enforcement | 201 | 133 | 0 | 68 | 0 | 66.2% |
| D_GOV_REPAIR | rollback | 0 | 0 | 0 | 0 | 0 | N/A |
| D_GOV_RULE | rule_governance | 0 | 0 | 0 | 0 | 0 | N/A |
| D_GOV_SCRIPTS | script_governance | 435 | 32 | 0 | 403 | 0 | 7.4% |
| D_INFRA_A2A | a2a_communication | 89 | 32 | 0 | 57 | 0 | 36.0% |
| D_INFRA_OPS | asset-inventory | 1 | 0 | 1 | 0 | 0 | 0.0% |
| D_INFRA_RECOVERY | rollback_recovery | 54 | 48 | 0 | 6 | 0 | 88.9% |
| D_INFRA_RUNTIME | runtime_core | 132 | 87 | 0 | 45 | 0 | 65.9% |
| D_INFRA_TELEMETRY | observability_profiling | 25 | 13 | 0 | 12 | 0 | 52.0% |
| D_INTEGRATION | pipeline_routing | 72 | 30 | 0 | 42 | 0 | 41.7% |
| D_INTEGRATION_GATEWAY | mcp_servers | 20 | 14 | 0 | 6 | 0 | 70.0% |
| D_INTELLIGENCE | context_management | 43 | 21 | 0 | 22 | 0 | 48.8% |
| D_KNOWLEDGE | vector_storage | 9 | 0 | 2 | 7 | 0 | 0.0% |
| D_MKT_DATA | 行情数据 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_ML_SERVE | 推理 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_ML_TRAIN | model_evaluation | 12 | 0 | 1 | 11 | 0 | 0.0% |
| D_OPS | telemetry | 3 | 3 | 0 | 0 | 0 | 100.0% |
| D_PF_ALLOC | 组合分配 | 8 | 0 | 1 | 7 | 0 | 0.0% |
| D_PF_CORE | 组合核心 | 14 | 4 | 0 | 10 | 0 | 28.6% |
| D_POSITION | 仓位管理 | 8 | 1 | 0 | 7 | 0 | 12.5% |
| D_REPORTING | 报告 | 10 | 1 | 0 | 9 | 0 | 10.0% |
| D_RISK | 风控 | 20 | 9 | 0 | 11 | 0 | 45.0% |
| D_SECURITY | orphan_judge | 147 | 80 | 0 | 67 | 0 | 54.4% |
| D_SECURITY_LLM | llm_defense | 44 | 33 | 0 | 11 | 0 | 75.0% |
| D_SELL_DECISION | 卖出决策 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_SHARED | shared_services | 225 | 94 | 0 | 131 | 0 | 41.8% |
| D_SIGQC | signal_quality | 8 | 0 | 0 | 8 | 0 | 0.0% |
| D_SIMULATION | 仿真 | 11 | 2 | 1 | 8 | 0 | 18.2% |
| D_TRADING | 交易运营 | 481 | 280 | 0 | 201 | 0 | 58.2% |

## 生产化率最低的域（Top 10，需优先推进）

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 7 | 0 | 0.0% |
| D_ASHARE_SIGNAL | ashare_signal | 7 | 0 | 0.0% |
| D_AUTONOMY_PERM | budget_enforcement | 14 | 0 | 0.0% |
| D_DATA_ENG | 数据工程 | 7 | 0 | 0.0% |
| D_DATA_GOV | 数据治理 | 7 | 0 | 0.0% |
| D_DATA_SEC | 数据安全与契约 | 7 | 0 | 0.0% |
| D_DIGITAL_TWIN | 数字孪生 | 8 | 0 | 0.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 0 | 0.0% |
| D_EX_SOR | 执行路由 | 7 | 0 | 0.0% |
| D_GOV_AUDIT | audit_orchestration | 2 | 0 | 0.0% |
