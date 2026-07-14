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
| 域总数 | 63 |
| 超容域 | 1 |
| 接近超容域（>80%） | 3 |
| 空域（0模块） | 18 |

## 超容域清单（需拆分）

| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 超出 / Over |
|------|--------|:---:|:---:|:---:|
| D_SHARED | shared_services | 155 | 150 | +5 |

## 接近超容域清单（>80%，需关注）

| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage |
|------|--------|:---:|:---:|:---:|
| D_AUTONOMY_CORE | agent_lifecycle | 133 | 150 | 88.7% |
| D_GOVERNANCE | registry_management | 147 | 150 | 98.0% |
| D_INFRA_RUNTIME | runtime_core | 148 | 150 | 98.7% |

## 空域清单（0模块，待开发）

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 上限 / Max |
|------|--------|--------|:---:|
| D_ALT_DATA | 另类数据 | L1_foundation | 150 |
| D_ASHARE_SIGNAL | ashare_signal | L2_domain | 150 |
| D_AUTONOMY_PERM | budget_enforcement | L2_domain | 150 |
| D_BEHAVIORAL_AUDIT | drift_detector_core |  | 150 |
| D_COMPLIANCE | compliance_gate |  | 150 |
| D_DATA_ENG | 数据工程 | L1_foundation | 150 |
| D_DATA_GOV | 数据治理 | L1_foundation | 150 |
| D_DATA_SEC | 数据安全与契约 | L1_foundation | 150 |
| D_DIGITAL_TWIN | 数字孪生 | L2_domain | 150 |
| D_EXEC_SIM | 执行仿真 | L2_domain | 150 |
| D_EX_SOR | 执行路由 | L2_domain | 150 |
| D_INFRA_OPS | asset-inventory | L0_infrastructure | 150 |
| D_KNOWLEDGE | vector_storage | L2_domain | 150 |
| D_MKT_DATA | 行情数据 | L1_foundation | 150 |
| D_ML_SERVE | 推理 | L2_domain | 150 |
| D_ML_TRAIN | model_evaluation | L2_domain | 150 |
| D_SELL_DECISION | 卖出决策 | L2_domain | 150 |
| D_SIGQC | signal_quality | L2_domain | 150 |

