---
module_id: STRATEGY_EVALUATION_CRITERIA
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: STRATEGY_EVALUATION_CRITERIA_001
version: 1.0.0
status: Active
created_date: 2026-04-07
owner: 首席架构师
responsibility:
  - 扩展功能、辅助模块、支撑文档
  - 绩效分析
  - 系统架构
priority: P1
implementation_status: 蓝图阶段---


# 策略评估标准蓝图
> **核心职责**: 策略评估标准设计
> **职责边界**: 
> - ✅ 本文档负责：策略评估标准设计相关内容
> - ❌ 本文档不负责：其他模块内容

> **核心职责**: 蓝图设计和规划
> **职责边界**: 
> - ✅ 本文档负责：蓝图设计和规划相关内容
> - ❌ 本文档不负责：其他模块内容


## 核心职责

定义策略评估的标准体系，包括绩效指标、风险指标、稳定性指标、一致性指标，为策略选择提供量化依据。

## 关键功能

### 1. 绩效评估指标

**收益指标**：
- 总收益率（Total Return）
- 年化收益率（Annual Return）
- 超额收益率（Excess Return）
- 信息比率（Information Ratio）

**风险调整收益指标**：
- 夏普比率（Sharpe Ratio）：目标值 > 1.0
- 索提诺比率（Sortino Ratio）：目标值 > 1.2
- 卡玛比率（Calmar Ratio）：目标值 > 0.8
- 特雷诺比率（Treynor Ratio）

### 2. 风险评估指标

**波动性指标**：
- 年化波动率（Annual Volatility）：目标值 < 20%
- 下行波动率（Downside Volatility）
- 跟踪误差（Tracking Error）

**尾部风险指标**：
- 最大回撤（Max Drawdown）：目标值 < 20%
- VaR（Value at Risk）：95%置信度
- CVaR（Conditional VaR）：条件风险价值

### 3. 稳定性评估指标

**一致性指标**：
- 胜率（Win Rate）：目标值 > 50%
- 盈亏比（Profit/Loss Ratio）：目标值 > 1.5
- 月度正收益比例：目标值 > 60%

**稳定性指标**：
- 策略稳定性系数：目标值 > 0.8
- 收益分布偏度（Skewness）
- 收益分布峰度（Kurtosis）

### 4. 评估标准体系

**优秀策略标准**：
- 夏普比率 > 1.5
- 最大回撤 < 15%
- 年化收益 > 15%
- 胜率 > 55%

**合格策略标准**：
- 夏普比率 > 1.0
- 最大回撤 < 20%
- 年化收益 > 10%
- 胜率 > 50%

**淘汰策略标准**：
- 夏普比率 < 0.5
- 最大回撤 > 30%
- 年化收益 < 5%
- 连续3个月负收益

## 开源方案

- **empyrical**：绩效指标计算
- **pyfolio**：投资组合分析
- **QuantStats**：量化统计分析

## 依赖关系

**上游模块**：策略数据、市场数据

**下游模块**：策略选择框架、策略组合优化

## 实施优先级

P1 - 重要支持模块，建议在策略选择框架实施前完成

---

**版本**: v1.0 | **创建日期**: 2026-04-07 | **状态**: ✅ 蓝图完成
