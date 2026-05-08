---
task_id: "TASK-INF-0246"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.15 + §6.12 B70 + §9 exit code 26"
title: "AI 时间上下文断裂修复——temporal_context_adapter + TOTP/NTP 时间证明"
description: |
  实现 temporal_context_adapter.py：
  AI agent 回滚后时间上下文断裂（agent 认为当前是 T 时刻，实际是 T+N）。
  引入 NTP time attestation + TOTP 一次性时间证明机制。
  Agent 恢复时提交时间证明 → Adapter 验证 → 对齐 AI 上下文。
  时间证明不可伪造或 repudiate → 验伪失败 exit code 26 (TIME_ATTEST_FAIL)。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\temporal_context_adapter.py"
    description: "AI 时间上下文修复——NTP+TOTP 时间证明 + agent 时间对齐"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\temporal_context_adapter.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B70 时间上下文断裂"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "NTP time attestation 不可伪造时间戳"
  - "TOTP 一次性时间证明 Agent 提交 → Adapter 验证"
  - "时间证明失败 → exit code 26 (TIME_ATTEST_FAIL)"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\temporal_context_adapter.py
depends_on:
  - "TASK-INF-0232"
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
