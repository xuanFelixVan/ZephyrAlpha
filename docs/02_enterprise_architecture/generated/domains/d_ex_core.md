---
doc_type: domain_architecture_doc
title: D-EX_CORE 执行核心架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-EX_CORE 执行核心架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-EX_CORE |
| 域名称 | 执行核心 |
| 架构层 | L2_domain |
| 模块总数 | 135 |
| 设计态模块 | 120 |
| 原型态模块 | 6 |
| 生产态模块 | 3 |
| 容量 | 5/150 (正常) |
| 描述 | 执行核心域。负责订单执行核心引擎，包括订单拆分、执行算法(VWAP/TWAP/Iceberg)、执行质量分析。 |

## 模块清单

共 135 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
|  | MOD-EXECUTION_CORE | active | design | 0 | 0 |
| D-EX-CORE/Agent State Inconsistency Agent状态不一致 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Arbitration Priority System 仲裁优先级体系 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Auction Deviation Threshold Executor 竞价偏离阈值执行器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Blueprint Implementer 蓝图实现器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Broker ACL Broker访问控制列表 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Broker API 券商API |  | design_only | design | 0 | 0 |
| D-EX-CORE/Broker Interface broker接口 |  | design_only | design | 0 | 0 |
| D-EX-CORE/BrokerInterface 券商适配器接口 |  | design_only | design | 0 | 0 |
| D-EX-CORE/C Track L06 Layer C轨L06层 |  | design_only | design | 0 | 0 |
| D-EX-CORE/CTR-005 Fill CTR-005 Fill契约 |  | design_only | design | 0 | 0 |
| D-EX-CORE/CTR-006 PositionSnapshot CTR-006 PositionSnapshot契约 |  | design_only | design | 0 | 0 |
| ...ORE/CTR-ERR-005 ExecutionRejectionError CTR-ERR-005 ExecutionRejectionError契约 |  | design_only | design | 0 | 0 |
| D-EX-CORE/CTR-P1-007 ExecutionReport CTR-P1-007 ExecutionReport契约 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Circuit Breaker Pattern 熔断器模式 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Conditional Order Manager 条件订单管理器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Day Trade Execution 做T执行 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Day Trade PnL Estimate 做T盈亏预估 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Degradation Constraint Set 降级约束集 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Deployment Consistency Manager 部署一致性管理器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Design Decision Constraint Set 设计决策约束集 |  | design_only | design | 0 | 0 |
| D-EX-CORE/E-EX-04 FillReceived E-EX-04 FillReceived事件 |  | design_only | design | 0 | 0 |
| D-EX-CORE/E0.5 Integration Path Layer E0.5集成路径层 |  | design_only | design | 0 | 0 |
| D-EX-CORE/E1 Integration Path Layer E1集成路径层 |  | design_only | design | 0 | 0 |
| D-EX-CORE/E2 Integration Path Layer E2集成路径层 |  | design_only | design | 0 | 0 |
| D-EX-CORE/E3 Integration Path Layer E3集成路径层 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Emergency Execution 紧急执行 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Execution Aggregate Root Manager 执行聚合根管理器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Execution Auditor 执行审计 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Execution Core 执行核心 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Execution Domain Factory Method 执行域工厂方法 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Execution Domain Repository Interface 执行域仓储接口 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Execution Domain Value Object Definition 执行域值对象定义 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Execution Engine 执行引擎 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Execution Ops Auto-Optimization 执行运营自优化 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Execution Quality Analysis (TCA) 执行质量分析 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Execution Risk Gate 执行风险门禁 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Execution TCA 执行TCA |  | design_only | design | 0 | 0 |
| ...CORE/ExecutionModuleBase Code Generation Base Class ExecutionModuleBase代码生成基类 |  | design_only | design | 0 | 0 |
| D-EX-CORE/ExecutionRejectionError 执行拒绝错误 |  | design_only | design | 0 | 0 |
| D-EX-CORE/ExecutionReport 交易执行报告 |  | design_only | design | 0 | 0 |
| D-EX-CORE/ExecutionReport 执行报告 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Executor Agent 执行Agent |  | design_only | design | 0 | 0 |
| D-EX-CORE/Fill Contract 成交契约 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Fill Processor 成交处理器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Fill Tracker 成交跟踪器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/FillReceived 成交回报已接收 |  | design_only | design | 0 | 0 |
| D-EX-CORE/IdempotencyBlocked 幂等性拦截事件 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Integration Path Layer 集成路径层 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Intraday Position Reconciler 盘中持仓对账器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Kill Switch 紧急停机事件 |  | design_only | design | 0 | 0 |
| D-EX-CORE/L1 Fixed Slippage Model L1固定滑点模型 |  | design_only | design | 0 | 0 |
| D-EX-CORE/L2 Square Root Impact Slippage Model L2平方根冲击滑点模型 |  | design_only | design | 0 | 0 |
| D-EX-CORE/L3 Order Book Simulation Slippage Model L3订单簿模拟滑点模型 |  | design_only | design | 0 | 0 |
| D-EX-CORE/L4 to Execution Order Submission L4→执行订单提交 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Live/Simulation Switcher 实盘/模拟切换器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Microstructure Modeler 微观结构建模器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Nanosecond Critical Path Analyzer 纳秒级关键路径分析器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Non-Trading Hours Order Prohibition 非交易时段禁止下单 |  | design_only | design | 0 | 0 |
| D-EX-CORE/OMS Risk Engine OMS风险引擎 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Order Aggregate 订单聚合根 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Order Contract 订单契约 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Order Execution Saga Orchestrator 下单执行Saga编排器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Order Generation 订单生成 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Order Manager 订单管理器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Order Splitter 订单拆分器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Order State Machine 订单状态机 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Order Submission 订单提交 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Order Tracking 订单跟踪 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Order 订单聚合根 |  | design_only | design | 0 | 0 |
| D-EX-CORE/OrderCancelled 订单撤销事件 |  | design_only | design | 0 | 0 |
| D-EX-CORE/OrderCreated 订单创建事件 |  | design_only | design | 0 | 0 |
| D-EX-CORE/OrderExpired 订单过期事件 |  | design_only | design | 0 | 0 |
| D-EX-CORE/OrderFilled 订单已成交 |  | design_only | design | 0 | 0 |
| D-EX-CORE/OrderFilled 订单成交事件 |  | design_only | design | 0 | 0 |
| D-EX-CORE/OrderPlaced 订单已提交 |  | design_only | design | 0 | 0 |
| D-EX-CORE/OrderRejected 订单拒绝事件 |  | design_only | design | 0 | 0 |
| D-EX-CORE/OrderRejected 订单被拒事件 |  | design_only | design | 0 | 0 |
| D-EX-CORE/OrderSubmitted 订单提交事件 |  | design_only | design | 0 | 0 |
| D-EX-CORE/OrderSubmitted 订单提交契约 |  | design_only | design | 0 | 0 |
| D-EX-CORE/P2-Medium P2中优先级指令 |  | design_only | design | 0 | 0 |
| D-EX-CORE/P3 Heartbeat Loss Alert P3心跳丢失告警 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Parameterized Batch Executor 参数化分批执行器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Parameterized Batch Take Profit Executor 参数化分批止盈执行器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Parameterized Stop Loss/Take Profit Executor 参数化止损止盈执行器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Partial Fill Processor 部分成交处理器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Performance Monitor 性能监控器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Position Aggregate 持仓聚合根 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Position Tracker 持仓追踪 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Pre-Execution Checker 执行前检查器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Price 价格 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Quantity 数量 |  | design_only | design | 0 | 0 |
| D-EX-CORE/RL Optimal Executor RL最优执行器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Sell Priority Scheduler 卖出优先级调度器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Side 方向 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Simulation Broker 模拟Broker |  | design_only | design | 0 | 0 |
| D-EX-CORE/Single Large Order Non-Auto-Execute 单笔大额下单不可自动执行 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Slippage Model 3 Level Progressive 滑点模型3级渐进 |  | design_only | design | 0 | 0 |
| ...tive Trading Experience to Quantitative Framework Transformation 主观交易经验量化框架转化 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Subjective to Quantitative Transformation Record 主观到量化转化记录 |  | design_only | design | 0 | 0 |
| D-EX-CORE/T+1 Rule Non-Violable T+1规则不可违反 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Timer Agent 择时Agent |  | design_only | design | 0 | 0 |
| D-EX-CORE/Timing Decision 择时决策 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Trade Execution Core 交易执行核心 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Trade Execution 交易执行与订单管理 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Trading Channel Auto Recovery 交易通道熔断自动恢复 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Trading Kill Switch 交易Kill Switch |  | design_only | design | 0 | 0 |
| D-EX-CORE/Trading Pipeline Process 交易流水线进程 |  | design_only | design | 0 | 0 |
| D-EX-CORE/Trigger Evaluation 触发评估 |  | design_only | design | 0 | 0 |
| D-EX-CORE/l06-oms C轨L06层订单管理系统子模块 |  | design_only | design | 0 | 0 |
| D-EX-CORE/l06-pre-trade C轨L06层Pre-Trade子模块 |  | design_only | design | 0 | 0 |
| D-EX-CORE/miniQMT API Unavailable miniQMT API不可用 |  | design_only | design | 0 | 0 |
| D-EX-CORE/miniQMT Trading Channel Manager miniQMT交易通道管理器 |  | design_only | design | 0 | 0 |
| D-EX-CORE/miniQMT Trading Channel miniQMT交易通道 |  | design_only | design | 0 | 0 |
| D-EX-CORE/下单执行 下单执行 Execution |  | design_only | design | 0 | 0 |
| D-EX-CORE/任务执行流 Task Execution Stream |  | design_only | design | 0 | 0 |
| D-EX-CORE/做T日内套利 |  | design_only | design | 0 | 0 |
| D-EX-CORE/多契约生产适配器 Multi-contract Production Adapter |  | design_only | design | 0 | 0 |
| D-EX-CORE/当前持仓物化视图 Current Position View |  | design_only | design | 0 | 0 |
| D-EX-CORE/当日交易物化视图 Today's Trade View |  | design_only | design | 0 | 0 |
| src/zephyr/ex_core/__init__.py | MOD-L06-001 | draft | production | 4 | 0 |
| src/zephyr/ex_core/_extensions/__init__.py | MOD-EX_CORE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ex_core/adapters/__init__.py | MOD-EX_CORE | draft | prototype | 0 | 3 |
| src/zephyr/ex_core/adapters/broker_interface.py | MOD-EX_CORE | draft | production | 2 | 1 |
| src/zephyr/ex_core/adapters/risk_validation_bridge.py | MOD-EX_CORE | draft | prototype | 0 | 1 |
| src/zephyr/ex_core/adapters/simulation_broker.py | MOD-EX_CORE | draft | production | 4 | 1 |
| src/zephyr/ex_core/api/__init__.py | MOD-EX_CORE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ex_core/broker_interface.py | MOD-EX_CORE | draft | prototype | 0 | 1 |
| src/zephyr/ex_core/core/__init__.py | MOD-EX_CORE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ex_core/execution_engine.py | MOD-L06-001 | draft | prototype | 1 | 3 |
| src/zephyr/ex_core/infrastructure/__init__.py | MOD-EX_CORE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ex_core/models/__init__.py | MOD-EX_CORE | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ex_core/order_manager.py | MOD-L06-001 | draft | prototype | 2 | 3 |
| src/zephyr/ex_core/order_state_escalator.py | MOD-INF-022 | draft | prototype | 0 | 1 |
| src/zephyr/ex_core/services/__init__.py | MOD-EX_CORE | orphan | scaffold_placeholder | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-FACTOR | 15 | config_depends,data,contract,event |
| D-INFRA_RUNTIME | 10 | contract,event,config_depends,data |
| D-GOVERNANCE | 10 | import_depends,config_depends |
| D-MKT_DATA | 9 | data,contract,event |
| D-TRADING | 7 | import_depends,contract,data |
| D-EX_SOR | 7 | data,contract,event |
| D-DATA_ENG | 4 | data,contract |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 23 | import_depends,test_depends,config_depends,data,contract,event |
| D-COMPLIANCE | 23 | event,config_depends,contract,data |
| D-RISK | 20 | data,event,contract,config_depends |
| D-SECURITY | 16 | contract,data,event,config_depends |
| D-SIGNAL | 15 | data,contract,event,config_depends |
| D-INTEGRATION | 15 | data,config_depends,event,contract |
| D-AUTONOMY_CORE | 15 | config_depends,contract,data,event |
| D-OPS | 10 | data,contract,event |
| D-PF_CORE | 9 | event,config_depends,contract |
| D-SIMULATION | 7 | data,contract,event |
| D-INFRA_OPS | 7 | data,contract,event |
| D-INTELLIGENCE | 6 | data,config_depends,contract |
| D-REPORTING | 5 | data,contract,event |
| D-FRONTEND | 5 | event,config_depends,data |
| D-AUTONOMY_PERM | 4 | event,contract |
| D-POSITION | 3 | event,data,contract |
| D-KNOWLEDGE | 3 | event,contract,data |
| D-SELL_DECISION | 2 | data,event |
| D-CROSS_ASSET | 2 | contract,config_depends |
| D-PF_ALLOC | 1 | data |

## 域内依赖图

详见 [d_ex_core_dependency.mmd](d_ex_core_dependency.mmd)
