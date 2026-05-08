---
task_id: "TASK-INF-0211"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 3.2 + §6.2 B12"
title: "Rollback Metrics + MTTR Tracking——回滚 SLA 可观测性"
description: |
  实现 rollback_metrics 表：rollback_id/trigger/start_iso/end_iso/duration_ms/success/files_reverted/conflict。
  CLI: zephyr rollback stats 显示 MTTR/频率/成功率/冲突记录。
  metrics 写入失败不 block 回滚——fallback 写入 stderr + terminal logger text log（B30）。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\data\\rollback\\rollback_metrics.db"
    description: "回滚指标——MTTR/频率/成功率/冲突记录/drill 结果"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_metrics.py"
    description: "回滚指标采集器——记录每次回滚的耗时/成功率/文件数"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_metrics.py"
  - "D:\\ZephyrAlpha\\data\\rollback\\rollback_metrics.db"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.2 B12/B30 指标盲点"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "每次回滚记录 rollback_metrics 条目（含 duration_ms/success/files）"
  - "CLI zephyr rollback stats 显示 MTTR/频率/成功率"
  - "metrics 写入失败 → fallback 到 stderr"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\rollback_metrics.py
  2. 删除 D:\ZephyrAlpha\data\rollback\rollback_metrics.db
depends_on:
  - "TASK-INF-0203"
blocked_by: []
status: "created"
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
