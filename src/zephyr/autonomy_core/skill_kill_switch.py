# [A_module] module_id=MOD-ORC_skill_kill_switch | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md

# [MODULE] zephyr.orchestration.agent_lifecycle.skill_kill_switch

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
MOD-INF-019: Agent Spec — Skill Kill Switch
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 熔断开关 —— 紧急停用异常 Skill，防雪崩。
集成 CircuitBreakerCheck + blind_spot_tracker B96/B98 模式。
"""


from __future__ import annotations

import time
from typing import Dict, Any, List

from zephyr.autonomy_core.skill_model import SkillStatus


class SkillKillSwitch:
    """Skill 熔断开关 —— 紧急停用."""

    _killed: Dict[str, Dict[str, Any]] = {}

    _FAIL_THRESHOLD = 3
    _COOLDOWN_S = 300.0

    @classmethod
    def kill(cls, skill_id: str, reason: str,
             trigger: str = "manual") -> Dict[str, Any]:
        cls._killed[skill_id] = {
            "skill_id": skill_id,
            "status": SkillStatus.DEPRECATED.value,
            "killed_at": time.time(),
            "reason": reason,
            "trigger": trigger,
        }
        return dict(cls._killed[skill_id], action="killed")

    @classmethod
    def revive(cls, skill_id: str) -> Dict[str, Any]:
        if skill_id in cls._killed:
            del cls._killed[skill_id]
            return {"skill_id": skill_id, "status": SkillStatus.ACTIVE.value, "action": "revived"}
        return {"skill_id": skill_id, "action": "not_killed"}

    @classmethod
    def is_killed(cls, skill_id: str) -> bool:
        if skill_id not in cls._killed:
            return False
        entry = cls._killed[skill_id]
        return time.time() - entry["killed_at"] < cls._COOLDOWN_S

    @classmethod
    def auto_kill_on_errors(cls, skill_id: str,
                            error_count: int) -> Optional[Dict[str, Any]]:
        if error_count >= cls._FAIL_THRESHOLD:
            return cls.kill(
                skill_id,
                reason=f"auto-kill: {error_count} consecutive errors >= threshold {cls._FAIL_THRESHOLD}",
                trigger="circuit_breaker",
            )
        return None

    @classmethod
    def list_killed(cls) -> List[Dict[str, Any]]:
        return [
            {"skill_id": sid, **entry}
            for sid, entry in cls._killed.items()
            if time.time() - entry["killed_at"] < cls._COOLDOWN_S
        ]

    @classmethod
    def clear_all(cls):
        cls._killed.clear()
