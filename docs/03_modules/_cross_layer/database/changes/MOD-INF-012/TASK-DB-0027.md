---
task_id: "DB-025-0027"
namespace: "OPS"
seq: 27
title: "集成——task-system (MOD-INF-006) 集成验证"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "medium"
directive: "verify_integration"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:integration", "ly:cross_layer"]
depends_on: ["DB-025-0023"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
acceptance_criteria:
  - "task-system 通过 task_repo.py 消费 TaskRepository CRUD + 状态机"
  - "task_repo.transition() 中 G1 门禁调 GateEngine.evaluate()，conn 参数传递正确"
rollback_instructions: "集成断链 → §20 R*"
context_assembly_manifest: []
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

# DB-025-0027：集成——task-system (MOD-INF-006) 集成验证

§7 #1: task-system → task_repo.py 状态机 + 审计互锁。确认 TaskRepository 接口被正确消费。
