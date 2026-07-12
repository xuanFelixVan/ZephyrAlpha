# [A_test] module_id: SRC-TST-0907 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_file_attr_checker
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_file_attr_checker.py -q
# [TTL] task_bound

from __future__ import annotations

import os
import stat
from datetime import UTC, datetime

from zephyr.gov_drift.file_attr_checker import (
    _FILE_ATTR_CACHE,
    FileAttrIssue,
    _snapshot_file_attrs,
    capture_baseline,
    check_encoding,
    check_size_anomaly,
)


class TestFileAttrIssueInstantiation:
    def test_required_fields(self):
        issue = FileAttrIssue(
            issue_id="test-1",
            file_path="/tmp/test.py",
            issue_type="size_anomaly",
            expected="100 bytes",
            actual="2000 bytes",
        )
        assert issue.issue_id == "test-1"
        assert issue.file_path == "/tmp/test.py"
        assert issue.issue_type == "size_anomaly"
        assert issue.expected == "100 bytes"
        assert issue.actual == "2000 bytes"

    def test_default_severity(self):
        issue = FileAttrIssue(
            issue_id="test-2",
            file_path="/tmp/test.py",
            issue_type="size_anomaly",
            expected="100",
            actual="2000",
        )
        assert issue.severity == "MINOR"

    def test_custom_severity(self):
        issue = FileAttrIssue(
            issue_id="test-3",
            file_path="/tmp/test.py",
            issue_type="file_missing",
            expected="exists",
            actual="deleted",
            severity="CRITICAL",
        )
        assert issue.severity == "CRITICAL"

    def test_detected_at_auto_generated(self):
        issue = FileAttrIssue(
            issue_id="test-4",
            file_path="/tmp/test.py",
            issue_type="encoding_regression",
            expected="utf-8",
            actual="latin-1",
        )
        assert isinstance(issue.detected_at, datetime)
        assert issue.detected_at.tzinfo is not None

    def test_custom_detected_at(self):
        now = datetime.now(UTC)
        issue = FileAttrIssue(
            issue_id="test-5",
            file_path="/tmp/test.py",
            issue_type="size_anomaly",
            expected="100",
            actual="2000",
            detected_at=now,
        )
        assert issue.detected_at == now


