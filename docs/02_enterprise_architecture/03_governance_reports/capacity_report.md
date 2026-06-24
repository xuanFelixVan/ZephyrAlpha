---
doc_type: capacity_report
title: 域容量报告
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 域容量报告

> **文档作用 / Purpose**: 展示各功能域的模块数量与容量上限对比，识别超容域和接近超容域，为域拆分决策提供依据。

> 本文档由 generate_capacity_report.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 23:01:39
> 数据源: depgraph.db domains表 + nodes表

## 统计概览

| 指标 / Metric | 值 / Value |
|------|-----|
| 域总数 | 58 |
| 超容域 | 20 |
| 接近超容域（>80%） | 6 |
| 空域（0模块） | 15 |

## 超容域清单（需拆分）

| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 超出 / Over |
|------|--------|:---:|:---:|:---:|
| D-AUTONOMY_CORE | 自治核心 | 650 | 150 | +500 |
| D-AUTONOMY_PERM | 自治保护 | 270 | 150 | +120 |
| D-COMPLIANCE | 合规 | 916 | 150 | +766 |
| D-FACTOR | 因子 | 318 | 150 | +168 |
| D-FRONTEND | 前端 | 236 | 150 | +86 |
| D-GOVERNANCE | 生命周期管理 | 3860 | 200 | +3660 |
| D-GOV_AUDIT | 审计追踪 | 217 | 200 | +17 |
| D-INFRA_OPS | 基础设施运维 | 418 | 150 | +268 |
| D-INFRA_RUNTIME | 运行时集成 | 727 | 150 | +577 |
| D-INTEGRATION | 管线路由 | 705 | 150 | +555 |
| D-INTELLIGENCE | 上下文管理 | 273 | 150 | +123 |
| D-KNOWLEDGE | 知识管理 | 194 | 150 | +44 |
| D-MKT_DATA | 行情数据 | 266 | 150 | +116 |
| D-OPS | 反馈循环 | 679 | 150 | +529 |
| D-PF_CORE | 组合核心 | 201 | 150 | +51 |
| D-RISK | 风控 | 774 | 150 | +624 |
| D-SECURITY | 对抗验证 | 849 | 200 | +649 |
| D-SHARED | 共享服务 | 289 | 150 | +139 |
| D-SIGNAL | 信号 | 476 | 150 | +326 |
| D-TRADING | 交易运营 | 249 | 150 | +99 |

## 接近超容域清单（>80%，需关注）

| 域ID / Domain ID | 域名称 / Domain Name | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage |
|------|--------|:---:|:---:|:---:|
| D-DATA_ENG | 数据工程 | 147 | 150 | 98.0% |
| D-EX_CORE | 执行核心 | 134 | 150 | 89.3% |
| D-EX_SOR | 执行路由 | 131 | 150 | 87.3% |
| D-GOV_RULE | 规则治理 | 178 | 200 | 89.0% |
| D-REPORTING | 报告 | 132 | 150 | 88.0% |
| D-SIMULATION | 仿真 | 128 | 150 | 85.3% |

## 空域清单（0模块，待开发）

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 上限 / Max |
|------|--------|--------|:---:|
| D-GOV-ENFORCEMENT | rule_enforcement |  | 200 |
| D-GOV-REPAIR | rollback |  | 200 |
| D-GOV-SCRIPTS | code_dedup |  | 200 |
| D-INTEGRATION-GATEWAY | mcp_servers |  | 200 |
| D-SECURITY-LLM | llm_defense |  | 200 |
| D-T3-W0 | 测试域T3-0 | L2_domain | 50 |
| D-T3-W1 | 测试域T3-1 | L2_domain | 50 |
| D-T3-W2 | 测试域T3-2 | L2_domain | 50 |
| D-T3-W3 | 测试域T3-3 | L2_domain | 50 |
| D-T4-SAME | 相同域T4 | L2_domain | 50 |
| D-T5-W0 | 读写并发T5-0 | L2_domain | 200 |
| D-T5-W1 | 读写并发T5-1 | L2_domain | 200 |
| D-T5-W2 | 读写并发T5-2 | L2_domain | 200 |
| D-T5-W3 | 读写并发T5-3 | L2_domain | 200 |
| D-T9-PREREQ | T9前置域 | L2_domain | 200 |

## 完整域容量清单

