---
task_id: "DB-025-0008"
namespace: "OPS"
seq: 8
title: "DD-05——SQLite Backup API 备份策略设计决策落地任务卡"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
model_rationale: "DD 技术决策审计——验证 backup API vs cp 的实现正确性"
fallback_model: "glm-4.7"
safety_level: "high"
directive: "verify_design_decision"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
files_in_scope:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"
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
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"
downstream_outputs: []
acceptance_criteria:
  - "database_manager.py 中 backup() 方法使用 sqlite3 backup API（非 os.copy / shutil.copy）"
  - "备份目录为 D:\\ZephyrAlpha\\data\\backups\\"
  - "备份保留策略：7天日备份 + 4周末备份"
  - "backup() 返回备份文件完整路径"
rollback_instructions: "若 backup 使用 cp 而非 SQLite backup API → 登记为 R* 追加到 §20 风险矩阵：DD-05 备份策略未正确实现"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§1.1——SQLite backup API 设计决策"}
  - {file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py", reason: "backup() 方法代码"}
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

# DB-025-0008：DD-05——SQLite Backup API 备份策略设计决策落地

## 任务来源

蓝图 §1.1：「备份策略 → SQLite backup API（非 cp）。替代方案：pg_dump / S3。选择理由：使用 SQLite 内置 API 保证备份一致性。」

## 落地验证清单

| # | 验证项 | 确认方式 |
|---|--------|---------|
| 1 | backup() 使用 `source.backup(dest)` API | 代码搜索 `backup(` |
| 2 | 备份路径为 `D:\ZephyrAlpha\data\backups\` | 搜索 "backups" 目录引用 |
| 3 | 保留策略——7 天日备份 | 搜索日期相关文件名格式 |
| 4 | 保留策略——4 周末备份 | 搜索 week 相关逻辑 |
| 5 | 不使用 os.copy / shutil.copy | 确认无此类调用 |

## 验收标准

- [ ] backup() 使用 `sqlite3.Connection.backup()` 方法
- [ ] 不能是 `shutil.copy2(db_path, backup_path)` 或 `os.system("cp ...")`
- [ ] 备份文件名含时间戳（可在 backup 目录下验证）
- [ ] maintenance() 中有旧备份清理逻辑

## 回滚方案

若 backup 实现错误（使用 cp 而非 SQLite backup API）→ 登记到 §20 风险矩阵，追加 R* 条目——备份可能不一致。
