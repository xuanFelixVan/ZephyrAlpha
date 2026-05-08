---
task_id: "TASK-INF-0233"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.2 + §6.12 B57 + 决策 D-021-12"
title: "AI 幻觉防护——回滚后强制 state_verification_round + VeriTrail 风格溯源验证"
description: |
  实现 hallucination_guard.py：
  回滚后不是直接放行——而是强制 AI 进入 state_verification_round：
  要求 AI 逐文件列出 MD5 / 行数 / 关键函数签名，
  Guard 验证 AI 的输出与实际 git 状态一致。
  连续 3 轮未通过 → 判定 AI 产生幻觉 → exit code 11 (HALLUCINATION_DETECTED) → 暂停该 agent。
  对标 Microsoft VeriTrail DAG 溯源验证风格。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\hallucination_guard.py"
    description: "AI 幻觉防护——state_verification_round + 逐文件 MD5/行数/签名验证"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\hallucination_guard.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B57 幻觉防护 + D-021-12 决策"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 9000
timeout_minutes: 35
acceptance_criteria:
  - "回滚后自动触发 state_verification_round"
  - "AI 列出文件 MD5/行数/函数签名 → Guard 逐项比对 git 实际状态"
  - "连续 3 轮未通过 → exit code 11 (HALLUCINATION_DETECTED) → 暂停 agent"
  - "对标杆 Microsoft VeriTrail DAG 溯源风格"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\hallucination_guard.py
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
