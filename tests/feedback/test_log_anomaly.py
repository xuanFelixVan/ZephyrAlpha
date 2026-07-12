# [A_test] module_id: SRC-TST-1241 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_log_anomaly
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_log_anomaly.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.log_anomaly import LogAnomaly


class TestLogAnomaly:
    def test_default_construction(self):
        det = LogAnomaly()
        assert det.error_rate_threshold == 0.05

    def test_custom_construction(self):
        det = LogAnomaly(error_rate_threshold=0.1)
        assert det.error_rate_threshold == 0.1

    def test_check_below_threshold(self):
        det = LogAnomaly(error_rate_threshold=0.05)
        assert det.check(0.03) is False

    def test_check_above_threshold(self):
        det = LogAnomaly(error_rate_threshold=0.05)
        assert det.check(0.10) is True

    def test_check_at_threshold(self):
        det = LogAnomaly(error_rate_threshold=0.05)
        assert det.check(0.05) is False

    def test_check_zero_error_rate(self):
        det = LogAnomaly(error_rate_threshold=0.05)
        assert det.check(0.0) is False

    def test_check_full_error_rate(self):
        det = LogAnomaly(error_rate_threshold=0.05)
        assert det.check(1.0) is True

    def test_check_very_small_threshold(self):
        det = LogAnomaly(error_rate_threshold=0.001)
        assert det.check(0.002) is True
        assert det.check(0.0005) is False

    def test_check_boundary_just_above(self):
        det = LogAnomaly(error_rate_threshold=0.05)
        assert det.check(0.0501) is True
