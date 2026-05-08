---
task_id: "TASK-INF-0002"
source_blueprint: "MOD-INF-006"
source_section: "§11.3 步骤2"

# ===== 内容 =====
title: "同步 task-card-meta-registry.yaml（迁移追踪）"
description: >-
  产出位置：docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.yaml。
  验收标准（蓝图原文）：记录 MOD-INF-006 v0.2.0→v0.3.0 迁移——TaskCard 基座从独立模型→继承 shared/schemas.py Task。
priority: "P0"

upstream_files:
  - "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\task-card-meta-registry.yaml"

downstream_outputs:
  - path: "D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\task-card-meta-registry.yaml"
    description: "MOD-INF-006 v0.3.0 迁移追踪条目"

allowed_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\task-card-meta-registry.yaml"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\03_modules\**\blueprint.md"
  - "D:\ZephyrAlpha\src\**"

applicable_rules:
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规创建"

context_assembly_manifest:
  - file_path: "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"
    reason: "§11.3 步骤2 真源"

estimated_tokens: 6000
timeout_minutes: 25

acceptance_criteria:
  - "task-card-meta-registry.yaml 含 MOD-INF-006 的 v0.2.0→v0.3.0 Task 基座继承说明"

rollback_instructions: "git restore docs/01_policies_and_standards/_registry/catalogs/task-card-meta-registry.yaml"

depends_on:
  - "TASK-INF-0001"
blocked_by: []

status: "done"

tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-006"]

completed_gates: []
blocked_gates: {}

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1", "M3"]

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
