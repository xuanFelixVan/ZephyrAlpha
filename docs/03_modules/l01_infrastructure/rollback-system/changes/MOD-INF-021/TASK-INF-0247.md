---
task_id: "TASK-INF-0247"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.16 + §6.12 B71"
title: "Owner 目标覆盖 CLI——zephyr rollback --to 强制覆盖 + ACL 权限检查"
description: |
  在 zephyr_rollback_cli 中新增 --to 参数：
  允许 Owner 指定回滚到特定 SHA / tag / branch。
  ACL 权限检查：--to 操作的执行者必须为 Owner（不可由 AI agent 自行指定）。
  --to 权限验证失败 → 拒绝 + 审计日志。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\zephyr_rollback_cli"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "集成 --to 参数 ACL 权限验证 — Owner-only"
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
    reason: "本蓝图——§6.12 B71 Owner 目标覆盖"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "zephyr rollback --to <SHA|tag|branch> 可用"
  - "ACL 验证：仅 Owner 可使用 --to"
  - "非 Owner --to 尝试 → 拒绝 + 审计日志"
rollback_instructions: |
  1. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py
depends_on:
  - "TASK-INF-0215"
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
