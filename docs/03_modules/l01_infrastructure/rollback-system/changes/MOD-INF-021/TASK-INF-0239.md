---
task_id: "TASK-INF-0239"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.8 + §6.12 B63"
title: "分支拓扑回滚——topology_change_log + reflog 分支恢复"
description: |
  实现分支拓扑回滚能力：
  每次分支操作（merge/rebase/cherry-pick/branch delete）记录 topology_change_log。
  回滚涉及分支结构变更时，从 topology_change_log 重建操作前分支拓扑。
  利用 git reflog 恢复被删除的分支。
  支持 zephyr rollback --branch-topology 回滚分支级操作。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\topology_change_log.py"
    description: "分支拓扑变更日志——记录 merge/rebase/cherry-pick/branch delete 操作"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\topology_change_log.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B63 分支拓扑回滚"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "merge/rebase/cherry-pick/delete → 自动记录到 topology_change_log"
  - "回滚涉及分支结构变更时从 topology_change_log 重建拓扑"
  - "利用 git reflog 恢复被删除分支"
  - "zephyr rollback --branch-topology CLI 支持"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\topology_change_log.py
depends_on:
  - "TASK-INF-0203"
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
