---
task_id: "TASK-INF-0222"
source_blueprint: "MOD-INF-011"
source_section: "变更记录"

title: "VMS 蓝图版本管理——变更日志维护 + 版本号同步 + TASK-INF 任务卡版本追溯"
description: |
  维护蓝图变更记录的持续更新机制：
  1. 确保蓝图 §变更记录 与所有 TASK-INF-0201~0224 的完成状态同步
  2. 每次蓝图版本 bump 在变更记录中增行记录：日期/版本号/变更内容(≥50字)
  3. 全局版本一致性检查：MOD-INF-011 蓝图 version / blueprint-registry.yaml / module-id-registry.yaml / b_vector_memory.yaml 四者的版本号必须一致
  4. 创建版本一致性检验脚本 vms_version_sync_check.py
  5. 所有 TASK-INF-XXXX task_id 注册到本次 session 的任务清单中
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\module-id-registry.yaml"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\vms_version_sync_check.py"
    description: "VMS 版本一致性检查脚本——比对蓝图/registry/SSoT 三处版本号 → 不一致立即告警"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\vms_version_sync_check.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\module-id-registry.yaml"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "scripts/governance/ 路径合规"
  - module_id: "PS-STD-011"
    section: "MTH-012"
    reason: "涌现式设计——版本变更跟随 content evolution"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "变更记录节——当前 v0.7.0 及历史 6 个版本的变更内容作为版本管理基线"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 5000
timeout_minutes: 15

acceptance_criteria:
  - "vms_version_sync_check.py 存在且可独立运行——输出 SSoT_version / registry_version / blueprint_version 三处比对"
  - "三处版本号一致 → VERSION SYNCED / 不一致 → VERSION DRIFT DETECTED + 列出差异"
  - "vms_version_sync_check.py 应作为 pre-commit hook 的一部分运行"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\scripts\governance\vms_version_sync_check.py
  2. 如果脚本产生 false positive（如 intentional version divergence）→ 在脚本白名单中允许特定组合不同步
  3. 版本检查不影响 VMS 正常运行——它仅做一致性告警

depends_on:
  - "TASK-INF-0211"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "governance"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-011"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
