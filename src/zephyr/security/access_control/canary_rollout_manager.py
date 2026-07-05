# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.canary_rollout_manager
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_permissions.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] register stores CanaryPermission; start_sampling transitions to SAMPLING state
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] register/start_sampling never raise
# [TESTS] tests/agent_rbac/test_permissions.py
# [A_module] module_id=MOD-SEC_canary_rollout_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""CanaryRolloutManager — 灰度发布管理器.

依据蓝图 MOD-INF-018 §3:
- 注册灰度权限规则
- 控制灰度状态机（DRAFT → SAMPLING → ROLLOUT）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class CanaryState:
    """灰度状态枚举."""

    DRAFT = "DRAFT"
    SAMPLING = "SAMPLING"
    ROLLOUT = "ROLLOUT"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class CanaryPermission:
    """灰度权限.

    Attributes:
        name: 权限名称
        rules: 关联规则列表
        state: 当前状态
    """

    name: str
    rules: list[str] = field(default_factory=list)
    state: str = CanaryState.DRAFT


class CanaryRolloutManager:
    """灰度发布管理器 — 注册与控制灰度权限."""

    def __init__(self) -> None:
        self._canaries: dict[str, CanaryPermission] = {}

    def register(self, name: str, rules: list[str]) -> CanaryPermission:
        """注册灰度权限.

        Args:
            name: 权限名称
            rules: 关联规则列表

        Returns:
            CanaryPermission 初始状态为 DRAFT
        """
        canary = CanaryPermission(name=name, rules=list(rules), state=CanaryState.DRAFT)
        self._canaries[name] = canary
        return canary

    def start_sampling(self, name: str) -> dict[str, Any]:
        """启动灰度采样.

        Args:
            name: 权限名称

        Returns:
            dict 包含 state 字段
        """
        canary = self._canaries.get(name)
        if canary is None:
            return {"state": "NOT_FOUND", "error": "canary_not_registered"}
        canary.state = CanaryState.SAMPLING
        return {
            "state": CanaryState.SAMPLING,
            "name": name,
            "rules": list(canary.rules),
        }


__all__ = [
    "CanaryPermission",
    "CanaryRolloutManager",
    "CanaryState",
]
