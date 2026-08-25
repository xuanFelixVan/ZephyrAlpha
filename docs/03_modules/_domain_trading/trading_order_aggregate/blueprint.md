---
blueprint_id: MOD-TRADING-009
module_name: trading_order_aggregate
domain: D_TRADING
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_TRADING
path: src/zephyr/trading/trading_order_aggregate.py
granularity: file
---

# MOD-TRADING-009 trading_order_aggregate 蓝图（核心聚合 AGG-TRD-01 TradingOrder）

> **module_id**: MOD-TRADING-009 | **域**: D_TRADING | **优先级**: P1
> **来源**: B6-08087（AUD-DRAFT-001-DIGEST P1 波 W-P1-23，CAND-TRD-009，D-TRADING §0）
> 代码：`src/zephyr/trading/trading_order_aggregate.py`

## 0. 定位

交易运营域 OMS 侧订单核心聚合（DDD 聚合根）。TSV 现状注记
"部分:src/zephyr/ex_core/order_manager.py"——订单管理逻辑在 EX 域，
TradingOrder 聚合根与领域事件未归位 D-TRADING。

运营视角订单聚合跟踪**业务全生命周期**（接收→派发→执行→成交→结算中→
已结算→已对账），与 EX 域执行段状态机粒度正交：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| ex_core/order_manager | MOD-L06-001 | 执行段状态机（PENDING→SUBMITTED→PARTIAL→FILLED/CANCELLED）+合规双闸+券商路由 | 本件不重复执行段状态机，仅消费其执行结果快照推进运营段状态 |
| trading_contracts/execution/order | MOD-INF-016 | CTR-004 Order 契约 re-export（数据载体） | 本件聚合根引用契约，不重复定义 |
| settlement_reconciliation | MOD-TRADING-003 | 交易级对账引擎（比对+差异+报告） | 本件运营状态 SETTLING→SETTLED→RECONCILED 由对账/结算事件驱动 |

不做什么：不重建执行段状态机（委托 MOD-L06-001）、不直接下单、不做对账
比对（委托 MOD-TRADING-003）。

## 1. 规则（确定性，Fail-Closed）

- **聚合根 TradingOrder**：order_id 唯一 + idempotency_key 幂等（同键重复
  注册返回既有聚合，不新建）。
- **运营状态机**：RECEIVED→DISPATCHED→EXECUTING→FILLED→SETTLING→
  SETTLED→RECONCILED；支路 REJECTED/CANCELLED 终态；非法转换
  Fail-Closed 抛 InvalidOrderTransitionError。
- **领域事件发布**：每次状态迁移产出不可变 OrderDomainEvent
  （order_id/from_status/to_status/occurred_at/payload），经注入式
  event_sink 发布；event_sink 缺失仅落聚合内事件日志（不阻断）。
- **事件溯源**：聚合内 events 元组只增不改（append-only），支持
  replay 重建状态。
