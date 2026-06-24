---
doc_type: domain_architecture_diagram
title: D-POSITION 仓位管理架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 35_d_position / 仓位管理 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示仓位管理（D-POSITION）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 仓位管理（D-POSITION）的模块分布。共 77 个模块 / 77 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (1 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/position/position_reconciler.py  [prototype]        │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (7 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/position/__init__.py  [prototype]                   │
│   src/zephyr/position/_extensions/__init__.py  [scaffold_plac... │
│   src/zephyr/position/api/__init__.py  [scaffold_placeholder]    │
│   src/zephyr/position/core/__init__.py  [scaffold_placeholder]   │
│   src/zephyr/position/infrastructure/__init__.py  [scaffold_p... │
│   src/zephyr/position/models/__init__.py  [scaffold_placeholder] │
│   src/zephyr/position/services/__init__.py  [scaffold_placeho... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (69 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   Anti-Pyramiding Scaler倒金字塔减仓器  [design]                 │
│   Calendar Position Constraint 日历仓位约束  [design]            │
│   CalendarPositionAlert 日历仓位预警  [design]                   │
│   Capital Curve Manager资金曲线管理器  [design]                  │
│   CapitalCurve 资金曲线  [design]                                │
│   CapitalCurveUpdated 资金曲线已更新  [design]                   │
│   Cash Manager现金管理器  [design]                               │
│   Corporate Action Processor 公司行为处理器  [design]            │
│   Correlation Regime Monitor Gate 相关性状态监控器门禁  [design] │
│   Correlation Regime Monitor相关性体制监控器  [design]           │
│   Covariance Estimator Gate 协方差估计器门禁  [design]           │
│   Covariance Estimator协方差矩阵估计器  [design]                 │
│   Cross-Strategy Position Merger Gate 多策略同标仓位合并门禁 ... │
│   Cross-Strategy Position Merger跨策略仓位合并器  [design]       │
│   D-POSITION 仓位  [design]                                      │
│   Daily Loss 5% AUM Liquidation 单日亏损超过AUM 5%清仓  [design] │
│   Drawdown Controller回撤控制器  [design]                        │
│   DriftDetected 漂移已检测  [design]                             │
│   ...还有 51 个模块 / 51 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 77 个模块 / 77 modules）。

### L1 基础层 / Foundation Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/position/position_reconciler.py | src/zephyr/position/position_reconcil... | prototype | draft |

### L2 领域层 / Domain Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/position/__init__.py | src/zephyr/position/__init__.py | prototype | orphan |
| 2 | src/zephyr/position/_extensions/__init__.py | src/zephyr/position/_extensions/__ini... | scaffold_placeholder | orphan |
| 3 | src/zephyr/position/api/__init__.py | src/zephyr/position/api/__init__.py | scaffold_placeholder | orphan |
| 4 | src/zephyr/position/core/__init__.py | src/zephyr/position/core/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/position/infrastructure/__init__.py | src/zephyr/position/infrastructure/__... | scaffold_placeholder | orphan |
| 6 | src/zephyr/position/models/__init__.py | src/zephyr/position/models/__init__.py | scaffold_placeholder | orphan |
| 7 | src/zephyr/position/services/__init__.py | src/zephyr/position/services/__init__.py | scaffold_placeholder | orphan |

### 未分类 / Unclassified (69 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-POSITION/Anti-Pyramiding Scaler倒金字塔减仓器 | Anti-Pyramiding Scaler倒金字塔减仓器 | design | design_only |
| 2 | D-POSITION/Calendar Position Constraint 日历仓位约束 | Calendar Position Constraint 日历仓位... | design | design_only |
| 3 | D-POSITION/CalendarPositionAlert 日历仓位预警 | CalendarPositionAlert 日历仓位预警 | design | design_only |
| 4 | D-POSITION/Capital Curve Manager资金曲线管理器 | Capital Curve Manager资金曲线管理器 | design | design_only |
| 5 | D-POSITION/CapitalCurve 资金曲线 | CapitalCurve 资金曲线 | design | design_only |
| 6 | D-POSITION/CapitalCurveUpdated 资金曲线已更新 | CapitalCurveUpdated 资金曲线已更新 | design | design_only |
| 7 | D-POSITION/Cash Manager现金管理器 | Cash Manager现金管理器 | design | design_only |
| 8 | D-POSITION/Corporate Action Processor 公司行为处理器 | Corporate Action Processor 公司行为处... | design | design_only |
| 9 | D-POSITION/Correlation Regime Monitor Gate 相关性状态监控... | Correlation Regime Monitor Gate 相关... | design | design_only |
| 10 | D-POSITION/Correlation Regime Monitor相关性体制监控器 | Correlation Regime Monitor相关性体制... | design | design_only |
| 11 | D-POSITION/Covariance Estimator Gate 协方差估计器门禁 | Covariance Estimator Gate 协方差估计... | design | design_only |
| 12 | D-POSITION/Covariance Estimator协方差矩阵估计器 | Covariance Estimator协方差矩阵估计器 | design | design_only |
| 13 | D-POSITION/Cross-Strategy Position Merger Gate 多策略同标... | Cross-Strategy Position Merger Gate ... | design | design_only |
| 14 | D-POSITION/Cross-Strategy Position Merger跨策略仓位合并器 | Cross-Strategy Position Merger跨策略... | design | design_only |
| 15 | D-POSITION/D-POSITION 仓位 | D-POSITION 仓位 | design | design_only |
| 16 | D-POSITION/Daily Loss 5% AUM Liquidation 单日亏损超过AUM ... | Daily Loss 5% AUM Liquidation 单日亏... | design | design_only |
| 17 | D-POSITION/Drawdown Controller回撤控制器 | Drawdown Controller回撤控制器 | design | design_only |
| 18 | D-POSITION/DriftDetected 漂移已检测 | DriftDetected 漂移已检测 | design | design_only |
| 19 | D-POSITION/Dynamic Level Decision 动态级决策 | Dynamic Level Decision 动态级决策 | design | design_only |
| 20 | D-POSITION/Every Order Must Pass Risk Check 每笔订单必须... | Every Order Must Pass Risk Check 每笔... | design | design_only |
| 21 | D-POSITION/Four-track Position Decision Architecture 仓位 | Four-track Position Decision Architec... | design | design_only |
| 22 | D-POSITION/Hot Plane Position Data Isolation 仓位 | Hot Plane Position Data Isolation 仓位 | design | design_only |
| 23 | D-POSITION/Intraday Position Constraint Gate 日内仓位约束... | Intraday Position Constraint Gate 日... | design | design_only |
| 24 | D-POSITION/Intraday Position Constraint 日内仓位约束 | Intraday Position Constraint 日内仓位... | design | design_only |
| 25 | D-POSITION/KS-L4 Derated Operation KS-L4降级运行 | KS-L4 Derated Operation KS-L4降级运行 | design | design_only |
| 26 | D-POSITION/L3 to L3.5 Position Sizing L3→L3.5仓位裁决 | L3 to L3.5 Position Sizing L3→L3.5仓... | design | design_only |
| 27 | D-POSITION/Liquidity Downgrade Mode 流动性降级模式 | Liquidity Downgrade Mode 流动性降级模式 | design | design_only |
| 28 | D-POSITION/Liquidity Spiral Three Phases 流动性螺旋三阶段 | Liquidity Spiral Three Phases 流动性... | design | design_only |
| 29 | D-POSITION/Loss Position Add Hard Block Invariant 亏损标... | Loss Position Add Hard Block Invarian... | design | design_only |
| 30 | D-POSITION/No Buy at Limit Up 涨停板不买入 | No Buy at Limit Up 涨停板不买入 | design | design_only |
| 31 | D-POSITION/No Order Outside Trading Hours 非交易时段不下单 | No Order Outside Trading Hours 非交易... | design | design_only |
| 32 | D-POSITION/No Sell at Limit Down 跌停板不卖出 | No Sell at Limit Down 跌停板不卖出 | design | design_only |
| 33 | D-POSITION/Order Saga Position Step 仓位订单 | Order Saga Position Step 仓位订单 | design | design_only |
| 34 | D-POSITION/Portfolio Level Decision 组合 | Portfolio Level Decision 组合 | design | design_only |
| 35 | D-POSITION/Position Arbitration Cannot Bypass Invariant ... | Position Arbitration Cannot Bypass In... | design | design_only |
| 36 | D-POSITION/Position Audit Logger仓位审计日志 | Position Audit Logger仓位审计日志 | design | design_only |
| 37 | D-POSITION/Position Behavior Classifier Gate 持仓行为分类... | Position Behavior Classifier Gate 持... | design | design_only |
| 38 | D-POSITION/Position Behavior Classifier 持仓行为分类器 | Position Behavior Classifier 持仓行为... | design | design_only |
| 39 | D-POSITION/Position Drift Monitor仓位漂移监控器 | Position Drift Monitor仓位漂移监控器 | design | design_only |
| 40 | D-POSITION/Position Limit Enforcer 持仓限额执行器 | Position Limit Enforcer 持仓限额执行器 | design | design_only |
| 41 | D-POSITION/Position Limit Enforcer仓位限制执行器 | Position Limit Enforcer仓位限制执行器 | design | design_only |
| 42 | D-POSITION/Position Management 仓位管理唯一裁决中心 | Position Management 仓位管理唯一裁决中心 | design | design_only |
| 43 | D-POSITION/Position RPO Zero Invariant 持仓RPO=0不变量 | Position RPO Zero Invariant 持仓RPO=0... | design | design_only |
| 44 | D-POSITION/Position Risk Monitor 持仓风险监控器 | Position Risk Monitor 持仓风险监控器 | design | design_only |
| 45 | D-POSITION/Position Sizing Engine标级仓位决策引擎 | Position Sizing Engine标级仓位决策引擎 | design | design_only |
| 46 | D-POSITION/Position State Machine持仓状态机 | Position State Machine持仓状态机 | design | design_only |
| 47 | D-POSITION/Position Time Budget Gate 仓位时间预算门禁 | Position Time Budget Gate 仓位时间预... | design | design_only |
| 48 | D-POSITION/Position Time Budget持仓时间预算器 | Position Time Budget持仓时间预算器 | design | design_only |
| 49 | D-POSITION/Position Tracker 持仓跟踪器 | Position Tracker 持仓跟踪器 | design | design_only |
| 50 | D-POSITION/Position 持仓聚合根 | Position 持仓聚合根 | design | design_only |
| 51 | D-POSITION/PositionPlan 仓位方案 | PositionPlan 仓位方案 | design | design_only |
| 52 | D-POSITION/PositionPlan 仓位方案契约 | PositionPlan 仓位方案契约 | design | design_only |
| 53 | D-POSITION/PositionSized 仓位已定 | PositionSized 仓位已定 | design | design_only |
| 54 | D-POSITION/PositionUpdated 持仓更新契约 | PositionUpdated 持仓更新契约 | design | design_only |
| 55 | D-POSITION/Rebalance Engine再平衡决策引擎 | Rebalance Engine再平衡决策引擎 | design | design_only |
| 56 | D-POSITION/RebalanceTriggered 再平衡已触发 | RebalanceTriggered 再平衡已触发 | design | design_only |
| 57 | D-POSITION/Risk Budget Allocator Gate 风险预算分配器门禁 | Risk Budget Allocator Gate 风险预算分... | design | design_only |
| 58 | D-POSITION/Risk Budget Allocator风险配额分配器 | Risk Budget Allocator风险配额分配器 | design | design_only |
| 59 | D-POSITION/ST/Delisting Risk Next Day Liquidation 持仓股... | ST/Delisting Risk Next Day Liquidatio... | design | design_only |
| 60 | D-POSITION/Scaling-Out Executor Gate 减仓执行器门禁 | Scaling-Out Executor Gate 减仓执行器门禁 | design | design_only |
| 61 | D-POSITION/Sell-Position Bidirectional Link卖出-仓位双向... | Sell-Position Bidirectional Link卖出-... | design | design_only |
| 62 | D-POSITION/Semi-Kelly Hard Cap Invariant 半Kelly为硬上限... | Semi-Kelly Hard Cap Invariant 半Kelly... | design | design_only |
| 63 | D-POSITION/Single Position 10% AUM Cap 单票持仓不超过AUM... | Single Position 10% AUM Cap 单票持仓... | design | design_only |
| 64 | D-POSITION/State-Position Mapping Immutable Invariant 状... | State-Position Mapping Immutable Inva... | design | design_only |
| 65 | D-POSITION/StateChanged 状态已变更 | StateChanged 状态已变更 | design | design_only |
| 66 | D-POSITION/Strategy Level Decision 策略 | Strategy Level Decision 策略 | design | design_only |
| 67 | D-POSITION/Symbol Level Decision 标的级决策 | Symbol Level Decision 标的级决策 | design | design_only |
| 68 | D-POSITION/Total Position 30% AUM Cap 总仓位不超过AUM的30% | Total Position 30% AUM Cap 总仓位不超... | design | design_only |
| 69 | D-POSITION/Unfilled Position Disaster Recovery 仓位 | Unfilled Position Disaster Recovery 仓位 | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 68 条 / 68 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 68 条 / 68 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 4                               │
│   [import_depends]: 43 条 / edges                                │
│   [config_depends]: 16 条 / edges                                │
│   [event]: 7 条 / edges                                          │
│   [contract]: 2 条 / edges                                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (43 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   Position Management 仓位... → Capital Curve Manager资金...     │
│   Position Sizing Engine标... → Position State Machine持...      │
│   Position Sizing Engine标... → Portfolio Level Decision ...     │
│   Position Sizing Engine标... → Symbol Level Decision 标...      │
│   Position Sizing Engine标... → Unfilled Position Disaste...     │
│   Position State Machine持... → Position Drift Monitor仓...      │
│   Position State Machine持... → L3 to L3.5 Position Sizin...     │
│   Position Drift Monitor仓... → Rebalance Engine再平衡决...      │
│   Position Drift Monitor仓... → Position 持仓聚合根              │
│   Rebalance Engine再平衡决... → Cross-Strategy Position M...     │
│   Rebalance Engine再平衡决... → PositionPlan 仓位方案            │
│   Rebalance Engine再平衡决... → Loss Position Add Hard Bl...     │
│   Cross-Strategy Position M... → Cash Manager现金管理器          │
│   Cross-Strategy Position M... → Position Arbitration Cann...    │
│   Cross-Strategy Position M... → Strategy Level Decision 策略    │
│   Cash Manager现金管理器 → Capital Curve Manager资金...          │
│   Cash Manager现金管理器 → Position RPO Zero Invaria...          │
│   Cash Manager现金管理器 → Liquidity Downgrade Mode ...          │
│   Capital Curve Manager资金... → Drawdown Controller回撤控...    │
│   Drawdown Controller回撤控... → Position Audit Logger仓位...    │
│   Drawdown Controller回撤控... → Order Saga Position Step ...    │
│   Position Audit Logger仓位... → Position Limit Enforcer仓...    │
│   Position Audit Logger仓位... → State-Position Mapping Im...    │
│   Position Audit Logger仓位... → Liquidity Spiral Three Ph...    │
│   Position Limit Enforcer仓... → Covariance Estimator协方...     │
│   Covariance Estimator协方... → Correlation Regime Monito...     │
│   Covariance Estimator协方... → Hot Plane Position Data I...     │
│   Correlation Regime Monito... → Risk Budget Allocator风险...    │
│   Correlation Regime Monito... → Dynamic Level Decision 动...    │
│   Risk Budget Allocator风险... → Anti-Pyramiding Scaler倒...     │
│   Anti-Pyramiding Scaler倒... → Position Time Budget持仓...      │
│   Position Time Budget持仓... → Sell-Position Bidirection...     │
│   Position Time Budget持仓... → CapitalCurve 资金曲线            │
│   Sell-Position Bidirection... → Position Tracker 持仓跟踪器     │
│   Position Tracker 持仓跟踪器 → Position Risk Monitor 持...      │
│   Position Risk Monitor 持... → Position Limit Enforcer ...      │
│   Position Risk Monitor 持... → Semi-Kelly Hard Cap Invar...     │
│   Position Limit Enforcer ... → Corporate Action Processo...     │
│   Position Limit Enforcer ... → KS-L4 Derated Operation K...     │
│   Corporate Action Processo... → Calendar Position Constra...    │
│   Calendar Position Constra... → Intraday Position Constra...    │
│   Intraday Position Constra... → Position Behavior Classif...    │
│   Intraday Position Constra... → Four-track Position Decis...    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (16 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   Position Sizing Engine标... → No Order Outside Trading ...     │
│   Position Drift Monitor仓... → Scaling-Out Executor Gate...     │
│   Cross-Strategy Position M... → Covariance Estimator Gate...    │
│   Cross-Strategy Position M... → No Buy at Limit Up 涨停板...    │
│   Cross-Strategy Position M... → ST/Delisting Risk Next Da...    │
│   Capital Curve Manager资金... → Risk Budget Allocator Gat...    │
│   ...还有 10 条 / 10 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[event]** (7 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (2 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 68 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `35_d_position_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
