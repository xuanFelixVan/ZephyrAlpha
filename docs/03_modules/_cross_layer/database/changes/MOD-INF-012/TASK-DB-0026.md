---
task_id: "DB-025-0026"
namespace: "OPS"
seq: 26
title: "CT-DB-004 运维管理契约落地——§12 健康检查+备份+维护接口验证"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "high"
directive: "verify_contract"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:contract", "ly:cross_layer", "st:active", "mo:manual"]
depends_on: ["DB-025-0008"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"
acceptance_criteria:
  - "health_check: output=HealthStatus{healthy,schema_version,db_size_bytes,wal_size_bytes,table_count,integrity_ok}, checks=[integrity_check, quick_check, 文件大小, schema, 表数]"
  - "backup: input=label?, output=Path, consistency=SQLite backup API, retention=7天+4周末"
  - "maintenance: output={vacuum,integrity,wal_truncated,pre_health,post_health}, schedule=cron每周"
  - "stats: output={task_count,active_task_count,...,slow_query_count,db_size_mb,wal_size_mb,schema_version}"
rollback_instructions: "差异 → §20 R09备份未验证"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§12 CT-DB-004 YAML"}
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules: []
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M6", "M7"]
ai_autonomy_level: "supervised"
construction_status: "pending"
verification_status: "unverified"
parent_task_id: null
epic: "MOD-INF-012-database-v2.2-decomposition"
effective_priority: "P1"
diff_plan_required: false
estimated_context_tokens: 4000
context_window_limit: 128000
---

# DB-025-0026：CT-DB-004 运维管理契约落地

Provider: MOD-INF-012 (DatabaseManager). Consumers: MOD-INF-015, MOD-INF-001.
