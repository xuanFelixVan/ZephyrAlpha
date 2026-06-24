---
doc_type: domain_architecture_diagram
title: D-SELL_DECISION 卖出决策架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 37_d_sell_decision / 卖出决策 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示卖出决策（D-SELL_DECISION）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 卖出决策（D-SELL_DECISION）的模块分布。共 64 个模块 / 64 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (7 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/sell_decision/__init__.py  [prototype]              │
│   src/zephyr/sell_decision/_extensions/__init__.py  [scaffold... │
│   src/zephyr/sell_decision/api/__init__.py  [scaffold_placeho... │
│   src/zephyr/sell_decision/core/__init__.py  [scaffold_placeh... │
│   src/zephyr/sell_decision/infrastructure/__init__.py  [scaff... │
│   src/zephyr/sell_decision/models/__init__.py  [scaffold_plac... │
│   src/zephyr/sell_decision/services/__init__.py  [scaffold_pl... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (57 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   Adjusted Stop Level 调整后止损位  [design]                     │
│   Average True Range ATR动态止损  [design]                       │
│   Breakout Failure Detector突破成败检测器  [design]              │
│   Breakout Result 突破成败结果  [design]                         │
│   Buy-Sell Conflict Arbitrator买卖冲突仲裁器  [design]           │
│   D-SELL  [design]                                               │
│   Day Trade Agent 做T Agent  [design]                            │
│   Exit Scenario Plan 卖出情景预案  [design]                      │
│   Exit Scenario Planner卖出情景预案器  [design]                  │
│   Fused Sell Decision 融合卖出决策  [design]                     │
│   LimitDownBlock 跌停板拦截事件  [design]                        │
│   Opportunity Cost Analyzer 机会成本分析器  [design]             │
│   Position Triage Result 持仓分级结果  [design]                  │
│   Position Triage持仓分级器  [design]                            │
│   Replacement & Rebalance Sell置换与再平衡卖出  [design]         │
│   Risk-Based Sell Trigger 风险驱动卖出触发器  [design]           │
│   Scaling Out Architect分批退出架构师  [design]                  │
│   Scaling Out Plan 分批退出计划  [design]                        │
│   ...还有 39 个模块 / 39 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 64 个模块 / 64 modules）。

### L2 领域层 / Domain Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/sell_decision/__init__.py | src/zephyr/sell_decision/__init__.py | prototype | orphan |
| 2 | src/zephyr/sell_decision/_extensions/__init__.py | src/zephyr/sell_decision/_extensions/... | scaffold_placeholder | orphan |
| 3 | src/zephyr/sell_decision/api/__init__.py | src/zephyr/sell_decision/api/__init__.py | scaffold_placeholder | orphan |
| 4 | src/zephyr/sell_decision/core/__init__.py | src/zephyr/sell_decision/core/__init_... | scaffold_placeholder | orphan |
| 5 | src/zephyr/sell_decision/infrastructure/__init__.py | src/zephyr/sell_decision/infrastructu... | scaffold_placeholder | orphan |
| 6 | src/zephyr/sell_decision/models/__init__.py | src/zephyr/sell_decision/models/__ini... | scaffold_placeholder | orphan |
| 7 | src/zephyr/sell_decision/services/__init__.py | src/zephyr/sell_decision/services/__i... | scaffold_placeholder | orphan |

### 未分类 / Unclassified (57 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-SELL-DECISION/Adjusted Stop Level 调整后止损位 | Adjusted Stop Level 调整后止损位 | design | design_only |
| 2 | D-SELL-DECISION/Average True Range ATR动态止损 | Average True Range ATR动态止损 | design | design_only |
| 3 | D-SELL-DECISION/Breakout Failure Detector突破成败检测器 | Breakout Failure Detector突破成败检测器 | design | design_only |
| 4 | D-SELL-DECISION/Breakout Result 突破成败结果 | Breakout Result 突破成败结果 | design | design_only |
| 5 | D-SELL-DECISION/Buy-Sell Conflict Arbitrator买卖冲突仲裁器 | Buy-Sell Conflict Arbitrator买卖冲突... | design | design_only |
| 6 | D-SELL-DECISION/D-SELL | D-SELL | design | design_only |
| 7 | D-SELL-DECISION/Day Trade Agent 做T Agent | Day Trade Agent 做T Agent | design | design_only |
| 8 | D-SELL-DECISION/Exit Scenario Plan 卖出情景预案 | Exit Scenario Plan 卖出情景预案 | design | design_only |
| 9 | D-SELL-DECISION/Exit Scenario Planner卖出情景预案器 | Exit Scenario Planner卖出情景预案器 | design | design_only |
| 10 | D-SELL-DECISION/Fused Sell Decision 融合卖出决策 | Fused Sell Decision 融合卖出决策 | design | design_only |
| 11 | D-SELL-DECISION/LimitDownBlock 跌停板拦截事件 | LimitDownBlock 跌停板拦截事件 | design | design_only |
| 12 | D-SELL-DECISION/Opportunity Cost Analyzer 机会成本分析器 | Opportunity Cost Analyzer 机会成本分析器 | design | design_only |
| 13 | D-SELL-DECISION/Position Triage Result 持仓分级结果 | Position Triage Result 持仓分级结果 | design | design_only |
| 14 | D-SELL-DECISION/Position Triage持仓分级器 | Position Triage持仓分级器 | design | design_only |
| 15 | D-SELL-DECISION/Replacement & Rebalance Sell置换与再平衡卖出 | Replacement & Rebalance Sell置换与再... | design | design_only |
| 16 | D-SELL-DECISION/Risk-Based Sell Trigger 风险驱动卖出触发器 | Risk-Based Sell Trigger 风险驱动卖出... | design | design_only |
| 17 | D-SELL-DECISION/Scaling Out Architect分批退出架构师 | Scaling Out Architect分批退出架构师 | design | design_only |
| 18 | D-SELL-DECISION/Scaling Out Plan 分批退出计划 | Scaling Out Plan 分批退出计划 | design | design_only |
| 19 | D-SELL-DECISION/Self-Reflection Agent 自反Agent | Self-Reflection Agent 自反Agent | design | design_only |
| 20 | D-SELL-DECISION/Sell A/B Test Result 卖出A/B测试结果 | Sell A/B Test Result 卖出A/B测试结果 | design | design_only |
| 21 | D-SELL-DECISION/Sell Audit Report 卖出审计报告 | Sell Audit Report 卖出审计报告 | design | design_only |
| 22 | D-SELL-DECISION/Sell Convergence Result 多策略卖出共振结果 | Sell Convergence Result 多策略卖出共... | design | design_only |
| 23 | D-SELL-DECISION/Sell Decision Domain 卖出决策域 | Sell Decision Domain 卖出决策域 | design | design_only |
| 24 | D-SELL-DECISION/Sell Decision Must Pass Fusion Arbitratio... | Sell Decision Must Pass Fusion Arbitr... | design | design_only |
| 25 | D-SELL-DECISION/Sell Execution Optimizer 卖出执行优化器 | Sell Execution Optimizer 卖出执行优化器 | design | design_only |
| 26 | D-SELL-DECISION/Sell Execution Quality Tracker卖出执行质... | Sell Execution Quality Tracker卖出执... | design | design_only |
| 27 | D-SELL-DECISION/Sell Execution Quality 卖出执行质量 | Sell Execution Quality 卖出执行质量 | design | design_only |
| 28 | D-SELL-DECISION/Sell Signal Accuracy Monitor卖出信号准确... | Sell Signal Accuracy Monitor卖出信号... | design | design_only |
| 29 | D-SELL-DECISION/Sell Signal Collector卖出信号收集器 | Sell Signal Collector卖出信号收集器 | design | design_only |
| 30 | D-SELL-DECISION/Sell Signal Fusion Engine卖出信号融合引擎 | Sell Signal Fusion Engine卖出信号融合... | design | design_only |
| 31 | D-SELL-DECISION/Sell Signal Score 卖出信号评分 | Sell Signal Score 卖出信号评分 | design | design_only |
| 32 | D-SELL-DECISION/Sell Signal Scorer卖出信号评分器 | Sell Signal Scorer卖出信号评分器 | design | design_only |
| 33 | D-SELL-DECISION/Sell Signal 卖出信号 | Sell Signal 卖出信号 | design | design_only |
| 34 | D-SELL-DECISION/Sell Strategy A/B Tester卖出策略A/B测试 | Sell Strategy A/B Tester卖出策略A/B测试 | design | design_only |
| 35 | D-SELL-DECISION/Sell Urgency Score 卖出紧迫度评分 | Sell Urgency Score 卖出紧迫度评分 | design | design_only |
| 36 | D-SELL-DECISION/Sell Urgency Scorer卖出紧迫度评分器 | Sell Urgency Scorer卖出紧迫度评分器 | design | design_only |
| 37 | D-SELL-DECISION/SellArbitrated 卖出仲裁完成事件 | SellArbitrated 卖出仲裁完成事件 | design | design_only |
| 38 | D-SELL-DECISION/SellArbitration 卖出仲裁 | SellArbitration 卖出仲裁 | design | design_only |
| 39 | D-SELL-DECISION/SellDecided 卖出决策事件 | SellDecided 卖出决策事件 | design | design_only |
| 40 | D-SELL-DECISION/SellDecision Contract SellDecision 卖出决... | SellDecision Contract SellDecision 卖... | design | design_only |
| 41 | D-SELL-DECISION/SellExecuted 卖出执行完成事件 | SellExecuted 卖出执行完成事件 | design | design_only |
| 42 | D-SELL-DECISION/SellLoopFeedback 卖出闭环反馈事件 | SellLoopFeedback 卖出闭环反馈事件 | design | design_only |
| 43 | D-SELL-DECISION/SellSignalFused Event SellSignalFused 卖... | SellSignalFused Event SellSignalFused... | design | design_only |
| 44 | D-SELL-DECISION/Signal Reversal Detector 信号反转检测器 | Signal Reversal Detector 信号反转检测器 | design | design_only |
| 45 | D-SELL-DECISION/Stop Cost Estimate 止损成本估计 | Stop Cost Estimate 止损成本估计 | design | design_only |
| 46 | D-SELL-DECISION/Stop Loss Strategy Family止损策略族 | Stop Loss Strategy Family止损策略族 | design | design_only |
| 47 | D-SELL-DECISION/Stop Option Pricer止损期权定价器 | Stop Option Pricer止损期权定价器 | design | design_only |
| 48 | D-SELL-DECISION/Stop Paradigm Selection 止损范式选择 | Stop Paradigm Selection 止损范式选择 | design | design_only |
| 49 | D-SELL-DECISION/Stop-Hunting Protector止损猎杀防护器 | Stop-Hunting Protector止损猎杀防护器 | design | design_only |
| 50 | D-SELL-DECISION/Stop-Loss Decision Engine 止损决策引擎 | Stop-Loss Decision Engine 止损决策引擎 | design | design_only |
| 51 | D-SELL-DECISION/StopLossTriggerReversalDetector 猎杀止损... | StopLossTriggerReversalDetector 猎杀... | design | design_only |
| 52 | D-SELL-DECISION/Strategy-Specific Stop Framework策略类型... | Strategy-Specific Stop Framework策略... | design | design_only |
| 53 | D-SELL-DECISION/T-Trade Coordinator做T决策协调器 | T-Trade Coordinator做T决策协调器 | design | design_only |
| 54 | D-SELL-DECISION/T-Trade Instruction 做T指令 | T-Trade Instruction 做T指令 | design | design_only |
| 55 | D-SELL-DECISION/TTradeExecuted 做T执行完成事件 | TTradeExecuted 做T执行完成事件 | design | design_only |
| 56 | D-SELL-DECISION/Take Profit Strategy Family止盈策略族 | Take Profit Strategy Family止盈策略族 | design | design_only |
| 57 | D-SELL-DECISION/Take-Profit Decision Engine 止盈决策引擎 | Take-Profit Decision Engine 止盈决策引擎 | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 55 条 / 55 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 55 条 / 55 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 4                               │
│   [import_depends]: 46 条 / edges                                │
│   [event]: 7 条 / edges                                          │
│   [config_depends]: 1 条 / edges                                 │
│   [contract]: 1 条 / edges                                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (46 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   D-SELL → Position Triage持仓分级器                             │
│   Position Triage持仓分级器 → Sell Signal Collector卖出...       │
│   Sell Signal Collector卖出... → Sell Signal Scorer卖出信...     │
│   Sell Signal Collector卖出... → Sell A/B Test Result 卖出...    │
│   Sell Signal Scorer卖出信... → Breakout Failure Detector...     │
│   Breakout Failure Detector... → Take Profit Strategy Fami...    │
│   Breakout Failure Detector... → Stop Cost Estimate 止损成...    │
│   Take Profit Strategy Fami... → Stop Loss Strategy Family...    │
│   Take Profit Strategy Fami... → Breakout Result 突破成败结果    │
│   Stop Loss Strategy Family... → Replacement & Rebalance S...    │
│   Replacement & Rebalance S... → Sell Signal Fusion Engine...    │
│   Replacement & Rebalance S... → Sell Convergence Result ...     │
│   Sell Signal Fusion Engine... → Buy-Sell Conflict Arbitra...    │
│   Buy-Sell Conflict Arbitra... → Sell Urgency Scorer卖出紧...    │
│   Buy-Sell Conflict Arbitra... → Self-Reflection Agent 自...     │
│   Buy-Sell Conflict Arbitra... → T-Trade Instruction 做T指令     │
│   Sell Urgency Scorer卖出紧... → Sell Signal Accuracy Moni...    │
│   Sell Signal Accuracy Moni... → Sell Strategy A/B Tester...     │
│   Sell Strategy A/B Tester... → Sell Execution Quality Tr...     │
│   Sell Strategy A/B Tester... → Sell Audit Report 卖出审...      │
│   Sell Execution Quality Tr... → Exit Scenario Planner卖出...    │
│   Sell Execution Quality Tr... → Day Trade Agent 做T Agent       │
│   Exit Scenario Planner卖出... → Strategy-Specific Stop Fr...    │
│   Exit Scenario Planner卖出... → Stop Paradigm Selection ...     │
│   Exit Scenario Planner卖出... → Sell Urgency Score 卖出紧...    │
│   Strategy-Specific Stop Fr... → Stop-Hunting Protector止...     │
│   Strategy-Specific Stop Fr... → Sell Signal 卖出信号            │
│   Strategy-Specific Stop Fr... → Sell Signal Score 卖出信...     │
│   Stop-Hunting Protector止... → Stop Option Pricer止损期...      │
│   Stop-Hunting Protector止... → Exit Scenario Plan 卖出情...     │
│   Stop Option Pricer止损期... → Scaling Out Architect分批...     │
│   Scaling Out Architect分批... → T-Trade Coordinator做T决...     │
│   T-Trade Coordinator做T决... → Stop-Loss Decision Engine...     │
│   Stop-Loss Decision Engine... → Take-Profit Decision Engi...    │
│   Stop-Loss Decision Engine... → Fused Sell Decision 融合...     │
│   Take-Profit Decision Engi... → Signal Reversal Detector ...    │
│   Take-Profit Decision Engi... → Adjusted Stop Level 调整...     │
│   Signal Reversal Detector ... → Risk-Based Sell Trigger ...     │
│   Risk-Based Sell Trigger ... → Opportunity Cost Analyzer...     │
│   Risk-Based Sell Trigger ... → Sell Execution Quality 卖...     │
│   Opportunity Cost Analyzer... → Sell Execution Optimizer ...    │
│   Opportunity Cost Analyzer... → SellArbitration 卖出仲裁        │
│   Opportunity Cost Analyzer... → Position Triage Result 持...    │
│   Sell Execution Optimizer ... → StopLossTriggerReversalDe...    │
│   StopLossTriggerReversalDe... → Average True Range ATR动...     │
│   Average True Range ATR动... → Scaling Out Plan 分批退出...     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      [event] (7 条 / edges)                      │
├──────────────────────────────────────────────────────────────────┤
│   Breakout Failure Detector... → SellArbitrated 卖出仲裁完...    │
│   Sell Signal Fusion Engine... → SellDecided 卖出决策事件        │
│   Sell Strategy A/B Tester... → SellSignalFused Event Sel...     │
│   ...还有 4 条 / 4 more edges                                    │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (1 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 55 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `37_d_sell_decision_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
