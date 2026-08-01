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
| production（生产态） | 2864 | 92.5% |
| design（设计态） | 232 | 7.5% |
| scaffold_placeholder（脚手架） | 0 | 0.0% |
| **总计** | **3096** | **100%** |

## 构建状态统计（build_status）

| 构建状态 / Build Status | 模块数 / Modules | 占比 / Ratio |
|---------|:---:|:---:|
| generated | 4029 | 130.1% |
| stable | 1663 | 53.7% |
| planned | 145 | 4.7% |
| deprecated | 83 | 2.7% |

## 各域设计成熟度统计

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 设计态 / Design | 脚手架 / Scaffold | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|:---:|:---:|
| D_ALT_DATA | 另类数据 | 8 | 7 | 1 | 0 | 87.5% |
| D_ARCHIVE_SCRIPTS | Archived Scripts | 0 | 0 | 0 | 0 | N/A |
| D_ARCH_GUARD | 架构守护脚本 | 0 | 0 | 0 | 0 | N/A |
| D_ARCH_SCRIPTS | 架构治理脚本 | 0 | 0 | 0 | 0 | N/A |
| D_ASHARE_SIGNAL | A股特色信号 | 17 | 7 | 10 | 0 | 41.2% |
| D_AUDITTEST | 审计测试套件 | 1 | 1 | 0 | 0 | 100.0% |
| D_AUTONOMY_CORE | 自治核心 | 130 | 130 | 0 | 0 | 100.0% |
| D_AUTONOMY_PERM | 自治保护 | 2 | 2 | 0 | 0 | 100.0% |
| D_BACKTEST | 回测 | 27 | 18 | 9 | 0 | 66.7% |
| D_BEHAVIORAL_AUDIT | 行为审计 | 0 | 0 | 0 | 0 | N/A |
| D_CODE_SCRIPTS | 代码质量脚本 | 0 | 0 | 0 | 0 | N/A |
| D_COMPLIANCE | 合规 | 3 | 2 | 1 | 0 | 66.7% |
| D_COMPLIANCE_SCRIPTS | 合规治理脚本 | 0 | 0 | 0 | 0 | N/A |
| D_CONTRACTS | 共享契约 | 0 | 0 | 0 | 0 | N/A |
| D_CROSS_ASSET | 跨资产 | 7 | 7 | 0 | 0 | 100.0% |
| D_DATA | 数据接入层 | 179 | 162 | 17 | 0 | 90.5% |
| D_DATA_ENG | 数据工程 | 20 | 7 | 13 | 0 | 35.0% |
| D_DATA_GOV | 数据治理 | 10 | 10 | 0 | 0 | 100.0% |
| D_DATA_SCRIPTS | 数据治理脚本 | 0 | 0 | 0 | 0 | N/A |
| D_DATA_SEC | 数据安全与契约 | 7 | 7 | 0 | 0 | 100.0% |
| D_DIGITAL_TWIN | 数字孪生 | 7 | 7 | 0 | 0 | 100.0% |
| D_EXEC_SIM | 执行仿真 | 7 | 7 | 0 | 0 | 100.0% |
| D_EX_CORE | 执行核心 | 25 | 8 | 17 | 0 | 32.0% |
| D_EX_SOR | 执行路由 | 17 | 7 | 10 | 0 | 41.2% |
| D_FACTOR | 因子 | 86 | 37 | 49 | 0 | 43.0% |
| D_FBL_DETECTORS | 反馈检测器 | 65 | 65 | 0 | 0 | 100.0% |
| D_FBL_DIAGNOSERS | 反馈诊断器 | 76 | 76 | 0 | 0 | 100.0% |
| D_FBL_VERIFICATION | 反馈验证 | 71 | 71 | 0 | 0 | 100.0% |
| D_FEEDBACK_LOOP | 反馈循环引擎 | 125 | 125 | 0 | 0 | 100.0% |
| D_FRONTEND | 前端 | 16 | 12 | 4 | 0 | 75.0% |
| D_FUNDAMENTAL_SIGNAL | 基本面信号 | 13 | 10 | 3 | 0 | 76.9% |
| D_GOVERNANCE | 生命周期管理 | 222 | 222 | 0 | 0 | 100.0% |
| D_GOV_AUDIT | 审计追踪 | 124 | 121 | 3 | 0 | 97.6% |
| D_GOV_CODE_QUALITY | 代码质量治理 | 169 | 169 | 0 | 0 | 100.0% |
| D_GOV_DOCS | 架构文档治理 | 26 | 2 | 24 | 0 | 7.7% |
| D_GOV_DRIFT | 漂移检测 | 75 | 74 | 1 | 0 | 98.7% |
| D_GOV_ENFORCEMENT | 规则执行 | 42 | 41 | 1 | 0 | 97.6% |
| D_GOV_OPS_RESILIENCE | 运维弹性治理 | 91 | 91 | 0 | 0 | 100.0% |
| D_GOV_REPAIR | 治理修复 | 1 | 1 | 0 | 0 | 100.0% |
| D_GOV_RULE | 规则治理 | 35 | 35 | 0 | 0 | 100.0% |
| D_GOV_SCRIPTS | 脚本治理 | 385 | 384 | 1 | 0 | 99.7% |
| D_INFRASTRUCTURE | 跨层契约基础设施 | 25 | 25 | 0 | 0 | 100.0% |
| D_INFRA_A2A | A2A通信 | 72 | 72 | 0 | 0 | 100.0% |
| D_INFRA_OPS | 基础设施运维 | 0 | 0 | 0 | 0 | N/A |
| D_INFRA_RECOVERY | 回滚恢复 | 55 | 55 | 0 | 0 | 100.0% |
| D_INFRA_RUNTIME | 运行时集成 | 161 | 160 | 1 | 0 | 99.4% |
| D_INFRA_TELEMETRY | 可观测性 | 0 | 0 | 0 | 0 | N/A |
| D_INTEGRATION | 管线路由 | 71 | 71 | 0 | 0 | 100.0% |
| D_INTEGRATION_GATEWAY | 集成网关 | 0 | 0 | 0 | 0 | N/A |
| D_INTELLIGENCE | 上下文管理 | 31 | 31 | 0 | 0 | 100.0% |
| D_KNOWLEDGE | 知识管理 | 1 | 0 | 1 | 0 | 0.0% |
| D_META_SCRIPTS | 元治理脚本 | 0 | 0 | 0 | 0 | N/A |
| D_MKT_DATA | 行情数据 | 15 | 9 | 6 | 0 | 60.0% |
| D_ML_SERVE | 推理 | 7 | 7 | 0 | 0 | 100.0% |
| D_ML_TRAIN | 训练 | 6 | 3 | 3 | 0 | 50.0% |
| D_OPS | 反馈循环 | 11 | 11 | 0 | 0 | 100.0% |
| D_ORCHESTRATOR | 代理编排器 | 70 | 70 | 0 | 0 | 100.0% |
| D_PF_ALLOC | 组合分配 | 5 | 2 | 3 | 0 | 40.0% |
| D_PF_CORE | 组合核心 | 16 | 10 | 6 | 0 | 62.5% |
| D_POSITION | 仓位管理 | 11 | 1 | 10 | 0 | 9.1% |
| D_REPORTING | 报告 | 12 | 3 | 9 | 0 | 25.0% |
| D_RISK | 风控 | 15 | 11 | 4 | 0 | 73.3% |
| D_SECURITY | 对抗验证 | 166 | 166 | 0 | 0 | 100.0% |
| D_SECURITY_LLM | LLM防御 | 0 | 0 | 0 | 0 | N/A |
| D_SEC_SCRIPTS | 安全治理脚本 | 0 | 0 | 0 | 0 | N/A |
| D_SELL_DECISION | 卖出决策 | 21 | 7 | 14 | 0 | 33.3% |
| D_SHARED | 共享服务 | 184 | 184 | 0 | 0 | 100.0% |
| D_SIGLEGACY | 信号遗留设计态 | 0 | 0 | 0 | 0 | N/A |
| D_SIGQC | 信号质量控制 | 2 | 2 | 0 | 0 | 100.0% |
| D_SIMULATION | 仿真 | 10 | 2 | 8 | 0 | 20.0% |
| D_STRUCT_SCRIPTS | 结构治理脚本 | 0 | 0 | 0 | 0 | N/A |
| D_TRADING | 交易运营 | 40 | 37 | 3 | 0 | 92.5% |

## 生产化率最低的域（Top 10，需优先推进）

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|
| D_KNOWLEDGE | 知识管理 | 1 | 0 | 0.0% |
| D_GOV_DOCS | 架构文档治理 | 26 | 2 | 7.7% |
| D_POSITION | 仓位管理 | 11 | 1 | 9.1% |
| D_SIMULATION | 仿真 | 10 | 2 | 20.0% |
| D_REPORTING | 报告 | 12 | 3 | 25.0% |
| D_EX_CORE | 执行核心 | 25 | 8 | 32.0% |
| D_SELL_DECISION | 卖出决策 | 21 | 7 | 33.3% |
| D_DATA_ENG | 数据工程 | 20 | 7 | 35.0% |
| D_PF_ALLOC | 组合分配 | 5 | 2 | 40.0% |
| D_ASHARE_SIGNAL | A股特色信号 | 17 | 7 | 41.2% |
