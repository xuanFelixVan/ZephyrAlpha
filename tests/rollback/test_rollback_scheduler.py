# [A_test] module_id=TEST-rollback-scheduler | layer=test | stability=evolving | safety=L
# [BLUEPRINT] MOD-INF-021 | tests/rollback/ | §7 Phase 5.3
# [DOMAIN] D_INFRA_RECOVERY
# [GOVERNANCE] A_test 6-field: test_id=DM-201911-ADV | type=adversarial | scope=scheduler | gate=G0 | owner=AI-09 | rollback=delete_file
# [TTL] task_bound
"""
DM-201911 红蓝对抗极端测试: RollbackScheduler 自动运行+自动关闭.

测试场景:
    1. 重复 start/stop 循环（100次）—— 资源泄漏检测
    2. start 后立即 stop —— 竞态条件
    3. WAL GC 空 WAL 文件
    4. WAL GC 全 PENDING 条目（不删除）
    5. WAL GC 过期 COMPLETE 条目（删除）
    6. schedule_drill 演练时间触发（mock is_drill_time）
    7. schedule_drill 异常处理（run_drill 抛异常）
    8. 守护线程异常不崩溃
    9. 并发 start/stop（多线程）
    10. stop 超时处理
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.infrastructure.rollback.rollback_scheduler import RollbackScheduler, SchedulerResult


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """临时项目根目录。"""
    (tmp_path / ".zephyr").mkdir(parents=True, exist_ok=True)
    return tmp_path


class TestSchedulerStartStopExtreme:
    """极端启动/停止测试。"""

    def test_repeated_start_stop_100_cycles(self, temp_project: Path) -> None:
        """100 次 start/stop 循环——检测资源泄漏。"""
        rs = RollbackScheduler(project_root=temp_project)
        for i in range(100):
            assert rs.start() is True
            assert rs.is_running is True
            assert rs.stop(timeout=2.0) is True
            assert rs.is_running is False
        # 验证没有残留线程
        active = [t for t in threading.enumerate() if t.name == "rollback-scheduler" and t.is_alive()]
        assert len(active) == 0

    def test_start_then_immediate_stop_race(self, temp_project: Path) -> None:
        """start 后立即 stop——竞态条件。"""
        rs = RollbackScheduler(project_root=temp_project)
        for _ in range(20):
            rs.start()
            rs.stop(timeout=2.0)
        assert rs.is_running is False

    def test_double_start_idempotent(self, temp_project: Path) -> None:
        """重复 start 幂等。"""
        rs = RollbackScheduler(project_root=temp_project)
        assert rs.start() is True
        assert rs.start() is True
        assert rs.is_running is True
        rs.stop(timeout=2.0)

    def test_double_stop_idempotent(self, temp_project: Path) -> None:
        """重复 stop 幂等。"""
        rs = RollbackScheduler(project_root=temp_project)
        rs.start()
        assert rs.stop() is True
        assert rs.stop() is True
        assert rs.is_running is False

    def test_stop_without_start(self, temp_project: Path) -> None:
        """未启动直接 stop。"""
        rs = RollbackScheduler(project_root=temp_project)
        assert rs.stop() is True
        assert rs.is_running is False


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


class TestDaemonThreadResilience:
    """守护线程韧性测试。"""

    def test_daemon_survives_wal_gc_exception(self, temp_project: Path) -> None:
        """WAL GC 异常不崩溃守护线程。"""
        rs = RollbackScheduler(project_root=temp_project)
        # 缩短间隔以快速触发
        rs.DRILL_CHECK_INTERVAL_SECONDS = 0.05
        rs.WAL_GC_INTERVAL_SECONDS = 0.05

        call_count = 0
        original_gc = rs.schedule_wal_gc

        def failing_gc() -> SchedulerResult:
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise RuntimeError("gc boom")
            return original_gc()

        rs.schedule_wal_gc = failing_gc

        rs.start()
        time.sleep(0.5)
        rs.stop(timeout=2.0)

        # 线程应存活并继续运行
        assert rs.is_running is False  # 已 stop
        assert call_count >= 3  # 异常被捕获，继续运行

    def test_daemon_survives_drill_exception(self, temp_project: Path) -> None:
        """drill 异常不崩溃守护线程。"""
        rs = RollbackScheduler(project_root=temp_project)
        rs.DRILL_CHECK_INTERVAL_SECONDS = 0.05
        rs.WAL_GC_INTERVAL_SECONDS = 999  # 不触发 GC

        call_count = 0

        def failing_drill() -> None:
            nonlocal call_count
            call_count += 1
            raise RuntimeError("drill boom")

        rs.schedule_drill = failing_drill

        rs.start()
        time.sleep(0.5)
        rs.stop(timeout=2.0)

        assert call_count >= 3  # 异常被捕获，继续运行

    def test_concurrent_start_stop_multiple_threads(self, temp_project: Path) -> None:
        """多线程并发 start/stop——无死锁。"""
        rs = RollbackScheduler(project_root=temp_project)
        errors: list[Exception] = []

        def worker_start() -> None:
            try:
                for _ in range(20):
                    rs.start()
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)

        def worker_stop() -> None:
            try:
                for _ in range(20):
                    rs.stop(timeout=1.0)
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker_start) for _ in range(3)]
        threads += [threading.Thread(target=worker_stop) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        rs.stop(timeout=2.0)
        assert len(errors) == 0
        assert rs.is_running is False

    def test_stop_timeout_warning(self, temp_project: Path) -> None:
        """stop 超时——不永久阻塞。"""
        rs = RollbackScheduler(project_root=temp_project)
        rs.DRILL_CHECK_INTERVAL_SECONDS = 0.01
        rs.start()
        time.sleep(0.1)
        # 超时很短——即使线程还在运行也返回
        result = rs.stop(timeout=0.001)
        assert result is True  # stop 总是返回 True
        assert rs.is_running is False


class TestSchedulerStats:
    """统计信息测试。"""

    def test_get_stats_initial(self, temp_project: Path) -> None:
        """初始统计。"""
        rs = RollbackScheduler(project_root=temp_project)
        stats = rs.get_stats()
        assert stats["running"] is False
        assert stats["gc_count"] == 0
        assert stats["drill_count"] == 0
        assert stats["wal_gc_interval_seconds"] == 3600
        assert stats["drill_check_interval_seconds"] == 60
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
