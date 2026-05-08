---
task_id: "TASK-INF-0219"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.2 + §6.10 B42"
title: "回滚状态机——步骤级状态追踪 + 部分失败恢复 + 可逆/不可逆步分类"
description: |
  实现 RollbackStateMachine：
  回滚拆分为独立步骤（preflight → lock → git_revert → db_rebuild → verify → audit），
  每步独立状态（PENDING/SUCCESS/FAILED/RETRYING）。
  部分成功时记录每步状态，可逆步重试，不可逆步产生 forward-fix commit。
  in_flight 文件管理与状态机联动。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_state_machine.py"
    description: "回滚状态机——步骤级状态追踪(PENDING/SUCCESS/FAILED/RETRYING)+部分失败恢复"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_state_machine.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.10 B42 状态机结论"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 10000
timeout_minutes: 40
acceptance_criteria:
  - "6 步骤状态机：preflight/lock/git_revert/db_rebuild/verify/audit"
  - "每步状态：PENDING/SUCCESS/FAILED/RETRYING"
  - "可逆步重试，不可逆步产生 forward-fix commit"
  - "与 execution_id + in_flight 文件联动"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\rollback_state_machine.py
depends_on:
  - "TASK-INF-0218"
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
