---
task_id: "TASK-INF-0234"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.3 + §6.12 B58 + 决策 D-021-13 + §9 exit code 12"
title: "语义变形检测——AST 结构 / 调用链 / 敏感 API 模式的相似度比较"
description: |
  实现 semantic_similar_detector.py：
  回滚后比较回滚前后代码的 AST 语义特征：
  AST 结构相似度 / 函数调用链 / 敏感 API 使用模式。
  新旧代码 >70% 相似度 → 判定为语义变形攻击（malicious AI 换写法绕过门禁）：
  exit code 12 (MORPHING_DETECTED) → 自动升级到 L2 Skill Kill。
  不计行级差异——只看语义等价性。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\semantic_similar_detector.py"
    description: "语义变形检测——AST 结构/调用链/敏感 API 相似度 >70% → L2 Kill"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\semantic_similar_detector.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B58 语义变形检测 + D-021-13 决策"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 10000
timeout_minutes: 40
acceptance_criteria:
  - "AST 结构相似度计算（不计行级差异）"
  - "调用链 graph 相似度比较"
  - "敏感 API 模式匹配（eval/exec/os.system/subprocess 等）"
  - "新旧代码 >70% 相似 → exit code 12 → L2 Skill Kill"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\semantic_similar_detector.py
depends_on:
  - "TASK-INF-0233"
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
