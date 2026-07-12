# [A_test] module_id: SRC-TST-1553 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_self_check
# [INVARIANTS] 自检逻辑不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_self_check.py
# [TTL] task_bound

import tempfile
from pathlib import Path

from zephyr.gov_drift.self_check import (
    bootstrap_self_check,
    check_core_files,
    check_registry_parsable,
    run_self_check,
    sha256_file,
)


class TestSha256File:
    def test_hash_existing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fp = Path(tmpdir) / "test_file.py"
            fp.write_bytes(b"hello world")
            result = sha256_file(fp)
            assert result != "ERROR"
            assert len(result) == 64

    def test_hash_nonexistent_file(self):
        result = sha256_file(Path("/nonexistent/file/abc.py"))
        assert result == "ERROR"

    def test_hash_empty_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fp = Path(tmpdir) / "empty.py"
            fp.write_bytes(b"")
            result = sha256_file(fp)
            assert result != "ERROR"
            assert len(result) == 64


class TestCheckCoreFiles:
    def test_missing_files_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            results = check_core_files(Path(tmpdir))
            assert "drift_engine.py" in results
            assert results["drift_engine.py"] == "MISSING"

    def test_present_files_hashed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "drift_engine.py").write_text("x=1", encoding="utf-8")
            results = check_core_files(Path(tmpdir))
            assert results["drift_engine.py"] != "MISSING"
            assert len(results["drift_engine.py"]) == 64

    def test_all_expected_filenames_checked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            results = check_core_files(Path(tmpdir))
            expected = {
                "_detector-registry.yaml",
                "drift_engine.py",
                "reconciler.py",
                "state_machine.py",
                "baseline_manager.py",
                "detector_dispatcher.py",
                "drift_models.py",
            }
            assert set(results.keys()) == expected


class TestCheckRegistryParsable:
    def test_missing_registry_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            assert check_registry_parsable(Path(tmpdir)) is False

    def test_valid_registry_returns_true(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = Path(tmpdir) / "_detector-registry.yaml"
            registry.write_text("detectors:\n  d1:\n    name: test\n", encoding="utf-8")
            assert check_registry_parsable(Path(tmpdir)) is True

    def test_empty_registry_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = Path(tmpdir) / "_detector-registry.yaml"
            registry.write_text("", encoding="utf-8")
            assert check_registry_parsable(Path(tmpdir)) is False

    def test_invalid_yaml_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = Path(tmpdir) / "_detector-registry.yaml"
            registry.write_text("detectors: [invalid: yaml: content", encoding="utf-8")
            assert check_registry_parsable(Path(tmpdir)) is False


class TestBootstrapSelfCheck:
    def test_fails_with_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            assert bootstrap_self_check(Path(tmpdir)) is False

    def test_passes_with_all_files_and_valid_registry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            for fname in [
                "_detector-registry.yaml",
                "drift_engine.py",
                "reconciler.py",
                "state_machine.py",
                "baseline_manager.py",
                "detector_dispatcher.py",
                "drift_models.py",
            ]:
                (base / fname).write_text("x=1", encoding="utf-8")
            registry = base / "_detector-registry.yaml"
            registry.write_text("detectors:\n  d1:\n    name: test\n", encoding="utf-8")
            assert bootstrap_self_check(base) is True


class TestRunSelfCheck:
    def test_returns_int(self):
        result = run_self_check()
        assert isinstance(result, int)
        assert result in (0, 1)
