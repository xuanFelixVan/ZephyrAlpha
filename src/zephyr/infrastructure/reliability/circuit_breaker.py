# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.reliability.circuit_breaker
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_circuit_breaker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Circuit Breaker — 熔断器：连续失败 -> OPEN -> 暂停执行。

依据：
    蓝图 MOD-TASK_SYSTEM §6.2.1 + v0.6.0
    任务卡 TASK-INF-0108 (Part 1/4)

功能：
    - 三状态：CLOSED/OPEN/HALF_OPEN
    - 熔断阈值：failure_threshold_continuous=3, timeout_s=60
    - HALF_OPEN 试探性恢复
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 3
    recovery_timeout_s: int = 60
    _state: CircuitState = CircuitState.CLOSED
    _failure_count: int = 0
    _last_failure_time: float = 0.0
    _success_count: int = 0
    _half_open_success_threshold: int = 2
    _lock: Lock = field(default_factory=Lock)

    def call(self, func, *args, **kwargs):
        with self._lock:
            if self._state is CircuitState.OPEN:
                if time.time() - self._last_failure_time >= self.recovery_timeout_s:
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit {self.name} is OPEN. "
                        f"Retry in {self.recovery_timeout_s - (time.time() - self._last_failure_time):.0f}s"
                    )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self) -> None:
        with self._lock:
            if self._state is CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._half_open_success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
            elif self._state is CircuitState.CLOSED:
                self._failure_count = 0

    def _on_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN

    @property
    def state(self) -> CircuitState:
        return self._state

    def reset(self) -> None:
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0


class CircuitBreakerOpenError(Exception):
    error_code = "ZA-IF-0010"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code
