---
module_id: VIEW-04PRINC-APPFLOWS
title: 应用流程时序图 / Application Flow Sequence Diagrams
doc_type: architecture_view
status: Active
version: 0.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-07-22
superseded_by: null
supersedes: null
related_rationale: []
related_open_questions: []
tags:
- sequence-diagram
- application-flow
- methodology
- pending-review
summary: 5 张应用流程端到端时序图（订单提交 / 成交回报 / 风控触发 / 组合再平衡 / 异常处置），原 .mmd 已删除，本文档为应用流程时序图单一真源（内嵌 mermaid）。
date: '2026-07-22'
ttl: permanent
---

# 应用流程时序图
# Application Flow Sequence Diagrams

> **单一真源 / Single Source of Truth** — 本文档内嵌 5 张应用流程端到端时序图（订单提交 / 成交回报 / 风控触发 / 组合再平衡 / 异常处置），原独立 `.mmd` 已删除。
>
> **背景**：H11 系列 5 张时序图原为独立 `.mmd`，AI 不会主动读取独立 `.mmd`，人亦难直接查看；转为内嵌 mermaid 后可在 IDE 直接渲染。

---

## 1. 订单提交端到端时序（Order Submission）

> 订单提交全流程（覆盖 H10 幂等 + H8 ACL + H9 熔断）。3 场景：正常首次提交（happy path）+ 瞬时网络失败→Retry（幂等）+ Broker CB OPEN→SOR 切换 fallback。

> **版本**: v1.1.0 (2026-05-04) — 标注 CTR-004 Order 契约作为架构承重墙 ｜ **契约真源**: `architecture_model/contracts/cross_layer_contracts.yaml`
> **来源**: 03-AA §9.2 时序图主干抽取 + ACL 三段结构 + Pre-Trade Fail-Closed
> **一致性**: 03-AA §9.2（Idempotency 三场景）｜ ocp-extension-points.md §5（Broker ACL 三段 + failover）｜ fault-tolerance-matrix.md §D_RISK/§D_EX_CORE（Fail-Closed + Retry 过 Guard）｜ domain-event-catalog.md E-EX-01/07、E-RK-04 ｜ ddd-aggregates.md AR-01 Order.submit()

