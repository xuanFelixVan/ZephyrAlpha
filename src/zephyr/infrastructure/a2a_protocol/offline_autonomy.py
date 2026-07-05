# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.offline_autonomy
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.__init__
# [CONSUMERS] MOD-INF-027;MOD-INF-018;MOD-INF-022
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Agent间通信;冲突解决;四级委托约束
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md;src/zephyr/infrastructure/runtime_integration/a2a_protocol/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CommunicationError;ConflictError;DelegationError
# [TESTS] tests/test_a2a_protocol/
# [A_module] module_id=MOD-INF_offline_autonomy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
