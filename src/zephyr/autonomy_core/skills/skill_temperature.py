# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_temperature
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_skill_temperature | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Temperature
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill Temperature——按任务类型自适应调度 LLM 创造性.
支持: per-skill override, adaptive calibration, task-type defaults.
"""

from __future__ import annotations

from typing import Any


class SkillTemperature:
    """Skill Temperature——自适应 LLM 创造性调度."""

    DEFAULT_TEMPERATURE = 0.3
    _overrides: dict[str, float] = {}
    _task_defaults = {
        "construction": 0.1,
        "design": 0.5,
        "audit": 0.0,
        "feedback": 0.2,
        "brainstorm": 0.7,
        "code_generation": 0.15,
        "code_review": 0.1,
        "documentation": 0.2,
        "testing": 0.0,
    }

    @classmethod
    def get_temperature(cls, skill_id: str, task_type: str | None = None) -> float:
        if skill_id in cls._overrides:
            return cls._overrides[skill_id]
        if task_type:
            for key, temp in cls._task_defaults.items():
                if key in task_type.lower():
                    return temp
        return cls.DEFAULT_TEMPERATURE

    @classmethod
    def set_override(cls, skill_id: str, temperature: float) -> dict[str, Any]:
        clamped = max(0.0, min(2.0, temperature))
        cls._overrides[skill_id] = clamped
        return {"skill_id": skill_id, "temperature": clamped}

    @classmethod
    def remove_override(cls, skill_id: str):
        cls._overrides.pop(skill_id, None)

    @classmethod
    def adaptive(cls, skill_id: str, confidence: float) -> float:
        base = cls.get_temperature(skill_id)
        if confidence < 0.5:
            return min(2.0, base * 1.5)
        if confidence > 0.9:
            return max(0.0, base * 0.5)
        return base

    @classmethod
    def list_overrides(cls) -> dict[str, float]:
        return dict(cls._overrides)

    @classmethod
    def clear_overrides(cls):
        cls._overrides.clear()


__all__ = ["SkillTemperature"]
