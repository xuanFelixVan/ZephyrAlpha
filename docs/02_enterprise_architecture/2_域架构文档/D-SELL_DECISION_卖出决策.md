---
doc_type: domain_architecture_doc
title: D-SELL_DECISION 卖出决策架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-SELL_DECISION 卖出决策架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-SELL_DECISION |
| 域名称 | 卖出决策 |
| 架构层 | L2_domain |
| 模块总数 | 64 |
| 设计态模块 | 57 |
| 原型态模块 | 1 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 卖出决策域。负责卖出时机判断与卖出策略执行，包括止盈止损策略、持仓时间优化、卖出信号聚合。 |

## 模块清单

共 64 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-SELL-DECISION/Adjusted Stop Level 调整后止损位 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Average True Range ATR动态止损 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Breakout Failure Detector突破成败检测器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Breakout Result 突破成败结果 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Buy-Sell Conflict Arbitrator买卖冲突仲裁器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/D-SELL |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Day Trade Agent 做T Agent |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Exit Scenario Plan 卖出情景预案 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Exit Scenario Planner卖出情景预案器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Fused Sell Decision 融合卖出决策 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/LimitDownBlock 跌停板拦截事件 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Opportunity Cost Analyzer 机会成本分析器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Position Triage Result 持仓分级结果 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Position Triage持仓分级器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Replacement & Rebalance Sell置换与再平衡卖出 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Risk-Based Sell Trigger 风险驱动卖出触发器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Scaling Out Architect分批退出架构师 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Scaling Out Plan 分批退出计划 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Self-Reflection Agent 自反Agent |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell A/B Test Result 卖出A/B测试结果 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Audit Report 卖出审计报告 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Convergence Result 多策略卖出共振结果 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Decision Domain 卖出决策域 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Decision Must Pass Fusion Arbitration 卖出决策必须经过融合仲裁 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Execution Optimizer 卖出执行优化器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Execution Quality Tracker卖出执行质量追踪 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Execution Quality 卖出执行质量 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Signal Accuracy Monitor卖出信号准确率监控 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Signal Collector卖出信号收集器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Signal Fusion Engine卖出信号融合引擎 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Signal Score 卖出信号评分 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Signal Scorer卖出信号评分器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Signal 卖出信号 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Strategy A/B Tester卖出策略A/B测试 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Urgency Score 卖出紧迫度评分 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Sell Urgency Scorer卖出紧迫度评分器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/SellArbitrated 卖出仲裁完成事件 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/SellArbitration 卖出仲裁 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/SellDecided 卖出决策事件 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/SellDecision Contract SellDecision 卖出决策契约 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/SellExecuted 卖出执行完成事件 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/SellLoopFeedback 卖出闭环反馈事件 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/SellSignalFused Event SellSignalFused 卖出信号已融合 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Signal Reversal Detector 信号反转检测器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Stop Cost Estimate 止损成本估计 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Stop Loss Strategy Family止损策略族 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Stop Option Pricer止损期权定价器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Stop Paradigm Selection 止损范式选择 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Stop-Hunting Protector止损猎杀防护器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Stop-Loss Decision Engine 止损决策引擎 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/StopLossTriggerReversalDetector 猎杀止损保护器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Strategy-Specific Stop Framework策略类型→止损范式映射 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/T-Trade Coordinator做T决策协调器 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/T-Trade Instruction 做T指令 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/TTradeExecuted 做T执行完成事件 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Take Profit Strategy Family止盈策略族 |  | design_only | design | 0 | 0 |
| D-SELL-DECISION/Take-Profit Decision Engine 止盈决策引擎 |  | design_only | design | 0 | 0 |
| src/zephyr/sell_decision/__init__.py | MOD-SELL_DECISION | orphan | prototype | 0 | 0 |
| src/zephyr/sell_decision/_extensions/__init__.py | MOD-SELL_DECISION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/sell_decision/api/__init__.py | MOD-SELL_DECISION | orphan | scaffold_placeholder | 0 | 4 |
| src/zephyr/sell_decision/core/__init__.py | MOD-SELL_DECISION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/sell_decision/infrastructure/__init__.py | MOD-SELL_DECISION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/sell_decision/models/__init__.py | MOD-SELL_DECISION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/sell_decision/services/__init__.py | MOD-SELL_DECISION | orphan | scaffold_placeholder | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-RISK | 14 | domain_dependency,event,config_depends,data,contract |
| D-SECURITY | 9 | data,event,contract |
| D-GOVERNANCE | 7 | data,contract |
| D-DATA_ENG | 6 | event,contract,data |
| D-AUTONOMY_CORE | 6 | config_depends,contract,event,data |
| D-POSITION | 5 | domain_dependency,data,contract,event |
| D-INTEGRATION | 5 | data,event,contract |
| D-SIGNAL | 4 | contract,config_depends |
| D-REPORTING | 4 | config_depends,data,contract |
| D-EX_SOR | 4 | event,contract |
| D-PF_CORE | 3 | data,contract,event |
| D-ML_TRAIN | 3 | config_depends,data,event |
| D-KNOWLEDGE | 3 | event,config_depends,data |
| D-MKT_DATA | 2 | event,data |
| D-INTELLIGENCE | 2 | data,contract |
| D-FACTOR | 2 | contract,event |
| D-EX_CORE | 2 | event,data |
| D-AUTONOMY_PERM | 2 | data,config_depends |
| D-SHARED | 1 | contract |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-COMPLIANCE | 9 | config_depends,event,contract |
| D-INFRA_OPS | 6 | event,contract,data |
| D-FRONTEND | 5 | contract,data,config_depends |
| D-PF_ALLOC | 2 | event,contract |
| D-OPS | 1 | config_depends |
| D-DATA_GOV | 1 | event |

## 域内依赖图

详见 [d_sell_decision_dependency.mmd](d_sell_decision_dependency.mmd)
