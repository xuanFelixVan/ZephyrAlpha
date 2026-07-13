# [A_test] module_id: SRC-TST-1389 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_positive_feedback_defense
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_positive_feedback_defense.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.guard.positive_feedback_defense import PositiveFeedbackDefense


class TestPositiveFeedbackDefense:
    def test_default_construction(self):
        det = PositiveFeedbackDefense()
        assert det.recent_actions == []

    def test_detect_loop_no_loop(self):
        det = PositiveFeedbackDefense()
        assert det.detect_loop("action_A") is False
        assert det.detect_loop("action_B") is False

    def test_detect_loop_triggers_on_repetition(self):
        det = PositiveFeedbackDefense()
        det.detect_loop("action_A")
        det.detect_loop("action_A")
        result = det.detect_loop("action_A")
        assert result is True

    def test_detect_loop_sliding_window(self):
        det = PositiveFeedbackDefense()
        for _ in range(10):
            det.detect_loop("other")
        det.detect_loop("action_A")
        det.detect_loop("action_A")
        result = det.detect_loop("action_A")
        assert result is True

    def test_detect_loop_window_evicts_old(self):
        det = PositiveFeedbackDefense()
        det.detect_loop("action_A")
        det.detect_loop("action_A")
        for _ in range(10):
            det.detect_loop("other")
        result = det.detect_loop("action_A")
        assert result is False

    def test_detect_loop_mixed_actions(self):
        det = PositiveFeedbackDefense()
        det.detect_loop("action_A")
        det.detect_loop("action_B")
        det.detect_loop("action_A")
        result = det.detect_loop("action_A")
        assert result is True

    def test_detect_loop_empty_string_action(self):
        det = PositiveFeedbackDefense()
        det.detect_loop("")
        det.detect_loop("")
        result = det.detect_loop("")
        assert result is True

    def test_detect_loop_preserves_recent_list_size(self):
        det = PositiveFeedbackDefense()
        for i in range(15):
            det.detect_loop(f"action_{i}")
        assert len(det.recent_actions) <= 10
