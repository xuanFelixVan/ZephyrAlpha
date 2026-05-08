---
task_id: "TASK-INF-0203"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.3 分级 Provenance（决策 D-020-03）"

title: "实现分级 Provenance 模型——ProvenanceDepth + ProvenanceLight/Standard/Full"
description: |
  实现分级 Provenance 模型体系：
  ProvenanceDepth(str, Enum): LIGHT/STANDARD/FULL
  ProvenanceLight: agent_id/timestamp/action_type/ide_source/decision_brief（always_allow 操作）
  ProvenanceStandard: 含 decision_basis/guard_checks_executed/passed/failed/guard_result/confidence_level（auto_guard 操作）
  ProvenanceFull: 含 blocked_reason/attempted_action/rule_violated/escalation_triggered/escalation_target（blocked 操作）
  落地决策 D-020-03：Provenance 深度由权限级别决定。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"
    description: "追加 ProvenanceDepth 枚举 + ProvenanceLight/Standard/Full 三模型"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_models.py"
    description: "追加 Provenance 三级模型单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_models.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\**\\*.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.3——Provenance 三级模型字段定义 + D-020-03 决策"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 6000
timeout_minutes: 35

acceptance_criteria:
  - "ProvenanceDepth(str, Enum): LIGHT='light' / STANDARD='standard' / FULL='full'"
  - "ProvenanceLight 含 5 字段——agent_id/timestamp/action_type/ide_source/decision_brief(default='')"
  - "ProvenanceStandard 含 9 字段——含 decision_basis[]/guard_checks_executed[]/passed[]/failed[]/guard_result/confidence_level"
  - "ProvenanceFull 含 7 字段——含 blocked_reason/attempted_action/rule_violated/escalation_triggered/escalation_target"
  - "config=ConfigDict(frozen=True)"
  - "丢失字段时 model_validate() 抛出 ValidationError"

rollback_instructions: |
  1. 从 models.py 中删除 ProvenanceDepth + ProvenanceLight/Standard/Full
  2. 从 test_models.py 中删除对应测试

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
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
