# [A_test] module_id: SRC-TST-1436 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_recursive_diagnosis_trust_evaluator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_recursive_diagnosis_trust_evaluator.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.guard.recursive_diagnosis_trust_evaluator import (
    ExternalSignal,
    RecursiveDiagnosisTrustEvaluator,
)


class TestExternalSignal:
    def test_creation(self):
        sig = ExternalSignal(source="cpu", value=0.9, threshold=0.8, direction="above")
        assert sig.source == "cpu"
        assert sig.value == 0.9
        assert sig.threshold == 0.8
        assert sig.direction == "above"

    def test_creation_below_direction(self):
        sig = ExternalSignal(source="disk_free", value=0.1, threshold=0.2, direction="below")
        assert sig.direction == "below"


class TestRecursiveDiagnosisTrustEvaluator:
    def test_default_construction(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        assert eval_.external_signals == {}
        assert eval_.self_diagnosis_history == []
        assert eval_.max_history == 50

    def test_custom_construction(self):
        eval_ = RecursiveDiagnosisTrustEvaluator(max_history=100)
        assert eval_.max_history == 100

    def test_register_external_signal(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("cpu", 0.9, 0.8, "above")
        assert "cpu" in eval_.external_signals
        assert eval_.external_signals["cpu"].value == 0.9

    def test_register_external_signal_default_direction(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("cpu", 0.9, 0.8)
        assert eval_.external_signals["cpu"].direction == "above"

    def test_update_external_signal(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("cpu", 0.5, 0.8, "above")
        eval_.update_external_signal("cpu", 0.95)
        assert eval_.external_signals["cpu"].value == 0.95

    def test_update_external_signal_nonexistent(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.update_external_signal("nonexistent", 0.5)
        assert "nonexistent" not in eval_.external_signals

    def test_evaluate_trust_no_external_signals(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        result = eval_.evaluate_trust({"status": "healthy"})
        assert result["external_verdict"] == "unknown"
        assert result["trust-score"] == 0.4
        assert result["trustworthy"] is False

    def test_evaluate_trust_agree_healthy(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("cpu", 0.5, 0.8, "above")
        result = eval_.evaluate_trust({"status": "healthy"})
        assert result["self_diagnosis_status"] == "healthy"
        assert result["external_verdict"] == "healthy"
        assert result["trust-score"] == 0.9
        assert result["trustworthy"] is True

    def test_evaluate_trust_agree_unhealthy(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("cpu", 0.95, 0.8, "above")
        result = eval_.evaluate_trust({"status": "unhealthy"})
        assert result["external_verdict"] == "unhealthy"
        assert result["trust-score"] == 0.9

    def test_evaluate_trust_disagree_healthy_vs_unhealthy(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("cpu", 0.95, 0.8, "above")
        result = eval_.evaluate_trust({"status": "healthy"})
        assert result["trust-score"] == 0.1

    def test_evaluate_trust_near_disagree(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("cpu", 0.95, 0.8, "above")
        result = eval_.evaluate_trust({"status": "degraded"})
        assert result["trust-score"] == 0.3

    def test_evaluate_trust_recommendation_trust_self(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("cpu", 0.5, 0.8, "above")
        result = eval_.evaluate_trust({"status": "healthy"})
        assert result["recommendation"] == "trust_self"

    def test_evaluate_trust_recommendation_trust_external(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("cpu", 0.95, 0.8, "above")
        result = eval_.evaluate_trust({"status": "healthy"})
        assert result["recommendation"] == "trust_external"

    def test_evaluate_trust_recommendation_inconclusive(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("cpu", 0.5, 0.8, "above")
        result = eval_.evaluate_trust({"status": "degraded"})
        assert result["recommendation"] in ("inconclusive", "trust_external")

    def test_evaluate_trust_history_appended(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.evaluate_trust({"status": "healthy"})
        eval_.evaluate_trust({"status": "unhealthy"})
        assert len(eval_.self_diagnosis_history) == 2

    def test_evaluate_trust_history_trims(self):
        eval_ = RecursiveDiagnosisTrustEvaluator(max_history=5)
        for i in range(10):
            eval_.evaluate_trust({"status": "healthy"})
        assert len(eval_.self_diagnosis_history) <= 5

    def test_aggregate_external_signals_below_direction(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("disk_free", 0.05, 0.2, "below")
        result = eval_.evaluate_trust({"status": "unhealthy"})
        assert result["external_verdict"] == "unhealthy"

    def test_aggregate_external_signals_mixed(self):
        eval_ = RecursiveDiagnosisTrustEvaluator()
        eval_.register_external_signal("cpu", 0.5, 0.8, "above")
        eval_.register_external_signal("memory", 0.5, 0.8, "above")
        eval_.register_external_signal("disk", 0.95, 0.8, "above")
        eval_.register_external_signal("network", 0.95, 0.8, "above")
        result = eval_.evaluate_trust({"status": "healthy"})
        assert result["external_verdict"] == "unhealthy"
