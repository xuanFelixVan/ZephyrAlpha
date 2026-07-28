# [A_test] module_id: MOD-GOV_git_metadata | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-230 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_git_metadata
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 §25 Git Metadata module."""

from datetime import UTC, datetime
from pathlib import Path

from zephyr.infrastructure.asset_inventory.metadata import (
    GitAssetMetadata,
    GitCommitInfo,
    GitMetadataExtractor,
)
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）


class TestGitCommitInfo:
    def test_model_creation(self) -> None:
        c = GitCommitInfo(
            sha="abc123",
            author="test",
            date=datetime.now(UTC),
            message="fix: test",
        )
        assert c.sha == "abc123"
        assert c.author == "test"

    def test_model_defaults(self) -> None:
        c = GitCommitInfo(
            sha="abc",
            author="a",
            date=datetime.now(UTC),
            message="m",
        )
        assert c.lines_added == 0
        assert c.lines_deleted == 0


class TestGitAssetMetadata:
    def test_model_creation(self) -> None:
        m = GitAssetMetadata(file_path="src/test.py")
        assert m.file_path == "src/test.py"
        assert m.authors == []
        assert m.co_changed_files == []

    def test_defaults(self) -> None:
        m = GitAssetMetadata(file_path="x.py")
        assert m.total_commits == 0
        assert m.ai_commits_ratio == 0.0
        assert m.churn_rate == 0.0


class TestGitMetadataExtractor:
    def test_constructor(self) -> None:
        ex = GitMetadataExtractor(REPO_ROOT)
        assert ex.root

    def test_current_lines_real_file(self) -> None:
        ex = GitMetadataExtractor(REPO_ROOT)
        lines = ex.current_lines("README.md")
        assert lines > 0

    def test_current_lines_nonexistent(self) -> None:
        ex = GitMetadataExtractor(REPO_ROOT)
        assert ex.current_lines("_nonexistent_xyz.txt") == 0

    def test_parse_date(self) -> None:
        dt = GitMetadataExtractor.parse_date("2024-06-15 12:30:45 +0000")
        assert dt.year == 2024
        assert dt.month == 6

    def test_is_ai_commit(self) -> None:
        assert GitMetadataExtractor.is_ai_commit("[AI] auto generated")
        assert not GitMetadataExtractor.is_ai_commit("normal commit")
