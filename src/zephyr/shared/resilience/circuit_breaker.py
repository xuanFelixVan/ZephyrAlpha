# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.resilience.circuit_breaker
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_circuit_breaker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
circuit_breaker.py —— 轻量熔断器状态机（Phase 2 新增 | 零依赖）

对标：gates/circuit_breaker.py（SQLite 持久化 + 门禁集成版）的轻量基类。

本模块是 gates/circuit_breaker.py 的**零依赖互补品**：
  - 本模块 → 纯内存状态机，适合本地调用保护（不持久化）
  - gates/circuit_breaker.py → SQLite 持久化 + Capability 管控 + Gate Engine 集成

状态迁移（经典三态）：
  CLOSED  ──(failure_rate ≥ threshold)──→  OPEN
  OPEN    ──(timeout_ms 到期)─────────→  HALF_OPEN
  HALF_OPEN ──(一次成功)───────────────→  CLOSED
  HALF_OPEN ──(任意一次失败)───────────→  OPEN

设计原则：
  - 线程安全（RLock）
  - 零持久化依赖——模块 import 即可用
  - 滑动窗口失败计数

AI 施工约定：
  - 跨模块调用保护用 gates/circuit_breaker.py
  - 模块内部自保护（如限流、API 调用保护）用本模块

SSoT: MOD-INF-016 §2.6 shared-resilience
Version: 0.1.0
"""

from __future__ import annotations

import time
from enum import Enum, unique
from threading import RLock
from typing import Any

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "CircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
]


@unique
class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpenError(ZephyrBaseError):
    """熔断器处于 OPEN 状态时拒绝调用。"""
    error_code = "ZA-SH-0020"

    def __init__(self, name: str, message: str | None = None, *, details: dict[str, Any] | None = None, error_code: str | None = None) -> None:
        super().__init__(
            message or f"CircuitBreaker '{name}' is OPEN",
            details=details or {},
        )
        self.circuit_name: str = name
        if error_code is not None:
            self.error_code = error_code


class CircuitBreaker:
    """纯内存三态熔断器。

    Usage::

        cb = CircuitBreaker("llm_api", failure_threshold=5, recovery_timeout_ms=30_000)

        try:
            result = cb.call(my_function, arg1, arg2)
        except CircuitOpenError:
            result = fallback_value
    """

    def __init__(
        self,
        name: str,
        *,
        failure_threshold: int = 5,
        recovery_timeout_ms: int = 30_000,
        half_open_max_calls: int = 1,
    ) -> None:
        self.name: str = name
        self._failure_threshold: int = failure_threshold
        self._recovery_timeout_ms: int = recovery_timeout_ms
        self._half_open_max_calls: int = half_open_max_calls

        self._lock = RLock()
        self._state: CircuitState = CircuitState.CLOSED
        self._failure_count: int = 0
        self._last_failure_time: float = 0.0
        self._opened_at: float = 0.0
        self._half_open_calls: int = 0

    @property
    def state(self) -> CircuitState:
        with self._lock:
            return self._state

    @property
    def failure_count(self) -> int:
        with self._lock:
            return self._failure_count

    def _transition(self) -> CircuitState:
        """执行状态检查与自动迁移（调用方需持有锁）。"""
        if self._state is CircuitState.OPEN:
            if (time.monotonic() - self._opened_at) * 1000 >= self._recovery_timeout_ms:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0

        if self._state is CircuitState.HALF_OPEN and self._half_open_calls >= self._half_open_max_calls:
            pass

        return self._state

    def record_success(self) -> None:
        # 5.16.1 修复：failure_count 重置移入锁内，避免锁外竞态导致断路器永远到不了 threshold
        with self._lock:
            if self._state is CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._half_open_calls = 0
            self._failure_count = 0

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()

            if self._state is CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._opened_at = time.monotonic()
                return

            if self._state is CircuitState.CLOSED and self._failure_count >= self._failure_threshold:
                self._state = CircuitState.OPEN
                self._opened_at = time.monotonic()

    def reset(self) -> None:
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_failure_time = 0.0
            self._opened_at = 0.0
            self._half_open_calls = 0

    def call(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        with self._lock:
            state = self._transition()
            if state is CircuitState.OPEN:
                raise CircuitOpenError(
                    self.name,
                    details={
                        "state": state.value,
                        "failure_count": self._failure_count,
                        "opened_at": self._opened_at,
                    },
                )
            if state is CircuitState.HALF_OPEN:
                self._half_open_calls += 1

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception:
            self.record_failure()
            raise
