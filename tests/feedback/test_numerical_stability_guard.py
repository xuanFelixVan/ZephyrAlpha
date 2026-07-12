# [A_test] module_id: SRC-TST-1317 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_numerical_stability_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.numerical_stability_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_numerical_stability_guard.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.numerical_stability_guard import (
    NumAnomaly,
    NumericalStabilityGuard,
)


class TestNumAnomaly:
    def test_clean_value(self):
        assert NumAnomaly.CLEAN.value == "CLEAN"

    def test_nan_value(self):
        assert NumAnomaly.NAN.value == "NAN"

    def test_pos_inf_value(self):
        assert NumAnomaly.POS_INF.value == "POS_INF"

    def test_neg_inf_value(self):
        assert NumAnomaly.NEG_INF.value == "NEG_INF"

    def test_subnormal_value(self):
        assert NumAnomaly.SUBNORMAL.value == "SUBNORMAL"

    def test_overflow_suspect_value(self):
        assert NumAnomaly.OVERFLOW_SUSPECT.value == "OVERFLOW_SUSPECT"

    def test_zero_division_value(self):
        assert NumAnomaly.ZERO_DIVISION.value == "ZERO_DIVISION"

    def test_all_anomalies_count(self):
        assert len(NumAnomaly) == 7


class TestNumericalStabilityGuardInstantiation:
    def test_default_instantiation(self):
        nsg = NumericalStabilityGuard()
        assert nsg.nan_threshold_ratio == 0.01
        assert nsg.inf_sentinel == 1e308
        assert nsg.max_safe_float == 1e154
        assert nsg.quarantine == {}
        assert nsg.health_scores == {}
        assert nsg.total_checks == {}
        assert nsg.anomaly_counts == {}

    def test_custom_instantiation(self):
        nsg = NumericalStabilityGuard(nan_threshold_ratio=0.05, inf_sentinel=1e100, max_safe_float=1e50)
        assert nsg.nan_threshold_ratio == 0.05
        assert nsg.inf_sentinel == 1e100


class TestValidate:
    def test_clean_value(self):
        nsg = NumericalStabilityGuard()
        result = nsg.validate("cpu_pct", 75.5)
        assert result["classification"] == NumAnomaly.CLEAN.value
        assert result["sanitized"] == 75.5

    def test_nan_value(self):
        nsg = NumericalStabilityGuard()
        result = nsg.validate("cpu_pct", float("nan"))
        assert result["classification"] == NumAnomaly.NAN.value
        assert result["sanitized"] == 0.0

    def test_pos_inf_value(self):
        nsg = NumericalStabilityGuard()
        result = nsg.validate("cpu_pct", float("inf"))
        assert result["classification"] == NumAnomaly.POS_INF.value
        assert result["sanitized"] == nsg.inf_sentinel

    def test_neg_inf_value(self):
        nsg = NumericalStabilityGuard()
        result = nsg.validate("cpu_pct", float("-inf"))
        assert result["classification"] == NumAnomaly.NEG_INF.value
        assert result["sanitized"] == -nsg.inf_sentinel

    def test_overflow_suspect(self):
        nsg = NumericalStabilityGuard(max_safe_float=1e10)
        result = nsg.validate("big_val", 1e20)
        assert result["classification"] == NumAnomaly.OVERFLOW_SUSPECT.value

    def test_subnormal_value(self):
        nsg = NumericalStabilityGuard()
        result = nsg.validate("tiny_val", 1e-310)
        assert result["classification"] == NumAnomaly.SUBNORMAL.value
        assert result["sanitized"] == 0.0

    def test_zero_is_clean(self):
        nsg = NumericalStabilityGuard()
        result = nsg.validate("zero_val", 0.0)
        assert result["classification"] == NumAnomaly.CLEAN.value

    def test_validate_increments_total_checks(self):
        nsg = NumericalStabilityGuard()
        nsg.validate("m1", 1.0)
        nsg.validate("m1", 2.0)
        assert nsg.total_checks["m1"] == 2

    def test_validate_nan_quarantined(self):
        nsg = NumericalStabilityGuard()
        nsg.validate("m1", float("nan"))
        assert "m1" in nsg.quarantine
        assert len(nsg.quarantine["m1"]) == 1

    def test_validate_returns_health_score(self):
        nsg = NumericalStabilityGuard()
        result = nsg.validate("m1", 1.0)
        assert "health_score" in result
        assert result["health_score"] == 1.0

    def test_validate_negative_clean(self):
        nsg = NumericalStabilityGuard()
        result = nsg.validate("m1", -42.5)
        assert result["classification"] == NumAnomaly.CLEAN.value


class TestIsStreamHealthy:
    def test_healthy_stream(self):
        nsg = NumericalStabilityGuard()
        nsg.validate("m1", 1.0)
        assert nsg.is_stream_healthy("m1") is True

    def test_unhealthy_after_nan(self):
        nsg = NumericalStabilityGuard()
        for _ in range(5):
            nsg.validate("m1", float("nan"))
        assert nsg.is_stream_healthy("m1") is False

    def test_unknown_metric_is_healthy(self):
        nsg = NumericalStabilityGuard()
        assert nsg.is_stream_healthy("nonexistent") is True


class TestResetMetric:
    def test_reset_removes_all_tracking(self):
        nsg = NumericalStabilityGuard()
        nsg.validate("m1", float("nan"))
        nsg.validate("m1", 1.0)
        nsg.reset_metric("m1")
        assert "m1" not in nsg.quarantine
        assert "m1" not in nsg.total_checks
        assert "m1" not in nsg.anomaly_counts
        assert "m1" not in nsg.health_scores

    def test_reset_nonexistent_metric_no_error(self):
        nsg = NumericalStabilityGuard()
        nsg.reset_metric("no_such_metric")

    def test_reset_then_revalidate(self):
        nsg = NumericalStabilityGuard()
        nsg.validate("m1", float("nan"))
        nsg.reset_metric("m1")
        result = nsg.validate("m1", 1.0)
        assert result["classification"] == NumAnomaly.CLEAN.value


class TestGetQuarantineSummary:
    def test_empty_summary(self):
        nsg = NumericalStabilityGuard()
        assert nsg.get_quarantine_summary() == {}

    def test_summary_with_data(self):
        nsg = NumericalStabilityGuard()
        nsg.validate("m1", 1.0)
        nsg.validate("m1", float("nan"))
        summary = nsg.get_quarantine_summary()
        assert "m1" in summary
        assert summary["m1"]["total_checks"] == 2
        assert "anomaly_counts" in summary["m1"]
        assert "health_score" in summary["m1"]

    def test_summary_multiple_metrics(self):
        nsg = NumericalStabilityGuard()
        nsg.validate("m1", 1.0)
        nsg.validate("m2", float("inf"))
        summary = nsg.get_quarantine_summary()
        assert "m1" in summary
        assert "m2" in summary
