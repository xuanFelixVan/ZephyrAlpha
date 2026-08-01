---
doc_type: audit_report
title: 候选模块清单 — D_SELL_DECISION
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_SELL_DECISION 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **27** 条（原有 0 + harvest 27）。
> harvest 去重四态: likely_new=2 / likely_planned=25

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0109 | Position Triage持仓分级器 | / SELL-00 / Position Triage持仓分级器 / ✅ 能建 / / Watch/Monitor/Hold三级分级，动态升降级 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0110 | Sell Signal Collector卖出信号收集器 | / SELL-01 / Sell Signal Collector卖出信号收集器 / ✅ 能建 / / 汇聚8类卖出信号，输出标准化SellSignal列表 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0111 | Sell Signal Scorer卖出信号评分器 | / SELL-02 / Sell Signal Scorer卖出信号评分器 / ✅ 能建 / / 每类信号独立评分(0~1)+动态权重+多时间框架共振 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0112 | Breakout Failure Detector突破成败检测器 | / SELL-03 / Breakout Failure Detector突破成败检测器 / ✅ 能建 / / 消费L1因子层压力位判定突破成败，第K次失败(K>=3)强制清仓 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0113 | Take Profit Strategy Family止盈策略族 | / SELL-04 / Take Profit Strategy Family止盈策略族 / ✅ 能建 / / 固定/移动/分批/时间加权止盈，密度感知增强 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0114 | Stop Loss Strategy Family止损策略族 | / SELL-05 / Stop Loss Strategy Family止损策略族 / ✅ 能建 / / 固定/ATR/密度感知/移动止损+逻辑止损族 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0115 | Replacement & Rebalance Sell置换与再平衡卖出 | / SELL-06 / Replacement & Rebalance Sell置换与再平衡卖出 / ✅ 能建 / / 机会成本驱动(卖A买B)+组合权重偏离驱动被动卖出 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0116 | Sell Signal Fusion Engine卖出信号融合引擎 | / SELL-07 / Sell Signal Fusion Engine卖出信号融合引擎 / ✅ 能建 / / 多信号加权融合(加权平均/贝叶斯/Dempster-Shafer) / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0117 | Buy-Sell Conflict Arbitrator买卖冲突仲裁器 | / SELL-08 / Buy-Sell Conflict Arbitrator买卖冲突仲裁器 / ✅ 能建 / / 同标的买卖信号冲突时卖出优先(保守原则) / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0118 | Sell Urgency Scorer卖出紧迫度评分器 | SELL 09 Sell Urgency Scorer卖出紧迫度评分器 ✅ 能建 紧急清仓(1.0) | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0119 | Sell Signal Accuracy Monitor卖出信号准确率监控 | / SELL-10 / Sell Signal Accuracy Monitor卖出信号准确率监控 / ✅ 能建 / / 假阳性/假阴性分析，准确率趋势驱动权重调整 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0120 | Sell Strategy A/B Tester卖出策略A/B测试 | / SELL-11 / Sell Strategy A/B Tester卖出策略A/B测试 / ✅ 能建 / / 止盈线/止损方式/分批vs一次性对比 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0121 | Sell Execution Quality Tracker卖出执行质量追踪 | / SELL-12 / Sell Execution Quality Tracker卖出执行质量追踪 / ✅ 能建 / / 滑点/冲击成本/执行延迟/分批执行效果评分 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0122 | Exit Scenario Planner卖出情景预案器 | / SELL-13 / Exit Scenario Planner卖出情景预案器 / ✅ 能建 / / 盘前预计算6类卖出预案，盘中触发直接执行 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0123 | Strategy-Specific Stop Framework策略类型→止损范式映射 | / SELL-14 / Strategy-Specific Stop Framework策略类型→止损范式映射 / ✅ 能建 / / 趋势跟踪→宽止损+移动/均值回归→中等+固定等 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0124 | Stop-Hunting Protector止损猎杀防护器 | / SELL-15 / Stop-Hunting Protector止损猎杀防护器 / ✅ 能建 / / 止损位偏移1-2%防猎杀+软止损OBSERVING观察期 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0125 | Stop Option Pricer止损期权定价器 | / SELL-16 / Stop Option Pricer止损期权定价器 / ✅ 能建 / / 设止损=卖出隐含看跌期权→止损成本=隐含期权费 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0126 | Scaling Out Architect分批退出架构师 | / SELL-17 / Scaling Out Architect分批退出架构师 / ✅ 能建 / / 等分/倒金字塔/混合/风险驱动退出 / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0127 | T-Trade Coordinator做T决策协调器 | / SELL-18 / T-Trade Coordinator做T决策协调器 / ✅ 能建 / / A股T+1约束下正T/反T原子协调，做T仓位<=底仓30% / | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0920 | Stop-Loss Decision Engine 止损决策引擎 | 止损决策引擎固定比例止损+追踪止损+ATR止损+时间止损+逻辑失效止损+A股特色止损 | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0921 | Take-Profit Decision Engine 止盈决策引擎 | 止盈决策引擎目标价止盈+移动止盈+分批止盈+时间止盈+逻辑兑现止盈 | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0922 | Signal Reversal Detector 信号反转检测器 | 信号反转检测器买入信号失效检测+信号衰减检测+信号反转检测+反转确认 | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0923 | Risk-Based Sell Trigger 风险驱动卖出触发器 | 风险驱动卖出触发器VaR超限+回撤超限+集中度超限+流动性恶化+黑天鹅事件 | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0924 | Opportunity Cost Analyzer 机会成本分析器 | 机会成本分析器持仓机会成本+替代投资机会+资金效率+换仓决策 | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0925 | Sell Execution Optimizer 卖出执行优化器 | 卖出执行优化器卖出时机+卖出节奏+冲击成本控制+滑点控制+卖出算法 | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4885 | StopLossTriggerReversalDetector 猎杀止损保护器 | 止损触发后N分钟价格反转>M%统计显著 | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5081 | Average True Range ATR动态止损 | **核心逻辑**: 固定百分比止损（如-7%）是拍脑门的——高波动股7%只是正常波动，低波动股7%已是重大破位。专业机构用ATR（Average True Range）动态调整止损：Stop = Entry ± k×ATR，k通过Bayes | D_SELL_DECISION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（27 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0109 | Position Triage持仓分级器 | / SELL-00 / Position Triage持仓分级器 / ✅ 能建 / / Watch/Monitor/Hold三级分级，动态升降级 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0110 | Sell Signal Collector卖出信号收集器 | / SELL-01 / Sell Signal Collector卖出信号收集器 / ✅ 能建 / / 汇聚8类卖出信号，输出标准化SellSignal列表 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0111 | Sell Signal Scorer卖出信号评分器 | / SELL-02 / Sell Signal Scorer卖出信号评分器 / ✅ 能建 / / 每类信号独立评分(0~1)+动态权重+多时间框架共振 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0112 | Breakout Failure Detector突破成败检测器 | / SELL-03 / Breakout Failure Detector突破成败检测器 / ✅ 能建 / / 消费L1因子层压力位判定突破成败，第K次失败(K>=3)强制清仓 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0113 | Take Profit Strategy Family止盈策略族 | / SELL-04 / Take Profit Strategy Family止盈策略族 / ✅ 能建 / / 固定/移动/分批/时间加权止盈，密度感知增强 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0114 | Stop Loss Strategy Family止损策略族 | / SELL-05 / Stop Loss Strategy Family止损策略族 / ✅ 能建 / / 固定/ATR/密度感知/移动止损+逻辑止损族 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0115 | Replacement & Rebalance Sell置换与再平衡卖出 | / SELL-06 / Replacement & Rebalance Sell置换与再平衡卖出 / ✅ 能建 / / 机会成本驱动(卖A买B)+组合权重偏离驱动被动卖出 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0116 | Sell Signal Fusion Engine卖出信号融合引擎 | / SELL-07 / Sell Signal Fusion Engine卖出信号融合引擎 / ✅ 能建 / / 多信号加权融合(加权平均/贝叶斯/Dempster-Shafer) / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0117 | Buy-Sell Conflict Arbitrator买卖冲突仲裁器 | / SELL-08 / Buy-Sell Conflict Arbitrator买卖冲突仲裁器 / ✅ 能建 / / 同标的买卖信号冲突时卖出优先(保守原则) / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0118 | Sell Urgency Scorer卖出紧迫度评分器 | SELL 09 Sell Urgency Scorer卖出紧迫度评分器 ✅ 能建 紧急清仓(1.0) | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0119 | Sell Signal Accuracy Monitor卖出信号准确率监控 | / SELL-10 / Sell Signal Accuracy Monitor卖出信号准确率监控 / ✅ 能建 / / 假阳性/假阴性分析，准确率趋势驱动权重调整 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0120 | Sell Strategy A/B Tester卖出策略A/B测试 | / SELL-11 / Sell Strategy A/B Tester卖出策略A/B测试 / ✅ 能建 / / 止盈线/止损方式/分批vs一次性对比 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0121 | Sell Execution Quality Tracker卖出执行质量追踪 | / SELL-12 / Sell Execution Quality Tracker卖出执行质量追踪 / ✅ 能建 / / 滑点/冲击成本/执行延迟/分批执行效果评分 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0122 | Exit Scenario Planner卖出情景预案器 | / SELL-13 / Exit Scenario Planner卖出情景预案器 / ✅ 能建 / / 盘前预计算6类卖出预案，盘中触发直接执行 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0123 | Strategy-Specific Stop Framework策略类型→止损范式映射 | / SELL-14 / Strategy-Specific Stop Framework策略类型→止损范式映射 / ✅ 能建 / / 趋势跟踪→宽止损+移动/均值回归→中等+固定等 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0124 | Stop-Hunting Protector止损猎杀防护器 | / SELL-15 / Stop-Hunting Protector止损猎杀防护器 / ✅ 能建 / / 止损位偏移1-2%防猎杀+软止损OBSERVING观察期 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0125 | Stop Option Pricer止损期权定价器 | / SELL-16 / Stop Option Pricer止损期权定价器 / ✅ 能建 / / 设止损=卖出隐含看跌期权→止损成本=隐含期权费 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0126 | Scaling Out Architect分批退出架构师 | / SELL-17 / Scaling Out Architect分批退出架构师 / ✅ 能建 / / 等分/倒金字塔/混合/风险驱动退出 / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0127 | T-Trade Coordinator做T决策协调器 | / SELL-18 / T-Trade Coordinator做T决策协调器 / ✅ 能建 / / A股T+1约束下正T/反T原子协调，做T仓位<=底仓30% / | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0920 | Stop-Loss Decision Engine 止损决策引擎 | 止损决策引擎固定比例止损+追踪止损+ATR止损+时间止损+逻辑失效止损+A股特色止损 | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0921 | Take-Profit Decision Engine 止盈决策引擎 | 止盈决策引擎目标价止盈+移动止盈+分批止盈+时间止盈+逻辑兑现止盈 | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0922 | Signal Reversal Detector 信号反转检测器 | 信号反转检测器买入信号失效检测+信号衰减检测+信号反转检测+反转确认 | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0923 | Risk-Based Sell Trigger 风险驱动卖出触发器 | 风险驱动卖出触发器VaR超限+回撤超限+集中度超限+流动性恶化+黑天鹅事件 | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0924 | Opportunity Cost Analyzer 机会成本分析器 | 机会成本分析器持仓机会成本+替代投资机会+资金效率+换仓决策 | D_SELL_DECISION | harvest待评估（likely_new） |  |
| CAND-HARVEST-0925 | Sell Execution Optimizer 卖出执行优化器 | 卖出执行优化器卖出时机+卖出节奏+冲击成本控制+滑点控制+卖出算法 | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-4885 | StopLossTriggerReversalDetector 猎杀止损保护器 | 止损触发后N分钟价格反转>M%统计显著 | D_SELL_DECISION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-5081 | Average True Range ATR动态止损 | **核心逻辑**: 固定百分比止损（如-7%）是拍脑门的——高波动股7%只是正常波动，低波动股7%已是重大破位。专业机构用ATR（Average True Range）动态调整止损：Stop = Entry ± k×ATR，k通过Bayes | D_SELL_DECISION | harvest待评估（likely_new） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0109 | Position Triage持仓分级器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0110 | Sell Signal Collector卖出信号收集器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0111 | Sell Signal Scorer卖出信号评分器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0112 | Breakout Failure Detector突破成败检测器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0113 | Take Profit Strategy Family止盈策略族 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0114 | Stop Loss Strategy Family止损策略族 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0115 | Replacement & Rebalance Sell置换与再平衡卖出 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0116 | Sell Signal Fusion Engine卖出信号融合引擎 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0117 | Buy-Sell Conflict Arbitrator买卖冲突仲裁器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0118 | Sell Urgency Scorer卖出紧迫度评分器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0119 | Sell Signal Accuracy Monitor卖出信号准确率监控 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0120 | Sell Strategy A/B Tester卖出策略A/B测试 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0121 | Sell Execution Quality Tracker卖出执行质量追踪 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0122 | Exit Scenario Planner卖出情景预案器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0123 | Strategy-Specific Stop Framework策略类型→止损范式映射 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0124 | Stop-Hunting Protector止损猎杀防护器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0125 | Stop Option Pricer止损期权定价器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0126 | Scaling Out Architect分批退出架构师 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0127 | T-Trade Coordinator做T决策协调器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0920 | Stop-Loss Decision Engine 止损决策引擎 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0921 | Take-Profit Decision Engine 止盈决策引擎 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0922 | Signal Reversal Detector 信号反转检测器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0923 | Risk-Based Sell Trigger 风险驱动卖出触发器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0924 | Opportunity Cost Analyzer 机会成本分析器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0925 | Sell Execution Optimizer 卖出执行优化器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-4885 | StopLossTriggerReversalDetector 猎杀止损保护器 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-5081 | Average True Range ATR动态止损 | D_SELL_DECISION | 候选待评（candidate） | harvest待评估（likely_new） |
