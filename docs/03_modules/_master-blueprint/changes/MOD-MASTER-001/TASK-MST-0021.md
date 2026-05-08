---
task_id: "TASK-MST-0021"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §二十二 时间维度腐烂防护——CT-KNOWLEDGE-FRESHNESS-001/CT-HOUSEKEEPING-001/CT-SESSION-HANDOFF-001"

title: "实现知识新鲜度废止 + 文件卫生保洁 + AI 会话手递手协议"
description: |
  实现 §二十二 定义的时间维度三防护契约：
  (1)CT-KNOWLEDGE-FRESHNESS-001 知识新鲜度与废止——KE 语义生命周期管理；
  freshness_signals: 含版本号→stale_warning；引用API端点→API变更后标记；last_verified>180d→NEEDS_REVIEW；
  3级降级: stale_warning(CE降低优先级)→needs_review(仅include_stale=true时返回)→deprecated(仅审计)；
  (2)CT-HOUSEKEEPING-001 系统文件卫生保洁——每周日 02:00 清理 cache/ChromaDB orphan/SQLite WAL/session-logs/git gc；
  disk watermark: 80% WARN / 90% CRITICAL→暂停非P0任务；
  (3)CT-SESSION-HANDOFF-001 AI会话手递手协议——Session A→Session B 无损上下文转移；
  handoff_manifest(.trae/session_state/{CT_ID}_progress.yaml) 持久化 completion_percent/remaining_items/known_issues/next_session_instructions。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\knowledge_base\\ke_manager.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\knowledge_base\\freshness_manager.py"
    description: "知识新鲜度管理器——CT-KNOWLEDGE-FRESHNESS-001——3级降级+每月sweep"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\housekeeping.py"
    description: "文件卫生保洁——CT-HOUSEKEEPING-001——清理+disk watermark"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\handoff_manager.py"
    description: "会话手递手管理器——CT-SESSION-HANDOFF-001——读写handoff manifest"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\check_handoff_manifests.py"
    description: "CI 手递手 manifest 完整性检查——≤30天未更新→CI WARN"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_freshness_manager.py"
    description: "新鲜度管理器单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_handoff_manager.py"
    description: "手递手管理器单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\knowledge_base\\freshness_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\housekeeping.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\handoff_manager.py"
  - "D:\\ZephyrAlpha\\scripts\\governance\\check_handoff_manifests.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_freshness_manager.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_handoff_manager.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\knowledge_base\\ke_manager.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§二十二——freshness+housekeeping+handoff 三契约完整定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 18000
timeout_minutes: 90

acceptance_criteria:
  - "freshness_manager.py 实现 KE 3 级降级 (stale_warning→NEEDS_REVIEW→DEPRECATED) + 每月 freshness_sweep"
  - "stale_warning KE: CE 降低优先级排在 fresh KE 之后；NEEDS_REVIEW: 仅 include_stale=true 返回"
  - "housekeeping.py 清理 __pycache__/.pytest_cache/.mypy_cache/.ruff_cache/ + ChromaDB vacuum + WAL TRUNCATE"
  - "disk watermark 80%→WARN / 90%→CRITICAL→暂停非P0"
  - "handoff_manager.py 读写 handoff manifest(.trae/session_state/{CT_ID}_progress.yaml)"
  - "handoff manifest 包含 completion_percent/remaining_items/known_issues/next_session_instructions"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除新增的 4 个源码/脚本文件
  2. 删除新增的测试文件
  3. 如有创建 handoff manifests → 删除 .trae/session_state/CT-*_progress.yaml

depends_on: []
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
