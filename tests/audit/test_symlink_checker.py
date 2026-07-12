# [A_test] module_id: SRC-TST-1712 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_symlink_checker
# [INVARIANTS] 软链接检查不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_symlink_checker.py
# [TTL] task_bound

import os
import tempfile
from datetime import UTC

import pytest

from zephyr.gov_drift.symlink_checker import (
    SymlinkIssue,
    check_broken_symlinks,
)


class TestSymlinkIssue:
    def test_instantiation_defaults(self):
        issue = SymlinkIssue(
            issue_id="test-1",
            symlink_path="/tmp/link",
            target_path="/tmp/target",
            issue_type="broken_symlink",
        )
        assert issue.issue_id == "test-1"
        assert issue.severity == "MAJOR"
        assert issue.detected_at is not None

    def test_instantiation_custom(self):
        from datetime import datetime

        dt = datetime(2026, 1, 1, tzinfo=UTC)
        issue = SymlinkIssue(
            issue_id="test-2",
            symlink_path="/tmp/link2",
            target_path="/tmp/target2",
            issue_type="circular_symlink",
            severity="CRITICAL",
            detected_at=dt,
        )
        assert issue.severity == "CRITICAL"
        assert issue.detected_at == dt

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            SymlinkIssue()


class TestCheckBrokenSymlinks:
    def test_nonexistent_root_returns_empty(self):
        issues = check_broken_symlinks("/nonexistent/path/xyz")
        assert issues == []

    def test_empty_directory_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            issues = check_broken_symlinks(tmpdir)
            assert issues == []

    def test_no_symlinks_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "normal.txt").write_text("hello", encoding="utf-8")
            issues = check_broken_symlinks(tmpdir)
            assert issues == []

    def test_broken_symlink_detected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            link_path = os.path.join(tmpdir, "broken_link")
            target_path = os.path.join(tmpdir, "nonexistent_target")
            try:
                os.symlink(target_path, link_path)
                issues = check_broken_symlinks(tmpdir)
                assert len(issues) >= 1
                assert issues[0].issue_type == "broken_symlink"
            except OSError:
                pytest.skip("symlinks not supported on this platform")

    def test_valid_symlink_not_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "real_target.txt")
            with open(target, "w", encoding="utf-8") as f:
                f.write("content")
            link_path = os.path.join(tmpdir, "valid_link")
            try:
                os.symlink(target, link_path)
                issues = check_broken_symlinks(tmpdir)
                assert len(issues) == 0
            except OSError:
                pytest.skip("symlinks not supported on this platform")


from pathlib import Path
