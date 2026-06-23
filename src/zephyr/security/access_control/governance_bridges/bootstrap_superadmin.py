# [A_module] module_id=MOD-SEC_bootstrap_superadmin_bridge | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §bootstrap_superadmin
# [MODULE] zephyr.security.access_control.governance_bridges.bootstrap_superadmin
# [INVARIANTS] bootstrap is idempotent; superadmin account created once; capabilities never include destructive ops
# [MODIFY-GUARD] Owner approval required; changes require blueprint update
# [CONSUMERS] genesis_bootstrap._bootstrap_superadmin(); auto_runtime_core.boot()
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] bootstrap() never raises; returns dict with bootstrapped flag and error detail
# [TESTS] tests/agent_rbac/test_rbac_auto_lifecycle.py
"""BootstrapSuperadminBridge — Superadmin 账户启动桥接.

依据蓝图 MOD-INF-018 §bootstrap_superadmin:
- 创建superadmin账户（唯一特权账户）
- 初始化superadmin角色和权限
- 桥接 access_control/bootstrap_superadmin.py 到 genesis_bootstrap
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class BootstrapSuperadminBridge:
    """Superadmin 账户启动桥接器.

    在RBAC系统启动时创建superadmin账户，
    确保系统至少有一个特权账户可用于管理。

    幂等性: 重复调用不会重复创建账户。
    """

    _bootstrapped: bool = False
    _account_id: str = ""
    _bootstrapped_at: float = 0.0

    def __init__(self) -> None:
        self._reset_if_needed()

    def _reset_if_needed(self) -> None:
        if not hasattr(self.__class__, "_bootstrapped"):
            self.__class__._bootstrapped = False
        if not hasattr(self.__class__, "_account_id"):
            self.__class__._account_id = ""
        if not hasattr(self.__class__, "_bootstrapped_at"):
            self.__class__._bootstrapped_at = 0.0

    @property
    def is_bootstrapped(self) -> bool:
        """是否已启动."""
        return self.__class__._bootstrapped

    @property
    def account_id(self) -> str:
        """superadmin账户ID."""
        return self.__class__._account_id

    def bootstrap(self) -> dict[str, Any]:
        """创建superadmin账户.

        Returns:
            dict包含:
            - bootstrapped: bool — 是否成功
            - account: str — 账户ID
            - roles: list — 角色列表
            - capabilities: list — 权限列表
            - error: str — 错误信息（失败时）
        """
        if self.is_bootstrapped:
            logger.info("BootstrapSuperadminBridge: already bootstrapped, skipping")
            return {
                "bootstrapped": True,
                "account": self.__class__._account_id,
                "roles": ["superadmin"],
                "capabilities": ["read", "write", "execute"],
                "skipped": True,
            }

        try:
            from zephyr.security.access_control.bootstrap_superadmin import (
                SUPERADMIN_ACCOUNT,
                SUPERADMIN_CAPABILITIES,
                SUPERADMIN_ROLES,
                BootstrapSuperadmin,
            )

            superadmin = BootstrapSuperadmin()
            check_result = superadmin.check("read", "/system")
            if not check_result.get("granted"):
                return {
                    "bootstrapped": False,
                    "error": "superadmin check failed",
                }

            bootstrap_result = superadmin.bootstrap()
            if not bootstrap_result.get("bootstrapped"):
                return {
                    "bootstrapped": False,
                    "error": "superadmin.bootstrap() returned False",
                }

            self.__class__._bootstrapped = True
            self.__class__._account_id = SUPERADMIN_ACCOUNT
            self.__class__._bootstrapped_at = time.time()

            logger.info(
                "BootstrapSuperadminBridge: superadmin '%s' bootstrapped successfully",
                SUPERADMIN_ACCOUNT,
            )

            return {
                "bootstrapped": True,
                "account": SUPERADMIN_ACCOUNT,
                "roles": list(SUPERADMIN_ROLES),
                "capabilities": list(SUPERADMIN_CAPABILITIES),
                "bootstrapped_at": self.__class__._bootstrapped_at,
            }

        except ImportError as e:
            logger.error("BootstrapSuperadminBridge: import failed: %s", e)
            return {
                "bootstrapped": False,
                "error": f"import failed: {e}",
            }
        except Exception as e:
            logger.error("BootstrapSuperadminBridge: bootstrap failed: %s", e)
            return {
                "bootstrapped": False,
                "error": f"bootstrap exception: {e}",
            }

    def verify(self) -> dict[str, Any]:
        """验证superadmin账户是否有效.

        Returns:
            dict包含:
            - valid: bool — 是否有效
            - account: str — 账户ID
            - error: str — 错误信息
        """
        if not self.is_bootstrapped:
            return {"valid": False, "error": "not bootstrapped"}

        try:
            from zephyr.security.access_control.bootstrap_superadmin import (
                SUPERADMIN_ACCOUNT,
                BootstrapSuperadmin,
            )

            superadmin = BootstrapSuperadmin()
            check_result = superadmin.check("read", "/system")
            return {
                "valid": check_result.get("granted", False),
                "account": SUPERADMIN_ACCOUNT,
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def shutdown(self) -> dict[str, Any]:
        """关闭superadmin桥接 — 清理状态."""
        self.__class__._bootstrapped = False
        self.__class__._account_id = ""
        self.__class__._bootstrapped_at = 0.0
        logger.info("BootstrapSuperadminBridge: shutdown completed")
        return {"shutdown": True}


def get_bootstrap_superadmin_bridge() -> BootstrapSuperadminBridge:
    """获取BootstrapSuperadminBridge实例."""
    return BootstrapSuperadminBridge()


__all__ = [
    "BootstrapSuperadminBridge",
    "get_bootstrap_superadmin_bridge",
]
