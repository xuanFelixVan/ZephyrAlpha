"""kill_switch.py — 安全熔断 (DD110, TASK-019)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class FuseState:
    on: bool
    trigger_reason: str
    manual_reset_needed: bool


class KillSwitch:
    """per-session_err>threshold → fuse off. needs manual reset (DD110)."""
    def __init__(self, threshold: int = 5) -> None:
        self._threshold = threshold
        self._error_count = 0
        self._fuse_on = False

    def record_error(self, reason: str = "") -> FuseState:
        self._error_count += 1
        if self._error_count >= self._threshold:
            self._fuse_on = True
        return FuseState(on=self._fuse_on, trigger_reason=reason, manual_reset_needed=True)

    def reset(self) -> None:
        self._error_count = 0
        self._fuse_on = False
