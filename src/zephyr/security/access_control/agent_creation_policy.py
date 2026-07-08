# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.agent_creation_policy
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] child capabilities <= parent capabilities; len(child) <= len(parent)
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get_child_capabilities()/can_create() never raises; returns list/dict
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_agent_creation_policy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AgentCreationPolicy — Agent 创建策略.

依据蓝图 MOD-INF-018 §3:
- 子 agent 的能力必须 <= 父 agent 的能力（能力衰减）
- 高风险能力（delete/modify:blueprint/audit）不传递给子 agent
- 防止通过创建子 agent 实现权限提升
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# 子 agent 不允许继承的高风险能力前缀/关键词
_BLOCKED_PREFIXES = ("delete:", "reset:", "disable:", "circumvent:")
_BLOCKED_KEYWORDS = (
    "blueprint", "audit", "immutable", "kill_switch",
    "rbac_roles", "superadmin", "delete",
)

# 父成熟度 -> 子成熟度映射
_MATURITY_DECAY_MAP: dict[str, str] = {
    "PROVEN": "MATURE",
    "MATURE": "GROWING",
    "GROWING": "SEEDLING",
    "SEEDLING": "SEEDLING",
}

_MAX_CHILD_CAPABILITIES = 3


@dataclass
class CreationPolicy:
    """Agent 创建策略参数.

    Attributes:
        parent_agent_id: 父 agent ID
        parent_maturity: 父 agent 成熟度
        parent_capability_count: 父 agent 能力数量
    """

    parent_agent_id: str = ""
    parent_maturity: str = ""
    parent_capability_count: int = 0


class AgentCreationPolicy:
    """Agent 创建策略 — 能力衰减控制器.

    确保子 agent 获得的能力是父 agent 能力的子集，
    且高风险能力不向下传递。
    """

    def __init__(self) -> None:
        self._decay_rules: list[str] = list(_BLOCKED_PREFIXES)

    def _is_high_risk(self, capability: str) -> bool:
        """判断能力是否为高风险（不应传递给子 agent）."""
        cap_lower = capability.lower()
        for prefix in _BLOCKED_PREFIXES:
            if cap_lower.startswith(prefix):
                return True
        for keyword in _BLOCKED_KEYWORDS:
            if keyword in cap_lower:
                return True
        return False

    def get_child_maturity(self, parent_maturity: str) -> str:
        """返回子 agent 的成熟度（能力衰减后）.

        Args:
            parent_maturity: 父 agent 的成熟度

        Returns:
            str: 子 agent 的成熟度
        """
        return _MATURITY_DECAY_MAP.get(parent_maturity, "SEEDLING")

    def get_child_capabilities(self, parent_capabilities: list[str]) -> list[str]:
        """返回子 agent 能力列表（能力衰减后）.

        Args:
            parent_capabilities: 父 agent 的能力列表

        Returns:
            子 agent 的能力列表，长度 <= 父能力列表长度
        """
        if not parent_capabilities:
            return []

        child_caps: list[str] = []
        for cap in parent_capabilities:
            if not isinstance(cap, str):
                continue
            if self._is_high_risk(cap):
                logger.debug("AgentCreationPolicy: capability '%s' decayed (high-risk)", cap)
                continue
            child_caps.append(cap)
            if len(child_caps) >= _MAX_CHILD_CAPABILITIES:
                break

        logger.debug(
            "AgentCreationPolicy: parent=%d caps -> child=%d caps (decayed %d)",
            len(parent_capabilities),
            len(child_caps),
            len(parent_capabilities) - len(child_caps),
        )
        return child_caps

    def can_create(self, policy: CreationPolicy) -> dict[str, Any]:
        """检查是否允许创建子 agent.

        Args:
            policy: 创建策略参数

        Returns:
            dict 包含 allowed 标志
        """
        if not policy.parent_agent_id:
            return {"allowed": False, "reason": "parent_agent_id required"}
        if policy.parent_capability_count > 10:
            return {"allowed": False, "reason": "too many parent capabilities"}
        return {"allowed": True, "reason": "creation allowed"}


__all__ = [
    "AgentCreationPolicy",
    "CreationPolicy",
]
