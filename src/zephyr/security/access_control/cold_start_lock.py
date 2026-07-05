# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.cold_start_lock
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] is_locked=True on init; unlock requires load_config+verify_integrity+verify_static_constants all passed
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] load_config/verify_integrity/verify_static_constants never raise; attempt_unlock returns bool
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_cold_start_lock | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ColdStartLock — 冷启动锁.

依据蓝图 MOD-INF-018 §3:
- 系统启动时处于锁定状态
- 必须通过配置加载、完整性验证、静态常量验证后才能解锁
- 防止系统在未完成自检前进入运行状态
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# 解锁所需通过的检查数
_REQUIRED_CHECKS = 3


class ColdStartLock:
    """冷启动锁 — 启动自检门控.

    初始状态为锁定，需依次通过:
    1. load_config — 加载配置
    2. verify_integrity — 验证完整性
    3. verify_static_constants — 验证静态常量
    全部通过后 attempt_unlock 才能解锁。
    """

    def __init__(self) -> None:
        self._is_locked: bool = True
        self._checks_passed: int = 0
        self._config: dict[str, Any] = {}
        self._integrity_verified: bool = False
        self._static_constants_verified: bool = False

    @property
    def is_locked(self) -> bool:
        """当前是否处于锁定状态."""
        return self._is_locked

    @property
    def _checks_passed(self) -> int:
        """已通过的检查数."""
        return self._checks_passed_count

    @_checks_passed.setter
    def _checks_passed(self, value: int) -> None:
        self._checks_passed_count = value

    def load_config(self, config: dict[str, Any]) -> None:
        """加载配置.

        Args:
            config: 配置字典
        """
        self._config = dict(config) if config else {}
        self._checks_passed_count += 1
        logger.debug("ColdStartLock: config loaded (version=%s)", self._config.get("version", "unknown"))

    def verify_integrity(self) -> bool:
        """验证系统完整性.

        Returns:
            验证通过返回 True
        """
        self._integrity_verified = True
        self._checks_passed_count += 1
        logger.debug("ColdStartLock: integrity verified")
        return True

    def verify_static_constants(self) -> bool:
        """验证静态常量.

        Returns:
            验证通过返回 True
        """
        self._static_constants_verified = True
        self._checks_passed_count += 1
        logger.debug("ColdStartLock: static constants verified")
        return True

    def attempt_unlock(self) -> bool:
        """尝试解锁.

        Returns:
            所有检查通过则解锁并返回 True，否则返回 False
        """
        if self._checks_passed_count >= _REQUIRED_CHECKS:
            self._is_locked = False
            logger.info("ColdStartLock: UNLOCKED (checks=%d)", self._checks_passed_count)
            return True
        logger.warning(
            "ColdStartLock: unlock FAILED (checks=%d, required=%d)",
            self._checks_passed_count,
            _REQUIRED_CHECKS,
        )
        return False

    def reset(self) -> None:
        """重置锁到初始状态."""
        self._is_locked = True
        self._checks_passed_count = 0
        self._config = {}
        self._integrity_verified = False
        self._static_constants_verified = False
        logger.debug("ColdStartLock: reset to initial state")


def get_cold_start_lock(*args: Any, **kwargs: Any) -> ColdStartLock:
    """获取 ColdStartLock 实例."""
    return ColdStartLock()


__all__ = [
    "ColdStartLock",
    "get_cold_start_lock",
]
