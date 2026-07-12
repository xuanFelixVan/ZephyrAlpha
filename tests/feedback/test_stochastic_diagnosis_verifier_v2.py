# [A_test] module_id: SRC-TST-1691 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_stochastic_diagnosis_verifier_v2
# [INVARIANTS] consensus_threshold=0.60; min_reruns=5; max_variance_tolerance=0.20
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_stochastic_diagnosis_verifier_v2.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.verifiers.stochastic_diagnosis_verifier import (
    StochasticDiagnosisVerifier,
)


class TestStochasticDiagnosisVerifierInstantiation:
    def test_default_construction(self):
        sdv = StochasticDiagnosisVerifier()
        assert sdv.min_reruns == 5
        assert sdv.consensus_threshold == pytest.approx(0.60)
        assert sdv.max_variance_tolerance == pytest.approx(0.20)

    def test_custom_params(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=3, consensus_threshold=0.8)
        assert sdv.min_reruns == 3
        assert sdv.consensus_threshold == pytest.approx(0.8)


class TestDeterministicSeed:
    def test_deterministic_same_inputs(self):
        sdv = StochasticDiagnosisVerifier()
        seed1 = sdv.deterministic_seed("anom-1", 0)
        seed2 = sdv.deterministic_seed("anom-1", 0)
        assert seed1 == seed2

    def test_different_inputs_different_seeds(self):
        sdv = StochasticDiagnosisVerifier()
        seed1 = sdv.deterministic_seed("anom-1", 0)
        seed2 = sdv.deterministic_seed("anom-2", 0)
        assert seed1 != seed2

    def test_different_run_indices_different_seeds(self):
        sdv = StochasticDiagnosisVerifier()
        seed1 = sdv.deterministic_seed("anom-1", 0)
        seed2 = sdv.deterministic_seed("anom-1", 1)
        assert seed1 != seed2


class TestRecordAndVerifyStability:
    def test_insufficient_reruns(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=5)
        for i in range(3):
            sdv.record_diagnosis_run("anom-1", i, "cause-a", 0.9)
        result = sdv.verify_stability("anom-1")
        assert result["stable"] is False
        assert "insufficient_reruns" in result["reason"]

    def test_stable_consensus(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=5, consensus_threshold=0.60)
        for i in range(5):
            sdv.record_diagnosis_run("anom-1", i, "cause-a", 0.9)
        result = sdv.verify_stability("anom-1")
        assert result["stable"] is True
        assert result["consensus_cause"] == "cause-a"
        assert result["consensus_ratio"] == pytest.approx(1.0)

    def test_unstable_no_consensus(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=5, consensus_threshold=0.60)
        causes = ["cause-a", "cause-b", "cause-c", "cause-d", "cause-e"]
        for i in range(5):
            sdv.record_diagnosis_run("anom-2", i, causes[i], 0.5)
        result = sdv.verify_stability("anom-2")
        assert result["stable"] is False
        assert result["consensus_cause"] is None

    def test_empty_anomaly_id(self):
        sdv = StochasticDiagnosisVerifier()
        result = sdv.verify_stability("nonexistent")
        assert result["stable"] is False
        assert "insufficient_reruns" in result["reason"]

    def test_recommendation_request_human_review(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=5, consensus_threshold=0.60)
        sdv.record_diagnosis_run("anom-3", 0, "cause-a", 0.9)
        sdv.record_diagnosis_run("anom-3", 1, "cause-b", 0.8)
        sdv.record_diagnosis_run("anom-3", 2, "cause-c", 0.7)
        sdv.record_diagnosis_run("anom-3", 3, "cause-d", 0.6)
        sdv.record_diagnosis_run("anom-3", 4, "cause-e", 0.5)
        result = sdv.verify_stability("anom-3")
        assert result["recommendation"] == "request_human_review"


class TestGetUnstableCount:
    def test_no_unstable(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=3, consensus_threshold=0.60)
        for i in range(3):
            sdv.record_diagnosis_run("anom-1", i, "same-cause", 0.9)
        sdv.verify_stability("anom-1")
        assert sdv.get_unstable_count() == 0

    def test_with_unstable(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=5, consensus_threshold=0.60)
        causes = ["a", "b", "c", "d", "e"]
        for i in range(5):
            sdv.record_diagnosis_run("anom-1", i, causes[i], 0.5)
        sdv.verify_stability("anom-1")
        assert sdv.get_unstable_count() == 1


class TestOverallDiagnosisReliability:
    def test_empty_scores(self):
        sdv = StochasticDiagnosisVerifier()
        assert sdv.overall_diagnosis_reliability() == pytest.approx(1.0)

    def test_mixed_reliability(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=3, consensus_threshold=0.60)
        for i in range(3):
            sdv.record_diagnosis_run("anom-1", i, "same", 0.9)
        sdv.verify_stability("anom-1")
        causes = ["a", "b", "c"]
        for i in range(3):
            sdv.record_diagnosis_run("anom-2", i, causes[i], 0.5)
        sdv.verify_stability("anom-2")
        reliability = sdv.overall_diagnosis_reliability()
        assert 0.0 <= reliability <= 1.0


class TestClearRuns:
    def test_clear_existing(self):
        sdv = StochasticDiagnosisVerifier()
        sdv.record_diagnosis_run("anom-1", 0, "cause", 0.9)
        sdv.clear_runs("anom-1")
        assert "anom-1" not in sdv.diagnosis_runs

    def test_clear_nonexistent_no_error(self):
        sdv = StochasticDiagnosisVerifier()
        sdv.clear_runs("nonexistent")
