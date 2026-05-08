---
task_id: "TASK-INF-0220"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.3 + §6.10 B41/B52 + 决策 D-021-09"
title: "定期回滚演练调度器——每周 DiRT drill + 混沌场景注入"
description: |
  实现 rollback_drill.py + 调度器：
  每周六凌晨 3:00 AM 自动触发 drill。
  在 git worktree 副本中执行真实回滚 → 记录 drill 耗时/冲突率/DB 重建完整性。
  混沌场景注入：gc_concurrent/sqlite_locked/disk_90pct/CPU 极限。
  连续 2 次 drill FAIL → P0 Alert → 熔断所有自动回滚（R10）。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_drill.py"
    description: "回滚演练调度器——每周定时 DiRT 演练 + 混沌场景注入"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_drill.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——B41 DiRT 演练 + B52 混沌工程 + D-021-09"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 12000
timeout_minutes: 45
acceptance_criteria:
  - "每周六 3:00 AM 自动触发 rollback drill"
  - "chaos scenarios: gc_concurrent/sqlite_locked/disk_90pct/CPU 极限"
  - "drill 耗时/冲突率/DB 重建完整性记录"
  - "连续 2 次 FAIL → P0 Alert → 熔断所有自动回滚"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\rollback_drill.py
depends_on:
  - "TASK-INF-0210"
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
