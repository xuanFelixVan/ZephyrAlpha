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

> 本域候选 **72** 条（原有 11 + harvest 61）。
> harvest 去重四态: likely_new=12 / likely_implemented=34 / likely_planned=14 / uncertain=1

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 一问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0016 | 做T日内套利 | C 012：做T日内套利 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0021 | Trade Execution 交易执行与订单管理 | C 002：交易执行与订单管理 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0023 | Execution Quality Analysis (TCA) 执行质量分析 | C 046：执行质量分析（TCA, Transaction Cost Analysis） | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0025 | Execution Ops Auto-Optimization 执行运营自优化 | C 026：执行运营自优化 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0529 | Execution Core 执行核心 | / L2→L3 / momentum_buy_signal / risk_budget_alloc / buy_decision / D-PF-CORE / CTR-005 / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0624 | Position Tracker 持仓追踪 | / D-EX-CORE-04 / Position Tracker / 持仓追踪+快照+DuckDB持仓历史+SQLite最新快照缓存+CTR-006 PositionSnapshot / ✅能建。当前持仓数据已在DuckDB中管理，增量改 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0625 | Execution Auditor 执行审计 | 审计日志记录器+合规规则引擎+执行质量评分器 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0626 | 多契约生产适配器 Multi-contract Production Adapter | / D-EX-CORE-55 / 多契约生产适配器 / CTR-004/005/006三个契约Schema定义+版本演进+消费者注册 / ✅能建。与§16 #3 Data Contract对齐，在SQLite中增加contract_regi | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0674 | 当前持仓物化视图 Current Position View | / 当前持仓 / position:{symbol} / Hash / 实时 / <5ms / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0676 | 当日交易物化视图 Today's Trade View | / 当日交易 / trade:today:{symbol} / List / 实时 / <5ms / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0704 | Order Manager 订单管理器 | 订单管理器订单创建状态机NEW SENT FILLED CANCELLED REJECTED订单路由 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0705 | Execution Engine 执行引擎 | 执行引擎订单执行执行算法执行质量评估滑点控制执行报告 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0706 | Fill Tracker 成交跟踪器 | 成交跟踪器成交确认成交分析成交归因成交统计异常成交检测 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1379 | Fill Processor 成交处理器 | 成交解析器+部分成交聚合器+成交归因器+费用计算器 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1380 | Order State Machine 订单状态机 | 7状态机+持久化+事件发射 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1381 | Execution TCA 执行TCA | IS计算器+延迟成本+机会成本+市场冲击归因+三阶段TCA | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1382 | Order Splitter 订单拆分器 | 拆分策略选择器+子订单生成器+Almgren-Chriss最优拆分 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1383 | Deployment Consistency Manager 部署一致性管理器 | 配置版本管理器+一致性检查器+灰度控制器+回滚管理器 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1384 | Pre-Execution Checker 执行前检查器 | 订单合规校验+市场状态检查+Pre-Trade主链6项 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1385 | Parameterized Stop Loss/Take Profit Executor 参数化止损止盈执行器 | 固定比例止损+MA破位止损+封流比阈值止盈等 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1386 | Parameterized Batch Executor 参数化分批执行器 | 分批比例配置+条件触发+进度追踪+失败回滚 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1387 | Parameterized Batch Take Profit Executor 参数化分批止盈执行器 | 触发止盈后分批卖出+MA破位确认清仓 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1388 | Auction Deviation Threshold Executor 竞价偏离阈值执行器 | 竞价偏离阈值→挂单卖出+MA反弹失败卖出 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1389 | Sell Priority Scheduler 卖出优先级调度器 | 优先级评分函数+优先级队列+滑点控制 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1390 | Live/Simulation Switcher 实盘/模拟切换器 | 实盘与模拟盘一键切换+状态同步+资金隔离 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1391 | Performance Monitor 性能监控器 | 执行成功率+延迟+可用性3维监控+SLA告警 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1392 | Blueprint Implementer 蓝图实现器 | EXEC.001订单生成+执行+状态机+路由+报告 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1393 | Conditional Order Manager 条件订单管理器 | 条件订单(OCO/OTO)+父子订单+订单簿 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1394 | Partial Fill Processor 部分成交处理器 | 部分成交状态更新与后续处理 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1395 | Execution Aggregate Root Manager 执行聚合根管理器 | Order/Position聚合根生命周期管理 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1396 | Execution Domain Factory Method 执行域工厂方法 | Order/Position复杂聚合根创建工厂 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1397 | Intraday Position Reconciler 盘中持仓对账器 | 每5分钟与miniQMT持仓查询自动对账 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1398 | Order Execution Saga Orchestrator 下单执行Saga编排器 | 编排式Saga六步+补偿幂等+≤5s超时硬约束 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1399 | miniQMT Trading Channel Manager miniQMT交易通道管理器 | xtquant接口封装+连接认证+指令签名+会话超时 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1401 | RL Optimal Executor RL最优执行器 | DQN/PPO增强Almgren-Chriss+学习非线性微观结构 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1402 | Microstructure Modeler 微观结构建模器 | VPIN订单流毒性检测+LOB动力学+做市商推断 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2094 | Timer Agent 择时Agent | 战术层择时Agent买卖点择时信号触发判定 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2096 | Executor Agent 执行Agent | 执行层执行Agent订单提交成交确认订单状态跟踪 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2102 | miniQMT Trading Channel miniQMT交易通道 | miniQMT交易通道唯一下单出口 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2124 | Timing Decision 择时决策 | 择时Agent技能择时决策ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2125 | Trigger Evaluation 触发评估 | 择时Agent技能触发评估ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2128 | Day Trade Execution 做T执行 | 做T Agent技能做T执行ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2129 | Day Trade PnL Estimate 做T盈亏预估 | 做T Agent技能做T盈亏预估ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2130 | Order Submission 订单提交 | 执行Agent技能订单提交ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2131 | Order Tracking 订单跟踪 | 执行Agent技能订单跟踪ACTIVE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2327 | P2-Medium P2中优先级指令 | P2-中交易指令信号触发战术层按队列顺序处理可被P0/P1中断 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2564 | C-002 Execution Domain 执行域 | 执行域订单执行+Wash Trade检查 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2970 | Order Generation 订单生成 | 订单生成 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3429 | Trade Execution Core 交易执行核心 | / MOD-L06-001 / Trade Execution Core / 🔧部分实现 / risk_validation_bridge / §3.2 / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3885 | 下单执行 下单执行 Execution | Hot平面5ms延迟预算miniQMT API | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4119 | Trading Pipeline Process 交易流水线进程 | A1迁移概念级进程P0 因子增量计算信号生成风控监控做T触发执行算法不可崩溃 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4166 | P3 Heartbeat Loss Alert P3心跳丢失告警 | / AD-001b / P3心跳丢失 / rate(process_heartbeat_total{process='trading_core'}[10s])==0 持续10s / AL-P1(最高紧急) / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4167 | Simulation Broker 模拟Broker | / l06_trade_execution/adapters/simulation_broker.py / EX-CORE-03+04 / ❌Position Tracker耦合在内 / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4168 | OMS Risk Engine OMS风险引擎 | 场内代码对标EX-CORE-07归属应为D-EX-CORE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4169 | Trading Kill Switch 交易Kill Switch | 场内代码对标EX-CORE-02执行逻辑应在EX-CORE | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4257 | l06-oms C轨L06层订单管理系统子模块 | C轨L06层子模块映射l06-oms订单管理系统 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4258 | l06-pre-trade C轨L06层Pre-Trade子模块 | / l06-pre-trade / D-EX-CORE-03 + D-EX-CORE-07 / 交易前风控与适配 / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-4259 | ExecutionModuleBase Code Generation Base Class ExecutionModuleBase代码生成基类 | > LLM生成执行模块代码必须: 继承ExecutionModuleBase+所有订单操作通过OrderManager+所有持仓写入通过PositionTracker+所有Broker调用通过ExecutionEngine(INV-005) | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5050 | Nanosecond Critical Path Analyzer 纳秒级关键路径分析器 | / 纳秒级关键路径分析器 / Python运行时+miniQMT 3秒Tick / FPGA/内核旁路+交易通道延迟<1ms / | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5054 | Trading Channel Auto Recovery 交易通道熔断自动恢复 | HB-SEC-06+HB-SEC-07双重锁定 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5080 | Emergency Execution 紧急执行 | 风控强制卖出链——EX-CORE-02紧急执行 | D_EX_CORE | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-EX-001 | Futu/IB Broker Adapters / 富途IB券商适配器 | 实盘需要非MiniQMT渠道(如港股/美股/期货)下单时,无对应券商适配器 | D_EX_CORE | 延后（deferred） | 一问通过 | P1 | 实盘扩展到港股/美股/期货市场(MiniQMT仅覆盖A股) 等3条 | 2027-01-31 |
| CAND-EX-002 | Multi-threaded Order Processing / 多线程订单处理 | 高频/批量下单时单线程订单处理成为瓶颈(并发>10) | D_EX_CORE | 延后（deferred） | 一问通过 | P1 | 并发订单数持续>10 等3条 | 2027-01-31 |
| CAND-EX-003 | Redis幂等性存储 / Redis Idempotency Store | 下单幂等性(INV-007),防重复扣减/重复创建 | D_EX_CORE | 否决（rejected） | q1 已实现/重复 | P3 | MOD-INF-016 出现跨进程去重缺口且 SQLite 后端不足以支撑 | 2027-08-05 |
| CAND-EX-004 | 蓝图Implementer / Blueprint Implementer | (无具体业务问题——自我指涉元概念) | D_EX_CORE | 否决（rejected） | 一问通过 | P3 | — | 2027-08-05 |
| CAND-EX-005 | 执行域值对象 / Execution Value Objects | (无——Pydantic BaseModel原生提供值对象语义) | D_EX_CORE | 否决（rejected） | q1 已实现/重复 | P3 | — | 2027-08-05 |
| CAND-EX-006 | 执行域工厂 / Execution Factory | (无——aggregate_root_manager已是Facade构建入口) | D_EX_CORE | 否决（rejected） | q1 已实现/重复 | P3 | — | 2027-08-05 |
| CAND-EX004-001 | MOD-EX-004 redis幂等性(重复幽灵节点) | (已解决)订单幂等性去重已由shared/infra/idempotency.py承接 | D_EX_CORE | 否决（rejected） | q1 已实现/重复 | P2 | — | 2027-08-05 |
| CAND-EX015-001 | MOD-EX-015 execution_report(重复幽灵节点) | (已解决)执行报告已由MOD-INF-016正确承接,3处实现(trading/shared/contracts) | D_EX_CORE | 否决（rejected） | q1 已实现/重复 | P2 | — | 2027-08-04 |
| CAND-EX037-001 | MOD-EX-037 蓝图Implementer(概念错误节点) | (无真实痛点)D_EX_CORE做订单执行,不存在把蓝图转代码的需求 | D_EX_CORE | 否决（rejected） | q1 已实现/重复 | P2 | — | 2027-08-05 |
| CAND-EX051-001 | MOD-EX-051 值对象(分散实现幽灵节点) | (已解决)值对象已分散在trading_contracts的dataclass实现 | D_EX_CORE | 否决（rejected） | q1 已实现/重复 | P2 | — | 2027-08-05 |
| CAND-EX052-001 | MOD-EX-052 工厂(分散实现幽灵节点) | (已解决)工厂模式已分散在shared/contracts/core/factories.py和trading_contracts/factories.py实现 | D_EX_CORE | 否决（rejected） | q1 已实现/重复 | P2 | — | 2027-08-05 |

