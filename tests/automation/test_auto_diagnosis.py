# [A_test] module_id: SRC-TST-0371 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_auto_diagnosis
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.auto_diagnosis
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_auto_diagnosis.py
# [TTL] task_bound

from zephyr.feedback_loop.diagnosers.auto_diagnosis import AutoDiagnosis


class TestAutoDiagnosis:
    def test_instantiation_default(self):
        ad = AutoDiagnosis()
        assert ad.enabled is True
        assert ad.max_concurrent == 5

    def test_instantiation_disabled(self):
        ad = AutoDiagnosis(enabled=False)
        assert ad.enabled is False

    def test_instantiation_custom_max_concurrent(self):
        ad = AutoDiagnosis(max_concurrent=10)
        assert ad.max_concurrent == 10

    def test_diagnose_returns_dict(self):
        ad = AutoDiagnosis()
        result = ad.diagnose("anomaly-001")
        assert isinstance(result, dict)

    def test_diagnose_contains_anomaly_id(self):
        ad = AutoDiagnosis()
        result = ad.diagnose("anomaly-001")
        assert result["anomaly_id"] == "anomaly-001"

    def test_diagnose_contains_status(self):
        ad = AutoDiagnosis()
        result = ad.diagnose("anomaly-001")
        assert "status" in result

    def test_diagnose_empty_string(self):
        ad = AutoDiagnosis()
        result = ad.diagnose("")
        assert result["anomaly_id"] == ""

    def test_diagnose_various_ids(self):
        ad = AutoDiagnosis()
        result_a = ad.diagnose("a-001")
        result_b = ad.diagnose("b-002")
        assert result_a["anomaly_id"] == "a-001"
        assert result_b["anomaly_id"] == "b-002"

    def test_diagnose_unicode_id(self):
        ad = AutoDiagnosis()
        result = ad.diagnose("异常-001")
        assert result["anomaly_id"] == "异常-001"

    def test_diagnose_long_id(self):
        ad = AutoDiagnosis()
        long_id = "a" * 1000
        result = ad.diagnose(long_id)
        assert result["anomaly_id"] == long_id

    def test_diagnose_special_characters(self):
        ad = AutoDiagnosis()
        result = ad.diagnose("id/with:special@chars#123")
        assert result["anomaly_id"] == "id/with:special@chars#123"

    def test_max_concurrent_zero(self):
        ad = AutoDiagnosis(max_concurrent=0)
        assert ad.max_concurrent == 0
        result = ad.diagnose("anomaly-001")
        assert result["anomaly_id"] == "anomaly-001"

    def test_diagnose_returns_status_queued(self):
        ad = AutoDiagnosis()
        result = ad.diagnose("anomaly-001")
        assert result["status"] == "queued"
