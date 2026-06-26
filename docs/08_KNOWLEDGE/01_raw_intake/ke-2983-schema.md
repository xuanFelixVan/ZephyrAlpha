---
module_id: KE-2883
title: Schema 版本历史全景
category: module_blueprint
ttl: permanent
---

# Schema 版本历史全景

Schema 版本历史全景

蓝图 Schema 版本历史表 §记录了 v1-v8 八版迁移：

| 版本 | 描述 |
|:---:|------|
| v1 | Initial schema: tasks + events + knowledge + gates + indexes + views |
| v2 | task_files N:N mapping + namespace + seq columns |
| v3 | priority + model_rationale + actual_hours + files_in_scope + tags + completed_at + name→title |
| v4 | knowledge status column |
| v5 | circuit_breaker_state table |
| v6 | TaskCard 24 extension columns |
| v7 | _schema_version + slow_queries + tx_idempotency + wal_autocheckpoint |
| v8 | soft delete: is_deleted + deleted_at |
