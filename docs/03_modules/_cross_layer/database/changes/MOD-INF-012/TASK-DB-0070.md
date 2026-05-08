---
task_id: "DB-025-0070"
namespace: "OPS"
seq: 70
title: "T-DB-004——修复 b_db.yaml SSoT (Phase experimental，P1，0.5h)"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "high"
directive: "modify_and_verify"
idempotent: false
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:registry", "ly:cross_layer", "T-DB-004"]
depends_on: ["DB-025-0036"]
upstream_files: ["D:\\ZephyrAlpha\\architecture-model\\layers\\b_db.yaml"]
downstream_outputs: ["D:\\ZephyrAlpha\\architecture-model\\layers\\b_db.yaml"]
acceptance_criteria:
  - "files 4→7 (3 missing.py追加)"
  - "schema_version→2.1.0"
  - "db_file_path 修正为 D:\\ZephyrAlpha\\docs\\09_audit\\state\\zalpha_metadata.db"
  - "interfaces.contracts 对齐蓝图 §12 的4个CT-DB-*"
rollback_instructions: "git checkout b_db.yaml → 恢复原版"
upstream_files_content_hash: null
allowed_touch: ["D:\\ZephyrAlpha\\architecture-model\\layers\\b_db.yaml"]
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
effective_priority: "P1"
diff_plan_required: true
estimated_context_tokens: 3000
context_window_limit: 128000
---

# DB-025-0070：T-DB-004——修复 b_db.yaml SSoT

§16.4 T-DB-004: 修正 YAML files 4→7 / schema →2.1.0 / contracts 对齐。
