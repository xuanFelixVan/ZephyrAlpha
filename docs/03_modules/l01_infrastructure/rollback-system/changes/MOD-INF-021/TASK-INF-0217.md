---
task_id: "TASK-INF-0217"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 4.3 + §6.2 B17 + §9 CT-RBK-GATE-001"
title: "CT-RBK-GATE-001 集成契约落地——Exit Code 传播到 Gate/Pipeline 判定链"
description: |
  实现 CT-RBK-GATE-001 集成契约全部 46 个 exit code：
  RollbackExecutor.revert() 返回 exit code 0-46 → Gate 判定 → Pipeline 行为传播。
  实现 exit_code→Gate判定→Pipeline 行为的映射表 + 全局状态传播闭环。
  MOD-MASTER-001 §4 集成契约落地。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\_domain-governance\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\contract.py"
    description: "CT-RBK-GATE-001 集成契约落地——46 exit code 枚举 + Gate+Pipeline 行为映射"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\contract.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§9 CT-RBK-GATE-001 完整 46 exit code 契约表"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 7000
timeout_minutes: 25
acceptance_criteria:
  - "contract.py 含全部 46 exit code 的枚举定义"
  - "exit_code → Gate判定 → Pipeline 行为 映射完整"
  - "RollbackExecutor.revert() 返回标准化 exit code"
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\contract.py
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
