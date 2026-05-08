---
task_id: "TASK-INF-0221"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.4 + §6.10 B46 + 决策 D-021-08"
title: "三级 Kill Switch——L1 Session/L2 Skill/L3 Global + 自动递进升级"
description: |
  实现 kill_switch.py：
  L1 Session Kill（暂停单个 agent session 写操作）。
  L2 Skill Kill（禁写特定类型文件，含 semantic morphing detection escalation → B58）。
  L3 Global Kill（全量 hard_reset）。
  kill_level 枚举 + 生效范围 + 自动递进升级逻辑。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\kill_switch.py"
    description: "三级 Kill Switch 管理器——L1/L2/L3 + 递进升级"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\kill_switch.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——B46 Kill Switch 粒度 + D-021-08"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 10000
timeout_minutes: 40
acceptance_criteria:
  - "L1 Session Kill：暂停单个 agent 写操作"
  - "L2 Skill Kill：禁写特定类型文件"
  - "L3 Global Kill：全量 hard_reset"
  - "自动递进升级：L1→L2→L3"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\kill_switch.py
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