## 按一问卡点分组（为什么没开发）

> 一问标准（裁定 2026-08-04）：仅 q1 已实现/重复。q1「是」即不进 depgraph 设计态，登记在候选库。原 q2/q3/q4 灰度已废。

### q1 已实现/重复（8 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-EX-003 | Redis幂等性存储 / Redis Idempotency Store | 下单幂等性(INV-007),防重复扣减/重复创建 | D_EX_CORE | IdempotencyStore/SQLiteIdempotencyStore/build_idempotency_key 已production;repository_interface INVARIANT save幂等;idempotency_key 已内联5处 | 维持 MOD-INF-016 + repository_interface save幂等。代价:无,已完整覆盖 |
| CAND-EX-005 | 执行域值对象 / Execution Value Objects | (无——Pydantic BaseModel原生提供值对象语义) | D_EX_CORE | 项目全局强制Pydantic V2;值对象语义原生支持,无需独立模块 | 维持 shared.contracts Pydantic 模型。代价:无 |
| CAND-EX-006 | 执行域工厂 / Execution Factory | (无——aggregate_root_manager已是Facade构建入口) | D_EX_CORE | aggregate_root_manager已承担Facade/构建入口('把订单仓储/成交处理/持仓跟踪拧成一股绳');Python用__init__/classmethod构造 | 维持 aggregate_root_manager。代价:无 |
| CAND-EX004-001 | MOD-EX-004 redis幂等性(重复幽灵节点) | (已解决)订单幂等性去重已由shared/infra/idempotency.py承接 | D_EX_CORE | shared/infra/idempotency.py 291行,RedisIdempotencyGateway类+is_already_processed/handle_execution方法,stable,有测试tests/infrastructure/test_infra_idempotency.py.幂等机制已上移至基础设施层 | MOD-INF-016(节点8640073,src/zephyr/shared/infra/idempotency.py,stable,291行) |
| CAND-EX015-001 | MOD-EX-015 execution_report(重复幽灵节点) | (已解决)执行报告已由MOD-INF-016正确承接,3处实现(trading/shared/contracts) | D_EX_CORE | execution_report已由MOD-INF-016实现,3处:trading/trading_contracts/execution/execution_report.py(stable)+shared/contracts/execution/execution_report.py(generated)+shared/contracts/execution_report.py(generated) | MOD-INF-016(节点8616268,src/zephyr/trading/trading_contracts/execution/execution_report.py,stable) |
| CAND-EX037-001 | MOD-EX-037 蓝图Implementer(概念错误节点) | (无真实痛点)D_EX_CORE做订单执行,不存在把蓝图转代码的需求 | D_EX_CORE | rg全项目搜blueprint_implementer/BlueprintImplementer 0结果,execute_blueprint/implement_blueprint动词 0结果。该功能无任何实现也无任何消费者,属概念错误非功能缺失 | 无(D_EX_CORE不需要蓝图转代码功能) |
| CAND-EX051-001 | MOD-EX-051 值对象(分散实现幽灵节点) | (已解决)值对象已分散在trading_contracts的dataclass实现 | D_EX_CORE | trading_contracts/order.py有OrderId/Order等dataclass(frozen=True不可变值对象),shared/contracts/下亦有大量dataclass/Pydantic BaseModel.值对象模式已分散在各contracts内联实现,无集中模块需求 | trading_contracts/order.py(OrderId/Order等)+shared/contracts/下dataclass(分散实现) |
| CAND-EX052-001 | MOD-EX-052 工厂(分散实现幽灵节点) | (已解决)工厂模式已分散在shared/contracts/core/factories.py和trading_contracts/factories.py实现 | D_EX_CORE | shared/contracts/core/factories.py 248行有OrderFactory/ExecutionReportFactory,trading_contracts/factories.py 252行有ModelFactory等.工厂模式已分散在各模块内联实现,module_onboarding_scanner.py亦有factory_create逻辑.无集中D_EX_CORE工厂需求 | shared/contracts/core/factories.py(248行,OrderFactory/ExecutionReportFactory)+trading_contracts/factories.py(252行,分散实现) |

