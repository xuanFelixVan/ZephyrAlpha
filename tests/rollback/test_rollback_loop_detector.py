# [A_test] module_id: MOD-GOV_rollback_loop_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rollback_loop_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from zephyr.infrastructure.rollback.rollback_loop_detector import (
    LoopAlert,
    LoopDetectorResult,
    RollbackLoopDetector,
)


@pytest.fixture
def detector(tmp_path: Path) -> RollbackLoopDetector:
    return RollbackLoopDetector(project_root=tmp_path)


@pytest.fixture
def log_path(tmp_path: Path) -> Path:
    return tmp_path / ".zephyr" / "rollback_loop_log.jsonl"


def _write_log_entries(log_path: Path, entries: list[dict]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class TestRollbackLoopDetectorInstantiation:
    def test_creates_with_defaults(self):
        d = RollbackLoopDetector()
        assert d.project_root is not None

    def test_creates_with_custom_root(self, tmp_path: Path):
        d = RollbackLoopDetector(project_root=tmp_path)
        assert d.project_root == tmp_path

    def test_log_path_set(self, detector: RollbackLoopDetector):
        assert detector.log_path.name == "rollback_loop_log.jsonl"

    def test_max_rollbacks_constants(self):
        assert RollbackLoopDetector.MAX_ROLLBACKS_PER_HOUR == 3
        assert RollbackLoopDetector.MAX_ROLLBACKS_PER_DAY == 10
        assert RollbackLoopDetector.BLOCK_DURATION_MINUTES == 60


class TestRecord:
    def test_record_creates_log(self, detector: RollbackLoopDetector, log_path: Path):
        detector.record("task-1", "gate-1", success=False)
        assert log_path.exists()
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["task_id"] == "task-1"
        assert entry["gate_id"] == "gate-1"
        assert entry["success"] is False

    def test_record_multiple_entries(self, detector: RollbackLoopDetector, log_path: Path):
        for i in range(5):
            detector.record("task-1", "gate-1", success=(i % 2 == 0))
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 5

    def test_record_appends_to_existing(self, detector: RollbackLoopDetector, log_path: Path):
        _write_log_entries(
            log_path,
            [
                {
                    "timestamp_utc": datetime.now(UTC).isoformat(),
                    "task_id": "old-task",
                    "gate_id": "old-gate",
                    "success": True,
                }
            ],
        )
        detector.record("new-task", "new-gate")
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2

    def test_record_creates_parent_dir(self, tmp_path: Path):
        deep_path = tmp_path / "deep" / "nested"
        d = RollbackLoopDetector(project_root=deep_path)
        d.record("task-1", "gate-1")
        assert (deep_path / ".zephyr" / "rollback_loop_log.jsonl").exists()


class TestCheck:
    def test_check_no_log(self, detector: RollbackLoopDetector):
        result = detector.check()
        assert isinstance(result, LoopDetectorResult)
        assert result.loop_detected is False
        assert result.alerts == []

    def test_check_below_threshold(self, detector: RollbackLoopDetector, log_path: Path):
        for i in range(3):
            detector.record("task-1", "gate-1", success=False)
        result = detector.check()
        assert result.loop_detected is False

    def test_check_above_threshold(self, detector: RollbackLoopDetector, log_path: Path):
        for i in range(4):
            detector.record("task-1", "gate-1", success=False)
        result = detector.check()
        assert result.loop_detected is True
        assert len(result.alerts) == 1
        alert = result.alerts[0]
        assert isinstance(alert, LoopAlert)
        assert alert.task_id == "task-1"
        assert alert.gate_id == "gate-1"
        assert alert.count_in_hour == 4

    def test_check_different_combinations(self, detector: RollbackLoopDetector, log_path: Path):
        for _ in range(4):
            detector.record("task-1", "gate-1", success=False)
        for _ in range(4):
            detector.record("task-2", "gate-2", success=False)
        result = detector.check()
        assert result.loop_detected is True
        assert len(result.alerts) == 2

    def test_check_old_entries_ignored(self, detector: RollbackLoopDetector, log_path: Path):
        old_ts = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
        _write_log_entries(
            log_path,
            [
                {"timestamp_utc": old_ts, "task_id": "task-1", "gate_id": "gate-1", "success": False},
                {"timestamp_utc": old_ts, "task_id": "task-1", "gate_id": "gate-1", "success": False},
                {"timestamp_utc": old_ts, "task_id": "task-1", "gate_id": "gate-1", "success": False},
                {"timestamp_utc": old_ts, "task_id": "task-1", "gate_id": "gate-1", "success": False},
            ],
        )
        result = detector.check()
        assert result.loop_detected is False

    def test_check_mixed_old_and_new(self, detector: RollbackLoopDetector, log_path: Path):
        old_ts = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
        _write_log_entries(
            log_path,
            [
                {"timestamp_utc": old_ts, "task_id": "task-1", "gate_id": "gate-1", "success": False},
            ],
        )
        for _ in range(4):
            detector.record("task-1", "gate-1", success=False)
        result = detector.check()
        assert result.loop_detected is True
        assert result.alerts[0].count_in_hour == 4

    def test_check_corrupted_line_skipped(self, detector: RollbackLoopDetector, log_path: Path):
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("not-json\n")
        for _ in range(4):
            detector.record("task-1", "gate-1", success=False)
        result = detector.check()
        assert result.loop_detected is True


class TestIsBlocked:
    def test_not_blocked(self, detector: RollbackLoopDetector):
        assert detector.is_blocked("task-1", "gate-1") is False

    def test_blocked_after_exceeding(self, detector: RollbackLoopDetector):
        for _ in range(4):
            detector.record("task-1", "gate-1", success=False)
        assert detector.is_blocked("task-1", "gate-1") is True

    def test_different_combination_not_blocked(self, detector: RollbackLoopDetector):
        for _ in range(4):
            detector.record("task-1", "gate-1", success=False)
        assert detector.is_blocked("task-2", "gate-2") is False

    def test_empty_task_and_gate(self, detector: RollbackLoopDetector):
        assert detector.is_blocked("", "") is False


class TestGetBlockedCombinations:
    def test_no_blocked(self, detector: RollbackLoopDetector):
        result = detector.get_blocked_combinations()
        assert result == {}

    def test_blocked_combinations(self, detector: RollbackLoopDetector):
        for _ in range(4):
            detector.record("task-1", "gate-1", success=False)
        for _ in range(4):
            detector.record("task-1", "gate-2", success=False)
        result = detector.get_blocked_combinations()
        assert "task-1" in result
        assert "gate-1" in result["task-1"]
        assert "gate-2" in result["task-1"]

    def test_multiple_tasks(self, detector: RollbackLoopDetector):
        for _ in range(4):
            detector.record("task-1", "gate-1", success=False)
        for _ in range(4):
            detector.record("task-2", "gate-1", success=False)
        result = detector.get_blocked_combinations()
        assert "task-1" in result
        assert "task-2" in result