```mermaid
sequenceDiagram
    autonumber

    participant Strategy as D_PF_CORE Strategy<br/>(signal source)
    participant OMS as D_EX_CORE OMS<br/>(Order Aggregate)
    participant Idem as D_EX_CORE Idempotency<br/>Guard
    participant Redis as Redis<br/>(hot layer)
    participant PreTrade as D_EX_CORE Pre-Trade<br/>Checker
    participant SOR as D_EX_CORE SOR
    participant Facade as Broker Adapter<br/>Facade (ACL)
    participant Mapper as Broker Adapter<br/>Mapper (ACL)
    participant Raw as Broker Raw<br/>Client (ACL)
    participant Broker as External<br/>Broker API
    participant Audit as L2 Audit Log
    participant Notif as D_FRONTEND Notifications

    Note over Strategy,Broker: === 场景 A：正常首次提交（happy path）===
    Note right of Strategy: 🔓 CTR-004: Order<br/>D_PF_CORE → D_EX_CORE 可变契约（状态机）
    Strategy->>OMS: submit(signal{strategy_id, signal_id, asof_ts, instrument, side, qty, price_hint})
    OMS->>Idem: compute_key(signal)
    Note right of Idem: Key = SHA-256(8 fields)<br/>→ 128-bit hex prefix<br/>= client_order_id
    Idem->>Redis: SETNX "idem:v1:{key}" {status:pending}, EX=EOD+24h
    Redis-->>Idem: 1 (首次写入成功)
    Idem-->>OMS: OK (first submit)
    OMS->>PreTrade: evaluate(candidate_order, position_state)
    alt Pre-Trade passed
        PreTrade-->>OMS: PASS
        OMS->>Audit: publish E-EX-01 OrderSubmitted{order_id, client_order_id=key, ...}
        OMS->>SOR: route(order, client_order_id=key)
        SOR->>Facade: submit_order(order)
        Facade->>Mapper: map(internal Order → vendor schema)
        Mapper-->>Facade: vendor_order_payload
        Facade->>Raw: raw_submit(vendor_payload, clOrdID=key)
        Raw->>Broker: HTTP POST /orders OR FIX NewOrderSingle (Tag 11 = key)
        Broker-->>Raw: ack {broker_ref_id}
        Raw-->>Facade: broker_ack
        Facade-->>SOR: success
        SOR-->>OMS: accepted(broker_ref_id)
        OMS->>Redis: UPDATE {status:accepted, broker_ref_id}
        OMS->>Audit: publish E-EX-02 OrderAccepted
    else Pre-Trade failed (Fail-Closed)
        PreTrade-->>OMS: REJECT {reason, category}
        OMS->>Redis: UPDATE {status:pre_trade_rejected}
        OMS->>Audit: publish E-RK-04 PreTradeRejected
        Note right of OMS: ⚠️ Fail-Closed 铁律<br/>checker timeout / error<br/>= 视同拒单，绝不放行
        OMS-->>Strategy: rejected
    end

    Note over Strategy,Broker: === 场景 B：瞬时网络失败 → tenacity Retry（必过 Guard）===
    Strategy->>OMS: retry submit (same signal, attempt 2)
    OMS->>Idem: compute_key(signal)
    Note right of Idem: 字段不变 → 相同 Key
    Idem->>Redis: SETNX "idem:v1:{key}" ...
    Redis-->>Idem: 0 (key exists)
    Idem->>Redis: GET value
    Redis-->>Idem: {status:accepted, broker_ref_id:...}
    Idem-->>OMS: DUPLICATE (already submitted)
    OMS->>Audit: publish E-EX-07 OrderIdempotencyBlocked{detection_source:REDIS_SETNX}
    Note right of OMS: 🔴 H10 红线生效<br/>broker 绝不收到第二次
    OMS-->>Strategy: return existing state

    Note over Strategy,Broker: === 场景 C：Broker CB OPEN → SOR 切换 fallback broker ===
    Strategy->>OMS: submit(signal{...})
    OMS->>Idem: compute_key + SETNX → OK
    OMS->>PreTrade: evaluate → PASS
    OMS->>SOR: route(order)
    SOR->>Facade: submit_order (primary broker)
    Facade->>Raw: raw_submit
    Raw--xBroker: connection error / 5xx
    Raw-->>Facade: RemoteServiceError
    Facade->>Facade: CircuitBreaker.record_failure()
    Note right of Facade: pybreaker threshold=40%<br/>若触发 → OPEN 60s
    Facade-->>SOR: failure (primary)
    SOR->>SOR: failover_policy.resolve() → next broker
    Note right of SOR: ⚠️ failover 前必须<br/>重查 Idempotency Guard<br/>避免 primary 实际已收到
    SOR->>Idem: revalidate_key(key) → still pending
    SOR->>Facade: submit_order (fallback broker, same key)
    Facade->>Raw: raw_submit(clOrdID=key)
    Raw->>Broker: fallback broker API
    Broker-->>Raw: ack {broker_ref_id}
    Raw-->>SOR: accepted
    SOR-->>OMS: accepted
    OMS->>Redis: UPDATE {status:accepted, broker_id:fallback}
    OMS->>Audit: publish E-EX-02 OrderAccepted
    OMS->>Notif: D_FRONTEND notify {event:failover_triggered}
```

---

## 2. 成交回报处理时序（Fill Received）

> 成交回报处理流程（含 Position/PnL 更新 + Risk 重算 + Strategy 回调）。6 步骤：Order Aggregate 状态更新 + Position Aggregate 更新 + PnL 增量计算 + Risk Monitor 重算 + Strategy.on_fill() 回调 + 完成态审计。

> **版本**: v1.1.0 (2026-05-04) — 标注 CTR-005 Fill + CTR-006 PositionSnapshot 契约作为架构承重墙 ｜ **契约真源**: `architecture_model/contracts/cross_layer_contracts.yaml`
> **来源**: ddd-aggregates.md AR-01 Order.add_fill() + AR-02 Position.apply_fill() ｜ domain-event-catalog.md E-EX-04 FillReceived + E-PF-02 PositionLimitBreached ｜ interface-contracts.md §1.5 Fill + §1.6 PositionSnapshot
> **一致性**: 03-AA §7.2 Broker 回调机制 ｜ fault-tolerance-matrix.md §D_RISK（Risk Fail-Closed）｜ c4_l3_d_ex_core（组件命名一致）

