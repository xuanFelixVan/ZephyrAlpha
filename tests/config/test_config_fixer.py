# [A_test] module_id: MOD-GOV_config_fixer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §test
# [MODULE] tests.test_config_fixer
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_config_fixer.py
# [TTL] task_bound

import os
import tempfile
from pathlib import Path

import pytest

config_mod = pytest.importorskip(
    "zephyr.infrastructure.auto_fix_engine.config_fixer", reason="config_fixer not available"
)
ConfigFixer = config_mod.ConfigFixer

models = pytest.importorskip("zephyr.infrastructure.auto_fix_engine.models", reason="models not available")
FixStatus = models.FixStatus
FixLevel = models.FixLevel


class TestConfigFixerInstantiation:
    def test_fixer_id(self):
        fixer = ConfigFixer()
        assert fixer.fixer_id == "config_fixer"

    def test_action_type(self):
        fixer = ConfigFixer()
        assert fixer.action_type == "config_fix"

    def test_level_is_l1_rule(self):
        fixer = ConfigFixer()
        assert fixer.level == FixLevel.L1_RULE


class TestConfigFixerScan:
    def test_scan_returns_list(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        fixer = ConfigFixer()
        result = fixer.scan()
        assert isinstance(result, list)

    def test_scan_detects_merge_conflict(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "test.yaml").write_text(
            "key: val\n<<<<<<< HEAD\na: 1\n=======\nb: 2\n>>>>>>> br\n", encoding="utf-8"
        )
        fixer = ConfigFixer()
        result = fixer.scan()
        assert any(f["type"] == "merge_conflict_markers" for f in result)

    def test_scan_empty_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        fixer = ConfigFixer()
        result = fixer.scan()
        assert result == []


class TestConfigFixerFix:
    def test_fix_nonexistent_target(self):
        fixer = ConfigFixer()
        action = fixer.fix("/nonexistent/path/config.yaml")
        assert action.status == FixStatus.FAILED
        assert "error" in action.metadata

    def test_fix_merge_conflicts_dry_run(self):
        fixer = ConfigFixer()
        content = "key1: value1\n<<<<<<< HEAD\nkey2: ours\n=======\nkey2: theirs\n>>>>>>> branch\nkey3: value3\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = fixer.fix(path, dry_run=True)
            assert action.status == FixStatus.COMPLETED
            current = Path(path).read_text(encoding="utf-8")
            assert "<<<<<<< HEAD" in current
        finally:
            os.unlink(path)

    def test_fix_merge_conflicts_writes(self):
        fixer = ConfigFixer()
        content = "key1: value1\n<<<<<<< HEAD\nkey2: ours\n=======\nkey2: theirs\n>>>>>>> branch\nkey3: value3\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = fixer.fix(path, dry_run=False)
            assert action.status == FixStatus.COMPLETED
            current = Path(path).read_text(encoding="utf-8")
            assert "<<<<<<<" not in current
            assert "=======" not in current
            assert ">>>>>>>" not in current
        finally:
            os.unlink(path)

    def test_fix_tabs(self):
        fixer = ConfigFixer()
        content = "key:\n\tsub: value\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = fixer.fix(path, dry_run=False)
            assert action.status == FixStatus.COMPLETED
            current = Path(path).read_text(encoding="utf-8")
            assert "\t" not in current
        finally:
            os.unlink(path)

    def test_fix_trailing_whitespace(self):
        fixer = ConfigFixer()
        content = "key: value   \nother: data  \n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = fixer.fix(path, dry_run=False)
            assert action.status == FixStatus.COMPLETED
            current = Path(path).read_text(encoding="utf-8")
            for line in current.splitlines():
                if line.strip():
                    assert line == line.rstrip()
        finally:
            os.unlink(path)

    def test_fix_no_issues_found(self):
        fixer = ConfigFixer()
        content = "key: value\nother: data\n"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            path = f.name
        try:
            action = fixer.fix(path, dry_run=False)
            assert action.status == FixStatus.COMPLETED
            assert "note" in action.metadata
        finally:
            os.unlink(path)


class TestConfigFixerValidate:
    def test_validate_nonexistent_target(self):
        fixer = ConfigFixer()
        result = fixer.validate("/nonexistent/path/config.yaml")
        assert result.valid is False

    def test_validate_valid_yaml(self):
        fixer = ConfigFixer()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write("key: value\n")
            f.flush()
            path = f.name
        try:
            result = fixer.validate(path)
            assert result.valid is True
            assert result.check_name == "config_fix"
        finally:
            os.unlink(path)

    def test_validate_merge_conflict_markers(self):
        fixer = ConfigFixer()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            f.write("key: value\n<<<<<<< HEAD\nother: data\n=======\nother: data2\n>>>>>>> branch\n")
            f.flush()
            path = f.name
        try:
            result = fixer.validate(path)
            assert result.valid is False
            assert "merge conflict" in result.error.lower() or "Merge conflict" in result.error
        finally:
            os.unlink(path)


class TestConfigFixerRollback:
    def test_rollback_returns_false(self):
        fixer = ConfigFixer()
        assert fixer.rollback("any_target") is False


class TestConfigFixerInternalMethods:
    def test_fix_merge_conflicts_keeps_longer_side(self):
        fixer = ConfigFixer()
        fixes = []
        content = "<<<<<<< HEAD\nlonger ours content here\n=======\nshort\n>>>>>>> branch\n"
        result = fixer._fix_merge_conflicts(content, fixes)
        assert "longer ours content here" in result
        assert "short" not in result
        assert len(fixes) == 1

    def test_fix_tabs_replaces_with_spaces(self):
        fixer = ConfigFixer()
        fixes = []
        content = "key:\n\tsub: value\n"
        result = fixer._fix_tabs(content, fixes)
        assert "    " in result
        assert "\t" not in result

    def test_fix_trailing_whitespace_strips(self):
        fixer = ConfigFixer()
        fixes = []
        content = "key: value   \n"
        result = fixer._fix_trailing_whitespace(content, fixes)
        assert result.strip() == "key: value"
