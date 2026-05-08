---
task_id: "TASK-INF-0202"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.1 两层审计粒度（决策 D-020-01）"

title: "实现两层审计粒度模型——TaskAuditSummary + FileAuditDetail Pydantic V2 模型"
description: |
  实现 `TaskAuditSummary` 和 `FileAuditDetail` 两个 Pydantic V2 BaseModel。
  TaskAuditSummary 含 16 字段：event_id/timestamp/agent_id/ide_source/lamport_counter/
  session_id/task_id/task_type/action_summary/files_affected/result/permission_level/
  provenance_depth/tokens_used/cost_estimate_usd/duration_ms。
  FileAuditDetail 含 9 字段：event_id/task_audit_id/timestamp/lamport_counter/
  file_path/action_type/sha256_before/sha256_after/diff_size_bytes。
  task_audit_id 外键关联 TaskAuditSummary.event_id。
  落地决策 D-020-01：两层审计粒度——任务级摘要（快速浏览）+ 文件级明细（问题定位）。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"
    description: "追加 TaskAuditSummary + FileAuditDetail + FileActionType 枚举"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_models.py"
    description: "追加两层模型序列化/反序列化 + 字段校验测试"

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
  - module_id: "PS-STD-001"
    section: "§7"
    reason: "字段定义真源"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.1——TaskAuditSummary + FileAuditDetail 字段定义 + D-020-01 决策"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 45

acceptance_criteria:
  - "TaskAuditSummary 含全部 16 字段——event_id(UUID7-SEQ格式)/timestamp(UTC)/agent_id/ide_source/lamport_counter/session_id/task_id/task_type/action_summary/files_affected/result/permission_level/provenance_depth(ProvenanceDepth)/tokens_used/cost_estimate_usd/duration_ms"
  - "FileAuditDetail 含全部 9 字段——event_id(UUID7-SEQ)/task_audit_id/timestamp/lamport_counter/file_path/action_type(FileActionType)/sha256_before/sha256_after/diff_size_bytes"
  - "FileActionType(str, Enum): READ/WRITE/CREATE/DELETE"
  - "config=ConfigDict(frozen=True, extra='forbid')"
  - "event_id 格式校验：AUD-T-{UUID7}-{SEQ} / AUD-F-{UUID7}-{SEQ}"
  - "Pydantic V2 model_dump() / model_validate_json() 往返无丢失"

rollback_instructions: |
  1. 从 models.py 中删除 TaskAuditSummary / FileAuditDetail / FileActionType
  2. 从 test_models.py 中删除对应测试
  3. 确认 writer.py / query.py 未引用这些类（若已引用需同步清理）

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
