---
module_id: KE-3402
title: 8.1 五类标准断言
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 8.1 五类标准断言

8.1 五类标准断言

| 类别 | 断言示例 | 触发时机 |
|------|---------|---------|
| **Schema** | 字段类型 / 必填 / 取值域（enum） | ingest 时（fail-fast）+ CI |
| **Range** | `0 < price < 10000`、`volume ≥ 0`、`abs(daily_return) < 0.5`（非异常停牌） | ingest 时 + 每日报表 |
| **Null / Completeness** | 关键字段缺失率 < 0.01% | 每日 ETL 后 |
| **Freshness** | `max(ts_ingest)` 与当前时间差 < SLA | 调度器健康检查 |
| **Distribution Drift** | 因子值分布与近 60 日基线 PSI < 0.2 | 每日因子计算后 |
