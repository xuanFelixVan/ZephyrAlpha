from __future__ import annotations

from enum import Enum
from typing import Optional


class OfflineMode(str, Enum):
    AUTO = "AUTO"
    SEMIAUTO_MANUAL = "SEMIAUTO_MANUAL"
    ONLINE = "ONLINE"


class AutonomyState:
    def __init__(self) -> None:
        self._mode: OfflineMode = OfflineMode.ONLINE
        self._cache: list[str] = []

    @property
    def mode(self) -> OfflineMode:
        return self._mode

    def transition(self, connected: bool) -> OfflineMode:
        if connected:
            self._mode = OfflineMode.ONLINE
            self._cache.clear()
        elif self._mode == OfflineMode.ONLINE:
            self._mode = OfflineMode.AUTO
        return self._mode

    def cache_command(self, cmd: str) -> None:
        self._cache.append(cmd)

    def has_cached_commands(self) -> bool:
        return len(self._cache) > 0
