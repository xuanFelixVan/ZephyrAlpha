# [A_test] module_id: MOD-GOV_task_scheduler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-439 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_task_scheduler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/test_task_scheduler.py
# [TTL] task_bound

from __future__ import annotations

import json

from zephyr.infrastructure.queue.task_scheduler import (
    ScheduledTask,
    ScheduleStatus,
    TaskScheduler,
)


class TestTaskSchedulerInstantiation:
    def test_default_construction(self):
        s = TaskScheduler()
        assert s._tasks == {}

    def test_custom_data_dir(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path / "sched")
        assert s._data_dir == tmp_path / "sched"


class TestSchedule:
    def test_schedule_returns_scheduled_task(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        task = s.schedule("TASK-001")
        assert isinstance(task, ScheduledTask)
        assert task.task_id == "TASK-001"
        assert task.status == ScheduleStatus.PENDING
        assert task.scheduled_at != ""

    def test_schedule_with_estimated_tokens(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        task = s.schedule("TASK-002", estimated_tokens=500)
        assert task.estimated_tokens == 500

    def test_schedule_persists_to_file(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        s.schedule("TASK-003")
        sched_file = tmp_path / "schedules.jsonl"
        assert sched_file.exists()
        lines = sched_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["task_id"] == "TASK-003"

    def test_schedule_empty_task_id(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        task = s.schedule("")
        assert task.task_id == ""
        assert task.status == ScheduleStatus.PENDING

    def test_schedule_generates_unique_schedule_id(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        a = s.schedule("TASK-A")
        b = s.schedule("TASK-B")
        assert a.schedule_id != b.schedule_id


class TestStart:
    def test_start_changes_status_to_running(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        task = s.schedule("TASK-001")
        started = s.start(task.schedule_id)
        assert started is not None
        assert started.status == ScheduleStatus.RUNNING
        assert started.started_at != ""

    def test_start_nonexistent_returns_none(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        assert s.start("NONEXISTENT") is None

    def test_start_persists_change(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        task = s.schedule("TASK-001")
        s.start(task.schedule_id)
        sched_file = tmp_path / "schedules.jsonl"
        lines = sched_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        data = json.loads(lines[1])
        assert data["status"] == "running"


class TestComplete:
    def test_complete_changes_status(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        task = s.schedule("TASK-001")
        s.start(task.schedule_id)
        completed = s.complete(task.schedule_id)
        assert completed is not None
        assert completed.status == ScheduleStatus.COMPLETED
        assert completed.completed_at != ""

    def test_complete_nonexistent_returns_none(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        assert s.complete("NONEXISTENT") is None


class TestFail:
    def test_fail_changes_status(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        task = s.schedule("TASK-001")
        failed = s.fail(task.schedule_id)
        assert failed is not None
        assert failed.status == ScheduleStatus.FAILED
        assert failed.completed_at != ""

    def test_fail_nonexistent_returns_none(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        assert s.fail("NONEXISTENT") is None


class TestCancel:
    def test_cancel_changes_status(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        task = s.schedule("TASK-001")
        cancelled = s.cancel(task.schedule_id)
        assert cancelled is not None
        assert cancelled.status == ScheduleStatus.CANCELLED

    def test_cancel_nonexistent_returns_none(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        assert s.cancel("NONEXISTENT") is None


class TestGetPending:
    def test_get_pending_returns_only_pending(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        t1 = s.schedule("TASK-001")
        t2 = s.schedule("TASK-002")
        s.start(t1.schedule_id)
        pending = s.get_pending()
        assert len(pending) == 1
        assert pending[0].schedule_id == t2.schedule_id

    def test_get_pending_empty(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        assert s.get_pending() == []


class TestGetStats:
    def test_stats_empty(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        stats = s.get_stats()
        assert all(v == 0 for v in stats.values())

    def test_stats_after_operations(self, tmp_path):
        s = TaskScheduler(data_dir=tmp_path)
        t1 = s.schedule("TASK-001")
        t2 = s.schedule("TASK-002")
        s.start(t1.schedule_id)
        s.fail(t2.schedule_id)
        stats = s.get_stats()
        assert stats["running"] == 1
        assert stats["failed"] == 1


class TestScheduledTaskDataclass:
    def test_default_values(self):
        t = ScheduledTask(schedule_id="S1", task_id="T1", scheduled_at="2025-01-01")
        assert t.status == ScheduleStatus.PENDING
        assert t.assigned_model == "deepseek"
        assert t.assigned_pipeline == "A"
        assert t.estimated_tokens == 0
        assert t.timeout_minutes == 60
        assert t.started_at == ""
        assert t.completed_at == ""
