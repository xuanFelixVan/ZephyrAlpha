# [A_test] module_id=TEST-rollback-scheduler | layer=test | stability=evolving | safety=L
# [BLUEPRINT] MOD-INF-021 | tests/rollback/ | §7 Phase 5.3
# [DOMAIN] D_INFRA_RECOVERY
# [GOVERNANCE] A_test 6-field: test_id=DM-201911-ADV | type=adversarial | scope=scheduler | gate=G0 | owner=AI-09 | rollback=delete_file
# [TTL] task_bound
"""
DM-201911 红蓝对抗极端测试: RollbackScheduler 事件驱动调度.

治本修复(2026-07-17, AI-14 审计 P2): 移除 start/stop/daemon thread 时间触发循环
测试（TestSchedulerStartStopExtreme/TestDaemonThreadResilience），仅保留事件驱动
可调用方法（schedule_wal_gc/schedule_drill）的极端测试。

测试场景:
    1. WAL GC 空 WAL 文件
    2. WAL GC 全 PENDING 条目（不删除）
    3. WAL GC 过期 COMPLETE 条目（删除）
    4. WAL GC 混合状态条目
    5. WAL GC 损坏行跳过
    6. schedule_drill 非演练时间返回 None
    7. schedule_drill 演练时间触发（mock is_drill_time）
    8. schedule_drill 同一时间不重复触发
    9. schedule_drill 异常处理
    10. schedule_drill 不可用处理
    11. 统计信息
"""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.rollback.rollback_scheduler import RollbackScheduler, SchedulerResult


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """临时项目根目录。"""
    (tmp_path / ".zephyr").mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestWalGcExtreme:
    """WAL GC 极端测试。"""

    def test_gc_empty_wal_file(self, temp_project: Path) -> None:
        """WAL 文件不存在时 GC。"""
        rs = RollbackScheduler(project_root=temp_project)
        result = rs.schedule_wal_gc()
        assert result.success is True
        assert result.details.get("removed", 0) == 0

    def test_gc_all_pending_entries_preserved(self, temp_project: Path) -> None:
        """全 PENDING 条目——不删除。"""
        wal_path = temp_project / ".zephyr" / "rollback_wal.jsonl"
        wal_path.parent.mkdir(parents=True, exist_ok=True)
        old_time = (datetime.now(UTC) - timedelta(days=30)).isoformat()
        entries = [
            {"entry_id": "WAL-1", "operation": "full_revert", "status": "PENDING", "written_at": old_time},
            {"entry_id": "WAL-2", "operation": "partial_revert", "status": "PENDING", "written_at": old_time},
        ]
        with open(wal_path, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        rs = RollbackScheduler(project_root=temp_project)
        result = rs.schedule_wal_gc()
        assert result.success is True
        assert result.details.get("removed", 0) == 0
        assert result.details.get("kept", 0) == 2

    def test_gc_expired_complete_entries_removed(self, temp_project: Path) -> None:
        """过期 COMPLETE 条目——删除。"""
        wal_path = temp_project / ".zephyr" / "rollback_wal.jsonl"
        wal_path.parent.mkdir(parents=True, exist_ok=True)
        old_time = (datetime.now(UTC) - timedelta(days=30)).isoformat()
        new_time = datetime.now(UTC).isoformat()
        entries = [
            {"entry_id": "WAL-OLD-1", "operation": "full_revert", "status": "COMPLETE", "written_at": old_time},
            {"entry_id": "WAL-OLD-2", "operation": "partial_revert", "status": "COMPLETE", "written_at": old_time},
            {"entry_id": "WAL-NEW-1", "operation": "full_revert", "status": "COMPLETE", "written_at": new_time},
            {"entry_id": "WAL-PENDING-1", "operation": "discard", "status": "PENDING", "written_at": old_time},
        ]
        with open(wal_path, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        rs = RollbackScheduler(project_root=temp_project)
        result = rs.schedule_wal_gc()
        assert result.success is True
        assert result.details.get("removed", 0) == 2  # 2 个过期 COMPLETE
        assert result.details.get("kept", 0) == 2  # 1 个新 COMPLETE + 1 个 PENDING

        # 验证文件内容
        with open(wal_path, encoding="utf-8") as f:
            remaining = [json.loads(line) for line in f if line.strip()]
        entry_ids = [e["entry_id"] for e in remaining]
        assert "WAL-OLD-1" not in entry_ids
        assert "WAL-OLD-2" not in entry_ids
        assert "WAL-NEW-1" in entry_ids
        assert "WAL-PENDING-1" in entry_ids

    def test_gc_mixed_statuses(self, temp_project: Path) -> None:
        """混合状态条目。"""
        wal_path = temp_project / ".zephyr" / "rollback_wal.jsonl"
        wal_path.parent.mkdir(parents=True, exist_ok=True)
        old_time = (datetime.now(UTC) - timedelta(days=10)).isoformat()
        entries = [
            {"entry_id": f"WAL-{i}", "operation": "op", "status": "COMPLETE" if i % 2 == 0 else "PENDING", "written_at": old_time}
            for i in range(20)
        ]
        with open(wal_path, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        rs = RollbackScheduler(project_root=temp_project)
        result = rs.schedule_wal_gc()
        assert result.success is True
        # 10 个 COMPLETE 过期 → 删除；10 个 PENDING → 保留
        assert result.details.get("removed", 0) == 10
        assert result.details.get("kept", 0) == 10

    def test_gc_corrupted_wal_entries_skipped(self, temp_project: Path) -> None:
        """损坏的 WAL 行被跳过（不崩溃）。"""
        wal_path = temp_project / ".zephyr" / "rollback_wal.jsonl"
        wal_path.parent.mkdir(parents=True, exist_ok=True)
        old_time = (datetime.now(UTC) - timedelta(days=10)).isoformat()
        with open(wal_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"entry_id": "WAL-1", "status": "COMPLETE", "written_at": old_time}) + "\n")
            f.write("CORRUPTED_LINE_NOT_JSON\n")
            f.write(json.dumps({"entry_id": "WAL-2", "status": "PENDING", "written_at": old_time}) + "\n")

        rs = RollbackScheduler(project_root=temp_project)
        # 不应崩溃——_read_all 会跳过损坏行
        result = rs.schedule_wal_gc()
        assert result.success is True


class TestDrillSchedulingExtreme:
    """演练调度极端测试。"""

    def test_drill_not_time_returns_none(self, temp_project: Path) -> None:
        """非演练时间返回 None。"""
        mock_drill = MagicMock()
        mock_drill.is_drill_time.return_value = False
        rs = RollbackScheduler(project_root=temp_project, drill=mock_drill)
        result = rs.schedule_drill()
        assert result is None

    def test_drill_time_triggers_drill(self, temp_project: Path) -> None:
        """演练时间触发 drill。"""
        mock_drill = MagicMock()
        mock_drill.is_drill_time.return_value = True
        mock_result = MagicMock()
        mock_result.drill_id = "DRILL-TEST-001"
        mock_result.commit_sha = "abc123"
        mock_result.duration_ms = 500
        mock_result.chaos_scenario = "gc_concurrent"
        mock_result.db_integrity_pass = True
        mock_result.success = True
        mock_result.details = []
        mock_drill.run_drill.return_value = mock_result

        rs = RollbackScheduler(project_root=temp_project, drill=mock_drill)
        result = rs.schedule_drill()
        assert result is not None
        assert result.success is True
        assert result.details["drill_id"] == "DRILL-TEST-001"
        mock_drill.run_drill.assert_called_once()

    def test_drill_already_done_no_retrigger(self, temp_project: Path) -> None:
        """同一演练时间不重复触发。"""
        mock_drill = MagicMock()
        mock_drill.is_drill_time.return_value = True
        mock_result = MagicMock()
        mock_result.drill_id = "DRILL-TEST-002"
        mock_result.commit_sha = "def456"
        mock_result.duration_ms = 300
        mock_result.chaos_scenario = "sqlite_locked"
        mock_result.db_integrity_pass = True
        mock_result.success = True
        mock_result.details = []
        mock_drill.run_drill.return_value = mock_result

        rs = RollbackScheduler(project_root=temp_project, drill=mock_drill)
        # 第一次触发
        result1 = rs.schedule_drill()
        assert result1 is not None
        assert result1.success is True
        # 第二次不应触发（marker 已存在）
        result2 = rs.schedule_drill()
        assert result2 is None
        mock_drill.run_drill.assert_called_once()

    def test_drill_exception_handled(self, temp_project: Path) -> None:
        """drill.run_drill 抛异常——不崩溃。"""
        mock_drill = MagicMock()
        mock_drill.is_drill_time.return_value = True
        mock_drill.run_drill.side_effect = RuntimeError("drill boom")

        rs = RollbackScheduler(project_root=temp_project, drill=mock_drill)
        result = rs.schedule_drill()
        assert result is not None
        assert result.success is False
        assert len(result.errors) > 0
        assert "drill exception" in result.errors[0]

    def test_drill_not_available(self, temp_project: Path) -> None:
        """drill 不可用时返回失败。"""
        rs = RollbackScheduler(project_root=temp_project, drill=None)
        # mock _get_drill 返回 None
        with patch.object(rs, "_get_drill", return_value=None):
            result = rs.schedule_drill()
            assert result is not None
            assert result.success is False
            assert "drill not available" in result.errors


class TestSchedulerStats:
    """统计信息测试。"""

    def test_get_stats_initial(self, temp_project: Path) -> None:
        """初始统计（事件驱动，无 running/interval 字段）。"""
        rs = RollbackScheduler(project_root=temp_project)
        stats = rs.get_stats()
        assert stats["gc_count"] == 0
        assert stats["drill_count"] == 0
        assert stats["wal_retention_days"] == 7

    def test_gc_count_increments(self, temp_project: Path) -> None:
        """GC 计数递增。"""
        rs = RollbackScheduler(project_root=temp_project)
        assert rs.gc_count == 0
        rs.schedule_wal_gc()
        assert rs.gc_count == 1
        rs.schedule_wal_gc()
        assert rs.gc_count == 2

    def test_drill_count_increments(self, temp_project: Path) -> None:
        """drill 计数递增。"""
        mock_drill = MagicMock()
        mock_drill.is_drill_time.return_value = True
        mock_result = MagicMock()
        mock_result.drill_id = "DRILL-1"
        mock_result.commit_sha = "abc"
        mock_result.duration_ms = 100
        mock_result.chaos_scenario = "test"
        mock_result.db_integrity_pass = True
        mock_result.success = True
        mock_result.details = []
        mock_drill.run_drill.return_value = mock_result

        rs = RollbackScheduler(project_root=temp_project, drill=mock_drill)
        assert rs.drill_count == 0
        rs.schedule_drill()
        assert rs.drill_count == 1
