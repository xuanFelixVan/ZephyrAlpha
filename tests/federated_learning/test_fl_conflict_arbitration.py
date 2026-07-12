# [A_test] module_id: SRC-TST-0947 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_conflict_arbitration
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.conflict_arbitration
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_conflict_arbitration.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.conflict_arbitration import ConflictArbitration


class TestConflictArbitrationInstantiation:
    def test_default_construction(self):
        ca = ConflictArbitration()
        assert ca is not None


class TestArbitrate:
    def test_higher_priority_wins(self):
        ca = ConflictArbitration()
        a = {"action": "repair_a", "priority": 5}
        b = {"action": "repair_b", "priority": 3}
        result = ca.arbitrate(a, b)
        assert result["action"] == "repair_a"

    def test_equal_priority_first_wins(self):
        ca = ConflictArbitration()
        a = {"action": "first", "priority": 3}
        b = {"action": "second", "priority": 3}
        result = ca.arbitrate(a, b)
        assert result["action"] == "first"

    def test_no_priority_defaults_to_zero(self):
        ca = ConflictArbitration()
        a = {"action": "no_priority_a"}
        b = {"action": "no_priority_b"}
        result = ca.arbitrate(a, b)
        assert result["action"] == "no_priority_a"


class TestBoundaries:
    def test_arbitrate_empty_dicts(self):
        ca = ConflictArbitration()
        result = ca.arbitrate({}, {})
        assert result == {}

    def test_arbitrate_one_with_priority_one_without(self):
        ca = ConflictArbitration()
        a = {"action": "a"}
        b = {"action": "b", "priority": 10}
        result = ca.arbitrate(a, b)
        assert result["action"] == "b"
