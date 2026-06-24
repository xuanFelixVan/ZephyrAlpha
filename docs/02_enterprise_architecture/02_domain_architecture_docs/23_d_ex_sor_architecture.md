---
doc_type: domain_architecture_diagram
title: D-EX_SOR 执行路由架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 23_d_ex_sor / 执行路由 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示执行路由（D-EX_SOR）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 执行路由（D-EX_SOR）的模块分布。共 131 个模块 / 131 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (7 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/ex_sor/__init__.py  [prototype]                     │
│   src/zephyr/ex_sor/_extensions/__init__.py  [scaffold_placeh... │
│   src/zephyr/ex_sor/api/__init__.py  [scaffold_placeholder]      │
│   src/zephyr/ex_sor/core/__init__.py  [scaffold_placeholder]     │
│   src/zephyr/ex_sor/infrastructure/__init__.py  [scaffold_pla... │
│   src/zephyr/ex_sor/models/__init__.py  [scaffold_placeholder]   │
│   src/zephyr/ex_sor/services/__init__.py  [scaffold_placeholder] │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (124 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   A2A-01 交易执行禁止A2A  [design]                               │
│   ALT算法 Aggressive Liquidity Taking  [design]                  │
│   API Doc Auto Version Syncer API文档自动版本同步器  [design]    │
│   API Route & Service Discovery API路由与服务发现  [design]      │
│   AUM>500万门禁  [design]                                        │
│   Adaptive Routing Optimizer 自适应路由优化器  [design]          │
│   Algo Execution Selector 算法执行选择器  [design]               │
│   Almgren-Chriss最优执行框架  [design]                           │
│   Backtrader框架  [design]                                       │
│   Broker API Connector 券商API连接器  [design]                   │
│   Broker Adapter 适配器  [design]                                │
│   C-026 API行为监控 API Behavior Monitor  [design]               │
│   CB-001 iFind数据拉取熔断器  [design]                           │
│   CB-002 miniQMT下单熔断器  [design]                             │
│   Close-Only Mode 仅平仓模式  [design]                           │
│   D-15 编排式Saga  [design]                                      │
│   D-EX-SOR 执行路由域 Execution Routing  [design]                │
│   D-EXECUTION-SOR 执行路由域  [design]                           │
│   ...还有 106 个模块 / 106 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 131 个模块 / 131 modules）。

### L2 领域层 / Domain Layer (7 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/ex_sor/__init__.py | src/zephyr/ex_sor/__init__.py | prototype | orphan |
| 2 | src/zephyr/ex_sor/_extensions/__init__.py | src/zephyr/ex_sor/_extensions/__init_... | scaffold_placeholder | orphan |
| 3 | src/zephyr/ex_sor/api/__init__.py | src/zephyr/ex_sor/api/__init__.py | scaffold_placeholder | orphan |
| 4 | src/zephyr/ex_sor/core/__init__.py | src/zephyr/ex_sor/core/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/ex_sor/infrastructure/__init__.py | src/zephyr/ex_sor/infrastructure/__in... | scaffold_placeholder | orphan |
| 6 | src/zephyr/ex_sor/models/__init__.py | src/zephyr/ex_sor/models/__init__.py | scaffold_placeholder | orphan |
| 7 | src/zephyr/ex_sor/services/__init__.py | src/zephyr/ex_sor/services/__init__.py | scaffold_placeholder | orphan |

### 未分类 / Unclassified (124 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-EX-SOR/A2A-01 交易执行禁止A2A | A2A-01 交易执行禁止A2A | design | design_only |
| 2 | D-EX-SOR/ALT算法 Aggressive Liquidity Taking | ALT算法 Aggressive Liquidity Taking | design | design_only |
| 3 | D-EX-SOR/API Doc Auto Version Syncer API文档自动版本同步器 | API Doc Auto Version Syncer API文档自... | design | design_only |
| 4 | D-EX-SOR/API Route & Service Discovery API路由与服务发现 | API Route & Service Discovery API路由... | design | design_only |
| 5 | D-EX-SOR/AUM>500万门禁 | AUM>500万门禁 | design | design_only |
| 6 | D-EX-SOR/Adaptive Routing Optimizer 自适应路由优化器 | Adaptive Routing Optimizer 自适应路由... | design | design_only |
| 7 | D-EX-SOR/Algo Execution Selector 算法执行选择器 | Algo Execution Selector 算法执行选择器 | design | design_only |
| 8 | D-EX-SOR/Almgren-Chriss最优执行框架 | Almgren-Chriss最优执行框架 | design | design_only |
| 9 | D-EX-SOR/Backtrader框架 | Backtrader框架 | design | design_only |
| 10 | D-EX-SOR/Broker API Connector 券商API连接器 | Broker API Connector 券商API连接器 | design | design_only |
| 11 | D-EX-SOR/Broker Adapter 适配器 | Broker Adapter 适配器 | design | design_only |
| 12 | D-EX-SOR/C-026 API行为监控 API Behavior Monitor | C-026 API行为监控 API Behavior Monitor | design | design_only |
| 13 | D-EX-SOR/CB-001 iFind数据拉取熔断器 | CB-001 iFind数据拉取熔断器 | design | design_only |
| 14 | D-EX-SOR/CB-002 miniQMT下单熔断器 | CB-002 miniQMT下单熔断器 | design | design_only |
| 15 | D-EX-SOR/Close-Only Mode 仅平仓模式 | Close-Only Mode 仅平仓模式 | design | design_only |
| 16 | D-EX-SOR/D-15 编排式Saga | D-15 编排式Saga | design | design_only |
| 17 | D-EX-SOR/D-EX-SOR 执行路由域 Execution Routing | D-EX-SOR 执行路由域 Execution Routing | design | design_only |
| 18 | D-EX-SOR/D-EXECUTION-SOR 执行路由域 | D-EXECUTION-SOR 执行路由域 | design | design_only |
| 19 | D-EX-SOR/DQN强化学习执行 | DQN强化学习执行 | design | design_only |
| 20 | D-EX-SOR/EX-SOR四域链路位置 | EX-SOR四域链路位置 | design | design_only |
| 21 | D-EX-SOR/Exchange API Rate Limiter 交易所API限速器 | Exchange API Rate Limiter 交易所API限... | design | design_only |
| 22 | D-EX-SOR/Execution Algorithm Engine 执行算法引擎 | Execution Algorithm Engine 执行算法引擎 | design | design_only |
| 23 | D-EX-SOR/Execution Quality Scorer 执行质量评分器 | Execution Quality Scorer 执行质量评分器 | design | design_only |
| 24 | D-EX-SOR/Execution Scheduler 调度器执行 | Execution Scheduler 调度器执行 | design | design_only |
| 25 | D-EX-SOR/FIX 4.2 协议 | FIX 4.2 协议 | design | design_only |
| 26 | D-EX-SOR/Fail-Closed 合规规则引擎不可用机制 | Fail-Closed 合规规则引擎不可用机制 | design | design_only |
| 27 | D-EX-SOR/Freqtrade框架 | Freqtrade框架 | design | design_only |
| 28 | D-EX-SOR/GATE-LP02 Kill Switch直连券商紧急平仓门禁 | GATE-LP02 Kill Switch直连券商紧急平仓... | design | design_only |
| 29 | D-EX-SOR/GATE-QP01 交易通道熔断自动恢复门禁 | GATE-QP01 交易通道熔断自动恢复门禁 | design | design_only |
| 30 | D-EX-SOR/GATE-QP02 MCP交易执行Server门禁 | GATE-QP02 MCP交易执行Server门禁 | design | design_only |
| 31 | D-EX-SOR/GATE-XS03 L2订单簿数据源门禁 | GATE-XS03 L2订单簿数据源门禁 | design | design_only |
| 32 | D-EX-SOR/GATE-XS04 多框架集成门禁 | GATE-XS04 多框架集成门禁 | design | design_only |
| 33 | D-EX-SOR/GATE-XS06 多交易场所接入门禁 | GATE-XS06 多交易场所接入门禁 | design | design_only |
| 34 | D-EX-SOR/GATE-XS07 L2订单簿+ABIDES门禁 | GATE-XS07 L2订单簿+ABIDES门禁 | design | design_only |
| 35 | D-EX-SOR/GATE-XS08 RL训练基础设施门禁 | GATE-XS08 RL训练基础设施门禁 | design | design_only |
| 36 | D-EX-SOR/GATE-XS09 DPDK/RDMA硬件门禁 | GATE-XS09 DPDK/RDMA硬件门禁 | design | design_only |
| 37 | D-EX-SOR/GATE-XS10 裸金属部署门禁 | GATE-XS10 裸金属部署门禁 | design | design_only |
| 38 | D-EX-SOR/GATE-XS12 ML训练管线门禁 | GATE-XS12 ML训练管线门禁 | design | design_only |
| 39 | D-EX-SOR/GATE-XS15 API文档结构化访问门禁 | GATE-XS15 API文档结构化访问门禁 | design | design_only |
| 40 | D-EX-SOR/GATE-XS16 多机部署门禁 | GATE-XS16 多机部署门禁 | design | design_only |
| 41 | D-EX-SOR/HB-01 外部系统故障不传染 | HB-01 外部系统故障不传染 | design | design_only |
| 42 | D-EX-SOR/HB-04 API版本不匹配拒绝 | HB-04 API版本不匹配拒绝 | design | design_only |
| 43 | D-EX-SOR/HB-05 隔离策略不可绕过 | HB-05 隔离策略不可绕过 | design | design_only |
| 44 | D-EX-SOR/HB-06 交易通道熔断人工恢复 | HB-06 交易通道熔断人工恢复 | design | design_only |
| 45 | D-EX-SOR/HB-07 下单不可自动重试 | HB-07 下单不可自动重试 | design | design_only |
| 46 | D-EX-SOR/HB-11 外部API统一网关 | HB-11 外部API统一网关 | design | design_only |
| 47 | D-EX-SOR/HYDRA-EI→HMARL 主观交易经验映射 | HYDRA-EI→HMARL 主观交易经验映射 | design | design_only |
| 48 | D-EX-SOR/Hawkes过程 | Hawkes过程 | design | design_only |
| 49 | D-EX-SOR/Hot平面10ms延迟预算 | Hot平面10ms延迟预算 | design | design_only |
| 50 | D-EX-SOR/ICEBERG算法 ICEBERG Algorithm | ICEBERG算法 ICEBERG Algorithm | design | design_only |
| 51 | D-EX-SOR/Implementation Shortfall算法 IS Algorithm | Implementation Shortfall算法 IS Algor... | design | design_only |
| 52 | D-EX-SOR/Kill-Switch五层防御架构 Kill Switch 5-Layer Defense | Kill-Switch五层防御架构 Kill Switch 5... | design | design_only |
| 53 | D-EX-SOR/L0 正常降级等级 | L0 正常降级等级 | design | design_only |
| 54 | D-EX-SOR/L1全局限流 | L1全局限流 | design | design_only |
| 55 | D-EX-SOR/L2外部系统级限流 | L2外部系统级限流 | design | design_only |
| 56 | D-EX-SOR/L3操作级限流 | L3操作级限流 | design | design_only |
| 57 | D-EX-SOR/L4优先级限流 | L4优先级限流 | design | design_only |
| 58 | D-EX-SOR/LOB不平衡度 | LOB不平衡度 | design | design_only |
| 59 | D-EX-SOR/LOB恢复速度 | LOB恢复速度 | design | design_only |
| 60 | D-EX-SOR/Level-2数据需求 Level-2 Data Requirement | Level-2数据需求 Level-2 Data Requirement | design | design_only |
| 61 | D-EX-SOR/Liquidity Detector 流动性检测器 | Liquidity Detector 流动性检测器 | design | design_only |
| 62 | D-EX-SOR/Low-Latency Data Handler 低延迟数据处理器 | Low-Latency Data Handler 低延迟数据处... | design | design_only |
| 63 | D-EX-SOR/Low-Latency Path Optimizer 低延迟路径优化器 | Low-Latency Path Optimizer 低延迟路径... | design | design_only |
| 64 | D-EX-SOR/MQMT-01 XtMiniQmt启动顺序 | MQMT-01 XtMiniQmt启动顺序 | design | design_only |
| 65 | D-EX-SOR/MQMT-02 极简模式登录 | MQMT-02 极简模式登录 | design | design_only |
| 66 | D-EX-SOR/MQMT-03 非交易时段拦截 | MQMT-03 非交易时段拦截 | design | design_only |
| 67 | D-EX-SOR/MQMT-04 版本匹配 | MQMT-04 版本匹配 | design | design_only |
| 68 | D-EX-SOR/MQMT-05 单进程单账户 | MQMT-05 单进程单账户 | design | design_only |
| 69 | D-EX-SOR/Market Impact Estimator 市场冲击估算器 | Market Impact Estimator 市场冲击估算器 | design | design_only |
| 70 | D-EX-SOR/Market Impact Modeler 模型 | Market Impact Modeler 模型 | design | design_only |
| 71 | D-EX-SOR/Multi-Exchange Optimal Router 多交易所最优路由器 | Multi-Exchange Optimal Router 多交易... | design | design_only |
| 72 | D-EX-SOR/Multi-Framework Strategy Router 多框架策略路由器 | Multi-Framework Strategy Router 多框... | design | design_only |
| 73 | D-EX-SOR/Order Book Simulator 订单簿仿真器 | Order Book Simulator 订单簿仿真器 | design | design_only |
| 74 | D-EX-SOR/Order Routing 订单路由 | Order Routing 订单路由 | design | design_only |
| 75 | D-EX-SOR/Order Splitting 拆单策略 | Order Splitting 拆单策略 | design | design_only |
| 76 | D-EX-SOR/P2子模块暂不纳入骨架 | P2子模块暂不纳入骨架 | design | design_only |
| 77 | D-EX-SOR/POV算法 POV Algorithm | POV算法 POV Algorithm | design | design_only |
| 78 | D-EX-SOR/PPO强化学习执行 | PPO强化学习执行 | design | design_only |
| 79 | D-EX-SOR/QP-01 交易通道熔断自动恢复不能建 | QP-01 交易通道熔断自动恢复不能建 | design | design_only |
| 80 | D-EX-SOR/QP-02 MCP交易执行Server不能建 | QP-02 MCP交易执行Server不能建 | design | design_only |
| 81 | D-EX-SOR/RL Execution Training Env RL执行训练环境 | RL Execution Training Env RL执行训练环境 | design | design_only |
| 82 | D-EX-SOR/SOR Agent 路由Agent | SOR Agent 路由Agent | design | design_only |
| 83 | D-EX-SOR/Saga超时硬约束 Saga Timeout Hard Constraint | Saga超时硬约束 Saga Timeout Hard Cons... | design | design_only |
| 84 | D-EX-SOR/Slippage Analyzer 滑点分析器 | Slippage Analyzer 滑点分析器 | design | design_only |
| 85 | D-EX-SOR/Smart Order Router 智能订单路由 | Smart Order Router 智能订单路由 | design | design_only |
| 86 | D-EX-SOR/Smart Order Router 智能订单路由器 | Smart Order Router 智能订单路由器 | design | design_only |
| 87 | D-EX-SOR/Smart Routing 智能路由 | Smart Routing 智能路由 | design | design_only |
| 88 | D-EX-SOR/Smart→Optimal/Adaptive 主观交易经验映射 | Smart→Optimal/Adaptive 主观交易经验映射 | design | design_only |
| 89 | D-EX-SOR/Sniper→ALT 主观交易经验映射 | Sniper→ALT 主观交易经验映射 | design | design_only |
| 90 | D-EX-SOR/TWAP算法 TWAP Algorithm | TWAP算法 TWAP Algorithm | design | design_only |
| 91 | D-EX-SOR/Transaction Cost Optimizer 交易成本优化器 | Transaction Cost Optimizer 交易成本优... | design | design_only |
| 92 | D-EX-SOR/VPIN 订单流毒性 | VPIN 订单流毒性 | design | design_only |
| 93 | D-EX-SOR/VWAP算法 VWAP Algorithm | VWAP算法 VWAP Algorithm | design | design_only |
| 94 | D-EX-SOR/VeighNa框架 | VeighNa框架 | design | design_only |
| 95 | D-EX-SOR/XS-05 Algo Trading Engine 算法交易引擎 | XS-05 Algo Trading Engine 算法交易引擎 | design | design_only |
| 96 | D-EX-SOR/XS-06 Venue Selector 交易场所选择器 | XS-06 Venue Selector 交易场所选择器 | design | design_only |
| 97 | D-EX-SOR/XS-07~XS-16 子模块设计引用 | XS-07~XS-16 子模块设计引用 | design | design_only |
| 98 | D-EX-SOR/XS-BrokerDisconnected 券商断开事件 | XS-BrokerDisconnected 券商断开事件 | design | design_only |
| 99 | D-EX-SOR/XS-ExecutionCompleted 执行完成事件 | XS-ExecutionCompleted 执行完成事件 | design | design_only |
| 100 | D-EX-SOR/XS-FillReceived 成交已收到事件 | XS-FillReceived 成交已收到事件 | design | design_only |
| 101 | D-EX-SOR/XS-OrderRouted 订单已路由事件 | XS-OrderRouted 订单已路由事件 | design | design_only |
| 102 | D-EX-SOR/XS-RouteOptimized 路由已优化事件 | XS-RouteOptimized 路由已优化事件 | design | design_only |
| 103 | D-EX-SOR/XTP/CTP/OKX 券商API | XTP/CTP/OKX 券商API | design | design_only |
| 104 | D-EX-SOR/XtMiniQmt.exe 极简模式进程 | XtMiniQmt.exe 极简模式进程 | design | design_only |
| 105 | D-EX-SOR/execution-sor 路由Agent | execution-sor 路由Agent | design | design_only |
| 106 | D-EX-SOR/miniQMT个人账户限制 | miniQMT个人账户限制 | design | design_only |
| 107 | D-EX-SOR/trading_core P3交易核心进程 | trading_core P3交易核心进程 | design | design_only |
| 108 | D-EX-SOR/xtquant miniQMT接口库 | xtquant miniQMT接口库 | design | design_only |
| 109 | D-EX-SOR/亏损报复→Revenge Trading 主观交易经验映射 | 亏损报复→Revenge Trading 主观交易经... | design | design_only |
| 110 | D-EX-SOR/仅平仓→Close-Only Mode 主观交易经验映射 | 仅平仓→Close-Only Mode 主观交易经验映射 | design | design_only |
| 111 | D-EX-SOR/保命轨→Emergency Survival Track 主观交易经验映射 | 保命轨→Emergency Survival Track 主观... | design | design_only |
| 112 | D-EX-SOR/做T→Intraday Round-trip Trading 主观交易经验映射 | 做T→Intraday Round-trip Trading 主观... | design | design_only |
| 113 | D-EX-SOR/做市商行为推断 Market Maker Behavior Inference | 做市商行为推断 Market Maker Behavior ... | design | design_only |
| 114 | D-EX-SOR/先报告后交易铁律 Report Before Trade | 先报告后交易铁律 Report Before Trade | design | design_only |
| 115 | D-EX-SOR/场内代码现状 On-site Code Status | 场内代码现状 On-site Code Status | design | design_only |
| 116 | D-EX-SOR/权重中心接口约束 Weight Center Interface Constraint | 权重中心接口约束 Weight Center Interf... | design | design_only |
| 117 | D-EX-SOR/止损减仓允许 Stop Loss Reduction Allowed | 止损减仓允许 Stop Loss Reduction Allowed | design | design_only |
| 118 | D-EX-SOR/盈利骄傲→Overconfidence 主观交易经验映射 | 盈利骄傲→Overconfidence 主观交易经验映射 | design | design_only |
| 119 | D-EX-SOR/被套补仓→Underwater Averaging Down 主观交易经验映射 | 被套补仓→Underwater Averaging Down ... | design | design_only |
| 120 | D-EX-SOR/路由Agent反思频率 Reflection Frequency | 路由Agent反思频率 Reflection Frequency | design | design_only |
| 121 | D-EX-SOR/路由Agent熔断器 | 路由Agent熔断器 | design | design_only |
| 122 | D-EX-SOR/路由降级 Route Degradation | 路由降级 Route Degradation | design | design_only |
| 123 | D-EX-SOR/踏空追高→FOMO Entry 主观交易经验映射 | 踏空追高→FOMO Entry 主观交易经验映射 | design | design_only |
| 124 | D-EX-SOR/追跌卖出→Distressed Selling 主观交易经验映射 | 追跌卖出→Distressed Selling 主观交易... | design | design_only |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 123 条 / 123 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 123 条 / 123 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 5                               │
│   [import_depends]: 87 条 / edges                                │
│   [config_depends]: 26 条 / edges                                │
│   [event]: 6 条 / edges                                          │
│   [runtime]: 3 条 / edges                                        │
│   [contract]: 1 条 / edges                                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (87 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   Smart Order Router 智能订... → Broker Adapter 适配器           │
│   Broker Adapter 适配器 → Market Impact Modeler 模型             │
│   Market Impact Modeler 模型 → Execution Scheduler 调度...       │
│   Execution Scheduler 调度... → Broker API Connector 券商...     │
│   Broker API Connector 券商... → C-026 API行为监控 API Beh...    │
│   C-026 API行为监控 API Beh... → Smart Order Router 智能订...    │
│   Smart Order Router 智能订... → Execution Algorithm Engin...    │
│   Execution Algorithm Engin... → Market Impact Estimator ...     │
│   Market Impact Estimator ... → Liquidity Detector 流动性...     │
│   Market Impact Estimator ... → 场内代码现状 On-site Code...     │
│   Liquidity Detector 流动性... → Order Book Simulator 订单...    │
│   Order Book Simulator 订单... → RL Execution Training Env...    │
│   RL Execution Training Env... → Low-Latency Data Handler ...    │
│   Low-Latency Data Handler ... → Low-Latency Path Optimize...    │
│   Low-Latency Path Optimize... → Algo Execution Selector ...     │
│   Algo Execution Selector ... → Adaptive Routing Optimize...     │
│   Adaptive Routing Optimize... → Exchange API Rate Limiter...    │
│   Exchange API Rate Limiter... → API Doc Auto Version Sync...    │
│   API Doc Auto Version Sync... → API Route & Service Disco...    │
│   API Route & Service Disco... → Slippage Analyzer 滑点分析器    │
│   Slippage Analyzer 滑点分析器 → Execution Quality Scorer ...    │
│   Execution Quality Scorer ... → Transaction Cost Optimize...    │
│   Transaction Cost Optimize... → Multi-Framework Strategy ...    │
│   Multi-Framework Strategy ... → Multi-Exchange Optimal Ro...    │
│   Multi-Exchange Optimal Ro... → SOR Agent 路由Agent             │
│   SOR Agent 路由Agent → Smart Routing 智能路由                   │
│   Smart Routing 智能路由 → Order Splitting 拆单策略              │
│   Order Splitting 拆单策略 → Order Routing 订单路由              │
│   Order Routing 订单路由 → XS-05 Algo Trading Engine...          │
│   D-EXECUTION-SOR 执行路由域 → 做市商行为推断 Market Mak...      │
│   XS-05 Algo Trading Engine... → XS-06 Venue Selector 交易...    │
│   XS-06 Venue Selector 交易... → execution-sor 路由Agent         │
│   execution-sor 路由Agent → 路由Agent熔断器                      │
│   路由Agent熔断器 → CB-002 miniQMT下单熔断器                     │
│   CB-002 miniQMT下单熔断器 → CB-001 iFind数据拉取熔断器          │
│   CB-001 iFind数据拉取熔断器 → Close-Only Mode 仅平仓模式        │
│   Close-Only Mode 仅平仓模式 → trading_core P3交易核心进程       │
│   trading_core P3交易核心进程 → xtquant miniQMT接口库            │
│   xtquant miniQMT接口库 → XtMiniQmt.exe 极简模式进程             │
│   XtMiniQmt.exe 极简模式进程 → XTP/CTP/OKX 券商API               │
│   XTP/CTP/OKX 券商API → FIX 4.2 协议                             │
│   FIX 4.2 协议 → L1全局限流                                      │
│   L1全局限流 → L2外部系统级限流                                  │
│   L2外部系统级限流 → L3操作级限流                                │
│   L3操作级限流 → L4优先级限流                                    │
│   L4优先级限流 → Almgren-Chriss最优执行框架                      │
│   Almgren-Chriss最优执行框架 → TWAP算法 TWAP Algorithm           │
│   Almgren-Chriss最优执行框架 → EX-SOR四域链路位置                │
│   TWAP算法 TWAP Algorithm → VWAP算法 VWAP Algorithm              │
│   ...还有 38 条 / 38 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (26 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (6 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (3 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 123 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `23_d_ex_sor_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
