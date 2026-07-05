# [BLUEPRINT] MOD-SHARED-002
# [MODULE] zephyr.shared.contracts.backpressure._types
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.core.trace_context
# [CONSUMERS] zephyr.shared.contracts.backpressure.resume; zephyr.shared.contracts.backpressure.pause; zephyr.shared.contracts.backpressure.throttle
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
# Re-homed type definitions — eliminates circular import from shared -> infrastructure
"""Shared internal backpressure type definitions.
Previously re-exported from infrastructure_runtime_integration.pipeline.backpressure_types.
Now canonical for shared layer, keeping infrastructure free of shared->infra reverses."""

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
