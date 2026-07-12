# [A_test] module_id: SRC-TST-0267 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_action_reversibility
# [INVARIANTS] IRREVERSIBLE + autonomy<3 must block; FULLY_REVERSIBLE must pass
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.action_reversibility import ActionReversibility, Reversibility


class TestReversibility:
    def test_enum_values(self):
        assert Reversibility.FULLY_REVERSIBLE == "FULLY_REVERSIBLE"
        assert Reversibility.PARTIALLY_REVERSIBLE == "PARTIALLY_REVERSIBLE"
        assert Reversibility.IRREVERSIBLE == "IRREVERSIBLE"
        assert Reversibility.UNKNOWN == "UNKNOWN"


class TestActionReversibilityInstantiation:
    def test_default_empty_blocked(self):
        ar = ActionReversibility()
        assert ar.blocked_actions == []


class TestClassify:
    def test_both_rollback_and_snapshot_fully_reversible(self):
        ar = ActionReversibility()
        result = ar.classify("action1", has_rollback=True, has_snapshot=True)
        assert result == Reversibility.FULLY_REVERSIBLE

    def test_rollback_only_partially_reversible(self):
        ar = ActionReversibility()
        result = ar.classify("action1", has_rollback=True, has_snapshot=False)
        assert result == Reversibility.PARTIALLY_REVERSIBLE

    def test_snapshot_only_partially_reversible(self):
        ar = ActionReversibility()
        result = ar.classify("action1", has_rollback=False, has_snapshot=True)
        assert result == Reversibility.PARTIALLY_REVERSIBLE

    def test_neither_irreversible(self):
        ar = ActionReversibility()
        result = ar.classify("action1", has_rollback=False, has_snapshot=False)
        assert result == Reversibility.IRREVERSIBLE


class TestGate:
    def test_irreversible_low_autonomy_blocks(self):
        ar = ActionReversibility()
        result = ar.gate("delete_prod", Reversibility.IRREVERSIBLE, autonomy_level=2)
        assert result is False
        assert "delete_prod" in ar.blocked_actions

    def test_irreversible_high_autonomy_passes(self):
        ar = ActionReversibility()
        result = ar.gate("delete_prod", Reversibility.IRREVERSIBLE, autonomy_level=3)
        assert result is True

    def test_fully_reversible_passes(self):
        ar = ActionReversibility()
        result = ar.gate("safe_action", Reversibility.FULLY_REVERSIBLE, autonomy_level=0)
        assert result is True

    def test_partially_reversible_passes(self):
        ar = ActionReversibility()
        result = ar.gate("partial_action", Reversibility.PARTIALLY_REVERSIBLE, autonomy_level=1)
        assert result is True

    def test_blocked_actions_accumulate(self):
        ar = ActionReversibility()
        ar.gate("action1", Reversibility.IRREVERSIBLE, autonomy_level=0)
        ar.gate("action2", Reversibility.IRREVERSIBLE, autonomy_level=1)
        assert len(ar.blocked_actions) == 2
