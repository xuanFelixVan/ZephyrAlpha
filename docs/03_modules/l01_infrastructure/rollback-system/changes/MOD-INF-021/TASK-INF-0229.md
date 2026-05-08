---
task_id: "TASK-INF-0229"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.12 + §6.10 B50"
title: "Checkpoint GC 策略——快照保留上限 100 + 90 天 max_age + 定期清理"
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\checkpoint_gc.py"
    description: "Checkpoint GC——快照保留策略(max 100/max 90 天)+定期清理"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\checkpoint_gc.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——B50 快照保留策略"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 4000
timeout_minutes: 15
acceptance_criteria:
  - "max_snapshots=100 / max_age=90天"
  - "TASK 边界全量 dump 永不删除"
  - "zephyr rollback gc 命令手动触发清理"
rollback_instructions: "1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\checkpoint_gc.py"
depends_on: ["TASK-INF-0201"]
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
