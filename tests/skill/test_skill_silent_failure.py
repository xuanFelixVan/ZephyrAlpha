# [A_test] module_id: MOD-GOV_skill_silent_failure | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_silent_failure
# [INVARIANTS] SilentFailureDetector.scan returns dict with silent_failure_detected and anomalies
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] scan returns structured dict; get_session_anomalies filters by skill_id
# [TESTS] tests/test_skill_silent_failure.py
# [TTL] task_bound

from zephyr.autonomy_core.skills.skill_silent_failure import SilentFailureDetector


class TestSilentFailureDetectorInstantiation:
    def test_instantiation(self):
        detector = SilentFailureDetector()
        assert detector is not None
        assert detector.execution_history == {}
        assert detector.anomalies == []

    def test_anomaly_constants(self):
        assert SilentFailureDetector.ANOMALY_TRUNCATION == "output_truncation"
        assert SilentFailureDetector.ANOMALY_PARTIAL_SUCCESS == "partial_success"
        assert SilentFailureDetector.ANOMALY_ASSUMPTION == "assumption_violation"
        assert SilentFailureDetector.ANOMALY_NON_IDEMPOTENT == "non_idempotent"


class TestSilentFailureDetectorScan:
    def test_clean_output(self):
        detector = SilentFailureDetector()
        result = detector.scan("skill-a", "All checks passed successfully.")
        assert result["silent_failure_detected"] is False
        assert result["anomalies"] == []
        assert result["anomaly_count"] == 0
        assert result["checks_run"] == 4

    def test_empty_output(self):
        detector = SilentFailureDetector()
        result = detector.scan("skill-b", "")
        assert result["silent_failure_detected"] is False
        assert result["output_length"] == 0

    def test_truncation_detected(self):
        detector = SilentFailureDetector()
        result = detector.scan("skill-c", "Some output that was truncated")
        assert result["silent_failure_detected"] is True
        truncation = [a for a in result["anomalies"] if a["type"] == "output_truncation"]
        assert len(truncation) > 0

    def test_truncation_ellipsis_at_end(self):
        detector = SilentFailureDetector()
        result = detector.scan("skill-d", "Partial content...")
        assert result["silent_failure_detected"] is True

    def test_partial_success_detected(self):
        detector = SilentFailureDetector()
        result = detector.scan("skill-e", "3/5 passed, some checks failed")
        assert result["silent_failure_detected"] is True
        partial = [a for a in result["anomalies"] if a["type"] == "partial_success"]
        assert len(partial) > 0

    def test_assumption_violation_detected(self):
        detector = SilentFailureDetector()
        result = detector.scan("skill-f", "assuming that the database is available but it was not")
        assert result["silent_failure_detected"] is True
        assumption = [a for a in result["anomalies"] if a["type"] == "assumption_violation"]
        assert len(assumption) > 0

    def test_non_idempotent_detected(self):
        detector = SilentFailureDetector()
        prefix = "x" * 200
        detector.scan("skill-g", prefix + "AAAA", operation="op1")
        result = detector.scan("skill-g", prefix + "BBBB", operation="op1")
        non_idem = [a for a in result["anomalies"] if a["type"] == "non_idempotent"]
        assert len(non_idem) > 0

    def test_idempotent_same_output(self):
        detector = SilentFailureDetector()
        detector.scan("skill-h", "same output", operation="op2")
        result = detector.scan("skill-h", "same output", operation="op2")
        non_idem = [a for a in result["anomalies"] if a["type"] == "non_idempotent"]
        assert len(non_idem) == 0

    def test_multiple_anomalies(self):
        detector = SilentFailureDetector()
        result = detector.scan("skill-i", "3/5 passed... assuming that data exists but it was not found")
        assert result["silent_failure_detected"] is True
        assert result["anomaly_count"] >= 2

    def test_scan_returns_skill_id(self):
        detector = SilentFailureDetector()
        result = detector.scan("my-skill", "clean output")
        assert result["skill_id"] == "my-skill"

    def test_scan_returns_operation(self):
        detector = SilentFailureDetector()
        result = detector.scan("skill-j", "output", operation="my-op")
        assert result["operation"] == "my-op"


class TestSilentFailureDetectorGetSessionAnomalies:
    def test_no_anomalies(self):
        detector = SilentFailureDetector()
        assert detector.get_session_anomalies() == []

    def test_all_anomalies(self):
        detector = SilentFailureDetector()
        detector.scan("skill-k", "truncated output...")
        anomalies = detector.get_session_anomalies()
        assert len(anomalies) > 0

    def test_filter_by_skill_id(self):
        detector = SilentFailureDetector()
        detector.scan("skill-l", "truncated output...")
        detector.scan("skill-m", "clean output")
        anomalies_l = detector.get_session_anomalies("skill-l")
        anomalies_m = detector.get_session_anomalies("skill-m")
        assert len(anomalies_l) > 0
        assert len(anomalies_m) == 0

    def test_filter_nonexistent_skill(self):
        detector = SilentFailureDetector()
        detector.scan("skill-n", "truncated output...")
        anomalies = detector.get_session_anomalies("nonexistent")
        assert anomalies == []
