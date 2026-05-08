---
task_id: "TASK-INF-0205"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 1.5 + §6.2 B15 + 决策 D-021-05"

title: "AutoRollbackTrigger 实现——auto_guard 监听 + 失败信号三分类（hard/soft/transient）"
description: |
  实现 AutoRollbackTrigger 核心类：
  - 监听 auto_guard 后验结果
  - 失败信号三分类：hard_failure(立即回滚)/soft_failure(forward-fix 优先)/transient(只重试不回滚)
  - 按失败来源分类：Drift Detector / CI FAIL / G6 secrets → hard；G0-G3 格式/语法 → soft；timeout/network → transient
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\gate-engine\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\auto_rollback_trigger.py"
    description: "自动回滚触发器——监听 auto_guard 后验结果 + 失败信号三分类"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\auto_rollback_trigger.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——所有模型基座"
  - module_id: "GOV-AI-002"
    section: "全篇"
    reason: "模型路由策略——auto_rollback_trigger 作为断路器触发条件之一"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§2.2 自动回滚流程 + §6.2 B15 失败信号分类 + D-021-05"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\drift-detector\\blueprint.md"
    reason: "Drift Detector 蓝图——理解 drift 信号格式（classify_failure 输入来源）"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "classify_failure(signal) → hard/soft/transient 三分类"
  - "hard_failure → 立即调用 RollbackExecutor.revert()"
  - "soft_failure → 等待 3 次 retry → 仍失败则 partial_revert"
  - "transient → 不回滚，只重试"
  - "触发信号来源验证——仅接受 trusted sources(auto_guard/gate_engine/Owner CLI)"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\auto_rollback_trigger.py

depends_on:
  - "TASK-INF-0201"
  - "TASK-INF-0203"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-021"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
