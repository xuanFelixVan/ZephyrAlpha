# [A_test] module_id: SRC-TST-1056 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_gitignore_auditor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_gitignore_auditor.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.gitignore_auditor import (
    CRITICAL_FILE_EXTENSIONS,
    CRITICAL_FILE_PATTERNS,
    GENERATED_FILE_EXTENSIONS,
    GitignoreAudit,
    _is_ignored,
    audit_gitignore,
    find_over_ignored_critical,
    find_uncovered_types,
    find_untracked_generated,
    parse_gitignore,
)


class TestGitignoreAuditInstantiation:
    def test_default_fields(self):
        audit = GitignoreAudit()
        assert audit.project_root == ""
        assert audit.gitignore_rules == []
        assert audit.untracked_generated == []
        assert audit.over_ignored == []
        assert audit.uncovered_types == []
        assert audit.suggestions == []

    def test_custom_fields(self):
        audit = GitignoreAudit(
            project_root="/tmp",
            gitignore_rules=["*.pyc"],
            untracked_generated=["cache.pkl"],
            over_ignored=["config.yaml"],
            uncovered_types=["*.xyz"],
            suggestions=["Add *.xyz"],
        )
        assert audit.project_root == "/tmp"
        assert len(audit.gitignore_rules) == 1
        assert "cache.pkl" in audit.untracked_generated


class TestConstants:
    def test_generated_extensions_non_empty(self):
        assert len(GENERATED_FILE_EXTENSIONS) > 0

    def test_critical_extensions_non_empty(self):
        assert len(CRITICAL_FILE_EXTENSIONS) > 0

    def test_critical_patterns_non_empty(self):
        assert len(CRITICAL_FILE_PATTERNS) > 0

    def test_common_extensions_present(self):
        assert ".pyc" in GENERATED_FILE_EXTENSIONS
        assert ".py" in CRITICAL_FILE_EXTENSIONS
        assert ".yaml" in CRITICAL_FILE_EXTENSIONS
        assert ".log" in GENERATED_FILE_EXTENSIONS
        assert ".db" in GENERATED_FILE_EXTENSIONS


class TestIsIgnored:
    def test_exact_match(self):
        assert _is_ignored("model.pkl", ["*.pkl"]) is True

    def test_no_match(self):
        assert _is_ignored("main.py", ["*.pkl"]) is False

    def test_basename_match(self):
        assert _is_ignored("subdir/model.pkl", ["*.pkl"]) is True

    def test_empty_rules(self):
        assert _is_ignored("anything.txt", []) is False


class TestParseGitignore:
    def test_no_gitignore_file(self, tmp_path):
        rules = parse_gitignore(str(tmp_path))
        assert rules == []

    def test_parse_valid_gitignore(self, tmp_path):
        gi = tmp_path / ".gitignore"
        gi.write_text("*.pyc\n__pycache__/\n# comment\n\n*.log\n", encoding="utf-8")
        rules = parse_gitignore(str(tmp_path))
        assert "*.pyc" in rules
        assert "__pycache__" in rules
        assert "*.log" in rules
        assert not any(r.startswith("#") for r in rules)

    def test_strips_trailing_slash(self, tmp_path):
        gi = tmp_path / ".gitignore"
        gi.write_text("build/\n", encoding="utf-8")
        rules = parse_gitignore(str(tmp_path))
        assert "build" in rules
        assert "build/" not in rules

    def test_skips_blank_lines(self, tmp_path):
        gi = tmp_path / ".gitignore"
        gi.write_text("*.pyc\n\n\n*.log\n", encoding="utf-8")
        rules = parse_gitignore(str(tmp_path))
        assert len(rules) == 2

    def test_empty_gitignore(self, tmp_path):
        gi = tmp_path / ".gitignore"
        gi.write_text("", encoding="utf-8")
        rules = parse_gitignore(str(tmp_path))
        assert rules == []


class TestFindUntrackedGenerated:
    def test_no_generated_files(self, tmp_path):
        result = find_untracked_generated(str(tmp_path), [])
        assert isinstance(result, list)
        assert len(result) == 0

    def test_finds_untracked_pkl(self, tmp_path):
        pkl_file = tmp_path / "model.pkl"
        pkl_file.write_bytes(b"fake pkl")
        result = find_untracked_generated(str(tmp_path), [])
        assert any("model.pkl" in r for r in result)

    def test_ignores_tracked_pkl(self, tmp_path):
        pkl_file = tmp_path / "model.pkl"
        pkl_file.write_bytes(b"fake pkl")
        result = find_untracked_generated(str(tmp_path), ["*.pkl"])
        assert not any("model.pkl" in r for r in result)

    def test_skips_git_dirs(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        db_file = git_dir / "index.db"
        db_file.write_bytes(b"fake db")
        result = find_untracked_generated(str(tmp_path), [])
        assert not any(".git" in r for r in result)

    def test_finds_db_files(self, tmp_path):
        db_file = tmp_path / "data.db"
        db_file.write_bytes(b"fake db")
        result = find_untracked_generated(str(tmp_path), [])
        assert any("data.db" in r for r in result)


class TestFindOverIgnoredCritical:
    def test_no_over_ignored(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("print('hello')", encoding="utf-8")
        result = find_over_ignored_critical(str(tmp_path), [])
        assert isinstance(result, list)
        assert len(result) == 0

    def test_finds_over_ignored_yaml(self, tmp_path):
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("key: value", encoding="utf-8")
        result = find_over_ignored_critical(str(tmp_path), ["*.yaml"])
        assert any("config.yaml" in r for r in result)

    def test_critical_file_not_ignored(self, tmp_path):
        py_file = tmp_path / "main.py"
        py_file.write_text("print('hello')", encoding="utf-8")
        result = find_over_ignored_critical(str(tmp_path), ["*.pkl"])
        assert not any("main.py" in r for r in result)


class TestFindUncoveredTypes:
    def test_finds_uncovered_extension(self, tmp_path):
        xyz_file = tmp_path / "data.xyz"
        xyz_file.write_text("xyz data", encoding="utf-8")
        result = find_uncovered_types(str(tmp_path), [])
        assert any(".xyz" in r for r in result)

    def test_covered_extension_excluded(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("print('hello')", encoding="utf-8")
        result = find_uncovered_types(str(tmp_path), ["*.py"])
        assert not any(".py" in r for r in result)

    def test_returns_sorted(self, tmp_path):
        result = find_uncovered_types(str(tmp_path), [])
        assert result == sorted(result)

    def test_no_files(self, tmp_path):
        result = find_uncovered_types(str(tmp_path), [])
        assert isinstance(result, list)


class TestAuditGitignore:
    def test_returns_gitignore_audit(self, tmp_path):
        result = audit_gitignore(str(tmp_path))
        assert isinstance(result, GitignoreAudit)
        assert result.project_root == str(tmp_path)

    def test_with_gitignore_file(self, tmp_path):
        gi = tmp_path / ".gitignore"
        gi.write_text("*.pyc\n*.log\n", encoding="utf-8")
        result = audit_gitignore(str(tmp_path))
        assert "*.pyc" in result.gitignore_rules
        assert "*.log" in result.gitignore_rules

    def test_suggestions_limited_to_10(self, tmp_path):
        result = audit_gitignore(str(tmp_path))
        assert len(result.suggestions) <= 10

    def test_audit_empty_project(self, tmp_path):
        result = audit_gitignore(str(tmp_path))
        assert isinstance(result.untracked_generated, list)
        assert isinstance(result.over_ignored, list)
        assert isinstance(result.uncovered_types, list)
