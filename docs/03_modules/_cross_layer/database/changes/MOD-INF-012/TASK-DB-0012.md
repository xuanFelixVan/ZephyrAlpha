---
task_id: "DB-025-0012"
namespace: "OPS"
seq: 12
title: "必备链接验证——§0 八项必备链接存在性确认任务卡"
status: "PENDING"
priority: "P2"
phase: 0
execution_model: "deepseek-v4-pro"
model_rationale: "文件路径验证——逐项确认 8 个必备链接磁盘存在"
fallback_model: "glm-4.7"
safety_level: "low"
directive: "verify_links"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
files_in_scope: []
deliverables: []
acceptance: ""
depends_on: ["DB-025-0001"]
tags: ["fn:governance", "ly:cross_layer", "st:active", "mo:manual"]
session_id: null
waiting_for: null
ready_at: null
completed_at: null
created_at: "2026-05-06T23:37:00Z"
updated_at: "2026-05-06T23:37:00Z"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\blueprint-architecture-standard.md"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\module-id-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\adr\\adr-0030-sqlite-task-metadata-store.md"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\adr\\adr-0041-session-handoff-protocol.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\_registry\\catalogs\\ai-autonomy-authority-registry.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_db.yaml"
downstream_outputs: []
acceptance_criteria:
  - "8/8 必备链接文件在磁盘上存在（os.path.exists() 或 Test-Path 验证）"
rollback_instructions: "若某链接文件缺失 → 登记到 §20 风险矩阵——必备链接断裂"
context_assembly_manifest: []
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules:
  - {module_id: "PS-STD-002", section: "§3.1~§3.2", reason: "必备链接必要性——蓝图铁律#2"}
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

# DB-025-0012：必备链接验证——§0 八项必备链接存在性确认

## 任务来源

蓝图 §0 必备链接表列出 8 个上游文件。蓝图铁律 #2：必备链接不可省略。

## 八项链接逐项验证

| # | 文件 | 完整绝对路径 | 检查 |
|---|------|------------|:---:|
| 1 | metadata-registry.md | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` | EXISTS? |
| 2 | directory-structure-standard.md | `D:\ZephyrAlpha\docs\01_policies_and_standards\governance\document\directory-structure-standard.md` | EXISTS? |
| 3 | blueprint-architecture-standard.md | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\blueprint-architecture-standard.md` | EXISTS? |
| 4 | module-id-registry.yaml | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture-model\module-id-registry.yaml` | EXISTS? |
| 5 | adr-0030 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0030-sqlite-task-metadata-store.md` | EXISTS? |
| 6 | adr-0041 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\adr\adr-0041-session-handoff-protocol.md` | EXISTS? |
| 7 | ai-autonomy-authority-registry.md | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai-autonomy-authority-registry.md` | EXISTS? |
| 8 | b_db.yaml | `D:\ZephyrAlpha\architecture-model\layers\b_db.yaml` | EXISTS? |

## 验收标准

- [ ] 8/8 文件存在
- [ ] 缺链 → P1 风险登记

## 回滚方案

缺失 → §20 R*。不修复源码。
