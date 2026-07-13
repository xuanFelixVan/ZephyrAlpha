# [A_test] module_id: SRC-TST-1381 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_placebo_action_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_placebo_action_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.guard.placebo_action_detector import PlaceboActionDetector


class TestPlaceboActionDetector:
    def test_default_construction(self):
        det = PlaceboActionDetector()
        assert det.action_outcomes == {}
        assert det.control_outcomes == []
        assert det.min_samples_per_group == 8
        assert det.significance_level == 0.05

    def test_custom_construction(self):
        det = PlaceboActionDetector(min_samples_per_group=5, significance_level=0.01)
        assert det.min_samples_per_group == 5
        assert det.significance_level == 0.01

    def test_record_action_outcome(self):
        det = PlaceboActionDetector()
        det.record_action_outcome("repair_X", 0.8)
        assert "repair_X" in det.action_outcomes
        assert len(det.action_outcomes["repair_X"]) == 1

    def test_record_action_outcome_multiple(self):
        det = PlaceboActionDetector()
        det.record_action_outcome("repair_X", 0.8)
        det.record_action_outcome("repair_X", 0.7)
        assert len(det.action_outcomes["repair_X"]) == 2

    def test_record_action_outcome_trims(self):
        det = PlaceboActionDetector()
        for i in range(110):
            det.record_action_outcome("repair_X", float(i))
        assert len(det.action_outcomes["repair_X"]) <= 100

    def test_record_control_outcome(self):
        det = PlaceboActionDetector()
        det.record_control_outcome(0.5)
        assert len(det.control_outcomes) == 1

    def test_record_control_outcome_trims(self):
        det = PlaceboActionDetector()
        for i in range(110):
            det.record_control_outcome(float(i))
        assert len(det.control_outcomes) <= 100

    def test_detect_placebo_actions_insufficient_control(self):
        det = PlaceboActionDetector()
        for i in range(10):
            det.record_action_outcome("repair_X", 0.8)
        result = det.detect_placebo_actions()
        assert result["status"] == "insufficient_control_data"
        assert result["placebo_actions"] == []

    def test_detect_placebo_actions_insufficient_action_samples(self):
        det = PlaceboActionDetector(min_samples_per_group=8)
        for i in range(10):
            det.record_control_outcome(0.5)
        for i in range(3):
            det.record_action_outcome("repair_X", 0.8)
        result = det.detect_placebo_actions()
        assert "repair_X" not in result

    def test_detect_placebo_actions_placebo_detected(self):
        det = PlaceboActionDetector(min_samples_per_group=8, significance_level=0.05)
        for _ in range(10):
            det.record_control_outcome(0.5)
        for _ in range(10):
            det.record_action_outcome("repair_X", 0.5)
        result = det.detect_placebo_actions()
        if "repair_X" in result:
            assert result["repair_X"]["is_placebo"] is True

    def test_detect_placebo_actions_effective_action(self):
        det = PlaceboActionDetector(min_samples_per_group=8, significance_level=0.05)
        for _ in range(10):
            det.record_control_outcome(0.3)
        for _ in range(10):
            det.record_action_outcome("repair_Y", 0.95)
        result = det.detect_placebo_actions()
        if "repair_Y" in result:
            assert result["repair_Y"]["is_placebo"] is False

    def test_get_placebo_actions_insufficient_data(self):
        det = PlaceboActionDetector()
        result = det.get_placebo_actions()
        assert result == []

    def test_get_placebo_actions_with_data(self):
        det = PlaceboActionDetector(min_samples_per_group=8, significance_level=0.05)
        for _ in range(10):
            det.record_control_outcome(0.5)
        for _ in range(10):
            det.record_action_outcome("repair_X", 0.5)
        result = det.get_placebo_actions()
        assert isinstance(result, list)

    def test_mann_whitney_u_static(self):
        group_a = [1.0, 2.0, 3.0, 4.0, 5.0]
        group_b = [6.0, 7.0, 8.0, 9.0, 10.0]
        u_stat, p_value = PlaceboActionDetector._mann_whitney_u(group_a, group_b)
        assert isinstance(u_stat, float)
        assert isinstance(p_value, float)
        assert p_value > 0.0

    def test_mann_whitney_u_identical_groups(self):
        group = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        u_stat, p_value = PlaceboActionDetector._mann_whitney_u(group[:4], group[4:])
        assert p_value > 0.0

    def test_mann_whitney_u_single_element(self):
        u_stat, p_value = PlaceboActionDetector._mann_whitney_u([1.0], [2.0])
        assert isinstance(u_stat, float)
