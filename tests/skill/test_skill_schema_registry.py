# [A_test] module_id: MOD-GOV_skill_schema_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_schema_registry
# [INVARIANTS] SkillSchemaRegistry.clear() called in every test teardown
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] validate_input/validate_output return {valid: bool, errors: list}
# [TESTS] tests/test_skill_schema_registry.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.autonomy_core.skills.skill_schema_registry import SkillSchemaRegistry


@pytest.fixture(autouse=True)
def _clear_registry():
    yield
    SkillSchemaRegistry.clear()


class TestSkillSchemaRegistryInstantiation:
    def test_schemas_initially_empty(self):
        SkillSchemaRegistry.clear()
        assert SkillSchemaRegistry.schemas == {}

    def test_list_registered_empty(self):
        SkillSchemaRegistry.clear()
        assert SkillSchemaRegistry.list_registered() == []


class TestRegister:
    def test_register_returns_confirmation(self):
        result = SkillSchemaRegistry.register(
            "skill_x",
            input_schema={"query": {"type": "str", "required": True}},
            output_schema={"result": {"type": "str", "required": True}},
        )
        assert result["skill_id"] == "skill_x"
        assert result["registered"] is True

    def test_register_stores_schema(self):
        inp = {"query": {"type": "str", "required": True}}
        out = {"result": {"type": "str", "required": True}}
        SkillSchemaRegistry.register("skill_y", inp, out)
        schema = SkillSchemaRegistry.get_schema("skill_y")
        assert schema["input"] == inp
        assert schema["output"] == out

    def test_register_overwrites_existing(self):
        SkillSchemaRegistry.register(
            "skill_z",
            input_schema={"a": {"type": "int", "required": True}},
            output_schema={"b": {"type": "str"}},
        )
        SkillSchemaRegistry.register(
            "skill_z",
            input_schema={"c": {"type": "float", "required": False}},
            output_schema={"d": {"type": "bool"}},
        )
        schema = SkillSchemaRegistry.get_schema("skill_z")
        assert "c" in schema["input"]
        assert "a" not in schema["input"]

    def test_list_registered_returns_sorted(self):
        SkillSchemaRegistry.register("beta", {}, {})
        SkillSchemaRegistry.register("alpha", {}, {})
        SkillSchemaRegistry.register("gamma", {}, {})
        assert SkillSchemaRegistry.list_registered() == ["alpha", "beta", "gamma"]


class TestGetSchema:
    def test_returns_schema_for_registered_skill(self):
        SkillSchemaRegistry.register(
            "skill_g1",
            input_schema={"x": {"type": "int"}},
            output_schema={"y": {"type": "str"}},
        )
        result = SkillSchemaRegistry.get_schema("skill_g1")
        assert "input" in result
        assert "output" in result

    def test_returns_empty_for_unknown_skill(self):
        result = SkillSchemaRegistry.get_schema("nonexistent")
        assert result == {}

    def test_returns_empty_for_empty_string(self):
        result = SkillSchemaRegistry.get_schema("")
        assert result == {}


class TestValidateInput:
    def test_valid_input_passes(self):
        SkillSchemaRegistry.register(
            "skill_vi",
            input_schema={"name": {"type": "str", "required": True}},
            output_schema={},
        )
        result = SkillSchemaRegistry.validate_input("skill_vi", {"name": "alice"})
        assert result["valid"] is True
        assert result["errors"] == []

    def test_missing_required_field_fails(self):
        SkillSchemaRegistry.register(
            "skill_mi",
            input_schema={"name": {"type": "str", "required": True}},
            output_schema={},
        )
        result = SkillSchemaRegistry.validate_input("skill_mi", {})
        assert result["valid"] is False
        assert any("Missing required" in e for e in result["errors"])

    def test_wrong_type_fails(self):
        SkillSchemaRegistry.register(
            "skill_wt",
            input_schema={"count": {"type": "int", "required": True}},
            output_schema={},
        )
        result = SkillSchemaRegistry.validate_input("skill_wt", {"count": "not_int"})
        assert result["valid"] is False
        assert any("expected int" in e for e in result["errors"])

    def test_optional_field_missing_passes(self):
        SkillSchemaRegistry.register(
            "skill_opt",
            input_schema={"name": {"type": "str", "required": True}, "age": {"type": "int", "required": False}},
            output_schema={},
        )
        result = SkillSchemaRegistry.validate_input("skill_opt", {"name": "bob"})
        assert result["valid"] is True

    def test_unregistered_skill_returns_valid(self):
        result = SkillSchemaRegistry.validate_input("no_such_skill", {"a": 1})
        assert result["valid"] is True
        assert result["errors"] == []

    def test_empty_data_with_required_field(self):
        SkillSchemaRegistry.register(
            "skill_ed",
            input_schema={"field": {"type": "str", "required": True}},
            output_schema={},
        )
        result = SkillSchemaRegistry.validate_input("skill_ed", {})
        assert result["valid"] is False


class TestValidateOutput:
    def test_valid_output_passes(self):
        SkillSchemaRegistry.register(
            "skill_vo",
            input_schema={},
            output_schema={"status": {"type": "str", "required": True}},
        )
        result = SkillSchemaRegistry.validate_output("skill_vo", {"status": "ok"})
        assert result["valid"] is True

    def test_missing_required_output_field(self):
        SkillSchemaRegistry.register(
            "skill_mo",
            input_schema={},
            output_schema={"status": {"type": "str", "required": True}},
        )
        result = SkillSchemaRegistry.validate_output("skill_mo", {})
        assert result["valid"] is False

    def test_wrong_output_type(self):
        SkillSchemaRegistry.register(
            "skill_wto",
            input_schema={},
            output_schema={"code": {"type": "int", "required": True}},
        )
        result = SkillSchemaRegistry.validate_output("skill_wto", {"code": "200"})
        assert result["valid"] is False
        assert any("expected int" in e for e in result["errors"])

    def test_unregistered_skill_returns_valid(self):
        result = SkillSchemaRegistry.validate_output("no_such_skill", {"x": 1})
        assert result["valid"] is True


class TestClear:
    def test_clear_empties_registry(self):
        SkillSchemaRegistry.register("a", {}, {})
        SkillSchemaRegistry.register("b", {}, {})
        SkillSchemaRegistry.clear()
        assert SkillSchemaRegistry.list_registered() == []
        assert SkillSchemaRegistry.schemas == {}
