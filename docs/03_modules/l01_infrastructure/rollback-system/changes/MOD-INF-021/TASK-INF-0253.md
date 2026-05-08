---
task_id: "TASK-INF-0253"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 7.2 + §6.13 B79 + 决策 D-021-18 + §9 exit code 18"
title: "LLM Prompt Injection 防护——回滚 trigger/message 内容扫描 + prompt_injection_filter"
description: |
  实现 Prompt Injection 过滤：
  回滚系统接收到的每个 trigger 和 message 都进行 Prompt Injection 扫描。
  检测到 prompt 中嵌入越狱指令（DAN/UNICHAT/ignore all）→ 过滤并 sanitize。
  exit code 18 (PROMPT_INJECTION_FILTERED) → 记录 + 通知 Owner 已拦截。
  对标 OWASP LLM Top 10 #1: Prompt Injection。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "在回滚执行器入口集成 Prompt Injection 过滤扫描"
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
    reason: "本蓝图——§6.13 B79 Prompt Injection 防护 + D-021-18"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "回滚 trigger/message 逐条做 Prompt Injection 扫描"
  - "检测到 DAN/UNICHAT/ignore all 等越狱指令 → 过滤"
  - "exit 18 PROMPT_INJECTION_FILTERED + 拦截记录"
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
