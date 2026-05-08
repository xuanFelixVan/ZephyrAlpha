---
task_id: "DB-025-0006"
namespace: "OPS"
seq: 6
title: "DD-03——ATM v2.0 两阶段提交设计决策落地任务卡"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
model_rationale: "DD 技术决策审计——ATM v2.0 四个状态 + tx_idempotency + compensation"
fallback_model: "glm-4.7"
safety_level: "high"
directive: "verify_design_decision"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
files_in_scope:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_atomic_transaction_manager.py"
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
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_atomic_transaction_manager.py"
downstream_outputs: []
acceptance_criteria:
  - "ATM 实现两阶段提交：phase_1_prepare + phase_2_commit"
  - "tx_idempotency 表用于去重——同一 tx_id 重复调用抛 TransactionError"
  - "compensating_transaction 已实现（SQLite COMMIT 成功但文件 rename 失败 → COMPENSATED）"
  - "事务超时 30s 配置存在"
  - "write_file 使用 InputSanitizer.validate_path + os.replace(tmp, target)"
rollback_instructions: "若 ATM 实现有缺陷 → 登记到 §20 风险矩阵 R3/R7。不修改源文件"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§3 ATM v2.0 契约 + §1.1 设计决策"}
  - {file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py", reason: "ATM 核心代码"}
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules:
  - {module_id: "ADR-0030", section: "全篇", reason: "SQLite 原子事务要求"}
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

# DB-025-0006：DD-03——ATM v2.0 两阶段提交设计决策落地

## 任务来源

蓝图 §1.1 + §3：「原子事务 → ATM v2.0 两阶段提交。替代方案：2PC 经典模式。选择理由：跨 SQLite/文件系统保证原子性——既写 DB 又写文件时不能半成功。」

## ATM v2.0 关键特性验证

| # | 特性 | 蓝图要求 | 验证方式 |
|---|------|---------|---------|
| 1 | 两阶段提交 | phase_1_prepare → phase_2_commit | 审查 `atomic_transaction_manager.py` |
| 2 | 幂等去重 | tx_idempotency 表 + 重复 tx_id → TransactionError | 搜索 `tx_idempotency` / `TransactionError` |
| 3 | 补偿事务 | rename 失败 → compensation event + COMPENSATED | 搜索 `compensat` |
| 4 | 超时控制 | 30s 事务级超时，超时自动 ROLLBACK | 搜索 `timeout` / `30` |
| 5 | 文件原子写入 | tmp → fsync → os.replace | 搜索 `os.replace` / `tmp` |

## 验收标准

- [ ] atm_contract P0-DB-ATM-v2 的 5 项全部在代码中落地
- [ ] pytest test_atomic_transaction_manager.py 通过（18+ 测试）
- [ ] tx_idempotency 表在 sqlite_schema.py 中有 DDL 定义
- [ ] compensating_transaction 写入 events 表可追踪

## 回滚方案

若验证失败 → 登记到 §20 R3/R7 风险矩阵条目。不修改源文件。
