---
module_id: KE-261
title: 3.2 分类矩阵（按实体）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3.2 分类矩阵（按实体）

3.2 分类矩阵（按实体）

| Entity | 温度 | 节奏 | 来源 |
|--------|-----|-----|------|
| Tick / OrderBookSnapshot | 热 | 流 | 外 |
| Bar (intraday) | 热 | 流 | 派生 |
| Bar (EOD) | 温 | 批 | 派生 |
| Security / TradingCalendar / Benchmark | 温 | 批 | 外 |
| IndexConstituent | 温 | 批 | 外（bitemporal） |
| CorporateAction | 温 | 批 | 外 |
| FactorValue / FeatureSet | 温 | 批（夜间）/ 流（日内因子） | 派生 |
| Signal / TargetPosition | 热 | 流 | 派生 |
| Order / Fill | 热 | 流 | 内 |
| Position | 温 | 批（快照）/ 流（实时增量） | 派生 |
| PnL / RiskMetric | 温 | 批 | 派生 |
| 历史 Tick (>2y) | 冷 | 批 | 外 |
| 退役模型的 FactorValue | 冷 | 批 | 派生 |
