"""Agent Orchestrator (Orc)
=====================================

Vibe Coding 2.0 基础设施 · L12 跨层支撑层 · 5 大核心服务之一

职责
----
任务生命周期管理 + Agent 调度 + 沙箱执行 + 幻觉检测

状态机
------
DRAFT → QUEUED → ASSIGNED → RUNNING → REVIEWING → COMPLETED
分支 : BLOCKED / FAILED / CANCELLED / HALLUCINATING

基础设施
--------
任务队列 : SQLite + asyncio.Queue（2）
          NATS JetStream（beta+ 升级）
沙箱     : Windows ACL + 只读挂载
          Docker Desktop（beta+ 升级）

P0 降级红线
-----------
DEGRADE-003: 沙箱创建失败 → 任务 FAIL，拒绝无沙箱运行（安全优于可用性）

架构归属
--------
LPC 双轨架构 B 轨（Bounded Context · 无 l<NN>_ 前缀）
架构决策：ADR-0022 目录双轨治理 + ADR-0017 Orc + ADR-0018 Sandbox
架构真源：docs/02_enterprise_architecture/target-architecture/
         vibe-coding-infrastructure-architecture.md §3.4

依赖
----
- CE（context_engine/）：上下文构建
- VMS（vector_memory/）：任务输出写入
- LSG（llm_security/）：工具调用验证
"""

__all__ = ['agent_health_monitor', 'agent_orchestrator', 'agent_quality', 'autonomy_guard', 'backup_manager', 'batch_orchestrator', 'benchmark_runner', 'blind_spot_closure', 'blueprint_health', 'bulkhead_manager', 'canary_manager', 'capacity_budget', 'chaos_engine', 'config_manager', 'construction_guide', 'contract_registry', 'contract_router', 'data_lifecycle', 'deferred_queue', 'degrade_cascade', 'dependency_lock', 'design_decisions', 'disk_guard', 'dlq_manager', 'failure_matcher', 'feature_flag', 'file_task_mapper', 'finding_bridge', 'hallucination_detector', 'housekeeping', 'incident_postmortem', 'ke_quality', 'knowledge_freshness', 'lean_scanner', 'model_registry', 'network_partition', 'path_index', 'phase_executor', 'prompt_version', 'reconciliation_loop', 'risk_registry', 'rollback_manager', 'rolling_upgrade', 'schema_migration', 'session_conflict', 'session_handoff', 'session_manager', 'stability_guard', 'startup_sequencer', 'state_propagation', 'state_synchronizer', 'system_transfer', 'task_queue', 'teardown_manager', 'trigger_router', 'version_manifest', 'wave_generator']
