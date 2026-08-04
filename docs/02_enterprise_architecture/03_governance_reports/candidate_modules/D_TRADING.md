---
doc_type: audit_report
title: 候选模块清单 — D_TRADING
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_TRADING 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **29** 条（原有 0 + harvest 29）。
> harvest 去重四态: likely_new=8 / likely_implemented=17 / likely_planned=4

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 一问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0017 | External Instruction Monitoring 外部指令盯盘 | C 013：外部指令盯盘 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0045 | 交易运营 Trading Operations | C 017：交易运营 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0550 | Reference Data Manager 参考数据管理 | 证券主数据管理+参考数据同步+数据质量检查+变更管理+数据分发(Golden Record/MDM) | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0912 | Intraday Instant Reaction Decision Engine 盘中即时反应决策引擎 | 异常冲高回落/放量/分时M顶→短路仲裁→<3秒执行 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2862 | Global State Aggregator 全局状态聚合器 | A1四轨并行决策编排器+全局状态聚合器 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2967 | Intraday Trading Agent 日内交易代理 | 日内T+0套利+底仓管理 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-2975 | 交易域规则目录 Trading Domain Rule Catalog | 策略上线退役参数调整 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3055 | Trader 交易员角色 | 审批交易相关变更 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3953 | 延迟预算分配器 Latency Budget Allocator | 延迟预算分配器 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3954 | 延迟归因器 Latency Attributor | 延迟归因器 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3955 | 纳秒级关键路径分析器 Nanosecond Critical Path Analyzer | 约束二单机Python运行时纳秒级无意义 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5033 | Cash Management 资金与现金管理 | 现金储备+机会储备+T+1可用资金规划+逆回购+出入金调度 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5034 | Settlement Reconciliation 结算与对账 | 持仓对账+资金对账+T+1结算追踪+分红配股 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5035 | Intraday PnL Monitor 日内盈亏监控 | 实时PnL计算+盈亏告警 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5036 | Position Accounting 持仓会计 | 持仓成本计算+分红配股处理 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5037 | End-of-Day Processor 日终处理器 | 日终清算+结算追踪+数据归档 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-5060 | Gift Declaration Form Engine 礼品申报表引擎 | 标准化礼品/招待申报表单GATE-001后由微信Hub扩展 | D_TRADING | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0184 | Margin Calculator保证金计算器 | / D-TRADING-01 / Margin Calculator保证金计算器 / ❌ 不能建 / / 门禁: Long-Only无保证金交易 / | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0185 | Reconciliation Engine对账引擎 | / D-TRADING-02 / Reconciliation Engine对账引擎 / ✅ 能建 / / 交易/持仓/资金对账+异常分类+自动匹配 / | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0186 | Settlement Manager结算管理器 | / D-TRADING-03 / Settlement Manager结算管理器 / ✅ 能建 / / 结算指令+CCP接口+结算状态机 / | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0187 | EOD Processor日终处理器 | / D-TRADING-04 / EOD Processor日终处理器 / ✅ 能建 / / 价格快照+NAV计算+P&L确认+风险重估 / | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0188 | Pre-Market Checker盘前检查器 | / D-TRADING-05 / Pre-Market Checker盘前检查器 / ✅ 能建 / / 限额检查/合规预检/数据完整性/系统就绪 / | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0189 | Trading Calendar Engine交易日历引擎 | / D-TRADING-07 / Trading Calendar Engine交易日历引擎 / ✅ 能建 / / 交易所日历/假日管理/T+N计算 / | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0190 | Position Accountant持仓会计 | / D-TRADING-08 / Position Accountant持仓会计 / ✅ 能建 / / 持仓账本+成本计算+已实现/未实现P&L / | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0191 | Trading Cost Analyzer交易成本分析 | / D-TRADING-10 / Trading Cost Analyzer交易成本分析 / ✅ 能建 / / 执行落差/市场冲击/时机成本/佣金分析 / | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0192 | A-Share Pre-Market Standardized Workflow A股盘前标准化工作流 | / D-TRADING-15 / A-Share Pre-Market Standardized Workflow A股盘前标准化工作流 / ✅ 能建 / / 08:00-09:15三段式+分钟级编排+进度追踪 / | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0789 | WeChat Interaction Hub 微信交互中心 | 微信机器人双向交互 | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1201 | Treasury Manager 资金管理器 | 资金管理器 | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-1202 | Cash Flow Manager 现金流管理器 | 现金流管理器 | D_TRADING | 否决（rejected） | 待评估 | P2 | — | 2026-11-30 |

## 按一问卡点分组（为什么没开发）

> 一问标准（裁定 2026-08-04）：仅 q1 已实现/重复。q1「是」即不进 depgraph 设计态，登记在候选库。原 q2/q3/q4 灰度已废。

