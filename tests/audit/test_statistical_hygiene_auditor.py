# [A_test] module_id: SRC-TST-1688 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_statistical_hygiene_auditor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.diagnosis.statistical_hygiene_auditor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_statistical_hygiene_auditor.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.diagnosis.statistical_hygiene_auditor import (
    StatisticalHygieneAuditor,
    StatViolation,
)


class TestStatViolation:
    def test_p_hacking_value(self):
        assert StatViolation.P_HACKING.value == "P_HACKING"

    def test_multiple_comparisons_value(self):
        assert StatViolation.MULTIPLE_COMPARISONS.value == "MULTIPLE_COMPARISONS"

    def test_survivorship_bias_value(self):
        assert StatViolation.SURVIVORSHIP_BIAS.value == "SURVIVORSHIP_BIAS"

    def test_small_sample_value(self):
        assert StatViolation.SMALL_SAMPLE.value == "SMALL_SAMPLE"

    def test_all_violations_count(self):
        assert len(StatViolation) == 6


class TestStatisticalHygieneAuditorInstantiation:
    def test_default_params(self):
        sha = StatisticalHygieneAuditor()
        assert sha.min_sample_size == 30
        assert sha.max_threshold_attempts == 5
        assert sha.bonferroni_active_metrics == 1
        assert sha.replication_required is True
        assert sha.threshold_attempts == {}
        assert sha.active_metrics_count == 0
        assert sha.violations == []
        assert sha.confirmed_anomalies == {}
        assert sha.unconfirmed_anomalies == {}

    def test_custom_params(self):
        sha = StatisticalHygieneAuditor(
            min_sample_size=50,
            max_threshold_attempts=3,
            bonferroni_active_metrics=5,
            replication_required=False,
        )
        assert sha.min_sample_size == 50
        assert sha.max_threshold_attempts == 3
        assert sha.bonferroni_active_metrics == 5
        assert sha.replication_required is False


class TestSetActiveMetrics:
    def test_low_count_ok(self):
        sha = StatisticalHygieneAuditor()
        result = sha.set_active_metrics(10)
        assert result["ok"] is True

    def test_high_count_triggers_violation(self):
        sha = StatisticalHygieneAuditor()
        result = sha.set_active_metrics(25)
        assert "violation" in result
        assert result["violation"] == StatViolation.MULTIPLE_COMPARISONS.value

    def test_bonferroni_alpha_returned(self):
        sha = StatisticalHygieneAuditor()
        result = sha.set_active_metrics(5)
        assert "bonferroni_alpha" in result
        assert result["bonferroni_alpha"] == round(0.05 / 5, 5)

    def test_zero_metrics(self):
        sha = StatisticalHygieneAuditor()
        result = sha.set_active_metrics(0)
        assert result["ok"] is True


class TestRecordThresholdAttempt:
    def test_within_limit_ok(self):
        sha = StatisticalHygieneAuditor(max_threshold_attempts=5)
        for _ in range(5):
            result = sha.record_threshold_attempt("metric_a")
        assert result["ok"] is True

    def test_exceeds_limit_triggers_p_hacking(self):
        sha = StatisticalHygieneAuditor(max_threshold_attempts=3)
        for _ in range(3):
            sha.record_threshold_attempt("metric_b")
        result = sha.record_threshold_attempt("metric_b")
        assert result["violation"] == StatViolation.P_HACKING.value

    def test_independent_metrics(self):
        sha = StatisticalHygieneAuditor(max_threshold_attempts=2)
        sha.record_threshold_attempt("m1")
        sha.record_threshold_attempt("m1")
        result = sha.record_threshold_attempt("m2")
        assert result["ok"] is True


