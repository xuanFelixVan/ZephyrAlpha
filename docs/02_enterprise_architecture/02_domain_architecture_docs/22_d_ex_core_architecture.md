---
doc_type: domain_architecture_diagram
title: D-EX_CORE 执行核心架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 22_d_ex_core / 执行核心 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示执行核心（D-EX_CORE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:01:56
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 执行核心（D-EX_CORE）的模块分布。共 134 个模块 / 134 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│             L1 基础层 / Foundation Layer (3 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/ex_core/execution_engine.py  [prototype]            │
│   src/zephyr/ex_core/order_manager.py  [prototype]               │
│   src/zephyr/ex_core/order_state_escalator.py  [prototype]       │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│              L2 领域层 / Domain Layer (12 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   AGG-002  [design]                                              │
│   src/zephyr/ex_core/__init__.py  [production]                   │
│   src/zephyr/ex_core/_extensions/__init__.py  [scaffold_place... │
│   src/zephyr/ex_core/adapters/__init__.py  [prototype]           │
│   src/zephyr/ex_core/adapters/broker_interface.py  [production]  │
│   src/zephyr/ex_core/adapters/risk_validation_bridge.py  [pro... │
│   src/zephyr/ex_core/adapters/simulation_broker.py  [production] │
│   src/zephyr/ex_core/api/__init__.py  [scaffold_placeholder]     │
│   src/zephyr/ex_core/broker_interface.py  [prototype]            │
│   src/zephyr/ex_core/core/__init__.py  [scaffold_placeholder]    │
│   src/zephyr/ex_core/infrastructure/__init__.py  [scaffold_pl... │
│   src/zephyr/ex_core/services/__init__.py  [scaffold_placehol... │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (119 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   Agent State Inconsistency Agent状态不一致  [design]            │
│   Arbitration Priority System 仲裁优先级体系  [design]           │
│   Auction Deviation Threshold Executor 竞价偏离阈值执行器  [d... │
│   Blueprint Implementer 蓝图实现器  [design]                     │
│   Broker ACL Broker访问控制列表  [design]                        │
│   Broker API 券商API  [design]                                   │
│   Broker Interface broker接口  [design]                          │
│   BrokerInterface 券商适配器接口  [design]                       │
│   C Track L06 Layer C轨L06层  [design]                           │
│   CTR-005 Fill CTR-005 Fill契约  [design]                        │
│   CTR-006 PositionSnapshot CTR-006 PositionSnapshot契约  [des... │
│   CTR-ERR-005 ExecutionRejectionError CTR-ERR-005 ExecutionRe... │
│   CTR-P1-007 ExecutionReport CTR-P1-007 ExecutionReport契约  ... │
│   Circuit Breaker Pattern 熔断器模式  [design]                   │
│   Conditional Order Manager 条件订单管理器  [design]             │
│   Day Trade Execution 做T执行  [design]                          │
│   Day Trade PnL Estimate 做T盈亏预估  [design]                   │
│   Degradation Constraint Set 降级约束集  [design]                │
│   ...还有 101 个模块 / 101 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 134 个模块 / 134 modules）。

### L1 基础层 / Foundation Layer (3 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/ex_core/execution_engine.py | src/zephyr/ex_core/execution_engine.py | prototype | draft |
| 2 | src/zephyr/ex_core/order_manager.py | src/zephyr/ex_core/order_manager.py | prototype | draft |
| 3 | src/zephyr/ex_core/order_state_escalator.py | src/zephyr/ex_core/order_state_escala... | prototype | draft |

### L2 领域层 / Domain Layer (12 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 |  | AGG-002 | design | active |
| 2 | src/zephyr/ex_core/__init__.py | src/zephyr/ex_core/__init__.py | production | draft |
| 3 | src/zephyr/ex_core/_extensions/__init__.py | src/zephyr/ex_core/_extensions/__init... | scaffold_placeholder | orphan |
| 4 | src/zephyr/ex_core/adapters/__init__.py | src/zephyr/ex_core/adapters/__init__.py | prototype | draft |
| 5 | src/zephyr/ex_core/adapters/broker_interface.py | src/zephyr/ex_core/adapters/broker_in... | production | draft |
| 6 | src/zephyr/ex_core/adapters/risk_validation_bridge.py | src/zephyr/ex_core/adapters/risk_vali... | prototype | draft |
| 7 | src/zephyr/ex_core/adapters/simulation_broker.py | src/zephyr/ex_core/adapters/simulatio... | production | draft |
| 8 | src/zephyr/ex_core/api/__init__.py | src/zephyr/ex_core/api/__init__.py | scaffold_placeholder | orphan |
| 9 | src/zephyr/ex_core/broker_interface.py | src/zephyr/ex_core/broker_interface.py | prototype | draft |
| 10 | src/zephyr/ex_core/core/__init__.py | src/zephyr/ex_core/core/__init__.py | scaffold_placeholder | orphan |
| 11 | src/zephyr/ex_core/infrastructure/__init__.py | src/zephyr/ex_core/infrastructure/__i... | scaffold_placeholder | orphan |
| 12 | src/zephyr/ex_core/services/__init__.py | src/zephyr/ex_core/services/__init__.py | scaffold_placeholder | orphan |

### 未分类 / Unclassified (119 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-EX-CORE/Agent State Inconsistency Agent状态不一致 | Agent State Inconsistency Agent状态不... | design | design_only |
| 2 | D-EX-CORE/Arbitration Priority System 仲裁优先级体系 | Arbitration Priority System 仲裁优先... | design | design_only |
| 3 | D-EX-CORE/Auction Deviation Threshold Executor 竞价偏离阈... | Auction Deviation Threshold Executor ... | design | design_only |
| 4 | D-EX-CORE/Blueprint Implementer 蓝图实现器 | Blueprint Implementer 蓝图实现器 | design | design_only |
| 5 | D-EX-CORE/Broker ACL Broker访问控制列表 | Broker ACL Broker访问控制列表 | design | design_only |
| 6 | D-EX-CORE/Broker API 券商API | Broker API 券商API | design | design_only |
| 7 | D-EX-CORE/Broker Interface broker接口 | Broker Interface broker接口 | design | design_only |
| 8 | D-EX-CORE/BrokerInterface 券商适配器接口 | BrokerInterface 券商适配器接口 | design | design_only |
| 9 | D-EX-CORE/C Track L06 Layer C轨L06层 | C Track L06 Layer C轨L06层 | design | design_only |
| 10 | D-EX-CORE/CTR-005 Fill CTR-005 Fill契约 | CTR-005 Fill CTR-005 Fill契约 | design | design_only |
| 11 | D-EX-CORE/CTR-006 PositionSnapshot CTR-006 PositionSnapsh... | CTR-006 PositionSnapshot CTR-006 Posi... | design | design_only |
| 12 | D-EX-CORE/CTR-ERR-005 ExecutionRejectionError CTR-ERR-005... | CTR-ERR-005 ExecutionRejectionError C... | design | design_only |
| 13 | D-EX-CORE/CTR-P1-007 ExecutionReport CTR-P1-007 Execution... | CTR-P1-007 ExecutionReport CTR-P1-007... | design | design_only |
| 14 | D-EX-CORE/Circuit Breaker Pattern 熔断器模式 | Circuit Breaker Pattern 熔断器模式 | design | design_only |
| 15 | D-EX-CORE/Conditional Order Manager 条件订单管理器 | Conditional Order Manager 条件订单管理器 | design | design_only |
| 16 | D-EX-CORE/Day Trade Execution 做T执行 | Day Trade Execution 做T执行 | design | design_only |
| 17 | D-EX-CORE/Day Trade PnL Estimate 做T盈亏预估 | Day Trade PnL Estimate 做T盈亏预估 | design | design_only |
| 18 | D-EX-CORE/Degradation Constraint Set 降级约束集 | Degradation Constraint Set 降级约束集 | design | design_only |
| 19 | D-EX-CORE/Deployment Consistency Manager 部署一致性管理器 | Deployment Consistency Manager 部署一... | design | design_only |
| 20 | D-EX-CORE/Design Decision Constraint Set 设计决策约束集 | Design Decision Constraint Set 设计决... | design | design_only |
| 21 | D-EX-CORE/E-EX-04 FillReceived E-EX-04 FillReceived事件 | E-EX-04 FillReceived E-EX-04 FillRece... | design | design_only |
| 22 | D-EX-CORE/E0.5 Integration Path Layer E0.5集成路径层 | E0.5 Integration Path Layer E0.5集成... | design | design_only |
| 23 | D-EX-CORE/E1 Integration Path Layer E1集成路径层 | E1 Integration Path Layer E1集成路径层 | design | design_only |
| 24 | D-EX-CORE/E2 Integration Path Layer E2集成路径层 | E2 Integration Path Layer E2集成路径层 | design | design_only |
| 25 | D-EX-CORE/E3 Integration Path Layer E3集成路径层 | E3 Integration Path Layer E3集成路径层 | design | design_only |
| 26 | D-EX-CORE/Emergency Execution 紧急执行 | Emergency Execution 紧急执行 | design | design_only |
| 27 | D-EX-CORE/Execution Aggregate Root Manager 执行聚合根管理器 | Execution Aggregate Root Manager 执行... | design | design_only |
| 28 | D-EX-CORE/Execution Auditor 执行审计 | Execution Auditor 执行审计 | design | design_only |
| 29 | D-EX-CORE/Execution Core 执行核心 | Execution Core 执行核心 | design | design_only |
| 30 | D-EX-CORE/Execution Domain Factory Method 执行域工厂方法 | Execution Domain Factory Method 执行... | design | design_only |
| 31 | D-EX-CORE/Execution Domain Repository Interface 执行域仓... | Execution Domain Repository Interface... | design | design_only |
| 32 | D-EX-CORE/Execution Domain Value Object Definition 执行域... | Execution Domain Value Object Definit... | design | design_only |
| 33 | D-EX-CORE/Execution Engine 执行引擎 | Execution Engine 执行引擎 | design | design_only |
| 34 | D-EX-CORE/Execution Ops Auto-Optimization 执行运营自优化 | Execution Ops Auto-Optimization 执行... | design | design_only |
| 35 | D-EX-CORE/Execution Quality Analysis (TCA) 执行质量分析 | Execution Quality Analysis (TCA) 执行... | design | design_only |
| 36 | D-EX-CORE/Execution Risk Gate 执行风险门禁 | Execution Risk Gate 执行风险门禁 | design | design_only |
| 37 | D-EX-CORE/Execution TCA 执行TCA | Execution TCA 执行TCA | design | design_only |
| 38 | D-EX-CORE/ExecutionModuleBase Code Generation Base Class ... | ExecutionModuleBase Code Generation B... | design | design_only |
| 39 | D-EX-CORE/ExecutionRejectionError 执行拒绝错误 | ExecutionRejectionError 执行拒绝错误 | design | design_only |
| 40 | D-EX-CORE/ExecutionReport 交易执行报告 | ExecutionReport 交易执行报告 | design | design_only |
| 41 | D-EX-CORE/ExecutionReport 执行报告 | ExecutionReport 执行报告 | design | design_only |
| 42 | D-EX-CORE/Executor Agent 执行Agent | Executor Agent 执行Agent | design | design_only |
| 43 | D-EX-CORE/Fill Contract 成交契约 | Fill Contract 成交契约 | design | design_only |
| 44 | D-EX-CORE/Fill Processor 成交处理器 | Fill Processor 成交处理器 | design | design_only |
| 45 | D-EX-CORE/Fill Tracker 成交跟踪器 | Fill Tracker 成交跟踪器 | design | design_only |
| 46 | D-EX-CORE/FillReceived 成交回报已接收 | FillReceived 成交回报已接收 | design | design_only |
| 47 | D-EX-CORE/IdempotencyBlocked 幂等性拦截事件 | IdempotencyBlocked 幂等性拦截事件 | design | design_only |
| 48 | D-EX-CORE/Integration Path Layer 集成路径层 | Integration Path Layer 集成路径层 | design | design_only |
| 49 | D-EX-CORE/Intraday Position Reconciler 盘中持仓对账器 | Intraday Position Reconciler 盘中持仓... | design | design_only |
| 50 | D-EX-CORE/Kill Switch 紧急停机事件 | Kill Switch 紧急停机事件 | design | design_only |
| 51 | D-EX-CORE/L1 Fixed Slippage Model L1固定滑点模型 | L1 Fixed Slippage Model L1固定滑点模型 | design | design_only |
| 52 | D-EX-CORE/L2 Square Root Impact Slippage Model L2平方根冲... | L2 Square Root Impact Slippage Model ... | design | design_only |
| 53 | D-EX-CORE/L3 Order Book Simulation Slippage Model L3订单... | L3 Order Book Simulation Slippage Mod... | design | design_only |
| 54 | D-EX-CORE/L4 to Execution Order Submission L4→执行订单提交 | L4 to Execution Order Submission L4→... | design | design_only |
| 55 | D-EX-CORE/Live/Simulation Switcher 实盘/模拟切换器 | Live/Simulation Switcher 实盘/模拟切换器 | design | design_only |
| 56 | D-EX-CORE/Microstructure Modeler 微观结构建模器 | Microstructure Modeler 微观结构建模器 | design | design_only |
| 57 | D-EX-CORE/Nanosecond Critical Path Analyzer 纳秒级关键路... | Nanosecond Critical Path Analyzer 纳... | design | design_only |
| 58 | D-EX-CORE/Non-Trading Hours Order Prohibition 非交易时段... | Non-Trading Hours Order Prohibition ... | design | design_only |
| 59 | D-EX-CORE/OMS Risk Engine OMS风险引擎 | OMS Risk Engine OMS风险引擎 | design | design_only |
| 60 | D-EX-CORE/Order Aggregate 订单聚合根 | Order Aggregate 订单聚合根 | design | design_only |
| 61 | D-EX-CORE/Order Contract 订单契约 | Order Contract 订单契约 | design | design_only |
| 62 | D-EX-CORE/Order Execution Saga Orchestrator 下单执行Saga... | Order Execution Saga Orchestrator 下... | design | design_only |
| 63 | D-EX-CORE/Order Generation 订单生成 | Order Generation 订单生成 | design | design_only |
| 64 | D-EX-CORE/Order Manager 订单管理器 | Order Manager 订单管理器 | design | design_only |
| 65 | D-EX-CORE/Order Splitter 订单拆分器 | Order Splitter 订单拆分器 | design | design_only |
| 66 | D-EX-CORE/Order State Machine 订单状态机 | Order State Machine 订单状态机 | design | design_only |
| 67 | D-EX-CORE/Order Submission 订单提交 | Order Submission 订单提交 | design | design_only |
| 68 | D-EX-CORE/Order Tracking 订单跟踪 | Order Tracking 订单跟踪 | design | design_only |
| 69 | D-EX-CORE/Order 订单聚合根 | Order 订单聚合根 | design | design_only |
| 70 | D-EX-CORE/OrderCancelled 订单撤销事件 | OrderCancelled 订单撤销事件 | design | design_only |
| 71 | D-EX-CORE/OrderCreated 订单创建事件 | OrderCreated 订单创建事件 | design | design_only |
| 72 | D-EX-CORE/OrderExpired 订单过期事件 | OrderExpired 订单过期事件 | design | design_only |
| 73 | D-EX-CORE/OrderFilled 订单已成交 | OrderFilled 订单已成交 | design | design_only |
| 74 | D-EX-CORE/OrderFilled 订单成交事件 | OrderFilled 订单成交事件 | design | design_only |
| 75 | D-EX-CORE/OrderPlaced 订单已提交 | OrderPlaced 订单已提交 | design | design_only |
| 76 | D-EX-CORE/OrderRejected 订单拒绝事件 | OrderRejected 订单拒绝事件 | design | design_only |
| 77 | D-EX-CORE/OrderRejected 订单被拒事件 | OrderRejected 订单被拒事件 | design | design_only |
| 78 | D-EX-CORE/OrderSubmitted 订单提交事件 | OrderSubmitted 订单提交事件 | design | design_only |
| 79 | D-EX-CORE/OrderSubmitted 订单提交契约 | OrderSubmitted 订单提交契约 | design | design_only |
| 80 | D-EX-CORE/P2-Medium P2中优先级指令 | P2-Medium P2中优先级指令 | design | design_only |
| 81 | D-EX-CORE/P3 Heartbeat Loss Alert P3心跳丢失告警 | P3 Heartbeat Loss Alert P3心跳丢失告警 | design | design_only |
| 82 | D-EX-CORE/Parameterized Batch Executor 参数化分批执行器 | Parameterized Batch Executor 参数化分... | design | design_only |
| 83 | D-EX-CORE/Parameterized Batch Take Profit Executor 参数化... | Parameterized Batch Take Profit Execu... | design | design_only |
| 84 | D-EX-CORE/Parameterized Stop Loss/Take Profit Executor 参... | Parameterized Stop Loss/Take Profit E... | design | design_only |
| 85 | D-EX-CORE/Partial Fill Processor 部分成交处理器 | Partial Fill Processor 部分成交处理器 | design | design_only |
| 86 | D-EX-CORE/Performance Monitor 性能监控器 | Performance Monitor 性能监控器 | design | design_only |
| 87 | D-EX-CORE/Position Aggregate 持仓聚合根 | Position Aggregate 持仓聚合根 | design | design_only |
| 88 | D-EX-CORE/Position Tracker 持仓追踪 | Position Tracker 持仓追踪 | design | design_only |
| 89 | D-EX-CORE/Pre-Execution Checker 执行前检查器 | Pre-Execution Checker 执行前检查器 | design | design_only |
| 90 | D-EX-CORE/Price 价格 | Price 价格 | design | design_only |
| 91 | D-EX-CORE/Quantity 数量 | Quantity 数量 | design | design_only |
| 92 | D-EX-CORE/RL Optimal Executor RL最优执行器 | RL Optimal Executor RL最优执行器 | design | design_only |
| 93 | D-EX-CORE/Sell Priority Scheduler 卖出优先级调度器 | Sell Priority Scheduler 卖出优先级调度器 | design | design_only |
| 94 | D-EX-CORE/Side 方向 | Side 方向 | design | design_only |
| 95 | D-EX-CORE/Simulation Broker 模拟Broker | Simulation Broker 模拟Broker | design | design_only |
| 96 | D-EX-CORE/Single Large Order Non-Auto-Execute 单笔大额下... | Single Large Order Non-Auto-Execute ... | design | design_only |
| 97 | D-EX-CORE/Slippage Model 3 Level Progressive 滑点模型3级渐进 | Slippage Model 3 Level Progressive 滑... | design | design_only |
| 98 | D-EX-CORE/Subjective Trading Experience to Quantitative F... | Subjective Trading Experience to Quan... | design | design_only |
| 99 | D-EX-CORE/Subjective to Quantitative Transformation Recor... | Subjective to Quantitative Transforma... | design | design_only |
| 100 | D-EX-CORE/T+1 Rule Non-Violable T+1规则不可违反 | T+1 Rule Non-Violable T+1规则不可违反 | design | design_only |
| 101 | D-EX-CORE/Timer Agent 择时Agent | Timer Agent 择时Agent | design | design_only |
| 102 | D-EX-CORE/Timing Decision 择时决策 | Timing Decision 择时决策 | design | design_only |
| 103 | D-EX-CORE/Trade Execution Core 交易执行核心 | Trade Execution Core 交易执行核心 | design | design_only |
| 104 | D-EX-CORE/Trade Execution 交易执行与订单管理 | Trade Execution 交易执行与订单管理 | design | design_only |
| 105 | D-EX-CORE/Trading Channel Auto Recovery 交易通道熔断自动恢复 | Trading Channel Auto Recovery 交易通... | design | design_only |
| 106 | D-EX-CORE/Trading Kill Switch 交易Kill Switch | Trading Kill Switch 交易Kill Switch | design | design_only |
| 107 | D-EX-CORE/Trading Pipeline Process 交易流水线进程 | Trading Pipeline Process 交易流水线进程 | design | design_only |
| 108 | D-EX-CORE/Trigger Evaluation 触发评估 | Trigger Evaluation 触发评估 | design | design_only |
| 109 | D-EX-CORE/l06-oms C轨L06层订单管理系统子模块 | l06-oms C轨L06层订单管理系统子模块 | design | design_only |
| 110 | D-EX-CORE/l06-pre-trade C轨L06层Pre-Trade子模块 | l06-pre-trade C轨L06层Pre-Trade子模块 | design | design_only |
| 111 | D-EX-CORE/miniQMT API Unavailable miniQMT API不可用 | miniQMT API Unavailable miniQMT API不... | design | design_only |
| 112 | D-EX-CORE/miniQMT Trading Channel Manager miniQMT交易通道... | miniQMT Trading Channel Manager miniQ... | design | design_only |
| 113 | D-EX-CORE/miniQMT Trading Channel miniQMT交易通道 | miniQMT Trading Channel miniQMT交易通道 | design | design_only |
| 114 | D-EX-CORE/下单执行 下单执行 Execution | 下单执行 下单执行 Execution | design | design_only |
| 115 | D-EX-CORE/任务执行流 Task Execution Stream | 任务执行流 Task Execution Stream | design | design_only |
| 116 | D-EX-CORE/做T日内套利 | 做T日内套利 | design | design_only |
| 117 | D-EX-CORE/多契约生产适配器 Multi-contract Production Adapter | 多契约生产适配器 Multi-contract Produ... | design | design_only |
| 118 | D-EX-CORE/当前持仓物化视图 Current Position View | 当前持仓物化视图 Current Position View | design | design_only |
| 119 | D-EX-CORE/当日交易物化视图 Today's Trade View | 当日交易物化视图 Today's Trade View | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 116 条 / 116 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 116 条 / 116 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 4                               │
│   [import_depends]: 84 条 / edges                                │
│   [event]: 14 条 / edges                                         │
│   [contract]: 13 条 / edges                                      │
│   [config_depends]: 5 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (84 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   execution_engine.py → order_manager.py                         │
│   做T日内套利 → Day Trade Execution 做T执行                      │
│   Execution Quality Analysi... → P3 Heartbeat Loss Alert P...    │
│   Execution Ops Auto-Optimi... → Fill Tracker 成交跟踪器         │
│   Position Tracker 持仓追踪 → Execution Auditor 执行审计         │
│   Execution Auditor 执行审计 → 多契约生产适配器 Multi-co...      │
│   多契约生产适配器 Multi-co... → 当前持仓物化视图 Current ...    │
│   当前持仓物化视图 Current ... → 当日交易物化视图 Today's ...    │
│   当日交易物化视图 Today's ... → Order Manager 订单管理器        │
│   Order Manager 订单管理器 → Execution Engine 执行引擎           │
│   Order Manager 订单管理器 → Slippage Model 3 Level Pr...        │
│   Execution Engine 执行引擎 → Fill Tracker 成交跟踪器            │
│   Execution Engine 执行引擎 → Subjective Trading Experi...       │
│   Fill Tracker 成交跟踪器 → Fill Processor 成交处理器            │
│   Fill Tracker 成交跟踪器 → Price 价格                           │
│   Fill Processor 成交处理器 → Order State Machine 订单...        │
│   Order State Machine 订单... → Execution TCA 执行TCA            │
│   Execution TCA 执行TCA → Order Splitter 订单拆分器              │
│   Execution TCA 执行TCA → Position Aggregate 持仓聚...           │
│   Order Splitter 订单拆分器 → Deployment Consistency Ma...       │
│   Order Splitter 订单拆分器 → Execution Domain Value Ob...       │
│   Deployment Consistency Ma... → Pre-Execution Checker 执...     │
│   Pre-Execution Checker 执... → Parameterized Stop Loss/T...     │
│   Pre-Execution Checker 执... → Design Decision Constrain...     │
│   Parameterized Stop Loss/T... → Parameterized Batch Execu...    │
│   Parameterized Batch Execu... → Parameterized Batch Take ...    │
│   Parameterized Batch Execu... → L4 to Execution Order Sub...    │
│   Parameterized Batch Execu... → L2 Square Root Impact Sli...    │
│   Parameterized Batch Take ... → Auction Deviation Thresho...    │
│   Auction Deviation Thresho... → Sell Priority Scheduler ...     │
│   Sell Priority Scheduler ... → Live/Simulation Switcher ...     │
│   Live/Simulation Switcher ... → Performance Monitor 性能...     │
│   Performance Monitor 性能... → Blueprint Implementer 蓝...      │
│   Blueprint Implementer 蓝... → Conditional Order Manager...     │
│   Conditional Order Manager... → Partial Fill Processor 部...    │
│   Conditional Order Manager... → E1 Integration Path Layer...    │
│   Conditional Order Manager... → Degradation Constraint Se...    │
│   Partial Fill Processor 部... → Execution Aggregate Root ...    │
│   Partial Fill Processor 部... → C Track L06 Layer C轨L06层      │
│   Execution Aggregate Root ... → Execution Domain Factory ...    │
│   Execution Aggregate Root ... → miniQMT API Unavailable m...    │
│   Execution Domain Factory ... → Intraday Position Reconci...    │
│   Execution Domain Factory ... → Order Aggregate 订单聚合根      │
│   Intraday Position Reconci... → Order Execution Saga Orch...    │
│   Order Execution Saga Orch... → miniQMT Trading Channel M...    │
│   miniQMT Trading Channel M... → RL Optimal Executor RL最...     │
│   miniQMT Trading Channel M... → E0.5 Integration Path Lay...    │
│   RL Optimal Executor RL最... → Microstructure Modeler 微...     │
│   RL Optimal Executor RL最... → 任务执行流 Task Execution...     │
│   ...还有 35 条 / 35 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[event]** (14 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (13 条 / edges) — 已达显示上限，省略 / limit reached

**[config_depends]** (5 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 116 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `22_d_ex_core_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