### 待评估（61 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0016 | 做T日内套利 | C 012：做T日内套利 | D_EX_CORE | harvest待评估（uncertain） |  |
| CAND-HARVEST-0021 | Trade Execution 交易执行与订单管理 | C 002：交易执行与订单管理 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0023 | Execution Quality Analysis (TCA) 执行质量分析 | C 046：执行质量分析（TCA, Transaction Cost Analysis） | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0025 | Execution Ops Auto-Optimization 执行运营自优化 | C 026：执行运营自优化 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0529 | Execution Core 执行核心 | / L2→L3 / momentum_buy_signal / risk_budget_alloc / buy_decision / D-PF-CORE / CTR-005 / | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0624 | Position Tracker 持仓追踪 | / D-EX-CORE-04 / Position Tracker / 持仓追踪+快照+DuckDB持仓历史+SQLite最新快照缓存+CTR-006 PositionSnapshot / ✅能建。当前持仓数据已在DuckDB中管理，增量改 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0625 | Execution Auditor 执行审计 | 审计日志记录器+合规规则引擎+执行质量评分器 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0626 | 多契约生产适配器 Multi-contract Production Adapter | / D-EX-CORE-55 / 多契约生产适配器 / CTR-004/005/006三个契约Schema定义+版本演进+消费者注册 / ✅能建。与§16 #3 Data Contract对齐，在SQLite中增加contract_regi | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0674 | 当前持仓物化视图 Current Position View | / 当前持仓 / position:{symbol} / Hash / 实时 / <5ms / | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0676 | 当日交易物化视图 Today's Trade View | / 当日交易 / trade:today:{symbol} / List / 实时 / <5ms / | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-0704 | Order Manager 订单管理器 | 订单管理器订单创建状态机NEW SENT FILLED CANCELLED REJECTED订单路由 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0705 | Execution Engine 执行引擎 | 执行引擎订单执行执行算法执行质量评估滑点控制执行报告 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0706 | Fill Tracker 成交跟踪器 | 成交跟踪器成交确认成交分析成交归因成交统计异常成交检测 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1379 | Fill Processor 成交处理器 | 成交解析器+部分成交聚合器+成交归因器+费用计算器 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1380 | Order State Machine 订单状态机 | 7状态机+持久化+事件发射 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1381 | Execution TCA 执行TCA | IS计算器+延迟成本+机会成本+市场冲击归因+三阶段TCA | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1382 | Order Splitter 订单拆分器 | 拆分策略选择器+子订单生成器+Almgren-Chriss最优拆分 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1383 | Deployment Consistency Manager 部署一致性管理器 | 配置版本管理器+一致性检查器+灰度控制器+回滚管理器 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1384 | Pre-Execution Checker 执行前检查器 | 订单合规校验+市场状态检查+Pre-Trade主链6项 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1385 | Parameterized Stop Loss/Take Profit Executor 参数化止损止盈执行器 | 固定比例止损+MA破位止损+封流比阈值止盈等 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1386 | Parameterized Batch Executor 参数化分批执行器 | 分批比例配置+条件触发+进度追踪+失败回滚 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1387 | Parameterized Batch Take Profit Executor 参数化分批止盈执行器 | 触发止盈后分批卖出+MA破位确认清仓 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1388 | Auction Deviation Threshold Executor 竞价偏离阈值执行器 | 竞价偏离阈值→挂单卖出+MA反弹失败卖出 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1389 | Sell Priority Scheduler 卖出优先级调度器 | 优先级评分函数+优先级队列+滑点控制 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1390 | Live/Simulation Switcher 实盘/模拟切换器 | 实盘与模拟盘一键切换+状态同步+资金隔离 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1391 | Performance Monitor 性能监控器 | 执行成功率+延迟+可用性3维监控+SLA告警 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1392 | Blueprint Implementer 蓝图实现器 | EXEC.001订单生成+执行+状态机+路由+报告 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-1393 | Conditional Order Manager 条件订单管理器 | 条件订单(OCO/OTO)+父子订单+订单簿 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1394 | Partial Fill Processor 部分成交处理器 | 部分成交状态更新与后续处理 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1395 | Execution Aggregate Root Manager 执行聚合根管理器 | Order/Position聚合根生命周期管理 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1396 | Execution Domain Factory Method 执行域工厂方法 | Order/Position复杂聚合根创建工厂 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1397 | Intraday Position Reconciler 盘中持仓对账器 | 每5分钟与miniQMT持仓查询自动对账 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1398 | Order Execution Saga Orchestrator 下单执行Saga编排器 | 编排式Saga六步+补偿幂等+≤5s超时硬约束 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1399 | miniQMT Trading Channel Manager miniQMT交易通道管理器 | xtquant接口封装+连接认证+指令签名+会话超时 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1401 | RL Optimal Executor RL最优执行器 | DQN/PPO增强Almgren-Chriss+学习非线性微观结构 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-1402 | Microstructure Modeler 微观结构建模器 | VPIN订单流毒性检测+LOB动力学+做市商推断 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2094 | Timer Agent 择时Agent | 战术层择时Agent买卖点择时信号触发判定 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2096 | Executor Agent 执行Agent | 执行层执行Agent订单提交成交确认订单状态跟踪 | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-2102 | miniQMT Trading Channel miniQMT交易通道 | miniQMT交易通道唯一下单出口 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2124 | Timing Decision 择时决策 | 择时Agent技能择时决策ACTIVE | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2125 | Trigger Evaluation 触发评估 | 择时Agent技能触发评估ACTIVE | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2128 | Day Trade Execution 做T执行 | 做T Agent技能做T执行ACTIVE | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2129 | Day Trade PnL Estimate 做T盈亏预估 | 做T Agent技能做T盈亏预估ACTIVE | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2130 | Order Submission 订单提交 | 执行Agent技能订单提交ACTIVE | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2131 | Order Tracking 订单跟踪 | 执行Agent技能订单跟踪ACTIVE | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2327 | P2-Medium P2中优先级指令 | P2-中交易指令信号触发战术层按队列顺序处理可被P0/P1中断 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-2564 | C-002 Execution Domain 执行域 | 执行域订单执行+Wash Trade检查 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2970 | Order Generation 订单生成 | 订单生成 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3429 | Trade Execution Core 交易执行核心 | / MOD-L06-001 / Trade Execution Core / 🔧部分实现 / risk_validation_bridge / §3.2 / | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3885 | 下单执行 下单执行 Execution | Hot平面5ms延迟预算miniQMT API | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4119 | Trading Pipeline Process 交易流水线进程 | A1迁移概念级进程P0 因子增量计算信号生成风控监控做T触发执行算法不可崩溃 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4166 | P3 Heartbeat Loss Alert P3心跳丢失告警 | / AD-001b / P3心跳丢失 / rate(process_heartbeat_total{process='trading_core'}[10s])==0 持续10s / AL-P1(最高紧急) / | D_EX_CORE | harvest待评估（likely_planned） |  |
| CAND-HARVEST-4167 | Simulation Broker 模拟Broker | / l06_trade_execution/adapters/simulation_broker.py / EX-CORE-03+04 / ❌Position Tracker耦合在内 / | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4168 | OMS Risk Engine OMS风险引擎 | 场内代码对标EX-CORE-07归属应为D-EX-CORE | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4169 | Trading Kill Switch 交易Kill Switch | 场内代码对标EX-CORE-02执行逻辑应在EX-CORE | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-4257 | l06-oms C轨L06层订单管理系统子模块 | C轨L06层子模块映射l06-oms订单管理系统 | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4258 | l06-pre-trade C轨L06层Pre-Trade子模块 | / l06-pre-trade / D-EX-CORE-03 + D-EX-CORE-07 / 交易前风控与适配 / | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-4259 | ExecutionModuleBase Code Generation Base Class ExecutionModuleBase代码生成基类 | > LLM生成执行模块代码必须: 继承ExecutionModuleBase+所有订单操作通过OrderManager+所有持仓写入通过PositionTracker+所有Broker调用通过ExecutionEngine(INV-005) | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5050 | Nanosecond Critical Path Analyzer 纳秒级关键路径分析器 | / 纳秒级关键路径分析器 / Python运行时+miniQMT 3秒Tick / FPGA/内核旁路+交易通道延迟<1ms / | D_EX_CORE | harvest待评估（likely_new） |  |
| CAND-HARVEST-5054 | Trading Channel Auto Recovery 交易通道熔断自动恢复 | HB-SEC-06+HB-SEC-07双重锁定 | D_EX_CORE | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5080 | Emergency Execution 紧急执行 | 风控强制卖出链——EX-CORE-02紧急执行 | D_EX_CORE | harvest待评估（likely_implemented） |  |

