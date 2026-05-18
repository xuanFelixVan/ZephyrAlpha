# [BLUEPRINT] MOD-INF-025 | docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md
# [MODULE] zephyr.l01_infrastructure.a2a_protocol
# [INVARIANTS] Agent间通信;冲突解决;四级委托约束
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md;src/zephyr/l01_infrastructure/a2a_protocol/__init__.py
# [CONSUMERS] MOD-INF-027;MOD-INF-018;MOD-INF-022
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CommunicationError;ConflictError;DelegationError
# [TESTS] tests/test_a2a_protocol/

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
