---
doc_type: audit_report
title: 候选模块清单 — D_EX_CORE
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_EX_CORE 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **63** 条（原有 2 + harvest 61）。
> harvest 去重四态: likely_new=12 / likely_implemented=34 / likely_planned=14 / uncertain=1

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0068 | 做T日内套利 | C 012：做T日内套利 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0073 | Trade Execution 交易执行与订单管理 | C 002：交易执行与订单管理 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0075 | Execution Quality Analysis (TCA) 执行质量分析 | C 046：执行质量分析（TCA, Transaction Cost Analysis） | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0077 | Execution Ops Auto-Optimization 执行运营自优化 | C 026：执行运营自优化 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0581 | Execution Core 执行核心 | / L2→L3 / momentum_buy_signal / risk_budget_alloc / buy_decision / D-PF-CORE / CTR-005 / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0676 | Position Tracker 持仓追踪 | / D-EX-CORE-04 / Position Tracker / 持仓追踪+快照+DuckDB持仓历史+SQLite最新快照缓存+CTR-006 PositionSnapshot / ✅能建。当前持仓数据已在DuckDB中管理，增量改 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0677 | Execution Auditor 执行审计 | 审计日志记录器+合规规则引擎+执行质量评分器 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0678 | 多契约生产适配器 Multi-contract Production Adapter | / D-EX-CORE-55 / 多契约生产适配器 / CTR-004/005/006三个契约Schema定义+版本演进+消费者注册 / ✅能建。与§16 #3 Data Contract对齐，在SQLite中增加contract_regi | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0725 | 当前持仓物化视图 Current Position View | / 当前持仓 / position:{symbol} / Hash / 实时 / <5ms / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0727 | 当日交易物化视图 Today's Trade View | / 当日交易 / trade:today:{symbol} / List / 实时 / <5ms / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0755 | Order Manager 订单管理器 | 订单管理器订单创建状态机NEW SENT FILLED CANCELLED REJECTED订单路由 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0756 | Execution Engine 执行引擎 | 执行引擎订单执行执行算法执行质量评估滑点控制执行报告 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0757 | Fill Tracker 成交跟踪器 | 成交跟踪器成交确认成交分析成交归因成交统计异常成交检测 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1402 | Fill Processor 成交处理器 | 成交解析器+部分成交聚合器+成交归因器+费用计算器 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1403 | Order State Machine 订单状态机 | 7状态机+持久化+事件发射 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1404 | Execution TCA 执行TCA | IS计算器+延迟成本+机会成本+市场冲击归因+三阶段TCA | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1405 | Order Splitter 订单拆分器 | 拆分策略选择器+子订单生成器+Almgren-Chriss最优拆分 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1406 | Deployment Consistency Manager 部署一致性管理器 | 配置版本管理器+一致性检查器+灰度控制器+回滚管理器 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1407 | Pre-Execution Checker 执行前检查器 | 订单合规校验+市场状态检查+Pre-Trade主链6项 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1408 | Parameterized Stop Loss/Take Profit Executor 参数化止损止盈执行器 | 固定比例止损+MA破位止损+封流比阈值止盈等 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1409 | Parameterized Batch Executor 参数化分批执行器 | 分批比例配置+条件触发+进度追踪+失败回滚 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1410 | Parameterized Batch Take Profit Executor 参数化分批止盈执行器 | 触发止盈后分批卖出+MA破位确认清仓 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1411 | Auction Deviation Threshold Executor 竞价偏离阈值执行器 | 竞价偏离阈值→挂单卖出+MA反弹失败卖出 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1412 | Sell Priority Scheduler 卖出优先级调度器 | 优先级评分函数+优先级队列+滑点控制 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1413 | Live/Simulation Switcher 实盘/模拟切换器 | 实盘与模拟盘一键切换+状态同步+资金隔离 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1414 | Performance Monitor 性能监控器 | 执行成功率+延迟+可用性3维监控+SLA告警 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1415 | Blueprint Implementer 蓝图实现器 | EXEC.001订单生成+执行+状态机+路由+报告 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1416 | Conditional Order Manager 条件订单管理器 | 条件订单(OCO/OTO)+父子订单+订单簿 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1417 | Partial Fill Processor 部分成交处理器 | 部分成交状态更新与后续处理 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1418 | Execution Aggregate Root Manager 执行聚合根管理器 | Order/Position聚合根生命周期管理 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1419 | Execution Domain Factory Method 执行域工厂方法 | Order/Position复杂聚合根创建工厂 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1420 | Intraday Position Reconciler 盘中持仓对账器 | 每5分钟与miniQMT持仓查询自动对账 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1421 | Order Execution Saga Orchestrator 下单执行Saga编排器 | 编排式Saga六步+补偿幂等+≤5s超时硬约束 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1422 | miniQMT Trading Channel Manager miniQMT交易通道管理器 | xtquant接口封装+连接认证+指令签名+会话超时 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1424 | RL Optimal Executor RL最优执行器 | DQN/PPO增强Almgren-Chriss+学习非线性微观结构 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1425 | Microstructure Modeler 微观结构建模器 | VPIN订单流毒性检测+LOB动力学+做市商推断 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2114 | Timer Agent 择时Agent | 战术层择时Agent买卖点择时信号触发判定 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2116 | Executor Agent 执行Agent | 执行层执行Agent订单提交成交确认订单状态跟踪 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2122 | miniQMT Trading Channel miniQMT交易通道 | miniQMT交易通道唯一下单出口 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2144 | Timing Decision 择时决策 | 择时Agent技能择时决策ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2145 | Trigger Evaluation 触发评估 | 择时Agent技能触发评估ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2148 | Day Trade Execution 做T执行 | 做T Agent技能做T执行ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2149 | Day Trade PnL Estimate 做T盈亏预估 | 做T Agent技能做T盈亏预估ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2150 | Order Submission 订单提交 | 执行Agent技能订单提交ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2151 | Order Tracking 订单跟踪 | 执行Agent技能订单跟踪ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2347 | P2-Medium P2中优先级指令 | P2-中交易指令信号触发战术层按队列顺序处理可被P0/P1中断 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2584 | C-002 Execution Domain 执行域 | 执行域订单执行+Wash Trade检查 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2990 | Order Generation 订单生成 | 订单生成 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3449 | Trade Execution Core 交易执行核心 | / MOD-L06-001 / Trade Execution Core / 🔧部分实现 / risk_validation_bridge / §3.2 / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3905 | 下单执行 下单执行 Execution | Hot平面5ms延迟预算miniQMT API | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4120 | Trading Pipeline Process 交易流水线进程 | A1迁移概念级进程P0 因子增量计算信号生成风控监控做T触发执行算法不可崩溃 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4167 | P3 Heartbeat Loss Alert P3心跳丢失告警 | / AD-001b / P3心跳丢失 / rate(process_heartbeat_total{process='trading_core'}[10s])==0 持续10s / AL-P1(最高紧急) / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4168 | Simulation Broker 模拟Broker | / l06_trade_execution/adapters/simulation_broker.py / EX-CORE-03+04 / ❌Position Tracker耦合在内 / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4169 | OMS Risk Engine OMS风险引擎 | 场内代码对标EX-CORE-07归属应为D-EX-CORE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4170 | Trading Kill Switch 交易Kill Switch | 场内代码对标EX-CORE-02执行逻辑应在EX-CORE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4258 | l06-oms C轨L06层订单管理系统子模块 | C轨L06层子模块映射l06-oms订单管理系统 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4259 | l06-pre-trade C轨L06层Pre-Trade子模块 | / l06-pre-trade / D-EX-CORE-03 + D-EX-CORE-07 / 交易前风控与适配 / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4260 | ExecutionModuleBase Code Generation Base Class ExecutionModuleBase代码生成基类 | > LLM生成执行模块代码必须: 继承ExecutionModuleBase+所有订单操作通过OrderManager+所有持仓写入通过PositionTracker+所有Broker调用通过ExecutionEngine(INV-005) | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5050 | Nanosecond Critical Path Analyzer 纳秒级关键路径分析器 | / 纳秒级关键路径分析器 / Python运行时+miniQMT 3秒Tick / FPGA/内核旁路+交易通道延迟<1ms / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5054 | Trading Channel Auto Recovery 交易通道熔断自动恢复 | HB-SEC-06+HB-SEC-07双重锁定 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5080 | Emergency Execution 紧急执行 | 风控强制卖出链——EX-CORE-02紧急执行 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-EX-001 | Futu/IB Broker Adapters / 富途IB券商适配器 | 对接富途/IB券商的真实下单API。现在MiniQMT只管A股，等真要做港股/美股/期货时再加。 | D_EX_CORE | 延后（deferred） | q2 无需求驱动 | P1 | 实盘扩展到港股/美股/期货市场(MiniQMT仅覆盖A股) 等3条 | 2027-01-31 |
| CAND-EX-002 | Multi-threaded Order Processing / 多线程订单处理 | 下单从单线程改多线程并发，一次能同时发多个单。现在订单量小（并发<10），单线程不卡，等批量下单真成瓶颈再改。 | D_EX_CORE | 延后（deferred） | q2 无需求驱动 | P1 | 并发订单数持续>10 等3条 | 2027-01-31 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### q2 无需求驱动（2 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-EX-001 | Futu/IB Broker Adapters / 富途IB券商适配器 | 对接富途/IB券商的真实下单API。现在MiniQMT只管A股，等真要做港股/美股/期货时再加。 | D_EX_CORE | 首次登记,待非MiniQMT渠道需求或实盘扩展时重新评估 | MiniQMT渠道(已施工,覆盖A股实盘)。代价:无法接入港股/美股/期货 |
| CAND-EX-002 | Multi-threaded Order Processing / 多线程订单处理 | 下单从单线程改多线程并发，一次能同时发多个单。现在订单量小（并发<10），单线程不卡，等批量下单真成瓶颈再改。 | D_EX_CORE | 首次登记,待并发订单>10或提交延迟>100ms时重新评估 | 单线程顺序提交(当前实现)。代价:并发>10时延迟增加 |

