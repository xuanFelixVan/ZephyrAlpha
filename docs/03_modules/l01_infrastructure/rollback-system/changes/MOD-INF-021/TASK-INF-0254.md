---
task_id: "TASK-INF-0254"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 7.3 + §6.13 B80 + 决策 D-021-19 + §9 exit code 20"
title: "PSQL 连接池恢复——回滚后自动重连 + pg_bouncer 健康检查"
description: |
  实现数据库连接池恢复检测：
  回滚可能涉及数据库 schema 变更 → 连接池中的 stale 连接全部断开。
  回滚后自动执行 pg_bouncer / connection pool health check → 重连。
  重连成功后通知 Agent 数据库连接已就绪。
  重连失败 → exit code 20 (CONNECTION_POOL_RECONNECTED/FAILED) → DEFER_TO_HUMAN。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "集成连接池健康检查 + 自动重连逻辑"
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
    reason: "本蓝图——§6.13 B80 连接池恢复 + D-021-19"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "回滚后 pg_bouncer / connection pool health check"
  - "stale 连接断开 → 自动重连到健康节点"
  - "重连成功 → Agent 通知数据库已就绪"
  - "重连失败 → exit 20 → DEFER_TO_HUMAN"
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
