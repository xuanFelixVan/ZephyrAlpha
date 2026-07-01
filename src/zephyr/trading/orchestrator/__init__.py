# [A_module] module_id=MOD-ORC_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from zephyr.trading.orchestrator.alert_handler import AlertHandler
from zephyr.trading.orchestrator.context_bridge import ContextBridge
from zephyr.trading.orchestrator.script_runner import ScriptRunner

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.integration.runtime_core.orchestrator
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
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
架构决策： 目录双轨治理 +  Orc +  Sandbox
架构真源：architecture_model/technology/vibe_coding_infrastructure_tech_stack.yaml

依赖
----
- CE（context_engine/）：上下文构建
- VMS（vector_memory/）：任务输出写入
- LSG（llm_security/）：工具调用验证
"""

__all__ = [
    "agent_health_monitor",
    "agent_orchestrator",
    "agent_quality",
    "alert_handler",
    "autonomy_guard",
    "backup_manager",
    "batch_orchestrator",
    "benchmark_runner",
    "blind_spot_closure",
    "blueprint_scorer",
    "bulkhead_manager",
    "canary_manager",
    "capacity_budget",
    "chaos_engine",
    "chaos_hooks",
    "construction_guide",
    "context_bridge",
    "contract_registry",
    "contract_router",
    "data_lifecycle",
    "deferred_queue",
    "degrade_cascade",
    "dependency_lock",
    "design_decisions",
    "disk_guard",
    "dlq_manager",
    "failure_matcher",
    "fault_types",
    "feature_flag",
    "file_task_mapper",
    "finding_bridge",
    "hallucination_detector",
    "housekeeping",
    "incident_postmortem",
    "ke_quality",
    "knowledge_freshness",
    "lean_scanner",
    "memory_writer",
    "model_registry",
    "network_partition",
    "path_index",
    "phase_executor",
    "prompt_version",
    "reconciliation_loop",
    "risk_registry",
    "rollback_manager",
    "rolling_upgrade",
    "schema_migration",
    "script_runner",
    "session_conflict",
    "session_manager",
    "stability_guard",
    "startup_sequencer",
    "state_propagation",
    "state_synchronizer",
    "system_transfer",
    "task_queue",
    "teardown_manager",
    "trigger_router",
    "version_manifest",
    "wave_generator",
]

_SUBMODULES = [
    "agent_health_monitor",
    "agent_orchestrator",
    "agent_quality",
    "autonomy_guard",
    "backup_manager",
    "batch_orchestrator",
    "benchmark_runner",
    "blind_spot_closure",
    "blueprint_scorer",
    "bulkhead_manager",
    "canary_manager",
    "capacity_budget",
    "chaos_engine",
    "chaos_hooks",
    "construction_guide",
    "contract_registry",
    "contract_router",
    "data_lifecycle",
    "deferred_queue",
    "degrade_cascade",
    "dependency_lock",
    "design_decisions",
    "disk_guard",
    "dlq_manager",
    "failure_matcher",
    "fault_types",
    "feature_flag",
    "file_task_mapper",
    "finding_bridge",
    "hallucination_detector",
    "housekeeping",
    "incident_postmortem",
    "ke_quality",
    "knowledge_freshness",
    "lean_scanner",
    "model_registry",
    "network_partition",
    "path_index",
    "phase_executor",
    "prompt_version",
    "reconciliation_loop",
    "risk_registry",
    "rollback_manager",
    "rolling_upgrade",
    "schema_migration",
    "session_conflict",
    "session_manager",
    "stability_guard",
    "startup_sequencer",
    "state_propagation",
    "state_synchronizer",
    "system_transfer",
    "task_queue",
    "teardown_manager",
    "trigger_router",
    "version_manifest",
    "wave_generator",
    "MemoryWriter",
    "alert_handler",
    "context_bridge",
    "memory_writer",
    "script_runner",
]


def __getattr__(name: str):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f"zephyr.trading.orchestrator.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__.append("AlertHandler")

__all__.append("ContextBridge")

__all__.append("ScriptRunner")

from zephyr.trading.orchestrator.memory_writer import MemoryWriter, archive_to_vms

__all__.append("MemoryWriter")
