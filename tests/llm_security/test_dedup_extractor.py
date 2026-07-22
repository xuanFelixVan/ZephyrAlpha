# [A_test] module_id: MOD-GOV_dedup_extractor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §test
# [MODULE] tests.test_dedup_extractor
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_dedup_extractor.py
# [TTL] task_bound

import os
import tempfile
from pathlib import Path

import pytest

dedup_mod = pytest.importorskip(
    "zephyr.infrastructure.auto_fix_engine.dedup_extractor", reason="dedup_extractor not available"
)
DedupExtractor = dedup_mod.DedupExtractor

models = pytest.importorskip("zephyr.infrastructure.auto_fix_engine.models", reason="models not available")
FixStatus = models.FixStatus
FixLevel = models.FixLevel


class TestDedupExtractorInstantiation:
    def test_default_min_occurrences(self):
        ext = DedupExtractor()
        assert ext._min_occurrences == 3

    def test_custom_min_occurrences(self):
        ext = DedupExtractor(min_occurrences=5)
        assert ext._min_occurrences == 5

    def test_fixer_id(self):
        ext = DedupExtractor()
        assert ext.fixer_id == "dedup_extractor"

    def test_action_type(self):
        ext = DedupExtractor()
        assert ext.action_type == "dedup_extraction"

    def test_level_is_l1_rule(self):
        ext = DedupExtractor()
        assert ext.level == FixLevel.L1_RULE


class TestDedupExtractorScan:
    def test_scan_returns_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dedup_mod, "REPO_ROOT", tmp_path)
        ext = DedupExtractor()
        result = ext.scan()
        assert isinstance(result, list)

    def test_scan_finding_structure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dedup_mod, "REPO_ROOT", tmp_path)
        code = "def foo():\n    x = 1\n    y = 2\n    z = 3\n    w = 4\n    return x + y + z + w\n"
        for i in range(4):
            (tmp_path / f"mod_{i}.py").write_text(code, encoding="utf-8")
        ext = DedupExtractor(min_occurrences=3)
        result = ext.scan()
        for finding in result:
            assert "hash" in finding
            assert "occurrences" in finding
            assert "locations" in finding
            assert "type" in finding
            assert finding["type"] == "code_duplication"

    def test_scan_respects_min_occurrences(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dedup_mod, "REPO_ROOT", tmp_path)
        ext = DedupExtractor(min_occurrences=999)
        result = ext.scan()
        assert len(result) == 0

    def test_scan_empty_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dedup_mod, "REPO_ROOT", tmp_path)
        ext = DedupExtractor()
        result = ext.scan()
        assert result == []


class TestDedupExtractorFix:
    def test_fix_nonexistent_target(self):
        ext = DedupExtractor()
        action = ext.fix("/nonexistent/path/file.py")
        assert action.status == FixStatus.FAILED

    def test_fix_dry_run_does_not_modify_file(self):
        ext = DedupExtractor()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("def foo():\n    x = 1\n    y = 2\n    return x + y\n")
            f.flush()
            path = f.name
        try:
            original = Path(path).read_text(encoding="utf-8")
            action = ext.fix(path, dry_run=True)
            current = Path(path).read_text(encoding="utf-8")
            assert current == original
        finally:
            os.unlink(path)

    def test_fix_valid_file_returns_action(self):
        ext = DedupExtractor()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("def foo():\n    x = 1\n    return x\n")
            f.flush()
            path = f.name
        try:
            action = ext.fix(path, dry_run=True)
            assert action.action_type == "dedup_extraction"
            assert action.target == path
        finally:
            os.unlink(path)


class TestDedupExtractorValidate:
    def test_validate_nonexistent_target(self):
        ext = DedupExtractor()
        result = ext.validate("/nonexistent/path/file.py")
        assert result.valid is False
        assert "not found" in result.error.lower() or "Target not found" in result.error

    def test_validate_valid_syntax(self):
        ext = DedupExtractor()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("x = 1\n")
            f.flush()
            path = f.name
        try:
            result = ext.validate(path)
            assert result.valid is True
            assert result.check_name == "dedup_extraction"
        finally:
            os.unlink(path)

    def test_validate_invalid_syntax(self):
        ext = DedupExtractor()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("def foo(:\n")
            f.flush()
            path = f.name
        try:
            result = ext.validate(path)
            assert result.valid is False
            assert "Syntax error" in result.error
        finally:
            os.unlink(path)


class TestDedupExtractorRollback:
    def test_rollback_returns_false(self):
        ext = DedupExtractor()
        assert ext.rollback("any_target") is False


class TestDedupExtractorNormalize:
    def test_normalize_strips_comments(self):
        ext = DedupExtractor()
        code = "x = 1\n# comment\ny = 2"
        result = ext._normalize_code(code)
        assert "#" not in result
        assert "x = 1" in result
        assert "y = 2" in result

    def test_normalize_strips_blank_lines(self):
        ext = DedupExtractor()
        code = "x = 1\n\n\ny = 2"
        result = ext._normalize_code(code)
        assert "\n\n" not in result

    def test_normalize_empty_input(self):
        ext = DedupExtractor()
        result = ext._normalize_code("")
        assert result == ""