```mermaid
sequenceDiagram
    autonumber

    participant Broker as External<br/>Broker API
    participant Raw as Broker Raw<br/>Client (ACL)
    participant Facade as Broker Adapter<br/>Facade (ACL)
    participant FillHandler as D_EX_CORE Fill<br/>Handler
    participant OrderAgg as Order Aggregate<br/>(OMS)
    participant PositionAgg as Position<br/>Aggregate
    participant PnL as D_TRADING PnL<br/>Calculator
    participant RiskMon as D_RISK Risk<br/>Monitor
    participant Strategy as D_PF_CORE Strategy<br/>(on_fill callback)
    participant Audit as L2 Audit Log
    participant Notif as D_FRONTEND Notifications

    Note over Broker,Strategy: === 主路径：部分成交 / 完全成交 统一处理 ===
    Broker->>Raw: FIX ExecutionReport / REST callback {fill_data}
    Raw->>Facade: raw_fill_event (vendor schema)
    Facade->>Facade: mapper.map_fill(vendor_schema → internal Fill)
    Note right of Facade: Fill frozen dataclass:<br/>fill_id / order_id / qty / price /<br/>fill_timestamp / commission / slippage
    Facade->>FillHandler: on_fill_received(Fill)

    Note over FillHandler,Audit: --- 步骤 1：Order Aggregate 状态更新 ---
    Note right of Facade: 🔒 CTR-005: Fill<br/>D_EX_CORE → D_TRADING frozen 契约
    FillHandler->>OrderAgg: add_fill(fill)
    OrderAgg->>OrderAgg: update filled_quantity (+= fill.qty)
    OrderAgg->>OrderAgg: recompute avg_fill_price (weighted)
    alt filled_quantity == quantity
        OrderAgg->>OrderAgg: status → FILLED
    else filled_quantity < quantity
        OrderAgg->>OrderAgg: status → PARTIAL
    end
    OrderAgg->>Audit: publish E-EX-04 FillReceived{fill_id, order_id, qty, price, ...}

    Note over FillHandler,PositionAgg: --- 步骤 2：Position Aggregate 最终一致性更新 ---
    Note right of PositionAgg: 🔒 CTR-006: PositionSnapshot<br/>D_EX_CORE/D_TRADING → D_RISK/D_ML_TRAIN frozen 契约
    FillHandler->>PositionAgg: apply_fill(fill, order.instrument_id, order.side)
    PositionAgg->>PositionAgg: update quantity / avg_cost<br/>(可选：Lot 开仓或平仓)
    PositionAgg->>Audit: log {position_snapshot_ts}

    Note over FillHandler,PnL: --- 步骤 3：D_TRADING PnL 增量计算 ---
    FillHandler->>PnL: compute_increment(fill, prev_position)
    PnL->>PnL: realized_pnl += (fill.price - lot.cost_basis) × qty - commission
    PnL->>PnL: unrealized_pnl = recompute via mark-to-market
    PnL-->>FillHandler: pnl_snapshot

    Note over FillHandler,RiskMon: --- 步骤 4：D_RISK Risk Monitor 重算 + 限额检查 ---
    FillHandler->>RiskMon: on_position_changed(position_snapshot)
    RiskMon->>RiskMon: evaluate_position(position, risk_policy)
    alt PositionLimit breached
        RiskMon->>Audit: publish E-PF-02 PositionLimitBreached
        RiskMon->>Notif: D_FRONTEND alert (severity=CRITICAL/EMERGENCY)
    else within limits
        RiskMon->>RiskMon: metric.zephyr_position_limit_headroom += update
    end
    RiskMon->>RiskMon: evaluate_portfolio(all_positions)
    alt Portfolio-level RiskLimit breached
        RiskMon->>Audit: publish E-RK-01 RiskLimitBreached
        RiskMon->>Notif: D_FRONTEND alert
    end

    Note over FillHandler,Strategy: --- 步骤 5：D_PF_CORE Strategy.on_fill() 回调 ---
    FillHandler->>Strategy: on_fill(fill, position_snapshot)
    Note right of Strategy: 策略跟踪自己的成交状态<br/>决定是否需要追单 / 撤单 /<br/>下一轮再平衡
    Strategy-->>FillHandler: ack (non-blocking)

    Note over FillHandler,Audit: --- 步骤 6：完成态审计 ---
    FillHandler->>Audit: append journal {fill_id, order_status, position_snapshot}
    Note right of Audit: ⚠️ 合规铁律<br/>Fill 永久保留（RPO=0）<br/>04-TA §8.1 对齐
```

