---
task_id: "TASK-INF-0231"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.14 + §6.10 B55"
title: "基于大语言模型的 commit impact analyzer——语义级风险评估"
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\llm_impact_analyzer.py"
    description: "LLM 影响分析器——commit diff → AI 语义级风险评估(RISK score/P0-P3)"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\llm_impact_analyzer.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——B55 LLM-based impact analyzer 结论"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "commit diff → LLM 语义分析 → RISK 分数(0-100) + P0-P3 分类"
  - "推荐操作：SAFE/MONITOR/AUDIT/BLOCK"
rollback_instructions: "1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\llm_impact_analyzer.py"
depends_on: ["TASK-INF-0203"]
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
