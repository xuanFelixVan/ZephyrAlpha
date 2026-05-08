---
task_id: "DB-025-0009"
namespace: "OPS"
seq: 9
title: "职责范围落地——§2.1 九项职责逐条验证任务卡"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
model_rationale: "模块边界审计——逐项对照 9 项职责与 7 个 .py 文件"
fallback_model: "glm-4.7"
safety_level: "medium"
directive: "verify_responsibilities"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
files_in_scope:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\*"
deliverables: []
acceptance: ""
depends_on: ["DB-025-0001"]
tags: ["fn:governance", "ly:cross_layer", "st:active", "mo:manual"]
session_id: null
waiting_for: null
ready_at: null
completed_at: null
created_at: "2026-05-06T23:36:00Z"
updated_at: "2026-05-06T23:36:00Z"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\olap_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\audit_schema.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\query_metrics.py"
downstream_outputs: []
acceptance_criteria:
  - "职责1：task_repo.py 实现 TaskCard CRUD + 状态转换 + events 写入"
  - "职责2：task_repo.py transition() 实现 10 状态机 + G1 门禁"
  - "职责3：atomic_transaction_manager.py 实现跨 SQLite/文件系统两阶段提交 + 幂等 + 补偿"
  - "职责4：sqlite_schema.py 实现 DDL + _MIGRATIONS 注册表 + init_db()"
  - "职责5：olap_engine.py 实现趋势查询 + 聚合 + 摘要"
  - "职责6：olap_engine.py archive_events() 实现冷热分层"
  - "职责7：database_manager.py 实现连接池 + 健康检查 + 备份 + WAL checkpoint + 统计"
  - "职责8：audit_schema.py 实现 AuditQuery + 补偿事件查询 + Schema 漂移检测"
  - "职责9：query_metrics.py 实现 P50/P95/P99 + slow_queries 记录"
rollback_instructions: "若某项职责缺失落位 → 登记到 §20 风险矩阵，追加 R* 条目——职责未覆盖"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§2.1——9 项职责范围 + 落位文件"}
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

# DB-025-0009：职责范围落地——§2.1 九项职责逐条验证

## 任务来源

蓝图 §2.1 定义了 MOD-INF-012 的 9 项职责，每项有明确的说明和落位文件。

## 九项职责验证矩阵

| # | 职责 | 落位文件 | 验证方式 |
|---|------|---------|---------|
| 1 | TaskCard CRUD + 状态转换 + events 写入 | `task_repo.py` | `grep "def create\|def get\|def update\|def upsert\|def delete\|def transition"` |
| 2 | 10 状态机 + G1 门禁 | `task_repo.py` transition() | 代码搜索 transition 函数 |
| 3 | 跨 SQLite/文件系统两阶段提交 + 幂等 + 补偿 | `atomic_transaction_manager.py` | 搜索 `prepare\|commit\|idempotency\|compensat` |
| 4 | DDL + _MIGRATIONS + init_db() 幂等 | `sqlite_schema.py` | 搜索 `_MIGRATIONS\|init_db\|schema_version` |
| 5 | 趋势查询 + 聚合 + 摘要 | `olap_engine.py` | 搜索 `trend\|summary` |
| 6 | 冷热数据分层归档 | `olap_engine.py` archive_events() | 搜索 `archive_events\|parquet` |
| 7 | 连接池 + 健康检查 + 备份 + WAL checkpoint | `database_manager.py` | 搜索 `health_check\|backup\|checkpoint` |
| 8 | 审计查询面板 | `audit_schema.py` | 搜索 `AuditQuery\|drift\|compensation` |
| 9 | 查询性能监控 | `query_metrics.py` | 搜索 `P50\|P95\|P99\|slow_query` |

## 验收标准

- [ ] 9/9 职责在对应文件中存在实现
- [ ] 职责 1-9 的落位文件与蓝图 §2.1 声明一致
- [ ] 若任一职责缺口 → 标记为遗漏并登记风险

## 回滚方案

职责缺口 → 登记为 R* 条目追加到 §20 风险矩阵。不修改源文件。
