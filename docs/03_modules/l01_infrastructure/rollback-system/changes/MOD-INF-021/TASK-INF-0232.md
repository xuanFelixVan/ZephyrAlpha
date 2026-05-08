---
task_id: "TASK-INF-0232"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.1 + §6.12 B56 + 决策 D-021-11"
title: "自举回滚器——rollback_bootstrap.py 零依赖最小化回滚 + chmod 444 只读锁定"
description: |
  实现 rollback_bootstrap.py：
  当主回滚器 (rollback_executor.py) 自身操作连续 3 次失败时，
  自动将回滚操作升级到 bootstrap 模式。
  bootstrap 仅依赖 git 命令行（git log / git revert / git status），
  不 import 任何项目 Python 模块——确保在项目自身损坏时仍可回滚。
  核心文件 chmod 444 (Owner只读) 锁定，防止 AI 篡改。
  对标 K8s static pod manifest 自愈模式。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_bootstrap.py"
    description: "自举回滚器——零依赖最小化回滚，仅依赖 git CLI，chmod 444 只读锁定"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_bootstrap.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B56 自举回滚 + D-021-11 决策"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "主回滚器连续 3 次自身操作失败 → 自动激活 bootstrap 模式"
  - "bootstrap 零项目依赖——仅 subprocess.run git CLI"
  - "rollback_bootstrap.py chmod 444 (Owner只读)"
  - "bootstrap 成功回滚 → exit code 10 (BOOTSTRAP_ESCALATED)"
  - "bootstrap 回滚路径：git_log → git_revert → git_status"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_bootstrap.py
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
