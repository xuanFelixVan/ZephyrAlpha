# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_feature_flags
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
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Feature Flags
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 特性开关 —— 运行时切换 Skill 行为。
支持预设 Flag (use_l3_refs, strict_mode, sandbox_preview, audit_enabled)
+ 环境变量覆盖 (ZEPHYR_SKILL_FLAGS)。
"""

from __future__ import annotations

import os
from typing import Any

_PREDEFINED_FLAGS = {
    "use_l3_refs": False,
    "strict_mode": True,
    "sandbox_preview": False,
    "audit_enabled": True,
    "rollback_on_failure": True,
    "circuit_breaker_enabled": False,
    "token_budget_check": True,
}


class SkillFeatureFlags:
    """Skill 特性开关 —— 运行时切换 Skill 行为."""

    _flags: dict[str, dict[str, bool]] = {}

    @classmethod
    def _resolve(cls, skill_id: str, flag: str) -> bool | None:
        env_key = f"ZEPHYR_SKILL_{skill_id.upper().replace('-', '_')}_{flag.upper()}"
        env_val = os.environ.get(env_key)
        if env_val is not None:
            return env_val.lower() in ("1", "true", "yes", "on")
        return None

    @classmethod
    def set_flag(cls, skill_id: str, flag: str, value: bool) -> dict[str, Any]:
        cls._flags.setdefault(skill_id, {})
        cls._flags[skill_id][flag] = value
        return {"skill_id": skill_id, "flag": flag, "value": value}

    @classmethod
    def get_flag(cls, skill_id: str, flag: str) -> bool:
        env_override = cls._resolve(skill_id, flag)
        if env_override is not None:
            return env_override
        return cls._flags.get(skill_id, {}).get(flag, _PREDEFINED_FLAGS.get(flag, False))

    @classmethod
    def get_all_flags(cls, skill_id: str) -> dict[str, bool]:
        result = dict(_PREDEFINED_FLAGS)
        result.update(cls._flags.get(skill_id, {}))
        for flag in result:
            env_override = cls._resolve(skill_id, flag)
            if env_override is not None:
                result[flag] = env_override
        return result

    @classmethod
    def enable_for_all(cls, flag: str):
        _PREDEFINED_FLAGS[flag] = True

    @classmethod
    def disable_for_all(cls, flag: str):
        _PREDEFINED_FLAGS[flag] = False

    @classmethod
    def reset_skill(cls, skill_id: str):
        cls._flags.pop(skill_id, None)

    @classmethod
    def is_strict_mode(cls, skill_id: str) -> bool:
        return cls.get_flag(skill_id, "strict_mode")
