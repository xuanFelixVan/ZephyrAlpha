---
task_id: "DB-025-0007"
namespace: "OPS"
seq: 7
title: "DD-04——版本化迁移框架（_MIGRATIONS 注册表）设计决策落地任务卡"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
model_rationale: "DD 技术决策审计——v1-v8 迁移链完整性"
fallback_model: "glm-4.7"
safety_level: "high"
directive: "verify_design_decision"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
files_in_scope:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_sqlite_schema.py"
deliverables: []
acceptance: ""
depends_on: ["DB-025-0001"]
tags: ["fn:architecture", "ly:cross_layer", "st:active", "mo:manual"]
session_id: null
waiting_for: null
ready_at: null
completed_at: null
created_at: "2026-05-06T23:35:00Z"
updated_at: "2026-05-06T23:35:00Z"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_sqlite_schema.py"
downstream_outputs: []
acceptance_criteria:
  - "sqlite_schema.py 中存在 _MIGRATIONS 注册表（v1-v8）"
  - "init_db() 幂等——多次执行不报错，迁移按序执行未运行的"
  - "schema_version() 函数存在——返回当前版本号（应为 8）"
  - "test_sqlite_schema.py 覆盖 init_db 幂等 + 迁移幂等"
rollback_instructions: "若迁移链断裂（版本号不连续）→ 登记到 §20 R03。不修改源文件"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§1.1——版本化迁移设计决策 + Schema版本历史"}
  - {file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py", reason: "_MIGRATIONS 注册表 + init_db()"}
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules: []
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M6", "M7"]
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
construction_status: "pending"
verification_status: "unverified"
parent_task_id: null
epic: "MOD-INF-012-database-v2.2-decomposition"
retry_count: 0
max_retries: 3
retry_backoff_seconds: 60
checkpoint_path: null
estimated_context_tokens: 4000
context_window_limit: 128000
effective_priority: "P1"
diff_plan_required: false
circuit_breaker_open: false
suspend_context_json: null
prompt_version: null
prompt_variant: null
compensation_steps: []
sla_deadline: null
sla_escalation_policy: null
original_priority: null
model_snapshot_pinned: null
thinking_state_json: null
emergency_mode: false
cross_task_learning: false
dependency_fingerprint: null
cancelled_artifacts: []
consumer_impact_report: null
run_consumer_tests: false
replan_proposed: false
modified_files_actual: null
lines_changed_actual: null
context_cache_key: null
---

# DB-025-0007：DD-04——版本化迁移框架（_MIGRATIONS 注册表）设计决策落地

## 任务来源

蓝图 §1.1：「版本化迁移 → 内嵌 _MIGRATIONS 注册表。替代方案：Alembic。选择理由：项目规模用 SQL 内联即可，无需引入 ORM 迁移工具链。」

## Schema 版本历史全景

蓝图 Schema 版本历史表 §记录了 v1-v8 八版迁移：

| 版本 | 描述 |
|:---:|------|
| v1 | Initial schema: tasks + events + knowledge + gates + indexes + views |
| v2 | task_files N:N mapping + namespace + seq columns |
| v3 | priority + model_rationale + actual_hours + files_in_scope + tags + completed_at + name→title |
| v4 | knowledge status column |
| v5 | circuit_breaker_state table |
| v6 | TaskCard 24 extension columns |
| v7 | _schema_version + slow_queries + tx_idempotency + wal_autocheckpoint |
| v8 | soft delete: is_deleted + deleted_at |

## 验收标准

- [ ] _MIGRATIONS 注册表包含 v1-v8 共 8 条迁移记录
- [ ] init_db() 幂等——`python -c "from zephyr.db.sqlite_schema import init_db; init_db(); init_db(); init_db()"` 三次执行不报错
- [ ] schema_version() 返回 8
- [ ] 迁移未运行时自动按序补运行（test_sqlite_schema.py 覆盖）
- [ ] 每个迁移版本有独立的 SQL DDL 块

## 回滚方案

若迁移链有缺口（缺版本或 init_db 不幂等）→ 登记到 §20 R03（Schema 迁移手动高风险），P2 级别。不修改源文件。
