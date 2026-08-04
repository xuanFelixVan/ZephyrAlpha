---
doc_type: audit_report
title: 候选模块清单 — D_POSITION
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_POSITION 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **24** 条（原有 0 + harvest 24）。
> harvest 去重四态: likely_new=4 / likely_implemented=15 / likely_planned=5

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 一问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0019 | Position Management 仓位管理唯一裁决中心 | C 047：仓位管理唯一裁决中心 | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0076 | Position Sizing Engine标级仓位决策引擎 | / POS-01 / Position Sizing Engine标级仓位决策引擎 / ✅ 能建 / / Kelly准则/风险预算/分布感知决策，半Kelly硬上限 / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0077 | Position State Machine持仓状态机 | / POS-02 / Position State Machine持仓状态机 / ✅ 能建 / / NONE→BUILDING→ACTIVE→REDUCING→EXITING→CLOSED(含冷却期) / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0078 | Position Drift Monitor仓位漂移监控器 | / POS-03 / Position Drift Monitor仓位漂移监控器 / ✅ 能建 / / 每5分钟检查实际vs目标权重偏差，偏差>2%触发再平衡 / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0079 | Rebalance Engine再平衡决策引擎 | / POS-04 / Rebalance Engine再平衡决策引擎 / ✅ 能建 / / 日历/偏离/事件触发三种模式，交易成本>收益则跳过 / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0080 | Cross-Strategy Position Merger跨策略仓位合并器 | / POS-05 / Cross-Strategy Position Merger跨策略仓位合并器 / ✅ 能建 / / 多头取sum(不超单票上限)，一买一卖→卖出优先 / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0081 | Cash Manager现金管理器 | / POS-06 / Cash Manager现金管理器 / ✅ 能建 / / 最低现金储备+T+1结算约束+闲置资金逆回购 / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0082 | Capital Curve Manager资金曲线管理器 | / POS-07 / Capital Curve Manager资金曲线管理器 / ✅ 能建 / / 回撤分级控制+盈利扩张+Kelly本金联动 / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0083 | Drawdown Controller回撤控制器 | / POS-08 / Drawdown Controller回撤控制器 / ✅ 能建 / / 实时监控+分级响应(预警→降仓→暂停→仅防御) / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0084 | Position Audit Logger仓位审计日志 | / POS-09 / Position Audit Logger仓位审计日志 / ✅ 能建 / / 仓位变更追溯+决策输入输出全记录+审批链 / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0085 | Position Limit Enforcer仓位限制执行器 | / POS-10 / Position Limit Enforcer仓位限制执行器 / ✅ 能建 / / 硬约束强制执行(单票/行业/总仓位/半Kelly) / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0086 | Covariance Estimator协方差矩阵估计器 | / POS-11 / Covariance Estimator协方差矩阵估计器 / ✅ 能建 / / 收缩估计(Ledoit-Wolf)/因子模型/Copula-GARCH / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0087 | Correlation Regime Monitor相关性体制监控器 | / POS-12 / Correlation Regime Monitor相关性体制监控器 / ✅ 能建 / / 牛市相关性趋同→分散化失效预警→自动降仓 / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0088 | Risk Budget Allocator风险配额分配器 | / POS-13 / Risk Budget Allocator风险配额分配器 / ✅ 能建 / / 组合总风险预算→协方差矩阵分解到每标的风险配额 / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0089 | Anti-Pyramiding Scaler倒金字塔减仓器 | / POS-14 / Anti-Pyramiding Scaler倒金字塔减仓器 / ✅ 能建 / / 减仓20%-30%-50%，逆向中止(反弹超X%暂停) / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0090 | Position Time Budget持仓时间预算器 | / POS-15 / Position Time Budget持仓时间预算器 / ✅ 能建 / / 策略类型+市场状态决定最大持仓时间，超时触发退出评估 / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0091 | Sell-Position Bidirectional Link卖出-仓位双向联动器 | / POS-16 / Sell-Position Bidirectional Link卖出-仓位双向联动器 / ✅ 能建 / / 正向(卖出→仓位调整)+反向(仓位状态→卖出阈值调整) / | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0700 | Position Tracker 持仓跟踪器 | 持仓跟踪器实时持仓成本计算盈亏计算持仓历史持仓快照 | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0701 | Position Risk Monitor 持仓风险监控器 | 持仓风险监控集中度行业暴露因子暴露流动性风险VaR贡献 | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0702 | Position Limit Enforcer 持仓限额执行器 | 持仓限额执行器个股限额行业限额总仓位限额实时检查超限处理 | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0703 | Corporate Action Processor 公司行为处理器 | 公司行为处理除权除息拆股合并配股分红停复盘处理 | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1376 | Calendar Position Constraint 日历仓位约束 | A股风险日历+当前日期→CalendarPositionAlert | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1377 | Intraday Position Constraint 日内仓位约束 | 做T指令+底仓信息→做T仓位约束检查结果 | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1378 | Position Behavior Classifier 持仓行为分类器 | 大单净流向+仓位变化率→持仓行为分类 | D_POSITION | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |

