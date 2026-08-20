# [A_test] module_id: MOD-GOV_cross_agent_conflict_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_cross_agent_conflict_detector
# [INVARIANTS] detect_conflicts returns list[ConflictReport]; resolve_conflicts returns same list; no git→empty
# [MODIFY-GUARD] blueprint.md §4
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError on invariant violation
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.governance.intelligence_governance.cross_agent_conflict_detector import (
    ConflictReport,
    CrossAgentConflictDetector,
)


@pytest.fixture
def detector(tmp_path: Path) -> CrossAgentConflictDetector:
    return CrossAgentConflictDetector(project_root=tmp_path)


class TestConflictReport:
    def test_creation(self):
        report = ConflictReport(
            file_path="src/main.py",
            agent_a="agent-1",
            agent_b="agent-2",
            has_conflict=True,
            resolution="SERIALIZE",
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert report.file_path == "src/main.py"
        assert report.agent_a == "agent-1"
        assert report.agent_b == "agent-2"
        assert report.has_conflict is True
        assert report.resolution == "SERIALIZE"

    def test_no_conflict_report(self):
        report = ConflictReport(
            file_path="src/util.py",
            agent_a="agent-1",
            agent_b="",
            has_conflict=False,
            resolution="NONE",
            timestamp_utc="2026-01-01T00:00:00+00:00",
        )
        assert report.has_conflict is False

    def test_default_fields(self):
        report = ConflictReport(
            file_path="f.py",
            agent_a="a",
            agent_b="b",
            has_conflict=True,
            resolution="R",
            timestamp_utc="t",
        )
        assert isinstance(report.file_path, str)
        assert isinstance(report.has_conflict, bool)


class TestCrossAgentConflictDetectorInstantiation:
    def test_default_project_root(self):
        detector = CrossAgentConflictDetector()
        assert detector.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path: Path):
        detector = CrossAgentConflictDetector(project_root=tmp_path)
        assert detector.project_root == tmp_path


class TestDetectConflicts:
    def test_no_uncommitted_files(self, detector: CrossAgentConflictDetector):
        with patch.object(detector, "_get_all_uncommitted_files", return_value=[]):
            reports = detector.detect_conflicts()
        assert reports == []

    def test_single_agent_no_conflict(self, detector: CrossAgentConflictDetector):
        with (
            patch.object(detector, "_get_all_uncommitted_files", return_value=["file1.py"]),
            patch.object(detector, "_get_most_recent_author", return_value="agent-a"),
        ):
            reports = detector.detect_conflicts()
        assert reports == []

    def test_two_agents_same_file_conflict(self, detector: CrossAgentConflictDetector):
        with (
            patch.object(detector, "_get_all_uncommitted_files", return_value=["file1.py", "file1.py"]),
            patch.object(detector, "_get_most_recent_author", side_effect=["agent-a", "agent-b"]),
        ):
            reports = detector.detect_conflicts()
        assert len(reports) >= 1
        assert reports[0].has_conflict is True
        assert reports[0].resolution == "SERIALIZE"

    def test_git_failure_returns_empty(self, detector: CrossAgentConflictDetector):
        with patch.object(detector, "_run_git", return_value=""):
            reports = detector.detect_conflicts()
        assert reports == []

    def test_multiple_files_different_agents_no_overlap(self, detector: CrossAgentConflictDetector):
        def mock_author(f):
            return "agent-a" if f == "file1.py" else "agent-b"

        with (
            patch.object(detector, "_get_all_uncommitted_files", return_value=["file1.py", "file2.py"]),
            patch.object(detector, "_get_most_recent_author", side_effect=mock_author),
        ):
            reports = detector.detect_conflicts()
        assert reports == []

    def test_conflict_report_has_timestamp(self, detector: CrossAgentConflictDetector):
        def mock_author(f):
            return "agent-a" if f == "shared.py" else "agent-b"

        with (
            patch.object(detector, "_get_all_uncommitted_files", return_value=["shared.py", "shared.py"]),
            patch.object(detector, "_get_most_recent_author", side_effect=mock_author),
        ):
            reports = detector.detect_conflicts()
        if reports:
            assert len(reports[0].timestamp_utc) > 0


class TestResolveConflicts:
    def test_empty_reports(self, detector: CrossAgentConflictDetector):
        result = detector.resolve_conflicts([])
        assert result == []

    def test_conflict_reports_resolved(self, detector: CrossAgentConflictDetector):
        reports = [
            ConflictReport(
                file_path="src/main.py",
                agent_a="a1",
                agent_b="a2",
                has_conflict=True,
                resolution="SERIALIZE",
                timestamp_utc="2026-01-01T00:00:00+00:00",
            )
        ]
        with patch.object(detector, "_run_git", return_value=""):
            result = detector.resolve_conflicts(reports)
        assert result == reports
        assert len(result) == 1

    def test_no_conflict_reports_unchanged(self, detector: CrossAgentConflictDetector):
        reports = [
            ConflictReport(
                file_path="src/util.py",
                agent_a="a1",
                agent_b="",
                has_conflict=False,
                resolution="NONE",
                timestamp_utc="2026-01-01T00:00:00+00:00",
            )
        ]
        result = detector.resolve_conflicts(reports)
        assert result == reports

    def test_git_add_failure_handled_gracefully(self, detector: CrossAgentConflictDetector):
        reports = [
            ConflictReport(
                file_path="src/broken.py",
                agent_a="a1",
                agent_b="a2",
                has_conflict=True,
                resolution="SERIALIZE",
                timestamp_utc="2026-01-01T00:00:00+00:00",
            )
        ]
        with patch.object(detector, "_run_git", side_effect=RuntimeError("git failed")):
            result = detector.resolve_conflicts(reports)
        assert result == reports

    def test_mixed_conflict_and_no_conflict(self, detector: CrossAgentConflictDetector):
        reports = [
            ConflictReport("f1.py", "a1", "a2", True, "SERIALIZE", "t1"),
            ConflictReport("f2.py", "a1", "", False, "NONE", "t2"),
        ]
        with patch.object(detector, "_run_git", return_value=""):
            result = detector.resolve_conflicts(reports)
        assert len(result) == 2


class TestRunGit:
    def test_git_success(self, detector: CrossAgentConflictDetector):
        with patch(
            "zephyr.governance.intelligence_governance.cross_agent_conflict_detector.run_subprocess_hidden"
        ) as mock_run:
            mock_run.return_value = MagicMock(stdout="file1.py\nfile2.py\n")
            result = detector.run_git(["diff", "--name-only", "HEAD"])
        assert "file1.py" in result

    def test_git_failure_returns_empty(self, detector: CrossAgentConflictDetector):
        with patch(
            "zephyr.governance.intelligence_governance.cross_agent_conflict_detector.run_subprocess_hidden"
        ) as mock_run:
            mock_run.side_effect = Exception("git not found")
            result = detector.run_git(["status"])
        assert result == ""


class TestGetMostRecentAuthor:
    def test_author_found(self, detector: CrossAgentConflictDetector):
        with patch.object(detector, "_run_git", return_value="user@example.com\n"):
            author = detector.get_most_recent_author("file1.py")
        assert author == "user@example.com"

    def test_author_not_found(self, detector: CrossAgentConflictDetector):
        with patch.object(detector, "_run_git", return_value=""):
            author = detector.get_most_recent_author("nonexistent.py")
        assert author == ""
