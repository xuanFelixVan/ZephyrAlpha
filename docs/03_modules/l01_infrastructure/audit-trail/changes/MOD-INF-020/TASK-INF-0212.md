---
task_id: "TASK-INF-0212"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §4.2 元审计——MetaAuditLogger"

title: "实现元审计记录器——审计系统自身操作的全量留痕"
description: |
  实现 `src/zephyr/audit_trail/query.py`（或独立 `meta_audit.py`）中的 `MetaAuditLogger`。
  元审计记录方法：
  - `log_audit_query(querier, query_params)`——记录谁执行了什么查询
  - `log_index_rebuild(trigger, entries_count)`——记录索引重建触发原因+重建量
  - `log_integrity_check(result: IntegrityReport)`——记录完整性校验结果
  - `log_retention_enforcement(deleted_entries, dry_run)`——记录保留期执行
  所有元审计自身也写入 JSONL（通过 AuditWriter），防止无限递归——元审计条目标记 `entry_type=audit_query`。
  落地决策 D-020-05 + D-020-49。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\query.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\query.py"
    description: "追加 MetaAuditLogger 类——4种元审计记录方法"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_meta_audit.py"
    description: "单元测试——每次查询自动留痕 + 索引重建触发记录"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\query.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_meta_audit.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-001"
    reason: "审计操作留痕——自身也需记录"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§4.2——MetaAuditLogger 方法定义 + D-020-05/49 决策"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 6000
timeout_minutes: 35

acceptance_criteria:
  - "log_audit_query('alice', params) → 写入 audit_query 事件到 JSONL"
  - "log_index_rebuild('manual', 5000) → 含 trigger + entries_count"
  - "log_integrity_check(report) → 含 is_valid 状态"
  - "log_retention_enforcement(100, True) → dry_run=True 标记"
  - "元审计条目不触发递归写——无 StackOverflow"
  - "4/4 方法单元测试通过"

rollback_instructions: |
  1. 从 query.py 中删除 MetaAuditLogger 类
  2. 删除 test_meta_audit.py

depends_on:
  - "TASK-INF-0209"
  - "TASK-INF-0211"
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
