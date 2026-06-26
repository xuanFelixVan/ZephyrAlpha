---
module_id: KE-169
title: 2.1 Market Data 域（行情数据）
category: documentation
ttl: permanent
---

# 2.1 Market Data 域（行情数据）

2.1 Market Data 域（行情数据）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E01 | `Tick` | 单笔成交/盘口快照（symbol, ts_exchange, ts_ingest, price, volume, side, bid/ask 五档） | append-only，永不修改 | 🔴 高 | 列存 / 时序库 |
| E02 | `Bar` | OHLCV 聚合（symbol, frequency=1m/5m/1d, ts_open, ts_close, open, high, low, close, volume, vwap） | append-only；当日 bar 在收盘前可滚动更新 | 🔴 高 | 时序库 |
| E03 | `OrderBookSnapshot` | L2 深度快照（symbol, ts, levels[10]） | append-only | 🔴 高 | 时序库 / 对象存储 |
| E04 | `CorporateAction` | 分红 / 拆股 / 配股 / 合并事件（symbol, ex_date, action_type, ratio, cash_amount） | 主数据，可修订（修订必须留痕） | 🔴 高（影响复权） | OLTP + 历史快照 |
