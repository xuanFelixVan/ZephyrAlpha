# [A_test] module_id: MOD-GOV_subagent_hook_propagator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_subagent_hook_propagator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_subagent_hook_propagator.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.intelligence_governance.subagent_hook_propagator import (
    SubagentHookPropagator,
)


class TestSubagentHookPropagatorInstantiation:
    def test_empty_on_creation(self):
        prop = SubagentHookPropagator()
        assert prop._hooks == {}

    def test_independent_instances(self):
        p1 = SubagentHookPropagator()
        p2 = SubagentHookPropagator()
        p1.register_hook("parent", "hook_a")
        assert "parent" not in p2._hooks


class TestRegisterHook:
    def test_register_with_propagate_true(self):
        prop = SubagentHookPropagator()
        prop.register_hook("parent_a", "safety_check", propagate=True)
        assert prop._hooks["parent_a"]["name"] == "safety_check"
        assert prop._hooks["parent_a"]["propagate_to_subagents"] is True

    def test_register_with_propagate_false(self):
        prop = SubagentHookPropagator()
        prop.register_hook("parent_b", "audit_log", propagate=False)
        assert prop._hooks["parent_b"]["name"] == "audit_log"
        assert prop._hooks["parent_b"]["propagate_to_subagents"] is False

    def test_register_default_propagate_is_true(self):
        prop = SubagentHookPropagator()
        prop.register_hook("parent_c", "default_hook")
        assert prop._hooks["parent_c"]["propagate_to_subagents"] is True

    def test_register_overwrites_previous(self):
        prop = SubagentHookPropagator()
        prop.register_hook("parent_d", "first_hook", propagate=True)
        prop.register_hook("parent_d", "second_hook", propagate=False)
        assert prop._hooks["parent_d"]["name"] == "second_hook"
        assert prop._hooks["parent_d"]["propagate_to_subagents"] is False

    def test_register_multiple_parents(self):
        prop = SubagentHookPropagator()
        prop.register_hook("p1", "hook1")
        prop.register_hook("p2", "hook2", propagate=False)
        prop.register_hook("p3", "hook3")
        assert len(prop._hooks) == 3


class TestMustPropagate:
    def test_propagate_true(self):
        prop = SubagentHookPropagator()
        prop.register_hook("parent", "hook", propagate=True)
        assert prop.must_propagate("parent") is True

    def test_propagate_false(self):
        prop = SubagentHookPropagator()
        prop.register_hook("parent", "hook", propagate=False)
        assert prop.must_propagate("parent") is False

    def test_unregistered_parent_defaults_to_true(self):
        prop = SubagentHookPropagator()
        assert prop.must_propagate("unknown_parent") is True

    def test_default_propagate_is_true(self):
        prop = SubagentHookPropagator()
        prop.register_hook("parent", "hook")
        assert prop.must_propagate("parent") is True

    def test_multiple_parents_mixed(self):
        prop = SubagentHookPropagator()
        prop.register_hook("p1", "h1", propagate=True)
        prop.register_hook("p2", "h2", propagate=False)
        assert prop.must_propagate("p1") is True
        assert prop.must_propagate("p2") is False

    def test_empty_string_agent_id(self):
        prop = SubagentHookPropagator()
        assert prop.must_propagate("") is True

    def test_register_empty_string_then_check(self):
        prop = SubagentHookPropagator()
        prop.register_hook("", "hook", propagate=False)
        assert prop.must_propagate("") is False
