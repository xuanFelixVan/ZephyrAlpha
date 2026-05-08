---
task_id: "TASK-INF-0249"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.18 + §6.12 B73"
title: "S3 快照防生命周期过期——S3 lifecycle policy + 脏表净化 cron"
description: |
  实现 S3 快照生命周期管理：
  设置 S3 bucket lifecycle policy——标记过期 checkpoint 为 Glacier 归档。
  S3 fast_purge: 定期 cron 清理 >90天未引用的快照。
  防止恢复时命中已过期的 S3 对象导致"看似存在实则已删除"的错误。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\s3_snapshot_lifecycle.py"
    description: "S3 快照防过期——lifecycle policy Glacier/GD archiving + 净化 cron"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\s3_snapshot_lifecycle.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B73 S3 快照防过期"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "S3 lifecycle policy——Glacier/GD 归档过期 checkpoint"
  - "定期 cron 清理 >90天未引用的快照 (fasclen)"
  - "恢复时检查 S3 对象是否存在 → 发现缺失则告警"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\s3_snapshot_lifecycle.py
depends_on:
  - "TASK-INF-0208"
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
