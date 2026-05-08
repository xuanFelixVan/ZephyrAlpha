---
task_id: "TASK-INF-0223"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.6 + §6.10 B44 + AP8"
title: "AI 对话上下文恢复——回滚后注入 context restoration prompt"
description: |
  实现 rollback_context_restorer.py：
  回滚后自动注入 context restoration prompt 到 AI 会话。
  prompt 格式：SYSTEM: ROLLBACK EXECUTED. commit {sha}→{new_sha}. 原因: {reason}. 受影响文件: {files}。
  与 temporal_context_adapter（B70）联动——检测时间上下文断裂。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_context_restorer.py"
    description: "上下文恢复器——回滚后注入 AI 会话恢复 prompt"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_context_restorer.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——B44 对话上下文恢复 + §8 AP8"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "回滚后自动注入 context restoration prompt"
  - "prompt 含 commit SHA/原因/受影响文件/下一步指示"
  - "与 temporal_context_adapter（B70）联动"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\rollback_context_restorer.py
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