## 完整域容量清单

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage | 状态 / Status |
|------|--------|--------|:---:|:---:|:---:|------|
| D_ALT_DATA | 另类数据 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_ASHARE_SIGNAL | ashare_signal | L2_domain | 0 | 150 | 0.0% | 空 |
| D_AUDITTEST | audit_test_suite | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_AUTONOMY_CORE | agent_lifecycle | L1_foundation | 133 | 150 | 88.7% | 接近超容 |
| D_AUTONOMY_PERM | budget_enforcement | L2_domain | 0 | 150 | 0.0% | 空 |
| D_BACKTEST | 回测 | L2_domain | 9 | 150 | 6.0% | 正常 |
| D_BEHAVIORAL_AUDIT | drift_detector_core |  | 0 | 150 | 0.0% | 空 |
| D_COMPLIANCE | compliance_gate |  | 0 | 150 | 0.0% | 空 |
| D_CROSS_ASSET | 跨资产 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_DATA | data_source_integrator |  | 7 | 150 | 4.7% | 正常 |
| D_DATA_ENG | 数据工程 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_DATA_GOV | 数据治理 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_DATA_SEC | 数据安全与契约 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_DIGITAL_TWIN | 数字孪生 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_EXEC_SIM | 执行仿真 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_EX_CORE | 执行核心 | L2_domain | 6 | 150 | 4.0% | 正常 |
| D_EX_SOR | 执行路由 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_FACTOR | 因子 | L2_domain | 3 | 150 | 2.0% | 正常 |
| D_FBL_DETECTORS | feedback_detectors | L1_foundation | 59 | 150 | 39.3% | 正常 |
| D_FBL_DIAGNOSERS | feedback_diagnosers | L1_foundation | 71 | 150 | 47.3% | 正常 |
| D_FBL_VERIFICATION | feedback_verification | L1_foundation | 67 | 150 | 44.7% | 正常 |
| D_FEEDBACK_LOOP | feedback_loop_engine | L1_foundation | 109 | 150 | 72.7% | 正常 |
| D_FRONTEND | 前端 | L1_foundation | 13 | 150 | 8.7% | 正常 |
| D_FUNDAMENTAL_SIGNAL | fundamental_signal | L2_domain | 3 | 150 | 2.0% | 正常 |
| D_GOVERNANCE | registry_management | L2_domain | 147 | 150 | 98.0% | 接近超容 |
| D_GOV_AUDIT | audit_orchestration | L2_domain | 68 | 150 | 45.3% | 正常 |
| D_GOV_CODE_QUALITY | code_quality_governance | L1_foundation | 100 | 150 | 66.7% | 正常 |
| D_GOV_DOCS | architecture_docs | L2_domain | 68 | 150 | 45.3% | 正常 |
| D_GOV_DRIFT | drift_detection | L2_domain | 71 | 150 | 47.3% | 正常 |
| D_GOV_ENFORCEMENT | rule_enforcement | L2_domain | 17 | 150 | 11.3% | 正常 |
| D_GOV_KB | knowledge_base_governance | L2_domain | 17 | 150 | 11.3% | 正常 |
| D_GOV_OPS_RESILIENCE | ops_resilience_governance | L1_foundation | 82 | 150 | 54.7% | 正常 |
| D_GOV_REPAIR | rollback | L2_domain | 4 | 150 | 2.7% | 正常 |
| D_GOV_RULE | rule_governance | L2_domain | 31 | 150 | 20.7% | 正常 |
| D_GOV_SCRIPTS | script_governance | L2_domain | 7 | 150 | 4.7% | 正常 |
| D_INFRASTRUCTURE | shared_contracts |  | 9 | 150 | 6.0% | 正常 |
| D_INFRA_A2A | a2a_communication | L0_infrastructure | 29 | 150 | 19.3% | 正常 |
| D_INFRA_OPS | asset-inventory | L0_infrastructure | 0 | 150 | 0.0% | 空 |
| D_INFRA_RECOVERY | rollback_recovery | L0_infrastructure | 48 | 150 | 32.0% | 正常 |
| D_INFRA_RUNTIME | runtime_core | L0_infrastructure | 148 | 150 | 98.7% | 接近超容 |
| D_INFRA_TELEMETRY | observability_profiling | L0_infrastructure | 8 | 150 | 5.3% | 正常 |
| D_INTEGRATION | pipeline_routing | L1_foundation | 53 | 150 | 35.3% | 正常 |
| D_INTEGRATION_GATEWAY | mcp_servers | L1_foundation | 1 | 150 | 0.7% | 正常 |
| D_INTELLIGENCE | context_management | L2_domain | 22 | 150 | 14.7% | 正常 |
| D_KNOWLEDGE | vector_storage | L2_domain | 0 | 150 | 0.0% | 空 |
| D_MKT_DATA | 行情数据 | L1_foundation | 0 | 150 | 0.0% | 空 |
| D_ML_SERVE | 推理 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_ML_TRAIN | model_evaluation | L2_domain | 0 | 150 | 0.0% | 空 |
| D_OPS | telemetry | L1_foundation | 8 | 150 | 5.3% | 正常 |
| D_ORCHESTRATOR | agent_orchestrator | L1_foundation | 59 | 150 | 39.3% | 正常 |
| D_PF_ALLOC | 组合分配 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_PF_CORE | 组合核心 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_POSITION | 仓位管理 | L2_domain | 1 | 150 | 0.7% | 正常 |
| D_REPORTING | 报告 | L1_foundation | 1 | 150 | 0.7% | 正常 |
| D_RISK | 风控 | L2_domain | 9 | 150 | 6.0% | 正常 |
| D_SECURITY | orphan_judge | L1_foundation | 101 | 150 | 67.3% | 正常 |
| D_SECURITY_LLM | llm_defense | L1_foundation | 5 | 150 | 3.3% | 正常 |
| D_SELL_DECISION | 卖出决策 | L2_domain | 0 | 150 | 0.0% | 空 |
| D_SHARED | shared_services | L1_foundation | 155 | 150 | 103.3% | 超容 |
| D_SIGLEGACY | signal_legacy |  | 1 | 150 | 0.7% | 正常 |
| D_SIGQC | signal_quality | L2_domain | 0 | 150 | 0.0% | 空 |
| D_SIMULATION | 仿真 | L2_domain | 2 | 150 | 1.3% | 正常 |
| D_TRADING | 交易运营 | L2_domain | 24 | 150 | 16.0% | 正常 |
