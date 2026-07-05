# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §bootstrap_superadmin
# [MODULE] zephyr.security.access_control.bootstrap_superadmin
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] genesis_bootstrap._phase_bootstrap_superadmin(); genesis_bootstrap.shutdown()
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] superadmin account created once; capabilities never include destructive ops; bootstrap is idempotent
# [MODIFY-GUARD] Owner approval required; changes require blueprint update
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] check() never raises; returns dict with granted flag; bootstrap() never raises
# [TESTS] tests/agent_rbac/test_rbac_auto_lifecycle.py
# [A_module] module_id=MOD-SEC_bootstrap_superadmin | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""BootstrapSuperadmin — Superadmin 账户启动器.

依据蓝图 MOD-INF-018 §bootstrap_superadmin:
- 创建superadmin账户（唯一特权账户）
- 初始化superadmin角色和权限
- 幂等性: 重复调用不会重复创建账户
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

SUPERADMIN_ACCOUNT = "superadmin"
SUPERADMIN_ROLES = ["superadmin", "admin"]
SUPERADMIN_CAPABILITIES = ["read", "write", "execute", "admin", "manage"]


class BootstrapSuperadmin:
    """Superadmin 账户启动器.

    在RBAC系统启动时创建superadmin账户，
    确保系统至少有一个特权账户可用于管理。

    幂等性: 重复调用不会重复创建账户。
    """

    _bootstrapped: bool = False
    _account: str = ""
    _bootstrapped_at: float = 0.0

    def __init__(self) -> None:
        self._reset_if_needed()

    def _reset_if_needed(self) -> None:
        if not hasattr(self.__class__, "_bootstrapped"):
            self.__class__._bootstrapped = False
        if not hasattr(self.__class__, "_account"):
            self.__class__._account = ""
        if not hasattr(self.__class__, "_bootstrapped_at"):
            self.__class__._bootstrapped_at = 0.0

    @property
    def is_bootstrapped(self) -> bool:
        """是否已启动."""
        return self.__class__._bootstrapped

    @property
    def account(self) -> str:
        """superadmin账户ID."""
        return self.__class__._account

    def check(self, operation: str, target: str) -> dict[str, Any]:
        """检查superadmin权限.

        Args:
            operation: 操作类型
            target: 目标路径

        Returns:
            dict包含 granted: bool
        """
        return {
            "granted": True,
            "account": SUPERADMIN_ACCOUNT,
            "operation": operation,
            "target": target,
        }

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
            logger.info("BootstrapSuperadmin: already bootstrapped, skipping")
            return {
                "bootstrapped": True,
                "account": self.__class__._account,
                "roles": list(SUPERADMIN_ROLES),
                "capabilities": list(SUPERADMIN_CAPABILITIES),
                "skipped": True,
            }

        self.__class__._bootstrapped = True
        self.__class__._account = SUPERADMIN_ACCOUNT
        self.__class__._bootstrapped_at = time.time()

        logger.info("BootstrapSuperadmin: superadmin '%s' bootstrapped", SUPERADMIN_ACCOUNT)

        return {
            "bootstrapped": True,
            "account": SUPERADMIN_ACCOUNT,
            "roles": list(SUPERADMIN_ROLES),
            "capabilities": list(SUPERADMIN_CAPABILITIES),
            "bootstrapped_at": self.__class__._bootstrapped_at,
        }

    def verify(self) -> dict[str, Any]:
        """验证superadmin账户是否有效.

        Returns:
            dict包含 valid: bool
        """
        if not self.is_bootstrapped:
            return {"valid": False, "error": "not bootstrapped"}
        return {"valid": True, "account": SUPERADMIN_ACCOUNT}

    def shutdown(self) -> dict[str, Any]:
        """关闭superadmin — 清理状态."""
        self.__class__._bootstrapped = False
        self.__class__._account = ""
        self.__class__._bootstrapped_at = 0.0
        logger.info("BootstrapSuperadmin: shutdown completed")
        return {"shutdown": True}


class BootstrapSuperadminBridge:
    """Superadmin 账户启动桥接器.

    在RBAC系统启动时创建superadmin账户，
    确保系统至少有一个特权账户可用于管理。

    幂等性: 重复调用不会重复创建账户。

    ARCH-035: 合并自 governance_bridges/bootstrap_superadmin.py（单文件子目录违反向内收原则①）。
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
    "SUPERADMIN_ACCOUNT",
    "SUPERADMIN_CAPABILITIES",
    "SUPERADMIN_ROLES",
    "BootstrapSuperadmin",
    "BootstrapSuperadminBridge",
    "get_bootstrap_superadmin_bridge",
]
