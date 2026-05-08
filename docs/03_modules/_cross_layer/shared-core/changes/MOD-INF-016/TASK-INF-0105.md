---
task_id: "TASK-INF-0105"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §4 Phase 13 + §12 盲点 B30, B31"

title: "Phase 13 施工——AI 流程可控：Durable Execution断点续跑(B30) + 后处理管道(B31)"
description: |
  实现 AI 长流程的可靠性与质量保障。
  B30：长流程 AI task 可能运行数小时——进程崩溃后从头重跑浪费已消耗 token。
  需实现：DurableExecution——Worker/Activity 抽象层、进度快照、断点恢复。
  B31：Boris Cherny 核心技巧——AI 生成代码后自动跑 lint/format/typecheck。
  需实现：PostProcessPipeline——可配置 hook 点（lint/format/typecheck/auto-fix）。
  专业对标：PydanticAI Durable Execution / Temporal.io / Claude Code PostToolUse hooks。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\.pre-commit-config.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\durable_execution.py"
    description: "DurableExecution——Activity/Workflow 抽象 + 进度快照 + 断点恢复"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\post_process.py"
    description: "PostProcessPipeline——可配置 hook 点（lint/format/typecheck/auto-fix）"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_durable_execution.py"
    description: "单元测试——验证断点恢复、快照一致性"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_post_process.py"
    description: "单元测试——验证 hook 链执行、失败处理"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\durable_execution.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\post_process.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_durable_execution.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_post_process.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\.pre-commit-config.yaml"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——被 ≥2 个 L01 模块消费"
  - module_id: "PS-STD-001"
    section: "§7"
    reason: "Task 31字段定义——durable execution 需与 TaskStatus 状态机集成"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §12——B30/B31 盲点详情与专业对标"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
    reason: "Task 模型——durable execution 需与 Task 生命周期集成"

assigned_model: "claude-opus-4.7"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 30000
timeout_minutes: 90

acceptance_criteria:
  - "durable_execution.py: Activity Protocol——execute() + checkpoint() + resume()"
  - "durable_execution.py: WorkflowManager——编排多个 Activity，保存进度快照"
  - "durable_execution.py: 进程崩溃后 resume() 可从最近快照恢复，不重复执行已完成 Activity"
  - "post_process.py: PostProcessPipeline——register_hook() + run()"
  - "post_process.py: 内置 3 个 hook——lint_hook / format_hook / typecheck_hook"
  - "post_process.py: hook 失败时的策略——skip/warn/abort 可配置"
  - "pytest tests/unit/test_durable_execution.py -v 全部通过"
  - "pytest tests/unit/test_post_process.py -v 全部通过"
  - "SHARED-QUICKREF.yml 更新——新增 durable_execution + post_process 入口"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\durable_execution.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\shared\post_process.py
  3. 删除 D:\ZephyrAlpha\tests\unit\test_durable_execution.py
  4. 删除 D:\ZephyrAlpha\tests\unit\test_post_process.py
  5. 还原 __init__.py 对应导出
  6. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0104"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "claude-opus-4.7"
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
