---
task_id: "TASK-INF-0216"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 4.2 + §6.2 B20"
title: "BREAK_GLASS adaption for rollback——Owner 紧急取消回滚"
description: |
  在 RollbackExecutor 中增加 BREAK_GLASS 机制：
  RollbackExecutor.cancel_pending_rollback(task_id, reason, token) ——在自动回滚还在队列中时取消。
  30s 内响应，超时则回滚已执行。对标 Gate Engine 的 BREAK_GLASS。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "新增 cancel_pending_rollback()——BREAK_GLASS 适配"
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
    reason: "本蓝图——§6.2 B20 BREAK_GLASS 适配结论"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 3000
timeout_minutes: 11
acceptance_criteria:
  - "cancel_pending_rollback(task_id, reason, token) 取消队列中的回滚"
  - "30s 内响应，超时则回滚已执行"
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
