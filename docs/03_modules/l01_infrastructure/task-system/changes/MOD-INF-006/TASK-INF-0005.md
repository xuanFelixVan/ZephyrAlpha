---
task_id: "TASK-INF-0005"
source_blueprint: "MOD-INF-006"
source_section: "§11.3 步骤5"

# ===== 内容 =====
title: "重写 task_manager_server.py — MCP 6 Tool + SQLite 真源"
description: >-
  产出：src/zephyr/mcp/task_manager_server.py。
  必须初始化 task_repo（SQLite）；实现 6 个 Tool（含 register_from_triage、sync_file_state）；
  decompose_blueprint 调用步骤4 的 BlueprintDecomposer；create/update/list 直连接 task_repo。
  验收标准见蓝图 §11.3 步骤5。
priority: "P0"

upstream_files:
  - "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"
  - "D:\ZephyrAlpha\src\zephyr\core\blueprint_decomposer.py"
  - "D:\ZephyrAlpha\src\zephyr\db\task_repo.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\mcp\task_manager_server.py"
    description: "Task Manager MCP Server v0.3.0"

allowed_touch:
  - "D:\ZephyrAlpha\src\zephyr\mcp\task_manager_server.py"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\docs\03_modules\**\blueprint.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"
    reason: "§11.3 步骤5"

estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "禁止使用内存 dict 作为任务唯一存储"
  - "6 Tool 齐全；list_tasks 返回 SQLite 真实数据；sync_file_state 可比对 .md 与 DB"

rollback_instructions: "git restore src/zephyr/mcp/task_manager_server.py"

depends_on:
  - "TASK-INF-0004"
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
pipeline_modules: ["M1", "M2", "M3"]

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
