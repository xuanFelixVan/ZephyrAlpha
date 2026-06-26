# [A_test] module_id: SRC-TST-0518 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_circadian_scheduler
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tests never raise; all assertions within pytest
# [TESTS] this file
#
# NOTE: 定时调度已废除（2026-06-26 裁定），register_task/start/stop/save_state 均为 no-op。
# 以下测试验证 no-op 行为而非定时触发行为。事件驱动机制（register_event_listener/
# trigger_event）仍保留，相关测试继续验证其功能。

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from zephyr.trading.circadian_scheduler import CircadianPhase, CircadianScheduler, ScheduledTask


class TestScheduledTask:
    def test_init_defaults(self) -> None:
        task = ScheduledTask(hour=8, name="test", layer="L1")
        assert task.hour == 8
        assert task.name == "test"
        assert task.layer == "L1"
        assert task.callback is None
        assert task.last_run_date == ""

    def test_init_with_callback(self) -> None:
        cb = lambda: None
        task = ScheduledTask(hour=10, name="cb_task", layer="L2", callback=cb)
        assert task.callback is cb


class TestCircadianPhase:
    def test_phase_values(self) -> None:
        assert CircadianPhase.MORNING == "MORNING"
        assert CircadianPhase.DAY == "DAY"
        assert CircadianPhase.EVENING == "EVENING"
        assert CircadianPhase.NIGHT == "NIGHT"


class TestCircadianSchedulerInit:
    def test_init_no_state_path(self) -> None:
        scheduler = CircadianScheduler()
        assert scheduler._state_path is None
        assert scheduler._tasks == []

    def test_init_with_state_path(self, tmp_path: Path) -> None:
        state = tmp_path / "state.json"
        scheduler = CircadianScheduler(state_path=state)
        assert scheduler._state_path == state


class TestRegisterTask:
    """register_task 已废除为 no-op，验证其不抛异常、不添加任务、不执行回调。"""

    def test_register_single_task_is_noop(self) -> None:
        scheduler = CircadianScheduler()
        # no-op: 不抛异常即可
        scheduler.register_task(hour=8, name="morning_scan", layer="L1")
        # 不添加任何任务到 _tasks
        assert scheduler._tasks == []

    def test_register_multiple_tasks_is_noop(self) -> None:
        scheduler = CircadianScheduler()
        scheduler.register_task(hour=8, name="task1", layer="L1")
        scheduler.register_task(hour=12, name="task2", layer="L2")
        # 多次调用仍不添加任务
        assert scheduler._tasks == []

    def test_register_task_with_callback_is_noop(self) -> None:
        called = []
        scheduler = CircadianScheduler()
        # 传入 callback 也不应执行
        scheduler.register_task(hour=9, name="cb_task", layer="L1", callback=lambda: called.append(1))
        # no-op: 不添加任务、不执行回调
        assert scheduler._tasks == []
        assert called == []


class TestEventListener:
    def test_trigger_event_no_listeners(self) -> None:
        scheduler = CircadianScheduler()
        scheduler.trigger_event("nonexistent")

    def test_register_and_trigger_event(self) -> None:
        results = []
        scheduler = CircadianScheduler()
        scheduler.register_event_listener("phase_change", lambda: results.append("fired"))
        scheduler.trigger_event("phase_change")
        assert results == ["fired"]

    def test_event_listener_exception_swallowed(self) -> None:
        scheduler = CircadianScheduler()
        scheduler.register_event_listener("bad", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
        scheduler.trigger_event("bad")

    def test_multiple_listeners_same_event(self) -> None:
        results = []
        scheduler = CircadianScheduler()
        scheduler.register_event_listener("ev", lambda: results.append(1))
        scheduler.register_event_listener("ev", lambda: results.append(2))
        scheduler.trigger_event("ev")
        assert results == [1, 2]


class TestGetCurrentPhase:
    def test_returns_valid_phase(self) -> None:
        scheduler = CircadianScheduler()
        phase = scheduler.get_current_phase()
        assert isinstance(phase, CircadianPhase)

    def test_phase_is_one_of_four(self) -> None:
        scheduler = CircadianScheduler()
        phase = scheduler.get_current_phase()
        assert phase in {CircadianPhase.MORNING, CircadianPhase.DAY, CircadianPhase.EVENING, CircadianPhase.NIGHT}


class TestGetNextTask:
    def test_no_tasks_returns_none(self) -> None:
        scheduler = CircadianScheduler()
        assert scheduler.get_next_task() is None

    def test_returns_none_after_register_task_noop(self) -> None:
        """register_task 是 no-op，_tasks 始终为空，get_next_task 始终返回 None。"""
        scheduler = CircadianScheduler()
        current_hour = datetime.now().hour
        future_hour = (current_hour + 5) % 24
        scheduler.register_task(hour=future_hour, name="future", layer="L1")
        # no-op: 未注册任何任务，无下一任务
        assert scheduler.get_next_task() is None

    def test_already_run_today_excluded_is_noop(self) -> None:
        """register_task 是 no-op，无法注册任务，get_next_task 返回 None。"""
        scheduler = CircadianScheduler()
        today = datetime.now().strftime("%Y-%m-%d")
        current_hour = datetime.now().hour
        future_hour = current_hour + 5
        scheduler.register_task(hour=future_hour, name="done_task", layer="L1")
        # no-op: _tasks 为空，无法设置 last_run_date，get_next_task 返回 None
        assert scheduler.get_next_task() is None


class TestSaveState:
    """save_state 已废除为 no-op，验证其不抛异常、不创建文件。"""

    def test_save_state_no_path_is_noop(self) -> None:
        scheduler = CircadianScheduler()
        scheduler.register_task(hour=8, name="test", layer="L1")
        # no-op: 不抛异常
        scheduler.save_state()

    def test_save_state_does_not_create_file(self, tmp_path: Path) -> None:
        """save_state 是 no-op，不创建状态文件。"""
        state_path = tmp_path / "state.json"
        scheduler = CircadianScheduler(state_path=state_path)
        scheduler.register_task(hour=8, name="test", layer="L1")
        scheduler.save_state()
        # no-op: 文件不应被创建
        assert not state_path.exists()

    def test_save_state_empty_tasks_is_noop(self, tmp_path: Path) -> None:
        """save_state 是 no-op，即使无任务也不创建文件。"""
        state_path = tmp_path / "state.json"
        scheduler = CircadianScheduler(state_path=state_path)
        scheduler.save_state()
        # no-op: 文件不应被创建
        assert not state_path.exists()


class TestStartStop:
    """start/stop 已废除为 no-op，验证其不抛异常、不改变 _running 状态。"""

    def test_start_is_noop(self) -> None:
        scheduler = CircadianScheduler()
        # no-op: start 不设置 _running
        scheduler.start()
        assert scheduler._running is False

    def test_stop_is_noop(self) -> None:
        scheduler = CircadianScheduler()
        # no-op: start/stop 都不改变 _running
        scheduler.start()
        scheduler.stop()
        assert scheduler._running is False
