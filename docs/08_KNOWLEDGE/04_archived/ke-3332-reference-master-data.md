---
module_id: KE-3212---master-data-000
title: 2.2 Reference & Master Data 域（参考与主数据）
category: documentation
---

# 2.2 Reference & Master Data 域（参考与主数据）

2.2 Reference & Master Data 域（参考与主数据）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E05 | `Security` / `Instrument` | 证券主数据（symbol, isin, exchange, sector, industry, listing_date, delisting_date, status, currency） | 主数据，**必须保留历史版本**（退市后保留） | 🔴 高（survivorship 关键） | OLTP + bitemporal 表 |
| E06 | `TradingCalendar` | 交易日历（exchange, date, is_trading, half_day, session_open, session_close） | 主数据，按月维护 | 🟡 中 | OLTP |
| E07 | `IndexConstituent` | 指数成分（index_code, symbol, weight, effective_date, end_date） | 主数据，**bitemporal**（必须 PIT 查询） | 🔴 高 | OLTP + bitemporal 表 |