---

## 3. 风控触发时序（Risk Trigger）

> 风控触发全链路（Pre-trade 拦截 + At-trade 监控 + Post-trade 告警）。3 阶段：Pre-trade（拦截）+ At-trade（实时监控）+ Post-trade（回撤监控 + EOD 对账）。

> **版本**: v1.0.0 (2026-04-19, S14-Phase2-BatchF R61)
> **来源**: fault-tolerance-matrix.md §D_RISK（Pre-Trade Fail-Closed 铁律）｜ ddd-aggregates.md AR-07 RiskPolicy ｜ domain-event-catalog.md E-RK-01/02/03/04 + E-PF-02 ｜ 01-BA §5.2 SLO-3 Order Submit Latency SLO-Audit

```mermaid
sequenceDiagram
    autonumber

    participant Strategy as D_PF_CORE Strategy
    participant OMS as D_EX_CORE OMS
    participant PreTrade as D_EX_CORE Pre-Trade<br/>Checker (D_RISK 规则)
    participant RiskPolicy as D_RISK RiskPolicy<br/>Aggregate
    participant RiskMon as D_RISK Risk<br/>Monitor
    participant Positions as Position<br/>Aggregates
    participant Drawdown as D_RISK Drawdown<br/>Tracker
    participant Audit as L2 Audit Log
    participant Notif as D_FRONTEND Notifications
    participant Runbook as Runbook /<br/>Human Ops

    Note over Strategy,Runbook: === 阶段 1：Pre-trade（订单提交前拦截）===
    Strategy->>OMS: submit(candidate_order)
    OMS->>PreTrade: evaluate(candidate_order, current_position_state)
    PreTrade->>RiskPolicy: evaluate_pre_trade(candidate, position_state)
    RiskPolicy->>RiskPolicy: run checker chain<br/>(position_limit / compliance / margin / blacklist)

    alt All checkers passed
        RiskPolicy-->>PreTrade: PASS
        PreTrade-->>OMS: PASS → submit continues
        Note right of OMS: (进入 seq-order-submit 主流程)
    else Hard limit breached
        RiskPolicy-->>PreTrade: REJECT {category:POSITION_LIMIT, reason}
        PreTrade-->>OMS: REJECT
        OMS->>Audit: publish E-RK-04 PreTradeRejected
        OMS-->>Strategy: rejected
    else Checker timeout (>200ms)
        Note right of RiskPolicy: ⚠️ Fail-Closed 铁律<br/>超时 = 视同拒单<br/>绝不默认放行
        RiskPolicy-->>PreTrade: REJECT {category:CHECKER_TIMEOUT}
        PreTrade-->>OMS: REJECT
        OMS->>Audit: publish E-RK-04 PreTradeRejected{category:CHECKER_TIMEOUT}
        OMS->>Notif: D_FRONTEND alert {severity:CRITICAL, reason:checker_degraded}
        OMS-->>Strategy: rejected
    else Checker exception
        RiskPolicy-->>PreTrade: REJECT {category:CHECKER_ERROR}
        PreTrade-->>OMS: REJECT
        OMS->>Audit: publish E-RK-04 PreTradeRejected{category:CHECKER_ERROR}
        OMS->>Notif: D_FRONTEND alert
        OMS-->>Strategy: rejected
    end

    Note over Strategy,Runbook: === 阶段 2：At-trade（实时监控持仓/组合）===
    loop 每次 Fill 触发 + 定时 30s
        Positions->>RiskMon: on_position_changed(position_snapshot)
        RiskMon->>RiskPolicy: evaluate_position(position, policy)
        alt Single Position limit breached
            RiskPolicy-->>RiskMon: breach {limit_type:SINGLE_INSTRUMENT_NOTIONAL}
            RiskMon->>Audit: publish E-PF-02 PositionLimitBreached
            RiskMon->>Notif: D_FRONTEND alert (severity:CRITICAL)
        end

        RiskMon->>RiskPolicy: evaluate_portfolio(all_positions)
        alt Portfolio-level breach (VaR / Gross Notional / Sector)
            RiskPolicy-->>RiskMon: breaches [...]
            RiskMon->>Audit: publish E-RK-01 RiskLimitBreached{severity:CRITICAL}
            RiskMon->>Notif: D_FRONTEND alert + D_PF_CORE 新单约束收紧标记
        end

        RiskMon->>RiskPolicy: check_margin()
        alt Margin insufficient
            RiskPolicy-->>RiskMon: margin_call {shortfall, grace_period}
            RiskMon->>Audit: publish E-RK-02 MarginCalled{severity:EMERGENCY}
            RiskMon->>Notif: D_FRONTEND 紧急告警 (飞书+短信+电话)
            RiskMon->>Runbook: trigger emergency reduction playbook
        end
    end

    Note over Strategy,Runbook: === 阶段 3：Post-trade（回撤监控 + EOD 复核）===
    loop 每 5 min + EOD
        Drawdown->>Drawdown: compute current_drawdown
        alt drawdown > threshold (5% / 10% / 20% 分档)
            Drawdown->>Audit: publish E-RK-03 DrawdownAlerted{severity}
            Drawdown->>Notif: D_FRONTEND alert
            Drawdown->>Runbook: trigger human review workflow
            Note right of Runbook: ⚠️ 不直接强制减仓<br/>避免噪声触发 trend-following<br/>由人工复核决定是否 revoke
        end
    end

    Note over Strategy,Runbook: === EOD 对账 ===
    Drawdown->>Audit: append EOD risk report {all_limits_status, pnl, drawdown_curve}
    Audit->>Audit: verify RPO=0 (journal + remote backup)
```

