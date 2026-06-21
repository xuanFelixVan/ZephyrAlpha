# 代理模块：将 zephyr.governance.persistence.circuit_breaker_types 重定向到 zephyr.governance.circuit_breaker_types
from zephyr.ops.circuit_breaker_types import CircuitBreakerState

__all__ = ["CircuitBreakerState"]
