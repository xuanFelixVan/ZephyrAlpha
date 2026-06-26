---
module_id: KE-2385
status: active
title: 6.3 DB Schema 漂移
category: module_blueprint
ttl: permanent
---

# 6.3 DB Schema 漂移

6.3 DB Schema 漂移

```yaml
db_schema_drift:
  description: "SQLite schema vs ORM model vs migration 文件三方对账"
  checks:
    - name: "schema_vs_orm"
      method: "sqlite_master 中的表结构 vs SQLAlchemy/peewee model 定义"
    - name: "orm_vs_migration"
      method: "ORM model 字段 vs 最新 migration 文件中的字段"
    - name: "index_consistency"
      method: "ORM 中声明的索引 vs 数据库中实际索引"
```
