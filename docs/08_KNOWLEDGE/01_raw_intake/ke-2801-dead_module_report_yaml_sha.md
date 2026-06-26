---
module_id: KE-2704----sha-000
status: active
title: dead_module_report.yaml —— shared_lifecycle_manager.py 产出
category: module_blueprint
ttl: permanent
---

# dead_module_report.yaml —— shared_lifecycle_manager.py 产出

dead_module_report.yaml —— shared_lifecycle_manager.py 产出
dead_modules:
  - module: "src/zephyr/shared/legacy_adapters.py"
    status: "DEAD"
    functions_all_deprecated_since: "2026-02-01"
    last_caller_migrated: "2026-04-15"
    days_since_last_modification: 95
    recommendation: "所有函数已退役且无调用方——建议删除此文件以减少认知负荷"
    dry_run_delete: "2026-07-15"      # 建议的安全删除日期（再等 15 天确认）
```
