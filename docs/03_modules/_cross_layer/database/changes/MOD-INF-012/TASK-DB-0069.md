---
task_id: "DB-025-0069"
namespace: "OPS"
seq: 69
title: "T-DB-003——补全 test_query_metrics.py (Phase experimental，P2，1.0h)"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "low"
directive: "create_and_test"
idempotent: false
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 1.0
tags: ["fn:test", "ly:cross_layer", "T-DB-003"]
depends_on: ["DB-025-0065"]
upstream_files: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\query_metrics.py"]
downstream_outputs: ["D:\\ZephyrAlpha\\tests\\unit\\test_query_metrics.py"]
acceptance_criteria:
  - "新建 test_query_metrics.py，覆盖 P50/P95/P99 + slow_queries 记录 + cleanup + summary"
  - "pytest 通过，覆盖率 ≥80%"
rollback_instructions: "不通过 → git checkout"
upstream_files_content_hash: null
allowed_touch: ["D:\\ZephyrAlpha\\tests\\unit\\test_query_metrics.py"]
forbidden_touch: ["D:\\ZephyrAlpha\\src\\zephyr\\db\\query_metrics.py"]
applicable_rules: []
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M7","M11"]
ai_autonomy_level: "supervised"
construction_status: "pending"
verification_status: "unverified"
parent_task_id: null
epic: "MOD-INF-012-database-v2.2-decomposition"
effective_priority: "P2"
diff_plan_required: false
estimated_context_tokens: 4000
context_window_limit: 128000
---

# DB-025-0069：T-DB-003——补全 test_query_metrics.py

§16.4 T-DB-003: Phase experimental, P2, 1.0h。覆盖 P50/P95/P99/slow_queries/summary。
