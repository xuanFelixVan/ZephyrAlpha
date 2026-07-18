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
| production（生产态） | 1566 | 58.5% |
| design（设计态） | 62 | 2.3% |
| prototype（原型态） | 1051 | 39.2% |
| scaffold_placeholder（脚手架） | 0 | 0.0% |
| **总计** | **2679** | **100%** |

## 构建状态统计（build_status）

| 构建状态 / Build Status | 模块数 / Modules | 占比 / Ratio |
|---------|:---:|:---:|
| generated | 3794 | 141.6% |
| stable | 1609 | 60.1% |
| planned | 38 | 1.4% |
| deprecated | 2 | 0.1% |

## 各域设计成熟度统计

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 脚手架 / Scaffold | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_ASHARE_SIGNAL | A股特色信号 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_AUDITTEST | 审计测试套件 | 1 | 1 | 0 | 0 | 0 | 100.0% |
| D_AUTONOMY_CORE | 自治核心 | 137 | 132 | 0 | 5 | 0 | 96.4% |
| D_AUTONOMY_PERM | 自治保护 | 2 | 0 | 0 | 2 | 0 | 0.0% |
| D_BACKTEST | 回测 | 25 | 9 | 8 | 8 | 0 | 36.0% |
| D_BEHAVIORAL_AUDIT | 行为审计 | 0 | 0 | 0 | 0 | 0 | N/A |
| D_COMPLIANCE | 合规 | 4 | 0 | 0 | 4 | 0 | 0.0% |
| D_CROSS_ASSET | 跨资产 | 8 | 0 | 1 | 7 | 0 | 0.0% |
| D_DATA | 数据接入层 | 42 | 9 | 0 | 33 | 0 | 21.4% |
| D_DATA_ENG | 数据工程 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DATA_GOV | 数据治理 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DATA_SEC | 数据安全与契约 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_DIGITAL_TWIN | 数字孪生 | 8 | 0 | 1 | 7 | 0 | 0.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_EX_CORE | 执行核心 | 8 | 4 | 1 | 3 | 0 | 50.0% |
| D_EX_SOR | 执行路由 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_FACTOR | 因子 | 5 | 2 | 0 | 3 | 0 | 40.0% |
| D_FBL_DETECTORS | 反馈检测器 | 65 | 59 | 0 | 6 | 0 | 90.8% |
| D_FBL_DIAGNOSERS | 反馈诊断器 | 76 | 71 | 0 | 5 | 0 | 93.4% |
| D_FBL_VERIFICATION | 反馈验证 | 71 | 67 | 0 | 4 | 0 | 94.4% |
| D_FEEDBACK_LOOP | 反馈循环引擎 | 124 | 112 | 0 | 12 | 0 | 90.3% |
| D_FRONTEND | 前端 | 18 | 9 | 6 | 3 | 0 | 50.0% |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | 10 | 4 | 0 | 6 | 0 | 40.0% |
| D_GOVERNANCE | 生命周期管理 | 213 | 96 | 1 | 116 | 0 | 45.1% |
| D_GOV_AUDIT | 审计追踪 | 102 | 67 | 2 | 33 | 0 | 65.7% |
| D_GOV_CODE_QUALITY | 代码质量治理 | 132 | 113 | 0 | 19 | 0 | 85.6% |
| D_GOV_DOCS | 架构文档治理 | 28 | 0 | 28 | 0 | 0 | 0.0% |
| D_GOV_DRIFT | 漂移检测 | 74 | 70 | 1 | 3 | 0 | 94.6% |
| D_GOV_ENFORCEMENT | 规则执行 | 32 | 15 | 0 | 17 | 0 | 46.9% |
| D_GOV_KB | 知识库治理 | 26 | 16 | 0 | 10 | 0 | 61.5% |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 | 90 | 81 | 0 | 9 | 0 | 90.0% |
| D_GOV_REPAIR | 治理修复 | 1 | 1 | 0 | 0 | 0 | 100.0% |
| D_GOV_RULE | 规则治理 | 35 | 31 | 0 | 4 | 0 | 88.6% |
| D_GOV_SCRIPTS | 脚本治理 | 358 | 10 | 2 | 346 | 0 | 2.8% |
| D_INFRASTRUCTURE | 跨层契约基础设施 | 26 | 12 | 0 | 14 | 0 | 46.2% |
| D_INFRA_A2A | A2A通信 | 72 | 28 | 0 | 44 | 0 | 38.9% |
| D_INFRA_OPS | 基础设施运维 | 2 | 0 | 2 | 0 | 0 | 0.0% |
| D_INFRA_RECOVERY | 回滚恢复 | 54 | 48 | 0 | 6 | 0 | 88.9% |
| D_INFRA_RUNTIME | 运行时集成 | 159 | 118 | 1 | 40 | 0 | 74.2% |
| D_INFRA_TELEMETRY | 可观测性 | 0 | 0 | 0 | 0 | 0 | N/A |
| D_INTEGRATION | 管线路由 | 73 | 45 | 0 | 28 | 0 | 61.6% |
| D_INTEGRATION_GATEWAY | 集成网关 | 0 | 0 | 0 | 0 | 0 | N/A |
| D_INTELLIGENCE | 上下文管理 | 31 | 21 | 0 | 10 | 0 | 67.7% |
| D_KNOWLEDGE | 知识管理 | 4 | 0 | 2 | 2 | 0 | 0.0% |
| D_MKT_DATA | 行情数据 | 10 | 0 | 3 | 7 | 0 | 0.0% |
| D_ML_SERVE | 推理 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_ML_TRAIN | 训练 | 4 | 0 | 1 | 3 | 0 | 0.0% |
| D_OPS | 反馈循环 | 9 | 8 | 0 | 1 | 0 | 88.9% |
| D_ORCHESTRATOR | 代理编排器 | 72 | 58 | 0 | 14 | 0 | 80.6% |
| D_PF_ALLOC | 组合分配 | 3 | 1 | 1 | 1 | 0 | 33.3% |
| D_PF_CORE | 组合核心 | 1 | 0 | 0 | 1 | 0 | 0.0% |
| D_POSITION | 仓位管理 | 1 | 1 | 0 | 0 | 0 | 100.0% |
| D_REPORTING | 报告 | 3 | 1 | 0 | 2 | 0 | 33.3% |
| D_RISK | 风控 | 11 | 9 | 0 | 2 | 0 | 81.8% |
| D_SECURITY | 对抗验证 | 165 | 99 | 0 | 66 | 0 | 60.0% |
| D_SECURITY_LLM | LLM防御 | 0 | 0 | 0 | 0 | 0 | N/A |
| D_SELL_DECISION | 卖出决策 | 7 | 0 | 0 | 7 | 0 | 0.0% |
| D_SHARED | 共享服务 | 184 | 115 | 0 | 69 | 0 | 62.5% |
| D_SIGLEGACY | 信号遗留设计态 | 0 | 0 | 0 | 0 | 0 | N/A |
| D_SIGQC | 信号质量控制 | 2 | 0 | 0 | 2 | 0 | 0.0% |
| D_SIMULATION | 仿真 | 3 | 2 | 1 | 0 | 0 | 66.7% |
| D_TRADING | 交易运营 | 32 | 21 | 0 | 11 | 0 | 65.6% |

## 生产化率最低的域（Top 10，需优先推进）

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 7 | 0 | 0.0% |
| D_ASHARE_SIGNAL | A股特色信号 | 7 | 0 | 0.0% |
| D_AUTONOMY_PERM | 自治保护 | 2 | 0 | 0.0% |
| D_COMPLIANCE | 合规 | 4 | 0 | 0.0% |
| D_CROSS_ASSET | 跨资产 | 8 | 0 | 0.0% |
| D_DATA_ENG | 数据工程 | 7 | 0 | 0.0% |
| D_DATA_GOV | 数据治理 | 7 | 0 | 0.0% |
| D_DATA_SEC | 数据安全与契约 | 7 | 0 | 0.0% |
| D_DIGITAL_TWIN | 数字孪生 | 8 | 0 | 0.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 0 | 0.0% |
