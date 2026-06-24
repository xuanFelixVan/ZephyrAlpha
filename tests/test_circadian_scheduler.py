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
    def test_register_single_task(self) -> None:
        scheduler = CircadianScheduler()
        scheduler.register_task(hour=8, name="morning_scan", layer="L1")
        assert len(scheduler._tasks) == 1
        assert scheduler._tasks[0].hour == 8
        assert scheduler._tasks[0].name == "morning_scan"

    def test_register_multiple_tasks(self) -> None:
        scheduler = CircadianScheduler()
        scheduler.register_task(hour=8, name="task1", layer="L1")
        scheduler.register_task(hour=12, name="task2", layer="L2")
        assert len(scheduler._tasks) == 2

    def test_register_task_with_callback(self) -> None:
        called = []
        scheduler = CircadianScheduler()
        scheduler.register_task(hour=9, name="cb_task", layer="L1", callback=lambda: called.append(1))
        assert scheduler._tasks[0].callback is not None
        scheduler._tasks[0].callback()
        assert called == [1]


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

    def test_returns_upcoming_task(self) -> None:
        scheduler = CircadianScheduler()
        current_hour = datetime.now().hour
        future_hour = (current_hour + 5) % 24
        scheduler.register_task(hour=future_hour, name="future", layer="L1")
        result = scheduler.get_next_task()
        if future_hour > current_hour:
            assert result is not None
            assert result.name == "future"
        else:
            assert result is None

    def test_already_run_today_excluded(self) -> None:
        scheduler = CircadianScheduler()
        today = datetime.now().strftime("%Y-%m-%d")
        current_hour = datetime.now().hour
        future_hour = current_hour + 5
        scheduler.register_task(hour=future_hour, name="done_task", layer="L1")
        scheduler._tasks[0].last_run_date = today
        result = scheduler.get_next_task()
        assert result is None


class TestSaveState:
    def test_save_state_no_path(self) -> None:
        scheduler = CircadianScheduler()
        scheduler.register_task(hour=8, name="test", layer="L1")
        scheduler.save_state()

    def test_save_state_creates_file(self, tmp_path: Path) -> None:
        state_path = tmp_path / "state.json"
        scheduler = CircadianScheduler(state_path=state_path)
        scheduler.register_task(hour=8, name="test", layer="L1")
        scheduler.save_state()
        assert state_path.exists()
        data = json.loads(state_path.read_text(encoding="utf-8"))
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["name"] == "test"

    def test_save_state_empty_tasks(self, tmp_path: Path) -> None:
        state_path = tmp_path / "state.json"
        scheduler = CircadianScheduler(state_path=state_path)
        scheduler.save_state()
        data = json.loads(state_path.read_text(encoding="utf-8"))
        assert data["tasks"] == []


class TestStartStop:
    def test_start_sets_running(self) -> None:
        scheduler = CircadianScheduler()
        scheduler.start()
        assert scheduler._running is True
        scheduler.stop()

    def test_stop_sets_not_running(self) -> None:
        scheduler = CircadianScheduler()
        scheduler.start()
        scheduler.stop()
        assert scheduler._running is False
