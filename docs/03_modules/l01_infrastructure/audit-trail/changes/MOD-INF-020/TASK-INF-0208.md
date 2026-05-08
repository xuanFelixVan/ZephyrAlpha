---
task_id: "TASK-INF-0208"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §4 审计查询接口 + §4.2 元审计 + §4.3 证据包 + §4.4 合规映射 + §5 异常检测辅助模型"

title: "实现全部辅助模型——IntegrityReport/DriftResult/EvidencePack/ReplayVerification/RetentionReport 等"
description: |
  实现蓝图引用的全部辅助 Pydantic V2 模型：
  - IntegrityReport(§4.1): is_valid/total_entries/hash_chain_breaks[]/hmac_failures[]/merkle_mismatches[]/checked_at
  - DriftResult/DriftReport(§5.2): entry_id/drift_detected/drift_type/expected/actual/severity/blueprint_ref
  - EvidencePack/CryptoProofs/DecisionDossier(§4.3): task_id/generated_at/timeline/decision_dossier/cryptographic_proofs/agent_identity_chain
  - ReplayVerification/ReplayMismatch(§2.14): target_time/files_in_audit/files_in_git/matched/mismatched/coverage_pct
  - RetentionReport(§6.2): entries_to_delete/total_size_bytes/oldest_entry_date/tiers_affected/dry_run
  - ConsistencyConflict(§2.13): entry_a_id/entry_b_id/field/value_a/value_b/ide_a/ide_b/severity
  全部 frozen=True + extra='forbid'。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"
    description: "追加 10+ 辅助模型"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_models.py"
    description: "追加辅助模型单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_models.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§4—辅助模型定义 + §5.2 DriftResult + §2.13 ConsistencyConflict + §2.14 ReplayVerification + §4.3 EvidencePack + §6.2 RetentionReport"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 45

acceptance_criteria:
  - "IntegrityReport 含 6 字段——类型正确"
  - "EvidencePack 含 7 字段——含嵌套 CryptoProofs/DecisionDossier"
  - "ReplayVerification 含 6 字段——mismatched 为 list[ReplayMismatch]"
  - "RetentionReport 含 5 字段"
  - "ConsistencyConflict 含 8 字段"
  - "DriftResult 含 8 字段"
  - "全部模型 frozen=True + extra='forbid'"
  - "10/10 单元测试通过"

rollback_instructions: |
  1. 从 models.py 中删除辅助模型类
  2. 从 test_models.py 中删除对应测试

depends_on:
  - "TASK-INF-0202"
  - "TASK-INF-0203"
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
