---
task_id: "TASK-INF-0243"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.12 + §6.12 B67"
title: "跨平台 Shell 双输出——cross_platform_shell.py 自动生成 .sh + .ps1"
description: |
  实现跨平台 Shell 双输出：
  对每个回滚操作自动生成 Linux (.sh) 和 Windows (.ps1) 双平台可执行脚本。
  消除"在 Windows 上回滚 Linux 产物"的跨平台兼容性盲点。
  .sh: bash shebang + chmod +x 标记 + git revert -- GPG-sign
  .ps1: PowerShell #Requires -Version 5.1 声明 + Set-ExecutionPolicy 保护
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\cross_platform_shell.py"
    description: "跨平台 Shell 双输出——.sh (Linux) + .ps1 (Windows) 自动生成"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\cross_platform_shell.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B67 跨平台 Shell"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "每个回滚操作生成 .sh + .ps1 双输出"
  - ".sh: #!/bin/bash + chmod +x + git revert --gpg-sign"
  - ".ps1: #Requires -Version 5.1 + Set-ExecutionPolicy"
  - "Linux 和 Windows 独立可执行"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\cross_platform_shell.py
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
