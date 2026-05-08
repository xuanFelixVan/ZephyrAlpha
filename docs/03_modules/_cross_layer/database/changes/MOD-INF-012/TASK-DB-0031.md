---
task_id: "DB-025-0031"
namespace: "OPS"
seq: 31
title: "集成——system-telemetry (MOD-INF-015) 集成验证"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "low"
directive: "verify_integration"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:integration", "ly:cross_layer"]
depends_on: ["DB-025-0026"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
acceptance_criteria:
  - "system-telemetry → database_manager.stats() + QueryMetrics"
  - "stats 面板数据可消费"
rollback_instructions: "集成断链 → §20 R*"
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

# DB-025-0031：集成——system-telemetry (MOD-INF-015) 集成验证

§7 #5: system-telemetry → database_manager stats 面板.
