---
task_id: "TASK-INF-0238"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.7 + §6.12 B62"
title: "语义化 Rollback Tag——TASK 边界 tag + before-refactor / after-migration 标签"
description: |
  实现语义化 Rollback Tag 机制：
  在 TASK 边界、大规模重构前/后、迁移操作前/后自动打 git tag：
  `rollback/task-{task_id}:before` / `rollback/task-{task_id}:after`
  `rollback/refactor/{module}:before` / `rollback/refactor/{module}:after`
  `rollback/migration/{migration_id}:before` / `rollback/migration/{migration_id}:after`
  Tag 作为语义化回滚目标——回滚时不需要查 SHA，用 `zephyr rollback --to rollback/refactor/auth:before` 即可。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\semantic_rollback_tag.py"
    description: "语义化 Rollback Tag——TASK/refactor/migration 边界的 git tag 自动管理"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\semantic_rollback_tag.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B62 语义化 Rollback Tag"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "TASK 边界自动 before/after tag"
  - "大规模重构前自动 tag: rollback/refactor/{module}:before"
  - "迁移操作前自动 tag: rollback/migration/{id}:before"
  - "支持 zephyr rollback --to {tag} 语义化目标选择"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\semantic_rollback_tag.py
  2. git tag -d 所有 rollback/* tag
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
