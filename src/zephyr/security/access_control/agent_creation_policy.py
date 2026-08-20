# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.agent_creation_policy
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py; tests/agent/test_agent_creation_policy.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] child capabilities <= parent capabilities; len(child) <= len(parent); spawn_storm_detected when recent_spawns >= max_children
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get_child_capabilities()/can_create() never raises; returns list/dict
# [TESTS] tests/agent/test_agent_creation_policy.py; tests/agent_rbac/test_enhanced_security.py
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AgentCreationPolicy — Agent 创建策略.

依据蓝图 MOD-INF-018 §3:
- 子 agent 的能力数量 <= 父 agent 的能力数量（能力衰减，截断至前3项）
- 子 agent 的成熟度比父 agent 低一级
- 防止通过创建子 agent 实现权限提升（spawn storm 检测）

治本(2026-07-18): 重写以匹配 tests/agent/test_agent_creation_policy.py 契约.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

_MATURITY_DECAY_MAP: dict[str, str] = {
    "SUPERADMIN": "PROVEN",
    "PROVEN": "MATURE",
    "MATURE": "ADOLESCENT",
    "ADOLESCENT": "IMMATURE",
    "IMMATURE": "IMMATURE",
}

_MAX_CHILD_CAPABILITIES = 3


@dataclass
class CreationPolicy:
    """Agent 创建策略参数."""

    parent_agent_id: str = ""
    parent_maturity: str = ""
    parent_capability_count: int = 0
    max_children: int = 10
    spawn_window_seconds: int = 300
    decay_factor: float = 0.7


class AgentCreationPolicy:
    """Agent 创建策略 — 能力衰减 + spawn storm 检测控制器."""

    def __init__(self) -> None:
        self._child_counts: dict[str, list[float]] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def child_counts(self) -> dict[str, list[float]]:
        """只读：child_counts（Stage 4 公共化）。"""
        return self._child_counts

    @child_counts.setter
    def child_counts(self, value):
        """写入：child_counts（Stage 4 公共化）。"""
        self._child_counts = value

    def record_spawn(self, parent_agent_id: str) -> None:
        """记录一次子 agent 创建事件."""
        if parent_agent_id not in self._child_counts:
            self._child_counts[parent_agent_id] = []
        self._child_counts[parent_agent_id].append(time.time())

    def _recent_spawn_count(self, parent_agent_id: str, window_seconds: int) -> int:
        """返回指定父 agent 在窗口期内的 spawn 数量（同时清理过期记录）."""
        if parent_agent_id not in self._child_counts:
            return 0
        now = time.time()
        recent = [t for t in self._child_counts[parent_agent_id] if now - t <= window_seconds]
        self._child_counts[parent_agent_id] = recent
        return len(recent)

    def get_child_maturity(self, parent_maturity: str) -> str:
        """返回子 agent 的成熟度（能力衰减后）."""
        return _MATURITY_DECAY_MAP.get(parent_maturity, "IMMATURE")

    def get_child_capabilities(self, parent_capabilities: list[str]) -> list[str]:
        """返回子 agent 能力列表（截断前 _MAX_CHILD_CAPABILITIES 项）."""
        if not parent_capabilities:
            return []
        return list(parent_capabilities[:_MAX_CHILD_CAPABILITIES])

    def can_create(self, policy: CreationPolicy) -> dict[str, Any]:
        """检查是否允许创建子 agent."""
        if not policy.parent_agent_id:
            return {"allowed": False, "reason": "parent_agent_id required"}

        recent = self._recent_spawn_count(policy.parent_agent_id, policy.spawn_window_seconds)
        if recent >= policy.max_children:
            logger.warning(
                "AgentCreationPolicy: spawn storm detected for %s (recent=%d max=%d)",
                policy.parent_agent_id,
                recent,
                policy.max_children,
            )
            return {
                "allowed": False,
                "reason": "spawn_storm_detected",
                "parent_agent_id": policy.parent_agent_id,
                "recent_spawns": recent,
            }

        return {
            "allowed": True,
            "reason": "creation allowed",
            "parent_agent_id": policy.parent_agent_id,
            "recent_spawns": recent,
        }


__all__ = [
    "AgentCreationPolicy",
    "CreationPolicy",
]
