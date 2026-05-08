---
task_id: "DB-025-0020"
namespace: "OPS"
seq: 20
title: "源码文件清单验证——§6.1 七份源码完整绝对路径确认"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "low"
directive: "verify_file_scope"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:governance", "ly:cross_layer", "st:active", "mo:manual"]
depends_on: ["DB-025-0011"]
upstream_files:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\olap_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\audit_schema.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\query_metrics.py"
acceptance_criteria:
  - "7/7 文件在 §6.1 声明的路径上存在 + 非空"
  - "Glob src/zephyr/db/*.py 结果 = 7 个文件（不多不少）"
rollback_instructions: "缺少文件 → §20 R07 P1 SSoT 漂移"
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
effective_priority: "P2"
diff_plan_required: false
estimated_context_tokens: 3000
context_window_limit: 128000
---

# DB-025-0020：源码文件清单验证——§6.1 七份源码完整绝对路径确认

§6.1 列出的 7 个源码文件需全部存在且非空: atomic_transaction_manager.py, olap_engine.py, sqlite_schema.py, task_repo.py, database_manager.py, audit_schema.py, query_metrics.py。

验收: 7/7 EXISTS + NON-EMPTY。
