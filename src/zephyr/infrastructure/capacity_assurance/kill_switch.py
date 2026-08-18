# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.kill_switch
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS] zephyr.autonomy_core.context.context_pipeline_auto
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] err_count>threshold -> fuse off; needs manual reset (DD110)
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FuseState
# [TESTS] tests/context/test_context_pipeline_auto.py
# [A_module] module_id=MOD-INF-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# SRC-0041 (P3 迁移恢复, 2026-07-02): 文件从 autonomy_core/kill_switch.py 迁移至
#   infrastructure/capacity_assurance/kill_switch.py（blueprint actual_disk_path 真源）。
#   原始 autonomy_core/kill_switch.py 的 SRC-0041 注释提到 shared/kill_switch.py 为
#   统一 SSoT 导出，但该文件当前不存在；本文件保留独立实现，待 future review 决定是否合并。
"""kill_switch.py -- safety circuit breaker (DD110, TASK-019).

Extends the basic per-session error-count fuse with:
  - `auto_kill_threshold`: batch error threshold for `check_errors_and_kill`.
  - `register_cleanup` / `trigger_shutdown`: resource cleanup callbacks that
    fire exactly once when the fuse trips (exceptions in one callback do not
    block subsequent callbacks).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class FuseState:
    on: bool
    trigger_reason: str
    manual_reset_needed: bool


# class-name-alias: capacity-assurance per-session error-count fuse (DD110); name shadows canonical zephyr.security.access_control.kill_switch.KillSwitch (MOD-SEC_kill_switch) but semantics differ (err threshold vs system-level breaker). Distinct domain (D_INFRA_RUNTIME) — not a re-export.
class KillSwitch:
    """per-session err>threshold -> fuse off. needs manual reset (DD110).

    Extended with batch error checking and cleanup callbacks:
      - `check_errors_and_kill(errors)`: returns True if `len(errors) >=
        auto_kill_threshold` (trips the fuse). `auto_kill_threshold=0` disables.
      - `register_cleanup(callback)` / `trigger_shutdown()`: callbacks fire
        once when `trigger_shutdown` is called; exceptions are logged but do
        not block subsequent callbacks. Callback list is cleared after firing.
    """

    def __init__(
        self,
        threshold: int = 5,
        auto_kill_threshold: int = 0,
    ) -> None:
        self._threshold = threshold
        self._auto_kill_threshold = auto_kill_threshold
        self._error_count = 0
        self._fuse_on = False
        self._cleanup_callbacks: list[Callable[[], None]] = []

    @property
    def fuse_on(self) -> bool:
        """Whether the kill switch fuse is on (public API)."""
        return self._fuse_on

    @fuse_on.setter
    def fuse_on(self, value: bool) -> None:
        self._fuse_on = value

    @property
    def error_count(self) -> int:
        """Current error count (public API)."""
        return self._error_count

    @property
    def threshold(self) -> int:
        """Error threshold for fuse activation (public API)."""
        return self._threshold

    @threshold.setter
    def threshold(self, value: int) -> None:
        self._threshold = value

    @property
    def cleanup_callbacks(self) -> list[Callable[[], None]]:
        """Registered cleanup callbacks (public API)."""
        return self._cleanup_callbacks

    def record_error(self, reason: str = "") -> FuseState:
        self._error_count += 1
        if self._error_count >= self._threshold:
            self._fuse_on = True
        return FuseState(on=self._fuse_on, trigger_reason=reason, manual_reset_needed=True)

    def check_errors_and_kill(self, errors: list[str]) -> bool:
        """Batch error check — trip the fuse if error count meets auto_kill_threshold.

        Returns True if the fuse was tripped by this call, False otherwise.
        Disabled when `auto_kill_threshold <= 0`.
        """
        if self._auto_kill_threshold <= 0:
            return False
        if len(errors) >= self._auto_kill_threshold:
            self._fuse_on = True
            logger.warning(
                "KillSwitch auto-kill triggered: %d errors >= threshold %d",
                len(errors),
                self._auto_kill_threshold,
            )
            return True
        return False

    def register_cleanup(self, callback: Callable[[], None]) -> None:
        """Register a cleanup callback to fire on `trigger_shutdown`."""
        self._cleanup_callbacks.append(callback)

    def trigger_shutdown(self) -> None:
        """Trip the fuse and fire all registered cleanup callbacks.

        Callback exceptions are logged but do not block subsequent callbacks.
        The callback list is cleared after firing (one-shot semantics).
        """
        self._fuse_on = True
        callbacks = self._cleanup_callbacks
        self._cleanup_callbacks = []
        for cb in callbacks:
            try:
                cb()
            except Exception:  # noqa: BLE001 — one callback failure must not block others
                logger.warning("KillSwitch cleanup callback raised", exc_info=True)

    def reset(self) -> None:
        self._error_count = 0
        self._fuse_on = False
