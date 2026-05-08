---
task_id: "TASK-INF-0262"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 7.12 + §6.15 B94 + 决策 D-021-25"
title: "AI 自主感知——autonomy_dashboard + autonomy_health gauge + 人工 alarm"
description: |
  实现 AI 自主感知健康仪表：
  autonomy_dashboard 实时展示 AI 自主回滚行为的健康指标：
  成功率 / 干预率 / 假阳性率 / token_cost / time_to_restore。
  autonomy_health gauge (0.0-1.0)——连续 5 分钟 <0.3 → autonomy_downgrade。
  exit code 35 (AUTONOMY_DOWNGRADED) → 通知 Owner 手动接管。
  对标特斯拉 Autopilot disengagement 人工接管模式。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\autonomy_dashboard.py"
    description: "AI 自主感知仪表——healthy_gauge + disengagement alarm"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\autonomy_dashboard.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.15 B94 AI 自主感知 + D-021-25"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "autonomy_dashboard 实时指标：success/intervention/fp/token/RTO"
  - "health < 0.3 连续 5 分钟 → autonomy_downgrade"
  - "exit 35 (AUTONOMY_DOWNGRADED) + Owner 通知"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\autonomy_dashboard.py
depends_on:
  - "TASK-INF-0251"
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
