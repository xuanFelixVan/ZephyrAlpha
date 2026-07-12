# [A_test] module_id: SRC-TST-1421 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_python_compat
# [INVARIANTS] 兼容性检查不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_python_compat.py
# [TTL] task_bound

import os
import tempfile

import pytest

from zephyr.gov_drift.python_compat import (
    PythonCompatIssue,
    _check_stdlib_imports,
    _check_type_hints,
    _check_union_syntax,
    _target_py_minor,
    auto_fix_compat,
    generate_compat_report,
    scan_python_compat,
)


class TestPythonCompatIssue:
    def test_instantiation_defaults(self):
        issue = PythonCompatIssue(
            issue_id="test-1",
            file_path="foo.py",
            line_no=10,
            issue_type="union_syntax",
            current_syntax="str | int",
            suggested_fix="Use Union[str, int]",
        )
        assert issue.issue_id == "test-1"
        assert issue.file_path == "foo.py"
        assert issue.line_no == 10
        assert issue.issue_type == "union_syntax"
        assert issue.target_python == "3.9"
        assert issue.severity == "MAJOR"

    def test_instantiation_custom_target_and_severity(self):
        issue = PythonCompatIssue(
            issue_id="test-2",
            file_path="bar.py",
            line_no=5,
            issue_type="stdlib_incompat",
            current_syntax="import tomllib",
            suggested_fix="Install backport",
            target_python="3.11",
            severity="MINOR",
        )
        assert issue.target_python == "3.11"
        assert issue.severity == "MINOR"

    def test_instantiation_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            PythonCompatIssue()


class TestTargetPyMinor:
    def test_known_versions(self):
        assert _target_py_minor("3.9") == 9
        assert _target_py_minor("3.10") == 10
        assert _target_py_minor("3.12") == 12
        assert _target_py_minor("3.13") == 13

    def test_unknown_version_defaults_to_9(self):
        assert _target_py_minor("2.7") == 9
        assert _target_py_minor("4.0") == 9

    def test_empty_string_defaults_to_9(self):
        assert _target_py_minor("") == 9


class TestCheckUnionSyntax:
    def test_detects_union_syntax_for_old_target(self):
        content = "def foo(x: str | int) -> None:\n    pass\n"
        issues = _check_union_syntax("test.py", content, target_minor=9)
        assert len(issues) >= 1
        assert issues[0].issue_type == "union_syntax"
        assert issues[0].file_path == "test.py"

    def test_no_issue_for_new_target(self):
        content = "def foo(x: str | int) -> None:\n    pass\n"
        issues = _check_union_syntax("test.py", content, target_minor=10)
        assert len(issues) == 0

    def test_empty_content(self):
        issues = _check_union_syntax("empty.py", "", target_minor=9)
        assert issues == []

    def test_multiple_union_occurrences(self):
        content = "x: str | int,\ny: float | None,\n"
        issues = _check_union_syntax("multi.py", content, target_minor=9)
        assert len(issues) == 2


class TestCheckStdlibImports:
    def test_detects_zoneinfo_for_target_39(self):
        content = "import zoneinfo\n"
        issues = _check_stdlib_imports("test.py", content, target_minor=9)
        assert len(issues) == 1
        assert issues[0].issue_type == "stdlib_incompat"
        assert "zoneinfo" in issues[0].current_syntax

    def test_detects_tomllib_for_target_39(self):
        content = "from tomllib import load\n"
        issues = _check_stdlib_imports("test.py", content, target_minor=9)
        assert len(issues) == 1
        assert "tomllib" in issues[0].current_syntax

    def test_no_issue_for_sufficient_target(self):
        content = "import zoneinfo\nfrom tomllib import load\n"
        issues = _check_stdlib_imports("test.py", content, target_minor=11)
        assert len(issues) == 0

    def test_empty_content(self):
        issues = _check_stdlib_imports("empty.py", "", target_minor=9)
        assert issues == []

    def test_from_import_detected(self):
        content = "from zoneinfo import ZoneInfo\n"
        issues = _check_stdlib_imports("test.py", content, target_minor=9)
        assert len(issues) == 1


