---
task_id: "TASK-INF-0245"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.14 + §6.12 B69"
title: "env 变量热重载——env_watcher.py + last_env_reload sentinel 文件"
description: |
  实现环境变量热重载：
  env_watcher 监控 .env 文件修改 → 写入 last_env_reload sentinel 文件。
  回滚涉及 .env 变更时 → watcher 检测 sentinel → 通知 Agent 需要 re-source。
  消除"回滚了 .env 但进程仍用旧环境变量"的半回滚盲点。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\env_watcher.py"
    description: "环境变量热重载——监控 .env + last_env_reload sentinel 通知"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\env_watcher.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B69 env 热重载"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "Watchdog 监控 .env 修改"
  - ".env 变更 → 写入 last_env_reload sentinel"
  - "Agent 检测到 sentinel → re-source 环境变量"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\env_watcher.py
depends_on:
  - "TASK-INF-0240"
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
