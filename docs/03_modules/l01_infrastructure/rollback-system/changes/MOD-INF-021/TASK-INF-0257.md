---
task_id: "TASK-INF-0257"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 7.6 + §6.13 B83 + §9 exit code 23"
title: "通知洪流节制——notify_rain_limit + throttle_window 防告警疲劳"
description: |
  实现通知洪流节制：
  notify_rain_limit: 限制 5 分钟内最多 10 条回滚相关通知。
  throttle_window 默认 300s。
  超过限制 → exit code 23 (NOTIFICATION_THROTTLED) → 合并多条通知为摘要。
  防止回滚级联失败导致告警风暴淹没 Owner 的信息通道。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "通知洪流节制——throttle_window 300s + 10条限制 + 摘要合并"
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
    reason: "本蓝图——§6.13 B83 通知洪流节制"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "5 分钟窗口 + 10 条通知上限"
  - "超过限制 → exit 23 → 合并摘要通知"
  - "可配置 notify_rain_limit + throttle_window"
rollback_instructions: |
  1. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py
depends_on:
  - "TASK-INF-0258"
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
