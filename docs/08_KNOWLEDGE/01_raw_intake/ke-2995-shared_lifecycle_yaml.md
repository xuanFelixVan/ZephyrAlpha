---
module_id: KE-2895----------000
status: active
title: shared-lifecycle.yaml —— 引擎 + shared_lifecycle_manager.py 自动维护
category: module_blueprint
---

# shared-lifecycle.yaml —— 引擎 + shared_lifecycle_manager.py 自动维护

shared-lifecycle.yaml —— 引擎 + shared_lifecycle_manager.py 自动维护
lifecycle_entries:
  - shared_func: "zephyr.shared.time_utils.legacy_timestamp"
    status: "deprecated"
    deprecated_since: "2026-05-01"
    stale_score: 45
    replacement: "zephyr.shared.time_utils.now_iso"
    active_caller_count: 3
    callers:
      - "orchestrator/backup_scheduler.py"
      - "context-engine/legacy_adapter.py"
    grace_period_ends: "2026-05-15"
    sunset_date: "2026-06-01"
    migration_diff: "s/legacy_timestamp()/now_iso()/g"
```
