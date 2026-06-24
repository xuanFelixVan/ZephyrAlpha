---
doc_type: design_vs_production_report
title: 设计态vs运营态统计报告
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 设计态vs运营态统计报告

> **文档作用 / Purpose**: 展示各域设计态模块与运营态模块的数量对比和迁移进度，跟踪从设计到落地的完成率。

> 本文档由 generate_design_vs_production.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 21:39:35
> 数据源: depgraph.db nodes表

## 全局统计

| 设计成熟度 / Maturity | 模块数 / Modules | 占比 / Ratio |
|-----------|:---:|:---:|
| production（生产态） | 1232 | 8.6% |
| design（设计态） | 8028 | 55.8% |
| prototype（原型态） | 4917 | 34.2% |
| scaffold_placeholder（脚手架） | 220 | 1.5% |
| **总计** | **14397** | **100%** |

## 构建状态统计（build_status）

| 构建状态 / Build Status | 模块数 / Modules | 占比 / Ratio |
|---------|:---:|:---:|
| design_only | 7991 | 55.5% |
| draft | 5493 | 38.2% |
| orphan | 711 | 4.9% |
| production | 142 | 1.0% |
| stable | 28 | 0.2% |
| unbuilt | 27 | 0.2% |
| path_invalid | 2 | 0.0% |
| active | 2 | 0.0% |
| testing | 1 | 0.0% |

