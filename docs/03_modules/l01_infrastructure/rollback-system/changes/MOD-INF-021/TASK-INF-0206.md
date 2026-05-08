---
task_id: "TASK-INF-0206"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 2.1 + §6.2 B7"

title: "Partial Revert 实现——file-glob 选择性回滚"
description: |
  实现 partial_revert(commit_sha, file_globs) 方法：
  git revert --no-commit {commit_sha} → git reset HEAD {safe_files} → git commit。
  支持 file-glob 粒度选择性回滚，按 AI 氛围编程核心体验需求——最小破坏半径。
  partial_revert 后强制全量 G0 验证——被保留文件 + 被 revert 文件都存在（R7 缓解）。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "新增 partial_revert() 方法——file-glob 粒度选择性回滚"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§2.1 partial_revert 操作定义 + §6.2 B7 无 Partial Rollback 盲点"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 30

acceptance_criteria:
  - "partial_revert(commit_sha, file_globs=['**/*.py']) 仅回滚匹配 glob 的文件"
  - "被保留的正确文件不受影响"
  - "partial_revert 后强制执行全量 G0 验证"
  - "commit message 标注 'PARTIAL_REVERT: original={sha}'"

rollback_instructions: |
  1. git checkout HEAD~1 -- D:\ZephyrAlpha\src\zephyr\rollback\rollback_executor.py

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
