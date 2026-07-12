# [A_test] module_id: SRC-TST-0902 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_feedback_delay_compensator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.feedback_delay_compensator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_feedback_delay_compensator.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.feedback_delay_compensator import (
    DelayState,
    FeedbackDelayCompensator,
)


class TestDelayStateEnum:
    def test_idle_value(self):
        assert DelayState.IDLE.value == "IDLE"

    def test_waiting_value(self):
        assert DelayState.WAITING.value == "WAITING"

    def test_evaluating_value(self):
        assert DelayState.EVALUATING.value == "EVALUATING"

    def test_all_states_count(self):
        assert len(DelayState) == 3


class TestFeedbackDelayCompensatorInstantiation:
    def test_default_params(self):
        comp = FeedbackDelayCompensator()
        assert comp.default_delay == 300.0
        assert comp.max_delay == 86400.0
        assert comp.action_delay_map == {}
        assert comp.pending_actions == {}
        assert comp.delay_violations == []

    def test_custom_params(self):
        comp = FeedbackDelayCompensator(default_delay=60.0, max_delay=3600.0)
        assert comp.default_delay == 60.0
        assert comp.max_delay == 3600.0


class TestRegisterActionDelay:
    def test_register_new_action_type(self):
        comp = FeedbackDelayCompensator()
        comp.register_action_delay("config_change", 120.0)
        assert comp.action_delay_map["config_change"] == 120.0

    def test_register_capped_by_max_delay(self):
        comp = FeedbackDelayCompensator(max_delay=100.0)
        comp.register_action_delay("slow_action", 500.0)
        assert comp.action_delay_map["slow_action"] == 100.0

    def test_register_overwrites_existing(self):
        comp = FeedbackDelayCompensator()
        comp.register_action_delay("config_change", 120.0)
        comp.register_action_delay("config_change", 240.0)
        assert comp.action_delay_map["config_change"] == 240.0


class TestDispatchWithDelay:
    def test_dispatch_creates_pending_action(self):
        comp = FeedbackDelayCompensator()
        comp.register_action_delay("config_change", 120.0)
        result = comp.dispatch_with_delay("act-1", "config_change", "cpu_util", 80.0)
        assert "act-1" in comp.pending_actions
        assert result["action_id"] == "act-1"
        assert result["delay_seconds"] == 120.0

    def test_dispatch_uses_default_delay_for_unknown_type(self):
        comp = FeedbackDelayCompensator(default_delay=60.0)
        result = comp.dispatch_with_delay("act-2", "unknown_type", "mem_util", 50.0)
        assert result["delay_seconds"] == 60.0

    def test_dispatch_sets_waiting_state(self):
        comp = FeedbackDelayCompensator()
        comp.dispatch_with_delay("act-1", "type_a", "cpu", 80.0)
        assert comp.pending_actions["act-1"]["state"] == DelayState.WAITING

    def test_dispatch_returns_suppress_instruction(self):
        comp = FeedbackDelayCompensator()
        result = comp.dispatch_with_delay("act-1", "type_a", "cpu", 80.0)
        assert "suppress_cpu_anomalies" in result["instruction"]


class TestShouldSuppress:
    def test_suppress_during_delay_window(self):
        comp = FeedbackDelayCompensator()
        comp.register_action_delay("config_change", 300.0)
        comp.dispatch_with_delay("act-1", "config_change", "cpu_util", 80.0)
        result = comp.should_suppress("cpu_util")
        assert result["suppress"] is True
        assert result["action_id"] == "act-1"

    def test_no_suppress_for_unrelated_metric(self):
        comp = FeedbackDelayCompensator()
        comp.dispatch_with_delay("act-1", "type_a", "cpu_util", 80.0)
        result = comp.should_suppress("mem_util")
        assert result["suppress"] is False

    def test_no_suppress_when_no_pending(self):
        comp = FeedbackDelayCompensator()
        result = comp.should_suppress("cpu_util")
        assert result["suppress"] is False


class TestEvaluateDelayedOutcome:
    def test_unknown_action_returns_error(self):
        comp = FeedbackDelayCompensator()
        result = comp.evaluate_delayed_outcome("nonexistent", 50.0)
        assert result["error"] == "unknown_action"

    def test_effective_action_positive_delta(self):
        comp = FeedbackDelayCompensator()
        comp.dispatch_with_delay("act-1", "type_a", "cpu", -10.0)
        result = comp.evaluate_delayed_outcome("act-1", -5.0)
        assert result["effective"] is True
        assert result["recommendation"] == "update_delay_estimate"

    def test_ineffective_action_records_violation(self):
        comp = FeedbackDelayCompensator()
        comp.dispatch_with_delay("act-1", "type_a", "cpu", 100.0)
        result = comp.evaluate_delayed_outcome("act-1", 120.0)
        if not result["effective"] and abs(result["delta"]) > abs(result["pre_value"]) * 0.1:
            assert len(comp.delay_violations) == 1

    def test_evaluated_action_set_to_idle(self):
        comp = FeedbackDelayCompensator()
        comp.dispatch_with_delay("act-1", "type_a", "cpu", 50.0)
        comp.evaluate_delayed_outcome("act-1", 45.0)
        assert comp.pending_actions["act-1"]["state"] == DelayState.IDLE


class TestCleanupCompleted:
    def test_removes_idle_actions(self):
        comp = FeedbackDelayCompensator()
        comp.dispatch_with_delay("act-1", "type_a", "cpu", 50.0)
        comp.evaluate_delayed_outcome("act-1", 45.0)
        removed = comp.cleanup_completed()
        assert removed == 1
        assert "act-1" not in comp.pending_actions

    def test_keeps_waiting_actions(self):
        comp = FeedbackDelayCompensator()
        comp.register_action_delay("config_change", 300.0)
        comp.dispatch_with_delay("act-1", "config_change", "cpu", 50.0)
        removed = comp.cleanup_completed()
        assert removed == 0
        assert "act-1" in comp.pending_actions

    def test_empty_pending_returns_zero(self):
        comp = FeedbackDelayCompensator()
        removed = comp.cleanup_completed()
        assert removed == 0


class TestGetPendingSummary:
    def test_empty_pending(self):
        comp = FeedbackDelayCompensator()
        assert comp.get_pending_summary() == []

    def test_waiting_actions_listed(self):
        comp = FeedbackDelayCompensator()
        comp.register_action_delay("config_change", 300.0)
        comp.dispatch_with_delay("act-1", "config_change", "cpu", 50.0)
        summary = comp.get_pending_summary()
        assert len(summary) == 1
        assert summary[0]["id"] == "act-1"
        assert summary[0]["target"] == "cpu"

    def test_idle_actions_not_listed(self):
        comp = FeedbackDelayCompensator()
        comp.dispatch_with_delay("act-1", "type_a", "cpu", 50.0)
        comp.evaluate_delayed_outcome("act-1", 45.0)
        summary = comp.get_pending_summary()
        assert len(summary) == 0
