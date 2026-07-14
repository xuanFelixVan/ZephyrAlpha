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
| production（生产态） | 1738 | 34.7% |
| design（设计态） | 64 | 1.3% |
| prototype（原型态） | 3206 | 64.0% |
| scaffold_placeholder（脚手架） | 0 | 0.0% |
| **总计** | **5008** | **100%** |

## 构建状态统计（build_status）

| 构建状态 / Build Status | 模块数 / Modules | 占比 / Ratio |
|---------|:---:|:---:|
| generated | 4947 | 98.8% |
| planned | 39 | 0.8% |
| stable | 20 | 0.4% |
| deprecated | 2 | 0.0% |

## 各域设计成熟度统计

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 脚手架 / Scaffold | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_ASHARE_SIGNAL | ashare_signal | 8 | 0 | 0 | 8 | 0 | 0.0% |
| D_AUDITTEST | audit_test_suite | 10 | 1 | 0 | 9 | 0 | 10.0% |
| D_AUTONOMY_CORE | agent_lifecycle | 430 | 133 | 0 | 297 | 0 | 30.9% |
| D_AUTONOMY_PERM | budget_enforcement | 55 | 0 | 0 | 55 | 0 | 0.0% |
| D_BACKTEST | 回测 | 33 | 9 | 8 | 16 | 0 | 27.3% |
| D_BEHAVIORAL_AUDIT | drift_detector_core | 0 | 0 | 0 | 0 | 0 | N/A |
| D_COMPLIANCE | compliance_gate | 23 | 0 | 0 | 23 | 0 | 0.0% |
| D_CROSS_ASSET | 跨资产 | 8 | 1 | 1 | 6 | 0 | 12.5% |
| D_DATA | data_source_integrator | 59 | 9 | 0 | 50 | 0 | 15.3% |
| D_DATA_ENG | 数据工程 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DATA_GOV | 数据治理 | 30 | 0 | 0 | 30 | 0 | 0.0% |
| D_DATA_SEC | 数据安全与契约 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DIGITAL_TWIN | 数字孪生 | 8 | 0 | 1 | 7 | 0 | 0.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_EX_CORE | 执行核心 | 23 | 6 | 1 | 16 | 0 | 26.1% |
| D_EX_SOR | 执行路由 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_FACTOR | 因子 | 13 | 3 | 0 | 10 | 0 | 23.1% |
| D_FBL_DETECTORS | feedback_detectors | 65 | 59 | 0 | 6 | 0 | 90.8% |
| D_FBL_DIAGNOSERS | feedback_diagnosers | 76 | 71 | 0 | 5 | 0 | 93.4% |
| D_FBL_VERIFICATION | feedback_verification | 71 | 67 | 0 | 4 | 0 | 94.4% |
| D_FEEDBACK_LOOP | feedback_loop_engine | 229 | 110 | 0 | 119 | 0 | 48.0% |
| D_FRONTEND | 前端 | 46 | 13 | 6 | 27 | 0 | 28.3% |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal | 9 | 3 | 0 | 6 | 0 | 33.3% |
| D_GOVERNANCE | registry_management | 714 | 142 | 1 | 571 | 0 | 19.9% |
| D_GOV_AUDIT | audit_orchestration | 276 | 69 | 2 | 205 | 0 | 25.0% |
| D_GOV_CODE_QUALITY | code_quality_governance | 114 | 102 | 0 | 12 | 0 | 89.5% |
| D_GOV_DOCS | architecture_docs | 96 | 68 | 28 | 0 | 0 | 70.8% |
| D_GOV_DRIFT | drift_detection | 77 | 71 | 1 | 5 | 0 | 92.2% |
| D_GOV_ENFORCEMENT | rule_enforcement | 82 | 17 | 0 | 65 | 0 | 20.7% |
| D_GOV_KB | knowledge_base_governance | 31 | 17 | 0 | 14 | 0 | 54.8% |
| D_GOV_OPS_RESILIENCE | ops_resilience_governance | 92 | 82 | 0 | 10 | 0 | 89.1% |
| D_GOV_REPAIR | rollback | 21 | 4 | 0 | 17 | 0 | 19.0% |
| D_GOV_RULE | rule_governance | 36 | 31 | 0 | 5 | 0 | 86.1% |
| D_GOV_SCRIPTS | script_governance | 452 | 12 | 2 | 438 | 0 | 2.7% |
| D_INFRASTRUCTURE | shared_contracts | 61 | 9 | 0 | 52 | 0 | 14.8% |
| D_INFRA_A2A | a2a_communication | 133 | 29 | 0 | 104 | 0 | 21.8% |
| D_INFRA_OPS | asset-inventory | 2 | 0 | 2 | 0 | 0 | 0.0% |
| D_INFRA_RECOVERY | rollback_recovery | 89 | 48 | 0 | 41 | 0 | 53.9% |
| D_INFRA_RUNTIME | runtime_core | 328 | 145 | 3 | 180 | 0 | 44.2% |
| D_INFRA_TELEMETRY | observability_profiling | 10 | 8 | 0 | 2 | 0 | 80.0% |
| D_INTEGRATION | pipeline_routing | 103 | 53 | 0 | 50 | 0 | 51.5% |
| D_INTEGRATION_GATEWAY | mcp_servers | 2 | 1 | 0 | 1 | 0 | 50.0% |
| D_INTELLIGENCE | context_management | 109 | 22 | 0 | 87 | 0 | 20.2% |
| D_KNOWLEDGE | vector_storage | 43 | 0 | 2 | 41 | 0 | 0.0% |
| D_MKT_DATA | 行情数据 | 10 | 0 | 3 | 7 | 0 | 0.0% |
| D_ML_SERVE | 推理 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_ML_TRAIN | model_evaluation | 6 | 0 | 1 | 5 | 0 | 0.0% |
| D_OPS | telemetry | 9 | 8 | 0 | 1 | 0 | 88.9% |
| D_ORCHESTRATOR | agent_orchestrator | 82 | 59 | 0 | 23 | 0 | 72.0% |
| D_PF_ALLOC | 组合分配 | 10 | 1 | 1 | 8 | 0 | 10.0% |
| D_PF_CORE | 组合核心 | 12 | 2 | 0 | 10 | 0 | 16.7% |
| D_POSITION | 仓位管理 | 8 | 1 | 0 | 7 | 0 | 12.5% |
| D_REPORTING | 报告 | 10 | 1 | 0 | 9 | 0 | 10.0% |
| D_RISK | 风控 | 29 | 9 | 0 | 20 | 0 | 31.0% |
| D_SECURITY | orphan_judge | 212 | 101 | 0 | 111 | 0 | 47.6% |
| D_SECURITY_LLM | llm_defense | 63 | 5 | 0 | 58 | 0 | 7.9% |
| D_SELL_DECISION | 卖出决策 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_SHARED | shared_services | 298 | 109 | 0 | 189 | 0 | 36.6% |
| D_SIGLEGACY | signal_legacy | 16 | 1 | 0 | 15 | 0 | 6.2% |
| D_SIGQC | signal_quality | 8 | 0 | 0 | 8 | 0 | 0.0% |
| D_SIMULATION | 仿真 | 11 | 2 | 1 | 8 | 0 | 18.2% |
| D_TRADING | 交易运营 | 108 | 24 | 0 | 84 | 0 | 22.2% |

## 生产化率最低的域（Top 10，需优先推进）

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 7 | 0 | 0.0% |
| D_ASHARE_SIGNAL | ashare_signal | 8 | 0 | 0.0% |
| D_AUTONOMY_PERM | budget_enforcement | 55 | 0 | 0.0% |
| D_COMPLIANCE | compliance_gate | 23 | 0 | 0.0% |
| D_DATA_ENG | 数据工程 | 7 | 0 | 0.0% |
| D_DATA_GOV | 数据治理 | 30 | 0 | 0.0% |
| D_DATA_SEC | 数据安全与契约 | 7 | 0 | 0.0% |
| D_DIGITAL_TWIN | 数字孪生 | 8 | 0 | 0.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 0 | 0.0% |
| D_EX_SOR | 执行路由 | 7 | 0 | 0.0% |
