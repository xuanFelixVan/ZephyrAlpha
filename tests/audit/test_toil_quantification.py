# [A_test] module_id: SRC-TST-1748 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_toil_quantification
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.reliability.toil_quantification
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_toil_quantification.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.reliability.toil_quantification import (
    ActionClass,
    ToilQuantification,
)


class TestActionClass:
    def test_fully_automated_value(self):
        assert ActionClass.FULLY_AUTOMATED.value == "FULLY_AUTOMATED"

    def test_semi_automated_value(self):
        assert ActionClass.SEMI_AUTOMATED.value == "SEMI_AUTOMATED"

    def test_manual_required_value(self):
        assert ActionClass.MANUAL_REQUIRED.value == "MANUAL_REQUIRED"

    def test_all_classes_count(self):
        assert len(ActionClass) == 3


class TestToilQuantificationInstantiation:
    def test_default_params(self):
        tq = ToilQuantification()
        assert tq.toil_threshold == 0.2
        assert tq.window_days == 7
        assert tq.action_history == []
        assert tq.total_actions == 0
        assert tq.manual_actions == 0
        assert tq.current_toil_ratio == 0.0

    def test_custom_params(self):
        tq = ToilQuantification(toil_threshold=0.3, window_days=14)
        assert tq.toil_threshold == 0.3
        assert tq.window_days == 14


class TestRecordAction:
    def test_automated_action_zero_toil(self):
        tq = ToilQuantification()
        ratio = tq.record_action(ActionClass.FULLY_AUTOMATED)
        assert ratio == 0.0

    def test_manual_action_increments_toil(self):
        tq = ToilQuantification()
        ratio = tq.record_action(ActionClass.MANUAL_REQUIRED)
        assert ratio == 1.0

    def test_mixed_actions_ratio(self):
        tq = ToilQuantification()
        tq.record_action(ActionClass.FULLY_AUTOMATED)
        tq.record_action(ActionClass.FULLY_AUTOMATED)
        tq.record_action(ActionClass.MANUAL_REQUIRED)
        ratio = tq.record_action(ActionClass.FULLY_AUTOMATED)
        assert 0.0 < ratio < 1.0

    def test_total_actions_incremented(self):
        tq = ToilQuantification()
        tq.record_action(ActionClass.FULLY_AUTOMATED)
        tq.record_action(ActionClass.SEMI_AUTOMATED)
        assert tq.total_actions == 2

    def test_manual_actions_only_manual(self):
        tq = ToilQuantification()
        tq.record_action(ActionClass.FULLY_AUTOMATED)
        tq.record_action(ActionClass.SEMI_AUTOMATED)
        assert tq.manual_actions == 0

    def test_returns_float(self):
        tq = ToilQuantification()
        result = tq.record_action(ActionClass.FULLY_AUTOMATED)
        assert isinstance(result, float)


class TestIsToilExcessive:
    def test_no_actions_not_excessive(self):
        tq = ToilQuantification()
        assert tq.is_toil_excessive() is False

    def test_all_automated_not_excessive(self):
        tq = ToilQuantification()
        for _ in range(10):
            tq.record_action(ActionClass.FULLY_AUTOMATED)
        assert tq.is_toil_excessive() is False

    def test_high_manual_excessive(self):
        tq = ToilQuantification(toil_threshold=0.2)
        for _ in range(8):
            tq.record_action(ActionClass.MANUAL_REQUIRED)
        for _ in range(2):
            tq.record_action(ActionClass.FULLY_AUTOMATED)
        assert tq.is_toil_excessive() is True

    def test_threshold_boundary(self):
        tq = ToilQuantification(toil_threshold=0.5)
        tq.record_action(ActionClass.MANUAL_REQUIRED)
        tq.record_action(ActionClass.FULLY_AUTOMATED)
        assert tq.is_toil_excessive() is False


class TestGetTopToilSources:
    def test_no_manual_actions_empty(self):
        tq = ToilQuantification()
        for _ in range(5):
            tq.record_action(ActionClass.FULLY_AUTOMATED)
        sources = tq.get_top_toil_sources()
        assert sources == []

    def test_manual_actions_with_source(self):
        tq = ToilQuantification()
        tq.action_history.append({"ts": 1.0, "class": ActionClass.MANUAL_REQUIRED.value, "source": "deploy"})
        tq.action_history.append({"ts": 2.0, "class": ActionClass.MANUAL_REQUIRED.value, "source": "deploy"})
        tq.action_history.append({"ts": 3.0, "class": ActionClass.MANUAL_REQUIRED.value, "source": "restart"})
        sources = tq.get_top_toil_sources()
        assert len(sources) >= 1
        assert sources[0]["source"] == "deploy"

    def test_top_n_limit(self):
        tq = ToilQuantification()
        for i in range(10):
            tq.action_history.append(
                {
                    "ts": float(i),
                    "class": ActionClass.MANUAL_REQUIRED.value,
                    "source": f"src-{i}",
                }
            )
        sources = tq.get_top_toil_sources(top_n=3)
        assert len(sources) <= 3
