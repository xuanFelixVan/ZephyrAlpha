---
task_id: "TASK-INF-0033"
title: "DB Schema 三方对账漂移检测（§6.3）"
module_id: "MOD-INF-023"
feature_id: "MOD-INF-023"
task_type: "implementation"
priority: "P1"
status: "draft"
estimated_effort: "4h"
depends_on: ["TASK-INF-0002"]
upstream_files: ["D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\drift_detector\\drift_engine.py"]
acceptance_criteria:
  - schema_vs_orm: sqlite_master表结构vs SQLAlchemy/peewee model
  - orm_vs_migration: ORM字段vs最新migration文件字段
  - index_consistency: ORM声明索引vs数据库实际索引
rollback_instructions: "git checkout src/zephyr/drift_detector/drift_engine.py"
context_assembly_manifest: [{file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md", sections: ["§6.3"]}]
tags: ["drift-detector","integration","§6.3"]
---
# TASK-INF-0033: DB Schema 三方对账漂移检测（§6.3）
对标 §6.3。schema_vs_orm: sqlite_master表结构vs SQLAlchemy/peewee model
