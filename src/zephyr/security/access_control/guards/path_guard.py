# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.guards.path_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] FORBIDDEN_PATHS never writable; CRITICAL_FILES always blocked for write
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check() never raises; returns dict with allowed/reason/path
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_path_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""PathGuard — 路径守卫.

依据蓝图 MOD-INF-018 §3:
- 检查路径是否在允许/禁止范围内
- 关键文件写操作被阻止
"""

from __future__ import annotations


ALLOWED_ROOTS = [
    "src/",
    "docs/",
    "scripts/",
    "tests/",
    "config/",
]

FORBIDDEN_PATHS = [
    ".git/",
    ".ailocks/",
    "data/databases/",
    ".env",
    "credentials",
    "/etc/",
    "/root/",
    "/var/",
    "/proc/",
    "/sys/",
    "/dev/",
    "/boot/",
    "/usr/",
    "/sbin/",
    "/bin/",
    "/lib/",
    "C:/Windows/",
    "C:/Program Files/",
]

CRITICAL_FILES = [
    ".git/config",
    "config/rbac_roles.yaml",
    ".ailocks/registry.json",
    ".ailocks/registry.json.lock",
    "data/databases/governance.db",
]


def _normalize_path(path: str) -> str:
    """规范化路径 — 统一为正斜杠，去除前导 ./"""
    normalized = str(path).replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


class PathGuard:
    """路径守卫.

    检查路径是否在允许/禁止范围内，关键文件写操作被阻止。
    """

    def check(self, path: str, operation: str = "read") -> dict:
        """检查路径权限.

        Args:
            path: 文件路径
            operation: 操作类型（read/write）

        Returns:
            dict: {"allowed": bool, "reason": str, "path": str}
        """
        path_str = str(path)
        normalized = _normalize_path(path_str)

        # 关键文件 — 写操作永远阻止
        for critical in CRITICAL_FILES:
            if normalized == critical or normalized.endswith("/" + critical):
                if operation == "write":
                    return {
                        "allowed": False,
                        "reason": f"critical file write blocked: {critical}",
                        "path": path_str,
                    }

        # 禁止路径 — 永远阻止
        for forbidden in FORBIDDEN_PATHS:
            if normalized.startswith(forbidden) or forbidden in normalized:
                return {
                    "allowed": False,
                    "reason": f"forbidden path: {forbidden}",
                    "path": path_str,
                }

        # 允许根路径
        for root in ALLOWED_ROOTS:
            if normalized.startswith(root):
                return {
                    "allowed": True,
                    "reason": f"within allowed root: {root}",
                    "path": path_str,
                }

        # 默认 — 读允许，写阻止
        if operation == "read":
            return {
                "allowed": True,
                "reason": "read allowed by default",
                "path": path_str,
            }
        return {
            "allowed": False,
            "reason": "path not in allowed roots",
            "path": path_str,
        }


__all__ = [
    "ALLOWED_ROOTS",
    "FORBIDDEN_PATHS",
    "CRITICAL_FILES",
    "PathGuard",
]
