---
task_id: "DB-025-0056"
namespace: "OPS"
seq: 56
title: "AP4 防护——禁止DDL穿插业务代码：DDL聚集在sqlite_schema.py"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "high"
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
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\olap_engine.py"
acceptance_criteria:
  - "task_repo.py/atomic_transaction_manager.py/olap_engine.py 中无 CREATE TABLE/ALTER TABLE/DROP TABLE 语句"
  - "所有 DDL 集中在 sqlite_schema.py _MIGRATIONS 注册表中"
rollback_instructions: "DDL泄漏到业务代码 → §20 R* P1"
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

# DB-025-0056：AP4 防护——禁止DDL穿插业务代码

§18.3 AP4: 禁止在业务代码中嵌入 CREATE TABLE/ALTER TABLE。DaaS 原则。
