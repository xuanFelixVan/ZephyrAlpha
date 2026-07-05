# [BLUEPRINT] SRC-072 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.resilience_governance.offline_autonomy
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.resilience_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_offline_autonomy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from enum import Enum


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
        elif self._mode is OfflineMode.ONLINE:
            self._mode = OfflineMode.AUTO
        return self._mode

    def cache_command(self, cmd: str) -> None:
        self._cache.append(cmd)

    def has_cached_commands(self) -> bool:
        return len(self._cache) > 0
