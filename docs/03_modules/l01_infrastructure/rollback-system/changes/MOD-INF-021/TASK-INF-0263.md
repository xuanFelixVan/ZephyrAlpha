---
task_id: "TASK-INF-0263"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 7.13 + §6.15 B95 + 决策 D-021-26 + Risks R15-R20"
title: "持续信任评估——continuous_trust_ledger + trust_delta + soft/hard 信任度裁剪"
description: |
  实现持续信任评估引擎：
  continuous_trust_ledger 记录 AI 每次回滚的 trust_delta (±)。
  信任度不是二进制是连续值 (-1.0 ~ +1.0)。
  trust_score 影响 AI 可以操作的 autonomy tier：
  trust > 0.8 → tier 2 (auto-revert); trust < 0.5 → tier 1 (propose-only);
  trust < -0.3 → tier 0 (read-only + human escalation)。
  涵盖 R15-R20 的 AI agent 信任安全风险。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\continuous_trust.py"
    description: "持续信任评估——trust_ledger + trust_score → tier 分级自主"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\continuous_trust.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.15 B95 持续信任 + D-021-26"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "continuous_trust_ledger 记录 trust_delta ±0.1"
  - "trust > 0.8 → tier 2 auto-revert"
  - "trust < 0.5 → tier 1 propose-only"
  - "trust < -0.3 → tier 0 read-only + human"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\continuous_trust.py
depends_on:
  - "TASK-INF-0262"
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
