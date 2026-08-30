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
# [TESTS] tests/test_schemas.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: severity_types.py
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 AuditSeverity, CircuitBreakerState, Priority, SafetyLevel（共 4 符号）
#   desc: __init__ import L0；__all__ 4 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（4 类）
#   name_en: data classes
#   intro: SafetyLevel, AuditSeverity, Priority, CircuitBreakerState
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
