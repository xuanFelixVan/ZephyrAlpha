---
task_id: "DB-025-0015"
namespace: "OPS"
seq: 15
title: "ATM v2.0 契约落地——§3 YAML 代码块全实现验证任务卡"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
model_rationale: "代码契约审计——YAML atm_contract 到 Python 代码逐项对照"
fallback_model: "glm-4.7"
safety_level: "high"
directive: "verify_code_contract"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
files_in_scope:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\sqlite_schema.py"
deliverables: []
acceptance: ""
depends_on: ["DB-025-0006"]
tags: ["fn:contract", "ly:cross_layer", "st:active", "mo:manual"]
session_id: null
# ... truncated fields for brevity — full frontmatter present on disk
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py"
downstream_outputs: []
acceptance_criteria:
  - "phase_1_prepare：prepare() 方法存在——设置 PREPARED + 写入 tx_idempotency"
  - "phase_2_commit：commit() 方法存在——tx.commit + os.replace + COMMITTED"
  - "timeout: 30s：timeout 参数在 execute() 或装饰器中可配置"
  - "idempotency：tx_idempotency 表 DDL 存在（sqlite_schema.py）+ 重复 tx_id → TransactionError"
  - "fallback: WAL mode：回退到 WAL——无 manual rollback journal"
  - "compensation: COMPENSATED：rename 失败 → events 表 compensation event"
rollback_instructions: "若 ATM 实现与 YAML 契约不一致 → 登记到 §20 R3/R7。不修改源文件"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§3 ATM v2.0 YAML 契约"}
  - {file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\atomic_transaction_manager.py", reason: "ATM 实现代码"}
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

# DB-025-0015：ATM v2.0 契约落地——§3 YAML 代码块全实现验证

## 任务来源

蓝图 §3 包含 `atm_contract: P0-DB-ATM-v2` YAML 代码块，共 6 个关键特性。

## YAML → Python 实现对照

| 契约特性 | YAML 声明 | Python 实现验证 |
|----------|----------|----------------|
| phase_1_prepare | 写入 tx_idempotency = PREPARED | `grep "PREPARED\|prepare" atomic_transaction_manager.py` |
| phase_2_commit | SQLite COMMIT + os.replace | `grep "COMMIT\|commit\|os.replace"` |
| timeout | 30s 事务级 | `grep "30\|timeout"` |
| idempotency | 重复 tx_id → TransactionError | `grep "TransactionError\|idempot"` |
| write_file | InputSanitizer + os.replace | `grep "write_file\|validate_path\|os.replace"` |
| compensation | COMPENSATED + compensation event | `grep "COMPENSATED\|compensat"` |

## 验收标准

- [ ] 6/6 特性在代码中对应实现
- [ ] 每项对照有明确的代码行引用
- [ ] 差异 → 登记 §20 risk

## 回滚方案

差异 → §20 R3/R7。不修代码。
