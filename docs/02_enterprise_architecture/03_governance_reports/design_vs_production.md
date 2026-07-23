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
| production（生产态） | 2718 | 97.1% |
| design（设计态） | 80 | 2.9% |
| scaffold_placeholder（脚手架） | 0 | 0.0% |
| **总计** | **2798** | **100%** |

## 构建状态统计（build_status）

| 构建状态 / Build Status | 模块数 / Modules | 占比 / Ratio |
|---------|:---:|:---:|
| generated | 3862 | 138.0% |
| stable | 1613 | 57.6% |
| planned | 74 | 2.6% |
| deprecated | 4 | 0.1% |

## 各域设计成熟度统计

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 设计态 / Design | 脚手架 / Scaffold | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 7 | 7 | 0 | 0 | 100.0% |
| D_ASHARE_SIGNAL | A股特色信号 | 7 | 7 | 0 | 0 | 100.0% |
| D_AUDITTEST | 审计测试套件 | 1 | 1 | 0 | 0 | 100.0% |
| D_AUTONOMY_CORE | 自治核心 | 130 | 130 | 0 | 0 | 100.0% |
| D_AUTONOMY_PERM | 自治保护 | 2 | 2 | 0 | 0 | 100.0% |
| D_BACKTEST | 回测 | 17 | 17 | 0 | 0 | 100.0% |
| D_BEHAVIORAL_AUDIT | 行为审计 | 0 | 0 | 0 | 0 | N/A |
| D_COMPLIANCE | 合规 | 2 | 2 | 0 | 0 | 100.0% |
| D_CROSS_ASSET | 跨资产 | 7 | 7 | 0 | 0 | 100.0% |
| D_DATA | 数据接入层 | 80 | 77 | 3 | 0 | 96.2% |
| D_DATA_ENG | 数据工程 | 7 | 7 | 0 | 0 | 100.0% |
| D_DATA_GOV | 数据治理 | 7 | 7 | 0 | 0 | 100.0% |
| D_DATA_SEC | 数据安全与契约 | 7 | 7 | 0 | 0 | 100.0% |
| D_DIGITAL_TWIN | 数字孪生 | 7 | 7 | 0 | 0 | 100.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 7 | 0 | 0 | 100.0% |
| D_EX_CORE | 执行核心 | 7 | 7 | 0 | 0 | 100.0% |
| D_EX_SOR | 执行路由 | 7 | 7 | 0 | 0 | 100.0% |
| D_FACTOR | 因子 | 50 | 5 | 45 | 0 | 10.0% |
| D_FBL_DETECTORS | 反馈检测器 | 65 | 65 | 0 | 0 | 100.0% |
| D_FBL_DIAGNOSERS | 反馈诊断器 | 76 | 76 | 0 | 0 | 100.0% |
| D_FBL_VERIFICATION | 反馈验证 | 71 | 71 | 0 | 0 | 100.0% |
| D_FEEDBACK_LOOP | 反馈循环引擎 | 125 | 125 | 0 | 0 | 100.0% |
| D_FRONTEND | 前端 | 12 | 12 | 0 | 0 | 100.0% |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | 10 | 10 | 0 | 0 | 100.0% |
| D_GOVERNANCE | 生命周期管理 | 218 | 218 | 0 | 0 | 100.0% |
| D_GOV_AUDIT | 审计追踪 | 124 | 121 | 3 | 0 | 97.6% |
| D_GOV_CODE_QUALITY | 代码质量治理 | 169 | 168 | 1 | 0 | 99.4% |
| D_GOV_DOCS | 架构文档治理 | 26 | 2 | 24 | 0 | 7.7% |
| D_GOV_DRIFT | 漂移检测 | 75 | 74 | 1 | 0 | 98.7% |
| D_GOV_ENFORCEMENT | 规则执行 | 40 | 40 | 0 | 0 | 100.0% |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 | 91 | 91 | 0 | 0 | 100.0% |
| D_GOV_REPAIR | 治理修复 | 1 | 1 | 0 | 0 | 100.0% |
| D_GOV_RULE | 规则治理 | 35 | 35 | 0 | 0 | 100.0% |
| D_GOV_SCRIPTS | 脚本治理 | 377 | 377 | 0 | 0 | 100.0% |
| D_INFRASTRUCTURE | 跨层契约基础设施 | 26 | 26 | 0 | 0 | 100.0% |
| D_INFRA_A2A | A2A通信 | 72 | 72 | 0 | 0 | 100.0% |
| D_INFRA_OPS | 基础设施运维 | 0 | 0 | 0 | 0 | N/A |
| D_INFRA_RECOVERY | 回滚恢复 | 55 | 55 | 0 | 0 | 100.0% |
| D_INFRA_RUNTIME | 运行时集成 | 161 | 160 | 1 | 0 | 99.4% |
| D_INFRA_TELEMETRY | 可观测性 | 0 | 0 | 0 | 0 | N/A |
| D_INTEGRATION | 管线路由 | 71 | 71 | 0 | 0 | 100.0% |
| D_INTEGRATION_GATEWAY | 集成网关 | 0 | 0 | 0 | 0 | N/A |
| D_INTELLIGENCE | 上下文管理 | 30 | 30 | 0 | 0 | 100.0% |
| D_KNOWLEDGE | 知识管理 | 1 | 0 | 1 | 0 | 0.0% |
| D_MKT_DATA | 行情数据 | 7 | 7 | 0 | 0 | 100.0% |
| D_ML_SERVE | 推理 | 7 | 7 | 0 | 0 | 100.0% |
| D_ML_TRAIN | 训练 | 4 | 3 | 1 | 0 | 75.0% |
| D_OPS | 反馈循环 | 11 | 11 | 0 | 0 | 100.0% |
| D_ORCHESTRATOR | 代理编排器 | 70 | 70 | 0 | 0 | 100.0% |
| D_PF_ALLOC | 组合分配 | 2 | 2 | 0 | 0 | 100.0% |
| D_PF_CORE | 组合核心 | 1 | 1 | 0 | 0 | 100.0% |
| D_POSITION | 仓位管理 | 1 | 1 | 0 | 0 | 100.0% |
| D_REPORTING | 报告 | 3 | 3 | 0 | 0 | 100.0% |
| D_RISK | 风控 | 11 | 11 | 0 | 0 | 100.0% |
| D_SECURITY | 对抗验证 | 166 | 166 | 0 | 0 | 100.0% |
| D_SECURITY_LLM | LLM防御 | 0 | 0 | 0 | 0 | N/A |
| D_SELL_DECISION | 卖出决策 | 7 | 7 | 0 | 0 | 100.0% |
| D_SHARED | 共享服务 | 184 | 184 | 0 | 0 | 100.0% |
| D_SIGLEGACY | 信号遗留设计态 | 0 | 0 | 0 | 0 | N/A |
| D_SIGQC | 信号质量控制 | 2 | 2 | 0 | 0 | 100.0% |
| D_SIMULATION | 仿真 | 2 | 2 | 0 | 0 | 100.0% |
| D_TRADING | 交易运营 | 37 | 37 | 0 | 0 | 100.0% |

## 生产化率最低的域（Top 10，需优先推进）

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|
| D_KNOWLEDGE | 知识管理 | 1 | 0 | 0.0% |
| D_GOV_DOCS | 架构文档治理 | 26 | 2 | 7.7% |
| D_FACTOR | 因子 | 50 | 5 | 10.0% |
| D_ML_TRAIN | 训练 | 4 | 3 | 75.0% |
| D_DATA | 数据接入层 | 80 | 77 | 96.2% |
| D_GOV_AUDIT | 审计追踪 | 124 | 121 | 97.6% |
| D_GOV_DRIFT | 漂移检测 | 75 | 74 | 98.7% |
| D_INFRA_RUNTIME | 运行时集成 | 161 | 160 | 99.4% |
| D_GOV_CODE_QUALITY | 代码质量治理 | 169 | 168 | 99.4% |
| D_ALT_DATA | 另类数据 | 7 | 7 | 100.0% |
