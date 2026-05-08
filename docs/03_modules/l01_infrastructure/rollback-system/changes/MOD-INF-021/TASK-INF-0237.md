---
task_id: "TASK-INF-0237"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.6 + §6.12 B61 + 决策 D-021-15 + §9 exit code 14"
title: "温备热切——warm_standby.py + parallel git worktree + <100ms RTO"
description: |
  实现 warm_standby.py：
  维护 git worktree 温备副本包含最近已验证状态。
  Agent 在回滚期间切换到读取备副本——不等待主仓库 git revert 完成。
  RTO 从 ~2s（git revert）降低到 <100ms（worktree 切换）。
  后台异步完成回滚验证后更新温备。
  exit code 14 (WARM_STANDBY_CUTOVER)。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\warm_standby.py"
    description: "温备热切——git worktree 副本维护 + <100ms RTO"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\warm_standby.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B61 温备热切 + D-021-15 决策"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 9000
timeout_minutes: 35
acceptance_criteria:
  - "git worktree add 创建温备副本含最近已验证状态"
  - "回滚时 Agent 切换到读备副本——<100ms 切换"
  - "后台 revert 完成后更新温备 → Agent 切回主仓库"
  - "exit code 14 (WARM_STANDBY_CUTOVER)"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\warm_standby.py
  2. git worktree remove warm_standby/
depends_on:
  - "TASK-INF-0232"
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
