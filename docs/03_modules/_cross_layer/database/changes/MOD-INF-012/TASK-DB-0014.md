---
task_id: "DB-025-0014"
namespace: "OPS"
seq: 14
title: "涉及文件范围验证——§0 十项文件存在性确认任务卡"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
model_rationale: "文件范围验证——逐项确认 10 项文件/目录的存在性"
fallback_model: "glm-4.7"
safety_level: "low"
directive: "verify_file_scope"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
files_in_scope:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\*"
  - "D:\\ZephyrAlpha\\data\\backups\\"
  - "D:\\ZephyrAlpha\\data\\warehouse\\"
deliverables: []
acceptance: ""
depends_on: ["DB-025-0011"]
tags: ["fn:governance", "ly:cross_layer", "st:active", "mo:manual"]
session_id: null
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
downstream_outputs: []
acceptance_criteria:
  - "7 个 .py 源文件已确认（= DB-025-0011）"
  - "文档/测试文件确认存在"
  - "数据目录确认存在/可创建"
rollback_instructions: "若文件缺失 → P1 登记 §20 risk"
context_assembly_manifest: []
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

# DB-025-0014：涉及文件范围验证——§0 十项文件存在性确认

## 任务来源

蓝图 "涉及的文件范围" 表列出 10 项文件/目录的完整绝对路径清单。

## 验收标准

- [ ] 7 个 .py 源文件（由 DB-025-0011 验证）
- [ ] 8：`docs/09_audit/state/zalpha_metadata.db` — SQLite 主数据库（可能运行时不生成）
- [ ] 9：`data/backups/` — 备份目录（可创建）
- [ ] 10：`data/warehouse/` — 冷数据归档（可创建）

## 回滚方案

文件缺 → §20 risk register P1。