class TestSnapshotFileAttrs:
    def test_existing_file(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')", encoding="utf-8")
        attrs = _snapshot_file_attrs(str(test_file))
        assert "size" in attrs
        assert "mode" in attrs
        assert "executable" in attrs
        assert "readonly" in attrs
        assert attrs["size"] > 0

    def test_nonexistent_file(self):
        attrs = _snapshot_file_attrs("/nonexistent/file.py")
        assert attrs == {}

    def test_size_matches_content(self, tmp_path):
        test_file = tmp_path / "sized.py"
        content = "x" * 500
        test_file.write_text(content, encoding="utf-8")
        attrs = _snapshot_file_attrs(str(test_file))
        assert attrs["size"] == len(content)

    def test_readonly_file(self, tmp_path):
        test_file = tmp_path / "readonly.py"
        test_file.write_text("data", encoding="utf-8")
        current_mode = os.stat(str(test_file)).st_mode
        os.chmod(str(test_file), current_mode & ~stat.S_IWUSR)
        attrs = _snapshot_file_attrs(str(test_file))
        assert attrs["readonly"] is True
        os.chmod(str(test_file), current_mode)

    def test_writable_file(self, tmp_path):
        test_file = tmp_path / "writable.py"
        test_file.write_text("data", encoding="utf-8")
        attrs = _snapshot_file_attrs(str(test_file))
        assert attrs["readonly"] is False


class TestCheckSizeAnomaly:
    def test_no_issues_same_size(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("x" * 100, encoding="utf-8")
        baseline = {str(test_file): {"size": 100}}
        issues = check_size_anomaly(str(tmp_path), baseline)
        assert len(issues) == 0

    def test_issue_when_file_missing(self, tmp_path):
        missing = str(tmp_path / "missing.py")
        baseline = {missing: {"size": 100}}
        issues = check_size_anomaly(str(tmp_path), baseline)
        assert len(issues) == 1
        assert issues[0].issue_type == "file_missing"
        assert issues[0].severity == "CRITICAL"
        assert issues[0].expected == "exists"
        assert issues[0].actual == "deleted"

    def test_issue_when_size_grows_10x(self, tmp_path):
        test_file = tmp_path / "big.py"
        test_file.write_text("x" * 2000, encoding="utf-8")
        baseline = {str(test_file): {"size": 100}}
        issues = check_size_anomaly(str(tmp_path), baseline)
        assert len(issues) == 1
        assert issues[0].issue_type == "size_anomaly"
        assert issues[0].severity == "MAJOR"

    def test_issue_when_size_shrinks_10x(self, tmp_path):
        test_file = tmp_path / "small.py"
        test_file.write_text("x", encoding="utf-8")
        baseline = {str(test_file): {"size": 1000}}
        issues = check_size_anomaly(str(tmp_path), baseline)
        assert len(issues) == 1
        assert issues[0].issue_type == "size_anomaly"

    def test_no_issue_moderate_change(self, tmp_path):
        test_file = tmp_path / "moderate.py"
        test_file.write_text("x" * 200, encoding="utf-8")
        baseline = {str(test_file): {"size": 100}}
        issues = check_size_anomaly(str(tmp_path), baseline)
        assert len(issues) == 0

    def test_empty_baseline(self, tmp_path):
        issues = check_size_anomaly(str(tmp_path), {})
        assert issues == []

    def test_zero_old_size_no_issue(self, tmp_path):
        test_file = tmp_path / "zero.py"
        test_file.write_text("hello", encoding="utf-8")
        baseline = {str(test_file): {"size": 0}}
        issues = check_size_anomaly(str(tmp_path), baseline)
        assert len(issues) == 0

    def test_zero_new_size_no_issue(self, tmp_path):
        test_file = tmp_path / "empty_new.py"
        test_file.write_text("", encoding="utf-8")
        baseline = {str(test_file): {"size": 100}}
        issues = check_size_anomaly(str(tmp_path), baseline)
        assert len(issues) == 0

    def test_exactly_10x_growth_is_not_anomaly(self, tmp_path):
        test_file = tmp_path / "exact10x.py"
        test_file.write_text("x" * 1000, encoding="utf-8")
        baseline = {str(test_file): {"size": 100}}
        issues = check_size_anomaly(str(tmp_path), baseline)
        assert len(issues) == 0

    def test_over_10x_growth_is_anomaly(self, tmp_path):
        test_file = tmp_path / "over10x.py"
        test_file.write_text("x" * 1001, encoding="utf-8")
        baseline = {str(test_file): {"size": 100}}
        issues = check_size_anomaly(str(tmp_path), baseline)
        assert len(issues) == 1

    def test_just_under_10x_no_anomaly(self, tmp_path):
        test_file = tmp_path / "just_under.py"
        test_file.write_text("x" * 999, encoding="utf-8")
        baseline = {str(test_file): {"size": 100}}
        issues = check_size_anomaly(str(tmp_path), baseline)
        assert len(issues) == 0

    def test_multiple_files(self, tmp_path):
        f1 = tmp_path / "ok.py"
        f2 = tmp_path / "big.py"
        f1.write_text("x" * 100, encoding="utf-8")
        f2.write_text("x" * 5000, encoding="utf-8")
        baseline = {str(f1): {"size": 100}, str(f2): {"size": 100}}
        issues = check_size_anomaly(str(tmp_path), baseline)
        assert len(issues) == 1
        assert "big" in issues[0].file_path


class TestCheckEncoding:
    def test_utf8_file(self, tmp_path):
        test_file = tmp_path / "utf8.py"
        test_file.write_text("hello world", encoding="utf-8")
        result = check_encoding(str(test_file))
        assert result in ("utf-8", "utf-8-bom")

    def test_utf8_bom_file(self, tmp_path):
        test_file = tmp_path / "bom.py"
        test_file.write_bytes(b"\xef\xbb\xbfhello")
        result = check_encoding(str(test_file))
        assert result == "utf-8-bom"

    def test_nonexistent_file(self):
        result = check_encoding("/nonexistent/file.py")
        assert result is None

    def test_empty_file(self, tmp_path):
        test_file = tmp_path / "empty.py"
        test_file.write_bytes(b"")
        result = check_encoding(str(test_file))
        assert result is not None

    def test_non_utf8_file(self, tmp_path):
        test_file = tmp_path / "binary.py"
        test_file.write_bytes(b"\x80\x81\x82\x83")
        result = check_encoding(str(test_file))
        assert result is not None
        assert result != "utf-8"

    def test_short_file_fewer_than_4_bytes(self, tmp_path):
        test_file = tmp_path / "short.py"
        test_file.write_bytes(b"ab")
        result = check_encoding(str(test_file))
        assert result is not None


class TestCaptureBaseline:
    def test_capture_baseline_populates_cache(self, tmp_path):
        test_file = tmp_path / "sample.py"
        test_file.write_text("print('hello')", encoding="utf-8")
        _FILE_ATTR_CACHE.clear()
        capture_baseline(str(tmp_path), "snap-1")
        found = any(str(test_file) in k for k in _FILE_ATTR_CACHE)
        assert found

    def test_capture_skips_git_dirs(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        git_file = git_dir / "config"
        git_file.write_text("test", encoding="utf-8")
        _FILE_ATTR_CACHE.clear()
        capture_baseline(str(tmp_path), "snap-2")
        assert str(git_file) not in _FILE_ATTR_CACHE

    def test_capture_skips_pycache(self, tmp_path):
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        pyc_file = pycache / "mod.cpython-311.pyc"
        pyc_file.write_bytes(b"\x00" * 10)
        _FILE_ATTR_CACHE.clear()
        capture_baseline(str(tmp_path), "snap-3")
        assert str(pyc_file) not in _FILE_ATTR_CACHE

    def test_capture_skips_venv(self, tmp_path):
        venv_dir = tmp_path / ".venv"
        venv_dir.mkdir()
        venv_file = venv_dir / "activate.py"
        venv_file.write_text("# venv", encoding="utf-8")
        _FILE_ATTR_CACHE.clear()
        capture_baseline(str(tmp_path), "snap-4")
        assert str(venv_file) not in _FILE_ATTR_CACHE

    def test_capture_multiple_files(self, tmp_path):
        for name in ("a.py", "b.py", "c.py"):
            (tmp_path / name).write_text(f"# {name}", encoding="utf-8")
        _FILE_ATTR_CACHE.clear()
        capture_baseline(str(tmp_path), "snap-5")
        py_entries = [k for k in _FILE_ATTR_CACHE if k.endswith(".py")]
        assert len(py_entries) >= 3

    def test_capture_empty_dir(self, tmp_path):
        _FILE_ATTR_CACHE.clear()
        capture_baseline(str(tmp_path), "snap-6")
        py_entries = [k for k in _FILE_ATTR_CACHE if str(tmp_path) in k]
        assert len(py_entries) == 0
