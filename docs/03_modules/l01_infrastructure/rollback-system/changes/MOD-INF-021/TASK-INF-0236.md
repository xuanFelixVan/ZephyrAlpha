---
task_id: "TASK-INF-0236"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.5 + §6.12 B60 + 决策 D-021-14"
title: "Token 会计——rollback_budget 增加 token_cost + max_daily_tokens 100000 限制"
description: |
  在 rollback_budget.py 中扩展 Token 会计维度：
  每次回滚操作不仅消耗回滚配额（并发/日配额），也消耗 LLM Token 成本。
  新增 max_daily_tokens 100000 限制。
  记录每轮回滚的 token_cost。
  CLI: zephyr rollback stats --tokens 展示 Token 消耗。
  预算耗尽 → 自动切换 forward-fix 模式 + 通知 Owner。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_budget.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_budget.py"
    description: "扩展 Token 会计维度——max_daily_tokens 100000 + CLI stats --tokens"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_budget.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B60 Token 会计 + D-021-14 决策"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "rollback_budget.py 新增 token_cost 字段 + max_daily_tokens 100000"
  - "回滚预算纳入 Token 成本——超限自动拒绝"
  - "zephyr rollback stats --tokens 展示 Token 消耗"
rollback_instructions: |
  1. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_budget.py
depends_on:
  - "TASK-INF-0229"
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
