---
task_id: "DB-025-0002"
namespace: "OPS"
seq: 2
title: "目标落地——§1.2 六项目标逐条验收任务卡"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
model_rationale: "结构化验收项——逐条对照验证，DeepSeek 精确匹配"
fallback_model: "glm-4.7"
safety_level: "medium"
directive: "verify_against_code"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 1.0
actual_hours: 0
files_in_scope:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\olap_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\query_metrics.py"
deliverables: []
acceptance: ""
depends_on: ["DB-025-0001"]
tags: ["fn:governance", "ly:cross_layer", "st:active", "mo:manual"]
session_id: null
waiting_for: null
ready_at: null
completed_at: null
created_at: "2026-05-06T23:34:00Z"
updated_at: "2026-05-06T23:34:00Z"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\olap_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\query_metrics.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_task_repo.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_atomic_transaction_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_olap_engine.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_sqlite_schema.py"
downstream_outputs: []
acceptance_criteria:
  - "目标1：执行 pytest test_task_repo.py — 所有 CRUD 操作 < 50ms，query_metrics P95 < 50ms 确认"
  - "目标2：执行 pytest test_atomic_transaction_manager.py — ATM execute 全部路径有测试覆盖，补偿事件链路完整"
  - "目标3：database_manager.py 中 health_check() 方法存在且能自动恢复"
  - "目标4：olap_engine.py 中 archive_events() 方法存在，归档后 events 表行数 ≤ 阈值"
  - "目标5：database_manager.py 中 ai_diagnostic_report() 返回结构化 dict，含 verdict + action"
  - "目标6：多次执行 init_db() 不报错且数据不丢失（test_sqlite_schema.py 已覆盖）"
rollback_instructions: "若有任一目标未通过验收 → 登记未达标项到蓝图 §20 风险矩阵，追加新 R* 条目，不修改代码文件"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "六项目标定义真源——§1.2"}
  - {file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py", reason: "目标1/6——TaskCard CRUD 性能"}
  - {file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py", reason: "目标2——ATM 原子事务"}
  - {file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\database_manager.py", reason: "目标3/5——健康检查/诊断报告"}
  - {file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\olap_engine.py", reason: "目标4——冷热分层"}
  - {file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py", reason: "目标6——init_db() 幂等"}
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules:
  - {module_id: "GOV-TASK-005", section: "全篇", reason: "关闭三步法——目标验收"}
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M7", "M11"]
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
estimated_context_tokens: 5000
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

# DB-025-0002：目标落地——§1.2 六项目标逐条验收

## 任务来源

蓝图 MOD-INF-012 §1.2 定义了 6 项可衡量的模块目标，每项目标有明确的验收标准。

## 六项目标逐条验收

| # | 目标 | 验收标准 | 验收方式 |
|---|------|---------|---------|
| 1 | 所有 TaskCard CRUD < 50ms | 含状态转换 + events 写入 | `pytest tests/unit/test_task_repo.py -v` + 检查 query_metrics P95 |
| 2 | 跨 SQLite/文件系统原子事务零不一致 | ATM execute 全部路径有测试 + 补偿事件链路完整 | `pytest tests/unit/test_atomic_transaction_manager.py -v` |
| 3 | DB 单点故障 5 分钟内自动恢复 | 健康检查自动检测 + 最新备份自动恢复（待 T-DB-005） | 审查 `database_manager.py` health_check() + backup() 方法 |
| 4 | events 表永不超过 30 天热数据 | archive_events 每次执行后 events 表行数 ≤ 阈值 | 审查 `olap_engine.py` archive_events() 方法 |
| 5 | AI Agent 可零上下文消费 DB 诊断信息 | ai_diagnostic_report() 返回结构化 dict，含 verdict + action | 审查 `database_manager.py` ai_diagnostic_report() 方法签名与返回值 |
| 6 | init_db() 幂等——任意环境可重复执行 | 多次执行不报错、不丢数据、迁移按序执行未运行的 | `pytest tests/unit/test_sqlite_schema.py -v` |

## 验收标准

- [ ] 目标 1–6 全部通过 pytest（4 份已有测试 + 3 份待补测试）
- [ ] 目标 1 验证：P95 查询延迟 < 50ms
- [ ] 目标 2 验证：补偿事件写入 events 表可追溯
- [ ] 目标 3 验证：health_check() 方法存在且可通过 PRAGMA integrity_check
- [ ] 目标 4 验证：archive_events() 方法存在且归档路径 `D:\ZephyrAlpha\data\warehouse\` 可写
- [ ] 目标 5 验证：`ai_diagnostic_report()` 返回字段含 `verdict` + `action`
- [ ] 目标 6 验证：`init_db()` 调用 ≥ 3 次不报错（test_sqlite_schema.py 证明）

## 回滚方案

任一目标未达标 → 不修改代码。将未达标项登记到蓝图 §20 风险矩阵追加条目（如 R14），由 Owner/后续 Phase 处理。

## 上下文装配清单

| 文件 | 用途 |
|------|------|
| `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\blueprint.md` §1.2 | 六项可衡量目标 |
| `D:\ZephyrAlpha\src\zephyr\db\task_repo.py` | 验证 CRUD 性能（目标1） |
| `D:\ZephyrAlpha\src\zephyr\db\atomic_transaction_manager.py` | 验证 ATM 事务（目标2） |
| `D:\ZephyrAlpha\src\zephyr\db\database_manager.py` | 验证健康检查/诊断（目标3/5） |
| `D:\ZephyrAlpha\src\zephyr\db\olap_engine.py` | 验证冷热分层（目标4） |
| `D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py` | 验证 init_db 幂等（目标6） |
