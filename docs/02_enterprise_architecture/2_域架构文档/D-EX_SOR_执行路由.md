---
doc_type: domain_architecture_doc
title: D-EX_SOR 执行路由架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-EX_SOR 执行路由架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 23:25:14
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-EX_SOR |
| 域名称 | 执行路由 |
| 架构层 | L2_domain |
| 模块总数 | 131 |
| 设计态模块 | 124 |
| 原型态模块 | 1 |
| 生产态模块 | 0 |
| 容量 | 0/150 (正常) |
| 描述 | 执行路由域。负责智能订单路由(SOR)，包括多交易通道选择、流动性聚合、最优执行路径规划。 |

## 模块清单

共 131 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| D-EX-SOR/A2A-01 交易执行禁止A2A |  | design_only | design | 0 | 0 |
| D-EX-SOR/ALT算法 Aggressive Liquidity Taking |  | design_only | design | 0 | 0 |
| D-EX-SOR/API Doc Auto Version Syncer API文档自动版本同步器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/API Route & Service Discovery API路由与服务发现 |  | design_only | design | 0 | 0 |
| D-EX-SOR/AUM>500万门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Adaptive Routing Optimizer 自适应路由优化器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Algo Execution Selector 算法执行选择器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Almgren-Chriss最优执行框架 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Backtrader框架 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Broker API Connector 券商API连接器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Broker Adapter 适配器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/C-026 API行为监控 API Behavior Monitor |  | design_only | design | 0 | 0 |
| D-EX-SOR/CB-001 iFind数据拉取熔断器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/CB-002 miniQMT下单熔断器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Close-Only Mode 仅平仓模式 |  | design_only | design | 0 | 0 |
| D-EX-SOR/D-15 编排式Saga |  | design_only | design | 0 | 0 |
| D-EX-SOR/D-EX-SOR 执行路由域 Execution Routing |  | design_only | design | 0 | 0 |
| D-EX-SOR/D-EXECUTION-SOR 执行路由域 |  | design_only | design | 0 | 0 |
| D-EX-SOR/DQN强化学习执行 |  | design_only | design | 0 | 0 |
| D-EX-SOR/EX-SOR四域链路位置 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Exchange API Rate Limiter 交易所API限速器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Execution Algorithm Engine 执行算法引擎 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Execution Quality Scorer 执行质量评分器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Execution Scheduler 调度器执行 |  | design_only | design | 0 | 0 |
| D-EX-SOR/FIX 4.2 协议 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Fail-Closed 合规规则引擎不可用机制 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Freqtrade框架 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-LP02 Kill Switch直连券商紧急平仓门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-QP01 交易通道熔断自动恢复门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-QP02 MCP交易执行Server门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-XS03 L2订单簿数据源门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-XS04 多框架集成门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-XS06 多交易场所接入门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-XS07 L2订单簿+ABIDES门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-XS08 RL训练基础设施门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-XS09 DPDK/RDMA硬件门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-XS10 裸金属部署门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-XS12 ML训练管线门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-XS15 API文档结构化访问门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/GATE-XS16 多机部署门禁 |  | design_only | design | 0 | 0 |
| D-EX-SOR/HB-01 外部系统故障不传染 |  | design_only | design | 0 | 0 |
| D-EX-SOR/HB-04 API版本不匹配拒绝 |  | design_only | design | 0 | 0 |
| D-EX-SOR/HB-05 隔离策略不可绕过 |  | design_only | design | 0 | 0 |
| D-EX-SOR/HB-06 交易通道熔断人工恢复 |  | design_only | design | 0 | 0 |
| D-EX-SOR/HB-07 下单不可自动重试 |  | design_only | design | 0 | 0 |
| D-EX-SOR/HB-11 外部API统一网关 |  | design_only | design | 0 | 0 |
| D-EX-SOR/HYDRA-EI→HMARL 主观交易经验映射 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Hawkes过程 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Hot平面10ms延迟预算 |  | design_only | design | 0 | 0 |
| D-EX-SOR/ICEBERG算法 ICEBERG Algorithm |  | design_only | design | 0 | 0 |
| D-EX-SOR/Implementation Shortfall算法 IS Algorithm |  | design_only | design | 0 | 0 |
| D-EX-SOR/Kill-Switch五层防御架构 Kill Switch 5-Layer Defense |  | design_only | design | 0 | 0 |
| D-EX-SOR/L0 正常降级等级 |  | design_only | design | 0 | 0 |
| D-EX-SOR/L1全局限流 |  | design_only | design | 0 | 0 |
| D-EX-SOR/L2外部系统级限流 |  | design_only | design | 0 | 0 |
| D-EX-SOR/L3操作级限流 |  | design_only | design | 0 | 0 |
| D-EX-SOR/L4优先级限流 |  | design_only | design | 0 | 0 |
| D-EX-SOR/LOB不平衡度 |  | design_only | design | 0 | 0 |
| D-EX-SOR/LOB恢复速度 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Level-2数据需求 Level-2 Data Requirement |  | design_only | design | 0 | 0 |
| D-EX-SOR/Liquidity Detector 流动性检测器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Low-Latency Data Handler 低延迟数据处理器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Low-Latency Path Optimizer 低延迟路径优化器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/MQMT-01 XtMiniQmt启动顺序 |  | design_only | design | 0 | 0 |
| D-EX-SOR/MQMT-02 极简模式登录 |  | design_only | design | 0 | 0 |
| D-EX-SOR/MQMT-03 非交易时段拦截 |  | design_only | design | 0 | 0 |
| D-EX-SOR/MQMT-04 版本匹配 |  | design_only | design | 0 | 0 |
| D-EX-SOR/MQMT-05 单进程单账户 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Market Impact Estimator 市场冲击估算器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Market Impact Modeler 模型 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Multi-Exchange Optimal Router 多交易所最优路由器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Multi-Framework Strategy Router 多框架策略路由器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Order Book Simulator 订单簿仿真器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Order Routing 订单路由 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Order Splitting 拆单策略 |  | design_only | design | 0 | 0 |
| D-EX-SOR/P2子模块暂不纳入骨架 |  | design_only | design | 0 | 0 |
| D-EX-SOR/POV算法 POV Algorithm |  | design_only | design | 0 | 0 |
| D-EX-SOR/PPO强化学习执行 |  | design_only | design | 0 | 0 |
| D-EX-SOR/QP-01 交易通道熔断自动恢复不能建 |  | design_only | design | 0 | 0 |
| D-EX-SOR/QP-02 MCP交易执行Server不能建 |  | design_only | design | 0 | 0 |
| D-EX-SOR/RL Execution Training Env RL执行训练环境 |  | design_only | design | 0 | 0 |
| D-EX-SOR/SOR Agent 路由Agent |  | design_only | design | 0 | 0 |
| D-EX-SOR/Saga超时硬约束 Saga Timeout Hard Constraint |  | design_only | design | 0 | 0 |
| D-EX-SOR/Slippage Analyzer 滑点分析器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Smart Order Router 智能订单路由 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Smart Order Router 智能订单路由器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Smart Routing 智能路由 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Smart→Optimal/Adaptive 主观交易经验映射 |  | design_only | design | 0 | 0 |
| D-EX-SOR/Sniper→ALT 主观交易经验映射 |  | design_only | design | 0 | 0 |
| D-EX-SOR/TWAP算法 TWAP Algorithm |  | design_only | design | 0 | 0 |
| D-EX-SOR/Transaction Cost Optimizer 交易成本优化器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/VPIN 订单流毒性 |  | design_only | design | 0 | 0 |
| D-EX-SOR/VWAP算法 VWAP Algorithm |  | design_only | design | 0 | 0 |
| D-EX-SOR/VeighNa框架 |  | design_only | design | 0 | 0 |
| D-EX-SOR/XS-05 Algo Trading Engine 算法交易引擎 |  | design_only | design | 0 | 0 |
| D-EX-SOR/XS-06 Venue Selector 交易场所选择器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/XS-07~XS-16 子模块设计引用 |  | design_only | design | 0 | 0 |
| D-EX-SOR/XS-BrokerDisconnected 券商断开事件 |  | design_only | design | 0 | 0 |
| D-EX-SOR/XS-ExecutionCompleted 执行完成事件 |  | design_only | design | 0 | 0 |
| D-EX-SOR/XS-FillReceived 成交已收到事件 |  | design_only | design | 0 | 0 |
| D-EX-SOR/XS-OrderRouted 订单已路由事件 |  | design_only | design | 0 | 0 |
| D-EX-SOR/XS-RouteOptimized 路由已优化事件 |  | design_only | design | 0 | 0 |
| D-EX-SOR/XTP/CTP/OKX 券商API |  | design_only | design | 0 | 0 |
| D-EX-SOR/XtMiniQmt.exe 极简模式进程 |  | design_only | design | 0 | 0 |
| D-EX-SOR/execution-sor 路由Agent |  | design_only | design | 0 | 0 |
| D-EX-SOR/miniQMT个人账户限制 |  | design_only | design | 0 | 0 |
| D-EX-SOR/trading_core P3交易核心进程 |  | design_only | design | 0 | 0 |
| D-EX-SOR/xtquant miniQMT接口库 |  | design_only | design | 0 | 0 |
| D-EX-SOR/亏损报复→Revenge Trading 主观交易经验映射 |  | design_only | design | 0 | 0 |
| D-EX-SOR/仅平仓→Close-Only Mode 主观交易经验映射 |  | design_only | design | 0 | 0 |
| D-EX-SOR/保命轨→Emergency Survival Track 主观交易经验映射 |  | design_only | design | 0 | 0 |
| D-EX-SOR/做T→Intraday Round-trip Trading 主观交易经验映射 |  | design_only | design | 0 | 0 |
| D-EX-SOR/做市商行为推断 Market Maker Behavior Inference |  | design_only | design | 0 | 0 |
| D-EX-SOR/先报告后交易铁律 Report Before Trade |  | design_only | design | 0 | 0 |
| D-EX-SOR/场内代码现状 On-site Code Status |  | design_only | design | 0 | 0 |
| D-EX-SOR/权重中心接口约束 Weight Center Interface Constraint |  | design_only | design | 0 | 0 |
| D-EX-SOR/止损减仓允许 Stop Loss Reduction Allowed |  | design_only | design | 0 | 0 |
| D-EX-SOR/盈利骄傲→Overconfidence 主观交易经验映射 |  | design_only | design | 0 | 0 |
| D-EX-SOR/被套补仓→Underwater Averaging Down 主观交易经验映射 |  | design_only | design | 0 | 0 |
| D-EX-SOR/路由Agent反思频率 Reflection Frequency |  | design_only | design | 0 | 0 |
| D-EX-SOR/路由Agent熔断器 |  | design_only | design | 0 | 0 |
| D-EX-SOR/路由降级 Route Degradation |  | design_only | design | 0 | 0 |
| D-EX-SOR/踏空追高→FOMO Entry 主观交易经验映射 |  | design_only | design | 0 | 0 |
| D-EX-SOR/追跌卖出→Distressed Selling 主观交易经验映射 |  | design_only | design | 0 | 0 |
| src/zephyr/ex_sor/__init__.py | MOD-EX_SOR | orphan | prototype | 0 | 5 |
| src/zephyr/ex_sor/_extensions/__init__.py | MOD-EX_SOR | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ex_sor/api/__init__.py | MOD-EX_SOR | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ex_sor/core/__init__.py | MOD-EX_SOR | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ex_sor/infrastructure/__init__.py | MOD-EX_SOR | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ex_sor/models/__init__.py | MOD-EX_SOR | orphan | scaffold_placeholder | 0 | 0 |
| src/zephyr/ex_sor/services/__init__.py | MOD-EX_SOR | orphan | scaffold_placeholder | 0 | 0 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-INFRA_RUNTIME | 12 | event,contract,data,domain_dependency |
| D-SHARED | 1 | contract |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-SECURITY | 23 | event,contract,data,config_depends |
| D-COMPLIANCE | 22 | data,contract,config_depends,event |
| D-RISK | 19 | data,config_depends,event,contract |
| D-GOVERNANCE | 15 | data,contract,event,config_depends |
| D-AUTONOMY_CORE | 15 | config_depends,data,contract,event |
| D-SIGNAL | 13 | data,event,config_depends,contract |
| D-OPS | 13 | event,contract,data |
| D-INFRA_OPS | 13 | data,contract,config_depends |
| D-INTEGRATION | 11 | config_depends,contract,event,data |
| D-MKT_DATA | 8 | data,contract,config_depends,event |
| D-AUTONOMY_PERM | 8 | contract,event,data,config_depends |
| D-FRONTEND | 7 | data,config_depends,contract |
| D-FACTOR | 7 | config_depends,contract,event |
| D-EX_CORE | 7 | contract,event,data |
| D-REPORTING | 6 | config_depends,data,contract |
| D-TRADING | 4 | domain_dependency,config_depends,data,event |
| D-SELL_DECISION | 4 | contract,event |
| D-PF_CORE | 4 | config_depends,event,data |
| D-PF_ALLOC | 4 | config_depends,data,contract |
| D-INTELLIGENCE | 4 | event,contract,data |
| D-DATA_ENG | 4 | event,data,contract |
| D-SIMULATION | 3 | data |
| D-POSITION | 3 | event,contract |
| D-ML_TRAIN | 3 | event,contract |
| D-CROSS_ASSET | 3 | event,data,contract |
| D-ML_SERVE | 2 | contract,data |
| D-DATA_SEC | 1 | data |
| D-DATA_GOV | 1 | contract |
| D-ALT_DATA | 1 | config_depends |

## 域内依赖图

详见 [d_ex_sor_dependency.mmd](d_ex_sor_dependency.mmd)
