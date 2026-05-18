# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
# [MODULE] zephyr.shared.schema.severity_types
# [INVARIANTS] Priority P0-P4 MUST align with GOV-TASK-004 §2.2; AuditSeverity MUST be backward-compatible alias for Priority P0-P2
# [MODIFY-GUARD] GOV-TASK-004; ADR-0030
# [CONSUMERS] gates.task_types; gates.check_types.ct_audit_findings_resolved; shared.schema.schemas; shared.schema.audit_types; kb.knowledge_types
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError on invalid enum value
# [TESTS] tests/unit/test_schemas.py; tests/unit/shared/test_schemas.py
from __future__ import annotations

from enum import Enum

from zephyr.db.circuit_breaker_types import CircuitBreakerState

__all__ = [
    "SafetyLevel",
    "AuditSeverity",
    "Priority",
    "CircuitBreakerState",
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
