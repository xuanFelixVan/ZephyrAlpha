---
task_id: "TASK-INF-0242"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.11 + §6.12 B66 + §9 exit code 15"
title: "密钥轮替感知——secret_rotation_aware 定期刷新 + 过期密钥自动告警"
description: |
  实现密钥轮替感知器：
  定期检查项目中的 API key / JWT / token 是否已过期。
  关联密钥管理系统的轮替周期。
  检测到过期密钥（>rotatie_threshold）→ exit code 15 (STALE_SECRET_FOUND) → 尝试自动轮替。
  不能自动轮替 → DEFER_TO_HUMAN + 列出过期密钥清单。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\secret_rotation_aware.py"
    description: "密钥轮替感知——过期检测 + 自动轮替 + 不可自动则 DEFER_TO_HUMAN"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\secret_rotation_aware.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B66 密钥轮替感知"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "定期检查 API key / JWT / token 过期状态"
  - "关联密钥管理系统轮替周期"
  - "过期 → exit code 15 → 自动轮替"
  - "不可自动轮替 → DEFER_TO_HUMAN + 清单"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\secret_rotation_aware.py
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
