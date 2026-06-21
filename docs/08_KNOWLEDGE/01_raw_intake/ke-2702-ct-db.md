---
module_id: KE-2605
status: active
title: CT-DB-004：运维管理契约
category: module_blueprint
---

# CT-DB-004：运维管理契约

CT-DB-004：运维管理契约

```yaml
contract_id: CT-DB-004
provider: MOD-INF-012 (DatabaseManager)
consumers:
  - MOD-INF-015 (system-telemetry)
  - MOD-INF-001 (capacity-assurance)

operations:
  health_check:
    output: "HealthStatus {healthy, schema_version, db_size_bytes, wal_size_bytes, table_count, integrity_ok}"
    checks: [integrity_check, quick_check, 文件大小, schema版本, 表数量]

  backup:
    input: "label?: str"
    output: "Path (备份文件路径)"
    consistency: "SQLite backup API（非 cp）"
    retention: "7天日备份 + 4周末备份"

  maintenance:
    output: "{vacuum, integrity, wal_truncated, pre_health, post_health}"
    schedule: "cron 每周触发"

  stats:
    output: "{task_count, active_task_count, event_count, gate_count, ke_count, slow_query_count, db_size_mb, wal_size_mb, schema_version}"
```

---
