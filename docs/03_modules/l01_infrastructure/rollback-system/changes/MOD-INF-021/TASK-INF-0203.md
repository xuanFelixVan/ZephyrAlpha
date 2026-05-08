---
task_id: "TASK-INF-0203"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 1.3 + §6.2 B4/B5 + 决策 D-021-02 + D-021-03"

title: "RollbackExecutor 核心封装——preflight_check + preview + 四级回滚操作"
description: |
  实现 RollbackExecutor 核心类：
  - preflight_check()：git status --porcelain / rev-parse --abbrev-ref HEAD / merge-base 检查
  - preview(commit_sha)：git diff --name-only → changed_files/conflict_risk/estimated_size
  - 四级回滚操作：full_revert(全量)/partial_revert(文件级)/discard(未提交)/hard_reset(核弹)
  - 集成全局锁管理 + 依赖影响分析调用
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_lock.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "完善 RollbackExecutor——preflight_check + preview + full_revert/partial_revert/discard/hard_reset"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——所有模型基座"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§2.1 四级回滚操作定义 + §6.2 B4/B5 盲点 + D-021-02/D-021-03 决策"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "preflight_check() 检查 working tree 干净性、detached HEAD、rebase/merge 状态、remote 超前"
  - "preview(commit_sha) 返回 changed_files/conflict_risk/estimated_size_bytes"
  - "full_revert(commit_sha) 执行 git revert + DB 重建 + G0 验证"
  - "discard(file_list) 执行 git checkout/restore 撤销未提交变更"
  - "hard_reset(token) 执行 git reset --hard {commit_sha}——仅 token-gated"
  - "所有操作写入审计日志"

rollback_instructions: |
  1. git checkout HEAD~1 -- D:\ZephyrAlpha\src\zephyr\rollback\rollback_executor.py

depends_on:
  - "TASK-INF-0201"
  - "TASK-INF-0202"
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
