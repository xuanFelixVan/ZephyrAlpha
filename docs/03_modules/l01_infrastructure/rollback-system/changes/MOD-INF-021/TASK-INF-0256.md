---
task_id: "TASK-INF-0256"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 7.5 + §6.13 B82 + 决策 D-021-21 + §9 exit code 22"
title: "MCP 不可逆操作识别——git reflog expire/gc --prune 列入不可逆清单"
description: |
  实现 MCP (Model Context Protocol) 不可逆操作识别器：
  维护不可逆操作清单——git reflog expire / git gc --prune / git push --force。
  回滚涉及这些操作 → exit code 22 (MCP_IRREVERSIBLE) → DEFER_TO_HUMAN。
  禁止 AI agent 自行执行清单中的操作——必须 Owner 亲自操作或人工授权。
  消除 AI 无差别执行不可逆 git 命令的安全盲点。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "MCP 不可逆操作清单 + AI 禁止执行 + Owner 授权门禁"
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
    reason: "本蓝图——§6.13 B82 MCP 不可逆 + D-021-21"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "不可逆操作清单：reflog expire / gc --prune / push --force / hard reset"
  - "涉及不可逆操作 → exit 22 MCP_IRREVERSIBLE"
  - "DEFER_TO_HUMAN——需 Owner 确认"
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
