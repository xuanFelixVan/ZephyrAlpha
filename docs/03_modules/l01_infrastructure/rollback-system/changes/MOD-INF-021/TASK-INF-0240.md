---
task_id: "TASK-INF-0240"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 6.9 + §6.12 B64"
title: "Git 基础设施防护——git_infra_snapshot + inotify hooks/config 监控"
description: |
  实现 Git 基础设施污染防护：
  定期 git_infra_snapshot 保存 .git/config + .git/hooks/ 到受保护位置。
  inotify/Watchdog 实时监控 git hooks 和配置文件的修改。
  检测到非 Owner 修改 git hooks → 立即告警 + 从 snapshot 恢复。
  防止 AI 通过篡改 git hooks 绕过门禁执行恶意代码。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\git_infra_snapshot.py"
    description: "Git 基础设施快照——.git/config + hooks/ 定期备份 + Watchdog 实时监控"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\git_infra_snapshot.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.12 B64 Git 基础设施防护"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30
acceptance_criteria:
  - "定期快照 .git/config + .git/hooks/"
  - "Watchdog 实时监控 git hooks/config 修改"
  - "非 Owner 修改 hooks → 告警 + 从 snapshot 恢复"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\git_infra_snapshot.py
depends_on:
  - "TASK-INF-0232"
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
