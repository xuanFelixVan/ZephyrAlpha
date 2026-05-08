---
task_id: "DB-025-0090"
namespace: "OPS"
seq: 90
title: "Schema 版本历史——v1→v8 八版 DDL 迁移链完整性验证"
tags: ["fn:governance", "ly:cross_layer"]
depends_on: ["DB-025-0007"]
upstream_files: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py"]
acceptance_criteria:
  - "v1 tasks+events+knowledge+gates+indexes+views完整"
  - "v2 task_files N:N+namespace+seq"
  - "v3 priority/model_rationale/actual_hours/files_in_scope/tags/completed_at/title"
  - "v4 knowledge status"
  - "v5 circuit_breaker_state"
  - "v6 24 extension columns"
  - "v7 _schema_version+slow_queries+tx_idempotency+wal_autocheckpoint"
  - "v8 is_deleted+deleted_at"
rollback_instructions: "迁移链断裂 → §20 R03"
---

# DB-025-0090：Schema 版本历史——v1→v8 八版迁移链

Schema History: 8 版本全部落地 _MIGRATIONS。
