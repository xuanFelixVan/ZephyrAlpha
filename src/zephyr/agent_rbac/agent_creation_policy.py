# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.agent_creation_policy

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Agent创建权与权限遗传——creation_policy/遗传衰减/spawn_storm熔断/生命周期管理."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreationPolicy(BaseModel):
    parent_agent_id: str
    parent_maturity: str
    parent_capability_count: int
    max_children: int = 10
    spawn_window_seconds: int = 300
    decay_factor: float = 0.7


class AgentCreationPolicy:
    def __init__(self) -> None:
        self._child_counts: dict[str, list[float]] = {}

    def can_create(self, policy: CreationPolicy) -> dict[str, Any]:
        spawns = self._child_counts.get(policy.parent_agent_id, [])
        recent_spawns = [t for t in spawns if t > __import__("time").time() - policy.spawn_window_seconds]

        if len(recent_spawns) >= policy.max_children:
            return {"allowed": False, "reason": "spawn_storm_detected", "recent_spawns": len(recent_spawns)}

        return {"allowed": True, "parent_agent_id": policy.parent_agent_id}

    def get_child_maturity(self, parent_maturity: str) -> str:
        levels = ["IMMATURE", "ADOLESCENT", "MATURE", "PROVEN", "SUPERADMIN"]
        try:
            idx = levels.index(parent_maturity)
        except ValueError:
            return "IMMATURE"
        return levels[max(0, idx - 1)]

    def get_child_capabilities(self, parent_capabilities: list[str]) -> list[str]:
        count = max(1, int(len(parent_capabilities) * 0.7))
        return parent_capabilities[:count]

    def record_spawn(self, parent_agent_id: str) -> None:
        if parent_agent_id not in self._child_counts:
            self._child_counts[parent_agent_id] = []
        self._child_counts[parent_agent_id].append(__import__("time").time())
