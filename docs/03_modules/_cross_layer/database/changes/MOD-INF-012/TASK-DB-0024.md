---
task_id: "DB-025-0024"
namespace: "OPS"
seq: 24
title: "CT-DB-002 ATM 事务契约落地——§12 两阶段提交接口验证"
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
depends_on: ["DB-025-0015"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py"
acceptance_criteria:
  - "transaction: isolation=BEGIN IMMEDIATE, timeout=30s, idempotency=tx_idempotency表去重, compensation=COMPENSATED状态"
  - "write_file: safety=InputSanitizer.validate_path, atomicity=tmp→fsync→os.replace, rollback=.bak文件恢复"
rollback_instructions: "契约差异 → §20 R03/R07"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§12 CT-DB-002 YAML"}
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

# DB-025-0024：CT-DB-002 ATM 事务契约落地

Provider: MOD-INF-012 (AtomicTransactionManager). Consumers: MOD-INF-006, MOD-INF-010.
