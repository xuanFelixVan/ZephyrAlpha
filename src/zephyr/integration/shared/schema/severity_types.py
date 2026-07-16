# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.integration.shared.schema.severity_types
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] gates.task_types; shared.schema.schemas; shared.schema.audit_types; kb.knowledge_types
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Priority P0-P4 MUST align with GOV-TASK-004 §2.2; AuditSeverity MUST be backward-compatible alias for Priority P0-P2
# [MODIFY-GUARD] GOV-TASK-004;
# [STABILITY] frozen
# [SAFETY] L
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] ValueError on invalid enum value
# [TESTS] tests/test_schemas.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=frozen | safety=L | ai_autonomy=immutable_core
# [TTL] permanent

from __future__ import annotations

from enum import Enum

from zephyr.shared.schema.severity_types import CircuitBreakerState

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
