# [BLUEPRINT] MOD-DATA_SEC
# [MODULE] zephyr.data.persistence.circuit_breaker_types
# [DOMAIN] D_DATA_SEC
# [DEPENDENCIES] zephyr.ops.circuit_breaker_types
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# 代理模块：将 zephyr.data.persistence.circuit_breaker_types 重定向到 zephyr.governance.circuit_breaker_types
# 原因：severity_types.py (immutable_core) 导入 zephyr.data.persistence.circuit_breaker_types，
# 但该路径在模块迁移后不存在。此代理模块保持immutable_core不变，仅提供导入兼容。
from zephyr.ops.circuit_breaker_types import CircuitBreakerState

__all__ = ["CircuitBreakerState"]
