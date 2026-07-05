# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §2.3
# [MODULE] zephyr.governance.resilience_governance.circuit_breaker
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.escalation.escalation_engine;zephyr.governance.escalation;zephyr.governance.intelligence_governance.self_test
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] error_budget是022特有扩展;接口call()->bool;与shared/resilience/circuit_breaker(MOD-INF-016)是不同实现(016用call(func)->raises)
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 熔断拒绝→call()返回False;error_budget耗尽→降级
# [TESTS] tests/infrastructure/test_escalation_engine.py
# [A_module] module_id=MOD-RES_circuit_breaker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
Circuit Breaker — MOD-INF-022

Half-open/closed/open state machine with error budget gating, cooldown, and auto-recovery.
Blueprint: docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md §2.3
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from enum import Enum


class CircuitState(Enum):
    # 5.92.2 修复: 统一日志格式, 返回 value 而非 ClassName.MEMBER
    def __str__(self) -> str:
        return self.value

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 60
    half_open_max_requests: int = 1
    cooldown_seconds: int = 300
    error_budget_per_hour: int = 10


class CircuitBreaker:
    def __init__(self, name: str, config: CircuitBreakerConfig | None = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count: int = 0
        self._success_count: int = 0
        self._last_failure_time: float = 0.0
        self._error_budget_consumed: int = 0
        self._error_budget_reset: float = time.time()
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            self._maybe_transition()
            return self._state

    def call(self) -> bool:
        with self._lock:
            self._maybe_transition()
            if self._state is CircuitState.OPEN:
                return False
            return True

    def record_success(self) -> None:
        with self._lock:
            if self._state is CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
            self._failure_count = 0

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            self._consume_error_budget()
            if self._failure_count >= self.config.failure_threshold or self._state is CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN

    def force_open(self) -> None:
        with self._lock:
            self._state = CircuitState.OPEN

    def force_close(self) -> None:
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0

    def _maybe_transition(self) -> None:
        if self._state is not CircuitState.OPEN:
            return
        if self._last_failure_time == 0.0:
            return
        elapsed = time.time() - self._last_failure_time
        if elapsed >= self.config.cooldown_seconds:
            self._state = CircuitState.HALF_OPEN
            self._success_count = 0

    def _consume_error_budget(self) -> None:
        now = time.time()
        if now - self._error_budget_reset > 3600:
            self._error_budget_consumed = 0
            self._error_budget_reset = now
        self._error_budget_consumed += 1

    @property
    def error_budget_remaining(self) -> int:
        return max(0, self.config.error_budget_per_hour - self._error_budget_consumed)


# 代理导出：CircuitBreakerOpenError 实际定义在 infrastructure.reliability.circuit_breaker
# 使用延迟导入避免循环依赖


def __getattr__(name):
    """延迟导入 CircuitBreakerOpenError 避免循环依赖."""
    if name == "CircuitBreakerOpenError":
        from zephyr.infrastructure.reliability.circuit_breaker import CircuitBreakerOpenError

        return CircuitBreakerOpenError
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["CircuitBreaker", "CircuitBreakerConfig", "CircuitBreakerOpenError", "CircuitState"]
