# [A_test] module_id: MOD-GOV_scaffold_registrar | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_scaffold_registrar
# [INVARIANTS] 只注册不删除;注册到manifest/registry/__init__.py
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml scaffold_registrar段
# [CONSUMERS] CI/CD;pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_scaffold_registrar.py
# [TTL] task_bound

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from zephyr.infrastructure.auto_fix_engine import scaffold_registrar as scaffold_mod
from zephyr.infrastructure.auto_fix_engine.models import FixLevel, FixStatus
from zephyr.infrastructure.auto_fix_engine.scaffold_registrar import ScaffoldRegistrar


class TestScaffoldRegistrarInstantiation:
    def test_creates_instance_with_correct_fixer_id(self):
        reg = ScaffoldRegistrar()
        assert reg.fixer_id == "scaffold_registrar"

    def test_creates_instance_with_correct_action_type(self):
        reg = ScaffoldRegistrar()
        assert reg.action_type == "scaffold_registration"

    def test_creates_instance_with_correct_level(self):
        reg = ScaffoldRegistrar()
        assert reg.level == FixLevel.L1_RULE

    def test_creates_instance_with_correct_dimension(self):
        reg = ScaffoldRegistrar()
        assert reg.dimension == "DIM-TYPE-002"


class TestScaffoldRegistrarScan:
    def test_scan_returns_list(self):
        reg = ScaffoldRegistrar()
        with patch.object(Path, "rglob", return_value=[]):
            result = reg.scan()
        assert isinstance(result, list)

    def test_scan_finds_unregistered_script(self):
        reg = ScaffoldRegistrar()
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()
            script_file = scripts_dir / "my_script.py"
            script_file.write_text("print('hello')\n", encoding="utf-8")
            manifest_path = scripts_dir / "script-manifest.yaml"
            manifest_path.write_text("scripts: []\n", encoding="utf-8")
            with patch.object(scaffold_mod, "REPO_ROOT", Path(tmpdir)):
                with patch.object(Path, "rglob") as mock_rglob:

                    def rglob_side_effect(pattern):
                        if pattern == "*.py":
                            return [script_file]
                        return []

                    mock_rglob.side_effect = rglob_side_effect
                    findings = reg.scan()
            assert any(f["type"] == "unregistered_script" for f in findings)

    def test_scan_skips_underscore_prefixed_scripts(self):
        reg = ScaffoldRegistrar()
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()
            underscore_script = scripts_dir / "_helper.py"
            underscore_script.write_text("pass\n", encoding="utf-8")
            with (
                patch.object(Path, "rglob", return_value=[underscore_script]),
                patch(
                    "zephyr.infrastructure.auto_fix_engine.scaffold_registrar.os.getcwd",
                    return_value=tmpdir,
                ),
            ):
                findings = reg.scan()
            assert not any(f.get("relative_path", "").endswith("_helper.py") for f in findings)

    def test_scan_handles_missing_manifest_gracefully(self):
        reg = ScaffoldRegistrar()
        with tempfile.TemporaryDirectory() as tmpdir:
            with (
                patch.object(Path, "rglob", return_value=[]),
                patch(
                    "zephyr.infrastructure.auto_fix_engine.scaffold_registrar.os.getcwd",
                    return_value=tmpdir,
                ),
            ):
                findings = reg.scan()
            assert isinstance(findings, list)


class TestScaffoldRegistrarFix:
    def test_fix_returns_failed_for_nonexistent_target(self):
        reg = ScaffoldRegistrar()
        action = reg.fix("/nonexistent/file.py")
        assert action.status == FixStatus.FAILED

    def test_fix_registers_script_in_manifest(self):
        reg = ScaffoldRegistrar()
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()
            script_file = scripts_dir / "my_script.py"
            script_file.write_text("print('hello')\n", encoding="utf-8")
            manifest_path = scripts_dir / "script-manifest.yaml"
            manifest_path.write_text("scripts: []\n", encoding="utf-8")
            target_rel = "scripts/my_script.py"
            os.chdir(tmpdir)
            try:
                action = reg.fix(target_rel)
            finally:
                os.chdir(original_cwd)
            assert action.status == FixStatus.COMPLETED
            assert action.metadata.get("registration_type") == "script_manifest"

    def test_fix_dry_run_does_not_modify_manifest(self):
        reg = ScaffoldRegistrar()
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()
            script_file = scripts_dir / "my_script.py"
            script_file.write_text("print('hello')\n", encoding="utf-8")
            manifest_path = scripts_dir / "script-manifest.yaml"
            manifest_path.write_text("scripts: []\n", encoding="utf-8")
            target_rel = "scripts/my_script.py"
            original_manifest = manifest_path.read_text(encoding="utf-8")
            os.chdir(tmpdir)
            try:
                reg.fix(target_rel, dry_run=True)
            finally:
                os.chdir(original_cwd)
            assert manifest_path.read_text(encoding="utf-8") == original_manifest

    def test_fix_returns_failed_for_unknown_target_type(self):
        reg = ScaffoldRegistrar()
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "data.json"
            target_file.write_text("{}", encoding="utf-8")
            os.chdir(tmpdir)
            try:
                action = reg.fix("data.json")
            finally:
                os.chdir(original_cwd)
        assert action.status == FixStatus.FAILED
        assert "Unknown registration target type" in action.metadata.get("error", "")


class TestScaffoldRegistrarValidate:
    def test_validate_returns_invalid_for_nonexistent_target(self):
        reg = ScaffoldRegistrar()
        result = reg.validate("/nonexistent/file.py")
        assert result.valid is False
        assert "Target not found" in result.error

    def test_validate_script_in_manifest(self):
        reg = ScaffoldRegistrar()
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()
            script_file = scripts_dir / "my_script.py"
            script_file.write_text("print('hello')\n", encoding="utf-8")
            manifest_path = scripts_dir / "script-manifest.yaml"
            manifest_path.write_text("scripts:\n  - path: scripts/my_script.py\n", encoding="utf-8")
            os.chdir(tmpdir)
            try:
                result = reg.validate("scripts/my_script.py")
            finally:
                os.chdir(original_cwd)
            assert result.valid is True

    def test_validate_script_not_in_manifest(self):
        reg = ScaffoldRegistrar()
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            scripts_dir = Path(tmpdir) / "scripts"
            scripts_dir.mkdir()
            missing_script = scripts_dir / "missing.py"
            missing_script.write_text("pass\n", encoding="utf-8")
            manifest_path = scripts_dir / "script-manifest.yaml"
            manifest_path.write_text("scripts: []\n", encoding="utf-8")
            os.chdir(tmpdir)
            try:
                result = reg.validate("scripts/missing.py")
            finally:
                os.chdir(original_cwd)
            assert result.valid is False


class TestScaffoldRegistrarRollback:
    def test_rollback_returns_false(self):
        reg = ScaffoldRegistrar()
        assert reg.rollback("any_target") is False

    def test_rollback_returns_false_for_empty_target(self):
        reg = ScaffoldRegistrar()
        assert reg.rollback("") is False
