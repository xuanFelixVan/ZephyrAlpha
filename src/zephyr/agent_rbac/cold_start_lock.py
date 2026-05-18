# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.cold_start_lock

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Cold Start Lock — 系统启动时全局拒绝，直到权限配置加载校验通过

MOD-INF-018 §2.16  D-018-21

lock_until_verify True 要求通过校验才能解锁，不接受手动跳过（除非 Owner bypass）。
"""

import time
from typing import Optional

from zephyr.agent_rbac.immutable_core import ImmutableCore


class ColdStartLock:
    """系统冷启动锁——配置加载校验通过后才能解锁"""

    def __init__(self, immutable_core: Optional[ImmutableCore] = None) -> None:
        self._immutable_core = immutable_core or ImmutableCore()
        self._locked: bool = True
        self._verified_at: float = 0.0
        self._config_loaded: bool = False
        self._checks_passed: int = 0
        self._required_checks: int = 3

    @property
    def is_locked(self) -> bool:
        return self._locked

    @property
    def verified_at(self) -> float:
        return self._verified_at

    def load_config(self, config: dict) -> bool:
        if config.get("version"):
            self._config_loaded = True
            self._checks_passed += 1
            return True
        return False

    def verify_integrity(self) -> bool:
        result = self._immutable_core.verify_immutable_core_integrity()
        if result.intact:
            self._checks_passed += 1
        return result.intact

    def verify_static_constants(self) -> bool:
        result = self._immutable_core.verify_static_constants_integrity()
        if result.intact:
            self._checks_passed += 1
        return result.intact

    def attempt_unlock(self) -> bool:
        if self._checks_passed >= self._required_checks and self._config_loaded:
            self._locked = False
            self._verified_at = time.time()
            return True
        return False

    def owner_bypass(self) -> None:
        self._locked = False
        self._verified_at = time.time()

    def status_dict(self) -> dict:
        return {
            "locked": self._locked,
            "config_loaded": self._config_loaded,
            "checks_passed": self._checks_passed,
            "required_checks": self._required_checks,
            "verified_at": self._verified_at if self._verified_at > 0 else None,
            "immutable_core_intact": self._immutable_core.verify_immutable_core_integrity().intact,
        }


_COLD_START_LOCK: Optional[ColdStartLock] = None


def get_cold_start_lock() -> ColdStartLock:
    global _COLD_START_LOCK
    if _COLD_START_LOCK is None:
        _COLD_START_LOCK = ColdStartLock()
    return _COLD_START_LOCK
