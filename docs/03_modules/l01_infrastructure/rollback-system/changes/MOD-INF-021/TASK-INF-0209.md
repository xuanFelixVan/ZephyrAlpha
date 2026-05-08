---
task_id: "TASK-INF-0209"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 2.4 + §6.2 B10 + AP7"

title: "Non-tracked 文件保护——.env/secrets 备份与恢复"
description: |
  实现回滚 preflight 中非 git-tracked 文件保护：
  - git status --ignored 列出所有非 tracked 文件
  - config 类非 tracked 文件（.env/secrets.yaml）在回滚前做备份
  - 备份格式：.env.rollback-{timestamp}
  - 回滚后比较备份与当前状态 → 不一致则提示 Owner
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "preflight_check 新增 non-tracked 文件扫描 + backup_config_files()"

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
    reason: "本蓝图——§6.2 B10 非 git-tracked 文件盲点 + §8 AP7 Anti-Pattern"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 4000
timeout_minutes: 20

acceptance_criteria:
  - "preflight_check 列出所有 git status --ignored 非 tracked 文件"
  - "config 类文件备份到 .env.rollback-{timestamp}"
  - "回滚后比较备份与当前状态"
  - "rollback_instructions 包含非 tracked 文件恢复步骤"

rollback_instructions: |
  1. git checkout HEAD~1 -- D:\ZephyrAlpha\src\zephyr\rollback\rollback_executor.py

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
