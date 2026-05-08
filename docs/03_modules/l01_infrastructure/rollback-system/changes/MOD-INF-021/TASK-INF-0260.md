---
task_id: "TASK-INF-0260"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 7.10 + §6.15 B96 + 决策 D-021-23"
title: "反向预言自我实现防护——prophecy 检测 + rollback 执行 check—act 隔离"
description: |
  实现反向预言 (reverse prophecy self-fulfilling) 防护：
  当 AI agent 预测"回滚会失败" → 该预测可能影响回滚执行 → self-fulfilling。
  检测 agent 输出中是否包含对回滚结果的 negative prediction。
  发现 → 隔离 check 阶段和 act 阶段——预测不能影响执行。
  对标 Goodhart's Law (metrics cease being good once targeted) +
  OpenAI 模型自我验证大使范式。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "反向预言防护——预测-执行隔离 + prophecy_detector 扫描"
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
    reason: "本蓝图——§6.15 B96 反向预言 + D-021-23"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "agent A 输出负面预测 → prophecy_detector 触发"
  - "隔离预测与执行——禁止 prediction → act 通道"
  - "预言失败不影响回滚本身执行"
rollback_instructions: |
  1. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py
depends_on:
  - "TASK-INF-0259"
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
