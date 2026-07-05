# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.schema.severity_types
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] gates.task_types; gates.check_types.ct_audit_findings_resolved; shared.schema.schemas; shared.schema.audit_types; kb.knowledge_types
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Priority P0-P4 MUST align with GOV-TASK-004 §2.2; AuditSeverity MUST be backward-compatible alias for Priority P0-P2
# [MODIFY-GUARD] GOV-TASK-004; ADR-0030
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError on invalid enum value
# [TESTS] tests/test_schemas.py
# [A_module] module_id=MOD-SHR_severity_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations

from enum import Enum

__all__ = [
    "AuditSeverity",
    "CircuitBreakerState",
    "Priority",
    "SafetyLevel",
]


class SafetyLevel(str, Enum):
    L = "L"
    M = "M"
    H = "H"


class AuditSeverity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class Priority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class CircuitBreakerState(str, Enum):
    """Circuit breaker states — re-homed from infrastructure_runtime_integration.db.circuit_breaker_types
    to eliminate shared->infrastructure circular import."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"
