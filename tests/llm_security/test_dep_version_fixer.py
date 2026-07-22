# [A_test] module_id: MOD-GOV_dep_version_fixer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_dep_version_fixer
# [INVARIANTS] 测试覆盖scan/fix/validate/rollback/_is_higher;边界:空输入/None/异常
# [MODIFY-GUARD] blueprint.md §3
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.infrastructure.auto_fix_engine import dep_version_fixer as dep_mod
from zephyr.infrastructure.auto_fix_engine.dep_version_fixer import DepVersionFixer
from zephyr.infrastructure.auto_fix_engine.models import FixStatus, ValidationResult


@pytest.fixture
def fixer():
    return DepVersionFixer()


@pytest.fixture
def conflicting_requirements(tmp_path):
    p = tmp_path / "requirements.txt"
    p.write_text(
        "requests==2.28.0\nflask>=1.0.0\nrequests==2.31.0\n",
        encoding="utf-8",
    )
    return str(p)


@pytest.fixture
def clean_requirements(tmp_path):
    p = tmp_path / "requirements.txt"
    p.write_text(
        "requests==2.31.0\nflask>=1.0.0\n",
        encoding="utf-8",
    )
    return str(p)


class TestDepVersionFixerInstantiation:
    def test_fixer_id(self, fixer):
        assert fixer.fixer_id == "dep_version_fixer"

    def test_action_type(self, fixer):
        assert fixer.action_type == "dep_version_fix"

    def test_dimension(self, fixer):
        assert fixer.dimension == "DIM-DEP-VERSION-001"


class TestScan:
    def test_scan_returns_list(self, fixer, tmp_path, monkeypatch):
        monkeypatch.setattr(dep_mod, "REPO_ROOT", tmp_path)
        result = fixer.scan()
        assert isinstance(result, list)

    def test_scan_finds_conflicts(self, tmp_path, monkeypatch, fixer):
        monkeypatch.setattr(dep_mod, "REPO_ROOT", tmp_path)
        req = tmp_path / "requirements.txt"
        req.write_text("requests==2.28.0\nrequests==2.31.0\n", encoding="utf-8")
        result = fixer.scan()
        assert any(f["type"] == "version_conflict" for f in result)

    def test_scan_no_conflicts(self, tmp_path, monkeypatch, fixer):
        monkeypatch.setattr(dep_mod, "REPO_ROOT", tmp_path)
        req = tmp_path / "requirements.txt"
        req.write_text("requests==2.31.0\nflask>=1.0.0\n", encoding="utf-8")
        result = fixer.scan()
        assert not any(f["type"] == "version_conflict" for f in result)


class TestFix:
    def test_fix_nonexistent_target(self, fixer):
        action = fixer.fix("/nonexistent/path/requirements.txt")
        assert action.status == FixStatus.FAILED

    def test_fix_no_conflicts(self, fixer, clean_requirements):
        action = fixer.fix(clean_requirements)
        assert action.status == FixStatus.COMPLETED

    def test_fix_with_conflicts_dry_run(self, fixer, conflicting_requirements):
        action = fixer.fix(conflicting_requirements, dry_run=True)
        assert action.status == FixStatus.COMPLETED

    def test_fix_with_conflicts_applied(self, fixer, conflicting_requirements):
        action = fixer.fix(conflicting_requirements, dry_run=False)
        assert action.status == FixStatus.COMPLETED
        with open(conflicting_requirements, encoding="utf-8") as f:
            content = f.read()
        assert "2.31.0" in content

    def test_fix_preserves_comments(self, tmp_path, fixer):
        req = tmp_path / "requirements.txt"
        req.write_text("# This is a comment\nrequests==2.31.0\n", encoding="utf-8")
        action = fixer.fix(str(req))
        with open(str(req), encoding="utf-8") as f:
            content = f.read()
        assert "# This is a comment" in content


class TestIsHigher:
    def test_higher_major(self, fixer):
        assert fixer._is_higher("2.0.0", "1.0.0") is True

    def test_higher_minor(self, fixer):
        assert fixer._is_higher("1.2.0", "1.1.0") is True

    def test_higher_patch(self, fixer):
        assert fixer._is_higher("1.0.1", "1.0.0") is True

    def test_not_higher(self, fixer):
        assert fixer._is_higher("1.0.0", "2.0.0") is False

    def test_equal(self, fixer):
        assert fixer._is_higher("1.0.0", "1.0.0") is False

    def test_invalid_version(self, fixer):
        assert fixer._is_higher("abc", "1.0.0") is False


class TestValidate:
    def test_validate_nonexistent_target(self, fixer):
        result = fixer.validate("/nonexistent/path/requirements.txt")
        assert isinstance(result, ValidationResult)
        assert not result.valid
        assert result.error == "Target not found"

    def test_validate_no_conflicts(self, fixer, clean_requirements):
        result = fixer.validate(clean_requirements)
        assert result.valid
        assert result.evidence == "No version conflicts"

    def test_validate_with_conflicts(self, fixer, conflicting_requirements):
        result = fixer.validate(conflicting_requirements)
        assert not result.valid
        assert "Version conflicts remain" in result.error


class TestRollback:
    def test_rollback_returns_false(self, fixer):
        assert fixer.rollback("any_path") is False
