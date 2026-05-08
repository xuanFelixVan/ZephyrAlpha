---
task_id: "TASK-INF-0255"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 7.4 + §6.13 B81 + §9 exit code 21"
title: "嵌套环境检测——nested_env honeypot + 环境深度敏感信号"
description: |
  实现嵌套环境检测：
  检测回滚本身是否在 Docker/k8s/VM 嵌套环境中执行。
  嵌套环境 git worktree/quota/timeout 参数与裸机不同。
  exit code 21 (NESTED_ENV_DETECTED) → 自动调整回滚参数适配嵌套约束。
  防止回滚在容器/VM 中因资源/路径限制而失败。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "嵌套环境检测——container/VM detection + 参数自适应"
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
    reason: "本蓝图——§6.13 B81 嵌套环境检测"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 6000
timeout_minutes: 25
acceptance_criteria:
  - "检测 /.dockerenv / /run/.containerenv /proc/1/cgroup"
  - "嵌套环境 → 自动调整 worktree/quota/timeout 约束"
  - "exit 21 (NESTED_ENV_DETECTED) → 继续执行（适配后）"
rollback_instructions: |
  1. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py
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
