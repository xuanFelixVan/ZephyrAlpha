# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §4
# [MODULE] zephyr.shared.contracts.orchestration_protocol
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.rollback; zephyr.governance.ops_governance; zephyr.infrastructure.rollback; zephyr.trading.orchestrator.chaos_hooks; zephyr.trading.orchestrator.batch_orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Protocol MUST NOT import from zephyr.trading; only structural subtyping
# [MODIFY-GUARD] shared/contracts/__init__.py; all consumers
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError when orchestration layer unavailable; consumers MUST handle
# [TESTS]
# [A_module] module_id=MOD-SHR_orchestration_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import importlib
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ShadowCanaryProtocol(Protocol):
    """Shadow canary deployment protocol - decouples D-RES/D-GOV from D-ORCH."""

    def shadow(self, strategy: str, context: str) -> Any: ...

    def promote(self, result: Any) -> bool: ...


@runtime_checkable
class ChaosEngineProtocol(Protocol):
    """Chaos fault injection engine protocol - decouples D-RES/D-GOV from D-ORCH."""

    def get_injection_points(self) -> list[dict[str, Any]]: ...

    def inject(self, injection_type_or_point: str = "", **kwargs: Any) -> Any: ...

    def recover(self, target: str = "") -> Any: ...

    def verify(self, target: str = "") -> Any: ...

    def cleanup(self) -> None: ...

    def fault_inject(self, target: str, fault_type: str, params: dict[str, Any] | None = None) -> Any: ...

    def get_active_faults(self) -> list[Any]: ...

    def is_healthy(self) -> bool: ...


@runtime_checkable
class BatchOrchestratorProtocol(Protocol):
    """Batch task orchestrator protocol - decouples D-RES/D-GOV from D-ORCH."""

    def claim_next(self) -> Any | None: ...

    def mark_done(self, task_id: str) -> None: ...

    def mark_failed(self, task_id: str, reason: str = "") -> None: ...

    def recover_stale_claims(self) -> int: ...

    def progress(self) -> Any: ...


def create_shadow_canary() -> ShadowCanaryProtocol:
    _mod = importlib.import_module("zephyr.autonomy_core.shadow_canary")
    _ShadowCanary = _mod.ShadowCanary
    return _ShadowCanary()


def create_chaos_engine() -> ChaosEngineProtocol:
    _mod = importlib.import_module("zephyr.trading.orchestrator.chaos_engine")
    _ChaosEngine = _mod.ChaosEngine
    return _ChaosEngine()


def create_batch_orchestrator(repo: Any, batch_id: str, worker_id: str, **kwargs: Any) -> BatchOrchestratorProtocol:
    _mod = importlib.import_module("zephyr.trading.orchestrator.batch_orchestrator")
    _BatchOrchestrator = _mod.BatchOrchestrator
    return _BatchOrchestrator(repo, batch_id, worker_id, **kwargs)
