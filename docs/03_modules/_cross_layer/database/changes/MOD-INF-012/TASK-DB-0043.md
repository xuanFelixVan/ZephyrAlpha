---
task_id: "DB-025-0043"
namespace: "OPS"
seq: 43
title: "R04 缓解——软删除数据残留：is_deleted=1 过滤+物理清理工具"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "low"
directive: "verify_risk_mitigation"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:risk", "ly:cross_layer"]
depends_on: ["DB-025-0017"]
upstream_files:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
acceptance_criteria:
  - "所有 list_by_* 自动过滤 is_deleted=0"
  - "hard_delete() 物理删除存在"
rollback_instructions: "缓解不充分 → §20 R04"
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

# DB-025-0043：R04 缓解——软删除数据残留

Risk: 🟡 P2 — 软删除=写新行，原行仍存在。缓解: is_deleted=1过滤+物理清理。状态: ✅ 缓解。
