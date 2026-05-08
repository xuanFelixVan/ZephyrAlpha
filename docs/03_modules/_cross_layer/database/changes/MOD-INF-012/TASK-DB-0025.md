---
task_id: "DB-025-0025"
namespace: "OPS"
seq: 25
title: "CT-DB-003 OLAP 查询契约落地——§12 趋势查询+归档接口验证"
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
depends_on: ["DB-025-0005"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\olap_engine.py"
acceptance_criteria:
  - "task_progress_trend: period支持day|week|month, limit=1-10000, phase可选, sql_injection=参数化+白名单"
  - "compliance_rate_trend: 同上+gate_id可选"
  - "knowledge_activation_trend: 同上+category可选"
  - "archive_events: days默认30, archive_dir可选, output={archived_count, archive_files, deleted_count}"
  - "query_unified_events: UNION ALL (SQLite热+Parquet冷)"
rollback_instructions: "差异 → §20 R05 DuckDB依赖"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§12 CT-DB-003 YAML"}
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

# DB-025-0025：CT-DB-003 OLAP 查询契约落地

Provider: MOD-INF-012 (OLAPEngine). Consumers: MOD-INF-010, MOD-INF-015.
