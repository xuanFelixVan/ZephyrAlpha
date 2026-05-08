---
task_id: "DB-025-0046"
namespace: "OPS"
seq: 46
title: "R07 缓解——b_db.yaml SSoT 漂移：T-DB-004修复+CI门禁"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "high"
directive: "verify_risk_mitigation"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:risk", "ly:cross_layer"]
depends_on: ["DB-025-0036"]
upstream_files:
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_db.yaml"
acceptance_criteria:
  - "b_db.yaml 文件清单 4→7, schema_version→2.1.0, db_file_path 修正, contracts 对齐"
  - "CI 门禁: 启动时 glob src/zephyr/db/*.py vs b_db.yaml.files → 不一致阻断"
rollback_instructions: "SSoT 漂移 → §20 R07 '❌ 待处理'"
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
effective_priority: "P1"
diff_plan_required: false
estimated_context_tokens: 3000
context_window_limit: 128000
---

# DB-025-0046：R07 缓解——b_db.yaml SSoT 漂移

Risk: 🟠 P1 — YAML 声明 4.py vs 磁盘 7.py 不一致。缓解: T-DB-004+CI门禁。状态: ❌ 待处理。
