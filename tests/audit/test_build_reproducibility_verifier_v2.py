# [A_test] module_id: SRC-TST-0472 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_build_reproducibility_verifier_v2
# [INVARIANTS] max_drift_tolerance=0.05; build_retention=10
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_build_reproducibility_verifier_v2.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.verifiers.build_reproducibility_verifier import (
    BuildIntegrity,
    BuildReproducibilityVerifier,
)


class TestBuildReproducibilityVerifierInstantiation:
    def test_default_construction(self):
        brv = BuildReproducibilityVerifier()
        assert brv.max_drift_tolerance == pytest.approx(0.05)
        assert brv.build_retention == 10
        assert brv.build_hashes == []

    def test_custom_params(self):
        brv = BuildReproducibilityVerifier(max_drift_tolerance=0.1, build_retention=5)
        assert brv.max_drift_tolerance == pytest.approx(0.1)
        assert brv.build_retention == 5


class TestHashDirectory:
    def test_hash_empty_dir(self, tmp_path):
        brv = BuildReproducibilityVerifier()
        h = brv.hash_directory(str(tmp_path))
        assert isinstance(h, str)
        assert len(h) > 0

    def test_hash_with_files(self, tmp_path):
        brv = BuildReproducibilityVerifier()
        (tmp_path / "a.py").write_text("print('hello')", encoding="utf-8")
        h = brv.hash_directory(str(tmp_path))
        assert isinstance(h, str)

    def test_hash_consistency(self, tmp_path):
        brv = BuildReproducibilityVerifier()
        (tmp_path / "a.py").write_text("x=1", encoding="utf-8")
        h1 = brv.hash_directory(str(tmp_path))
        h2 = brv.hash_directory(str(tmp_path))
        assert h1 == h2

    def test_hash_changes_with_content(self, tmp_path):
        brv = BuildReproducibilityVerifier()
        (tmp_path / "a.py").write_text("x=1", encoding="utf-8")
        h1 = brv.hash_directory(str(tmp_path))
        (tmp_path / "a.py").write_text("x=2", encoding="utf-8")
        h2 = brv.hash_directory(str(tmp_path))
        assert h1 != h2

    def test_hash_skips_pycache(self, tmp_path):
        brv = BuildReproducibilityVerifier()
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "mod.cpython-311.pyc").write_bytes(b"\x00\x01")
        (tmp_path / "mod.py").write_text("x=1", encoding="utf-8")
        h1 = brv.hash_directory(str(tmp_path))
        (cache_dir / "mod.cpython-311.pyc").write_bytes(b"\x00\x02")
        h2 = brv.hash_directory(str(tmp_path))
        assert h1 == h2


class TestRecordBuildHash:
    def test_first_build_reproducible(self):
        brv = BuildReproducibilityVerifier()
        result = brv.record_build_hash("build-1", "abc123")
        assert result["integrity"] == BuildIntegrity.REPRODUCIBLE.value

    def test_second_build_same_hash(self):
        brv = BuildReproducibilityVerifier()
        brv.record_build_hash("build-1", "abc123")
        result = brv.record_build_hash("build-2", "abc123")
        assert result["integrity"] == BuildIntegrity.REPRODUCIBLE.value

    def test_second_build_drift(self):
        brv = BuildReproducibilityVerifier()
        brv.record_build_hash("build-1", "hash_aaa")
        result = brv.record_build_hash("build-2", "hash_bbb")
        assert result["integrity"] == BuildIntegrity.DRIFT_DETECTED.value

    def test_retention_limit(self):
        brv = BuildReproducibilityVerifier(build_retention=3)
        for i in range(5):
            brv.record_build_hash(f"build-{i}", f"hash-{i}")
        assert len(brv.build_hashes) == 3


class TestVerifyDependencies:
    def test_all_present(self):
        brv = BuildReproducibilityVerifier()
        result = brv.verify_dependencies(["os", "sys"])
        assert result["integrity"] == BuildIntegrity.REPRODUCIBLE.value
        assert result["missing_modules"] == []

    def test_missing_module(self):
        brv = BuildReproducibilityVerifier()
        result = brv.verify_dependencies(["nonexistent_module_xyz_123"])
        assert result["integrity"] == BuildIntegrity.BROKEN.value
        assert len(result["missing_modules"]) == 1

    def test_empty_list(self):
        brv = BuildReproducibilityVerifier()
        result = brv.verify_dependencies([])
        assert result["integrity"] == BuildIntegrity.REPRODUCIBLE.value


class TestVerifyCIConsistency:
    def test_consistent(self):
        brv = BuildReproducibilityVerifier()
        result = brv.verify_ci_consistency("hash123", "hash123")
        assert result["consistent"] is True

    def test_inconsistent(self):
        brv = BuildReproducibilityVerifier()
        result = brv.verify_ci_consistency("hash_aaa", "hash_bbb")
        assert result["consistent"] is False


class TestOverallReproducibilityScore:
    def test_no_builds(self):
        brv = BuildReproducibilityVerifier()
        assert brv.overall_reproducibility_score() == pytest.approx(1.0)

    def test_single_build(self):
        brv = BuildReproducibilityVerifier()
        brv.record_build_hash("b1", "h1")
        assert brv.overall_reproducibility_score() == pytest.approx(1.0)

    def test_multiple_unique_hashes(self):
        brv = BuildReproducibilityVerifier()
        brv.record_build_hash("b1", "h1")
        brv.record_build_hash("b2", "h2")
        score = brv.overall_reproducibility_score()
        assert score < 1.0


class TestGetDaysSinceLastVerification:
    def test_no_verification(self):
        brv = BuildReproducibilityVerifier()
        assert brv.get_days_since_last_verification() == float("inf")

    def test_after_verification(self):
        brv = BuildReproducibilityVerifier()
        brv.record_build_hash("b1", "h1")
        days = brv.get_days_since_last_verification()
        assert days >= 0.0
