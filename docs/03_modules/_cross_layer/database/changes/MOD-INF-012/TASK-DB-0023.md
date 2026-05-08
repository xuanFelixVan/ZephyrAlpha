---
task_id: "DB-025-0023"
namespace: "OPS"
seq: 23
title: "CT-DB-001 task_repo CRUD 契约落地——§12 YAML 契约全量验证"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "medium"
directive: "verify_contract"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:contract", "ly:cross_layer", "st:active", "mo:manual"]
depends_on: ["DB-025-0016"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
acceptance_criteria:
  - "create: input=Task(62 fields), output=TaskCard, errors=[P0InflationFrozenError, P0InflationWarning, IntegrityError], idempotency=task_id UNIQUE"
  - "get: input=task_id:str, output=TaskCard|None, filter=is_deleted=0"
  - "transition: input=task_id+to_status+session_id?, output=TaskCard, errors=[TaskNotFoundError, InvalidTransitionError, GateViolationError], atomicity=G1+状态+events 在同一事务"
  - "upsert: input=Task+files?, output=TaskCard, semantics=ON CONFLICT DO UPDATE 保留created_at"
  - "delete: input=task_id:str, output=bool, semantics=软删除"
  - "list_by_*: 支持7种过滤器，自动排除is_deleted=0"
rollback_instructions: "契约差异 → §20 R07 SSoT漂移"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§12 CT-DB-001 YAML"}
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

# DB-025-0023：CT-DB-001 task_repo CRUD 契约落地

Provider: MOD-INF-012 (TaskRepository). Consumers: MOD-INF-006, MOD-INF-009, MOD-INF-013.

验收: 6 operations 全部在代码中实现。