### 待评估（29 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0017 | External Instruction Monitoring 外部指令盯盘 | C 013：外部指令盯盘 | D_TRADING | harvest待评估（likely_new） |  |
| CAND-HARVEST-0045 | 交易运营 Trading Operations | C 017：交易运营 | D_TRADING | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0184 | Margin Calculator保证金计算器 | / D-TRADING-01 / Margin Calculator保证金计算器 / ❌ 不能建 / / 门禁: Long-Only无保证金交易 / | D_TRADING | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-0185 | Reconciliation Engine对账引擎 | / D-TRADING-02 / Reconciliation Engine对账引擎 / ✅ 能建 / / 交易/持仓/资金对账+异常分类+自动匹配 / | D_TRADING | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-0186 | Settlement Manager结算管理器 | / D-TRADING-03 / Settlement Manager结算管理器 / ✅ 能建 / / 结算指令+CCP接口+结算状态机 / | D_TRADING | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-0187 | EOD Processor日终处理器 | / D-TRADING-04 / EOD Processor日终处理器 / ✅ 能建 / / 价格快照+NAV计算+P&L确认+风险重估 / | D_TRADING | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-0188 | Pre-Market Checker盘前检查器 | / D-TRADING-05 / Pre-Market Checker盘前检查器 / ✅ 能建 / / 限额检查/合规预检/数据完整性/系统就绪 / | D_TRADING | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-0189 | Trading Calendar Engine交易日历引擎 | / D-TRADING-07 / Trading Calendar Engine交易日历引擎 / ✅ 能建 / / 交易所日历/假日管理/T+N计算 / | D_TRADING | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-0190 | Position Accountant持仓会计 | / D-TRADING-08 / Position Accountant持仓会计 / ✅ 能建 / / 持仓账本+成本计算+已实现/未实现P&L / | D_TRADING | rejected(孤儿harvest):源文档已删除+依赖图文档未定义此ID,清理D-TRADING ID空间 | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-0191 | Trading Cost Analyzer交易成本分析 | / D-TRADING-10 / Trading Cost Analyzer交易成本分析 / ✅ 能建 / / 执行落差/市场冲击/时机成本/佣金分析 / | D_TRADING | rejected(孤儿harvest):源文档已删除+依赖图文档未定义此ID,清理D-TRADING ID空间 | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-0192 | A-Share Pre-Market Standardized Workflow A股盘前标准化工作流 | / D-TRADING-15 / A-Share Pre-Market Standardized Workflow A股盘前标准化工作流 / ✅ 能建 / / 08:00-09:15三段式+分钟级编排+进度追踪 / | D_TRADING | rejected(孤儿harvest):源文档已删除+依赖图文档未定义此ID,清理D-TRADING ID空间 | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-0550 | Reference Data Manager 参考数据管理 | 证券主数据管理+参考数据同步+数据质量检查+变更管理+数据分发(Golden Record/MDM) | D_TRADING | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0789 | WeChat Interaction Hub 微信交互中心 | 微信机器人双向交互 | D_TRADING | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-0912 | Intraday Instant Reaction Decision Engine 盘中即时反应决策引擎 | 异常冲高回落/放量/分时M顶→短路仲裁→<3秒执行 | D_TRADING | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-1201 | Treasury Manager 资金管理器 | 资金管理器 | D_TRADING | rejected(孤儿harvest):源文档已删除+依赖图文档未定义此ID,清理D-TRADING ID空间 | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-1202 | Cash Flow Manager 现金流管理器 | 现金流管理器 | D_TRADING | rejected(孤儿harvest):源文档已删除+依赖图文档未定义此ID,清理D-TRADING ID空间 | 以依赖图文档(docs/_working/依赖图/18-D-TRADING-交易运营域.md)子模块定义为准 |
| CAND-HARVEST-2862 | Global State Aggregator 全局状态聚合器 | A1四轨并行决策编排器+全局状态聚合器 | D_TRADING | harvest待评估（likely_new） |  |
| CAND-HARVEST-2967 | Intraday Trading Agent 日内交易代理 | 日内T+0套利+底仓管理 | D_TRADING | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-2975 | 交易域规则目录 Trading Domain Rule Catalog | 策略上线退役参数调整 | D_TRADING | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3055 | Trader 交易员角色 | 审批交易相关变更 | D_TRADING | harvest待评估（likely_new） |  |
| CAND-HARVEST-3953 | 延迟预算分配器 Latency Budget Allocator | 延迟预算分配器 | D_TRADING | harvest待评估（likely_new） |  |
| CAND-HARVEST-3954 | 延迟归因器 Latency Attributor | 延迟归因器 | D_TRADING | harvest待评估（likely_new） |  |
| CAND-HARVEST-3955 | 纳秒级关键路径分析器 Nanosecond Critical Path Analyzer | 约束二单机Python运行时纳秒级无意义 | D_TRADING | harvest待评估（likely_new） |  |
| CAND-HARVEST-5033 | Cash Management 资金与现金管理 | 现金储备+机会储备+T+1可用资金规划+逆回购+出入金调度 | D_TRADING | harvest待评估（likely_new） |  |
| CAND-HARVEST-5034 | Settlement Reconciliation 结算与对账 | 持仓对账+资金对账+T+1结算追踪+分红配股 | D_TRADING | harvest待评估（likely_planned） |  |
| CAND-HARVEST-5035 | Intraday PnL Monitor 日内盈亏监控 | 实时PnL计算+盈亏告警 | D_TRADING | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5036 | Position Accounting 持仓会计 | 持仓成本计算+分红配股处理 | D_TRADING | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-5037 | End-of-Day Processor 日终处理器 | 日终清算+结算追踪+数据归档 | D_TRADING | harvest待评估（likely_planned） |  |
| CAND-HARVEST-5060 | Gift Declaration Form Engine 礼品申报表引擎 | 标准化礼品/招待申报表单GATE-001后由微信Hub扩展 | D_TRADING | harvest待评估（likely_implemented） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过一问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-0017 | External Instruction Monitoring 外部指令盯盘 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0045 | 交易运营 Trading Operations | D_TRADING | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0184 | Margin Calculator保证金计算器 | D_TRADING | 否决（rejected） | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) |
| 2026-11-30 | quarterly | CAND-HARVEST-0185 | Reconciliation Engine对账引擎 | D_TRADING | 否决（rejected） | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) |
| 2026-11-30 | quarterly | CAND-HARVEST-0186 | Settlement Manager结算管理器 | D_TRADING | 否决（rejected） | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) |
| 2026-11-30 | quarterly | CAND-HARVEST-0187 | EOD Processor日终处理器 | D_TRADING | 否决（rejected） | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) |
| 2026-11-30 | quarterly | CAND-HARVEST-0188 | Pre-Market Checker盘前检查器 | D_TRADING | 否决（rejected） | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) |
| 2026-11-30 | quarterly | CAND-HARVEST-0189 | Trading Calendar Engine交易日历引擎 | D_TRADING | 否决（rejected） | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) |
| 2026-11-30 | quarterly | CAND-HARVEST-0190 | Position Accountant持仓会计 | D_TRADING | 否决（rejected） | rejected(孤儿harvest):源文档已删除+依赖图文档未定义此ID,清理D-TRADING ID空间 |
| 2026-11-30 | quarterly | CAND-HARVEST-0191 | Trading Cost Analyzer交易成本分析 | D_TRADING | 否决（rejected） | rejected(孤儿harvest):源文档已删除+依赖图文档未定义此ID,清理D-TRADING ID空间 |
| 2026-11-30 | quarterly | CAND-HARVEST-0192 | A-Share Pre-Market Standardized Workflow A股盘前标准化工作流 | D_TRADING | 否决（rejected） | rejected(孤儿harvest):源文档已删除+依赖图文档未定义此ID,清理D-TRADING ID空间 |
| 2026-11-30 | quarterly | CAND-HARVEST-0550 | Reference Data Manager 参考数据管理 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0789 | WeChat Interaction Hub 微信交互中心 | D_TRADING | 否决（rejected） | rejected(真源冲突):ID复用与依赖图文档冲突+源文档已删除,以依赖图文档为权威设计意图真源(TRAE-083) |
| 2026-11-30 | quarterly | CAND-HARVEST-0912 | Intraday Instant Reaction Decision Engine 盘中即时反应决策引擎 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-1201 | Treasury Manager 资金管理器 | D_TRADING | 否决（rejected） | rejected(孤儿harvest):源文档已删除+依赖图文档未定义此ID,清理D-TRADING ID空间 |
| 2026-11-30 | quarterly | CAND-HARVEST-1202 | Cash Flow Manager 现金流管理器 | D_TRADING | 否决（rejected） | rejected(孤儿harvest):源文档已删除+依赖图文档未定义此ID,清理D-TRADING ID空间 |
| 2026-11-30 | quarterly | CAND-HARVEST-2862 | Global State Aggregator 全局状态聚合器 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-2967 | Intraday Trading Agent 日内交易代理 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-2975 | 交易域规则目录 Trading Domain Rule Catalog | D_TRADING | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3055 | Trader 交易员角色 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3953 | 延迟预算分配器 Latency Budget Allocator | D_TRADING | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3954 | 延迟归因器 Latency Attributor | D_TRADING | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3955 | 纳秒级关键路径分析器 Nanosecond Critical Path Analyzer | D_TRADING | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5033 | Cash Management 资金与现金管理 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-5034 | Settlement Reconciliation 结算与对账 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-5035 | Intraday PnL Monitor 日内盈亏监控 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5036 | Position Accounting 持仓会计 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-5037 | End-of-Day Processor 日终处理器 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-5060 | Gift Declaration Form Engine 礼品申报表引擎 | D_TRADING | 候选待评（candidate） | harvest待评估（likely_implemented） |
