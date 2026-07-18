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
| production（生产态） | 1565 | 58.5% |
| design（设计态） | 62 | 2.3% |
| prototype（原型态） | 1048 | 39.2% |
| scaffold_placeholder（脚手架） | 0 | 0.0% |
| **总计** | **2675** | **100%** |

## 构建状态统计（build_status）

| 构建状态 / Build Status | 模块数 / Modules | 占比 / Ratio |
|---------|:---:|:---:|
| generated | 3311 | 123.8% |
| stable | 1610 | 60.2% |
| planned | 38 | 1.4% |
| deprecated | 2 | 0.1% |

## 各域设计成熟度统计

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 脚手架 / Scaffold | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_ASHARE_SIGNAL | ashare_signal | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_AUDITTEST | audit_test_suite | 1 | 1 | 0 | 0 | 0 | 100.0% |
| D_AUTONOMY_CORE | agent_lifecycle | 137 | 131 | 0 | 6 | 0 | 95.6% |
| D_AUTONOMY_PERM | budget_enforcement | 2 | 0 | 0 | 2 | 0 | 0.0% |
| D_BACKTEST | 回测 | 25 | 9 | 8 | 8 | 0 | 36.0% |
| D_BEHAVIORAL_AUDIT | drift_detector_core | 0 | 0 | 0 | 0 | 0 | N/A |
| D_COMPLIANCE | compliance_gate | 4 | 0 | 0 | 4 | 0 | 0.0% |
| D_CROSS_ASSET | 跨资产 | 8 | 0 | 1 | 7 | 0 | 0.0% |
| D_DATA | data_source_integrator | 42 | 9 | 0 | 33 | 0 | 21.4% |
| D_DATA_ENG | 数据工程 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DATA_GOV | 数据治理 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DATA_SEC | 数据安全与契约 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DIGITAL_TWIN | 数字孪生 | 8 | 0 | 1 | 7 | 0 | 0.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_EX_CORE | 执行核心 | 8 | 4 | 1 | 3 | 0 | 50.0% |
| D_EX_SOR | 执行路由 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_FACTOR | 因子 | 5 | 2 | 0 | 3 | 0 | 40.0% |
| D_FBL_DETECTORS | feedback_detectors | 65 | 59 | 0 | 6 | 0 | 90.8% |
| D_FBL_DIAGNOSERS | feedback_diagnosers | 76 | 71 | 0 | 5 | 0 | 93.4% |
| D_FBL_VERIFICATION | feedback_verification | 71 | 67 | 0 | 4 | 0 | 94.4% |
| D_FEEDBACK_LOOP | feedback_loop_engine | 124 | 112 | 0 | 12 | 0 | 90.3% |
| D_FRONTEND | 前端 | 18 | 9 | 6 | 3 | 0 | 50.0% |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal | 10 | 4 | 0 | 6 | 0 | 40.0% |
| D_GOVERNANCE | registry_management | 213 | 96 | 1 | 116 | 0 | 45.1% |
| D_GOV_AUDIT | audit_orchestration | 100 | 67 | 2 | 31 | 0 | 67.0% |
| D_GOV_CODE_QUALITY | code_quality_governance | 126 | 110 | 0 | 16 | 0 | 87.3% |
| D_GOV_DOCS | architecture_docs | 28 | 0 | 28 | 0 | 0 | 0.0% |
| D_GOV_DRIFT | drift_detection | 74 | 70 | 1 | 3 | 0 | 94.6% |
| D_GOV_ENFORCEMENT | rule_enforcement | 31 | 15 | 0 | 16 | 0 | 48.4% |
| D_GOV_KB | knowledge_base_governance | 31 | 18 | 0 | 13 | 0 | 58.1% |
| D_GOV_OPS_RESILIENCE | ops_resilience_governance | 90 | 81 | 0 | 9 | 0 | 90.0% |
| D_GOV_REPAIR | rollback | 1 | 1 | 0 | 0 | 0 | 100.0% |
| D_GOV_RULE | rule_governance | 35 | 31 | 0 | 4 | 0 | 88.6% |
| D_GOV_SCRIPTS | script_governance | 356 | 10 | 2 | 344 | 0 | 2.8% |
| D_INFRASTRUCTURE | shared_contracts | 26 | 12 | 0 | 14 | 0 | 46.2% |
| D_INFRA_A2A | a2a_communication | 72 | 28 | 0 | 44 | 0 | 38.9% |
| D_INFRA_OPS | asset-inventory | 2 | 0 | 2 | 0 | 0 | 0.0% |
| D_INFRA_RECOVERY | rollback_recovery | 54 | 48 | 0 | 6 | 0 | 88.9% |
| D_INFRA_RUNTIME | runtime_core | 159 | 118 | 1 | 40 | 0 | 74.2% |
| D_INFRA_TELEMETRY | observability_profiling | 0 | 0 | 0 | 0 | 0 | N/A |
| D_INTEGRATION | pipeline_routing | 77 | 50 | 0 | 27 | 0 | 64.9% |
| D_INTEGRATION_GATEWAY | mcp_servers | 0 | 0 | 0 | 0 | 0 | N/A |
| D_INTELLIGENCE | context_management | 30 | 21 | 0 | 9 | 0 | 70.0% |
| D_KNOWLEDGE | vector_storage | 4 | 0 | 2 | 2 | 0 | 0.0% |
| D_MKT_DATA | 行情数据 | 10 | 0 | 3 | 7 | 0 | 0.0% |
| D_ML_SERVE | 推理 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_ML_TRAIN | model_evaluation | 4 | 0 | 1 | 3 | 0 | 0.0% |
| D_OPS | telemetry | 9 | 8 | 0 | 1 | 0 | 88.9% |
| D_ORCHESTRATOR | agent_orchestrator | 72 | 58 | 0 | 14 | 0 | 80.6% |
| D_PF_ALLOC | 组合分配 | 3 | 1 | 1 | 1 | 0 | 33.3% |
| D_PF_CORE | 组合核心 | 1 | 0 | 0 | 1 | 0 | 0.0% |
| D_POSITION | 仓位管理 | 1 | 1 | 0 | 0 | 0 | 100.0% |
| D_REPORTING | 报告 | 3 | 1 | 0 | 2 | 0 | 33.3% |
| D_RISK | 风控 | 11 | 9 | 0 | 2 | 0 | 81.8% |
| D_SECURITY | orphan_judge | 165 | 99 | 0 | 66 | 0 | 60.0% |
| D_SECURITY_LLM | llm_defense | 0 | 0 | 0 | 0 | 0 | N/A |
| D_SELL_DECISION | 卖出决策 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_SHARED | shared_services | 183 | 111 | 0 | 72 | 0 | 60.7% |
| D_SIGLEGACY | signal_legacy | 0 | 0 | 0 | 0 | 0 | N/A |
| D_SIGQC | signal_quality | 2 | 0 | 0 | 2 | 0 | 0.0% |
| D_SIMULATION | 仿真 | 3 | 2 | 1 | 0 | 0 | 66.7% |
| D_TRADING | 交易运营 | 32 | 21 | 0 | 11 | 0 | 65.6% |

## 生产化率最低的域（Top 10，需优先推进）

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 7 | 0 | 0.0% |
| D_ASHARE_SIGNAL | ashare_signal | 7 | 0 | 0.0% |
| D_AUTONOMY_PERM | budget_enforcement | 2 | 0 | 0.0% |
| D_COMPLIANCE | compliance_gate | 4 | 0 | 0.0% |
| D_CROSS_ASSET | 跨资产 | 8 | 0 | 0.0% |
| D_DATA_ENG | 数据工程 | 7 | 0 | 0.0% |
| D_DATA_GOV | 数据治理 | 7 | 0 | 0.0% |
| D_DATA_SEC | 数据安全与契约 | 7 | 0 | 0.0% |
| D_DIGITAL_TWIN | 数字孪生 | 8 | 0 | 0.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 0 | 0.0% |
