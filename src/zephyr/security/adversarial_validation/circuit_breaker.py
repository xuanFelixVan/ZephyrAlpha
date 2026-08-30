# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §7.2 + §16 Phase 2b
# [MODULE] zephyr.security.adversarial_validation.circuit_breaker
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.models
# [CONSUMERS] game_day_runner.py; validator.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Auto-pauses adversarial testing when defense stress exceeds threshold; 3 states: CLOSED->OPEN->HALF_OPEN->CLOSED; cool_down_ms = 30000
# [MODIFY-GUARD] State transitions per blueprint §7.2 FSM; cool_down_ms MUST NOT be set below 10000
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CircuitBreakerOpenError when attempting to run while circuit is OPEN
# [TESTS] tests/red_blue/test_circuit_breaker.py
# [A_module] module_id=MOD-INF-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: cool_down_ms 参数
#   fields: 参数 cool_down_ms（无注解）
#   code: circuit_breaker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CircuitBreaker
#   name_en: CircuitBreaker
#   intro: class CircuitBreaker 源码 L82-L201
#   desc: 公共方法（定义序）: state, is_open, before_run, after_run, trip, reset, force_state, opened_at, cool_down_ms, bypass_h…
#   inputs: cool_down_ms
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: CircuitBreaker
#   downstream: game_day_runner.py; validator.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Final

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
    error_code = "ZA-SC-0012"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


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

    @state.setter
    def state(self, value):
        """写入：state（Stage 4 公共化）。"""
        self._state = value

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

    def trip(self) -> None:
        """公共 API（primary）：触发熔断。

        Stage 4 公共化：将熔断器状态置为 OPEN，记录打开时间戳并递增 trip_count。
        私有 _trip() 为 thin wrapper，委托到本方法。
        """
        self._state = CircuitState.OPEN
        self._opened_at = time.time() * 1000
        self._trip_count += 1
        logger.warning("circuit_breaker_tripped trip_count=%d cool_down_ms=%d", self._trip_count, self._cool_down_ms)

    def _trip(self) -> None:
        # Stage 4 公共化：thin wrapper，保留以兼容既有内部调用。
        self.trip()

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

    # ── Stage 4 公共化（2026-07-28）：force_state + opened_at property ──
    # 消除 tests/safety/test_async_monitor.py 中对 _state / _opened_at 的直接写。
    # force_state 绕过 _maybe_transition() 侧效，专供测试注入确定状态。

    def force_state(self, state: CircuitState, opened_at: float | None = None) -> None:
        """公共 API：强制设置熔断器状态（Stage 4 公共化，测试注入用）。

        与 state property getter 区别：getter 会触发 _maybe_transition()（OPEN→HALF_OPEN
        自动冷却转换），本方法直接赋值不触发，供测试精确控制状态。
        opened_at 仅在 state=OPEN 时有意义（控制冷却计时起点）。
        """
        self._state = state
        if opened_at is not None:
            self._opened_at = opened_at

    @property
    def opened_at(self) -> float:
        """熔断打开时间戳（毫秒，Stage 4 公共化，可读写）。"""
        return self._opened_at

    @opened_at.setter
    def opened_at(self, value: float) -> None:
        self._opened_at = value

    # ── Stage 4 公共化（2026-07-28）：只读属性暴露 ──
    # 消除 tests/safety/test_circuit_breaker.py 对私有属性的直接访问。

    @property
    def cool_down_ms(self) -> int:
        """公共 API：冷却时间（毫秒）。"""
        return self._cool_down_ms

    @property
    def bypass_history(self) -> list[float]:
        """公共 API：bypass 率历史记录（最近 20 条）。"""
        return self._bypass_history

    @property
    def trip_count(self) -> int:
        """公共 API：熔断累计触发次数。"""
        return self._trip_count
