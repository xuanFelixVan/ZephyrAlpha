# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
"""
resilience/__init__.py — 韧性工具包入口（Phase 2 新增）

零依赖共享基类——gates/circuit_breaker.py 可选在此基础上叠加 SQLite 持久化 + 门禁集成。

子模块：
  - retry.py            — 重试策略（指数退避 + jitter）
  - circuit_breaker.py  — 熔断器状态机（CLOSED/OPEN/HALF_OPEN，零依赖）
  - fallback.py         — 降级策略模式

SSoT: MOD-INF-016 §2.6 shared-resilience
Version: 0.1.0
"""

__all__ = [
    "RetryConfig",
    "RetryExhaustedError",
    "async_retry",
    "CircuitState",
    "CircuitBreaker",
    "CircuitOpenError",
    "FallbackChain",
    "fallback",
    "retry",
    "circuit_breaker",
    "fallback",
]

from .circuit_breaker import (  # noqa: E402
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
)
from .fallback import FallbackChain, fallback  # noqa: E402
from .retry import RetryConfig, RetryExhaustedError, async_retry  # noqa: E402
