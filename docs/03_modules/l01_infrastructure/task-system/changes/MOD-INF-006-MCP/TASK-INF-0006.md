---
task_id: "TASK-INF-0006"
source_blueprint: "MOD-INF-006"
source_section: "§11.3 步骤6"

# ===== 内容 =====
title: "补齐 context_engine + 落实 pipeline M1-M11（GOV-AI-002）"
description: >-
  产出区域：src/zephyr/context_engine/ 与 src/zephyr/pipeline/。
  验收标准（蓝图 §11.3 步骤6）：G3 可用——context_assembly_manifest 所列文件可装配；
  M1-M11 与 Vibe Coding 执行层字段对齐；管线执行事件写入 task_repo。
  M 模块分工与 Claude 救援条件见蓝图 §11.3 步骤6 表格。
priority: "P0"

upstream_files:
  - "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\governance\ai\model-routing-policy.md"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\context_engine\"
    description: "Context 装配与注入能力"
  - path: "D:\ZephyrAlpha\src\zephyr\pipeline\"
    description: "M1-M11 管线与编排"

allowed_touch:
  - "D:\ZephyrAlpha\src\zephyr\context_engine\**"
  - "D:\ZephyrAlpha\src\zephyr\pipeline\**"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\docs\03_modules\**\blueprint.md"

applicable_rules:
  - module_id: "GOV-AI-002"
    section: "全篇"
    reason: "模型路由与救援策略"

context_assembly_manifest:
  - file_path: "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"
    reason: "§11.3 步骤6"

estimated_tokens: 16000
timeout_minutes: 90

acceptance_criteria:
  - "G3：manifest 文件可读可装配"
  - "pipeline_modules/assigned_pipeline 等与蓝图一致；必要时写入 task_repo events"

rollback_instructions: "git restore src/zephyr/context_engine src/zephyr/pipeline"

depends_on:
  - "TASK-INF-0005"
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
pipeline_modules: ["M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11"]

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
