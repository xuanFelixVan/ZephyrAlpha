---
task_id: "DB-025-0054"
namespace: "OPS"
seq: 54
title: "AP2 防护——不同环境PRAGMA一致性：统一环境感知配置"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "medium"
directive: "verify_anti_pattern"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:anti_pattern", "ly:cross_layer"]
depends_on: ["DB-025-0004"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"
acceptance_criteria:
  - "get_db_connection() 统一设置 PRAGMA journal_mode/busy_timeout/wal_autocheckpoint"
  - "不同 env（Windows/macOS/Linux CI）使用相同 PRAGMA 配置"
rollback_instructions: "环境差异 → §20 R*"
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

# DB-025-0054：AP2 防护——不同环境PRAGMA一致性

§18.3 AP2: 统一 init_db() 设定所有 PRAGMA。
