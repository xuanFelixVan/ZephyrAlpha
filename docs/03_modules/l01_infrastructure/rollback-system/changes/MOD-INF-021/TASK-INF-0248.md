---
task_id: "TASK-INF-0248"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.17 + §6.12 B72"
title: "网络分区超时保护——git pull/push 10s timeout + 重试3次 + 重连通知"
description: |
  实现网络分区超时保护：
  git pull / git push 操作 10s timeout——避免 agent 在网络分区期间无限挂起。
  失败自动重试 3 次（线性退避）。
  3 次全部失败 → 穷尽 CDN/proxy/S3 mirror → exit code 22 (MCP_IRREVERSIBLE/nodetisolation)。
  通知 Owner 网络分区状态。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "网络分区超时——git pull/push 10s timeout + 3次重试 + S3/CDN fallback"
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
    reason: "本蓝图——§6.12 B72 网络分区"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "git pull/push 10s timeout"
  - "失败自动重试 3 次（线性退避）"
  - "全部失败 → 尝试 CDN/proxy/S3 mirror"
  - "最终失败 → 通知 Owner 网络分区"
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
