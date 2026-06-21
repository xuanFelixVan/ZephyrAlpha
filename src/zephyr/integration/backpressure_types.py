# [A_module] module_id=MOD-ORC_backpressure_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md

# [MODULE] zephyr.orchestration.pipeline_routing.backpressure_types

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] pipeline.backpressure_manager; shared.contracts.backpressure (re-export)

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
backpressure_types.py - Pipeline backpressure signal data types
===============================================================

Moved from shared.contracts.backpressure (pause/throttle/resume).
Canonical location is now zephyr.orchestration.pipeline_routing.backpressure_types.

CTR-BP-001: BackpressurePause — downstream overload pause signal
CTR-BP-002: BackpressureThrottle — downstream throttle signal
CTR-BP-003: BackpressureResume — downstream recovery signal
"""


from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from zephyr.integration.shared_08.contracts.core.trace_context import TraceContext

__all__ = [
    "BackpressurePause",
    "BackpressureThrottle",
    "BackpressureResume",
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
    trace_context: Optional[TraceContext] = None


@dataclass(frozen=True)
class BackpressureThrottle:
    idempotency_key: str
    max_rate_per_sec: int
    reason: str
    signal_id: str
    symbol: str
    action: str = "THROTTLE"
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None


@dataclass(frozen=True)
class BackpressureResume:
    idempotency_key: str
    reason: str
    signal_id: str
    symbol: str
    action: str = "RESUME"
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None
