---
task_id: "DB-025-0065"
namespace: "OPS"
seq: 65
title: "测试覆盖矩阵——§15 7个模块测试覆盖缺口关闭验证"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
fallback_model: "glm-4.7"
safety_level: "medium"
directive: "verify_test_coverage"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
tags: ["fn:test", "ly:cross_layer"]
depends_on: ["DB-025-0045"]
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_task_repo.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_atomic_transaction_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_sqlite_schema.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_olap_engine.py"
acceptance_criteria:
  - "task_repo ✅ (test_task_repo.py存在+通过)"
  - "ATM ✅ (test_atomic_transaction_manager.py存在+通过)"
  - "sqlite_schema ✅ (test_sqlite_schema.py存在+通过)"
  - "olap_engine ✅ (test_olap_engine.py存在+通过)"
  - "database_manager ❌ (待 T-DB-001, Phase experimental)"
  - "audit_schema ❌ (待 T-DB-002, Phase experimental)"
  - "query_metrics ❌ (待 T-DB-003, Phase experimental)"
  - "输出 test_coverage_gap_report: 3/7 missing → Priority P1"
rollback_instructions: "3缺口 → §20 R06 P1"
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
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
effective_priority: "P1"
diff_plan_required: false
estimated_context_tokens: 3000
context_window_limit: 128000
---

# DB-025-0065：测试覆盖矩阵——§15

§15: 4/7 covered (✅ task_repo, ATM, sqlite_schema, olap_engine). 3 gaps: database_manager, audit_schema, query_metrics → T-DB-001~003.
