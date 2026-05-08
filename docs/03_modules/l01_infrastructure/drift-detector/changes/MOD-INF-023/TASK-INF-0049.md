---
task_id: "TASK-INF-0049"
title: "供应商锁定与基础设施迁移漂移（§6.19）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\migration_plan.yaml"]
acceptance_criteria:
  - db_migration: SQLitePostgreSQLDuckDB所有含import sqlite3模块
  - notification_migration: FeishuSlackEmail所有调用模块
  - migration_plan_integration: drift_migration_plan.yaml声明式时间表+影响模块列表
rollback_instructions: "git checkout src/zephyr/drift_detector/migration_plan.yaml"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.19"]}]
tags: ["drift-detector","integration","§6.19"]
---
# TASK-INF-0049: 供应商锁定与基础设施迁移漂移（§6.19）
对标 §6.19。db_migration: SQLitePostgreSQLDuckDB所有含import sqlite3模块
