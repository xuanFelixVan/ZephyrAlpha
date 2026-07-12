# [A_test] module_id: SRC-TST-1346 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_oscillation_damping
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.resilience.oscillation_damping
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_oscillation_damping.py
# [TTL] task_bound


from zephyr.feedback_loop.resilience.oscillation_damping import (
    DampingState,
    OscillationDamping,
)


class TestOscillationDampingInstantiation:
    def test_default_instantiation(self):
        od = OscillationDamping()
        assert od.cooldown_seconds == 60.0
        assert od.max_reversals == 3
        assert od.reversal_window == 60.0
        assert od.state == DampingState.STABLE
        assert od.last_action_type == ""
        assert od.reversal_count == 0
        assert od.reversal_history == []
        assert od.cooldown_until == 0.0

    def test_custom_instantiation(self):
        od = OscillationDamping(cooldown_seconds=30.0, max_reversals=5)
        assert od.cooldown_seconds == 30.0
        assert od.max_reversals == 5


class TestRecordAction:
    def test_first_action_is_stable(self):
        od = OscillationDamping()
        state = od.record_action("scale_up")
        assert state == DampingState.STABLE

    def test_same_action_no_reversal(self):
        od = OscillationDamping()
        od.record_action("scale_up")
        state = od.record_action("scale_up")
        assert state == DampingState.STABLE

    def test_reversal_triggers_damping(self):
        od = OscillationDamping()
        od.record_action("scale_up")
        state = od.record_action("scale_down")
        assert state == DampingState.DAMPING

    def test_max_reversals_triggers_cooldown(self):
        od = OscillationDamping(max_reversals=2)
        od.record_action("scale_up")
        od.record_action("scale_down")
        state = od.record_action("scale_up")
        assert state == DampingState.COOLDOWN


class TestIsAllowed:
    def test_allowed_when_stable(self):
        od = OscillationDamping()
        assert od.is_allowed() is True

    def test_not_allowed_in_cooldown(self):
        od = OscillationDamping(cooldown_seconds=9999.0, max_reversals=2)
        od.record_action("up")
        od.record_action("down")
        od.record_action("up")
        assert od.is_allowed() is False


class TestRemainingCooldown:
    def test_zero_when_not_in_cooldown(self):
        od = OscillationDamping()
        assert od.remaining_cooldown() == 0.0

    def test_positive_in_cooldown(self):
        od = OscillationDamping(cooldown_seconds=9999.0, max_reversals=2)
        od.record_action("up")
        od.record_action("down")
        od.record_action("up")
        assert od.remaining_cooldown() > 0
