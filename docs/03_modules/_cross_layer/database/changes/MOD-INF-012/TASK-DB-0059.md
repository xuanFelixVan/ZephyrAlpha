---
task_id: "DB-025-0059"
namespace: "OPS"
seq: 59
title: "v2.0 迁移指南落地——§11 Python 代码块实现验证"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "medium"
directive: "verify_migration"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:migration", "ly:cross_layer"]
depends_on: ["DB-025-0007"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"
acceptance_criteria:
  - "§11.1 init_db()幂等迁移——从旧schema升级：调用init_db()自动检测legacy DB并运行v7/v8迁移"
  - "schema_version()返回值应为8——确认迁移完整执行"
  - "init_db()多次调用不报错、不丢数据——幂等性验证"
  - "迁移代码路径：from zephyr.db.sqlite_schema import init_db, schema_version"
rollback_instructions: "迁移失败 → §20 R*"
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules: []
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M7"]
ai_autonomy_level: "supervised"
construction_status: "pending"
verification_status: "unverified"
parent_task_id: null
epic: "MOD-INF-012-database-v2.2-decomposition"
effective_priority: "P2"
diff_plan_required: false
estimated_context_tokens: 3000
context_window_limit: 128000
---

# DB-025-0059：v2.0 迁移指南落地——§11 Python 代码块

§11: 调用链升级路径: init_db + backup + get_connection。
