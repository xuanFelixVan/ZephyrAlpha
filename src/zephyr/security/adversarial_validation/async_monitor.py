# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §8.1 + §16 Phase 2c
# [MODULE] zephyr.security.adversarial_validation.async_monitor
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.circuit_breaker; zephyr.security.adversarial_validation.bypass_recorder; zephyr.security.adversarial_validation.cleanup
# [CONSUMERS] cli.py; mcp_endpoints.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Background daemon monitors: circuit_breaker state / bypass_backlog / convergence_stagnation / cleanup_pending; 30s polling interval
# [MODIFY-GUARD] Adding monitors MUST register in _MONITORS; polling_interval_s MUST NOT be below 5
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] MonitorStallError on consecutive failures across all monitors
# [TESTS] tests/red_blue/test_async_monitor.py
# [A_module] module_id=MOD-SEC_async_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging
import threading
import time
from enum import Enum

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

    def _monitor_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._check_circuit_breaker()
                self._check_bypass_backlog()
                self._check_cleanup_residue()
                self._consecutive_failures = 0
            except Exception:
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

    def _check_circuit_breaker(self) -> None:
        if self._circuit_breaker.state is CircuitState.OPEN:
            self._alerts.append(
                MonitorAlert("circuit_breaker", "HIGH", "Circuit breaker OPEN - adversarial testing paused")
            )

    def _check_bypass_backlog(self) -> None:
        bypass_entries = self._bypass_recorder.escalated_entries()
        if len(bypass_entries) > 0:
            self._alerts.append(
                MonitorAlert(
                    "bypass_backlog", "MEDIUM", f"{len(bypass_entries)} escalated bypass entries pending resolution"
                )
            )

    def _check_cleanup_residue(self) -> None:
        cleanup = Cleanup()
        if not cleanup.verified():
            self._alerts.append(MonitorAlert("cleanup_residue", "LOW", "Cleanup residue detected - artifacts remain"))
