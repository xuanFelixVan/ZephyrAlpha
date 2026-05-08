---
task_id: "TASK-INF-0210"
source_blueprint: "MOD-INF-011"
source_section: "§8 集成目标"

title: "6 系统集成目标落地——VectorBridge + RetrievalFeedback + Audit Trail 集成"
description: |
  实现蓝图 §8 定义的 6 个目标系统的 VMS 集成：
  1. Context Engine (MOD-INF-008): CE→VMS 向量检索——context_assembler.py import InProcessVectorMemory.search() → 向量语义检索 KE 条目
  2. Knowledge Base (MOD-KB-001): KB→VMS 写入——KE 入库时同步写入 knowledge Collection → BridgeLayer.sync_knowledge()
  3. Feedback Loop (MOD-INF-010): FLE→VMS 双向——失败模式写入 lessons Collection + RetrievalFeedback 消费检查质量反馈
  4. Orchestrator (MOD-INF-006): Orc→VMS 写入——任务决策写入 decisions Collection
  5. SessionManager: Session→VMS 写入——session 结束时压缩摘要写入 session_snapshots Collection
  6. Audit Trail (MOD-INF-020): VMS 操作审计——每次 VMS 读写写入审计日志 + WriteTrace
  实现 VectorBridge 类作为外部集成适配器 + RetrievalFeedback 消费 FLE 信号
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\vector_bridge.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\context-engine\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\vector_bridge.py"
    description: "VectorBridge 实现——search_for_ce(query, k) / sync_knowledge(ke_id, content) / write_decision(task_id, decision_text) / write_session_summary(session_id, summary) / audit_operation(operation)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"
    description: "RetrievalFeedback 实现——record(hit_id, was_useful, task_id) + write_failure_pattern(pattern) + long_tail_tracker"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\vector_bridge.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\retrieval_feedback.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"

applicable_rules:
  - module_id: "CT-CE-VMS-001"
    section: "全篇"
    reason: "CE→VMS 集成契约——VMS.search() 必须满足 CE build 阶段的检索需求"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——所有 integration payload 类型"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§8 集成目标表——6 个目标系统的集成方式/集成点/验证方法完整定义"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\vector_bridge.py"
    reason: "VectorBridge 骨架——填充集成方法实现"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\context-engine\\blueprint.md"
    reason: "CT-CE-VMS-001 集成契约——CE build 阶段 VMS 检索的调用约定"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "VectorBridge.search_for_ce('因子衰减', k=5) → 内部调用 InProcessVectorMemory.search() → 返回 ScoredHit 列表"
  - "VectorBridge.sync_knowledge('KE-001', content) → 写入 VMS/knowledge Collection + 附带 WriteTrace"
  - "VectorBridge.write_decision('TASK-0042', '决定使用 RRF 而非加权求和') → 写入 VMS/decisions Collection"
  - "VectorBridge.write_session_summary('session-001', summary) → 写入 VMS/session_snapshots Collection"
  - "VectorBridge.audit_operation('search', {'query': 'test', 'results': 5}) → 写入审计日志"
  - "RetrievalFeedback.record('hit-001', was_useful=True, task_id='TASK-0042') → 存储反馈记录"
  - "RetrievalFeedback.write_failure_pattern('模式匹配失败导致...') → 写入 VMS/lessons Collection"

rollback_instructions: |
  1. 如果 VectorBridge 集成导致 CE build 阶段异常 → 设置 VMS_INTEGRATION_MODE=read_only（仅读不写）
  2. 还原 vector_bridge.py 和 retrieval_feedback.py 至 TASK-INF-0208 的骨架状态
  3. 移除对其他模块中对 VectorBridge / RetrievalFeedback 的 import

depends_on:
  - "TASK-INF-0208"
  - "TASK-INF-0209"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "data"
  - "observability"
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
