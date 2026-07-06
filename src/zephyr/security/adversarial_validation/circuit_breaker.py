# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §7.2 + §16 Phase 2b
# [MODULE] zephyr.security.adversarial_validation.circuit_breaker
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models
# [CONSUMERS] game_day_runner.py; validator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Auto-pauses adversarial testing when defense stress exceeds threshold; 3 states: CLOSED→OPEN→HALF_OPEN→CLOSED; cool_down_ms = 30000
# [MODIFY-GUARD] State transitions per blueprint §7.2 FSM; cool_down_ms MUST NOT be set below 10000
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CircuitBreakerOpenError when attempting to run while circuit is OPEN
# [TESTS] tests/red_blue/test_circuit_breaker.py
# [A_module] module_id=MOD-SEC_circuit_breaker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging
import time
from enum import Enum

from zephyr.security.adversarial_validation.models import RedBlueReport

logger = logging.getLogger(__name__)

__all__: list[str] = ["CircuitBreaker", "CircuitBreakerOpenError", "CircuitState"]

DEFAULT_COOL_DOWN_MS: Final[int] = 30000
BYPASS_RATE_OPEN_THRESHOLD: Final[float] = 0.3
STRESS_LEVEL_THRESHOLD: Final[int] = 10


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(RuntimeError):
    pass


class CircuitBreaker:
    def __init__(self, cool_down_ms: int = DEFAULT_COOL_DOWN_MS) -> None:
        self._state: CircuitState = CircuitState.CLOSED
        self._cool_down_ms: int = max(cool_down_ms, 10000)
        self._opened_at: float = 0.0
        self._bypass_history: list[float] = []
        self._trip_count: int = 0

    @property
    def state(self) -> CircuitState:
        self._maybe_transition()
        return self._state

    @property
    def is_open(self) -> bool:
        return self.state is CircuitState.OPEN

    def before_run(self) -> None:
        if self.state is CircuitState.OPEN:
            remaining = self._cool_down_ms - (time.time() * 1000 - self._opened_at)
            raise CircuitBreakerOpenError(f"Circuit breaker OPEN. Cool-down remaining: {max(0, remaining):.0f}ms")

    def after_run(self, report: RedBlueReport) -> None:
        if report.total == 0:
            return

        bypass_rate = report.bypassed / report.total
        self._bypass_history.append(bypass_rate)
        self._bypass_history = self._bypass_history[-20:]

        avg_bypass_rate = sum(self._bypass_history) / len(self._bypass_history)

        if self._state is CircuitState.CLOSED and avg_bypass_rate > BYPASS_RATE_OPEN_THRESHOLD:
            self._trip()
        elif self._state is CircuitState.HALF_OPEN:
            if avg_bypass_rate > BYPASS_RATE_OPEN_THRESHOLD:
                self._trip()
            else:
                self._reset()
        elif self._state is CircuitState.CLOSED and report.circuit_breaker_open:
            self._trip()

    def _trip(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = time.time() * 1000
        self._trip_count += 1
        logger.warning("circuit_breaker_tripped trip_count=%d cool_down_ms=%d", self._trip_count, self._cool_down_ms)

    def _reset(self) -> None:
        self._state = CircuitState.CLOSED
        self._bypass_history = []
        logger.info("circuit_breaker_reset")

    def _maybe_transition(self) -> None:
        if self._state is CircuitState.OPEN:
            elapsed = time.time() * 1000 - self._opened_at
            if elapsed >= self._cool_down_ms:
                self._state = CircuitState.HALF_OPEN
                logger.info("circuit_breaker_half_open elapsed_ms=%d", elapsed)

    def reset(self) -> None:
        self._reset()
        self._trip_count = 0
        self._opened_at = 0.0
