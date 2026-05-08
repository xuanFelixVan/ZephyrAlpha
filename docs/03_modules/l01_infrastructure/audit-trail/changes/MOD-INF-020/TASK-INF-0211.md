---
task_id: "TASK-INF-0211"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §4.1 查询接口——AuditQuery"

title: "实现审计查询接口——SQLite 优先 + JSONL 回退 + trail_for_ai_context()"
description: |
  实现 `src/zephyr/audit_trail/query.py` 中的 `AuditQuery` 查询接口。
  查询方法：
  - `by_task(task_id)` → TaskAuditSummary
  - `by_task_details(task_id)` → list[FileAuditDetail]
  - `by_agent(agent_id, time_range)` → list[TaskAuditSummary]
  - `by_target(file_path)` → list[FileAuditDetail]
  - `by_permission_level(level, time_range)` → list[TaskAuditSummary]
  - `by_anomaly(anomaly_type, min_score)` → list[AuditEntryV1]
  - `by_drift(severity)` → list[AuditEntryV1]
  - `by_cost(min_cost_usd, time_range)` → list[AuditEntryV1]
  - `trail_for_ai_context(session_id)` → Markdown 字符串（AI 零推理可消费，token 预算控制）
  策略：SQLite 优先查询 → 不可用时回退 JSONL 扫描。
  落地决策 D-020-30 + D-020-31。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\query.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\query.py"
    description: "完整实现 AuditQuery 类——9种查询方法 + SQLite回退 + AI context生成"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_query.py"
    description: "单元测试——各方法正确性 + 回退逻辑 + trail_for_ai_context() 格式验证"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\query.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_query.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\data\\audit\\**\\*.db"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-003"
    reason: "查询审计日志的访问控制"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§4.1——AuditQuery 完整接口定义 + D-020-30/31"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 10000
timeout_minutes: 60

acceptance_criteria:
  - "by_task() 返回 TaskAuditSummary 或 None"
  - "by_agent('agent-001', (t1, t2)) 返回该时段该 Agent 的所有任务摘要"
  - "by_target('D:\\foo.txt') 返回该文件被谁操作过的完整 lineage"
  - "by_anomaly('PERMISSION_VIOLATION', 0.7) 按类型+分数字段过滤"
  - "trail_for_ai_context() 输出 Markdown 格式——含 session 摘要 + 文件变更清单"
  - "trail_for_ai_context() 经 prompt injection 净化——语义沙箱包裹 + 禁止AI指令关键词"
  - "SQLite 不可用时自动回退 JSONL 扫描——无异常抛出"
  - "9/9 查询方法单元测试通过"

rollback_instructions: |
  1. 删除 query.py 内容
  2. 删除 test_query.py

depends_on:
  - "TASK-INF-0202"
  - "TASK-INF-0204"
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
