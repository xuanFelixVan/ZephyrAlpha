---
task_id: "TASK-INF-0222"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.5 + §6.10 B51 + 决策 D-021-07 + AP11"
title: "Forward-Fix 优先决策——评估变更范围后优先 forward-fix 而非 revert"
description: |
  实现 forward_fix_runner.py：
  auto_rollback_trigger 触发前先评估：变更 ≤ 3 文件 AND soft_failure AND 文件未锁定 → 优先 forward-fix。
  forward_fix：产生新 commit 直接修正问题，而非回滚旧 commit。
  连续 2 次 forward-fix 失败 → fallback revert。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\forward_fix_runner.py"
    description: "Forward-Fix 执行器——回滚的替代决策路径：优先 FIX commit 而非 revert"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\forward_fix_runner.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——B51 forward-fix 备选路径 + D-021-07 + §8 AP11"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "forward_fix_runner 评估变更范围 → soft_failure + ≤3 文件 → 优先 forward-fix"
  - "连续 2 次 forward-fix 失败 → fallback revert"
  - "forward_fix commit message 格式：FIX: {原问题描述}"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\forward_fix_runner.py
depends_on:
  - "TASK-INF-0205"
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
