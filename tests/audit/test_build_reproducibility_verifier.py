# [A_test] module_id: SRC-TST-0471 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_build_reproducibility_verifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.verifiers.build_reproducibility_verifier
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_build_reproducibility_verifier.py
# [TTL] task_bound


from zephyr.feedback_loop.verifiers.build_reproducibility_verifier import (
    BuildIntegrity,
    BuildReproducibilityVerifier,
)


class TestBuildReproducibilityVerifierInstantiation:
    def test_default_instantiation(self):
        brv = BuildReproducibilityVerifier()
        assert brv.max_drift_tolerance == 0.05
        assert brv.build_retention == 10
        assert brv.build_hashes == []
        assert brv.integrity_violations == []
        assert brv.last_verification == 0.0

    def test_custom_instantiation(self):
        brv = BuildReproducibilityVerifier(max_drift_tolerance=0.1, build_retention=5)
        assert brv.max_drift_tolerance == 0.1
        assert brv.build_retention == 5


class TestRecordBuildHash:
    def test_first_record_is_reproducible(self):
        brv = BuildReproducibilityVerifier()
        result = brv.record_build_hash("build-1", "abc123")
        assert result["integrity"] == BuildIntegrity.REPRODUCIBLE.value

    def test_same_hash_is_reproducible(self):
        brv = BuildReproducibilityVerifier()
        brv.record_build_hash("build-1", "abc123")
        result = brv.record_build_hash("build-2", "abc123")
        assert result["integrity"] == BuildIntegrity.REPRODUCIBLE.value

    def test_different_hash_is_drift(self):
        brv = BuildReproducibilityVerifier()
        brv.record_build_hash("build-1", "abc123")
        result = brv.record_build_hash("build-2", "def456")
        assert result["integrity"] == BuildIntegrity.DRIFT_DETECTED.value

    def test_retention_limits_hashes(self):
        brv = BuildReproducibilityVerifier(build_retention=3)
        for i in range(5):
            brv.record_build_hash(f"build-{i}", f"hash-{i}")
        assert len(brv.build_hashes) == 3


class TestVerifyDependencies:
    def test_all_present(self):
        brv = BuildReproducibilityVerifier()
        result = brv.verify_dependencies(["json", "os"])
        assert result["integrity"] == BuildIntegrity.REPRODUCIBLE.value
        assert result["missing_modules"] == []

    def test_missing_module(self):
        brv = BuildReproducibilityVerifier()
        result = brv.verify_dependencies(["nonexistent_module_xyz"])
        assert result["integrity"] == BuildIntegrity.BROKEN.value
        assert "nonexistent_module_xyz" in result["missing_modules"]


class TestVerifyCIConsistency:
    def test_consistent_hashes(self):
        brv = BuildReproducibilityVerifier()
        result = brv.verify_ci_consistency("abc", "abc")
        assert result["consistent"] is True

    def test_inconsistent_hashes(self):
        brv = BuildReproducibilityVerifier()
        result = brv.verify_ci_consistency("abc", "def")
        assert result["consistent"] is False


class TestOverallReproducibilityScore:
    def test_no_builds_returns_one(self):
        brv = BuildReproducibilityVerifier()
        assert brv.overall_reproducibility_score() == 1.0

    def test_single_build_returns_one(self):
        brv = BuildReproducibilityVerifier()
        brv.record_build_hash("b1", "h1")
        assert brv.overall_reproducibility_score() == 1.0

    def test_diverse_builds_lower_score(self):
        brv = BuildReproducibilityVerifier()
        brv.record_build_hash("b1", "h1")
        brv.record_build_hash("b2", "h2")
        assert brv.overall_reproducibility_score() < 1.0


class TestGetDaysSinceLastVerification:
    def test_never_verified(self):
        brv = BuildReproducibilityVerifier()
        assert brv.get_days_since_last_verification() == float("inf")

    def test_recently_verified(self):
        brv = BuildReproducibilityVerifier()
        brv.record_build_hash("b1", "h1")
        assert brv.get_days_since_last_verification() < 1.0
