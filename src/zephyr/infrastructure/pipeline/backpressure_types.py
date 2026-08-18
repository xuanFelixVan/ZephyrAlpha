# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.backpressure_types
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.contracts.core.trace_context
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-009 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
backpressure_types.py - Pipeline backpressure signal data types
===============================================================

Moved from shared.contracts.backpressure (pause/throttle/resume).
Canonical location is now zephyr.infrastructure.pipeline.backpressure_types.

CTR-BP-001: BackpressurePause — downstream overload pause signal
CTR-BP-002: BackpressureThrottle — downstream throttle signal
CTR-BP-003: BackpressureResume — downstream recovery signal
"""

from __future__ import annotations

from dataclasses import dataclass

from zephyr.shared.contracts.core.trace_context import TraceContext

__all__ = [
    "BackpressurePause",
    "BackpressureResume",
    "BackpressureThrottle",
]


@dataclass(frozen=True)
class BackpressurePause:
    duration_ms: int
    idempotency_key: str
    reason: str
    signal_id: str
    symbol: str
    action: str = "PAUSE"
    schema_version: str = "1.0"
    trace_context: TraceContext | None = None


@dataclass(frozen=True)
class BackpressureThrottle:
    idempotency_key: str
    max_rate_per_sec: int
    reason: str
    signal_id: str
    symbol: str
    action: str = "THROTTLE"
    schema_version: str = "1.0"
    trace_context: TraceContext | None = None


@dataclass(frozen=True)
class BackpressureResume:
    idempotency_key: str
    reason: str
    signal_id: str
    symbol: str
    action: str = "RESUME"
    schema_version: str = "1.0"
    trace_context: TraceContext | None = None
