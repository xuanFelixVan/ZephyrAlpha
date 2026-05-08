---
task_id: "TASK-INF-0228"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 5.11 + §6.10 B53"
title: "Differential 验证——回滚前后逐行比较 tasks/gates/events 表"
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_verifier.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_verifier.py"
    description: "新增 differential_check()——逐行比较回滚前后 DB 表差异"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_verifier.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——B53 differential check 结论"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 5000
timeout_minutes: 20
acceptance_criteria:
  - "differential_check 逐行比较 tasks/gates/events 表"
  - "diff > 3 行 → mark ROLLBACK_PARTIAL + 通知 Owner"
rollback_instructions: "1. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_verifier.py"
depends_on: ["TASK-INF-0204"]
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
