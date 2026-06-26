---
module_id: KE-318-----------schema-002
status: active
title: 4.1 PIT 三个核心字段（强制 schema）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4.1 PIT 三个核心字段（强制 schema）

4.1 PIT 三个核心字段（强制 schema）

凡 PIT 敏感（🔴 高）的实体，schema 中**必须**含：

| 字段 | 含义 | 业界对位 |
|------|------|---------|
| `asof_date` / `valid_time` | 数据所描述的"业务时间"（事件本身发生的时刻） | TimescaleDB / SQL:2011 valid time |
| `ts_ingest` / `transaction_time` | 数据**实际进入系统**的时间 | SQL:2011 transaction time / bitemporal |
| `vendor_release_ts` | 外部 vendor 把这条数据**对外发布**的时间（财报口径关键） | Bloomberg PIT / FactSet PIT |

**铁律**：任意因子计算 / 回测查询，**只能用 `vendor_release_ts ≤ T` 且 `ts_ingest ≤ T`** 的数据。`asof_date` 仅用作语义对齐，不做过滤条件。
