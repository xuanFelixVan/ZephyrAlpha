# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.circuit_breaker_manager
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
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
# [A_module] module_id=MOD-INF_circuit_breaker_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
CircuitBreakerManager -- standalone circuit breaker manager (Netflix Hystrix equivalent).

Extracted from PipelineOrchestrator (SRC-0024) to manage model call failure protection.

Three-state circuit breaker:
  CLOSED   -> normal traffic, accumulate failures
  OPEN     -> short-circuit rejection, wait for cooldown
  HALF_OPEN -> trial request, decided by result

Usage:
    cb = CircuitBreakerManager(log_fn=orch._log)
    if cb.allow_request("task:module:model", "deepseek-v4"):
        try:
            result = call_model(...)
            cb.record_result("task:module:model", success=True)
        except Exception:
            cb.record_result("task:module:model", success=False)
"""

from __future__ import annotations

import time
from collections.abc import Callable

from zephyr.infrastructure.pipeline.models import CircuitBreakerState


class CircuitBreakerManager:
    """模型调用断路器管理器。

    每个 cb_key 独立维护状态机和失败窗口。
    """

    # 默认参数
    FAILURE_WINDOW_S: float = 60.0
    FAILURE_THRESHOLD: int = 3
    COOLDOWN_S: float = 30.0

    def __init__(
        self,
        *,
        log_fn: Callable[[str, str], None] | None = None,
        failure_window_s: float | None = None,
        failure_threshold: int | None = None,
        cooldown_s: float | None = None,
    ) -> None:
        """初始化断路器管理器。

        Args:
            log_fn: 日志回调 (level, message) -> None
            failure_window_s: 失败统计窗口（秒），默认 60.0
            failure_threshold: 窗口内失败次数阈值，默认 3
            cooldown_s: OPEN→HALF_OPEN 冷却时间（秒），默认 30.0
        """
        self._states: dict[str, CircuitBreakerState] = {}
        self._failures: dict[str, list[float]] = {}

        self._failure_window_s = failure_window_s or self.FAILURE_WINDOW_S
        self._failure_threshold = failure_threshold or self.FAILURE_THRESHOLD
        self._cooldown_s = cooldown_s or self.COOLDOWN_S

        self._log_fn = log_fn or (lambda level, msg: None)

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def allow_request(self, cb_key: str, model: str = "") -> bool:
        """检查是否允许通过断路器发起请求。

        Args:
            cb_key: 断路器键（如 "task_id:module_id:model"）
            model: 模型名（仅用于日志）

        Returns:
            True 如果允许请求（CLOSED 或 HALF_OPEN），False 如果断路器 OPEN
        """
        state = self._check_state(cb_key, model)
        return state is not CircuitBreakerState.OPEN

    def record_result(self, cb_key: str, success: bool) -> None:
        """记录一次调用的结果。

        - 成功：清除该 cb_key 的失败记录（CLOSED/HALF_OPEN→CLOSED）
        - 失败：追加失败时间戳

        Args:
            cb_key: 断路器键
            success: 调用是否成功
        """
        if success:
            self._failures.pop(cb_key, None)
            if cb_key in self._states:
                old = self._states[cb_key]
                if old is CircuitBreakerState.HALF_OPEN:
                    self._states[cb_key] = CircuitBreakerState.CLOSED
                    self._log("INFO", f"CircuitBreaker[{cb_key}] HALF_OPEN→CLOSED (试探成功)")
        else:
            self._failures.setdefault(cb_key, []).append(time.time())

    def reset_all(self) -> int:
        """重置所有断路器到 CLOSED 状态。

        Returns:
            被重置的断路器数量
        """
        count = len(self._states)
        self._states.clear()
        self._failures.clear()
        self._log("INFO", f"reset_circuit_breakers: {count} breaker(s) reset to CLOSED")
        return count

    def status(self, cb_key: str | None = None) -> dict[str, str]:
        """获取断路器状态快照。

        Args:
            cb_key: 可选，指定键则只返回该键状态

        Returns:
            {cb_key: state_value, ...}
        """
        if cb_key is not None:
            st = self._states.get(cb_key, CircuitBreakerState.CLOSED)
            return {cb_key: st.value}
        return {k: v.value for k, v in self._states.items()}

    @property
    def open_count(self) -> int:
        """当前处于 OPEN 状态的断路器数量。"""
        return sum(1 for s in self._states.values() if s is CircuitBreakerState.OPEN)

    # ------------------------------------------------------------------
    # 内部状态机
    # ------------------------------------------------------------------

    def _check_state(self, cb_key: str, model: str) -> CircuitBreakerState:
        """检查断路器状态（内部状态机）。

        CLOSED → OPEN：窗口内失败 >= 阈值
        OPEN → HALF_OPEN：超过冷却时间
        HALF_OPEN → CLOSED/OPEN：由 record_result 决定
        """
        now = time.time()
        state = self._states.get(cb_key, CircuitBreakerState.CLOSED)

        if state is CircuitBreakerState.OPEN:
            failures = self._failures.get(cb_key, [])
            if failures:
                last_fail = max(failures)
                if now - last_fail >= self._cooldown_s:
                    self._states[cb_key] = CircuitBreakerState.HALF_OPEN
                    self._log(
                        "INFO",
                        f"CircuitBreaker[{model}] OPEN→HALF_OPEN (冷却{self._cooldown_s}s后尝试恢复)",
                    )
                    return CircuitBreakerState.HALF_OPEN
            return CircuitBreakerState.OPEN

        if state is CircuitBreakerState.CLOSED:
            failures = self._failures.get(cb_key, [])
            recent = [t for t in failures if now - t <= self._failure_window_s]
            if len(recent) >= self._failure_threshold:
                self._states[cb_key] = CircuitBreakerState.OPEN
                self._log(
                    "WARN",
                    f"CircuitBreaker[{model}] CLOSED→OPEN ({len(recent)} failures in {self._failure_window_s}s)",
                )
                return CircuitBreakerState.OPEN
            return CircuitBreakerState.CLOSED

        return state

    def _log(self, level: str, message: str) -> None:
        """委托日志回调。"""
        self._log_fn(level, message)
