# [A_test] module_id: MOD-GOV_topology_change_log | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_topology_change_log
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.rollback.topology_change_log import (
    TopologyChange,
    TopologyChangeLog,
    TopologyOp,
)


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def log(tmp_project: Path) -> TopologyChangeLog:
    return TopologyChangeLog(project_root=tmp_project)


def _make_change(
    op: TopologyOp = TopologyOp.MERGE,
    branch: str = "main",
    target: str = "feature",
    before_sha: str = "abc1234",
    after_sha: str = "def5678",
    timestamp_utc: str = "2026-01-01T00:00:00Z",
    details: dict | None = None,
) -> TopologyChange:
    return TopologyChange(
        op=op,
        branch=branch,
        target=target,
        before_sha=before_sha,
        after_sha=after_sha,
        timestamp_utc=timestamp_utc,
        details=details or {},
    )


class TestTopologyOp:
    def test_enum_values(self) -> None:
        assert TopologyOp.MERGE.value == "merge"
        assert TopologyOp.REBASE.value == "rebase"
        assert TopologyOp.CHERRY_PICK.value == "cherry_pick"
        assert TopologyOp.BRANCH_DELETE.value == "branch_delete"
        assert TopologyOp.BRANCH_CREATE.value == "branch_create"
        assert TopologyOp.RESET.value == "reset"

    def test_enum_from_string(self) -> None:
        assert TopologyOp("merge") is TopologyOp.MERGE
        with pytest.raises(ValueError):
            TopologyOp("nonexistent")


class TestTopologyChange:
    def test_dataclass_fields(self) -> None:
        change = _make_change()
        assert change.op == TopologyOp.MERGE
        assert change.branch == "main"
        assert change.target == "feature"
        assert change.before_sha == "abc1234"
        assert change.after_sha == "def5678"
        assert change.details == {}

    def test_default_details(self) -> None:
        change = TopologyChange(
            op=TopologyOp.RESET,
            branch="dev",
            target="main",
            before_sha="aaa",
            after_sha="bbb",
            timestamp_utc="2026-05-22T12:00:00Z",
        )
        assert change.details == {}

    def test_custom_details(self) -> None:
        change = _make_change(details={"conflicts": 3})
        assert change.details == {"conflicts": 3}


class TestTopologyChangeLogInit:
    def test_init_with_project_root(self, tmp_project: Path) -> None:
        tcl = TopologyChangeLog(project_root=tmp_project)
        assert tcl._project_root == tmp_project
        assert tcl._log_path == tmp_project / ".zephyr/topology_change_log.jsonl"

    def test_init_default_root(self) -> None:
        tcl = TopologyChangeLog()
        assert tcl._project_root == Path.cwd()

    def test_init_none_root(self) -> None:
        tcl = TopologyChangeLog(project_root=None)
        assert tcl._project_root == Path.cwd()


class TestRecord:
    def test_record_creates_file(self, log: TopologyChangeLog, tmp_project: Path) -> None:
        change = _make_change()
        log.record(change)
        log_path = tmp_project / ".zephyr/topology_change_log.jsonl"
        assert log_path.exists()

    def test_record_writes_valid_jsonl(self, log: TopologyChangeLog, tmp_project: Path) -> None:
        change = _make_change(details={"key": "value"})
        log.record(change)
        log_path = tmp_project / ".zephyr/topology_change_log.jsonl"
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["op"] == "merge"
        assert entry["branch"] == "main"
        assert entry["details"] == {"key": "value"}

    def test_record_appends_multiple(self, log: TopologyChangeLog, tmp_project: Path) -> None:
        log.record(_make_change(branch="a"))
        log.record(_make_change(branch="b"))
        log_path = tmp_project / ".zephyr/topology_change_log.jsonl"
        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2

    def test_record_creates_parent_dirs(self, log: TopologyChangeLog, tmp_project: Path) -> None:
        log.record(_make_change())
        assert (tmp_project / ".zephyr").is_dir()


