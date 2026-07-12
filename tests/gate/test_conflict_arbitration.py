# [A_test] module_id: SRC-TST-0576 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_conflict_arbitration
# [INVARIANTS] Higher priority proposal must always win
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.conflict_arbitration import ConflictArbitration


class TestConflictArbitrationInstantiation:
    def test_default_creation(self):
        ca = ConflictArbitration()
        assert ca is not None


class TestArbitrate:
    def test_higher_priority_a_wins(self):
        ca = ConflictArbitration()
        result = ca.arbitrate({"priority": 5}, {"priority": 3})
        assert result == {"priority": 5}

    def test_higher_priority_b_wins(self):
        ca = ConflictArbitration()
        result = ca.arbitrate({"priority": 2}, {"priority": 8})
        assert result == {"priority": 8}

    def test_equal_priority_a_wins(self):
        ca = ConflictArbitration()
        result = ca.arbitrate({"priority": 5}, {"priority": 5})
        assert result == {"priority": 5}

    def test_no_priority_defaults_to_zero(self):
        ca = ConflictArbitration()
        result = ca.arbitrate({}, {})
        assert result == {}

    def test_one_has_priority_other_does_not(self):
        ca = ConflictArbitration()
        result = ca.arbitrate({"priority": 1}, {})
        assert result == {"priority": 1}

    def test_empty_dicts(self):
        ca = ConflictArbitration()
        result = ca.arbitrate({}, {})
        assert result == {}
