# [A_test] module_id: MOD-GOV_zombie_cleaner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_zombie_cleaner
# [INVARIANTS] 只测试公共接口;不修改真实项目文件
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml zombie_cleaner段
# [CONSUMERS] CI/CD;pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_zombie_cleaner.py
# [TTL] task_bound

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

from zephyr.infrastructure.auto_fix_engine.models import FixLevel, FixStatus
from zephyr.infrastructure.auto_fix_engine.zombie_cleaner import ZombieCleaner


class TestZombieCleanerInstantiation:
    def test_creates_instance_with_correct_fixer_id(self):
        cleaner = ZombieCleaner()
        assert cleaner.fixer_id == "zombie_cleaner"

    def test_creates_instance_with_correct_action_type(self):
        cleaner = ZombieCleaner()
        assert cleaner.action_type == "zombie_cleanup"

    def test_creates_instance_with_correct_level(self):
        cleaner = ZombieCleaner()
        assert cleaner.level == FixLevel.L1_RULE

    def test_creates_instance_with_correct_dimension(self):
        cleaner = ZombieCleaner()
        assert cleaner.dimension == "DIM-PATH-001"


class TestZombieCleanerScan:
    def test_scan_returns_list(self):
        cleaner = ZombieCleaner()
        with patch.object(Path, "rglob", return_value=[]):
            result = cleaner.scan()
        assert isinstance(result, list)

    def test_scan_finds_zombie_yaml_reference(self):
        cleaner = ZombieCleaner()
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_content = 'path: "nonexistent/module.py"\n'
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text(yaml_content, encoding="utf-8")
            with patch.object(Path, "rglob") as mock_rglob:
                mock_rglob.side_effect = lambda pattern: [yaml_file] if pattern == "*.yaml" else []
                with patch("zephyr.infrastructure.auto_fix_engine.zombie_cleaner.os.getcwd", return_value=tmpdir):
                    findings = cleaner.scan()
            assert any(f["type"] == "zombie_reference" for f in findings)

    def test_scan_finds_zombie_import_in_py(self):
        cleaner = ZombieCleaner()
        with tempfile.TemporaryDirectory() as tmpdir:
            py_content = 'config_path = "nonexistent/config.yaml"\n'
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text(py_content, encoding="utf-8")
            with patch.object(Path, "rglob") as mock_rglob:
                mock_rglob.side_effect = lambda pattern: [py_file] if pattern == "*.py" else []
                with patch("zephyr.infrastructure.auto_fix_engine.zombie_cleaner.os.getcwd", return_value=tmpdir):
                    findings = cleaner.scan()
            assert any(f["type"] == "zombie_import" for f in findings)

    def test_scan_skips_site_packages_references(self):
        cleaner = ZombieCleaner()
        with tempfile.TemporaryDirectory() as tmpdir:
            py_content = 'import "site-packages/numpy/core.py"\n'
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text(py_content, encoding="utf-8")
            with patch.object(Path, "rglob") as mock_rglob:
                mock_rglob.side_effect = lambda pattern: [py_file] if pattern == "*.py" else []
                with patch("zephyr.infrastructure.auto_fix_engine.zombie_cleaner.os.getcwd", return_value=tmpdir):
                    findings = cleaner.scan()
            zombie_imports = [f for f in findings if f["type"] == "zombie_import"]
            assert len(zombie_imports) == 0

    def test_scan_handles_unreadable_file_gracefully(self):
        cleaner = ZombieCleaner()
        bad_file = Path("/nonexistent/path/broken.yaml")
        with patch.object(Path, "rglob", return_value=[bad_file]):
            findings = cleaner.scan()
        assert isinstance(findings, list)


class TestZombieCleanerFix:
    def test_fix_returns_failed_for_nonexistent_target(self):
        cleaner = ZombieCleaner()
        action = cleaner.fix("/nonexistent/file.yaml")
        assert action.status == FixStatus.FAILED
        assert action.metadata.get("error") == "Target file not found"

    def test_fix_removes_zombie_reference_in_yaml(self):
        cleaner = ZombieCleaner()
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_content = 'name: test\npath: "nonexistent/module.py"\nother: value\n'
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text(yaml_content, encoding="utf-8")
            with patch("zephyr.infrastructure.auto_fix_engine.zombie_cleaner.os.getcwd", return_value=tmpdir):
                action = cleaner.fix(str(yaml_file), dry_run=True)
            assert action.status == FixStatus.COMPLETED
            assert "nonexistent/module.py" not in action.after

    def test_fix_dry_run_does_not_modify_file(self):
        cleaner = ZombieCleaner()
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_content = 'path: "nonexistent/module.py"\n'
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text(yaml_content, encoding="utf-8")
            original = yaml_file.read_text(encoding="utf-8")
            with patch("zephyr.infrastructure.auto_fix_engine.zombie_cleaner.os.getcwd", return_value=tmpdir):
                cleaner.fix(str(yaml_file), dry_run=True)
            assert yaml_file.read_text(encoding="utf-8") == original

    def test_fix_completes_when_no_zombies_found(self):
        cleaner = ZombieCleaner()
        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_content = "name: test\n"
            yaml_file = Path(tmpdir) / "test.yaml"
            yaml_file.write_text(yaml_content, encoding="utf-8")
            with patch("zephyr.infrastructure.auto_fix_engine.zombie_cleaner.os.getcwd", return_value=tmpdir):
                action = cleaner.fix(str(yaml_file))
            assert action.status == FixStatus.COMPLETED

    def test_fix_handles_py_file_zombie_import(self):
        cleaner = ZombieCleaner()
        with tempfile.TemporaryDirectory() as tmpdir:
            py_content = 'config_path = "nonexistent/config.yaml"\nprint("hello")\n'
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text(py_content, encoding="utf-8")
            with patch("zephyr.infrastructure.auto_fix_engine.zombie_cleaner.os.getcwd", return_value=tmpdir):
                action = cleaner.fix(str(py_file), dry_run=True)
            assert action.status == FixStatus.COMPLETED


class TestZombieCleanerValidate:
    def test_validate_returns_invalid_for_nonexistent_target(self):
        cleaner = ZombieCleaner()
        result = cleaner.validate("/nonexistent/file.py")
        assert result.valid is False
        assert result.error == "Target not found"

    def test_validate_returns_valid_for_clean_file(self):
        cleaner = ZombieCleaner()
        with tempfile.TemporaryDirectory() as tmpdir:
            py_content = 'print("hello")\n'
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text(py_content, encoding="utf-8")
            with patch("zephyr.infrastructure.auto_fix_engine.zombie_cleaner.os.getcwd", return_value=tmpdir):
                result = cleaner.validate(str(py_file))
            assert result.valid is True

    def test_validate_returns_invalid_for_file_with_zombies(self):
        cleaner = ZombieCleaner()
        with tempfile.TemporaryDirectory() as tmpdir:
            py_content = 'ref = "nonexistent/module.py"\n'
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text(py_content, encoding="utf-8")
            with patch("zephyr.infrastructure.auto_fix_engine.zombie_cleaner.os.getcwd", return_value=tmpdir):
                result = cleaner.validate(str(py_file))
            assert result.valid is False


class TestZombieCleanerRollback:
    def test_rollback_returns_false(self):
        cleaner = ZombieCleaner()
        assert cleaner.rollback("any_target") is False

    def test_rollback_returns_false_for_none_target(self):
        cleaner = ZombieCleaner()
        assert cleaner.rollback("") is False
