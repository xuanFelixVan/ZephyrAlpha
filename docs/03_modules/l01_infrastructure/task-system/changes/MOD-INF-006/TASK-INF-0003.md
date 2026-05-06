---
task_id: "TASK-INF-0003"
source_blueprint: "MOD-INF-006"
source_section: "§11.3 步骤3"

# ===== 内容 =====
title: "重写 core/models.py — TaskCard 继承 Task（v0.3.0）"
description: >-
  产出：src/zephyr/core/models.py。
  内容变更与验收标准见蓝图 §11.3 步骤3：TaskCard 继承 shared/schemas.py Task；
  task_id 格式 {NAMESPACE}-{SEQ}；10 态 TaskStatus；扁平 tags[]；保留防漂移六维与门禁/管线扩展字段。
priority: "P0"

upstream_files:
  - "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"
  - "D:\ZephyrAlpha\src\zephyr\shared\schemas.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\core\models.py"
    description: "TaskCard v0.3.0 模型"

allowed_touch:
  - "D:\ZephyrAlpha\src\zephyr\core\models.py"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\docs\03_modules\**\blueprint.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"
    reason: "§11.3 步骤3"

estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "isinstance(TaskCard(...), Task) 为真"
  - "task_id 符合蓝图约定模式；status 属于 TaskStatus；防漂移六维字段存在"

rollback_instructions: "git restore src/zephyr/core/models.py"

depends_on:
  - "TASK-INF-0002"
blocked_by: []

status: "created"

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
