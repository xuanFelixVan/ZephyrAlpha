# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ports
# [MODULE] zephyr.trading.ports
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] zephyr.trading.auto_runtime_core;zephyr.trading.work_orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Ports define structural interfaces only; no concrete implementations; no imports from zephyr.infrastructure.pipeline
# [MODIFY-GUARD] blueprint.md §ports; runtime/__init__.py __all__
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_runtime_ports.py
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Protocol-based interface layer for runtime->pipeline dependency abstraction.

Breaks the deep dependency chain: runtime->pipeline->mcp->rollback->llm_security->shared.schema
by defining structural interfaces that runtime depends on instead of importing
pipeline concrete implementations directly.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ports.py
# 层: 算法
# - id: A1
#   name_zh: ① PipelineDispatcherProtocol
#   name_en: PipelineDispatcherProtocol
#   intro: Structural interface for pipeline task dispatching.
#   desc: Structural interface for pipeline task dispatching. Runtime depends on this protocol inst…；公共方法（定义序）: dispatc…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② PipelineStatusReporterProtocol
#   name_en: PipelineStatusReporterProtocol
#   intro: Structural interface for pipeline status reporting.
#   desc: Structural interface for pipeline status reporting. Runtime depends on this protocol inst…；公共方法（定义序）: get_sta…
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ TaskDispatchProtocol
#   name_en: TaskDispatchProtocol
#   intro: Structural interface for task dispatch handler used by runt…
#   desc: Structural interface for task dispatch handler used by runtime task queue.；公共方法（定义序）: handle；源码 L105-L108
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: PipelineDispatcherProtocol, PipelineStatusReporterProtocol, TaskDispatchProtocol
#   downstream: zephyr.trading.auto_runtime_core;zephyr.trading.work_orchestrator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from zephyr.shared.schema.task_types import TaskCard

__all__ = [
    "PipelineDispatcherProtocol",
    "PipelineStatusReporterProtocol",
    "TaskDispatchProtocol",
]


@runtime_checkable
class PipelineDispatcherProtocol(Protocol):
    """Structural interface for pipeline task dispatching.

    Runtime depends on this protocol instead of importing
    PipelineOrchestrator directly, breaking the runtime->pipeline link.
    """

    def dispatch(self, task: TaskCard) -> bool: ...


@runtime_checkable
class PipelineStatusReporterProtocol(Protocol):
    """Structural interface for pipeline status reporting.

    Runtime depends on this protocol instead of importing
    pipeline status models directly.
    """

    def get_status(self) -> dict[str, Any]: ...


@runtime_checkable
class TaskDispatchProtocol(Protocol):
    """Structural interface for task dispatch handler used by runtime task queue."""

    def handle(self, item: object) -> bool: ...
