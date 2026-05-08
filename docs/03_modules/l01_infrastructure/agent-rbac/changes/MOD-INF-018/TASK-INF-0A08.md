---
task_id: "TASK-INF-0A08"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.7 L4 — Sequence Guard 序列护栏 + D-018-09"

title: "实现L4 SequenceGuard — 操作序列追踪与危险序列阻断（最关键的盲点补丁）"
description: |
  实现sequence_guard.py。会话级操作序列追踪：每个Agent会话维护独立操作链，
  在SQLite中存储操作序列(非Context Window——防止上下文窗口操控)。
  危险序列阻断：定义forbidden_sequences规则集(read_credential→write_network→delete_logs等6+序列)。
  sequence_timeout=300s(5分钟间隙视为新序列)。
  跨Session关联检测：Agent间隐式通信检测(cross_session_correlation + inter_agent_communication_detection)。
  实施D-018-09：D2 Layer 3——单步合法≠序列安全，防御数据外泄/提权/破坏链。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\identity.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\sequence_guard.py"
    description: "SequenceGuard——per-session操作链/SQLite存储/forbidden_sequences匹配/sequence_timeout/跨Session关联/inter_agent_communication"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_sequence_guard.py"
    description: "测试——危险序列阻断/跨Session关联/合法序列放行/timeout/误报处理"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\sequence_guard.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_sequence_guard.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.7 L4 Sequence Guard+forbidden_sequences规则集+跨Session关联+决策D-018-09"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 16000
timeout_minutes: 60

acceptance_criteria:
  - "forbidden_sequences数量>=6(含data_exfiltration/privilege_escalation/destruction_chain)"
  - "read_credential→write_network→delete_logs七步链被成功阻断"
  - "跨Session关联：Agent A写→Agent B读→检测inter_agent_communication"
  - "sequence_timeout默认300s，可配置"
  - "操作链存在SQLite中(不受Context Window限制)——B126盲点关闭"
  - "WhiteList序列：Owner定义的合法序列不被阻断"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\sequence_guard.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_sequence_guard.py
  3. 如有SQLite数据库创建——删除var/agent_rbac/sequence_guard.db

depends_on:
  - "TASK-INF-0A02"
  - "TASK-INF-0A05"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-018"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
