---
task_id: "TASK-INF-0244"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.13 + §6.12 B68"
title: "venv 版本同步——回滚代码 + pip install -r 版本一致性保障"
description: |
  实现 venv/conda 版本同步：
  回滚不仅恢复代码，同时执行 pip install -r requirements.txt（冻结版本）。
  消除"代码回滚成功但依赖未回退导致运行时错误"的盲点。
  pip freeze 保存回滚前后的依赖快照用于差异审计。
  支持 --no-deps-sync 跳过（快速探索模式）。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\venv_sync.py"
    description: "venv 版本同步——pip install -r + freeze 差异审计"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\venv_sync.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B68 venv 同步"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "回滚后自动 pip install -r requirements.txt"
  - "冷冻前后 freeze 快照用于审计 diff"
  - "--no-deps-sync 跳过选项"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\venv_sync.py
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
