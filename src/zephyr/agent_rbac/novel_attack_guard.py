# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.novel_attack_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""未知攻击检测——签名未知的新型攻击行为基线偏离检测."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BehaviorProfile(BaseModel):
    agent_id: str
    normal_action_count: int = 0
    normal_permission_set: set[str] = Field(default_factory=set)
    novel_attempts: list[str] = Field(default_factory=list)
    suspicion_score: float = 0.0


class NovelAttackGuard:
    _NORMAL_PATTERNS = {"read", "write", "execute", "query", "list", "get", "check"}
    _MAX_SUSPICION = 5.0

    def __init__(self) -> None:
        self._profiles: dict[str, BehaviorProfile] = {}

    def profile_action(self, agent_id: str, action: str) -> dict[str, Any]:
        if agent_id not in self._profiles:
            self._profiles[agent_id] = BehaviorProfile(agent_id=agent_id)

        profile = self._profiles[agent_id]
        profile.normal_action_count += 1

        if action not in self._NORMAL_PATTERNS:
            profile.novel_attempts.append(action)
            profile.suspicion_score = min(self._MAX_SUSPICION, len(profile.novel_attempts) * 0.5)

        suspicious = profile.suspicion_score >= 2.0
        return {"agent_id": agent_id, "action": action, "suspicion_score": profile.suspicion_score, "suspicious": suspicious}
