# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.cold_start_lock
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.immutable_core
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
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
ColdStartLock — 冷启动锁.

依据蓝图 MOD-INF-018 §3:
- 系统启动时处于锁定状态
- 必须通过配置加载、完整性验证、静态常量验证后才能解锁
- 防止系统在未完成自检前进入运行状态

Stage 4 重构 (2026-07-28):
- 集成 ImmutableCore 进行真实的完整性/静态常量验证
- 新增 owner_bypass() / status_dict() / verified_at / config_loaded
- 私有属性公共化: checks_passed / immutable_core / config_loaded
- get_cold_start_lock() 改为单例模式

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: immutable_core 参数
#   fields: 参数 immutable_core（无注解）
#   code: cold_start_lock.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ColdStartLock
#   name_en: ColdStartLock
#   intro: 冷启动锁 — 启动自检门控.
#   desc: 冷启动锁 — 启动自检门控. 初始状态为锁定，需依次通过: 1. load_config — 加载配置（需含有效 version 字段） 2. verify_integrity…；公共方法（定义序）: is_locke…
#   inputs: immutable_core
#   outputs: 返回值
# - id: A2
#   name_zh: ② get_cold_start_lock
#   name_en: get_cold_start_lock
#   intro: 获取 ColdStartLock 单例.
#   desc: 获取 ColdStartLock 单例.；源码 L241-L246
#   inputs: 无参数
#   outputs: ColdStartLock
# 层: 输出
# - id: O1
#   name_zh: ColdStartLock
#   name_en: ColdStartLock
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/agent_rbac/test_redteam_adversarial.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import time
from typing import Any

from zephyr.security.access_control.immutable_core import ImmutableCore

logger = logging.getLogger(__name__)

# 解锁所需通过的检查数
_REQUIRED_CHECKS = 3


class ColdStartLock:
    """冷启动锁 — 启动自检门控.

    初始状态为锁定，需依次通过:
    1. load_config — 加载配置（需含有效 version 字段）
    2. verify_integrity — 验证完整性（通过 ImmutableCore）
    3. verify_static_constants — 验证静态常量（通过 ImmutableCore）
    全部通过后 attempt_unlock 才能解锁。
    owner_bypass() 提供无条件解锁逃生通道。
    """

    def __init__(self, immutable_core: ImmutableCore | None = None) -> None:
        self._is_locked: bool = True
        self._checks_passed_count: int = 0
        self._config: dict[str, Any] = {}
        self._config_loaded: bool = False
        self._verified_at: float = 0.0
        self._immutable_core = immutable_core or ImmutableCore()

    # ── 公共属性 ──

    @property
    def is_locked(self) -> bool:
        """当前是否处于锁定状态."""
        return self._is_locked

    @property
    def verified_at(self) -> float:
        """解锁时的时间戳（Unix epoch），未解锁时为 0.0."""
        return self._verified_at

    # ── Stage 4 公共化属性 ──

    @property
    def checks_passed(self) -> int:
        """已通过的检查数（public API, Stage 4）."""
        return self._checks_passed_count

    @checks_passed.setter
    def checks_passed(self, value: int) -> None:
        """设置已通过的检查数（for testing, Stage 4）."""
        self._checks_passed_count = value

    @property
    def immutable_core(self) -> ImmutableCore:
        """关联的 ImmutableCore 实例（public API, Stage 4）."""
        return self._immutable_core

    @property
    def config_loaded(self) -> bool:
        """配置是否已加载（public API, Stage 4）."""
        return self._config_loaded

    @config_loaded.setter
    def config_loaded(self, value: bool) -> None:
        """设置配置加载状态（for testing, Stage 4）."""
        self._config_loaded = value

    # ── 公共方法 ──

    def load_config(self, config: dict[str, Any]) -> bool:
        """加载配置.

        Args:
            config: 配置字典，必须包含有效的 version 字段.

        Returns:
            True 如果配置有效且加载成功，否则 False.
        """
        if not config:
            logger.debug("ColdStartLock: load_config rejected empty config")
            return False
        version = config.get("version")
        if not version:
            logger.debug("ColdStartLock: load_config rejected config without version")
            return False
        self._config = dict(config)
        self._config_loaded = True
        self._checks_passed_count += 1
        logger.debug("ColdStartLock: config loaded (version=%s)", version)
        return True

    def verify_integrity(self) -> bool:
        """验证系统完整性（通过 ImmutableCore）.

        Returns:
            验证通过返回 True.
        """
        result = self._immutable_core.verify_immutable_core_integrity()
        if result.intact:
            self._checks_passed_count += 1
            logger.debug("ColdStartLock: integrity verified")
        else:
            logger.warning("ColdStartLock: integrity check FAILED: %s", result.detail)
        return result.intact

    def verify_static_constants(self) -> bool:
        """验证静态常量（通过 ImmutableCore）.

        Returns:
            验证通过返回 True.
        """
        result = self._immutable_core.verify_static_constants_integrity()
        if result.intact:
            self._checks_passed_count += 1
            logger.debug("ColdStartLock: static constants verified")
        else:
            logger.warning("ColdStartLock: static constants check FAILED: %s", result.detail)
        return result.intact

    def attempt_unlock(self) -> bool:
        """尝试解锁.

        Returns:
            所有检查通过且配置已加载则解锁并返回 True，否则返回 False.
        """
        if self._checks_passed_count >= _REQUIRED_CHECKS and self._config_loaded:
            self._is_locked = False
            self._verified_at = time.time()
            logger.info("ColdStartLock: UNLOCKED (checks=%d)", self._checks_passed_count)
            return True
        logger.warning(
            "ColdStartLock: unlock FAILED (checks=%d, required=%d, config_loaded=%s)",
            self._checks_passed_count,
            _REQUIRED_CHECKS,
            self._config_loaded,
        )
        return False

    def owner_bypass(self) -> None:
        """无条件解锁（owner 逃生通道）."""
        self._is_locked = False
        self._verified_at = time.time()
        logger.info("ColdStartLock: owner_bypass UNLOCKED")

    def status_dict(self) -> dict[str, Any]:
        """返回当前状态字典."""
        return {
            "locked": self._is_locked,
            "config_loaded": self._config_loaded,
            "checks_passed": self._checks_passed_count,
            "required_checks": _REQUIRED_CHECKS,
            "verified_at": self._verified_at if self._verified_at > 0 else None,
            "immutable_core_intact": self._immutable_core.verify_immutable_core_integrity().intact,
        }

    def reset(self) -> None:
        """重置锁到初始状态."""
        self._is_locked = True
        self._checks_passed_count = 0
        self._config = {}
        self._config_loaded = False
        self._verified_at = 0.0
        logger.debug("ColdStartLock: reset to initial state")


# ── 单例工厂 ──

_cold_start_lock_instance: ColdStartLock | None = None


def get_cold_start_lock() -> ColdStartLock:
    """获取 ColdStartLock 单例."""
    global _cold_start_lock_instance
    if _cold_start_lock_instance is None:
        _cold_start_lock_instance = ColdStartLock()
    return _cold_start_lock_instance


__all__ = [
    "ColdStartLock",
    "get_cold_start_lock",
]
