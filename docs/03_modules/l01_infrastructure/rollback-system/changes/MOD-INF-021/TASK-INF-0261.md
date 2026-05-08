---
task_id: "TASK-INF-0261"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 7.11 + §6.15 B97 + 决策 D-021-24"
title: "青野 检查点密度——checkpoint_density 最小 10 分钟间隔 + token-aware 节流"
description: |
  实现 青野 检查点密度控制：
  限制 checkpoint 最小间隔为 10 分钟——防止高频 checkpoints 消耗存储/CPU。
  token-aware 节流：Agent 高 Token 消耗时自动提升 checkpoint 间隔。
  对标 FlowX 青野 架构项目内的软 SLO -> 硬阻断转化逻辑。
  checkpoint density 超限 → 降级到 git-native 单 sha 回滚模式。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "青野 检查点节流——10min 最小间隔 + token-aware 自适应"
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
    reason: "本蓝图——§6.15 B97 青野 检查点 + D-021-24"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "checkpoint 最小间隔 10 分钟"
  - "高 Token 消耗 → 自适应拉大间隔"
  - "超限 → 降级 git-native 模式"
rollback_instructions: |
  1. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py
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
