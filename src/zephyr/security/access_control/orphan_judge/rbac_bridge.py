# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §6.3
# [MODULE] zephyr.security.access_control.orphan_judge.rbac_bridge
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.guards.permission_guard
# [CONSUMERS] orphan-judge.judge.OrphanJudge(DELETE动作前)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 不实现权限逻辑; 仅桥接PermissionGuard.check()
# [MODIFY-GUARD] PermissionGuard API变更时同步此桥接
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败默认DENY
# [TESTS] tests/orphan-judge/test_rbac_bridge.py
# [A_module] module_id=MOD-SEC_rbac_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["RbacBridge"]


class RbacBridge:
    def __init__(self) -> None:
        self._guard = None
        self._available = False
        try:
            from zephyr.security.access_control.guards.permission_guard import PermissionGuard

            self._guard = PermissionGuard()
            self._available = True
        except ImportError:
            logger.warning("PermissionGuard not available")
        except Exception as exc:
            logger.warning("PermissionGuard init failed: %s", exc)

    def check_delete_permission(self, file_path: str) -> dict[str, Any]:
        if not self._available or self._guard is None:
            return {"allowed": False, "reason": "bridge_unavailable", "status": "denied"}
        try:
            result = self._guard.check(file_path, "DELETE")
            allowed = getattr(result, "allowed", False)
            return {
                "allowed": allowed,
                "status": "allowed" if allowed else "denied",
                "detail": str(result),
            }
        except Exception as exc:
            logger.error("RbacBridge.check_delete_permission failed: %s", exc)
            return {"allowed": False, "reason": str(exc), "status": "bridge_error"}

    def is_available(self) -> bool:
        return self._available
