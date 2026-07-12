# [A_test] module_id: SRC-TST-0926 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_action_reversibility
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.action_reversibility
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_action_reversibility.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.action_reversibility import ActionReversibility, Reversibility


class TestActionReversibilityInstantiation:
    def test_default_construction(self):
        ar = ActionReversibility()
        assert ar.blocked_actions == []

    def test_custom_blocked_actions(self):
        ar = ActionReversibility(blocked_actions=["DELETE_PROD"])
        assert "DELETE_PROD" in ar.blocked_actions


class TestClassify:
    def test_fully_reversible_when_snapshot_and_rollback(self):
        ar = ActionReversibility()
        result = ar.classify("action_a", has_rollback=True, has_snapshot=True)
        assert result == Reversibility.FULLY_REVERSIBLE

    def test_partially_reversible_when_rollback_only(self):
        ar = ActionReversibility()
        result = ar.classify("action_b", has_rollback=True, has_snapshot=False)
        assert result == Reversibility.PARTIALLY_REVERSIBLE

    def test_partially_reversible_when_snapshot_only(self):
        ar = ActionReversibility()
        result = ar.classify("action_c", has_rollback=False, has_snapshot=True)
        assert result == Reversibility.PARTIALLY_REVERSIBLE

    def test_irreversible_when_neither(self):
        ar = ActionReversibility()
        result = ar.classify("action_d", has_rollback=False, has_snapshot=False)
        assert result == Reversibility.IRREVERSIBLE


class TestGate:
    def test_gate_allows_reversible_action(self):
        ar = ActionReversibility()
        assert ar.gate("action_a", Reversibility.FULLY_REVERSIBLE, autonomy_level=0) is True

    def test_gate_blocks_irreversible_at_low_autonomy(self):
        ar = ActionReversibility()
        assert ar.gate("DELETE_PROD", Reversibility.IRREVERSIBLE, autonomy_level=2) is False
        assert "DELETE_PROD" in ar.blocked_actions

    def test_gate_allows_irreversible_at_high_autonomy(self):
        ar = ActionReversibility()
        assert ar.gate("DELETE_PROD", Reversibility.IRREVERSIBLE, autonomy_level=3) is True

    def test_gate_partially_reversible_always_allowed(self):
        ar = ActionReversibility()
        assert ar.gate("action_x", Reversibility.PARTIALLY_REVERSIBLE, autonomy_level=0) is True


class TestBoundaries:
    def test_classify_empty_action_string(self):
        ar = ActionReversibility()
        result = ar.classify("", has_rollback=False, has_snapshot=False)
        assert result == Reversibility.IRREVERSIBLE

    def test_gate_autonomy_level_boundary(self):
        ar = ActionReversibility()
        assert ar.gate("a", Reversibility.IRREVERSIBLE, autonomy_level=2) is False
        assert ar.gate("b", Reversibility.IRREVERSIBLE, autonomy_level=3) is True
