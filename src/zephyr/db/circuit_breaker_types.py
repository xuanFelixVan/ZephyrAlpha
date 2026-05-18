# [BLUEPRINT] MOD-INF-012 | 03_modules/_cross_layer/database/blueprint.md | §

# [MODULE] zephyr.db.circuit_breaker_types

# [INVARIANTS] Values MUST align with shared.schema.severity_types.CircuitBreakerState

# [MODIFY-GUARD] none

# [CONSUMERS] db.circuit_breaker_repo; shared.schema.severity_types (re-export)

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT]

# [TESTS]

"""
circuit_breaker_types.py - CircuitBreakerState enum for db package
===================================================================

Moved from shared.schema.severity_types.
Canonical location is now zephyr.db.circuit_breaker_types.
"""

from __future__ import annotations

from enum import Enum

__all__ = ["CircuitBreakerState"]


class CircuitBreakerState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"
