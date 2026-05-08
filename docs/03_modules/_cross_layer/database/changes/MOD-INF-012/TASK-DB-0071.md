---
task_id: "DB-025-0071"
namespace: "OPS"
seq: 71
title: "T-DB-005——verify_backup 恢复验证 (Phase experimental，P2，1.0h)"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "high"
directive: "modify_and_test"
idempotent: false
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 1.0
tags: ["fn:backup", "ly:cross_layer", "T-DB-005"]
depends_on: ["DB-025-0048"]
upstream_files: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"]
downstream_outputs: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"]
acceptance_criteria:
  - "database_manager新增 verify_backup(backup_path) → dict{损伤检查,表完整性,行数一致性,耗时ms}"
  - "test_database_manager 覆盖 verify_backup 功能"
rollback_instructions: "git checkout database_manager.py"
upstream_files_content_hash: null
allowed_touch: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"]
forbidden_touch: []
applicable_rules: []
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M7","M11"]
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

# DB-025-0071：T-DB-005——verify_backup 恢复验证

§16.4: T-DB-005 P2, 1.0h。verify_backup(backup_path) → dict{check,integrity,row_count,elapsed_ms}。
