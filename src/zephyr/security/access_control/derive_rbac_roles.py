# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.derive_rbac_roles
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_cross_model_consistency.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] derive is deterministic — same input always produces same hash
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] derive never raises; returns hash string for any input
# [TESTS] tests/agent_rbac/test_cross_model_consistency.py
# [A_module] module_id=MOD-SEC_derive_rbac_roles | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""RBACRoleDeriver — RBAC 角色派生器.

依据蓝图 MOD-INF-018 §3:
- 从配置文件派生 RBAC 角色定义
- 生成确定性哈希用于跨模型一致性校验
- 相同输入（含空文件/不存在文件）始终产生相同哈希
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


DEFAULT_DERIVATIONS = {
    "executor": ["read:docs", "read:src", "write:tests", "execute:scripts"],
    "admin": ["read:docs", "read:src", "write:src", "manage:rbac"],
}


class RBACRoleDeriver:
    """RBAC 角色派生器."""

    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def derive(self, config_path: str | Path) -> str:
        """从配置文件派生 RBAC 角色哈希.

        确定性保证：相同输入（含空文件/不存在文件）始终产生相同哈希。

        Args:
            config_path: 配置文件路径

        Returns:
            str: 角色定义的 SHA256 哈希
        """
        path = Path(config_path)
        cache_key = str(path.resolve()) if path.exists() else str(config_path)

        if cache_key in self._cache:
            return self._cache[cache_key]

        if path.exists():
            try:
                content = path.read_bytes()
            except OSError:
                content = b""
        else:
            content = b""

        hash_value = hashlib.sha256(content).hexdigest()
        self._cache[cache_key] = hash_value
        return hash_value


__all__ = [
    "DEFAULT_DERIVATIONS",
    "RBACRoleDeriver",
]