| 域ID / Domain ID | 域名称 / Domain Name | 架构层 / Layer | 实际模块数 / Actual Modules | 上限 / Max | 使用率 / Usage | 状态 / Status |
|------|--------|--------|:---:|:---:|:---:|------|
| D-ALT_DATA | 另类数据 | L1_foundation | 68 | 150 | 45.3% | 正常 |
| D-AUTONOMY_CORE | 自治核心 | L1_platform | 650 | 150 | 433.3% | 超容 |
| D-AUTONOMY_PERM | 自治保护 | L2_domain | 270 | 150 | 180.0% | 超容 |
| D-BACKTEST | 回测 | L2_domain | 9 | 150 | 6.0% | 正常 |
| D-BEHAVIORAL_AUDIT | 行为审计 | L1_foundation | 60 | 150 | 40.0% | 正常 |
| D-COMPLIANCE | 合规 | L2_domain | 916 | 150 | 610.7% | 超容 |
| D-CROSS_ASSET | 跨资产 | L2_domain | 76 | 150 | 50.7% | 正常 |
| D-DATA_ENG | 数据工程 | L1_foundation | 147 | 150 | 98.0% | 接近超容 |
| D-DATA_GOV | 数据治理 | L1_foundation | 38 | 150 | 25.3% | 正常 |
| D-DATA_SEC | 数据安全与契约 | L1_foundation | 30 | 150 | 20.0% | 正常 |
| D-DIGITAL_TWIN | 数字孪生 | L2_domain | 13 | 150 | 8.7% | 正常 |
| D-EXEC_SIM | 执行仿真 | L2_domain | 8 | 150 | 5.3% | 正常 |
| D-EX_CORE | 执行核心 | L2_domain | 134 | 150 | 89.3% | 接近超容 |
| D-EX_SOR | 执行路由 | L2_domain | 131 | 150 | 87.3% | 接近超容 |
| D-FACTOR | 因子 | L2_domain | 318 | 150 | 212.0% | 超容 |
| D-FRONTEND | 前端 | L1_platform | 236 | 150 | 157.3% | 超容 |
| D-GOV-ENFORCEMENT | rule_enforcement |  | 0 | 200 | 0.0% | 空 |
| D-GOV-REPAIR | rollback |  | 0 | 200 | 0.0% | 空 |
| D-GOV-SCRIPTS | code_dedup |  | 0 | 200 | 0.0% | 空 |
| D-GOVERNANCE | 生命周期管理 | L2_domain | 3860 | 200 | 1930.0% | 超容 |
| D-GOV_AUDIT | 审计追踪 | L2_domain | 217 | 200 | 108.5% | 超容 |
| D-GOV_DRIFT | 漂移检测 | L2_domain | 38 | 200 | 19.0% | 正常 |
| D-GOV_RULE | 规则治理 | L2_domain | 178 | 200 | 89.0% | 接近超容 |
| D-INFRA_OPS | 基础设施运维 | L0_infrastructure | 418 | 150 | 278.7% | 超容 |
| D-INFRA_RUNTIME | 运行时集成 | L0_infrastructure | 727 | 150 | 484.7% | 超容 |
| D-INTEGRATION | 管线路由 | L1_platform | 705 | 150 | 470.0% | 超容 |
| D-INTEGRATION-GATEWAY | mcp_servers |  | 0 | 200 | 0.0% | 空 |
| D-INTELLIGENCE | 上下文管理 | L2_domain | 273 | 150 | 182.0% | 超容 |
| D-KNOWLEDGE | 知识管理 | L2_domain | 194 | 150 | 129.3% | 超容 |
| D-MKT_DATA | 行情数据 | L1_foundation | 266 | 150 | 177.3% | 超容 |
| D-ML_SERVE | 推理 | L2_domain | 69 | 150 | 46.0% | 正常 |
| D-ML_TRAIN | 训练 | L2_domain | 119 | 150 | 79.3% | 正常 |
| D-OPS | 反馈循环 | L1_platform | 679 | 150 | 452.7% | 超容 |
| D-PF_ALLOC | 组合分配 | L2_domain | 114 | 150 | 76.0% | 正常 |
| D-PF_CORE | 组合核心 | L2_domain | 201 | 150 | 134.0% | 超容 |
| D-POSITION | 仓位管理 | L2_domain | 77 | 150 | 51.3% | 正常 |
| D-REPORTING | 报告 | L1_platform | 132 | 150 | 88.0% | 接近超容 |
| D-RISK | 风控 | L2_domain | 774 | 150 | 516.0% | 超容 |
| D-SECURITY | 对抗验证 | L1_platform | 849 | 200 | 424.5% | 超容 |
| D-SECURITY-LLM | llm_defense |  | 0 | 200 | 0.0% | 空 |
| D-SELL_DECISION | 卖出决策 | L2_domain | 64 | 150 | 42.7% | 正常 |
| D-SHARED | 共享服务 | L1_platform | 289 | 150 | 192.7% | 超容 |
| D-SIGNAL | 信号 | L2_domain | 476 | 150 | 317.3% | 超容 |
| D-SIGNAL_ASHARE | A股特色信号 | L2_domain | 27 | 150 | 18.0% | 正常 |
| D-SIGNAL_FUNDAMENTAL | 基本面信号 | L2_domain | 24 | 150 | 16.0% | 正常 |
| D-SIGNAL_QUALITY | 信号质量 | L2_domain | 18 | 150 | 12.0% | 正常 |
| D-SIMULATION | 仿真 | L2_domain | 128 | 150 | 85.3% | 接近超容 |
| D-T3-W0 | 测试域T3-0 | L2_domain | 0 | 50 | 0.0% | 空 |
| D-T3-W1 | 测试域T3-1 | L2_domain | 0 | 50 | 0.0% | 空 |
| D-T3-W2 | 测试域T3-2 | L2_domain | 0 | 50 | 0.0% | 空 |
| D-T3-W3 | 测试域T3-3 | L2_domain | 0 | 50 | 0.0% | 空 |
| D-T4-SAME | 相同域T4 | L2_domain | 0 | 50 | 0.0% | 空 |
| D-T5-W0 | 读写并发T5-0 | L2_domain | 0 | 200 | 0.0% | 空 |
| D-T5-W1 | 读写并发T5-1 | L2_domain | 0 | 200 | 0.0% | 空 |
| D-T5-W2 | 读写并发T5-2 | L2_domain | 0 | 200 | 0.0% | 空 |
| D-T5-W3 | 读写并发T5-3 | L2_domain | 0 | 200 | 0.0% | 空 |
| D-T9-PREREQ | T9前置域 | L2_domain | 0 | 200 | 0.0% | 空 |
| D-TRADING | 交易运营 | L2_domain | 249 | 150 | 166.0% | 超容 |
