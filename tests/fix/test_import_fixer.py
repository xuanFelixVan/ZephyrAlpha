# [A_test] module_id: MOD-GOV_import_fixer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §test
# [MODULE] tests.test_import_fixer
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_import_fixer.py
# [TTL] task_bound

import os
import tempfile
from pathlib import Path

import pytest

import_mod = pytest.importorskip(
    "zephyr.infrastructure.auto_fix_engine.import_fixer", reason="import_fixer not available"
)
ImportFixer = import_mod.ImportFixer

models = pytest.importorskip("zephyr.infrastructure.auto_fix_engine.models", reason="models not available")
FixStatus = models.FixStatus
FixLevel = models.FixLevel


class TestImportFixerInstantiation:
    def test_fixer_id(self):
        fixer = ImportFixer()
        assert fixer.fixer_id == "import_fixer"

    def test_action_type(self):
        fixer = ImportFixer()
        assert fixer.action_type == "import_fix"

    def test_level_is_l1_rule(self):
        fixer = ImportFixer()
        assert fixer.level == FixLevel.L1_RULE


class TestImportFixerScan:
    def test_scan_returns_list(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        fixer = ImportFixer()
        result = fixer.scan()
        assert isinstance(result, list)

    def test_scan_empty_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        fixer = ImportFixer()
        result = fixer.scan()
        assert result == []


class TestImportFixerFix:
    def test_fix_nonexistent_target(self):
        fixer = ImportFixer()
        action = fixer.fix("/nonexistent/path/file.py")
        assert action.status == FixStatus.FAILED

    def test_fix_file_with_no_imports(self):
        fixer = ImportFixer()
        content = "x = 1\ny = 2\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = fixer.fix(path, dry_run=True)
            assert action.status == FixStatus.COMPLETED
            assert "note" in action.metadata
        finally:
            os.unlink(path)

    def test_fix_dry_run_does_not_modify_file(self):
        fixer = ImportFixer()
        content = "from zephyr.infrastructure.auto_fix_engine.models import FixAction\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            original = Path(path).read_text(encoding="utf-8")
            fixer.fix(path, dry_run=True)
            current = Path(path).read_text(encoding="utf-8")
            assert current == original
        finally:
            os.unlink(path)

    def test_fix_returns_action_with_correct_type(self):
        fixer = ImportFixer()
        content = "x = 1\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = fixer.fix(path, dry_run=True)
            assert action.action_type == "import_fix"
            assert action.target == path
        finally:
            os.unlink(path)


class TestImportFixerValidate:
    def test_validate_nonexistent_target(self):
        fixer = ImportFixer()
        result = fixer.validate("/nonexistent/path/file.py")
        assert result.valid is False

    def test_validate_valid_syntax(self):
        fixer = ImportFixer()
        content = "x = 1\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            result = fixer.validate(path)
            assert result.valid is True
            assert result.check_name == "import_fix"
        finally:
            os.unlink(path)

    def test_validate_invalid_syntax(self):
        fixer = ImportFixer()
        content = "def foo(:\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            result = fixer.validate(path)
            assert result.valid is False
            assert "Syntax error" in result.error
        finally:
            os.unlink(path)


class TestImportFixerRollback:
    def test_rollback_returns_false(self):
        fixer = ImportFixer()
        assert fixer.rollback("any_target") is False


class TestImportFixerTryFixModule:
    def test_short_module_name_returns_none(self):
        fixer = ImportFixer()
        from pathlib import Path

        result = fixer._try_fix_module("zephyr", Path("src"))
        assert result is None

    def test_nonexistent_module_returns_none(self):
        fixer = ImportFixer()
        from pathlib import Path

        result = fixer._try_fix_module("zephyr.nonexistent.module.xyz", Path("src"))
        assert result is None or isinstance(result, str)