---

## 4. 组合再平衡时序（Portfolio Rebalance）

> 组合再平衡流程（Signal → Portfolio 决策 → 批量下单，每笔独立 Idempotency Key）。8 步骤：数据准备PIT + 策略产出信号 + meta_router多策略融合 + Risk约束注入 + Optimizer优化 + 目标→订单计划 + 批量下单 + 归档。

> **版本**: v1.1.0 (2026-05-04) — 标注 CTR-001/CTR-002/CTR-003/CTR-004 契约作为架构承重墙 ｜ **契约真源**: `architecture_model/contracts/cross_layer_contracts.yaml`
> **来源**: ddd-aggregates.md AR-03 Portfolio.rebalance() + AR-04 Strategy.generate_signal() ｜ domain-event-catalog.md E-PF-01 PortfolioRebalanced + E-SG-01 SignalGenerated ｜ 03-AA §4.1 D_PF_CORE rebalancing/ + strategic/ 子模块
> **一致性**: interface-contracts.md §1 NormalizedMarketData / FactorSignal / RiskLimits / Order ｜ fault-tolerance-matrix.md §D_FACTOR（Factor Fail-Safe）

```mermaid
sequenceDiagram
    autonumber

    participant Scheduler as D_INFRA_OPS Scheduler<br/>/ Trigger
    participant FactorEng as D_FACTOR Factor<br/>Engine
    participant DataSource as D_MKT_DATA Data<br/>Source (ACL)
    participant Strategies as D_SIGLEGACY Strategies<br/>(multi-strategy)
    participant RiskEng as D_RISK Risk<br/>Engine (Policy)
    participant Portfolio as D_PF_CORE Portfolio<br/>Aggregate
    participant Optimizer as D_PF_CORE Optimizer<br/>(rebalancing/)
    participant Meta as D_PF_CORE meta_router<br/>(策略融合)
    participant OMS as D_EX_CORE OMS
    participant Audit as L2 Audit Log
    participant Notif as D_FRONTEND Notifications

    Note over Scheduler,Notif: === 触发：定时 / 信号偏离阈值 / 手工 ===
    Scheduler->>Portfolio: trigger_rebalance(portfolio_id, source=SCHEDULED)

    Note over Portfolio,DataSource: --- 步骤 1：数据准备（PIT 合规）---
    Note right of DataSource: 🔒 CTR-001: NormalizedMarketData<br/>D_MKT_DATA → D_FACTOR frozen 契约
    Portfolio->>FactorEng: fetch_factor_values(strategy_required_factors, asof=t0)
    FactorEng->>DataSource: fetch market_data (via VendorRegistry)
    DataSource-->>FactorEng: NormalizedMarketData (含 data_quality_caveat 标记)
    FactorEng->>FactorEng: compute factor_values (per factor × per instrument)
    Note right of FactorEng: 🔒 CTR-002: FactorSignal<br/>D_FACTOR → D_SIGLEGACY/D_RISK/D_PF_CORE frozen 契约
    FactorEng-->>Portfolio: FactorValues {asof, quality_flag}
    alt 数据质量降级 (stale_data_warning or data_quality_caveat)
        Portfolio->>Notif: D_FRONTEND warn {event:degraded_rebalance_data}
        Note right of Portfolio: 继续流程但 RiskEng<br/>升级保守档位
    end

    Note over Portfolio,Strategies: --- 步骤 2：各策略产出信号 ---
    loop 每个 attached strategy
        Portfolio->>Strategies: generate_signals(factor_values, asof)
        Strategies->>Strategies: StrategyBase.generate_target_weights(...)
        Strategies->>Audit: publish E-SG-01 SignalGenerated (per signal)
        Strategies-->>Portfolio: List[Signal]
    end

    Note over Portfolio,Meta: --- 步骤 3：meta_router 多策略融合（若启用）---
    alt 多策略协同模式
        Portfolio->>Meta: combine(all_strategy_signals, weights)
        Meta->>Meta: apply meta policy (eq-weight / risk-parity / etc)
        Meta-->>Portfolio: consolidated_signals
    end

    Note over Portfolio,RiskEng: --- 步骤 4：Risk 约束注入 ---
    Note right of RiskEng: 🔒 CTR-003: RiskLimits<br/>D_RISK → D_PF_CORE frozen 契约
    Portfolio->>RiskEng: fetch_risk_limits(portfolio_id)
    RiskEng-->>Portfolio: RiskLimits (Sector cap / VaR / Leverage / ...)

    Note over Portfolio,Optimizer: --- 步骤 5：Optimizer 产出目标权重 ---
    Portfolio->>Optimizer: optimize(signals, current_positions, risk_limits, capital)
    Optimizer->>Optimizer: mean-variance / Kelly / CVaR / Black-Litterman (per config)
    alt Optimizer converged
        Optimizer-->>Portfolio: target_positions {instrument_id: weight}
    else Optimizer infeasible (constraints conflict)
        Optimizer-->>Portfolio: INFEASIBLE {conflicts}
        Portfolio->>Notif: D_FRONTEND alert {event:rebalance_infeasible}
        Note right of Portfolio: 保留当前持仓不变<br/>发布空 rebalance 事件
    end

    Note over Portfolio,OMS: --- 步骤 6：目标 → 订单计划 ---
    Portfolio->>Portfolio: diff(target_positions, current_positions)
    Portfolio->>Portfolio: generate order plan [{instrument, side, qty}...]
    Portfolio->>Audit: publish E-PF-01 PortfolioRebalanced{rebalance_id, orders_planned}

    Note over Portfolio,OMS: --- 步骤 7：批量下单（每笔独立 Idempotency Key）---
    Note right of Portfolio: 🔓 CTR-004: Order<br/>D_PF_CORE → D_EX_CORE 可变契约（状态机）
    loop 每笔 order_plan entry
        Portfolio->>OMS: submit(signal→order, parent_rebalance_id)
        Note right of OMS: ⚠️ 每笔订单独立 key<br/>不共享 rebalance_id<br/>Key = SHA-256(8 fields)
        OMS->>OMS: (进入 seq-order-submit 主流程)
        Note right of OMS: Idempotency Guard + Pre-Trade +<br/>SOR → Broker ACL (略，见 seq 1)
    end

    Note over Portfolio,Audit: --- 步骤 8：再平衡归档 + 归因起算点 ---
    Portfolio->>Audit: append rebalance_snapshot {target_positions, orders_planned, lineage_root}
    Portfolio->>Portfolio: D_TRADING 归因起算点标记
```

