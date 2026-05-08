---
task_id: "TASK-INF-0241"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.10 + §6.12 B65 + 决策 D-021-16 + §9 exit code 17"
title: "GPG 签名链保持——preflight 检测 gpgSign → git revert --gpg-sign"
description: |
  实现 GPG 签名链保持：
  preflight 检测项目 git config 是否开启 gpgSign。
  如果 gpgSign = true → 回滚产生的 revert commit 必须带 GPG 签名：
  `git revert --gpg-sign {commit_sha}`
  如果无可用 GPG key → exit code 17 (GPG_MISSING) → DEFER_TO_HUMAN。
  确保 revert commit 与项目签名策略一致——不破坏可验证链。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "在刀片 revert 逻辑中集成 GPG 签名检测 + --gpg-sign 参数"
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
    reason: "本蓝图——§6.12 B65 GPG 签名链 + D-021-16 决策"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "preflight 检测 git config commit.gpgSign"
  - "gpgSign=true → git revert --gpg-sign"
  - "无可用 GPG key → exit code 17 → DEFER_TO_HUMAN"
  - "revert commit 与项目签名链无缝衔接"
rollback_instructions: |
  1. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py
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
