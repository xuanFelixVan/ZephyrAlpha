"""权限模式管理器——scoped_run/最小权限/请求审批/hold整理."""
from __future__ import annotations

from enum import Enum
from typing import Any


class PermMode(str, Enum):
    SCOPED = "SCOPED"
    MINIMAL = "MINIMAL"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    HOLD = "HOLD"
    FULL = "FULL"


class PermissionModeManager:
    _MODE_ORDER: list[PermMode] = [PermMode.HOLD, PermMode.MINIMAL, PermMode.SCOPED, PermMode.APPROVAL_REQUIRED, PermMode.FULL]

    def __init__(self) -> None:
        self._current: PermMode = PermMode.MINIMAL
        self._history: list[dict[str, Any]] = []

    def transition(self, new_mode: PermMode, agent_id: str = "") -> dict[str, Any]:
        old = self._current
        self._current = new_mode
        entry = {"from": old.value, "to": new_mode.value, "agent_id": agent_id}
        self._history.append(entry)
        return {"transitioned": True, **entry}

    def scoped_run(self, agent_id: str, permissions: list[str]) -> dict[str, Any]:
        self.transition(PermMode.SCOPED, agent_id)
        return {"mode": "SCOPED", "agent_id": agent_id, "permissions": permissions}

    @property
    def mode(self) -> str:
        return self._current.value
