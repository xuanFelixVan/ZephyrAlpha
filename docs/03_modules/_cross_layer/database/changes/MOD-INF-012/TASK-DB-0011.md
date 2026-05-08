---
task_id: "DB-025-0011"
namespace: "OPS"
seq: 11
title: "七文件组成验证——§2.3 文件与职责对照任务卡"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
model_rationale: "文件清单验证——按文件名逐一对磁盘存在性"
fallback_model: "glm-4.7"
safety_level: "low"
directive: "verify_files"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
files_in_scope:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\*"
deliverables: []
acceptance: ""
depends_on: ["DB-025-0009"]
tags: ["fn:governance", "ly:cross_layer", "st:active", "mo:manual"]
session_id: null
waiting_for: null
ready_at: null
completed_at: null
created_at: "2026-05-06T23:36:00Z"
updated_at: "2026-05-06T23:36:00Z"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
downstream_outputs: []
acceptance_criteria:
  - "task_repo.py → D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py 存在 + 非空"
  - "atomic_transaction_manager.py → 存在 + 非空"
  - "sqlite_schema.py → 存在 + 非空"
  - "olap_engine.py → 存在 + 非空"
  - "database_manager.py → 存在 + 非空"
  - "audit_schema.py → 存在 + 非空"
  - "query_metrics.py → 存在 + 非空"
rollback_instructions: "若某文件缺失 → 登记为 R* 追加到 §20 风险矩阵，P1 级别——声称已实现但文件不在磁盘上"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§2.3——7 文件清单"}
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules: []
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M7"]
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
estimated_context_tokens: 3000
context_window_limit: 128000
effective_priority: "P2"
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

# DB-025-0011：七文件组成验证——§2.3 文件与职责对照

## 任务来源

蓝图 §2.3 列出 7 个 .py 文件及其职责。

## 七文件磁盘存在性验证

| 文件 | 完整绝对路径 | 期望 |
|------|------------|:---:|
| `task_repo.py` | `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` | EXISTS |
| `atomic_transaction_manager.py` | `D:\ZephyrAlpha\src\zephyr\db\atomic_transaction_manager.py` | EXISTS |
| `sqlite_schema.py` | `D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py` | EXISTS |
| `olap_engine.py` | `D:\ZephyrAlpha\src\zephyr\db\olap_engine.py` | EXISTS |
| `database_manager.py` | `D:\ZephyrAlpha\src\zephyr\db\database_manager.py` | EXISTS |
| `audit_schema.py` | `D:\ZephyrAlpha\src\zephyr\db\audit_schema.py` | EXISTS |
| `query_metrics.py` | `D:\ZephyrAlpha\src\zephyr\db\query_metrics.py` | EXISTS |

## 验收标准

- [ ] 7/7 文件存在且非空（`Get-ChildItem` 验证）
- [ ] 无多余 .py 文件（glob 结果 = 7）
- [ ] 文件名与蓝图 §2.3 完全一致

## 回滚方案

文件缺失 → P1 风险登记到 §20。声称已实现但文件不及。