### 一问通过（3 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-EX-001 | Futu/IB Broker Adapters / 富途IB券商适配器 | 实盘需要非MiniQMT渠道(如港股/美股/期货)下单时,无对应券商适配器 | D_EX_CORE | 首次登记,待非MiniQMT渠道需求或实盘扩展时重新评估 | MiniQMT渠道(已施工,覆盖A股实盘)。代价:无法接入港股/美股/期货 |
| CAND-EX-002 | Multi-threaded Order Processing / 多线程订单处理 | 高频/批量下单时单线程订单处理成为瓶颈(并发>10) | D_EX_CORE | 首次登记,待并发订单>10或提交延迟>100ms时重新评估 | 单线程顺序提交(当前实现)。代价:并发>10时延迟增加 |
| CAND-EX-004 | 蓝图Implementer / Blueprint Implementer | (无具体业务问题——自我指涉元概念) | D_EX_CORE | rejected,q2无驱动(自我指涉元模块)。除非出现明确的'蓝图→代码'自动化需求且无现有工具,否则不再评估 | 不实现。代价:无,无任何模块需要它 |

## 复查时间表

> 按 next_review_date 升序。复查时重新过一问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0016 | 做T日内套利 | D_EX_CORE | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-0021 | Trade Execution 交易执行与订单管理 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0023 | Execution Quality Analysis (TCA) 执行质量分析 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0025 | Execution Ops Auto-Optimization 执行运营自优化 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0529 | Execution Core 执行核心 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0624 | Position Tracker 持仓追踪 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0625 | Execution Auditor 执行审计 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0626 | 多契约生产适配器 Multi-contract Production Adapter | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0674 | 当前持仓物化视图 Current Position View | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0676 | 当日交易物化视图 Today's Trade View | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0704 | Order Manager 订单管理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0705 | Execution Engine 执行引擎 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0706 | Fill Tracker 成交跟踪器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1379 | Fill Processor 成交处理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1380 | Order State Machine 订单状态机 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1381 | Execution TCA 执行TCA | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1382 | Order Splitter 订单拆分器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1383 | Deployment Consistency Manager 部署一致性管理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1384 | Pre-Execution Checker 执行前检查器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1385 | Parameterized Stop Loss/Take Profit Executor 参数化止损止盈执行器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1386 | Parameterized Batch Executor 参数化分批执行器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1387 | Parameterized Batch Take Profit Executor 参数化分批止盈执行器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1388 | Auction Deviation Threshold Executor 竞价偏离阈值执行器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1389 | Sell Priority Scheduler 卖出优先级调度器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1390 | Live/Simulation Switcher 实盘/模拟切换器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1391 | Performance Monitor 性能监控器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1392 | Blueprint Implementer 蓝图实现器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-1393 | Conditional Order Manager 条件订单管理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1394 | Partial Fill Processor 部分成交处理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1395 | Execution Aggregate Root Manager 执行聚合根管理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1396 | Execution Domain Factory Method 执行域工厂方法 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1397 | Intraday Position Reconciler 盘中持仓对账器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1398 | Order Execution Saga Orchestrator 下单执行Saga编排器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1399 | miniQMT Trading Channel Manager miniQMT交易通道管理器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1401 | RL Optimal Executor RL最优执行器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-1402 | Microstructure Modeler 微观结构建模器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2094 | Timer Agent 择时Agent | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2096 | Executor Agent 执行Agent | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-2102 | miniQMT Trading Channel miniQMT交易通道 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2124 | Timing Decision 择时决策 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2125 | Trigger Evaluation 触发评估 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2128 | Day Trade Execution 做T执行 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2129 | Day Trade PnL Estimate 做T盈亏预估 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2130 | Order Submission 订单提交 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2131 | Order Tracking 订单跟踪 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2327 | P2-Medium P2中优先级指令 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2564 | C-002 Execution Domain 执行域 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2970 | Order Generation 订单生成 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3429 | Trade Execution Core 交易执行核心 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3885 | 下单执行 下单执行 Execution | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4119 | Trading Pipeline Process 交易流水线进程 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4166 | P3 Heartbeat Loss Alert P3心跳丢失告警 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-4167 | Simulation Broker 模拟Broker | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4168 | OMS Risk Engine OMS风险引擎 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4169 | Trading Kill Switch 交易Kill Switch | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-4257 | l06-oms C轨L06层订单管理系统子模块 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4258 | l06-pre-trade C轨L06层Pre-Trade子模块 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-4259 | ExecutionModuleBase Code Generation Base Class ExecutionModuleBase代码生成基类 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5050 | Nanosecond Critical Path Analyzer 纳秒级关键路径分析器 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5054 | Trading Channel Auto Recovery 交易通道熔断自动恢复 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5080 | Emergency Execution 紧急执行 | D_EX_CORE | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2027-01-31 | half_yearly | CAND-EX-001 | Futu/IB Broker Adapters / 富途IB券商适配器 | D_EX_CORE | 延后（deferred） | 首次登记,待非MiniQMT渠道需求或实盘扩展时重新评估 |
| 2027-01-31 | half_yearly | CAND-EX-002 | Multi-threaded Order Processing / 多线程订单处理 | D_EX_CORE | 延后（deferred） | 首次登记,待并发订单>10或提交延迟>100ms时重新评估 |
| 2027-08-04 | yearly | CAND-EX015-001 | MOD-EX-015 execution_report(重复幽灵节点) | D_EX_CORE | 否决（rejected） | rejected,确认重复幽灵节点。真源execution_report=MOD-INF-016(节点8616268 trading_contracts/execution/execution_report.py stable).除非MOD-INF-016出现重大缺口,否则不再评估MOD-EX-015 |
| 2027-08-05 | yearly | CAND-EX-003 | Redis幂等性存储 / Redis Idempotency Store | D_EX_CORE | 否决（rejected） | rejected,q1已实现(MOD-INF-016)。除非 shared/infra/idempotency 出现跨进程去重缺口需Redis后端,否则不再评估 |
| 2027-08-05 | yearly | CAND-EX-004 | 蓝图Implementer / Blueprint Implementer | D_EX_CORE | 否决（rejected） | rejected,q2无驱动(自我指涉元模块)。除非出现明确的'蓝图→代码'自动化需求且无现有工具,否则不再评估 |
| 2027-08-05 | yearly | CAND-EX-005 | 执行域值对象 / Execution Value Objects | D_EX_CORE | 否决（rejected） | rejected,q1已实现(Pydantic V2强制)。除非放弃Pydantic转纯dataclass,否则不再评估 |
| 2027-08-05 | yearly | CAND-EX-006 | 执行域工厂 / Execution Factory | D_EX_CORE | 否决（rejected） | rejected,q1已实现(aggregate_root_manager)。除非aggregate_root_manager重构移除Facade职责,否则不再评估 |
| 2027-08-05 | yearly | CAND-EX004-001 | MOD-EX-004 redis幂等性(重复幽灵节点) | D_EX_CORE | 否决（rejected） | rejected,确认重复幽灵节点。幂等机制已由shared/infra/idempotency.py(MOD-INF-016)承接.文件不存在+功能已上移基础设施层.软删除防误恢复 |
| 2027-08-05 | yearly | CAND-EX037-001 | MOD-EX-037 蓝图Implementer(概念错误节点) | D_EX_CORE | 否决（rejected） | rejected,确认概念错误节点。D_EX_CORE做订单执行不需要蓝图转代码功能,全项目0引用,文件不存在=幽灵。软删除防误恢复 |
| 2027-08-05 | yearly | CAND-EX051-001 | MOD-EX-051 值对象(分散实现幽灵节点) | D_EX_CORE | 否决（rejected） | rejected,确认分散实现。值对象已分散在trading_contracts/shared/contracts的dataclass内联实现,文件不存在=幽灵。软删除防误恢复 |
| 2027-08-05 | yearly | CAND-EX052-001 | MOD-EX-052 工厂(分散实现幽灵节点) | D_EX_CORE | 否决（rejected） | rejected,确认分散实现。工厂已由shared/contracts/core/factories.py(248行)+trading_contracts/factories.py(252行)分散实现,文件不存在=幽灵。软删除防误恢复 |
