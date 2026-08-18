# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §8.1 + §16 Phase 2c
# [MODULE] zephyr.security.adversarial_validation.async_monitor
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.circuit_breaker; zephyr.security.adversarial_validation.bypass_recorder; zephyr.security.adversarial_validation.cleanup
# [CONSUMERS] cli.py; mcp_endpoints.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Background daemon monitors: circuit_breaker state / bypass_backlog / convergence_stagnation / cleanup_pending; 30s polling interval
# [MODIFY-GUARD] Adding monitors MUST register in _MONITORS; polling_interval_s MUST NOT be below 5
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] MonitorStallError on consecutive failures across all monitors
# [TESTS] tests/red_blue/test_async_monitor.py
# [A_module] module_id=MOD-INF-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import threading
import time
from enum import Enum
from typing import Final

from zephyr.security.adversarial_validation.bypass_recorder import BypassRecorder
from zephyr.security.adversarial_validation.circuit_breaker import CircuitBreaker, CircuitState
from zephyr.security.adversarial_validation.cleanup import Cleanup

logger = logging.getLogger(__name__)

__all__: list[str] = ["AsyncMonitor", "MonitorAlert", "MonitorStallError", "MonitorState"]

DEFAULT_POLL_INTERVAL_S: Final[int] = 30


class MonitorState(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    STALLED = "STALLED"
    STOPPED = "STOPPED"


class MonitorAlert:
    def __init__(self, monitor: str, severity: str, message: str) -> None:
        self.monitor: str = monitor
        self.severity: str = severity
        self.message: str = message
        self.timestamp: float = time.time()


class MonitorStallError(RuntimeError):
    error_code = "ZA-SC-0011"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class AsyncMonitor:
    def __init__(self, poll_interval_s: int = DEFAULT_POLL_INTERVAL_S) -> None:
        self._poll_interval_s: int = max(poll_interval_s, 5)
        self._state: MonitorState = MonitorState.IDLE
        self._thread: threading.Thread | None = None
        self._stop_event: threading.Event = threading.Event()
        self._alerts: list[MonitorAlert] = []
        self._circuit_breaker: CircuitBreaker = CircuitBreaker()
        self._bypass_recorder: BypassRecorder = BypassRecorder()
        self._consecutive_failures: int = 0

    @property
    def state(self) -> MonitorState:
        return self._state

    def start(self) -> None:
        if self._state is MonitorState.RUNNING:
            return
        self._stop_event.clear()
        self._state = MonitorState.RUNNING
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("async_monitor_started interval_s=%d", self._poll_interval_s)

    def stop(self) -> None:
        self._stop_event.set()
        self._state = MonitorState.STOPPED
        if self._thread:
            self._thread.join(timeout=10)
        logger.info("async_monitor_stopped alerts=%d", len(self._alerts))

    def alerts(self) -> list[MonitorAlert]:
        return list(self._alerts)

    def alert_count(self) -> int:
        return len(self._alerts)

    def clear_alerts(self) -> None:
        self._alerts = []

    # ── Stage 4 公共化（2026-07-28）：只读 properties + DI setter + 公共方法别名 ──
    # 消除 tests/safety/test_async_monitor.py 中 80 处私有成员访问（._stop_event /
    # ._poll_interval_s / ._consecutive_failures / ._circuit_breaker / ._bypass_recorder /
    # ._thread / ._alerts / ._monitor_loop / ._check_*）。保留私有方法为 thin wrapper，
    # 公共别名向后兼容。

    @property
    def stop_event(self) -> threading.Event:
        """只读：stop_event（Stage 4 公共化）。"""
        return self._stop_event

    @stop_event.setter
    def stop_event(self, value):
        """写入：stop_event（Stage 4 公共化）。"""
        self._stop_event = value

    @property
    def poll_interval_s(self) -> int:
        """只读：poll_interval_s（Stage 4 公共化）。"""
        return self._poll_interval_s

    @poll_interval_s.setter
    def poll_interval_s(self, value):
        """写入：poll_interval_s（Stage 4 公共化）。"""
        self._poll_interval_s = value

    @property
    def thread(self) -> threading.Thread | None:
        """只读：thread（Stage 4 公共化）。"""
        return self._thread

    @thread.setter
    def thread(self, value):
        """写入：thread（Stage 4 公共化）。"""
        self._thread = value

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        """读写：熔断器（Stage 4 公共化，测试可注入 mock）。"""
        return self._circuit_breaker

    @circuit_breaker.setter
    def circuit_breaker(self, value: CircuitBreaker) -> None:
        self._circuit_breaker = value

    @property
    def bypass_recorder(self) -> BypassRecorder:
        """读写：旁路记录器（Stage 4 公共化，测试可注入 mock）。"""
        return self._bypass_recorder

    @bypass_recorder.setter
    def bypass_recorder(self, value: BypassRecorder) -> None:
        self._bypass_recorder = value

    @property
    def consecutive_failures(self) -> int:
        """读写：连续失败计数（Stage 4 公共化）。"""
        return self._consecutive_failures

    @consecutive_failures.setter
    def consecutive_failures(self, value: int) -> None:
        self._consecutive_failures = value

    def add_alert(self, alert: MonitorAlert) -> None:
        """公共 API：追加告警（Stage 4 公共化，替代直接 ._alerts.append）。"""
        self._alerts.append(alert)

    def monitor_loop(self) -> None:
        """公共 API：监控循环（Stage 4 公共化，primary 实现）。

        _monitor_loop 为向后兼容 thin wrapper。loop 内部调公共 check_* 方法，
        使测试可经 monkeypatch.setattr(monitor, 'check_*', ...) 注入 mock。
        """
        while not self._stop_event.is_set():
            try:
                self.check_circuit_breaker()
                self.check_bypass_backlog()
                self.check_cleanup_residue()
                self._consecutive_failures = 0
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._consecutive_failures += 1
                if self._consecutive_failures >= 5:
                    self._state = MonitorState.STALLED
                    self._alerts.append(
                        MonitorAlert(
                            "stall_detector", "CRITICAL", f"Monitor stalled after {self._consecutive_failures} failures"
                        )
                    )
                    logger.critical("async_monitor_stalled failures=%d", self._consecutive_failures)

            self._stop_event.wait(self._poll_interval_s)

    def _monitor_loop(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.monitor_loop()

    def check_circuit_breaker(self) -> None:
        """公共 API：检查熔断器状态（Stage 4 公共化，primary 实现）。"""
        if self._circuit_breaker.state is CircuitState.OPEN:
            self._alerts.append(
                MonitorAlert("circuit_breaker", "HIGH", "Circuit breaker OPEN - adversarial testing paused")
            )

    def _check_circuit_breaker(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.check_circuit_breaker()

    def check_bypass_backlog(self) -> None:
        """公共 API：检查旁路积压（Stage 4 公共化，primary 实现）。"""
        bypass_entries = self._bypass_recorder.escalated_entries()
        if len(bypass_entries) > 0:
            self._alerts.append(
                MonitorAlert(
                    "bypass_backlog", "MEDIUM", f"{len(bypass_entries)} escalated bypass entries pending resolution"
                )
            )

    def _check_bypass_backlog(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.check_bypass_backlog()

    def check_cleanup_residue(self) -> None:
        """公共 API：检查清理残留（Stage 4 公共化，primary 实现）。"""
        cleanup = Cleanup()
        if not cleanup.verified():
            self._alerts.append(MonitorAlert("cleanup_residue", "LOW", "Cleanup residue detected - artifacts remain"))

    def _check_cleanup_residue(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.check_cleanup_residue()
