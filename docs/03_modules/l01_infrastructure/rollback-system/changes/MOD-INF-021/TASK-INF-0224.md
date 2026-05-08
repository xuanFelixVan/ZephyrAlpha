---
task_id: "TASK-INF-0224"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.7 + §6.10 B48 + AP12"
title: "依赖感知回滚——blueprint dependency graph + impact broadcast + 下游自愈"
description: |
  回滚前 preflight 新增 dependency_impact_analysis()：
  从 blueprint-registry.yaml 加载完整模块依赖图 → 标记受影响模块。
  回滚后广播 MODULE_ROLLBACK_NOTIFICATION 事件 → 下游模块自愈。
  与 DOM-GOV-001 的 G-CT-002/G-CT-003/G-CT-005 集成契约联动。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\_domain-governance\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "preflight 新增 dependency_impact_analysis() + impact broadcast"
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
    reason: "本蓝图——B48 依赖感知回滚 + §8 AP12 + DOM-GOV-001 契约"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "dependency_impact_analysis 加载模块依赖图 → 标记受影响模块"
  - "回滚后广播 MODULE_ROLLBACK_NOTIFICATION"
  - "下游模块收到通知后执行自愈"
rollback_instructions: |
  1. git checkout HEAD~1 -- D:\ZephyrAlpha\src\zephyr\rollback\rollback_executor.py
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
