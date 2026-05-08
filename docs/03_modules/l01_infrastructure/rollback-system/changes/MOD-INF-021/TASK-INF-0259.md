---
task_id: "TASK-INF-0259"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 7.8 + §6.13 B85 + §9 exit code 25"
title: "Git Binary 完整性验证——git --version + sha256 hash + binary mismatch 告警"
description: |
  实现 git 二进制完整性验证：
  preflight 对 git executable 做 sha256 hash 校验。
  git binary 被替换/篡改 → exit code 25 (GIT_BINARY_MISMATCH) → L3 Kill Switch。
  防止通过替换 git 二进制绕过回滚门禁。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "git 二进制 hash 验证 + 篡改检测 → L3 Kill"
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
    reason: "本蓝图——§6.13 B85 Git Binary 完整性"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 5000
timeout_minutes: 20
acceptance_criteria:
  - "sha256(git.exe) 与已知 hash 对比"
  - "mismatch → exit 25 → L3 Kill Switch → 立即处置"
rollback_instructions: |
  1. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py
depends_on:
  - "TASK-INF-0255"
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
