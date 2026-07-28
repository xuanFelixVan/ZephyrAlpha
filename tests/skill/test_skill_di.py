# [A_test] module_id: MOD-GOV_skill_di | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_di
# [INVARIANTS] SkillDI topological_order must produce valid dependency ordering
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 = all pass; exit != 0 = regression
# [TESTS] tests/test_skill_di.py
# [TTL] task_bound

import pytest

from zephyr.autonomy_core.skills.skill_di import SkillDI


@pytest.fixture(autouse=True)
def clean_registry():
    SkillDI.clear()
    yield
    SkillDI.clear()


class TestSkillDIInstantiation:
    def test_registry_starts_empty(self):
        assert SkillDI.registry == {}

    def test_clear_empties_registry(self):
        SkillDI.register("skill-a", {"dep1": "fallback1"})
        assert len(SkillDI.registry) > 0
        SkillDI.clear()
        assert SkillDI.registry == {}


class TestRegister:
    def test_register_skill_with_deps(self):
        result = SkillDI.register("skill-a", {"dep1": "fallback1", "dep2": "fallback2"})
        assert result["skill_id"] == "skill-a"
        assert result["dependencies_registered"] is True

    def test_register_overwrites_existing(self):
        SkillDI.register("skill-a", {"dep1": "old"})
        SkillDI.register("skill-a", {"dep1": "new"})
        resolved = SkillDI.resolve("skill-a")
        assert resolved["dep1"] == "new"

    def test_register_empty_deps(self):
        result = SkillDI.register("skill-empty", {})
        assert result["dependencies_registered"] is True
        assert SkillDI.resolve("skill-empty") == {}


class TestResolve:
    def test_resolve_existing_skill(self):
        SkillDI.register("skill-a", {"dep1": "fallback1"})
        result = SkillDI.resolve("skill-a")
        assert result == {"dep1": "fallback1"}

    def test_resolve_nonexistent_skill_returns_empty(self):
        result = SkillDI.resolve("nonexistent")
        assert result == {}


class TestInject:
    def test_inject_missing_deps_from_registry(self):
        SkillDI.register("dep-a", {"default": "resolved_value"})
        SkillDI.register("skill-x", {"dep-a": "fallback_val"})
        result = SkillDI.inject("skill-x", {"existing_key": "existing_val"})
        assert result["existing_key"] == "existing_val"
        assert result["dep-a"] == "resolved_value"

    def test_inject_does_not_override_existing_context(self):
        SkillDI.register("dep-a", {"default": "resolved_value"})
        SkillDI.register("skill-x", {"dep-a": "fallback_val"})
        result = SkillDI.inject("skill-x", {"dep-a": "already_set"})
        assert result["dep-a"] == "already_set"

    def test_inject_uses_fallback_when_dep_not_registered(self):
        SkillDI.register("skill-x", {"missing-dep": "fallback_val"})
        result = SkillDI.inject("skill-x", {})
        assert result["missing-dep"] == "fallback_val"

    def test_inject_empty_context(self):
        SkillDI.register("skill-x", {"dep1": "fallback1"})
        result = SkillDI.inject("skill-x", {})
        assert "dep1" in result

    def test_inject_nonexistent_skill(self):
        result = SkillDI.inject("nonexistent", {"key": "val"})
        assert result == {"key": "val"}


class TestTopologicalOrder:
    def test_simple_chain(self):
        SkillDI.register("a", {})
        SkillDI.register("b", {"a": "fallback"})
        SkillDI.register("c", {"b": "fallback"})
        order = SkillDI.topological_order(["a", "b", "c"])
        assert order.index("a") < order.index("b")
        assert order.index("b") < order.index("c")

    def test_independent_skills_any_order(self):
        SkillDI.register("x", {})
        SkillDI.register("y", {})
        order = SkillDI.topological_order(["x", "y"])
        assert set(order) == {"x", "y"}

    def test_diamond_dependency(self):
        SkillDI.register("base", {})
        SkillDI.register("left", {"base": "fb"})
        SkillDI.register("right", {"base": "fb"})
        SkillDI.register("top", {"left": "fb", "right": "fb"})
        order = SkillDI.topological_order(["base", "left", "right", "top"])
        assert order.index("base") < order.index("left")
        assert order.index("base") < order.index("right")
        assert order.index("left") < order.index("top")
        assert order.index("right") < order.index("top")

    def test_empty_list(self):
        order = SkillDI.topological_order([])
        assert order == []

    def test_single_skill(self):
        SkillDI.register("solo", {})
        order = SkillDI.topological_order(["solo"])
        assert order == ["solo"]

    def test_deps_outside_skill_ids_ignored(self):
        SkillDI.register("a", {"external-dep": "fb"})
        order = SkillDI.topological_order(["a"])
        assert order == ["a"]

    def test_all_skills_in_result(self):
        SkillDI.register("a", {})
        SkillDI.register("b", {"a": "fb"})
        SkillDI.register("c", {"a": "fb"})
        order = SkillDI.topological_order(["a", "b", "c"])
        assert set(order) == {"a", "b", "c"}
