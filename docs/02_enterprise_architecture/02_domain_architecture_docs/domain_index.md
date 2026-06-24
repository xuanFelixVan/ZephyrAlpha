---
doc_type: domain_index
title: 域总览索引
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 域总览索引

> **文档作用 / Purpose**: 列出所有功能域的编号、ID、名称、层级、模块数等基本信息，是域架构文档的入口索引。

> 本文档由 generate_domain_index.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 23:01:39
> 数据源: depgraph.db domains表 + nodes表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 58 |
| 模块总数 | 14269 |
| 生产态模块 | 1232 |
| 设计态模块 | 8027 |
| 原型态模块 | 4794 |

## 域清单（按架构层分组）

### L0_infrastructure (2 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-INFRA_OPS | 基础设施运维 | 418 | 3 | 389 | 20 | 418/150 (超容) | [d_infra_ops.md](domains/d_infra_ops.md) |
| D-INFRA_RUNTIME | 运行时集成 | 727 | 410 | 311 | 0 | 727/150 (超容) | [d_infra_runtime.md](domains/d_infra_runtime.md) |

### L1_foundation (6 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-ALT_DATA | 另类数据 | 68 | 0 | 61 | 1 | 68/150 (OK) | [d_alt_data.md](domains/d_alt_data.md) |
| D-BEHAVIORAL_AUDIT | 行为审计 | 60 | 60 | 0 | 0 | 60/150 (OK) | [d_behavioral_audit.md](domains/d_behavioral_audit.md) |
| D-DATA_ENG | 数据工程 | 147 | 0 | 140 | 1 | 147/150 (OK) | [d_data_eng.md](domains/d_data_eng.md) |
| D-DATA_GOV | 数据治理 | 38 | 0 | 38 | 0 | 38/150 (OK) | [d_data_gov.md](domains/d_data_gov.md) |
| D-DATA_SEC | 数据安全与契约 | 30 | 0 | 20 | 4 | 30/150 (OK) | [d_data_sec.md](domains/d_data_sec.md) |
| D-MKT_DATA | 行情数据 | 266 | 1 | 257 | 2 | 266/150 (超容) | [d_mkt_data.md](domains/d_mkt_data.md) |

### L1_platform (7 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-AUTONOMY_CORE | 自治核心 | 650 | 1 | 475 | 168 | 650/150 (超容) | [d_autonomy_core.md](domains/d_autonomy_core.md) |
| D-FRONTEND | 前端 | 236 | 7 | 213 | 10 | 236/150 (超容) | [d_frontend.md](domains/d_frontend.md) |
| D-INTEGRATION | 管线路由 | 705 | 63 | 416 | 221 | 705/150 (超容) | [d_integration.md](domains/d_integration.md) |
| D-OPS | 反馈循环 | 679 | 5 | 264 | 404 | 679/150 (超容) | [d_ops.md](domains/d_ops.md) |
| D-REPORTING | 报告 | 132 | 0 | 118 | 8 | 132/150 (OK) | [d_reporting.md](domains/d_reporting.md) |
| D-SECURITY | 对抗验证 | 849 | 134 | 603 | 106 | 849/200 (超容) | [d_security.md](domains/d_security.md) |
| D-SHARED | 共享服务 | 289 | 79 | 7 | 203 | 289/150 (超容) | [d_shared.md](domains/d_shared.md) |

