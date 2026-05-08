---
task_id: "TASK-INF-0210"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 3.1 + §6.2 B11"
title: "Rollback Simulator + Test Framework——隔离 worktree 中模拟回滚流程"
description: |
  实现 rollback_simulator.py：在临时 git worktree 中模拟回滚流程。
  git worktree add /tmp/rollback-test → revert → verify → cleanup。
  CI 中跑模拟测试，不污染主仓库。集成到 CI pipeline。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_simulator.py"
    description: "回滚模拟器——在临时 git worktree 中模拟回滚流程，CI 集成"
  - path: "D:\\ZephyrAlpha\\tests\\rollback\\test_rollback_simulator.py"
    description: "单元测试——验证模拟回滚流程"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_simulator.py"
  - "D:\\ZephyrAlpha\\tests\\rollback\\test_rollback_simulator.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.2 B11 模拟测试盲点"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "simulate_revert(commit_sha) 在临时 worktree 中执行回滚 → 验证 → 清理"
  - "CI 集成——每次 push 自动跑模拟测试"
  - "不污染主仓库——worktree 隔离"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\rollback_simulator.py
  2. 删除 D:\ZephyrAlpha\tests\rollback\test_rollback_simulator.py
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
