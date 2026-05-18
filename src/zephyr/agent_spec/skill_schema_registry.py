# [BLUEPRINT] MOD-INF-019 | 03_modules/l01_infrastructure/agent-spec/blueprint.md | §

# [MODULE] zephyr.agent_spec.skill_schema_registry

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
MOD-INF-019: Agent Spec — Skill Schema Registry
Blueprint: docs/03_modules/l01_infrastructure/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill I/O Schema 注册与契约验证——确保 Skill 输入输出符合预期结构.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional


class SkillSchemaRegistry:
    """Skill I/O Schema 注册与契约验证."""

    _schemas: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, skill_id: str, input_schema: Dict[str, Any],
                 output_schema: Dict[str, Any]) -> Dict[str, Any]:
        cls._schemas[skill_id] = {"input": input_schema, "output": output_schema}
        return {"skill_id": skill_id, "registered": True}

    @classmethod
    def get_schema(cls, skill_id: str) -> Dict[str, Any]:
        return cls._schemas.get(skill_id, {})

    @classmethod
    def validate_input(cls, skill_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
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
    def validate_output(cls, skill_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
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
    def list_registered(cls) -> List[str]:
        return sorted(cls._schemas.keys())

    @classmethod
    def clear(cls):
        cls._schemas.clear()


__all__ = ["SkillSchemaRegistry"]
