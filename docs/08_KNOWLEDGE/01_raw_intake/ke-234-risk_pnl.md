---
module_id: KE-213---pnl-000
title: 2.6 Risk & PnL 域（风险与盈亏）
category: documentation
ttl: permanent
---

# 2.6 Risk & PnL 域（风险与盈亏）

2.6 Risk & PnL 域（风险与盈亏）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E17 | `RiskMetric` | 风险指标（portfolio_id, metric_name=VaR/Beta/Exposure/..., ts, value, scenario_id?） | append-only | 🟡 中 | 时序库 |
| E18 | `PnL` | 盈亏（portfolio_id, ts, realized, unrealized, fees, by_book, lineage_root） | append-only；T+1 修订需保留旧版本 | 🟡 中 | OLTP |
| E19 | `Benchmark` | 基准（benchmark_id, type, components[], ts） | 主数据 | — | OLTP |

> **PIT 敏感度图例**：🔴 高 = 任何错误都会让回测/归因撒谎；🟡 中 = 错误可被对账发现；🟢 低 = 事件流自然带时间。
