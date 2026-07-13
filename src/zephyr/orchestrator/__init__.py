# [DOMAIN] D_ORCHESTRATOR
# [A_module] module_id=MOD-ORC_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from zephyr.orchestrator.contracts.alert_handler import AlertHandler
from zephyr.orchestrator.execution.context_bridge import ContextBridge
from zephyr.orchestrator.execution.script_runner import ScriptRunner

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Agent Orchestrator (Orc)
=====================================

Vibe Coding 2.0 基础设施 · 遥测 跨层支撑层 · 5 大核心服务之一

职责
----
任务生命周期管理 + Agent 调度 + 沙箱执行 + 幻觉检测

状态机（真源：zephyr.governance.rule_enforcement.task_types.TaskStatus）
----------------------------------------------------------------------
PENDING -> READY -> IN_PROGRESS -> COMPLETED -> VERIFIED
分支 : BLOCKED / FAILED / RETRY / WAITING / CANCELLED
合法迁移定义见 TaskRepository.transition() + state_propagation.PROPAGATION_RULES（派生自 TaskStatus）

基础设施
--------
任务队列 : SQLite + asyncio.Queue（2）
          NATS JetStream（beta+ 升级）
沙箱     : Windows ACL + 只读挂载
          Docker Desktop（beta+ 升级）

P0 降级红线
-----------
DEGRADE-003: 沙箱创建失败 -> 任务 FAIL，拒绝无沙箱运行（安全优于可用性）

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
    "deferred_queue",
    "failure_matcher",
    "file_task_mapper",
    "hallucination_detector",
    "rollback_manager",
    "task_queue",
]

_SUBMODULES = [
    "agent_health_monitor",
    "agent_orchestrator",
    "deferred_queue",
    "failure_matcher",
    "file_task_mapper",
    "hallucination_detector",
    "rollback_manager",
    "task_queue",
    "MemoryWriter",
]


def __getattr__(name: str):
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f"zephyr.orchestrator.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__.append("AlertHandler")

__all__.append("ContextBridge")

__all__.append("ScriptRunner")

from zephyr.orchestrator.execution.memory_writer import MemoryWriter, archive_to_vms

__all__.append("MemoryWriter")
