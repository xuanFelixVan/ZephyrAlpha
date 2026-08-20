# [A_test] module_id=MOD-GOV_conductor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §3.1
# [MODULE] tests.test_conductor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError→skip
# [TESTS] tests/test_conductor.py
# [TTL] task_bound
"""Conductor 单元测试——覆盖核心编排接口。"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def conductor(tmp_path):
    """构造一个 Conductor 实例（mock 掉 AutoPilot 和 TaskRepository）。"""
    from zephyr.trading.conductor import Conductor

    c = Conductor("session-test-001", db_path=str(tmp_path / "tasks.db"), max_parallel=2)
    # 替换 autopilot 和 repo 为 mock（Stage 4 公共化：使用公共 setter）
    c.autopilot = MagicMock()
    c.repo = MagicMock()
    return c


class TestConductorInit:
    def test_init_defaults(self):
        from zephyr.trading.conductor import Conductor

        c = Conductor("session-001")
        assert c.session_id == "session-001"
        assert c.max_parallel == 3
        # autopilot/repo 为懒加载实现细节，行为由其它测试覆盖（Stage 4 公共化）

    def test_init_custom(self):
        from zephyr.trading.conductor import Conductor

        c = Conductor("session-002", db_path="/tmp/x.db", max_parallel=5)
        assert c.session_id == "session-002"
        assert c.db_path == "/tmp/x.db"
        assert c.max_parallel == 5


class TestConductorPlanCycle:
    def test_plan_cycle_no_tasks(self, conductor):
        """无任务时返回空列表。"""
        conductor.autopilot.run_cycle.return_value = []
        result = conductor.plan_cycle()
        assert result == []

    def test_plan_cycle_with_tasks_no_conflict(self, conductor):
        """有任务但无文件冲突——所有任务应在同一组。"""
        t1 = MagicMock()
        t1.task_id = "T1"
        t1.priority = MagicMock()
        t1.priority.value = "HIGH"
        t1.created_at = MagicMock()
        t1.created_at.isoformat.return_value = "2026-01-01T00:00:00"
        t1.files_in_scope = ["a.py"]
        t1.allowed_touch = []
        t1.downstream_outputs = []

        t2 = MagicMock()
        t2.task_id = "T2"
        t2.priority = MagicMock()
        t2.priority.value = "HIGH"
        t2.created_at = MagicMock()
        t2.created_at.isoformat.return_value = "2026-01-01T00:00:01"
        t2.files_in_scope = ["b.py"]
        t2.allowed_touch = []
        t2.downstream_outputs = []

        conductor.autopilot.run_cycle.return_value = [t1, t2]
        result = conductor.plan_cycle()

        assert len(result) == 1
        assert len(result[0]) == 2

    def test_plan_cycle_with_conflict(self, conductor):
        """有文件冲突——任务应分到不同组。"""
        t1 = MagicMock()
        t1.task_id = "T1"
        t1.priority = MagicMock()
        t1.priority.value = "HIGH"
        t1.created_at = MagicMock()
        t1.created_at.isoformat.return_value = "2026-01-01T00:00:00"
        t1.files_in_scope = ["shared.py"]
        t1.allowed_touch = []
        t1.downstream_outputs = []

        t2 = MagicMock()
        t2.task_id = "T2"
        t2.priority = MagicMock()
        t2.priority.value = "HIGH"
        t2.created_at = MagicMock()
        t2.created_at.isoformat.return_value = "2026-01-01T00:00:01"
        t2.files_in_scope = ["shared.py"]
        t2.allowed_touch = []
        t2.downstream_outputs = []

        conductor.autopilot.run_cycle.return_value = [t1, t2]
        result = conductor.plan_cycle()

        # 冲突——应分到2个组
        assert len(result) == 2
        assert len(result[0]) == 1
        assert len(result[1]) == 1


class TestConductorIsDone:
    def test_is_done_true(self, conductor):
        conductor.repo.count_by_status.return_value = {"READY": 0, "IN_PROGRESS": 0}
        assert conductor.is_done() is True

    def test_is_done_false_ready(self, conductor):
        conductor.repo.count_by_status.return_value = {"READY": 5, "IN_PROGRESS": 0}
        assert conductor.is_done() is False

    def test_is_done_false_in_progress(self, conductor):
        conductor.repo.count_by_status.return_value = {"READY": 0, "IN_PROGRESS": 2}
        assert conductor.is_done() is False


class TestConductorMarkCompleted:
    def test_mark_completed_calls_transition(self, conductor):
        conductor.mark_completed("T1", note="done")
        conductor.repo.transition.assert_called_once_with("T1", "COMPLETED", session_id="session-test-001", note="done")


class TestConductorMarkFailed:
    def test_mark_failed_calls_transition(self, conductor):
        conductor.mark_failed("T1", note="root cause: x")
        conductor.repo.transition.assert_called_once_with(
            "T1", "FAILED", session_id="session-test-001", note="root cause: x"
        )


class TestConductorGetTaskFiles:
    def test_get_task_files_from_files_in_scope(self, conductor):
        t = MagicMock()
        t.files_in_scope = ["a.py", "b.py"]
        t.allowed_touch = []
        t.downstream_outputs = []
        files = conductor.get_task_files(t)
        assert files == {"a.py", "b.py"}

    def test_get_task_files_from_allowed_touch(self, conductor):
        t = MagicMock()
        t.files_in_scope = []
        t.allowed_touch = ["c.py"]
        t.downstream_outputs = []
        files = conductor.get_task_files(t)
        assert files == {"c.py"}

    def test_get_task_files_from_downstream_outputs(self, conductor):
        t = MagicMock()
        t.files_in_scope = []
        t.allowed_touch = []
        t.downstream_outputs = [{"path": "d.py"}, {"path": "e.py"}]
        files = conductor.get_task_files(t)
        assert files == {"d.py", "e.py"}

    def test_get_task_files_json_string(self, conductor):
        t = MagicMock()
        t.files_in_scope = '["x.py", "y.py"]'
        t.allowed_touch = []
        t.downstream_outputs = []
        files = conductor.get_task_files(t)
        assert files == {"x.py", "y.py"}


class TestConductorDetectConflicts:
    def test_no_conflict(self, conductor):
        t1 = MagicMock()
        t1.task_id = "T1"
        t1.files_in_scope = ["a.py"]
        t1.allowed_touch = []
        t1.downstream_outputs = []

        t2 = MagicMock()
        t2.task_id = "T2"
        t2.files_in_scope = ["b.py"]
        t2.allowed_touch = []
        t2.downstream_outputs = []

        cm = conductor.detect_file_conflicts([t1, t2])
        assert cm["T1"] == set()
        assert cm["T2"] == set()

    def test_with_conflict(self, conductor):
        t1 = MagicMock()
        t1.task_id = "T1"
        t1.files_in_scope = ["shared.py"]
        t1.allowed_touch = []
        t1.downstream_outputs = []

        t2 = MagicMock()
        t2.task_id = "T2"
        t2.files_in_scope = ["shared.py"]
        t2.allowed_touch = []
        t2.downstream_outputs = []

        cm = conductor.detect_file_conflicts([t1, t2])
        assert "T2" in cm["T1"]
        assert "T1" in cm["T2"]


class TestConductorGroupByConflict:
    def test_group_no_conflict(self, conductor):
        t1 = MagicMock()
        t1.task_id = "T1"
        t1.priority = MagicMock()
        t1.priority.value = "HIGH"
        t1.created_at = MagicMock()
        t1.created_at.isoformat.return_value = "2026-01-01T00:00:00"

        t2 = MagicMock()
        t2.task_id = "T2"
        t2.priority = MagicMock()
        t2.priority.value = "HIGH"
        t2.created_at = MagicMock()
        t2.created_at.isoformat.return_value = "2026-01-01T00:00:01"

        cm = {"T1": set(), "T2": set()}
        groups = conductor.group_by_conflict([t1, t2], cm)
        assert len(groups) == 1
        assert len(groups[0]) == 2

    def test_group_with_conflict(self, conductor):
        t1 = MagicMock()
        t1.task_id = "T1"
        t1.priority = MagicMock()
        t1.priority.value = "HIGH"
        t1.created_at = MagicMock()
        t1.created_at.isoformat.return_value = "2026-01-01T00:00:00"

        t2 = MagicMock()
        t2.task_id = "T2"
        t2.priority = MagicMock()
        t2.priority.value = "HIGH"
        t2.created_at = MagicMock()
        t2.created_at.isoformat.return_value = "2026-01-01T00:00:01"

        cm = {"T1": {"T2"}, "T2": {"T1"}}
        groups = conductor.group_by_conflict([t1, t2], cm)
        assert len(groups) == 2

    def test_group_max_parallel_truncation(self, conductor):
        """max_parallel=2，3个无冲突任务应分成2组（2+1）。"""
        conductor.max_parallel = 2
        tasks = []
        for i in range(3):
            t = MagicMock()
            t.task_id = f"T{i}"
            t.priority = MagicMock()
            t.priority.value = "HIGH"
            t.created_at = MagicMock()
            t.created_at.isoformat.return_value = f"2026-01-01T00:00:0{i}"
            tasks.append(t)

        cm = {f"T{i}": set() for i in range(3)}
        groups = conductor.group_by_conflict(tasks, cm)
        # 第一组2个，第二组1个
        assert len(groups) == 2
        assert len(groups[0]) == 2
        assert len(groups[1]) == 1


class TestConductorStatusReport:
    def test_status_report(self, conductor):
        conductor.autopilot.status_report.return_value = "BASE"
        conductor.repo.count_by_status.return_value = {"READY": 3, "IN_PROGRESS": 1}
        report = conductor.status_report()
        assert "BASE" in report
        assert "Conductor" in report
        assert "session-test-001" in report
