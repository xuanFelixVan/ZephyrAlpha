# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.schema.severity_types
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Priority P0-P4 MUST align with GOV-TASK-004 §2.2; AuditSeverity MUST be backward-compatible alias for Priority P0-P2
# [MODIFY-GUARD] GOV-TASK-004; ADR-0030
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError on invalid enum value
# [TESTS] tests/automation/test_auto_split.py; tests/autonomy/test_task_system_red_team.py; tests/blueprint/test_blueprint_decomposer.py; tests/db/test_task_repo_db.py; tests/gate/test_circuit_breaker_types.py  # 2026-09-05 STEWARD B20 重锚：AI-00 修复脚本 src. 前缀 bug 漏网（AST/patch 直查 23 个测试）
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
# [ALGO_FLOW] external: docs/03_modules/_domain_shared/algo_flow/schema/severity_types.yaml
"""

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
