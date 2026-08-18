# [A_test] module_id: MOD-GOV_code_integrity | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_code_integrity
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import os
from pathlib import Path

from zephyr.security.llm_defense.llm_security.self_protection.code_integrity import (
    CodeIntegrityGuard,
    IntegrityStatus,
)
from zephyr.shared.io.paths import REPO_ROOT

PROJECT_ROOT = str(REPO_ROOT)


class TestCodeIntegrityGuardInit:
    def test_default_project_root(self):
        guard = CodeIntegrityGuard()
        assert guard.project_root == os.getcwd()

    def test_custom_project_root(self):
        guard = CodeIntegrityGuard(project_root=str(Path("/tmp")))
        assert guard.project_root == str(Path("/tmp"))

    def test_initial_state_not_compromised(self):
        guard = CodeIntegrityGuard()
        assert guard.is_compromised is False

    def test_initial_baseline_empty(self):
        guard = CodeIntegrityGuard()
        assert len(guard.baseline) == 0


class TestComputeBaseline:
    def test_compute_baseline_for_existing_dir(self):
        guard = CodeIntegrityGuard(project_root=PROJECT_ROOT)
        records = guard.compute_baseline_for_directory("src/zephyr/security/llm_defense/llm_security/layers")
        assert isinstance(records, list)
        assert len(records) > 0
        for r in records:
            assert r.status == IntegrityStatus.CLEAN
            assert len(r.sha256) == 64

    def test_compute_full_baseline(self):
        guard = CodeIntegrityGuard(project_root=PROJECT_ROOT)
        records = guard.compute_full_baseline()
        assert isinstance(records, list)
        assert len(records) > 0

    def test_baseline_populated_after_compute(self):
        guard = CodeIntegrityGuard(project_root=PROJECT_ROOT)
        guard.compute_full_baseline()
        assert len(guard.baseline) > 0

    def test_compute_baseline_for_nonexistent_dir(self):
        guard = CodeIntegrityGuard(project_root="/nonexistent")
        records = guard.compute_baseline_for_directory("src/zephyr/llm-security/layers")
        assert isinstance(records, list)
        assert len(records) == 0


class TestVerifySingle:
    def test_verify_existing_file(self):
        guard = CodeIntegrityGuard(project_root=PROJECT_ROOT)
        guard.compute_full_baseline()
        first_path = list(guard.baseline.keys())[0]
        record = guard.verify_single(first_path)
        assert record.status == IntegrityStatus.CLEAN

    def test_verify_nonexistent_file(self):
        guard = CodeIntegrityGuard(project_root="/nonexistent")
        record = guard.verify_single("nonexistent_file.py")
        assert record.status == IntegrityStatus.UNKNOWN


class TestVerifyAll:
    def test_verify_all_clean(self):
        guard = CodeIntegrityGuard(project_root=PROJECT_ROOT)
        guard.compute_full_baseline()
        result = guard.verify_all()
        assert result["total"] > 0
        assert result["tampered"] == 0
        assert result["compromised"] is False

    def test_verify_all_without_baseline(self):
        guard = CodeIntegrityGuard(project_root="/nonexistent")
        result = guard.verify_all()
        assert result["total"] == 0


class TestPeriodicScan:
    def test_periodic_scan_not_due_after_compute(self):
        guard = CodeIntegrityGuard(project_root=PROJECT_ROOT)
        guard.compute_full_baseline()
        result = guard.periodic_scan_if_due()
        assert result is None

    def test_periodic_scan_due_after_interval(self):
        guard = CodeIntegrityGuard(project_root=PROJECT_ROOT)
        guard.compute_full_baseline()
        guard.last_scan_time = 0.0
        result = guard.periodic_scan_if_due()
        assert result is not None
        assert "total" in result