## 各域设计成熟度统计

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 设计态 / Design | 原型态 / Prototype | 脚手架 / Scaffold | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | 68 | 0 | 61 | 1 | 6 | 0.0% |
| D-AUTONOMY_CORE | 自治核心 | 650 | 1 | 475 | 168 | 6 | 0.2% |
| D-AUTONOMY_PERM | 自治保护 | 270 | 4 | 197 | 63 | 6 | 1.5% |
| D-BACKTEST | 回测 | 9 | 0 | 2 | 1 | 6 | 0.0% |
| D-BEHAVIORAL_AUDIT | 行为审计 | 60 | 60 | 0 | 0 | 0 | 100.0% |
| D-COMPLIANCE | 合规 | 916 | 0 | 891 | 19 | 6 | 0.0% |
| D-CROSS_ASSET | 跨资产 | 79 | 1 | 66 | 6 | 6 | 1.3% |
| D-DATA_ENG | 数据工程 | 147 | 0 | 140 | 1 | 6 | 0.0% |
| D-DATA_GOV | 数据治理 | 38 | 0 | 38 | 0 | 0 | 0.0% |
| D-DATA_SEC | 数据安全与契约 | 30 | 0 | 20 | 4 | 6 | 0.0% |
| D-DIGITAL_TWIN | 数字孪生 | 13 | 0 | 6 | 1 | 6 | 0.0% |
| D-EXEC_SIM | 执行仿真 | 8 | 0 | 1 | 1 | 6 | 0.0% |
| D-EX_CORE | 执行核心 | 135 | 3 | 120 | 6 | 6 | 2.2% |
| D-EX_SOR | 执行路由 | 131 | 0 | 124 | 1 | 6 | 0.0% |
| D-FACTOR | 因子 | 320 | 2 | 302 | 10 | 6 | 0.6% |
| D-FRONTEND | 前端 | 237 | 7 | 213 | 11 | 6 | 3.0% |
| D-GOVERNANCE | 生命周期管理 | 3908 | 132 | 591 | 3174 | 11 | 3.4% |
| D-GOV_AUDIT | 审计追踪 | 268 | 69 | 6 | 193 | 0 | 25.7% |
| D-GOV_DRIFT | 漂移检测 | 38 | 22 | 1 | 15 | 0 | 57.9% |
| D-GOV_RULE | 规则治理 | 178 | 177 | 0 | 1 | 0 | 99.4% |
| D-INFRA_OPS | 基础设施运维 | 418 | 3 | 389 | 20 | 6 | 0.7% |
| D-INFRA_RUNTIME | 运行时集成 | 727 | 410 | 311 | 0 | 6 | 56.4% |
| D-INTEGRATION | 管线路由 | 706 | 63 | 416 | 222 | 5 | 8.9% |
| D-INTELLIGENCE | 上下文管理 | 273 | 18 | 217 | 32 | 6 | 6.6% |
| D-KNOWLEDGE | 知识管理 | 194 | 1 | 155 | 32 | 6 | 0.5% |
| D-MKT_DATA | 行情数据 | 266 | 1 | 257 | 2 | 6 | 0.4% |
| D-ML_SERVE | 推理 | 69 | 0 | 62 | 1 | 6 | 0.0% |
| D-ML_TRAIN | 训练 | 119 | 0 | 108 | 5 | 6 | 0.0% |
| D-OPS | 反馈循环 | 697 | 5 | 264 | 422 | 6 | 0.7% |
| D-PF_ALLOC | 组合分配 | 114 | 0 | 104 | 4 | 6 | 0.0% |
| D-PF_CORE | 组合核心 | 202 | 6 | 183 | 7 | 6 | 3.0% |
| D-POSITION | 仓位管理 | 77 | 0 | 69 | 2 | 6 | 0.0% |
| D-REPORTING | 报告 | 132 | 0 | 118 | 8 | 6 | 0.0% |
| D-RISK | 风控 | 775 | 9 | 749 | 11 | 6 | 1.2% |
| D-SECURITY | 对抗验证 | 849 | 134 | 603 | 106 | 6 | 15.8% |
| D-SELL_DECISION | 卖出决策 | 64 | 0 | 57 | 1 | 6 | 0.0% |
| D-SHARED | 共享服务 | 290 | 79 | 7 | 204 | 0 | 27.2% |
| D-SIGNAL | 信号 | 476 | 1 | 474 | 1 | 0 | 0.2% |
| D-SIGNAL_ASHARE | A股特色信号 | 27 | 0 | 20 | 1 | 6 | 0.0% |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | 24 | 3 | 1 | 14 | 6 | 12.5% |
| D-SIGNAL_QUALITY | 信号质量 | 18 | 0 | 11 | 1 | 6 | 0.0% |
| D-SIMULATION | 仿真 | 128 | 4 | 110 | 8 | 6 | 3.1% |
| D-T3-W0 | 测试域T3-0 | 0 | 0 | 0 | 0 | 0 | N/A |
| D-T3-W1 | 测试域T3-1 | 0 | 0 | 0 | 0 | 0 | N/A |
| D-T3-W2 | 测试域T3-2 | 0 | 0 | 0 | 0 | 0 | N/A |
| D-T3-W3 | 测试域T3-3 | 0 | 0 | 0 | 0 | 0 | N/A |
| D-T4-SAME | 相同域T4 | 0 | 0 | 0 | 0 | 0 | N/A |
| D-T5-W0 | 读写并发T5-0 | 0 | 0 | 0 | 0 | 0 | N/A |
| D-T5-W1 | 读写并发T5-1 | 0 | 0 | 0 | 0 | 0 | N/A |
| D-T5-W2 | 读写并发T5-2 | 0 | 0 | 0 | 0 | 0 | N/A |
| D-T5-W3 | 读写并发T5-3 | 0 | 0 | 0 | 0 | 0 | N/A |
| D-T9-PREREQ | T9前置域 | 0 | 0 | 0 | 0 | 0 | N/A |
| D-TRADING | 交易运营 | 249 | 17 | 89 | 137 | 6 | 6.8% |

## 生产化率最低的域（Top 10，需优先推进）

| 域ID / Domain ID | 域名称 / Domain Name | 总模块数 / Total | 生产态 / Production | 生产化率 / Production Rate |
|------|--------|:---:|:---:|:---:|
| D-ALT_DATA | 另类数据 | 68 | 0 | 0.0% |
| D-BACKTEST | 回测 | 9 | 0 | 0.0% |
| D-COMPLIANCE | 合规 | 916 | 0 | 0.0% |
| D-DATA_ENG | 数据工程 | 147 | 0 | 0.0% |
| D-DATA_GOV | 数据治理 | 38 | 0 | 0.0% |
| D-DATA_SEC | 数据安全与契约 | 30 | 0 | 0.0% |
| D-DIGITAL_TWIN | 数字孪生 | 13 | 0 | 0.0% |
| D-EXEC_SIM | 执行仿真 | 8 | 0 | 0.0% |
| D-EX_SOR | 执行路由 | 131 | 0 | 0.0% |
| D-ML_SERVE | 推理 | 69 | 0 | 0.0% |