class TestGetHistory:
    def test_empty_when_no_file(self, log: TopologyChangeLog) -> None:
        assert log.get_history() == []

    def test_returns_recorded_changes(self, log: TopologyChangeLog) -> None:
        log.record(_make_change(branch="a"))
        log.record(_make_change(branch="b"))
        history = log.get_history()
        assert len(history) == 2
        assert history[0].branch == "a"
        assert history[1].branch == "b"

    def test_limit_parameter(self, log: TopologyChangeLog) -> None:
        for i in range(5):
            log.record(_make_change(branch=f"br-{i}"))
        history = log.get_history(limit=3)
        assert len(history) == 3
        assert history[0].branch == "br-2"
        assert history[2].branch == "br-4"

    def test_skips_malformed_lines(self, log: TopologyChangeLog, tmp_project: Path) -> None:
        log.record(_make_change(branch="valid"))
        log_path = tmp_project / ".zephyr/topology_change_log.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("not json\n")
            f.write("\n")
        log.record(_make_change(branch="valid2"))
        history = log.get_history()
        assert len(history) == 2
        assert all(h.branch.startswith("valid") for h in history)

    def test_empty_lines_ignored(self, log: TopologyChangeLog, tmp_project: Path) -> None:
        log.record(_make_change(branch="x"))
        log_path = tmp_project / ".zephyr/topology_change_log.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("   \n")
        history = log.get_history()
        assert len(history) == 1


class TestGetLastChangeFor:
    def test_returns_none_when_no_history(self, log: TopologyChangeLog) -> None:
        assert log.get_last_change_for("main") is None

    def test_returns_latest_for_branch(self, log: TopologyChangeLog) -> None:
        log.record(_make_change(branch="main", before_sha="aaa"))
        log.record(_make_change(branch="dev", before_sha="bbb"))
        log.record(_make_change(branch="main", before_sha="ccc"))
        result = log.get_last_change_for("main")
        assert result is not None
        assert result.before_sha == "ccc"

    def test_returns_none_for_unknown_branch(self, log: TopologyChangeLog) -> None:
        log.record(_make_change(branch="main"))
        assert log.get_last_change_for("nonexistent") is None


class TestRestoreBranch:
    @patch("zephyr.infrastructure.rollback.topology_change_log.subprocess.run")
    def test_restore_success(self, mock_run: MagicMock, log: TopologyChangeLog) -> None:
        reflog_result = MagicMock()
        reflog_result.stdout = "abc123def456\n"
        branch_result = MagicMock()
        mock_run.side_effect = [reflog_result, branch_result]
        assert log.restore_branch("feature") is True
        assert mock_run.call_count == 2

    @patch("zephyr.infrastructure.rollback.topology_change_log.subprocess.run")
    def test_restore_no_reflog(self, mock_run: MagicMock, log: TopologyChangeLog) -> None:
        reflog_result = MagicMock()
        reflog_result.stdout = ""
        mock_run.return_value = reflog_result
        assert log.restore_branch("feature") is False

    @patch("zephyr.infrastructure.rollback.topology_change_log.subprocess.run")
    def test_restore_exception(self, mock_run: MagicMock, log: TopologyChangeLog) -> None:
        mock_run.side_effect = OSError("git not found")
        assert log.restore_branch("feature") is False


class TestSnapshotCurrentTopology:
    @patch("zephyr.infrastructure.rollback.topology_change_log.subprocess.run")
    def test_snapshot_success(self, mock_run: MagicMock, log: TopologyChangeLog) -> None:
        branches_result = MagicMock()
        branches_result.stdout = "main\ndevelop\n"
        current_result = MagicMock()
        current_result.stdout = "main\n"
        mock_run.side_effect = [branches_result, current_result]
        result = log.snapshot_current_topology()
        assert "branches" in result
        assert "main" in result["branches"]
        assert "develop" in result["branches"]
        assert result["current"] == "main"
        assert "snapshot_at" in result

    @patch("zephyr.infrastructure.rollback.topology_change_log.subprocess.run")
    def test_snapshot_exception(self, mock_run: MagicMock, log: TopologyChangeLog) -> None:
        mock_run.side_effect = OSError("git not found")
        result = log.snapshot_current_topology()
        assert result == {}

    @patch("zephyr.infrastructure.rollback.topology_change_log.subprocess.run")
    def test_snapshot_empty_branches(self, mock_run: MagicMock, log: TopologyChangeLog) -> None:
        branches_result = MagicMock()
        branches_result.stdout = ""
        current_result = MagicMock()
        current_result.stdout = ""
        mock_run.side_effect = [branches_result, current_result]
        result = log.snapshot_current_topology()
        assert result["branches"] == []