---

## 5. 异常处置时序（Exception Handling）

> 异常处置三类场景：数据源故障 / 券商断连 / 策略异常。3 场景：Vendor故障+Fallback链降级 + Broker P断连→SOR failover→Broker Q + 策略异常/策略级熔断 + 横向SLO burn-rate升级。

> **版本**: v1.0.0 (2026-04-19, S14-Phase2-BatchF R61)
> **来源**: ocp-extension-points.md §5 Vendor Registry + failover_policy.yaml ｜ fault-tolerance-matrix.md §D_MKT_DATA/§D_FACTOR/§D_PF_CORE/§D_EX_CORE 各层容错策略 ｜ domain-event-catalog.md E-OP-01 DataIngestionFailed + E-OP-03 SystemDegraded ｜ 04-TA §8 DR/BCP §8.3 量化特殊场景

```mermaid
sequenceDiagram
    autonumber

    participant Scheduler as D_INFRA_OPS Scheduler
    participant Registry as D_MKT_DATA Vendor<br/>Registry
    participant VendorA as Vendor A<br/>(Primary)
    participant VendorB as Vendor B<br/>(Fallback 1)
    participant Cache as D_MKT_DATA PIT Cache
    participant FactorEng as D_FACTOR Factor<br/>Engine
    participant Strategy as D_PF_CORE Strategy
    participant OMS as D_EX_CORE OMS
    participant BrokerP as Broker P<br/>(Primary)
    participant BrokerQ as Broker Q<br/>(Fallback)
    participant Idem as Idempotency<br/>Guard
    participant Audit as L2 Audit Log
    participant Notif as D_FRONTEND Notifications
    participant Runbook as Runbook

    Note over Scheduler,Runbook: === 场景 A：Vendor 故障 + Fallback 链降级 ===
    Scheduler->>Registry: fetch market_data (asof, instruments)
    Registry->>VendorA: resolve() → facade.fetch()
    VendorA--xRegistry: TimeoutError / 5xx
    Registry->>Registry: CircuitBreaker.record_failure()
    Note right of Registry: pybreaker failure>50%<br/>→ OPEN 60s 不再请求 A
    Registry->>VendorB: resolve() → fallback vendor
    VendorB-->>Registry: data (带 stale_data_warning)
    Registry->>FactorEng: NormalizedMarketData{vendor=B, quality_caveat=true}
    FactorEng->>Audit: publish E-OP-01 DataIngestionFailed{vendor_id:A, fallback_used:B}
    FactorEng->>Notif: D_FRONTEND warn (severity:WARNING)

    alt Fallback chain 耗尽
        Registry->>VendorB: facade.fetch()
        VendorB--xRegistry: error
        Registry->>Cache: fetch_latest_PIT_snapshot(asof)
        Cache-->>Registry: stale_cache_data{last_update, age}
        Registry->>FactorEng: stale data + stale_data_warning
        FactorEng->>Audit: publish E-OP-01{fallback_chain_depth:-1, cache_fallback_used:true}
        FactorEng->>Notif: D_FRONTEND alert (severity:CRITICAL)

        alt Stale age > tolerance
            FactorEng->>Audit: publish E-OP-03 SystemDegraded{slo:SLO-1}
            FactorEng->>Runbook: trigger DR review
            Note right of Runbook: 持续降级 > 15min<br/>升级到 04-TA §8 DR 预案
        end
    end

    Note over Scheduler,Runbook: === 场景 B：Broker P 断连 → SOR failover → Broker Q ===
    Strategy->>OMS: submit(order)
    OMS->>Idem: SETNX → OK
    OMS->>BrokerP: submit (via ACL facade)
    BrokerP--xOMS: connection error / 5xx
    OMS->>OMS: broker_cb.record_failure()
    alt CB not yet OPEN
        OMS->>OMS: tenacity retry (max=3, exp backoff)
        OMS->>Idem: revalidate_key(key) → still pending
        Note right of OMS: ⚠️ 每次 retry 前必过 Guard<br/>H9 与 H10 强耦合铁律
        OMS->>BrokerP: retry submit
        BrokerP--xOMS: still failing
    end
    OMS->>OMS: CircuitBreaker → OPEN 60s on BrokerP
    Note right of OMS: 不再向 P 发新请求<br/>已提交待确认订单进入<br/>"不确定状态"（DR §8.3.2）
    OMS->>OMS: failover_policy.resolve() → BrokerQ
    OMS->>Idem: revalidate_key(key) → still pending
    OMS->>BrokerQ: submit(order, clOrdID=key)
    BrokerQ->>BrokerQ: 识别 client_order_id 去重（双保险）
    alt BrokerQ 首次看到 key
        BrokerQ-->>OMS: ack {broker_ref_id}
        OMS->>Audit: publish E-EX-02 OrderAccepted{broker_id:Q, failover_from:P}
        OMS->>Notif: D_FRONTEND alert {event:broker_failover}
    else BrokerQ 侧也检出重复（极端场景）
        BrokerQ-->>OMS: reject {DUPLICATE_CLIENT_ORDER_ID, existing_broker_ref}
        OMS->>Audit: publish E-EX-03 OrderRejected + E-EX-07 OrderIdempotencyBlocked{source:BROKER_DEDUP_REJECT}
        Note right of OMS: 说明 BrokerP 实际收到了<br/>→ 资金安全无损失（双保险生效）
    end

    Note over Scheduler,Runbook: === 场景 C：Strategy 异常 / 策略级熔断 ===
    Strategy->>Strategy: generate_signals() throws ValueError / KeyError
    Strategy->>Audit: log exception {strategy_id, stack_trace, asof_ts}
    Strategy->>Strategy: strategy_cb.record_failure()
    alt strategy_cb 触发（failure rate > 30%）
        Strategy->>Strategy: CircuitBreaker → OPEN 60s
        Strategy->>Audit: publish strategy-level breaker OPEN log
        Strategy->>Notif: D_FRONTEND alert (severity:CRITICAL)

        Note right of Strategy: Fallback 选项（每策略配置）：
        alt Fallback = 保持当前持仓
            Strategy-->>Strategy: 返回 empty signals<br/>Portfolio 当轮不再平衡
        else Fallback = 保守默认权重
            Strategy-->>Strategy: 返回 equal_weight / cash 信号
        else Fallback = 停机
            Strategy->>OMS: cancel all pending orders for this strategy
            OMS->>Idem: 对 pending 订单逐一 cancel (生成新 key)
            Strategy->>Audit: publish E-SG-02 SignalRevoked (批量)
            Strategy->>Runbook: trigger human review
        end
    end

    Note over Scheduler,Runbook: === 横向：SLO burn-rate 升级 ===
    Audit->>Audit: aggregate E-OP-01 / broker_cb_open / strategy_cb_open 计数
    alt SLO error budget burn > 5%/h
        Audit->>Notif: publish E-OP-03 SystemDegraded{slo_id, burn_rate}
        Notif->>Runbook: trigger operational runbook
        Runbook->>Runbook: 判定是否升级 DR (04-TA §8)
    end
```

---

## 说明 / Notes

- **来源 / Source**: 5 张 `.mmd`（`seq_order_submit` / `seq_fill_received` / `seq_risk_trigger` / `seq_rebalance` / `seq_exception_handling`），原存于 `target_architecture/diagrams/`，H11 系列时序图 1/5 ~ 5/5
- **转换规则**: 剥离文件级 `%%` 注释（标题/描述/版本/契约真源/来源/一致性）为 `>` 引用行；`sequenceDiagram` 主体原样保留于 mermaid 代码块
- **审核要点 / Review Focus**:
  - 时序图描绘的参与者（OMS / SOR / Fill Handler / meta_router / Drift Tracker 等）是否与实际代码一致？
  - 事件命名（E-EX-01/02/04/07、E-RK-01~04、E-PF-01/02、E-SG-01/02、E-OP-01/03）是否与 `domain-event-catalog.md` 真源一致？
  - 契约标注（CTR-001~006）是否与 `cross_layer_contracts.yaml` 真源一致？
  - 已决定：作为应用流程时序图单一真源保留（原 `.mmd` 已删除）
