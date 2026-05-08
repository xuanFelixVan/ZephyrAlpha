---
task_id: "TASK-INF-0004"
source_blueprint: "MOD-INF-006"
source_section: "§11.3 步骤4"

# ===== 内容 =====
title: "重写 blueprint_decomposer.py — 以 task_repo 为主、.md 同步为辅"
description: >-
  产出：src/zephyr/core/blueprint_decomposer.py。
  decompose() 以 task_repo.create 为主；task_id 按 {NAMESPACE}-{SEQ}；每张卡执行 G0/G7；
  成功后同步 changes/ .md 副本。验收标准见蓝图 §11.3 步骤4。
priority: "P0"

upstream_files:
  - "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"
  - "D:\ZephyrAlpha\src\zephyr\db\task_repo.py"
  - "D:\ZephyrAlpha\src\zephyr\core\models.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py"
    description: "BlueprintDecomposer v0.3.0"

allowed_touch:
  - "D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\docs\03_modules\**\blueprint.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"
    reason: "§11.3 步骤4"

estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "decompose(本蓝图) 后 task_repo 中 N≥1 且 task_id 格式符合约定"
  - "changes/ 下存在对应 .md；G7 门禁可通过"

rollback_instructions: "git restore src/zephyr/core/blueprint_decomposer.py"

depends_on:
  - "TASK-INF-0003"
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