class TestCheckTypeHints:
    def test_detects_type_alias_for_old_target(self):
        content = "type MyAlias = str | int\n"
        issues = _check_type_hints("test.py", content, target_minor=11)
        assert len(issues) == 1
        assert issues[0].issue_type == "type_alias"
        assert issues[0].severity == "MINOR"

    def test_no_issue_for_python_312(self):
        content = "type MyAlias = str | int\n"
        issues = _check_type_hints("test.py", content, target_minor=12)
        assert len(issues) == 0

    def test_empty_content(self):
        issues = _check_type_hints("empty.py", "", target_minor=11)
        assert issues == []

    def test_multiple_type_aliases(self):
        content = "type A = int\ntype B = str\n"
        issues = _check_type_hints("multi.py", content, target_minor=11)
        assert len(issues) == 2


class TestScanPythonCompat:
    def test_scan_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            issues = scan_python_compat(tmpdir, target_python="3.9")
            assert issues == []

    def test_scan_detects_issues_in_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = os.path.join(tmpdir, "sample.py")
            with open(py_file, "w", encoding="utf-8") as f:
                f.write("import zoneinfo\n\ndef foo(x: str | int) -> None:\n    pass\n")
            issues = scan_python_compat(tmpdir, target_python="3.9")
            issue_types = {i.issue_type for i in issues}
            assert "stdlib_incompat" in issue_types
            assert "union_syntax" in issue_types

    def test_scan_no_issues_for_high_target(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = os.path.join(tmpdir, "sample.py")
            with open(py_file, "w", encoding="utf-8") as f:
                f.write("import zoneinfo\n\ndef foo(x: str | int) -> None:\n    pass\n")
            issues = scan_python_compat(tmpdir, target_python="3.12")
            assert len(issues) == 0

    def test_scan_skips_unreadable_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = os.path.join(tmpdir, "bad.py")
            with open(py_file, "w", encoding="utf-8") as f:
                f.write("x = 1\n")
            os.chmod(py_file, 0o000)
            try:
                issues = scan_python_compat(tmpdir, target_python="3.9")
                assert isinstance(issues, list)
            finally:
                os.chmod(py_file, 0o644)


class TestAutoFixCompat:
    def test_fix_union_syntax(self):
        issues = [
            PythonCompatIssue(
                issue_id="fix-1",
                file_path="a.py",
                line_no=1,
                issue_type="union_syntax",
                current_syntax="str | int",
                suggested_fix="Use Union",
            )
        ]
        fixes = auto_fix_compat(issues)
        assert "fix-1" in fixes
        assert "Union" in fixes["fix-1"]

    def test_fix_stdlib_incompat(self):
        issues = [
            PythonCompatIssue(
                issue_id="fix-2",
                file_path="b.py",
                line_no=2,
                issue_type="stdlib_incompat",
                current_syntax="import zoneinfo",
                suggested_fix="Install backport",
            )
        ]
        fixes = auto_fix_compat(issues)
        assert "fix-2" in fixes
        assert "backport" in fixes["fix-2"].lower() or "bump" in fixes["fix-2"].lower() or "3.9" in fixes["fix-2"]

    def test_empty_issues(self):
        fixes = auto_fix_compat([])
        assert fixes == {}

    def test_unsupported_issue_type_skipped(self):
        issues = [
            PythonCompatIssue(
                issue_id="fix-3",
                file_path="c.py",
                line_no=3,
                issue_type="type_alias",
                current_syntax="type X = int",
                suggested_fix="Use TypeAlias",
            )
        ]
        fixes = auto_fix_compat(issues)
        assert fixes == {}


class TestGenerateCompatReport:
    def test_empty_issues(self):
        report = generate_compat_report([], target_python="3.9")
        assert "Total issues: 0" in report
        assert "Python 3.9" in report

    def test_with_issues(self):
        issues = [
            PythonCompatIssue(
                issue_id="rpt-1",
                file_path="a.py",
                line_no=1,
                issue_type="union_syntax",
                current_syntax="str | int",
                suggested_fix="Use Union[str, int]",
                severity="MAJOR",
            ),
            PythonCompatIssue(
                issue_id="rpt-2",
                file_path="b.py",
                line_no=5,
                issue_type="stdlib_incompat",
                current_syntax="import zoneinfo",
                suggested_fix="Install backport",
                severity="MAJOR",
            ),
        ]
        report = generate_compat_report(issues, target_python="3.10")
        assert "Total issues: 2" in report
        assert "union_syntax" in report
        assert "stdlib_incompat" in report
        assert "a.py:1" in report
        assert "b.py:5" in report

    def test_report_contains_target_version(self):
        report = generate_compat_report([], target_python="3.11")
        assert "Python 3.11" in report
