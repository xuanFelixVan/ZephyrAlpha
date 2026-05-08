---
task_id: "TASK-INF-0212"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 3.3 + §6.2 B13/B33"
title: "Hard Reset token gating——不可逆操作的强制保护"
description: |
  实现 hard_reset 的 token-gated 保护：
  RollbackExecutor 中 hard_reset 方法签名绑定 require_token: str 参数类型。
  token 由 Owner 通过 CLI 生成，60s 过期。token 验证仅检查操作开始时是否有效。
  操作开始后允许完成，但 audit log 标记 token_expired_during_op: true（B33）。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "hard_reset 方法新增 token 参数 + token 校验逻辑"
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
    reason: "本蓝图——§2.1 hard_reset + §6.2 B13/B33 token 竞态圆点"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 5000
timeout_minutes: 20
acceptance_criteria:
  - "hard_reset(commit_sha, token) 不传 token → TypeError"
  - "token 验证：60s 过期，仅操作开始时检查"
  - "token_expired_during_op 标记写入 audit log"
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
