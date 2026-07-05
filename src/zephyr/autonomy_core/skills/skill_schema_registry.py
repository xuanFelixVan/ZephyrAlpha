# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_schema_registry
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
# [A_module] module_id=MOD-ORC_skill_schema_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Schema Registry
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill I/O Schema 注册与契约验证——确保 Skill 输入输出符合预期结构.
"""

from __future__ import annotations

from typing import Any


class SkillSchemaRegistry:
    """Skill I/O Schema 注册与契约验证."""

    _schemas: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, skill_id: str, input_schema: dict[str, Any], output_schema: dict[str, Any]) -> dict[str, Any]:
        cls._schemas[skill_id] = {"input": input_schema, "output": output_schema}
        return {"skill_id": skill_id, "registered": True}

    @classmethod
    def get_schema(cls, skill_id: str) -> dict[str, Any]:
        return cls._schemas.get(skill_id, {})

    @classmethod
    def validate_input(cls, skill_id: str, data: dict[str, Any]) -> dict[str, Any]:
        schema = cls._schemas.get(skill_id, {}).get("input", {})
        errors = []
        for key, rules in schema.items():
            if rules.get("required") and key not in data:
                errors.append(f"Missing required input field: {key}")
            if key in data and "type" in rules:
                expected = rules["type"]
                actual = type(data[key]).__name__
                if actual != expected:
                    errors.append(f"Field '{key}': expected {expected}, got {actual}")
        return {"valid": len(errors) == 0, "errors": errors}

    @classmethod
    def validate_output(cls, skill_id: str, data: dict[str, Any]) -> dict[str, Any]:
        schema = cls._schemas.get(skill_id, {}).get("output", {})
        errors = []
        for key, rules in schema.items():
            if rules.get("required") and key not in data:
                errors.append(f"Missing required output field: {key}")
            if key in data and "type" in rules:
                expected = rules["type"]
                actual = type(data[key]).__name__
                if actual != expected:
                    errors.append(f"Output field '{key}': expected {expected}, got {actual}")
        return {"valid": len(errors) == 0, "errors": errors}

    @classmethod
    def list_registered(cls) -> list[str]:
        return sorted(cls._schemas.keys())

    @classmethod
    def clear(cls):
        cls._schemas.clear()


__all__ = ["SkillSchemaRegistry"]