### L2_domain (38 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-AUTONOMY_PERM | 自治保护 | 270 | 4 | 197 | 63 | 270/150 (超容) | [d_autonomy_perm.md](domains/d_autonomy_perm.md) |
| D-BACKTEST | 回测 | 9 | 0 | 2 | 1 | 9/150 (OK) | [d_backtest.md](domains/d_backtest.md) |
| D-COMPLIANCE | 合规 | 916 | 0 | 891 | 19 | 916/150 (超容) | [d_compliance.md](domains/d_compliance.md) |
| D-CROSS_ASSET | 跨资产 | 76 | 1 | 66 | 3 | 76/150 (OK) | [d_cross_asset.md](domains/d_cross_asset.md) |
| D-DIGITAL_TWIN | 数字孪生 | 13 | 0 | 6 | 1 | 13/150 (OK) | [d_digital_twin.md](domains/d_digital_twin.md) |
| D-EXEC_SIM | 执行仿真 | 8 | 0 | 1 | 1 | 8/150 (OK) | [d_exec_sim.md](domains/d_exec_sim.md) |
| D-EX_CORE | 执行核心 | 134 | 3 | 120 | 6 | 134/150 (OK) | [d_ex_core.md](domains/d_ex_core.md) |
| D-EX_SOR | 执行路由 | 131 | 0 | 124 | 1 | 131/150 (OK) | [d_ex_sor.md](domains/d_ex_sor.md) |
| D-FACTOR | 因子 | 318 | 2 | 301 | 10 | 318/150 (超容) | [d_factor.md](domains/d_factor.md) |
| D-GOVERNANCE | 生命周期管理 | 3860 | 132 | 591 | 3126 | 3860/200 (超容) | [d_governance.md](domains/d_governance.md) |
| D-GOV_AUDIT | 审计追踪 | 217 | 69 | 6 | 142 | 217/200 (超容) | [d_gov_audit.md](domains/d_gov_audit.md) |
| D-GOV_DRIFT | 漂移检测 | 38 | 22 | 1 | 15 | 38/200 (OK) | [d_gov_drift.md](domains/d_gov_drift.md) |
| D-GOV_RULE | 规则治理 | 178 | 177 | 0 | 1 | 178/200 (OK) | [d_gov_rule.md](domains/d_gov_rule.md) |
| D-INTELLIGENCE | 上下文管理 | 273 | 18 | 217 | 32 | 273/150 (超容) | [d_intelligence.md](domains/d_intelligence.md) |
| D-KNOWLEDGE | 知识管理 | 194 | 1 | 155 | 32 | 194/150 (超容) | [d_knowledge.md](domains/d_knowledge.md) |
| D-ML_SERVE | 推理 | 69 | 0 | 62 | 1 | 69/150 (OK) | [d_ml_serve.md](domains/d_ml_serve.md) |
| D-ML_TRAIN | 训练 | 119 | 0 | 108 | 5 | 119/150 (OK) | [d_ml_train.md](domains/d_ml_train.md) |
| D-PF_ALLOC | 组合分配 | 114 | 0 | 104 | 4 | 114/150 (OK) | [d_pf_alloc.md](domains/d_pf_alloc.md) |
| D-PF_CORE | 组合核心 | 201 | 6 | 183 | 7 | 201/150 (超容) | [d_pf_core.md](domains/d_pf_core.md) |
| D-POSITION | 仓位管理 | 77 | 0 | 69 | 2 | 77/150 (OK) | [d_position.md](domains/d_position.md) |
| D-RISK | 风控 | 774 | 9 | 749 | 11 | 774/150 (超容) | [d_risk.md](domains/d_risk.md) |
| D-SELL_DECISION | 卖出决策 | 64 | 0 | 57 | 1 | 64/150 (OK) | [d_sell_decision.md](domains/d_sell_decision.md) |
| D-SIGNAL | 信号 | 476 | 1 | 474 | 1 | 476/150 (超容) | [d_signal.md](domains/d_signal.md) |
| D-SIGNAL_ASHARE | A股特色信号 | 27 | 0 | 20 | 1 | 27/150 (OK) | [d_signal_ashare.md](domains/d_signal_ashare.md) |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | 24 | 3 | 1 | 14 | 24/150 (OK) | [d_signal_fundamental.md](domains/d_signal_fundamental.md) |
| D-SIGNAL_QUALITY | 信号质量 | 18 | 0 | 11 | 1 | 18/150 (OK) | [d_signal_quality.md](domains/d_signal_quality.md) |
| D-SIMULATION | 仿真 | 128 | 4 | 110 | 8 | 128/150 (OK) | [d_simulation.md](domains/d_simulation.md) |
| D-T3-W0 | 测试域T3-0 | 0 | 0 | 0 | 0 | 0/50 (OK) | [d_t3_w0.md](domains/d_t3_w0.md) |
| D-T3-W1 | 测试域T3-1 | 0 | 0 | 0 | 0 | 0/50 (OK) | [d_t3_w1.md](domains/d_t3_w1.md) |
| D-T3-W2 | 测试域T3-2 | 0 | 0 | 0 | 0 | 0/50 (OK) | [d_t3_w2.md](domains/d_t3_w2.md) |
| D-T3-W3 | 测试域T3-3 | 0 | 0 | 0 | 0 | 0/50 (OK) | [d_t3_w3.md](domains/d_t3_w3.md) |
| D-T4-SAME | 相同域T4 | 0 | 0 | 0 | 0 | 0/50 (OK) | [d_t4_same.md](domains/d_t4_same.md) |
| D-T5-W0 | 读写并发T5-0 | 0 | 0 | 0 | 0 | 0/200 (OK) | [d_t5_w0.md](domains/d_t5_w0.md) |
| D-T5-W1 | 读写并发T5-1 | 0 | 0 | 0 | 0 | 0/200 (OK) | [d_t5_w1.md](domains/d_t5_w1.md) |
| D-T5-W2 | 读写并发T5-2 | 0 | 0 | 0 | 0 | 0/200 (OK) | [d_t5_w2.md](domains/d_t5_w2.md) |
| D-T5-W3 | 读写并发T5-3 | 0 | 0 | 0 | 0 | 0/200 (OK) | [d_t5_w3.md](domains/d_t5_w3.md) |
| D-T9-PREREQ | T9前置域 | 0 | 0 | 0 | 0 | 0/200 (OK) | [d_t9_prereq.md](domains/d_t9_prereq.md) |
| D-TRADING | 交易运营 | 249 | 17 | 89 | 137 | 249/150 (超容) | [d_trading.md](domains/d_trading.md) |

### 未分类 (5 个域)

| 域ID / Domain ID | 域名称 / Domain Name | 模块数 / Modules | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 容量 / Capacity | 文档 / Doc |
|------|--------|:---:|:---:|:---:|:---:|------|------|
| D-GOV-ENFORCEMENT | rule_enforcement | 0 | 0 | 0 | 0 | 0/200 (OK) | [d_gov_enforcement.md](domains/d_gov_enforcement.md) |
| D-GOV-REPAIR | rollback | 0 | 0 | 0 | 0 | 0/200 (OK) | [d_gov_repair.md](domains/d_gov_repair.md) |
| D-GOV-SCRIPTS | code_dedup | 0 | 0 | 0 | 0 | 0/200 (OK) | [d_gov_scripts.md](domains/d_gov_scripts.md) |
| D-INTEGRATION-GATEWAY | mcp_servers | 0 | 0 | 0 | 0 | 0/200 (OK) | [d_integration_gateway.md](domains/d_integration_gateway.md) |
| D-SECURITY-LLM | llm_defense | 0 | 0 | 0 | 0 | 0/200 (OK) | [d_security_llm.md](domains/d_security_llm.md) |
