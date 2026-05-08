---
task_id: "TASK-INF-0226"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.9 + §6.10 B47"
title: "30 秒回滚仪表盘——Markdown 零依赖 dashboard + IM 推送"
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_dashboard.py"
    description: "回滚仪表盘生成器——零依赖 Markdown dashboard + IM 推送"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_dashboard.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——B47 30秒仪表盘需求"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "每次回滚后自动生成 rollback_dashboard.md"
  - "dashboard 含原因/受影响文件/耗时/DB 变更/下一步建议"
  - "推送到飞书/钉钉/Slack"
rollback_instructions: "1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_dashboard.py"
depends_on: ["TASK-INF-0223"]
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
