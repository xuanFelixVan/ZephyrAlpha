---
doc_type: design_vs_production_report
title: 设计态vs运营态统计报告
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 设计态vs运营态统计报告

> **文档作用 / Purpose**: 展示各域设计态模块与运营态模块的数量对比和迁移进度，跟踪从设计到落地的完成率。

> 本文档由 generate_design_vs_production.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-25 03:41:37
> 数据源: depgraph.db nodes表

## 全局统计

| 设计成熟度 / Maturity | 模块数 / Modules | 占比 / Ratio |
|-----------|:---:|:---:|
| production（生产态） | 1428 | 20.9% |
| design（设计态） | 403 | 5.9% |
| prototype（原型态） | 5010 | 73.2% |
| scaffold_placeholder（脚手架） | 0 | 0.0% |
| **总计** | **6841** | **100%** |

## 构建状态统计（build_status）

| 构建状态 / Build Status | 模块数 / Modules | 占比 / Ratio |
|---------|:---:|:---:|
| generated | 5676 | 83.0% |
| deprecated | 628 | 9.2% |
| planned | 343 | 5.0% |
| stable | 194 | 2.8% |

## 各域设计成熟度统计

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 脚手架 / Scaffold | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | 8 | 1 | 0 | 7 | 0 | 12.5% |
| D-AUTONOMY_CORE | 自治核心 | 181 | 2 | 5 | 174 | 0 | 1.1% |
| D-AUTONOMY_PERM | 自治保护 | 88 | 2 | 19 | 67 | 0 | 2.3% |
| D-BACKTEST | 回测 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D-BEHAVIORAL_AUDIT | 行为审计 | 79 | 79 | 0 | 0 | 0 | 100.0% |
| D-COMPLIANCE | 合规 | 30 | 0 | 5 | 25 | 0 | 0.0% |
| D-CROSS_ASSET | 跨资产 | 15 | 1 | 5 | 9 | 0 | 6.7% |
| D-DATA_ENG | 数据工程 | 11 | 0 | 4 | 7 | 0 | 0.0% |
| D-DATA_GOV | 数据治理 | 0 | 0 | 0 | 0 | 0 | N/A |
| D-DATA_SEC | 数据安全与契约 | 10 | 0 | 0 | 10 | 0 | 0.0% |
| D-DIGITAL_TWIN | 数字孪生 | 12 | 0 | 5 | 7 | 0 | 0.0% |
| D-EXEC_SIM | 执行仿真 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D-EX_CORE | 执行核心 | 14 | 3 | 0 | 11 | 0 | 21.4% |
| D-EX_SOR | 执行路由 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D-FACTOR | 因子 | 17 | 2 | 0 | 15 | 0 | 11.8% |
| D-FRONTEND | 前端 | 33 | 7 | 10 | 16 | 0 | 21.2% |
| D-GOV-DOCS | architecture_docs | 151 | 100 | 0 | 51 | 0 | 66.2% |
| D-GOV-ENFORCEMENT | rule_enforcement | 107 | 69 | 0 | 38 | 0 | 64.5% |
| D-GOV-REPAIR | rollback | 0 | 0 | 0 | 0 | 0 | N/A |
| D-GOV-SCRIPTS | code_dedup | 416 | 26 | 0 | 390 | 0 | 6.2% |
| D-GOVERNANCE | 生命周期管理 | 2843 | 117 | 62 | 2664 | 0 | 4.1% |
| D-GOV_AUDIT | 审计追踪 | 189 | 54 | 3 | 132 | 0 | 28.6% |
| D-GOV_AUDIT_TESTS | audit_test_suite | 152 | 142 | 0 | 10 | 0 | 93.4% |
| D-GOV_DRIFT | 漂移检测 | 25 | 9 | 2 | 14 | 0 | 36.0% |
| D-GOV_RULE | 规则治理 | 12 | 11 | 1 | 0 | 0 | 91.7% |
| D-INFRA_A2A | a2a_communication | 114 | 114 | 0 | 0 | 0 | 100.0% |
| D-INFRA_OPS | 基础设施运维 | 46 | 7 | 13 | 26 | 0 | 15.2% |
| D-INFRA_RECOVERY | rollback_recovery | 107 | 107 | 0 | 0 | 0 | 100.0% |
| D-INFRA_RUNTIME | 运行时集成 | 148 | 139 | 3 | 6 | 0 | 93.9% |
| D-INFRA_TELEMETRY | observability_profiling | 51 | 51 | 0 | 0 | 0 | 100.0% |
| D-INTEGRATION | 管线路由 | 314 | 71 | 17 | 226 | 0 | 22.6% |
| D-INTEGRATION-GATEWAY | mcp_servers | 0 | 0 | 0 | 0 | 0 | N/A |
| D-INTELLIGENCE | 上下文管理 | 57 | 18 | 1 | 38 | 0 | 31.6% |
| D-KNOWLEDGE | 知识管理 | 50 | 1 | 11 | 38 | 0 | 2.0% |
| D-MKT_DATA | 行情数据 | 10 | 1 | 1 | 8 | 0 | 10.0% |
| D-ML_SERVE | 推理 | 8 | 0 | 1 | 7 | 0 | 0.0% |
| D-ML_TRAIN | 训练 | 13 | 0 | 2 | 11 | 0 | 0.0% |
| D-OPS | 反馈循环 | 445 | 24 | 13 | 408 | 0 | 5.4% |
| D-PF_ALLOC | 组合分配 | 15 | 0 | 5 | 10 | 0 | 0.0% |
| D-PF_CORE | 组合核心 | 48 | 6 | 30 | 12 | 0 | 12.5% |
| D-POSITION | 仓位管理 | 8 | 0 | 0 | 8 | 0 | 0.0% |
| D-REPORTING | 报告 | 19 | 1 | 4 | 14 | 0 | 5.3% |
| D-RISK | 风控 | 82 | 9 | 57 | 16 | 0 | 11.0% |
| D-SECURITY | 对抗验证 | 276 | 132 | 32 | 112 | 0 | 47.8% |
| D-SECURITY-LLM | llm_defense | 0 | 0 | 0 | 0 | 0 | N/A |
| D-SELL_DECISION | 卖出决策 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D-SHARED | 共享服务 | 303 | 94 | 6 | 203 | 0 | 31.0% |
| D-SIGNAL | 信号 | 47 | 1 | 45 | 1 | 0 | 2.1% |
| D-SIGNAL_ASHARE | A股特色信号 | 27 | 0 | 20 | 7 | 0 | 0.0% |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | 23 | 3 | 0 | 20 | 0 | 13.0% |
| D-SIGNAL_QUALITY | 信号质量 | 17 | 0 | 10 | 7 | 0 | 0.0% |
| D-SIMULATION | 仿真 | 23 | 4 | 5 | 14 | 0 | 17.4% |
| D-TRADING | 交易运营 | 169 | 20 | 6 | 143 | 0 | 11.8% |

## 生产化率最低的域（Top 10，需优先推进）

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|
| D-BACKTEST | 回测 | 7 | 0 | 0.0% |
| D-COMPLIANCE | 合规 | 30 | 0 | 0.0% |
| D-DATA_ENG | 数据工程 | 11 | 0 | 0.0% |
| D-DATA_SEC | 数据安全与契约 | 10 | 0 | 0.0% |
| D-DIGITAL_TWIN | 数字孪生 | 12 | 0 | 0.0% |
| D-EXEC_SIM | 执行仿真 | 7 | 0 | 0.0% |
| D-EX_SOR | 执行路由 | 7 | 0 | 0.0% |
| D-ML_SERVE | 推理 | 8 | 0 | 0.0% |
| D-ML_TRAIN | 训练 | 13 | 0 | 0.0% |
| D-PF_ALLOC | 组合分配 | 15 | 0 | 0.0% |