### 待评估（61 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0068 | 做T日内套利 | C 012：做T日内套利 | D_EX_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0073 | Trade Execution 交易执行与订单管理 | C 002：交易执行与订单管理 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0075 | Execution Quality Analysis (TCA) 执行质量分析 | C 046：执行质量分析（TCA, Transaction Cost Analysis） | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0077 | Execution Ops Auto-Optimization 执行运营自优化 | C 026：执行运营自优化 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0581 | Execution Core 执行核心 | / L2→L3 / momentum_buy_signal / risk_budget_alloc / buy_decision / D-PF-CORE / CTR-005 / | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0676 | Position Tracker 持仓追踪 | / D-EX-CORE-04 / Position Tracker / 持仓追踪+快照+DuckDB持仓历史+SQLite最新快照缓存+CTR-006 PositionSnapshot / ✅能建。当前持仓数据已在DuckDB中管理，增量改 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0677 | Execution Auditor 执行审计 | 审计日志记录器+合规规则引擎+执行质量评分器 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0678 | 多契约生产适配器 Multi-contract Production Adapter | / D-EX-CORE-55 / 多契约生产适配器 / CTR-004/005/006三个契约Schema定义+版本演进+消费者注册 / ✅能建。与§16 #3 Data Contract对齐，在SQLite中增加contract_regi | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0725 | 当前持仓物化视图 Current Position View | / 当前持仓 / position:{symbol} / Hash / 实时 / <5ms / | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0727 | 当日交易物化视图 Today's Trade View | / 当日交易 / trade:today:{symbol} / List / 实时 / <5ms / | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0755 | Order Manager 订单管理器 | 订单管理器订单创建状态机NEW SENT FILLED CANCELLED REJECTED订单路由 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0756 | Execution Engine 执行引擎 | 执行引擎订单执行执行算法执行质量评估滑点控制执行报告 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0757 | Fill Tracker 成交跟踪器 | 成交跟踪器成交确认成交分析成交归因成交统计异常成交检测 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1402 | Fill Processor 成交处理器 | 成交解析器+部分成交聚合器+成交归因器+费用计算器 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1403 | Order State Machine 订单状态机 | 7状态机+持久化+事件发射 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1404 | Execution TCA 执行TCA | IS计算器+延迟成本+机会成本+市场冲击归因+三阶段TCA | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1405 | Order Splitter 订单拆分器 | 拆分策略选择器+子订单生成器+Almgren-Chriss最优拆分 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1406 | Deployment Consistency Manager 部署一致性管理器 | 配置版本管理器+一致性检查器+灰度控制器+回滚管理器 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1407 | Pre-Execution Checker 执行前检查器 | 订单合规校验+市场状态检查+Pre-Trade主链6项 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1408 | Parameterized Stop Loss/Take Profit Executor 参数化止损止盈执行器 | 固定比例止损+MA破位止损+封流比阈值止盈等 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1409 | Parameterized Batch Executor 参数化分批执行器 | 分批比例配置+条件触发+进度追踪+失败回滚 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1410 | Parameterized Batch Take Profit Executor 参数化分批止盈执行器 | 触发止盈后分批卖出+MA破位确认清仓 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1411 | Auction Deviation Threshold Executor 竞价偏离阈值执行器 | 竞价偏离阈值→挂单卖出+MA反弹失败卖出 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1412 | Sell Priority Scheduler 卖出优先级调度器 | 优先级评分函数+优先级队列+滑点控制 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1413 | Live/Simulation Switcher 实盘/模拟切换器 | 实盘与模拟盘一键切换+状态同步+资金隔离 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1414 | Performance Monitor 性能监控器 | 执行成功率+延迟+可用性3维监控+SLA告警 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1415 | Blueprint Implementer 蓝图实现器 | EXEC.001订单生成+执行+状态机+路由+报告 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1416 | Conditional Order Manager 条件订单管理器 | 条件订单(OCO/OTO)+父子订单+订单簿 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1417 | Partial Fill Processor 部分成交处理器 | 部分成交状态更新与后续处理 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1418 | Execution Aggregate Root Manager 执行聚合根管理器 | Order/Position聚合根生命周期管理 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1419 | Execution Domain Factory Method 执行域工厂方法 | Order/Position复杂聚合根创建工厂 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1420 | Intraday Position Reconciler 盘中持仓对账器 | 每5分钟与miniQMT持仓查询自动对账 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1421 | Order Execution Saga Orchestrator 下单执行Saga编排器 | 编排式Saga六步+补偿幂等+≤5s超时硬约束 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1422 | miniQMT Trading Channel Manager miniQMT交易通道管理器 | xtquant接口封装+连接认证+指令签名+会话超时 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1424 | RL Optimal Executor RL最优执行器 | DQN/PPO增强Almgren-Chriss+学习非线性微观结构 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1425 | Microstructure Modeler 微观结构建模器 | VPIN订单流毒性检测+LOB动力学+做市商推断 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2114 | Timer Agent 择时Agent | 战术层择时Agent买卖点择时信号触发判定 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2116 | Executor Agent 执行Agent | 执行层执行Agent订单提交成交确认订单状态跟踪 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-2122 | miniQMT Trading Channel miniQMT交易通道 | miniQMT交易通道唯一下单出口 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2144 | Timing Decision 择时决策 | 择时Agent技能择时决策ACTIVE | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2145 | Trigger Evaluation 触发评估 | 择时Agent技能触发评估ACTIVE | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2148 | Day Trade Execution 做T执行 | 做T Agent技能做T执行ACTIVE | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2149 | Day Trade PnL Estimate 做T盈亏预估 | 做T Agent技能做T盈亏预估ACTIVE | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2150 | Order Submission 订单提交 | 执行Agent技能订单提交ACTIVE | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2151 | Order Tracking 订单跟踪 | 执行Agent技能订单跟踪ACTIVE | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2347 | P2-Medium P2中优先级指令 | P2-中交易指令信号触发战术层按队列顺序处理可被P0/P1中断 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2584 | C-002 Execution Domain 执行域 | 执行域订单执行+Wash Trade检查 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2990 | Order Generation 订单生成 | 订单生成 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3449 | Trade Execution Core 交易执行核心 | / MOD-L06-001 / Trade Execution Core / 🔧部分实现 / risk_validation_bridge / §3.2 / | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3905 | 下单执行 下单执行 Execution | Hot平面5ms延迟预算miniQMT API | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4120 | Trading Pipeline Process 交易流水线进程 | A1迁移概念级进程P0 因子增量计算信号生成风控监控做T触发执行算法不可崩溃 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4167 | P3 Heartbeat Loss Alert P3心跳丢失告警 | / AD-001b / P3心跳丢失 / rate(process_heartbeat_total{process='trading_core'}[10s])==0 持续10s / AL-P1(最高紧急) / | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-4168 | Simulation Broker 模拟Broker | / l06_trade_execution/adapters/simulation_broker.py / EX-CORE-03+04 / ❌Position Tracker耦合在内 / | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4169 | OMS Risk Engine OMS风险引擎 | 场内代码对标EX-CORE-07归属应为D-EX-CORE | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4170 | Trading Kill Switch 交易Kill Switch | 场内代码对标EX-CORE-02执行逻辑应在EX-CORE | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4258 | l06-oms C轨L06层订单管理系统子模块 | C轨L06层子模块映射l06-oms订单管理系统 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4259 | l06-pre-trade C轨L06层Pre-Trade子模块 | / l06-pre-trade / D-EX-CORE-03 + D-EX-CORE-07 / 交易前风控与适配 / | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4260 | ExecutionModuleBase Code Generation Base Class ExecutionModuleBase代码生成基类 | > LLM生成执行模块代码必须: 继承ExecutionModuleBase+所有订单操作通过OrderManager+所有持仓写入通过PositionTracker+所有Broker调用通过ExecutionEngine(INV-005) | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5050 | Nanosecond Critical Path Analyzer 纳秒级关键路径分析器 | / 纳秒级关键路径分析器 / Python运行时+miniQMT 3秒Tick / FPGA/内核旁路+交易通道延迟<1ms / | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5054 | Trading Channel Auto Recovery 交易通道熔断自动恢复 | HB-SEC-06+HB-SEC-07双重锁定 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5080 | Emergency Execution 紧急执行 | 风控强制卖出链——EX-CORE-02紧急执行 | D_EX_CORE | harvest待评估（likely_implemented） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0068 | 做T日内套利 | D_EX_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0073 | Trade Execution 交易执行与订单管理 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0075 | Execution Quality Analysis (TCA) 执行质量分析 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0077 | Execution Ops Auto-Optimization 执行运营自优化 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0581 | Execution Core 执行核心 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0676 | Position Tracker 持仓追踪 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0677 | Execution Auditor 执行审计 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0678 | 多契约生产适配器 Multi-contract Production Adapter | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0725 | 当前持仓物化视图 Current Position View | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0727 | 当日交易物化视图 Today's Trade View | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0755 | Order Manager 订单管理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0756 | Execution Engine 执行引擎 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0757 | Fill Tracker 成交跟踪器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1402 | Fill Processor 成交处理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1403 | Order State Machine 订单状态机 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1404 | Execution TCA 执行TCA | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1405 | Order Splitter 订单拆分器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1406 | Deployment Consistency Manager 部署一致性管理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1407 | Pre-Execution Checker 执行前检查器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1408 | Parameterized Stop Loss/Take Profit Executor 参数化止损止盈执行器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1409 | Parameterized Batch Executor 参数化分批执行器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1410 | Parameterized Batch Take Profit Executor 参数化分批止盈执行器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1411 | Auction Deviation Threshold Executor 竞价偏离阈值执行器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1412 | Sell Priority Scheduler 卖出优先级调度器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1413 | Live/Simulation Switcher 实盘/模拟切换器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1414 | Performance Monitor 性能监控器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1415 | Blueprint Implementer 蓝图实现器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1416 | Conditional Order Manager 条件订单管理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1417 | Partial Fill Processor 部分成交处理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1418 | Execution Aggregate Root Manager 执行聚合根管理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1419 | Execution Domain Factory Method 执行域工厂方法 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1420 | Intraday Position Reconciler 盘中持仓对账器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1421 | Order Execution Saga Orchestrator 下单执行Saga编排器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1422 | miniQMT Trading Channel Manager miniQMT交易通道管理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1424 | RL Optimal Executor RL最优执行器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1425 | Microstructure Modeler 微观结构建模器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2114 | Timer Agent 择时Agent | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2116 | Executor Agent 执行Agent | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-2122 | miniQMT Trading Channel miniQMT交易通道 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2144 | Timing Decision 择时决策 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2145 | Trigger Evaluation 触发评估 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2148 | Day Trade Execution 做T执行 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2149 | Day Trade PnL Estimate 做T盈亏预估 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2150 | Order Submission 订单提交 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2151 | Order Tracking 订单跟踪 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2347 | P2-Medium P2中优先级指令 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2584 | C-002 Execution Domain 执行域 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2990 | Order Generation 订单生成 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3449 | Trade Execution Core 交易执行核心 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3905 | 下单执行 下单执行 Execution | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4120 | Trading Pipeline Process 交易流水线进程 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4167 | P3 Heartbeat Loss Alert P3心跳丢失告警 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-4168 | Simulation Broker 模拟Broker | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4169 | OMS Risk Engine OMS风险引擎 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4170 | Trading Kill Switch 交易Kill Switch | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4258 | l06-oms C轨L06层订单管理系统子模块 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4259 | l06-pre-trade C轨L06层Pre-Trade子模块 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4260 | ExecutionModuleBase Code Generation Base Class ExecutionModuleBase代码生成基类 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5050 | Nanosecond Critical Path Analyzer 纳秒级关键路径分析器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5054 | Trading Channel Auto Recovery 交易通道熔断自动恢复 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5080 | Emergency Execution 紧急执行 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2027-01-31 | half_yearly | CAND-EX-001 | Futu/IB Broker Adapters / 富途IB券商适配器 | D_EX_CORE | 延后（deferred） | 首次登记,待非MiniQMT渠道需求或实盘扩展时重新评估 |
| 2027-01-31 | half_yearly | CAND-EX-002 | Multi-threaded Order Processing / 多线程订单处理 | D_EX_CORE | 延后（deferred） | 首次登记,待并发订单>10或提交延迟>100ms时重新评估 |
