# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.governance.persistence.circuit_breaker_types
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.ops.circuit_breaker_types
# [CONSUMERS] zephyr.ops.circuit_breaker_repo
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# 代理模块：将 zephyr.governance.persistence.circuit_breaker_types 重定向到 zephyr.governance.circuit_breaker_types
from zephyr.ops.circuit_breaker_types import CircuitBreakerState

__all__ = ["CircuitBreakerState"]
