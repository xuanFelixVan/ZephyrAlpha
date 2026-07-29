# [A_test] module_id: MOD-GOV_all_completer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §test
# [MODULE] tests.test_all_completer
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_all_completer.py
# [TTL] task_bound

import os
import re
import tempfile
from pathlib import Path

import pytest

completer_mod = pytest.importorskip(
    "zephyr.infrastructure.auto_fix_engine.all_completer", reason="all_completer not available"
)
AllCompleter = completer_mod.AllCompleter

models = pytest.importorskip("zephyr.infrastructure.auto_fix_engine.models", reason="models not available")
FixStatus = models.FixStatus
FixLevel = models.FixLevel


class TestAllCompleterInstantiation:
    def test_fixer_id(self):
        comp = AllCompleter()
        assert comp.fixer_id == "all_completer"

    def test_action_type(self):
        comp = AllCompleter()
        assert comp.action_type == "all_completion"

    def test_level_is_l1_rule(self):
        comp = AllCompleter()
        assert comp.level == FixLevel.L1_RULE


class TestAllCompleterScan:
    def test_scan_returns_list(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        comp = AllCompleter()
        result = comp.scan()
        assert isinstance(result, list)

    def test_scan_detects_missing_all(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "__init__.py").write_text("def public_func():\n    return 1\n", encoding="utf-8")
        comp = AllCompleter()
        result = comp.scan()
        assert any(f["type"] == "missing_all" for f in result)

    def test_scan_empty_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        comp = AllCompleter()
        result = comp.scan()
        assert result == []


class TestAllCompleterFix:
    def test_fix_nonexistent_target(self):
        comp = AllCompleter()
        action = comp.fix("/nonexistent/path/__init__.py")
        assert action.status == FixStatus.FAILED

    def test_fix_adds_missing_all(self):
        comp = AllCompleter()
        content = "def public_func():\n    return 1\n\ndef _private_func():\n    return 2\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = comp.fix(path, dry_run=True)
            assert action.status == FixStatus.COMPLETED
            assert action.after != ""
            assert "__all__" in action.after
            assert "public_func" in action.after
            all_match = re.search(r"__all__\s*=\s*\[([^\]]*)\]", action.after)
            assert all_match is not None
            all_content = all_match.group(1)
            assert "_private_func" not in all_content
        finally:
            os.unlink(path)

    def test_fix_completes_existing_all(self):
        comp = AllCompleter()
        content = '__all__ = ["existing_func"]\n\ndef existing_func():\n    return 1\n\ndef new_func():\n    return 2\n'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = comp.fix(path, dry_run=True)
            assert action.status == FixStatus.COMPLETED
            if action.after:
                assert "new_func" in action.after
        finally:
            os.unlink(path)

    def test_fix_no_public_symbols(self):
        comp = AllCompleter()
        content = "def _private():\n    return 1\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = comp.fix(path, dry_run=True)
            assert action.status == FixStatus.COMPLETED
            assert "note" in action.metadata
        finally:
            os.unlink(path)

    def test_fix_dry_run_does_not_modify_file(self):
        comp = AllCompleter()
        content = "def public_func():\n    return 1\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            original = Path(path).read_text(encoding="utf-8")
            comp.fix(path, dry_run=True)
            current = Path(path).read_text(encoding="utf-8")
            assert current == original
        finally:
            os.unlink(path)


class TestAllCompleterValidate:
    def test_validate_nonexistent_target(self):
        comp = AllCompleter()
        result = comp.validate("/nonexistent/path/__init__.py")
        assert result.valid is False

    def test_validate_missing_all(self):
        comp = AllCompleter()
        content = "def public_func():\n    return 1\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            result = comp.validate(path)
            assert result.valid is False
            assert "missing" in result.error.lower() or "Missing" in result.error
        finally:
            os.unlink(path)

    def test_validate_complete_all(self):
        comp = AllCompleter()
        content = '__all__ = ["public_func"]\n\ndef public_func():\n    return 1\n'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            result = comp.validate(path)
            assert result.valid is True
            assert result.check_name == "all_completion"
        finally:
            os.unlink(path)


class TestAllCompleterRollback:
    def test_rollback_returns_false(self):
        comp = AllCompleter()
        assert comp.rollback("any_target") is False


class TestAllCompleterInternalMethods:
    def test_extract_public_symbols_excludes_private(self):
        comp = AllCompleter()
        content = "def public_func():\n    return 1\n\ndef _private_func():\n    return 2\n"
        symbols = comp.extract_public_symbols(content)
        assert "public_func" in symbols
        assert "_private_func" not in symbols

    def test_extract_public_symbols_includes_classes(self):
        comp = AllCompleter()
        content = "class MyClass:\n    return 1\n"
        symbols = comp.extract_public_symbols(content)
        assert "MyClass" in symbols

    def test_parse_all_returns_list(self):
        comp = AllCompleter()
        content = '__all__ = ["func1", "func2"]\n'
        result = comp.parse_all(content)
        assert "func1" in result
        assert "func2" in result

    def test_parse_all_empty_content(self):
        comp = AllCompleter()
        result = comp.parse_all("")
        assert result == []

    def test_extract_public_symbols_syntax_error(self):
        comp = AllCompleter()
        result = comp.extract_public_symbols("def broken(:\n")
        assert isinstance(result, list)
