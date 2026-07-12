# [A_test] module_id: SRC-TST-1690 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_stochastic_diagnosis_verifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.verifiers.stochastic_diagnosis_verifier
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_stochastic_diagnosis_verifier.py
# [TTL] task_bound


from zephyr.feedback_loop.verifiers.stochastic_diagnosis_verifier import (
    StochasticDiagnosisVerifier,
)


class TestStochasticDiagnosisVerifierInstantiation:
    def test_default_instantiation(self):
        sdv = StochasticDiagnosisVerifier()
        assert sdv.min_reruns == 5
        assert sdv.consensus_threshold == 0.60
        assert sdv.max_variance_tolerance == 0.20
        assert sdv.diagnosis_runs == {}
        assert sdv.stability_scores == {}
        assert sdv.unstable_diagnoses == []

    def test_custom_instantiation(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=3, consensus_threshold=0.8)
        assert sdv.min_reruns == 3
        assert sdv.consensus_threshold == 0.8


class TestDeterministicSeed:
    def test_deterministic(self):
        sdv = StochasticDiagnosisVerifier()
        s1 = sdv.deterministic_seed("anomaly-1", 0)
        s2 = sdv.deterministic_seed("anomaly-1", 0)
        assert s1 == s2

    def test_different_inputs(self):
        sdv = StochasticDiagnosisVerifier()
        s1 = sdv.deterministic_seed("anomaly-1", 0)
        s2 = sdv.deterministic_seed("anomaly-2", 0)
        assert s1 != s2

    def test_different_run_indices(self):
        sdv = StochasticDiagnosisVerifier()
        s1 = sdv.deterministic_seed("anomaly-1", 0)
        s2 = sdv.deterministic_seed("anomaly-1", 1)
        assert s1 != s2


class TestRecordDiagnosisRun:
    def test_record_single_run(self):
        sdv = StochasticDiagnosisVerifier()
        sdv.record_diagnosis_run("a1", 0, "cpu_overload", 0.9)
        assert len(sdv.diagnosis_runs["a1"]) == 1

    def test_record_multiple_runs(self):
        sdv = StochasticDiagnosisVerifier()
        for i in range(5):
            sdv.record_diagnosis_run("a1", i, "cpu_overload", 0.9)
        assert len(sdv.diagnosis_runs["a1"]) == 5


class TestVerifyStability:
    def test_insufficient_reruns(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=5)
        sdv.record_diagnosis_run("a1", 0, "cpu_overload", 0.9)
        result = sdv.verify_stability("a1")
        assert result["stable"] is False
        assert "insufficient_reruns" in result["reason"]

    def test_stable_consensus(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=3, consensus_threshold=0.6)
        for i in range(3):
            sdv.record_diagnosis_run("a1", i, "cpu_overload", 0.9)
        result = sdv.verify_stability("a1")
        assert result["stable"] is True
        assert result["consensus_cause"] == "cpu_overload"

    def test_unstable_consensus(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=3, consensus_threshold=0.8)
        sdv.record_diagnosis_run("a1", 0, "cpu_overload", 0.9)
        sdv.record_diagnosis_run("a1", 1, "mem_leak", 0.8)
        sdv.record_diagnosis_run("a1", 2, "disk_full", 0.7)
        result = sdv.verify_stability("a1")
        assert result["stable"] is False


class TestGetUnstableCount:
    def test_no_unstable(self):
        sdv = StochasticDiagnosisVerifier()
        assert sdv.get_unstable_count() == 0

    def test_unstable_count(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=3, consensus_threshold=0.99)
        sdv.record_diagnosis_run("a1", 0, "cause_a", 0.9)
        sdv.record_diagnosis_run("a1", 1, "cause_b", 0.8)
        sdv.record_diagnosis_run("a1", 2, "cause_c", 0.7)
        sdv.verify_stability("a1")
        assert sdv.get_unstable_count() == 1


class TestOverallDiagnosisReliability:
    def test_no_scores(self):
        sdv = StochasticDiagnosisVerifier()
        assert sdv.overall_diagnosis_reliability() == 1.0

    def test_all_stable(self):
        sdv = StochasticDiagnosisVerifier(min_reruns=3, consensus_threshold=0.6)
        for i in range(3):
            sdv.record_diagnosis_run("a1", i, "same_cause", 0.9)
        sdv.verify_stability("a1")
        assert sdv.overall_diagnosis_reliability() == 1.0


class TestClearRuns:
    def test_clear_runs(self):
        sdv = StochasticDiagnosisVerifier()
        sdv.record_diagnosis_run("a1", 0, "cause", 0.9)
        sdv.clear_runs("a1")
        assert "a1" not in sdv.diagnosis_runs
        assert "a1" not in sdv.stability_scores

    def test_clear_nonexistent(self):
        sdv = StochasticDiagnosisVerifier()
        sdv.clear_runs("nonexistent")
