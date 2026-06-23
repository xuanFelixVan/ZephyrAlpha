---
doc_type: design_vs_production_report
title: 设计态vs运营态统计报告
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# 设计态vs运营态统计报告

> 本文档由 generate_design_vs_production.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:32:18
> 数据源: depgraph.db nodes表

## 全局统计

| 设计成熟度 | 模块数 | 占比 |
|-----------|:---:|:---:|
| production（生产态） | 1207 | 8.4% |
| design（设计态） | 8026 | 55.8% |
| prototype（原型态） | 4935 | 34.3% |
| scaffold_placeholder（脚手架） | 220 | 1.5% |
| **总计** | **14388** | **100%** |

## 构建状态统计（build_status）

| 构建状态 | 模块数 | 占比 |
|---------|:---:|:---:|
| design_only | 7991 | 55.5% |
| draft | 5509 | 38.3% |
| orphan | 711 | 4.9% |
| production | 142 | 1.0% |
| unbuilt | 25 | 0.2% |
| stable | 5 | 0.0% |
| path_invalid | 2 | 0.0% |
| active | 2 | 0.0% |
| testing | 1 | 0.0% |

## 各域设计成熟度统计

| 域ID | 域名称 | 总模块数 | 生产态 | 设计态 | 原型态 | 脚手架 | 生产化率 |
|------|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | 68 | 0 | 61 | 1 | 6 | 0.0% |
| D-AUTONOMY-CORE | agent_communication | 0 | 0 | 0 | 0 | 0 | N/A |
| D-AUTONOMY-PERM | escalation | 0 | 0 | 0 | 0 | 0 | N/A |
| D-AUTONOMY_CORE | 自治核心 | 650 | 1 | 475 | 168 | 6 | 0.2% |
| D-AUTONOMY_PERM | 自治保护 | 206 | 0 | 192 | 8 | 6 | 0.0% |
| D-BACKTEST | 回测 | 9 | 0 | 2 | 1 | 6 | 0.0% |
| D-BEHAVIORAL_AUDIT | 行为审计 | 60 | 60 | 0 | 0 | 0 | 100.0% |
| D-COMPLIANCE | 合规 | 916 | 0 | 891 | 19 | 6 | 0.0% |
| D-CROSS_ASSET | 跨资产 | 79 | 1 | 66 | 6 | 6 | 1.3% |
| D-DATA_ENG | 数据工程(增值+融合+知识) | 147 | 0 | 140 | 1 | 6 | 0.0% |
| D-DATA_GOV | 数据治理(质量+血缘+参考) | 38 | 0 | 38 | 0 | 0 | 0.0% |
| D-DATA_SEC | 数据安全与契约 | 30 | 0 | 20 | 4 | 6 | 0.0% |
| D-DIGITAL_TWIN | 数字孪生 | 13 | 0 | 6 | 1 | 6 | 0.0% |
| D-EXEC_SIM | 执行仿真 | 8 | 0 | 1 | 1 | 6 | 0.0% |
| D-EX_CORE | 执行核心 | 135 | 3 | 120 | 6 | 6 | 2.2% |
| D-EX_SOR | 执行路由 | 131 | 0 | 124 | 1 | 6 | 0.0% |
| D-FACTOR | 因子 | 320 | 2 | 302 | 10 | 6 | 0.6% |
| D-FRONTEND | 前端 | 237 | 7 | 213 | 11 | 6 | 3.0% |
| D-GOV-ENFORCEMENT | rule_enforcement | 0 | 0 | 0 | 0 | 0 | N/A |
| D-GOV-REPAIR | rollback | 0 | 0 | 0 | 0 | 0 | N/A |
| D-GOV-SCRIPTS | code_dedup | 0 | 0 | 0 | 0 | 0 | N/A |
| D-GOVERNANCE | lifecycle_management | 4289 | 138 | 611 | 3529 | 11 | 3.2% |
| D-GOV_AUDIT | audit-trail | 69 | 69 | 0 | 0 | 0 | 100.0% |
| D-GOV_DRIFT | drift_detection | 22 | 22 | 0 | 0 | 0 | 100.0% |
| D-GOV_RULE | 规则治理 | 175 | 175 | 0 | 0 | 0 | 100.0% |
| D-INFRA-OPS | resource_optimization | 0 | 0 | 0 | 0 | 0 | N/A |
| D-INFRA_OPS | 基础设施运维 | 404 | 3 | 387 | 8 | 6 | 0.7% |
| D-INFRA_RUNTIME | runtime_integration | 726 | 409 | 311 | 0 | 6 | 56.3% |
| D-INTEGRATION | pipeline_routing | 706 | 62 | 416 | 223 | 5 | 8.8% |
| D-INTEGRATION-GATEWAY | mcp_servers | 0 | 0 | 0 | 0 | 0 | N/A |
| D-INTELLIGENCE | context_management | 273 | 18 | 217 | 32 | 6 | 6.6% |
| D-KNOWLEDGE | knowledge_management | 160 | 0 | 153 | 1 | 6 | 0.0% |
| D-MKT_DATA | 行情数据(接入+存储) | 266 | 1 | 257 | 2 | 6 | 0.4% |
| D-ML-TRAIN | model_profiling | 0 | 0 | 0 | 0 | 0 | N/A |
| D-ML_SERVE | 推理 | 69 | 0 | 62 | 1 | 6 | 0.0% |
| D-ML_TRAIN | 训练 | 118 | 0 | 107 | 5 | 6 | 0.0% |
| D-OPS | feedback-loop | 641 | 1 | 259 | 375 | 6 | 0.2% |
| D-PF_ALLOC | 组合分配 | 114 | 0 | 104 | 4 | 6 | 0.0% |
| D-PF_CORE | 组合核心 | 202 | 6 | 183 | 7 | 6 | 3.0% |
| D-POSITION | 仓位管理 | 77 | 0 | 69 | 2 | 6 | 0.0% |
| D-REPORTING | 报告 | 132 | 0 | 118 | 8 | 6 | 0.0% |
| D-RISK | 风控 | 775 | 9 | 749 | 11 | 6 | 1.2% |
| D-SECURITY | adversarial_validation | 849 | 134 | 603 | 106 | 6 | 15.8% |
| D-SECURITY-LLM | llm_defense | 0 | 0 | 0 | 0 | 0 | N/A |
| D-SELL_DECISION | 卖出决策 | 64 | 0 | 57 | 1 | 6 | 0.0% |
| D-SHARED | shared_services | 288 | 62 | 7 | 219 | 0 | 21.5% |
| D-SIGNAL | 信号 | 476 | 1 | 474 | 1 | 0 | 0.2% |
| D-SIGNAL_ASHARE | A股特色信号 | 27 | 0 | 20 | 1 | 6 | 0.0% |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | 24 | 3 | 1 | 14 | 6 | 12.5% |
| D-SIGNAL_QUALITY | 信号质量 | 18 | 0 | 11 | 1 | 6 | 0.0% |
| D-SIMULATION | 仿真 | 128 | 4 | 110 | 8 | 6 | 3.1% |
| D-TRADING | 交易运营 | 249 | 16 | 89 | 138 | 6 | 6.4% |

## 生产化率最低的域（Top 10，需优先推进）

| 域ID | 域名称 | 总模块数 | 生产态 | 生产化率 |
|------|--------|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | 68 | 0 | 0.0% |
| D-AUTONOMY_PERM | 自治保护 | 206 | 0 | 0.0% |
| D-BACKTEST | 回测 | 9 | 0 | 0.0% |
| D-COMPLIANCE | 合规 | 916 | 0 | 0.0% |
| D-DATA_ENG | 数据工程(增值+融合+知识) | 147 | 0 | 0.0% |
| D-DATA_GOV | 数据治理(质量+血缘+参考) | 38 | 0 | 0.0% |
| D-DATA_SEC | 数据安全与契约 | 30 | 0 | 0.0% |
| D-DIGITAL_TWIN | 数字孪生 | 13 | 0 | 0.0% |
| D-EXEC_SIM | 执行仿真 | 8 | 0 | 0.0% |
| D-EX_SOR | 执行路由 | 131 | 0 | 0.0% |
