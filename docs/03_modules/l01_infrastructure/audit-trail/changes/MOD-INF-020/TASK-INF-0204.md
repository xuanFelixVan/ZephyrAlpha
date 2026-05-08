---
task_id: "TASK-INF-0204"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.4 密码学完整性数据模型——AuditEntryV1 核心字段"

title: "实现 AuditEntryV1 核心模型——身份/密码学完整性/时序字段（D-020-04/09/14）"
description: |
  实现 `AuditEntryV1` Pydantic V2 BaseModel 的核心字段集中。覆盖：
  - 身份与版本：entry_id(UUID7)/schema_version('1.1.0')/entry_type(AuditEventType)
  - 密码学完整性 D-020-04：prev_entry_hash/entry_hash/hmac_signature
  - Agent 签名 D-020-14：agent_did/agent_signature/agent_public_key_pem
  - Merkle：merkle_batch_id
  - 时序一致性 D-020-09：lamport_clock(tuple[str,int])/utc_timestamp
  - 操作上下文：agent_id/ide_source/session_id/task_id/task_type/permission_level/provenance_depth
  config=ConfigDict(frozen=True, extra='forbid')——不可变 + 禁止额外字段。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"
    description: "追加 AuditEntryV1 BaseModel——核心字段（身份/密码学/时序/上下文 ~20字段）"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_audit_entry.py"
    description: "单元测试——frozen=True 不可变 + extra='forbid' 拒绝额外字段 + entry_hash 自一致性"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_audit_entry.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\**\\*.md"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2——ConfigDict(frozen=True, extra='forbid')"
  - module_id: "PS-STD-001"
    section: "§7"
    reason: "字段定义遵循 metadata-registry"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.4——AuditEntryV1 全字段定义 + D-020-04/09/14 决策"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 60

acceptance_criteria:
  - "AuditEntryV1 含 ~20 核心字段：entry_id/schema_version/entry_type/prev_entry_hash/entry_hash/hmac_signature/agent_did/agent_signature/agent_public_key_pem/merkle_batch_id/lamport_clock/utc_timestamp/agent_id/ide_source/session_id/task_id/task_type/permission_level/provenance_depth"
  - "lamport_clock 类型为 tuple[str, int]"
  - "frozen=True：创建后修改任一字段 → ValidationError"
  - "extra='forbid'：传入未定义字段 → ValidationError"
  - "entry_id 格式 UUID7——时间有序，毫秒精度"
  - "model_dump_json() 排除 None 字段后 JSON 长度 < 2000 chars"

rollback_instructions: |
  1. 从 models.py 中删除 AuditEntryV1 类定义
  2. 从 test_audit_entry.py 中删除对应测试
  3. 确认 writer.py / query.py 未引用 AuditEntryV1

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