## 按一问卡点分组（为什么没开发）

> 一问标准（裁定 2026-08-04）：仅 q1 已实现/重复。q1「是」即不进 depgraph 设计态，登记在候选库。原 q2/q3/q4 灰度已废。

### 待评估（24 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0019 | Position Management 仓位管理唯一裁决中心 | C 047：仓位管理唯一裁决中心 | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0076 | Position Sizing Engine标级仓位决策引擎 | / POS-01 / Position Sizing Engine标级仓位决策引擎 / ✅ 能建 / / Kelly准则/风险预算/分布感知决策，半Kelly硬上限 / | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0077 | Position State Machine持仓状态机 | / POS-02 / Position State Machine持仓状态机 / ✅ 能建 / / NONE→BUILDING→ACTIVE→REDUCING→EXITING→CLOSED(含冷却期) / | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0078 | Position Drift Monitor仓位漂移监控器 | / POS-03 / Position Drift Monitor仓位漂移监控器 / ✅ 能建 / / 每5分钟检查实际vs目标权重偏差，偏差>2%触发再平衡 / | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0079 | Rebalance Engine再平衡决策引擎 | / POS-04 / Rebalance Engine再平衡决策引擎 / ✅ 能建 / / 日历/偏离/事件触发三种模式，交易成本>收益则跳过 / | D_POSITION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0080 | Cross-Strategy Position Merger跨策略仓位合并器 | / POS-05 / Cross-Strategy Position Merger跨策略仓位合并器 / ✅ 能建 / / 多头取sum(不超单票上限)，一买一卖→卖出优先 / | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0081 | Cash Manager现金管理器 | / POS-06 / Cash Manager现金管理器 / ✅ 能建 / / 最低现金储备+T+1结算约束+闲置资金逆回购 / | D_POSITION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0082 | Capital Curve Manager资金曲线管理器 | / POS-07 / Capital Curve Manager资金曲线管理器 / ✅ 能建 / / 回撤分级控制+盈利扩张+Kelly本金联动 / | D_POSITION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0083 | Drawdown Controller回撤控制器 | / POS-08 / Drawdown Controller回撤控制器 / ✅ 能建 / / 实时监控+分级响应(预警→降仓→暂停→仅防御) / | D_POSITION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0084 | Position Audit Logger仓位审计日志 | / POS-09 / Position Audit Logger仓位审计日志 / ✅ 能建 / / 仓位变更追溯+决策输入输出全记录+审批链 / | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0085 | Position Limit Enforcer仓位限制执行器 | / POS-10 / Position Limit Enforcer仓位限制执行器 / ✅ 能建 / / 硬约束强制执行(单票/行业/总仓位/半Kelly) / | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0086 | Covariance Estimator协方差矩阵估计器 | / POS-11 / Covariance Estimator协方差矩阵估计器 / ✅ 能建 / / 收缩估计(Ledoit-Wolf)/因子模型/Copula-GARCH / | D_POSITION | harvest待评估（likely_new） |  |
| CAND-HARVEST-0087 | Correlation Regime Monitor相关性体制监控器 | / POS-12 / Correlation Regime Monitor相关性体制监控器 / ✅ 能建 / / 牛市相关性趋同→分散化失效预警→自动降仓 / | D_POSITION | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0088 | Risk Budget Allocator风险配额分配器 | / POS-13 / Risk Budget Allocator风险配额分配器 / ✅ 能建 / / 组合总风险预算→协方差矩阵分解到每标的风险配额 / | D_POSITION | harvest待评估（likely_new） |  |
| CAND-HARVEST-0089 | Anti-Pyramiding Scaler倒金字塔减仓器 | / POS-14 / Anti-Pyramiding Scaler倒金字塔减仓器 / ✅ 能建 / / 减仓20%-30%-50%，逆向中止(反弹超X%暂停) / | D_POSITION | harvest待评估（likely_new） |  |
| CAND-HARVEST-0090 | Position Time Budget持仓时间预算器 | / POS-15 / Position Time Budget持仓时间预算器 / ✅ 能建 / / 策略类型+市场状态决定最大持仓时间，超时触发退出评估 / | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0091 | Sell-Position Bidirectional Link卖出-仓位双向联动器 | / POS-16 / Sell-Position Bidirectional Link卖出-仓位双向联动器 / ✅ 能建 / / 正向(卖出→仓位调整)+反向(仓位状态→卖出阈值调整) / | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0700 | Position Tracker 持仓跟踪器 | 持仓跟踪器实时持仓成本计算盈亏计算持仓历史持仓快照 | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0701 | Position Risk Monitor 持仓风险监控器 | 持仓风险监控集中度行业暴露因子暴露流动性风险VaR贡献 | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0702 | Position Limit Enforcer 持仓限额执行器 | 持仓限额执行器个股限额行业限额总仓位限额实时检查超限处理 | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0703 | Corporate Action Processor 公司行为处理器 | 公司行为处理除权除息拆股合并配股分红停复盘处理 | D_POSITION | harvest待评估（likely_new） |  |
| CAND-HARVEST-1376 | Calendar Position Constraint 日历仓位约束 | A股风险日历+当前日期→CalendarPositionAlert | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1377 | Intraday Position Constraint 日内仓位约束 | 做T指令+底仓信息→做T仓位约束检查结果 | D_POSITION | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1378 | Position Behavior Classifier 持仓行为分类器 | 大单净流向+仓位变化率→持仓行为分类 | D_POSITION | harvest待评估（likely_implemented） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过一问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0019 | Position Management 仓位管理唯一裁决中心 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0076 | Position Sizing Engine标级仓位决策引擎 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0077 | Position State Machine持仓状态机 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0078 | Position Drift Monitor仓位漂移监控器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0079 | Rebalance Engine再平衡决策引擎 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0080 | Cross-Strategy Position Merger跨策略仓位合并器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0081 | Cash Manager现金管理器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0082 | Capital Curve Manager资金曲线管理器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0083 | Drawdown Controller回撤控制器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0084 | Position Audit Logger仓位审计日志 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0085 | Position Limit Enforcer仓位限制执行器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0086 | Covariance Estimator协方差矩阵估计器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0087 | Correlation Regime Monitor相关性体制监控器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0088 | Risk Budget Allocator风险配额分配器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0089 | Anti-Pyramiding Scaler倒金字塔减仓器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0090 | Position Time Budget持仓时间预算器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0091 | Sell-Position Bidirectional Link卖出-仓位双向联动器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0700 | Position Tracker 持仓跟踪器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0701 | Position Risk Monitor 持仓风险监控器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0702 | Position Limit Enforcer 持仓限额执行器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0703 | Corporate Action Processor 公司行为处理器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1376 | Calendar Position Constraint 日历仓位约束 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1377 | Intraday Position Constraint 日内仓位约束 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1378 | Position Behavior Classifier 持仓行为分类器 | D_POSITION | 候选待评（candidate） | harvest待评估（likely_implemented） |
