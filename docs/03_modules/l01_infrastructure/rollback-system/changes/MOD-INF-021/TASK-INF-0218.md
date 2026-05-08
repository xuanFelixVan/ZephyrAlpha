---
task_id: "TASK-INF-0218"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.1 + §6.10 B43 + 决策 D-021-06"
title: "回滚幂等执行器——execution_id + in_flight 文件 + 崩溃恢复"
description: |
  实现幂等回滚执行器（Durable Execution）：
  每个回滚分配全局唯一 rollback_execution_id（UUIDv7）。
  回滚执行前写入 .zephyr/rollback_in_flight/{execution_id}.json。
  恢复时检查 in_flight 文件 → 存在则从最后完成的步骤之后继续。
  每步完成后 fsync + 更新 in_flight 文件。全部完成后删除。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "新增 execution_id 生成 + in_flight 文件管理 + 崩溃恢复逻辑"
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
    reason: "本蓝图——§6.10 B43 幂等回滚 + D-021-06 幂等保护决策"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 10000
timeout_minutes: 40
acceptance_criteria:
  - "每个回滚操作分配 UUIDv7 execution_id"
  - "in_flight 文件记录当前步骤状态(PENDING/SUCCESS/FAILED)"
  - "崩溃恢复：检查 in_flight → 从最后 SUCCESS 步之后继续"
  - "完成后删除 in_flight 文件"
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
