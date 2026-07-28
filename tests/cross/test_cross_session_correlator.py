# [A_test] module_id: MOD-GOV_cross_session_correlator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_cross_session_correlator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_cross_session_correlator.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.services.cross_session_correlator import CrossSessionCorrelator


class TestCrossSessionCorrelatorInstantiation:
    def test_creates_instance_without_args(self):
        corr = CrossSessionCorrelator()
        assert isinstance(corr, CrossSessionCorrelator)

    def test_initial_sessions_empty(self):
        corr = CrossSessionCorrelator()
        assert corr.sessions == {}


class TestRegisterSession:
    def test_register_single_session(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {"cpu": 50, "mem": 60})
        assert "s1" in corr.sessions
        assert corr.sessions["s1"] == {"cpu": 50, "mem": 60}

    def test_register_multiple_sessions(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {"cpu": 50})
        corr.register_session("s2", {"cpu": 60})
        assert len(corr.sessions) == 2

    def test_register_overwrites_existing_session(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {"cpu": 50})
        corr.register_session("s1", {"cpu": 90})
        assert corr.sessions["s1"] == {"cpu": 90}

    def test_register_empty_metrics(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {})
        assert corr.sessions["s1"] == {}


class TestDetectAnomalousSession:
    def test_returns_false_with_fewer_than_three_sessions(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {"cpu": 50})
        corr.register_session("s2", {"cpu": 60})
        result = corr.detect_anomalous_session({"cpu": 999})
        assert result is False

    def test_returns_false_with_zero_sessions(self):
        corr = CrossSessionCorrelator()
        result = corr.detect_anomalous_session({"cpu": 999})
        assert result is False

    def test_detects_anomalous_high_value(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {"cpu": 50})
        corr.register_session("s2", {"cpu": 55})
        corr.register_session("s3", {"cpu": 52})
        result = corr.detect_anomalous_session({"cpu": 200})
        assert result is True

    def test_normal_value_not_flagged(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {"cpu": 50})
        corr.register_session("s2", {"cpu": 55})
        corr.register_session("s3", {"cpu": 52})
        result = corr.detect_anomalous_session({"cpu": 54})
        assert result is False

    def test_custom_threshold(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {"cpu": 50})
        corr.register_session("s2", {"cpu": 55})
        corr.register_session("s3", {"cpu": 52})
        result_strict = corr.detect_anomalous_session({"cpu": 80}, std_dev_threshold=0.5)
        result_lenient = corr.detect_anomalous_session({"cpu": 80}, std_dev_threshold=5.0)
        assert result_strict is True
        assert result_lenient is False

    def test_zero_mean_metric_not_flagged(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {"errors": 0})
        corr.register_session("s2", {"errors": 0})
        corr.register_session("s3", {"errors": 0})
        result = corr.detect_anomalous_session({"errors": 100})
        assert result is False

    def test_boundary_exactly_at_threshold(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {"cpu": 100})
        corr.register_session("s2", {"cpu": 100})
        corr.register_session("s3", {"cpu": 100})
        result = corr.detect_anomalous_session({"cpu": 300}, std_dev_threshold=2.0)
        assert result is False

    def test_boundary_just_above_threshold(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {"cpu": 100})
        corr.register_session("s2", {"cpu": 100})
        corr.register_session("s3", {"cpu": 100})
        result = corr.detect_anomalous_session({"cpu": 301}, std_dev_threshold=2.0)
        assert result is True

    def test_multiple_metrics_anomaly_in_one(self):
        corr = CrossSessionCorrelator()
        corr.register_session("s1", {"cpu": 50, "mem": 60})
        corr.register_session("s2", {"cpu": 55, "mem": 65})
        corr.register_session("s3", {"cpu": 52, "mem": 62})
        result = corr.detect_anomalous_session({"cpu": 53, "mem": 200})
        assert result is True
