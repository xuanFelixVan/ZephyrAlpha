---
task_id: "DB-025-0055"
namespace: "OPS"
seq: 55
title: "AP3 防护——禁止绕过init_db()直接connect：强制入口"
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
depends_on: ["DB-025-0007"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py"
acceptance_criteria:
  - "get_connection() 是唯一获取 SQLite 连接的统一入口"
  - "task_repo 和 ATM 不直接 sqlite3.connect()"
rollback_instructions: "绕过入口 → §20 R*"
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

# DB-025-0055：AP3 防护——禁止绕过init_db()直接connect

§18.3 AP3: get_connection() 作为唯一 SQLite 连接入口。
