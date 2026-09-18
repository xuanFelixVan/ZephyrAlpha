# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.source_circuit_breaker
# [DOMAIN] D_DATA
# [DEPENDENCIES] none（stdlib only）
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] per-source 熔断状态机 CLOSED→OPEN→HALF_OPEN→CLOSED；线程安全；时钟可注入；纯内存不持久化
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 全部方法不抛异常（被动组件不得阻断调度主链路）
# [TESTS] tests/zephyr/data/test_source_circuit_breaker.py
# [A_module] module_id=MOD-L00-004-CB | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
per-source 自动熔断器（64号 Q17，P1，2026-08-20 AI-NIGHT-001 施工）。

裁定真源：64号 §16.2 Q17——scheduler 层对连续失败 N 次的数据源熔断 M 分钟，
滑窗错误率超阈值同样触发；冷却后进半开态放行单探针，探针成功恢复、失败再熔断。
与手动 `integrator pause <source>`（policy.enabled）互补不替代：手动熔断管人工处置，
本模块管运行时自动止血（如 akshare 某接口突然 blocked 时避免整日任务雪崩重试）。

纯内存实现：进程重启即复位（重启后首轮任务本身即探针），不引入持久化复杂度。

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/source_circuit_breaker.yaml
"""

from __future__ import annotations

import enum
import logging
import threading
import time
from collections import deque
from collections.abc import Callable

# 默认参数（64号 Q17"连续失败 N 次熔断 M 分钟"；构造时可覆盖）
DEFAULT_FAILURE_THRESHOLD = 5  # N：连续失败次数
DEFAULT_COOLDOWN_SECONDS = 1800.0  # M：熔断冷却 30 分钟
DEFAULT_WINDOW_SIZE = 20  # 滑窗样本数
DEFAULT_ERROR_RATE = 0.6  # 滑窗错误率阈值
DEFAULT_MIN_SAMPLES = 10  # 错误率判定的最小样本量（防小样本误判）

log = logging.getLogger(__name__)


class CircuitState(enum.Enum):
    """熔断器三态。"""

    CLOSED = "closed"  # 正常放行
    OPEN = "open"  # 熔断中（冷却期内拒绝）
    HALF_OPEN = "half_open"  # 半开（放行单探针试探）


class SourceCircuitBreaker:
    """单数据源熔断器（线程安全，时钟可注入便于测试）。"""

    def __init__(
        self,
        source: str,
        *,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        cooldown_seconds: float = DEFAULT_COOLDOWN_SECONDS,
        window_size: int = DEFAULT_WINDOW_SIZE,
        error_rate_threshold: float = DEFAULT_ERROR_RATE,
        min_samples: int = DEFAULT_MIN_SAMPLES,
        clock: Callable[[], float] = time.monotonic,
        on_trip: Callable[[str, str], None] | None = None,
    ) -> None:
        self.source = source
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.error_rate_threshold = error_rate_threshold
        self.min_samples = min_samples
        self._clock = clock
        self._on_trip = on_trip
        self._lock = threading.Lock()
        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._window: deque[bool] = deque(maxlen=window_size)  # True=成功 False=失败
        self._opened_at = 0.0
        #: 跳闸升级回调失败可观测面（BRK-049）：失败计数 + 最近一次真实错误。
        #: 回调通常是"发告警/写审计/通知调度器"，吞掉即等于"熔断了却没人知道"。
        self.trip_callback_failures = 0
        self.last_trip_callback_error: str | None = None
        self._probe_in_flight = False
        self._probe_started_at = 0.0

    @property
    def state(self) -> CircuitState:
        with self._lock:
            return self._state

    def allow_request(self) -> bool:
        """是否放行对该源的调用（OPEN 冷却到点自动转 HALF_OPEN 放行单探针）。"""
        with self._lock:
            now = self._clock()
            if self._state is CircuitState.CLOSED:
                return True
            if self._state is CircuitState.OPEN:
                if now - self._opened_at >= self.cooldown_seconds:
                    self._state = CircuitState.HALF_OPEN
                    self._probe_in_flight = True
                    self._probe_started_at = now
                    return True
                return False
            # HALF_OPEN：单探针在飞则拒绝；探针超时（进程异常未回报）允许补探
            if self._probe_in_flight:
                if now - self._probe_started_at >= self.cooldown_seconds:
                    self._probe_started_at = now  # 补探
                    return True
                return False
            self._probe_in_flight = True
            self._probe_started_at = now
            return True

    def record_success(self) -> None:
        """记录一次成功调用（HALF_OPEN 探针成功→CLOSED 复位）。"""
        with self._lock:
            self._window.append(True)
            self._consecutive_failures = 0
            if self._state is CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._probe_in_flight = False

    def record_failure(self) -> None:
        """记录一次失败调用（达阈值→OPEN；HALF_OPEN 探针失败→再 OPEN 重计冷却）。"""
        with self._lock:
            self._window.append(False)
            self._consecutive_failures += 1
            if self._state is CircuitState.HALF_OPEN:
                self._probe_in_flight = False
                self._trip("半开探针失败")
                return
            if self._state is CircuitState.CLOSED:
                if self._consecutive_failures >= self.failure_threshold:
                    self._trip(f"连续失败 {self._consecutive_failures} 次")
                elif self._error_rate_tripped():
                    self._trip(f"滑窗错误率超阈值（{self.error_rate_threshold:.0%}）")

    # ---- 内部 ----

    def _error_rate_tripped(self) -> bool:
        if len(self._window) < self.min_samples:
            return False
        failures = sum(1 for ok in self._window if not ok)
        return failures / len(self._window) >= self.error_rate_threshold

    def _trip(self, reason: str) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = self._clock()
        if self._on_trip is not None:
            try:
                self._on_trip(self.source, reason)
            except Exception as exc:  # noqa: BLE001 — 回调异常不得回滚状态机
                # BRK-049 收口：状态保持 OPEN 是正确的降级方向（回调故障不能
                # 让熔断器"复原放行"），但**零痕迹**会把"升级链已断"这个事实
                # 一起吞掉。故：不回滚状态、不抛给调用方，但必须计数+留痕，
                # 使外部可机械判"熔断器在跑而升级通道是死的"。
                # 日志不预设失败类别（类型缺陷/IO/锁竞争一律以真实类型名呈现）。
                self.trip_callback_failures += 1
                self.last_trip_callback_error = f"{type(exc).__name__}: {exc}"
                log.error(
                    "熔断跳闸升级回调失败 source=%s reason=%s %s: %s",
                    self.source,
                    reason,
                    type(exc).__name__,
                    exc,
                    exc_info=True,
                )


class CircuitBreakerRegistry:
    """per-source 熔断器注册表（懒创建，线程安全）。"""

    def __init__(
        self,
        *,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        cooldown_seconds: float = DEFAULT_COOLDOWN_SECONDS,
        window_size: int = DEFAULT_WINDOW_SIZE,
        error_rate_threshold: float = DEFAULT_ERROR_RATE,
        min_samples: int = DEFAULT_MIN_SAMPLES,
        clock: Callable[[], float] = time.monotonic,
        on_trip: Callable[[str, str], None] | None = None,
    ) -> None:
        self._defaults = {
            "failure_threshold": failure_threshold,
            "cooldown_seconds": cooldown_seconds,
            "window_size": window_size,
            "error_rate_threshold": error_rate_threshold,
            "min_samples": min_samples,
            "clock": clock,
            "on_trip": on_trip,
        }
        self._lock = threading.Lock()
        self._breakers: dict[str, SourceCircuitBreaker] = {}

    def get(self, source: str) -> SourceCircuitBreaker:
        with self._lock:
            breaker = self._breakers.get(source)
            if breaker is None:
                breaker = SourceCircuitBreaker(source, **self._defaults)
                self._breakers[source] = breaker
            return breaker

    def allow_request(self, source: str) -> bool:
        return self.get(source).allow_request()

    def record_success(self, source: str) -> None:
        self.get(source).record_success()

    def record_failure(self, source: str) -> None:
        self.get(source).record_failure()

    def state(self, source: str) -> CircuitState:
        return self.get(source).state

    def snapshot(self) -> dict[str, str]:
        """全源熔断状态快照（供 /status 端点或巡检）。"""
        with self._lock:
            return {src: b.state.value for src, b in self._breakers.items()}
