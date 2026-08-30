# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_temperature
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Temperature
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill Temperature——按任务类型自适应调度 LLM 创造性.
支持: per-skill override, adaptive calibration, task-type defaults.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: skill_temperature.py
# 层: 算法
# - id: A1
#   name_zh: ① SkillTemperature
#   name_en: SkillTemperature
#   intro: Skill Temperature——自适应 LLM 创造性调度.
#   desc: Skill Temperature——自适应 LLM 创造性调度.；公共方法（定义序）: get_temperature, set_override, remove_override, adaptive, list_o…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SkillTemperature
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
    overrides: dict[str, float] = _overrides  # public alias（Stage 4 公共化）
    task_defaults = _task_defaults  # public alias（Stage 4 公共化）

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
