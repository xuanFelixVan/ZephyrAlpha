---
task_id: "TASK-INF-0213"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 3.4 + §6.2 B14/B72"
title: "Remote Sync 冲突处理——preflight 中检查 remote 超前与网络分区超时"
description: |
  在 rollback_executor preflight 中增加 remote sync 检查：
  git rev-list --count HEAD..origin/main → N>0 时 git pull --rebase 或拒绝回滚。
  git pull 操作加 5s 超时（B72）→ 超时则标记 PREFLIGHT_NO_REMOTE → 仅本地回滚。
  事后通知 Owner "远程同步未确认"。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "preflight_check 新增 remote_sync_check + network_timeout 保护"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.2 B14 remote sync 盲点 + B72 网络分区超时"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 5000
timeout_minutes: 20
acceptance_criteria:
  - "preflight 检查 remote 是否超前 ← N>0 → git pull --rebase 或拒绝"
  - "git pull 超时 5s → PREFLIGHT_NO_REMOTE"
  - "回滚完成后通知 Owner 远程同步状态"
rollback_instructions: |
  1. git checkout HEAD~1 -- D:\ZephyrAlpha\src\zephyr\rollback\rollback_executor.py
depends_on:
  - "TASK-INF-0203"
blocked_by: []
status: "done"
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-021"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