class TestCheckSampleSize:
    def test_sufficient_sample_ok(self):
        sha = StatisticalHygieneAuditor(min_sample_size=30)
        result = sha.check_sample_size(50, "metric_x")
        assert result["ok"] is True

    def test_insufficient_sample_triggers_violation(self):
        sha = StatisticalHygieneAuditor(min_sample_size=30)
        result = sha.check_sample_size(10, "metric_y")
        assert result["violation"] == StatViolation.SMALL_SAMPLE.value
        assert result["sample_count"] == 10

    def test_exact_minimum_ok(self):
        sha = StatisticalHygieneAuditor(min_sample_size=30)
        result = sha.check_sample_size(30, "metric_z")
        assert result["ok"] is True

    def test_zero_sample_triggers_violation(self):
        sha = StatisticalHygieneAuditor(min_sample_size=30)
        result = sha.check_sample_size(0, "metric_w")
        assert result["violation"] == StatViolation.SMALL_SAMPLE.value


class TestCheckSurvivorshipBias:
    def test_no_anomalies_no_bias(self):
        sha = StatisticalHygieneAuditor()
        result = sha.check_survivorship_bias()
        assert result["survivorship_bias"] is False

    def test_high_confirmation_rate_triggers_bias(self):
        sha = StatisticalHygieneAuditor()
        for i in range(25):
            sha.record_anomaly_confirmation(f"anom-{i}", confirmed=True)
        for i in range(2):
            sha.record_anomaly_confirmation(f"unconf-{i}", confirmed=False)
        result = sha.check_survivorship_bias()
        assert result["survivorship_bias"] is True

    def test_balanced_no_bias(self):
        sha = StatisticalHygieneAuditor()
        for i in range(15):
            sha.record_anomaly_confirmation(f"anom-{i}", confirmed=True)
        for i in range(15):
            sha.record_anomaly_confirmation(f"unconf-{i}", confirmed=False)
        result = sha.check_survivorship_bias()
        assert result["survivorship_bias"] is False


class TestRecordAnomalyConfirmation:
    def test_confirmed_anomaly(self):
        sha = StatisticalHygieneAuditor()
        sha.record_anomaly_confirmation("a1", confirmed=True)
        assert "a1" in sha.confirmed_anomalies
        assert sha.confirmed_anomalies["a1"] == 1

    def test_unconfirmed_anomaly(self):
        sha = StatisticalHygieneAuditor()
        sha.record_anomaly_confirmation("a2", confirmed=False)
        assert "a2" in sha.unconfirmed_anomalies

    def test_repeated_confirmation_increments(self):
        sha = StatisticalHygieneAuditor()
        sha.record_anomaly_confirmation("a3", confirmed=True)
        sha.record_anomaly_confirmation("a3", confirmed=True)
        assert sha.confirmed_anomalies["a3"] == 2


class TestGetFalseDiscoveryRateEstimate:
    def test_no_confirmed_anomalies(self):
        sha = StatisticalHygieneAuditor()
        sha.set_active_metrics(10)
        fdr = sha.get_false_discovery_rate_estimate()
        assert isinstance(fdr, float)
        assert fdr >= 0.0

    def test_with_confirmed_anomalies(self):
        sha = StatisticalHygieneAuditor()
        sha.set_active_metrics(5)
        sha.record_anomaly_confirmation("a1", confirmed=True)
        sha.record_anomaly_confirmation("a2", confirmed=True)
        fdr = sha.get_false_discovery_rate_estimate()
        assert fdr <= 1.0

    def test_fdr_bounded(self):
        sha = StatisticalHygieneAuditor()
        fdr = sha.get_false_discovery_rate_estimate()
        assert 0.0 <= fdr <= 1.0


class TestOverallHygieneScore:
    def test_perfect_score_no_violations(self):
        sha = StatisticalHygieneAuditor()
        sha.set_active_metrics(5)
        for i in range(30):
            sha.record_anomaly_confirmation(f"a-{i}", confirmed=True)
        score = sha.overall_hygiene_score()
        assert score == 1.0

    def test_violations_reduce_score(self):
        sha = StatisticalHygieneAuditor(max_threshold_attempts=1)
        sha.set_active_metrics(25)
        sha.record_threshold_attempt("m1")
        sha.record_threshold_attempt("m1")
        score = sha.overall_hygiene_score()
        assert score < 1.0

    def test_score_bounded(self):
        sha = StatisticalHygieneAuditor()
        score = sha.overall_hygiene_score()
        assert 0.0 <= score <= 1.0
