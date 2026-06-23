---
doc_type: domain_architecture_doc
title: D-POSITION 仓位管理架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-POSITION 仓位管理架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-POSITION |
| 域名称 | 仓位管理 |
| 架构层 | L2_domain |
| 模块总数 | 77 |
| 设计态模块 | 69 |
| 原型态模块 | 2 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 持仓跟踪、仓位计算、盈亏归因、仓位调整。仓位账本。 |

## 模块清单

共 77 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-POSITION/Anti-Pyramiding Scaler倒金字塔减仓器 |  | design_only | design | 0 | 0 |
| D-POSITION/Calendar Position Constraint 日历仓位约束 |  | design_only | design | 0 | 0 |
| D-POSITION/CalendarPositionAlert 日历仓位预警 |  | design_only | design | 0 | 0 |
| D-POSITION/Capital Curve Manager资金曲线管理器 |  | design_only | design | 0 | 0 |
| D-POSITION/CapitalCurve 资金曲线 |  | design_only | design | 0 | 0 |
| D-POSITION/CapitalCurveUpdated 资金曲线已更新 |  | design_only | design | 0 | 0 |
| D-POSITION/Cash Manager现金管理器 |  | design_only | design | 0 | 0 |
| D-POSITION/Corporate Action Processor 公司行为处理器 |  | design_only | design | 0 | 0 |
| D-POSITION/Correlation Regime Monitor Gate 相关性状态监控器门禁 |  | design_only | design | 0 | 0 |
| D-POSITION/Correlation Regime Monitor相关性体制监控器 |  | design_only | design | 0 | 0 |
| D-POSITION/Covariance Estimator Gate 协方差估计器门禁 |  | design_only | design | 0 | 0 |
| D-POSITION/Covariance Estimator协方差矩阵估计器 |  | design_only | design | 0 | 0 |
| D-POSITION/Cross-Strategy Position Merger Gate 多策略同标仓位合并门禁 |  | design_only | design | 0 | 0 |
| D-POSITION/Cross-Strategy Position Merger跨策略仓位合并器 |  | design_only | design | 0 | 0 |
| D-POSITION/D-POSITION 仓位 |  | design_only | design | 0 | 0 |
| D-POSITION/Daily Loss 5% AUM Liquidation 单日亏损超过AUM 5%清仓 |  | design_only | design | 0 | 0 |
| D-POSITION/Drawdown Controller回撤控制器 |  | design_only | design | 0 | 0 |
| D-POSITION/DriftDetected 漂移已检测 |  | design_only | design | 0 | 0 |
| D-POSITION/Dynamic Level Decision 动态级决策 |  | design_only | design | 0 | 0 |
| D-POSITION/Every Order Must Pass Risk Check 每笔订单必须经过风控检查 |  | design_only | design | 0 | 0 |
| D-POSITION/Four-track Position Decision Architecture 仓位 |  | design_only | design | 0 | 0 |
| D-POSITION/Hot Plane Position Data Isolation 仓位 |  | design_only | design | 0 | 0 |
| D-POSITION/Intraday Position Constraint Gate 日内仓位约束门禁 |  | design_only | design | 0 | 0 |
| D-POSITION/Intraday Position Constraint 日内仓位约束 |  | design_only | design | 0 | 0 |
| D-POSITION/KS-L4 Derated Operation KS-L4降级运行 |  | design_only | design | 0 | 0 |
| D-POSITION/L3 to L3.5 Position Sizing L3→L3.5仓位裁决 |  | design_only | design | 0 | 0 |
| D-POSITION/Liquidity Downgrade Mode 流动性降级模式 |  | design_only | design | 0 | 0 |
| D-POSITION/Liquidity Spiral Three Phases 流动性螺旋三阶段 |  | design_only | design | 0 | 0 |
| D-POSITION/Loss Position Add Hard Block Invariant 亏损标的加仓Hard Block不变量 |  | design_only | design | 0 | 0 |
| D-POSITION/No Buy at Limit Up 涨停板不买入 |  | design_only | design | 0 | 0 |
| D-POSITION/No Order Outside Trading Hours 非交易时段不下单 |  | design_only | design | 0 | 0 |
| D-POSITION/No Sell at Limit Down 跌停板不卖出 |  | design_only | design | 0 | 0 |
| D-POSITION/Order Saga Position Step 仓位订单 |  | design_only | design | 0 | 0 |
| D-POSITION/Portfolio Level Decision 组合 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Arbitration Cannot Bypass Invariant 仓位裁决不可绕过不变量 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Audit Logger仓位审计日志 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Behavior Classifier Gate 持仓行为分类器门禁 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Behavior Classifier 持仓行为分类器 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Drift Monitor仓位漂移监控器 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Limit Enforcer 持仓限额执行器 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Limit Enforcer仓位限制执行器 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Management 仓位管理唯一裁决中心 |  | design_only | design | 0 | 0 |
| D-POSITION/Position RPO Zero Invariant 持仓RPO=0不变量 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Risk Monitor 持仓风险监控器 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Sizing Engine标级仓位决策引擎 |  | design_only | design | 0 | 0 |
| D-POSITION/Position State Machine持仓状态机 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Time Budget Gate 仓位时间预算门禁 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Time Budget持仓时间预算器 |  | design_only | design | 0 | 0 |
| D-POSITION/Position Tracker 持仓跟踪器 |  | design_only | design | 0 | 0 |
| D-POSITION/Position 持仓聚合根 |  | design_only | design | 0 | 0 |
| D-POSITION/PositionPlan 仓位方案 |  | design_only | design | 0 | 0 |
| D-POSITION/PositionPlan 仓位方案契约 |  | design_only | design | 0 | 0 |
| D-POSITION/PositionSized 仓位已定 |  | design_only | design | 0 | 0 |
| D-POSITION/PositionUpdated 持仓更新契约 |  | design_only | design | 0 | 0 |
| D-POSITION/Rebalance Engine再平衡决策引擎 |  | design_only | design | 0 | 0 |
| D-POSITION/RebalanceTriggered 再平衡已触发 |  | design_only | design | 0 | 0 |
| D-POSITION/Risk Budget Allocator Gate 风险预算分配器门禁 |  | design_only | design | 0 | 0 |
| D-POSITION/Risk Budget Allocator风险配额分配器 |  | design_only | design | 0 | 0 |
| D-POSITION/ST/Delisting Risk Next Day Liquidation 持仓股票ST/退市风险次日清仓 |  | design_only | design | 0 | 0 |
| D-POSITION/Scaling-Out Executor Gate 减仓执行器门禁 |  | design_only | design | 0 | 0 |
| D-POSITION/Sell-Position Bidirectional Link卖出-仓位双向联动器 |  | design_only | design | 0 | 0 |
| D-POSITION/Semi-Kelly Hard Cap Invariant 半Kelly为硬上限不变量 |  | design_only | design | 0 | 0 |
| D-POSITION/Single Position 10% AUM Cap 单票持仓不超过AUM的10% |  | design_only | design | 0 | 0 |
| D-POSITION/State-Position Mapping Immutable Invariant 状态→仓位映射不可AI修改不变量 |  | design_only | design | 0 | 0 |
| D-POSITION/StateChanged 状态已变更 |  | design_only | design | 0 | 0 |
| D-POSITION/Strategy Level Decision 策略 |  | design_only | design | 0 | 0 |
| D-POSITION/Symbol Level Decision 标的级决策 |  | design_only | design | 0 | 0 |
| D-POSITION/Total Position 30% AUM Cap 总仓位不超过AUM的30% |  | design_only | design | 0 | 0 |
| D-POSITION/Unfilled Position Disaster Recovery 仓位 |  | design_only | design | 0 | 0 |
| src/zephyr/position/__init__.py | MOD-POSITION | orphan | prototype | 0 | 0 |
| src/zephyr/position/_extensions/__init__.py | MOD-POSITION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/position/api/__init__.py | MOD-POSITION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/position/core/__init__.py | MOD-POSITION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/position/infrastructure/__init__.py | MOD-POSITION | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/position/models/__init__.py | MOD-POSITION | orphan | scaffold_placeholder | 0 | 10 |
| src/zephyr/position/position_reconciler.py | MOD-INF-022 | draft | prototype | 0 | 1 |
| src/zephyr/position/services/__init__.py | MOD-POSITION | orphan | scaffold_placeholder | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-MKT_DATA | 8 | data,contract,config_depends,event |
| D-FACTOR | 8 | data,contract,event,config_depends |
| D-TRADING | 7 | domain_dependency,contract,data,event |
| D-DATA_ENG | 4 | contract,data,config_depends |
| D-EX_SOR | 3 | contract,event |
| D-EX_CORE | 3 | data,contract,event |
| D-INFRA_RUNTIME | 2 | event,contract |
| D-SHARED | 1 | contract |
| D-GOVERNANCE | 1 | config_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-RISK | 18 | domain_dependency,event,data,contract,config_depends |
| D-GOVERNANCE | 14 | config_depends,event,contract,data |
| D-SECURITY | 8 | contract,event,data |
| D-INFRA_OPS | 8 | contract,event,config_depends,data |
| D-COMPLIANCE | 8 | data,contract,config_depends,event |
| D-AUTONOMY_CORE | 7 | contract,data,event |
| D-SELL_DECISION | 5 | domain_dependency,event,data,contract |
| D-REPORTING | 5 | domain_dependency,event,contract,data |
| D-INTELLIGENCE | 5 | config_depends,contract |
| D-SIGNAL | 4 | data,contract,event |
| D-OPS | 4 | config_depends,contract,event |
| D-KNOWLEDGE | 4 | data,contract,config_depends |
| D-INTEGRATION | 4 | event,contract,data |
| D-ML_TRAIN | 3 | contract,data,config_depends |
| D-ML_SERVE | 3 | data,contract |
| D-AUTONOMY_PERM | 3 | data |
| D-PF_CORE | 2 | contract |
| D-PF_ALLOC | 2 | config_depends,contract |
| D-FRONTEND | 2 | contract,config_depends |
| D-ALT_DATA | 2 | contract,data |
| D-DATA_SEC | 1 | event |
| D-DATA_GOV | 1 | event |

## 域内依赖图

详见 [d_position_dependency.mmd](d_position_dependency.mmd)
