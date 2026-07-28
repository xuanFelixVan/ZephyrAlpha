# [A_test] module_id: MOD-GOV_skill_temperature | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_temperature
# [INVARIANTS] SkillTemperature.overrides cleared between tests; temperature clamped [0.0, 2.0]
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_skill_temperature.py
# [TTL] task_bound

from zephyr.autonomy_core.skills.skill_temperature import SkillTemperature


class TestSkillTemperatureInstantiation:
    def test_class_exists(self):
        assert SkillTemperature is not None

    def test_default_temperature_value(self):
        assert SkillTemperature.DEFAULT_TEMPERATURE == 0.3

    def test_task_defaults_populated(self):
        assert "construction" in SkillTemperature.task_defaults
        assert "design" in SkillTemperature.task_defaults
        assert "audit" in SkillTemperature.task_defaults

    def test_overrides_initially_empty_or_cleared(self):
        SkillTemperature.clear_overrides()
        assert SkillTemperature.list_overrides() == {}


class TestGetTemperature:
    def setup_method(self):
        SkillTemperature.clear_overrides()

    def test_returns_default_when_no_override_no_task_type(self):
        result = SkillTemperature.get_temperature("unknown_skill")
        assert result == SkillTemperature.DEFAULT_TEMPERATURE

    def test_returns_override_when_set(self):
        SkillTemperature.set_override("my_skill", 0.8)
        result = SkillTemperature.get_temperature("my_skill")
        assert result == 0.8

    def test_override_takes_precedence_over_task_type(self):
        SkillTemperature.set_override("my_skill", 0.9)
        result = SkillTemperature.get_temperature("my_skill", task_type="construction")
        assert result == 0.9

    def test_task_type_construction(self):
        result = SkillTemperature.get_temperature("x", task_type="construction")
        assert result == 0.1

    def test_task_type_design(self):
        result = SkillTemperature.get_temperature("x", task_type="design")
        assert result == 0.5

    def test_task_type_audit(self):
        result = SkillTemperature.get_temperature("x", task_type="audit")
        assert result == 0.0

    def test_task_type_brainstorm(self):
        result = SkillTemperature.get_temperature("x", task_type="brainstorm")
        assert result == 0.7

    def test_task_type_case_insensitive(self):
        result = SkillTemperature.get_temperature("x", task_type="CONSTRUCTION")
        assert result == 0.1

    def test_task_type_partial_match(self):
        result = SkillTemperature.get_temperature("x", task_type="code_generation")
        assert result == 0.15

    def test_unknown_task_type_returns_default(self):
        result = SkillTemperature.get_temperature("x", task_type="unknown_type")
        assert result == SkillTemperature.DEFAULT_TEMPERATURE


class TestSetOverride:
    def setup_method(self):
        SkillTemperature.clear_overrides()

    def test_set_override_returns_dict(self):
        result = SkillTemperature.set_override("skill_a", 0.5)
        assert result["skill_id"] == "skill_a"
        assert result["temperature"] == 0.5

    def test_clamps_high_temperature(self):
        result = SkillTemperature.set_override("skill_b", 5.0)
        assert result["temperature"] == 2.0

    def test_clamps_negative_temperature(self):
        result = SkillTemperature.set_override("skill_c", -1.0)
        assert result["temperature"] == 0.0

    def test_clamp_at_boundary_zero(self):
        result = SkillTemperature.set_override("skill_d", 0.0)
        assert result["temperature"] == 0.0

    def test_clamp_at_boundary_two(self):
        result = SkillTemperature.set_override("skill_e", 2.0)
        assert result["temperature"] == 2.0


class TestRemoveOverride:
    def setup_method(self):
        SkillTemperature.clear_overrides()

    def test_remove_existing_override(self):
        SkillTemperature.set_override("skill_x", 0.6)
        SkillTemperature.remove_override("skill_x")
        assert SkillTemperature.get_temperature("skill_x") == SkillTemperature.DEFAULT_TEMPERATURE

    def test_remove_nonexistent_override_no_error(self):
        SkillTemperature.remove_override("nonexistent_skill")


class TestAdaptive:
    def setup_method(self):
        SkillTemperature.clear_overrides()

    def test_low_confidence_increases_temperature(self):
        base = SkillTemperature.get_temperature("x")
        result = SkillTemperature.adaptive("x", confidence=0.3)
        assert result >= base

    def test_high_confidence_decreases_temperature(self):
        base = SkillTemperature.get_temperature("x")
        result = SkillTemperature.adaptive("x", confidence=0.95)
        assert result <= base

    def test_medium_confidence_returns_base(self):
        base = SkillTemperature.get_temperature("x")
        result = SkillTemperature.adaptive("x", confidence=0.7)
        assert result == base

    def test_adaptive_clamped_at_two(self):
        SkillTemperature.set_override("hot_skill", 1.9)
        result = SkillTemperature.adaptive("hot_skill", confidence=0.1)
        assert result <= 2.0

    def test_adaptive_clamped_at_zero(self):
        SkillTemperature.set_override("cold_skill", 0.05)
        result = SkillTemperature.adaptive("cold_skill", confidence=0.99)
        assert result >= 0.0


class TestListAndClearOverrides:
    def setup_method(self):
        SkillTemperature.clear_overrides()

    def test_list_overrides_empty(self):
        assert SkillTemperature.list_overrides() == {}

    def test_list_overrides_after_setting(self):
        SkillTemperature.set_override("a", 0.5)
        SkillTemperature.set_override("b", 0.8)
        overrides = SkillTemperature.list_overrides()
        assert overrides == {"a": 0.5, "b": 0.8}

    def test_clear_overrides(self):
        SkillTemperature.set_override("a", 0.5)
        SkillTemperature.clear_overrides()
        assert SkillTemperature.list_overrides() == {}

    def test_list_overrides_returns_copy(self):
        SkillTemperature.set_override("a", 0.5)
        result = SkillTemperature.list_overrides()
        result["a"] = 999
        assert SkillTemperature.list_overrides()["a"] == 0.5
