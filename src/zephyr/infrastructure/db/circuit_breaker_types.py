# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md | §
# [MODULE] zephyr.infrastructure.db.circuit_breaker_types
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.db.__init__
# [CONSUMERS] db.circuit_breaker_repo; shared.schema.severity_types (re-export)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Values MUST align with shared.schema.severity_types.CircuitBreakerState
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_circuit_breaker_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
circuit_breaker_types.py - CircuitBreakerState enum for db package
===================================================================

Moved from shared.schema.severity_types.
Canonical location is now zephyr.infrastructure.db.circuit_breaker_types.
"""

from __future__ import annotations

from enum import Enum

__all__ = ["CircuitBreakerState"]


class CircuitBreakerState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"
