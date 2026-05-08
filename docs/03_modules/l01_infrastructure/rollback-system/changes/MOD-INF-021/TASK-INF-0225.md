---
task_id: "TASK-INF-0225"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.8 + §6.10 B45 + B67"
title: "Down-migration 脚本自动生成——pre-commit hook + .sh/.ps1 双版本"
description: |
  实现 down_migration_generator.py：
  pre-commit hook 自动生成 data/rollback/down/{commit_sha}.sh + {commit_sha}.ps1。
  含反向 SQL + 反向文件操作。full_revert 优先使用 down script 而非 git revert。
  down script 生成失败 → 拒绝 commit。
  跨平台 Shell 兼容：Bash .sh + PowerShell .ps1（B67）。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\down_migration_generator.py"
    description: "Down-migration 脚本生成器——pre-commit hook 自动生成反向脚本(.sh+.ps1)"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\down_migration_generator.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——B45 down-migration 生成 + B67 跨平台 Shell"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "pre-commit hook 调用 down_migration_generator 生成反向脚本"
  - "输出双版本：{sha}.sh + {sha}.ps1"
  - "down script 生成失败 → 拒绝 commit"
  - "full_revert 优先使用 down script"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\down_migration_generator.py
depends_on:
  - "TASK-INF-0201"
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
