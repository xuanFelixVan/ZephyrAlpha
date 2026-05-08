---
task_id: "TASK-INF-0252"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 7.1 + §6.13 B78 + 决策 D-021-17 + §9 exit code 19"
title: "GDPR 遗忘权检查——right_to_be_forgotten_registry + 自动净化敏感数据"
description: |
  实现 GDPR 遗忘权合规检查器：
  right_to_be_forgotten_registry 维护已知"被遗忘权"用户哈希集。
  回滚可能恢复包含已请求遗忘用户的数据 → 自动净化。
  检测到回滚恢复被遗忘权数据 → exit code 19 (GDPR_BLOCKED) → DEFER_TO_HUMAN。
  对标 EU GDPR Article 17 "Right to be forgotten"。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\right_to_be_forgotten.py"
    description: "GDPR 遗忘权——被遗忘用户哈希集 + 回滚数据自动净化 + GDPR_BLOCKED"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\right_to_be_forgotten.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.13 B78 GDPR 遗忘权 + D-021-17"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "被遗忘权用户哈希集维护"
  - "回滚恢复含被遗忘用户数据 → 自动净化"
  - "无法自动净化 → exit 19 GDPR_BLOCKED → DEFER_TO_HUMAN"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\right_to_be_forgotten.py
depends_on:
  - "TASK-INF-0251"
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
