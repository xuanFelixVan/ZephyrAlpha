# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.io.cache_invalidation
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_cache_invalidation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""cache_invalidation.py — 缓存一致性 (DD113, TASK-020)"""

from dataclasses import dataclass
from datetime import UTC, datetime

UTC = UTC


@dataclass
class CacheVersion:
    key: str
    version: int
    invalidated_at: str


class CacheInvalidationManager:
    """Mem/Redis 缓存 + event-driven KE update → cache invalidation (DD113)."""

    def __init__(self) -> None:
        self._versions: dict[str, CacheVersion] = {}

    def set_version(self, key: str, version: int) -> CacheVersion:
        cv = CacheVersion(key=key, version=version, invalidated_at=datetime.now(UTC).isoformat())
        self._versions[key] = cv
        return cv

    def check_staleness(self, key: str, client_version: int) -> bool:
        cv = self._versions.get(key)
        return cv is not None and cv.version > client_version
