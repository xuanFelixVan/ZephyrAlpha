---
task_id: "TASK-INF-0114"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §6 产出物存放目录"

title: "§6 产出物存放目录验证——changes/MOD-INF-016 准入合规审计"
description: |
  验证蓝图 §6 列出的 5 类产出物目录是否存在且满足准入规则。
  1. changes/MOD-INF-016/——本任务卡目录 = 施工后的任务卡归档。
  2. session-logs/YYYY/MM/——Session 审计轨迹（B32 产生的 JSONL 日志）。
  3. metrics/*.csv——性能基准测试结果（B26 产生的 cost metrics）。
  4. tests/unit/——单元测试（Phase 11-20 新增 25 个测试文件）。
  5. docs/03_modules/_cross_layer/shared-core/——蓝图本体与施工记录。
  所有产出物目录必须在 blueprint.md §6 中与实际磁盘路径保持一致。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\TASK-INF-0114.md"
    description: "本任务卡——§6 目录审计执行记录"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\TASK-INF-0114.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§3.3"
    reason: "产出物目录——changes/ 必须在模块子目录下"
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "session-logs/ 和 metrics/ 不在 shared/ 内，但仍受模块边界控制"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §6——产出物目录声明"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
    reason: "目录结构标准——验证产出物路径合规性"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 5000
timeout_minutes: 15

acceptance_criteria:
  - "changes/MOD-INF-016/ 目录存在（验证成功或可创建）"
  - "session-logs/ 父目录存在（YYYY/MM/ 子目录按需创建）"
  - "metrics/ 目录存在（可创建）——存放 cost/performance metrics"
  - "tests/unit/ 目录存在符合测试契约规定"
  - "docs/03_modules/_cross_layer/shared-core/ 目录存在——蓝图主目录"

rollback_instructions: |
  本任务为只读审计。如需创建缺失目录，仅通过 mkdir 创建空目录。
  回滚：删除本任务创建的目录。

depends_on: ["TASK-INF-0100"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "glm-5.1"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
