---
task_id: "TASK-INF-0251"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.20 + §6.12 B75 + §9 exit code 16"
title: "Submodule/Monorepo 同步回滚——submodule_sync 多仓库一致回滚"
description: |
  实现 Submodule/Monorepo 多仓库同步回滚：
  检测项目是否使用 git submodule 或 Monorepo layout。
  grpdt_root_path 遍历 submodule → 逐模块执行回滚 + 同步更新引用。
  Submodule 指针与主仓库版本不同步 → exit code 16 (SUBMODULE_OUT_OF_SYNC)。
  确保"多仓库视为单版本"——回滚一个不会导致其他 submodule 悬空。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\submodule_sync.py"
    description: "Submodule 同步回滚——多仓库一致回滚 + diff 引用同步"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\submodule_sync.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B75 Submodule 回滚"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "检测 git submodule / Monorepo layout"
  - "逐 submodule 回滚 + 更新主仓库引用"
  - "引用不同步 → exit code 16 (SUBMODULE_OUT_OF_SYNC)"
  - "多仓库版本视为单一单元回滚"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\submodule_sync.py
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
