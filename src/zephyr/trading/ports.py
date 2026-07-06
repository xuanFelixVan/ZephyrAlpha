# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §ports
# [MODULE] zephyr.trading.ports
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS] zephyr.trading.auto_runtime_core;zephyr.trading.work_orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Ports define structural interfaces only; no concrete implementations; no imports from zephyr.infrastructure.pipeline
# [MODIFY-GUARD] blueprint.md §ports; runtime/__init__.py __all__
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_runtime_ports.py
# [A_module] module_id=MOD-ORC_ports | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Protocol-based interface layer for runtime→pipeline dependency abstraction.

Breaks the deep dependency chain: runtime→pipeline→mcp→rollback→llm_security→shared.schema
by defining structural interfaces that runtime depends on instead of importing
pipeline concrete implementations directly.
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
    PipelineOrchestrator directly, breaking the runtime→pipeline link.
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
