---
task_id: "TASK-INF-0202"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 1.2 + §6.2 B2 + 决策 D-021-05"

title: "区分 revert vs discard 两套流程——pre-commit FAIL 鸡与蛋悖论解决"
description: |
  实现两套独立流程：已 commit 但后验失败 → git revert；pre-commit FAIL → discard changes(git checkout/restore)。
  解决蓝图 §2.2 中"pre-commit FAIL → git revert"的鸡与蛋悖论——未 commit 的代码没有可 revert 的对象。
  在 rollback_executor.py 中实现 discard 流程：git checkout -- {files} 或 git restore {files}。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "新增 discard_changes() 方法——未 commit 变更的撤销流程 + rollback_or_discard() 路由决策"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——所有模型基座"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§2.2 pre-commit 鸡与蛋悖论 + §6.2 B2 描述 + D-021-05 失败信号三分类决策"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 6000
timeout_minutes: 30

acceptance_criteria:
  - "rollback_executor.py 含 discard_changes(file_list) 方法——git checkout/restore 指定文件"
  - "rollback_executor.py 含 rollback_or_discard() 路由——根据是否已 commit 选择 revert 或 discard"
  - "discard 前检查被丢弃文件是否含 owner_session_id → 是则拒绝 + 告警(R8 缓解)"
  - "discard 操作记录到审计日志"

rollback_instructions: |
  1. 从 D:\ZephyrAlpha\src\zephyr\rollback\rollback_executor.py 移除 discard_changes() 和 rollback_or_discard() 方法
  2. 恢复文件到 git checkout HEAD~1 状态

depends_on:
  - "TASK-INF-0201"
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
