---
task_id: "TASK-INF-0215"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 4.1 + §6.2 B20/B27"
title: "1 人运维 CLI——zephyr rollback status/stats/preview/cancel/kill/gc/drill"
description: |
  实现 1 人运维 CLI 命令集，支持 30 秒内理解回滚状态：
  zephyr rollback status ——显示最近回滚状态
  zephyr rollback stats ——MTTR/频率/成功率
  zephyr rollback preview --tag {name} ——预览语义化回滚目标
  zephyr rollback cancel {rollback_id} ——BREAK_GLASS 取消
  B27 要求 CLI 在最烂状态下也能运行——独立脚本无 Python 依赖。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\audit_trail\cli.py"
    description: "回滚 CLI——zephyr rollback status/stats/preview/cancel"
  - path: "D:\\ZephyrAlpha\\scripts\\zephyr_rollback_cli.ps1"
    description: "最烂状态 CLI（PowerShell 脚本）——零 Python 依赖"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\cli.py"
  - "D:\\ZephyrAlpha\\scripts\\zephyr_rollback_cli.ps1"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§2.2 回滚流程 CLI + B20 BREAK_GLASS+B27 最烂状态 CLI"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 10000
timeout_minutes: 40
acceptance_criteria:
  - "zephyr rollback status 显示最近回滚记录摘要"
  - "zephyr rollback stats 显示 MTTR/频率/成功率"
  - "zephyr rollback preview --tag {name} 预览回滚影响"
  - "zephyr rollback cancel {id} BREAK_GLASS 适配（B20）"
  - "最烂状态 CLI（.ps1）仅依赖 git 原生命令"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\cli.py
  2. 删除 D:\ZephyrAlpha\scripts\zephyr_rollback_cli.ps1
depends_on:
  - "TASK-INF-0211"
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
