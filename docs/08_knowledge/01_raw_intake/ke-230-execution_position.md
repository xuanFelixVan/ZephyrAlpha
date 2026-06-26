---
module_id: KE-209---position-000
title: 2.5 Execution & Position 域（执行与持仓）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 2.5 Execution & Position 域（执行与持仓）

2.5 Execution & Position 域（执行与持仓）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E13 | `Order` | 委托（client_order_id, symbol, side, qty, type, ts_create, parent_order_id?） | 状态机：`new → routed → partial → filled / cancelled / rejected` | 🟢 低（事件流） | OLTP + 事件流 |
| E14 | `Fill` / `Execution` | 成交回报（exec_id, order_id, ts_exec, qty, price, venue, fee） | append-only | 🟢 低 | OLTP + 事件流 |
| E15 | `Position` | 持仓快照（account_id, symbol, qty, avg_cost, ts_snapshot） | bitemporal（valid_time + transaction_time） | 🟡 中 | OLTP |
| E16 | `Portfolio` | 组合定义（portfolio_id, name, base_currency, capital, mandate） | 主数据 | — | OLTP |
