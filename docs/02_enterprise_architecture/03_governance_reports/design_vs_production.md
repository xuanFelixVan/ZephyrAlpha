---
doc_type: audit_report
title: 设计态vs运营态统计报告
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: task_bound
---

# 设计态vs运营态统计报告

> **文档作用 / Purpose**: 展示各域设计态模块与运营态模块的数量对比和迁移进度，跟踪从设计到落地的完成率。

> 本文档由 generate_design_vs_production.py 从 depgraph.db 自动生成
> 最后更新以 git log 为准
> 数据源: depgraph.db nodes表

## 全局统计

| 设计成熟度 / Maturity | 模块数 / Modules | 占比 / Ratio |
|-----------|:---:|:---:|
| production（生产态） | 1375 | 21.4% |
| design（设计态） | 89 | 1.4% |
| prototype（原型态） | 4964 | 77.2% |
| scaffold_placeholder（脚手架） | 0 | 0.0% |
| **总计** | **6428** | **100%** |

## 构建状态统计（build_status）

| 构建状态 / Build Status | 模块数 / Modules | 占比 / Ratio |
|---------|:---:|:---:|
| generated | 5601 | 87.1% |
| deprecated | 604 | 9.4% |
| stable | 160 | 2.5% |
| planned | 63 | 1.0% |

## 各域设计成熟度统计

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 脚手架 / Scaffold | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 8 | 1 | 0 | 7 | 0 | 12.5% |
| D_ASHARE_SIGNAL | A股特色信号 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_AUDITTEST | audit_test_suite | 152 | 142 | 0 | 10 | 0 | 93.4% |
| D_AUTONOMY_CORE | 自治核心 | 176 | 2 | 0 | 174 | 0 | 1.1% |
| D_AUTONOMY_PERM | 自治保护 | 70 | 2 | 1 | 67 | 0 | 2.9% |
| D_BACKTEST | 回测 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_BEHAVIORAL_AUDIT | 行为审计 | 78 | 78 | 0 | 0 | 0 | 100.0% |
| D_COMPLIANCE | 合规 | 25 | 0 | 0 | 25 | 0 | 0.0% |
| D_CROSS_ASSET | 跨资产 | 11 | 1 | 1 | 9 | 0 | 9.1% |
| D_DATA_ENG | 数据工程 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DATA_GOV | 数据治理 | 0 | 0 | 0 | 0 | 0 | N/A |
| D_DATA_SEC | 数据安全与契约 | 10 | 0 | 0 | 10 | 0 | 0.0% |
| D_DIGITAL_TWIN | 数字孪生 | 8 | 0 | 1 | 7 | 0 | 0.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_EX_CORE | 执行核心 | 14 | 3 | 0 | 11 | 0 | 21.4% |
| D_EX_SOR | 执行路由 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_FACTOR | 因子 | 17 | 2 | 0 | 15 | 0 | 11.8% |
| D_FRONTEND | 前端 | 23 | 7 | 0 | 16 | 0 | 30.4% |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | 25 | 4 | 0 | 21 | 0 | 16.0% |
| D_GOV_REPAIR | rollback | 0 | 0 | 0 | 0 | 0 | N/A |
| D_GOVERNANCE | 生命周期管理 | 2825 | 117 | 50 | 2658 | 0 | 4.1% |
| D_GOV_AUDIT | 审计追踪 | 185 | 54 | 2 | 129 | 0 | 29.2% |
| D_GOV_DOCS | architecture_docs | 127 | 78 | 0 | 49 | 0 | 61.4% |
| D_GOV_DRIFT | 漂移检测 | 24 | 9 | 1 | 14 | 0 | 37.5% |
| D_GOV_ENFORCEMENT | rule_enforcement | 107 | 69 | 0 | 38 | 0 | 64.5% |
| D_GOV_RULE | 规则治理 | 11 | 11 | 0 | 0 | 0 | 100.0% |
| D_GOV_SCRIPTS | code_dedup | 413 | 26 | 0 | 387 | 0 | 6.3% |
| D_INFRA_A2A | a2a_communication | 101 | 101 | 0 | 0 | 0 | 100.0% |
| D_INFRA_OPS | 基础设施运维 | 34 | 7 | 1 | 26 | 0 | 20.6% |
| D_INFRA_RECOVERY | rollback_recovery | 107 | 107 | 0 | 0 | 0 | 100.0% |
| D_INFRA_RUNTIME | 运行时集成 | 145 | 139 | 0 | 6 | 0 | 95.9% |
| D_INFRA_TELEMETRY | observability_profiling | 37 | 37 | 0 | 0 | 0 | 100.0% |
| D_INTEGRATION | 管线路由 | 282 | 70 | 0 | 212 | 0 | 24.8% |
| D_INTEGRATION_GATEWAY | mcp_servers | 0 | 0 | 0 | 0 | 0 | N/A |
| D_INTELLIGENCE | 上下文管理 | 42 | 17 | 0 | 25 | 0 | 40.5% |
| D_KNOWLEDGE | 知识管理 | 40 | 1 | 2 | 37 | 0 | 2.5% |
| D_MKT_DATA | 行情数据 | 9 | 1 | 0 | 8 | 0 | 11.1% |
| D_ML_SERVE | 推理 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_ML_TRAIN | 训练 | 12 | 0 | 1 | 11 | 0 | 0.0% |
| D_OPS | 反馈循环 | 433 | 24 | 1 | 408 | 0 | 5.5% |
| D_PF_ALLOC | 组合分配 | 11 | 0 | 1 | 10 | 0 | 0.0% |
| D_PF_CORE | 组合核心 | 44 | 6 | 26 | 12 | 0 | 13.6% |
| D_POSITION | 仓位管理 | 8 | 0 | 0 | 8 | 0 | 0.0% |
| D_REPORTING | 报告 | 15 | 1 | 0 | 14 | 0 | 6.7% |
| D_RISK | 风控 | 25 | 9 | 0 | 16 | 0 | 36.0% |
| D_SECURITY | 对抗验证 | 243 | 132 | 0 | 111 | 0 | 54.3% |
| D_SECURITY_LLM | llm_defense | 0 | 0 | 0 | 0 | 0 | N/A |
| D_SELL_DECISION | 卖出决策 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_SHARED | 共享服务 | 295 | 93 | 0 | 202 | 0 | 31.5% |
| D_SIGLEGACY | 信号遗留设计态 | 0 | 0 | 0 | 0 | 0 | N/A |
| D_SIGQC | 信号质量控制 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_SIMULATION | 仿真 | 19 | 4 | 1 | 14 | 0 | 21.1% |
| D_TRADING | 交易运营 | 161 | 20 | 0 | 141 | 0 | 12.4% |

## 生产化率最低的域（Top 10，需优先推进）

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|
| D_ASHARE_SIGNAL | A股特色信号 | 7 | 0 | 0.0% |
| D_BACKTEST | 回测 | 7 | 0 | 0.0% |
| D_COMPLIANCE | 合规 | 25 | 0 | 0.0% |
| D_DATA_ENG | 数据工程 | 7 | 0 | 0.0% |
| D_DATA_SEC | 数据安全与契约 | 10 | 0 | 0.0% |
| D_DIGITAL_TWIN | 数字孪生 | 8 | 0 | 0.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 0 | 0.0% |
| D_EX_SOR | 执行路由 | 7 | 0 | 0.0% |
| D_ML_SERVE | 推理 | 7 | 0 | 0.0% |
| D_ML_TRAIN | 训练 | 12 | 0 | 0.0% |
